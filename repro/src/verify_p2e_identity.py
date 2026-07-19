#!/usr/bin/env python3
"""Independent finite-rank check of the P2E construction in Theorem 2.6.

This module intentionally implements the paper formula from scratch.  It does
not import ``upstream/``.  For every legal conformal rank p=j/(n+1), it finds
the positive C for which the P2E mapping is an exact e-value, verifies the
P2E/p-value set-membership identity, and checks classic calibrators as
set-inflating negative controls.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Iterable


def decreasing_logistic(x: float) -> float:
    """Stable ``1 / (1 + exp(x))`` independent of scipy/numpy."""
    if x >= 0.0:
        exp_neg_x = math.exp(-x)
        return exp_neg_x / (1.0 + exp_neg_x)
    exp_x = math.exp(x)
    return 1.0 / (1.0 + exp_x)


def log_decreasing_logistic(x: float) -> float:
    """Stable log of ``1 / (1 + exp(x))`` without underflow."""
    if x >= 0.0:
        return -x - math.log1p(math.exp(-x))
    return -math.log1p(math.exp(x))


def p2e_parameters(n_calibration: int, alpha: float) -> tuple[float, float]:
    """Construct one theorem-valid P2E calibrator for a finite rank law.

    The paper permits any s strictly between alpha and the first conformal rank
    above alpha.  We deliberately use that midpoint, rather than the source
    implementation's heuristic placement, and solve the exact discrete
    expectation equation by bisection.
    """
    if n_calibration < 1:
        raise ValueError("n_calibration must be positive")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0, 1)")

    denominator = n_calibration + 1
    first_above = math.floor(alpha * denominator + 1e-14) + 1
    if first_above > denominator:
        raise ValueError("no conformal rank exists above alpha")
    upper_rank = first_above / denominator
    if not alpha < upper_rank:
        raise ValueError("alpha lands on a conformal rank; excluded by theorem")
    s = 0.5 * (alpha + upper_rank)
    ranks = tuple(j / denominator for j in range(1, denominator + 1))

    def expectation_minus_one(c: float) -> float:
        at_alpha = decreasing_logistic(c * (alpha - s))
        values = [
            decreasing_logistic(c * (p - s)) / (alpha * at_alpha)
            for p in ranks
        ]
        return sum(values) / len(values) - 1.0

    low = 0.0
    high = 1.0
    low_value = expectation_minus_one(low)
    high_value = expectation_minus_one(high)
    while high_value > 0.0 and high < 1_000_000.0:
        high *= 2.0
        high_value = expectation_minus_one(high)
    if not (low_value >= 0.0 and high_value <= 0.0):
        raise RuntimeError("could not bracket the exact e-value solution")

    for _ in range(200):
        middle = 0.5 * (low + high)
        value = expectation_minus_one(middle)
        if value > 0.0:
            low = middle
        else:
            high = middle
    return 0.5 * (low + high), s


def p2e_value(p_value: float, alpha: float, c: float, s: float) -> float:
    """The explicit P2E function in Theorem 2.6."""
    return math.exp(p2e_log_value(p_value, alpha, c, s))


def p2e_log_value(p_value: float, alpha: float, c: float, s: float) -> float:
    """Log P2E value; finite even when an IEEE float would underflow."""
    return (
        log_decreasing_logistic(c * (p_value - s))
        - math.log(alpha)
        - log_decreasing_logistic(c * (alpha - s))
    )


def _control_value(name: str, p_value: float) -> float:
    if name == "log":
        return -math.log(p_value)
    if name == "sqrt":
        return p_value ** -0.5 - 1.0
    if name == "linear":
        return 2.0 * (1.0 - p_value)
    raise ValueError(f"unknown control {name}")


def evaluate_case(n_calibration: int, alpha: float) -> dict[str, float | int | bool | dict[str, int]]:
    c, s = p2e_parameters(n_calibration, alpha)
    ranks = [j / (n_calibration + 1) for j in range(1, n_calibration + 2)]
    p_values = [p2e_value(p, alpha, c, s) for p in ranks]
    log_p2e_values = [p2e_log_value(p, alpha, c, s) for p in ranks]
    p_members = [p > alpha for p in ranks]
    e_members = [value < 1.0 / alpha for value in p_values]
    mismatches = sum(left != right for left, right in zip(p_members, e_members))
    expectation = sum(p_values) / len(p_values)
    controls: dict[str, int] = {}
    for name in ("log", "sqrt", "linear"):
        member_count = sum(_control_value(name, p) < 1.0 / alpha for p in ranks)
        controls[name] = member_count - sum(p_members)

    return {
        "n_calibration": n_calibration,
        "alpha": alpha,
        "C": c,
        "s": s,
        "rank_count": len(ranks),
        "p_set_count": sum(p_members),
        "p2e_set_count": sum(e_members),
        "set_mismatches": mismatches,
        "exact_e_expectation": expectation,
        "expectation_abs_error": abs(expectation - 1.0),
        "p2e_strictly_positive": all(math.isfinite(value) for value in log_p2e_values),
        "min_log_p2e_value": min(log_p2e_values),
        "min_p2e_float": min(p_values),
        "classic_control_extra_members": controls,
    }


def run_cases(
    n_values: Iterable[int] = (10, 20, 30, 50, 100, 200),
    alpha_values: Iterable[float] = (0.05, 0.1, 0.2),
) -> dict[str, object]:
    rows = [evaluate_case(n, alpha) for n in n_values for alpha in alpha_values]
    all_identity = all(row["set_mismatches"] == 0 for row in rows)
    all_exact = all(float(row["expectation_abs_error"]) < 1e-11 for row in rows)
    all_positive = all(bool(row["p2e_strictly_positive"]) for row in rows)
    control_rows = [row for row in rows if row["p_set_count"] < row["rank_count"]]
    controls_inflate = bool(control_rows) and all(
        all(extra > 0 for extra in dict(row["classic_control_extra_members"]).values())
        for row in control_rows
    )
    return {
        "paper": "jNv4sl4YZH / arXiv:2606.03600",
        "implementation": "independent finite-rank construction",
        "cases": rows,
        "summary": {
            "case_count": len(rows),
            "all_set_identities_pass": all_identity,
            "all_exact_e_expectations_pass": all_exact,
            "all_positive_pass": all_positive,
            "all_classic_controls_inflate_sets": controls_inflate,
            "classic_control_case_count": len(control_rows),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_cases()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
