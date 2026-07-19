# Claim 1


---
<!-- trackio-cell
{"type": "code", "id": "cell_f1f02636328b", "created_at": "2026-07-18T12:24:07+00:00", "title": "Independent finite-rank P2E verification", "command": ["python", "repro/src/verify_p2e_identity.py", "--output", "outputs/claim1_independent.json"], "exit_code": 0, "duration_s": 0.213}
-->
````bash
$ python repro/src/verify_p2e_identity.py --output outputs/claim1_independent.json
````

exit 0 · 0.2s


````python title=verify_p2e_identity.py
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

````


````json title=claim1_independent.json
{
  "cases": [
    {
      "C": 32.899219106837066,
      "alpha": 0.05,
      "classic_control_extra_members": {
        "linear": 0,
        "log": 0,
        "sqrt": 0
      },
      "exact_e_expectation": 0.9999999999999997,
      "expectation_abs_error": 3.3306690738754696e-16,
      "min_log_p2e_value": -27.17334051675717,
      "min_p2e_float": 1.580404140046988e-12,
      "n_calibration": 10,
      "p2e_set_count": 11,
      "p2e_strictly_positive": true,
      "p_set_count": 11,
      "rank_count": 11,
      "s": 0.07045454545454546,
      "set_mismatches": 0
    },
    {
      "C": 65.07722023316114,
      "alpha": 0.1,
      "classic_control_extra_members": {
        "linear": 1,
        "log": 1,
        "sqrt": 1
      },
      "exact_e_expectation": 0.9999999999999997,
      "expectation_abs_error": 3.3306690738754696e-16,
      "min_log_p2e_value": -53.53719987644119,
      "min_p2e_float": 5.611636315886701e-24,
      "n_calibration": 10,
      "p2e_set_count": 10,
      "p2e_strictly_positive": true,
      "p_set_count": 10,
      "rank_count": 11,
      "s": 0.14090909090909093,
      "set_mismatches": 0
    },
    {
      "C": 71.7312565275491,
      "alpha": 0.2,
      "classic_control_extra_members": {
        "linear": 2,
        "log": 2,
        "sqrt": 2
      },
      "exact_e_expectation": 1.0000000000000002,
      "expectation_abs_error": 2.220446049250313e-16,
      "min_log_p2e_value": -53.09609242691801,
      "min_p2e_float": 8.722883020888222e-24,
      "n_calibration": 10,
      "p2e_set_count": 9,
      "p2e_strictly_positive": true,
      "p_set_count": 9,
      "rank_count": 11,
      "s": 0.23636363636363636,
      "set_mismatches": 0
    },
    {
      "C": 143.44819268231788,
      "alpha": 0.05,
      "classic_control_extra_members": {
        "linear": 1,
        "log": 1,
        "sqrt": 1
      },
      "exact_e_expectation": 1.0000000000000002,
      "expectation_abs_error": 2.220446049250313e-16,
      "min_log_p2e_value": -129.99714811937724,
      "min_p2e_float": 3.4910487108230056e-57,
      "n_calibration": 20,
      "p2e_set_count": 20,
      "p2e_strictly_positive": true,
      "p_set_count": 20,
      "rank_count": 21,
      "s": 0.07261904761904761,
      "set_mismatches": 0
    },
    {
      "C": 150.24495454452904,
      "alpha": 0.1,
      "classic_control_extra_members": {
        "linear": 2,
        "log": 2,
        "sqrt": 2
      },
      "exact_e_expectation": 0.9999999999999998,
      "expectation_abs_error": 2.220446049250313e-16,
      "min_log_p2e_value": -129.65914387856117,
      "min_p2e_float": 4.8949615553935044e-57,
      "n_calibration": 20,
      "p2e_set_count": 19,
      "p2e_strictly_positive": true,
      "p_set_count": 19,
      "rank_count": 21,
      "s": 0.12142857142857143,
      "set_mismatches": 0
    },
    {
      "C": 166.72966641514466,
      "alpha": 0.2,
      "classic_control_extra_members": {
        "linear": 4,
        "log": 4,
        "sqrt": 4
      },
      "exact_e_expectation": 1.0,
      "expectation_abs_error": 0.0,
      "min_log_p2e_value": -128.55757993160344,
      "min_p2e_float": 1.4728293460185009e-56,
      "n_calibration": 20,
      "p2e_set_count": 17,
      "p2e_strictly_positive": true,
      "p_set_count": 17,
      "rank_count": 21,
      "s": 0.21904761904761905,
      "set_mismatches": 0
    },
    {
      "C": 174.17299719890627,
      "alpha": 0.05,
      "classic_control_extra_members": {
        "linear": 1,
        "log": 1,
        "sqrt": 1
      },
      "exact_e_expectation": 1.0000000000000002,
      "expectation_abs_error": 2.220446049250313e-16,
      "min_log_p2e_value": -160.95566300543248,
      "min_p2e_float": 1.2526903320528512e-70,
      "n_calibration": 30,
      "p2e_set_count": 30,
      "p2e_strictly_positive": true,
      "p_set_count": 30,
      "rank_count": 31,
      "s": 0.05725806451612903,
      "set_mismatches": 0
    },
    {
      "C": 245.7194104724462,
      "alpha": 0.1,
      "classic_control_extra_members": {
        "linear": 3,
        "log": 3,
        "sqrt": 3
      },
      "exact_e_expectation": 1.0000000000000002,
      "expectation_abs_error": 2.220446049250313e-16,
      "min_log_p2e_value": -215.2501377324065,
      "min_p2e_float": 3.296499042243523e-94,
      "n_calibration": 30,
      "p2e_set_count": 28,
      "p2e_strictly_positive": true,
      "p_set_count": 28,
      "rank_count": 31,
      "s": 0.11451612903225807,
      "set_mismatches": 0
    },
    {
      "C": 273.57509255601883,
      "alpha": 0.2,
      "classic_control_extra_members": {
        "linear": 6,
        "log": 6,
        "sqrt": 6
      },
      "exact_e_expectation": 0.9999999999999999,
      "expectation_abs_error": 1.1102230246251565e-16,
      "min_log_p2e_value": -213.69175123664013,
      "min_p2e_float": 1.5662158319679543e-93,
      "n_calibration": 30,
      "p2e_set_count": 25,
      "p2e_strictly_positive": true,
      "p_set_count": 25,
      "rank_count": 31,
      "s": 0.2129032258064516,
      "set_mismatches": 0
    },
    {
      "C": 383.14005814359837,
      "alpha": 0.05,
      "classic_control_extra_members": {
        "linear": 2,
        "log": 2,
        "sqrt": 2
      },
      "exact_e_expectation": 1.0,
      "expectation_abs_error": 0.0,
      "min_log_p2e_value": -359.12771238068956,
      "min_p2e_float": 1.0784902283322196e-156,
      "n_calibration": 50,
      "p2e_set_count": 49,
      "p2e_strictly_positive": true,
      "p_set_count": 49,
      "rank_count": 51,
      "s": 0.054411764705882354,
      "set_mismatches": 0
    },
    {
      "C": 455.93837460449174,
      "alpha": 0.1,
      "classic_control_extra_members": {
        "linear": 5,
        "log": 5,
        "sqrt": 5
      },
      "exact_e_expectation": 0.9999999999999996,
      "expectation_abs_error": 4.440892098500626e-16,
      "min_log_p2e_value": -404.0012252580513,
      "min_p2e_float": 3.503460200719301e-176,
      "n_calibration": 50,
      "p2e_set_count": 46,
      "p2e_strictly_positive": true,
      "p_set_count": 46,
      "rank_count": 51,
      "s": 0.10882352941176471,
      "set_mismatches": 0
    },
    {
      "C": 509.3275927243293,
      "alpha": 0.2,
      "classic_control_extra_members": {
        "linear": 10,
        "log": 10,
        "sqrt": 9
      },
      "exact_e_expectation": 1.0000000000000002,
      "expectation_abs_error": 2.220446049250313e-16,
      "min_log_p2e_value": -401.8396650202642,
      "min_p2e_float": 3.0426421118437186e-175,
      "n_calibration": 50,
      "p2e_set_count": 41,
      "p2e_strictly_positive": true,
      "p_set_count": 41,
      "rank_count": 51,
      "s": 0.20784313725490197,
      "set_mismatches": 0
    },
    {
      "C": 995.0481689379562,
      "alpha": 0.05,
      "classic_control_extra_members": {
        "linear": 5,
        "log": 5,
        "sqrt": 5
      },
      "exact_e_expectation": 1.0000000000000002,
      "expectation_abs_error": 2.220446049250313e-16,
      "min_log_p2e_value": -937.6111070823506,
      "min_p2e_float": 0.0,
      "n_calibration": 100,
      "p2e_set_count": 96,
      "p2e_strictly_positive": true,
      "p_set_count": 96,
      "rank_count": 101,
      "s": 0.0547029702970297,
      "set_mismatches": 0
    },
    {
      "C": 1047.6009614158088,
      "alpha": 0.1,
      "classic_control_extra_members": {
        "linear": 10,
        "log": 10,
        "sqrt": 10
      },
      "exact_e_expectation": 0.9999999999999997,
      "expectation_abs_error": 3.3306690738754696e-16,
      "min_log_p2e_value": -935.8613995512967,
      "min_p2e_float": 0.0,
      "n_calibration": 100,
      "p2e_set_count": 91,
      "p2e_strictly_positive": true,
      "p_set_count": 91,
      "rank_count": 101,
      "s": 0.10445544554455446,
      "set_mismatches": 0
    },
    {
      "C": 1173.9359776490273,
      "alpha": 0.2,
      "classic_control_extra_members": {
        "linear": 20,
        "log": 20,
        "sqrt": 18
      },
      "exact_e_expectation": 1.0,
      "expectation_abs_error": 0.0,
      "min_log_p2e_value": -932.8805695383451,
      "min_p2e_float": 0.0,
      "n_calibration": 100,
      "p2e_set_count": 81,
      "p2e_strictly_positive": true,
      "p_set_count": 81,
      "rank_count": 101,
      "s": 0.20396039603960398,
      "set_mismatches": 0
    },
    {
      "C": 2259.7933820517146,
      "alpha": 0.05,
      "classic_control_extra_members": {
        "linear": 10,
        "log": 10,
        "sqrt": 10
      },
      "exact_e_expectation": 1.0,
      "expectation_abs_error": 0.0,
      "min_log_p2e_value": -2138.46288999339,
      "min_p2e_float": 0.0,
      "n_calibration": 200,
      "p2e_set_count": 191,
      "p2e_strictly_positive": true,
      "p_set_count": 191,
      "rank_count": 201,
      "s": 0.05236318407960199,
      "set_mismatches": 0
    },
    {
      "C": 2381.8015587265536,
      "alpha": 0.1,
      "classic_control_extra_members": {
        "linear": 20,
        "log": 20,
        "sqrt": 19
      },
      "exact_e_expectation": 0.9999999999999996,
      "expectation_abs_error": 4.440892098500626e-16,
      "min_log_p2e_value": -2135.9816053515365,
      "min_p2e_float": 0.0,
      "n_calibration": 200,
      "p2e_set_count": 181,
      "p2e_strictly_positive": true,
      "p_set_count": 181,
      "rank_count": 201,
      "s": 0.10223880597014925,
      "set_mismatches": 0
    },
    {
      "C": 2673.951166476484,
      "alpha": 0.2,
      "classic_control_extra_members": {
        "linear": 40,
        "log": 39,
        "sqrt": 35
      },
      "exact_e_expectation": 0.9999999999999999,
      "expectation_abs_error": 1.1102230246251565e-16,
      "min_log_p2e_value": -2132.225324897319,
      "min_p2e_float": 0.0,
      "n_calibration": 200,
      "p2e_set_count": 161,
      "p2e_strictly_positive": true,
      "p_set_count": 161,
      "rank_count": 201,
      "s": 0.2019900497512438,
      "set_mismatches": 0
    }
  ],
  "implementation": "independent finite-rank construction",
  "paper": "jNv4sl4YZH / arXiv:2606.03600",
  "summary": {
    "all_classic_controls_inflate_sets": true,
    "all_exact_e_expectations_pass": true,
    "all_positive_pass": true,
    "all_set_identities_pass": true,
    "case_count": 18,
    "classic_control_case_count": 17
  }
}

````


````output
{"all_classic_controls_inflate_sets": true, "all_exact_e_expectations_pass": true, "all_positive_pass": true, "all_set_identities_pass": true, "case_count": 18, "classic_control_case_count": 17}

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_1de5cec4259a", "created_at": "2026-07-18T12:24:10+00:00", "title": "Pinned source cross-check", "command": ["python", "repro/src/crosscheck_source_p2e.py", "--source", "upstream", "--output", "outputs/claim1_source_crosscheck.json"], "exit_code": 0, "duration_s": 2.413}
-->
````bash
$ python repro/src/crosscheck_source_p2e.py --source upstream --output outputs/claim1_source_crosscheck.json
````

exit 0 · 2.4s


````python title=crosscheck_source_p2e.py
#!/usr/bin/env python3
"""Cross-check the pinned author P2E helper without using it as verification."""

from __future__ import annotations

import argparse
import importlib
import json
import math
import sys
from pathlib import Path

from verify_p2e_identity import p2e_log_value, p2e_parameters


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    sys.path.insert(0, str(args.source / "e-ca"))
    source_utils = importlib.import_module("utils")
    rows = []
    for n_calibration in (10, 20, 30, 50, 100, 200):
        for alpha in (0.05, 0.1, 0.2):
            source_c, source_s = source_utils.get_C_s(alpha, n_calibration)
            source_fn = source_utils.get_p_to_e("P2E", alpha, n_calibration)
            clean_c, clean_s = p2e_parameters(n_calibration, alpha)
            ranks = [j / (n_calibration + 1) for j in range(1, n_calibration + 2)]
            source_values = [float(source_fn(rank)) for rank in ranks]
            source_members = [value < 1.0 / alpha for value in source_values]
            p_members = [rank > alpha for rank in ranks]
            clean_members = [
                p2e_log_value(rank, alpha, clean_c, clean_s) < -math.log(alpha)
                for rank in ranks
            ]
            rows.append(
                {
                    "n_calibration": n_calibration,
                    "alpha": alpha,
                    "source_C": source_c,
                    "source_s": source_s,
                    "source_mean_e": sum(source_values) / len(source_values),
                    "source_set_mismatches": sum(a != b for a, b in zip(source_members, p_members)),
                    "cleanroom_set_mismatches": sum(a != b for a, b in zip(clean_members, p_members)),
                    "source_float_underflow_count": sum(value == 0.0 for value in source_values),
                }
            )

    result = {
        "source": str(args.source),
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "all_source_membership_pass": all(row["source_set_mismatches"] == 0 for row in rows),
            "all_source_expectations_pass": all(abs(row["source_mean_e"] - 1.0) < 1e-11 for row in rows),
            "all_cleanroom_membership_pass": all(row["cleanroom_set_mismatches"] == 0 for row in rows),
            "underflow_is_documented": any(row["source_float_underflow_count"] > 0 for row in rows),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()

````


````json title=claim1_source_crosscheck.json
{
  "rows": [
    {
      "alpha": 0.05,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 10,
      "source_C": 33.79194024116984,
      "source_float_underflow_count": 0,
      "source_mean_e": 1.0000000000000002,
      "source_s": 0.07250000000000001,
      "source_set_mismatches": 0
    },
    {
      "alpha": 0.1,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 10,
      "source_C": 68.11548520237208,
      "source_float_underflow_count": 0,
      "source_mean_e": 1.0000000000000002,
      "source_s": 0.14500000000000002,
      "source_set_mismatches": 0
    },
    {
      "alpha": 0.2,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 10,
      "source_C": 70.2132429606004,
      "source_float_underflow_count": 0,
      "source_mean_e": 0.9999999999999999,
      "source_s": 0.24,
      "source_set_mismatches": 0
    },
    {
      "alpha": 0.05,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 20,
      "source_C": 153.1638207934431,
      "source_float_underflow_count": 0,
      "source_mean_e": 0.9999999999999998,
      "source_s": 0.07488095238095238,
      "source_set_mismatches": 0
    },
    {
      "alpha": 0.1,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 20,
      "source_C": 148.9403555297182,
      "source_float_underflow_count": 0,
      "source_mean_e": 1.0,
      "source_s": 0.12357142857142858,
      "source_set_mismatches": 0
    },
    {
      "alpha": 0.2,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 20,
      "source_C": 158.63182229120778,
      "source_float_underflow_count": 0,
      "source_mean_e": 0.9999999999999998,
      "source_s": 0.22095238095238096,
      "source_set_mismatches": 0
    },
    {
      "alpha": 0.05,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 30,
      "source_C": 171.33773647550407,
      "source_float_underflow_count": 0,
      "source_mean_e": 0.9999999999999998,
      "source_s": 0.057983870967741935,
      "source_set_mismatches": 0
    },
    {
      "alpha": 0.1,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 30,
      "source_C": 238.19898753142024,
      "source_float_underflow_count": 0,
      "source_mean_e": 1.0,
      "source_s": 0.11596774193548387,
      "source_set_mismatches": 0
    },
    {
      "alpha": 0.2,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 30,
      "source_C": 257.23510240678536,
      "source_float_underflow_count": 0,
      "source_mean_e": 0.9999999999999999,
      "source_s": 0.2141935483870968,
      "source_set_mismatches": 0
    },
    {
      "alpha": 0.05,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 50,
      "source_C": 368.68323974534627,
      "source_float_underflow_count": 0,
      "source_mean_e": 1.0,
      "source_s": 0.05485294117647059,
      "source_set_mismatches": 0
    },
    {
      "alpha": 0.1,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 50,
      "source_C": 432.899874439994,
      "source_float_underflow_count": 0,
      "source_mean_e": 0.9999999999999999,
      "source_s": 0.10970588235294118,
      "source_set_mismatches": 0
    },
    {
      "alpha": 0.2,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 50,
      "source_C": 473.6657222193878,
      "source_float_underflow_count": 0,
      "source_mean_e": 1.0,
      "source_s": 0.20862745098039218,
      "source_set_mismatches": 0
    },
    {
      "alpha": 0.05,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 100,
      "source_C": 949.3460610436144,
      "source_float_underflow_count": 17,
      "source_mean_e": 1.0000000000000002,
      "source_s": 0.05517326732673268,
      "source_set_mismatches": 0
    },
    {
      "alpha": 0.1,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 100,
      "source_C": 976.466583244924,
      "source_float_underflow_count": 14,
      "source_mean_e": 0.9999999999999997,
      "source_s": 0.10490099009900991,
      "source_set_mismatches": 0
    },
    {
      "alpha": 0.2,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 100,
      "source_C": 1081.133680479836,
      "source_float_underflow_count": 11,
      "source_mean_e": 1.0000000000000002,
      "source_s": 0.20435643564356437,
      "source_set_mismatches": 0
    },
    {
      "alpha": 0.05,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 200,
      "source_C": 2111.583645546632,
      "source_float_underflow_count": 120,
      "source_mean_e": 1.0000000000000002,
      "source_s": 0.05259950248756219,
      "source_set_mismatches": 0
    },
    {
      "alpha": 0.1,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 200,
      "source_C": 2195.949372184457,
      "source_float_underflow_count": 113,
      "source_mean_e": 1.0,
      "source_s": 0.10246268656716419,
      "source_set_mismatches": 0
    },
    {
      "alpha": 0.2,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 200,
      "source_C": 2448.5110038263592,
      "source_float_underflow_count": 100,
      "source_mean_e": 1.0000000000000002,
      "source_s": 0.20218905472636817,
      "source_set_mismatches": 0
    }
  ],
  "source": "upstream",
  "summary": {
    "all_cleanroom_membership_pass": true,
    "all_source_expectations_pass": true,
    "all_source_membership_pass": true,
    "rows": 18,
    "underflow_is_documented": true
  }
}

````


````output
{"all_cleanroom_membership_pass": true, "all_source_expectations_pass": true, "all_source_membership_pass": true, "rows": 18, "underflow_is_documented": true}

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_ab26a706c48b", "created_at": "2026-07-18T12:24:11+00:00", "title": "Deterministic unit tests", "command": ["python", "-m", "unittest", "discover", "-s", "repro/tests", "-v"], "exit_code": 0, "duration_s": 0.274}
-->
````bash
$ python -m unittest discover -s repro/tests -v
````

exit 0 · 0.3s


````output
test_expected_ccp_raw_cell_count (test_full_protocol.FullProtocolTests.test_expected_ccp_raw_cell_count) ... ok
test_protocol_matches_released_paper_scale (test_full_protocol.FullProtocolTests.test_protocol_matches_released_paper_scale) ... ok
test_classic_calibrator_controls_expand_the_set (test_p2e_identity.P2EIdentityTests.test_classic_calibrator_controls_expand_the_set) ... ok
test_full_grid_summary_passes (test_p2e_identity.P2EIdentityTests.test_full_grid_summary_passes) ... ok
test_p2e_exactly_preserves_each_finite_rank_set (test_p2e_identity.P2EIdentityTests.test_p2e_exactly_preserves_each_finite_rank_set) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.131s

OK

````


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_82e368f04d33", "created_at": "2026-07-18T12:24:38+00:00", "title": "Verified result"}
-->
The independent finite-rank construction evaluated 18 legal `(n, alpha)` cells. It found zero P2E/p-value set-membership mismatches, maximum exact-e expectation error `4.45e-16`, strictly positive mathematical e-values, and set-inflation from each eligible classic log/sqrt/linear control. A separate invocation of pinned author code also passed all 18 membership and expectation checks.


---
<!-- trackio-cell
{"type": "code", "id": "cell_95a10d606142", "created_at": "2026-07-19T16:05:26+00:00", "title": "Theorem-domain finite-rank P2E verification", "command": ["python", "repro/src/verify_p2e_identity.py", "--output", "outputs/claim1_independent.json"], "exit_code": 0, "duration_s": 0.108}
-->
````bash
$ python repro/src/verify_p2e_identity.py --output outputs/claim1_independent.json
````

exit 0 · 0.1s


````python title=verify_p2e_identity.py
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


# Every positive case satisfies the exact domain of the paper's main theorem:
# alpha * (n + 1) is strictly greater than one and is not an integer.  The
# extra (40, .05) cell replaces the earlier off-domain (10, .05) cell while
# retaining a broad 18-cell grid.
THEOREM_CASES = (
    (10, 0.1), (10, 0.2),
    (20, 0.05), (20, 0.1), (20, 0.2),
    (30, 0.05), (30, 0.1), (30, 0.2),
    (40, 0.05),
    (50, 0.05), (50, 0.1), (50, 0.2),
    (100, 0.05), (100, 0.1), (100, 0.2),
    (200, 0.05), (200, 0.1), (200, 0.2),
)
EXCLUDED_DOMAIN_CASES = (
    (10, 0.05),  # alpha(n+1) < 1
    (9, 0.1),    # alpha(n+1) = 1
    (19, 0.05),  # remaining cases land exactly on a conformal rank
    (19, 0.1),
    (19, 0.2),
)


def in_theorem_domain(n_calibration: int, alpha: float) -> bool:
    if n_calibration < 1 or not 0.0 < alpha < 1.0:
        return False
    scaled_level = alpha * (n_calibration + 1)
    return scaled_level > 1.0 and not math.isclose(
        scaled_level, round(scaled_level), rel_tol=0.0, abs_tol=1e-12
    )


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
    if not in_theorem_domain(n_calibration, alpha):
        raise ValueError(
            "paper theorem requires alpha*(n_calibration+1) > 1 and non-integer"
        )

    denominator = n_calibration + 1
    first_above = math.ceil(alpha * denominator)
    upper_rank = first_above / denominator
    if not alpha < upper_rank:
        raise RuntimeError("the theorem-domain check admitted a rank boundary")
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
        "alpha_times_rank_count": alpha * (n_calibration + 1),
        "theorem_domain_verified": in_theorem_domain(n_calibration, alpha),
        "C": c,
        "s": s,
        "rank_count": len(ranks),
        "p_set_count": sum(p_members),
        "p2e_set_count": sum(e_members),
        "set_mismatches": mismatches,
        "threshold_log_error": abs(
            p2e_log_value(alpha, alpha, c, s) + math.log(alpha)
        ),
        "exact_e_expectation": expectation,
        "expectation_abs_error": abs(expectation - 1.0),
        "p2e_strictly_positive": all(math.isfinite(value) for value in log_p2e_values),
        "min_log_p2e_value": min(log_p2e_values),
        "min_p2e_float": min(p_values),
        "classic_control_extra_members": controls,
    }


def run_cases(
    cases: Iterable[tuple[int, float]] = THEOREM_CASES,
) -> dict[str, object]:
    rows = [evaluate_case(n, alpha) for n, alpha in cases]
    domain_controls = []
    for n_calibration, alpha in EXCLUDED_DOMAIN_CASES:
        rejected = False
        try:
            p2e_parameters(n_calibration, alpha)
        except ValueError:
            rejected = True
        domain_controls.append(
            {
                "n_calibration": n_calibration,
                "alpha": alpha,
                "alpha_times_rank_count": alpha * (n_calibration + 1),
                "rejected": rejected,
            }
        )
    all_identity = all(row["set_mismatches"] == 0 for row in rows)
    all_exact = all(float(row["expectation_abs_error"]) < 1e-11 for row in rows)
    all_thresholds = all(float(row["threshold_log_error"]) < 1e-14 for row in rows)
    all_positive = all(bool(row["p2e_strictly_positive"]) for row in rows)
    control_rows = [row for row in rows if row["p_set_count"] < row["rank_count"]]
    controls_inflate = bool(control_rows) and all(
        all(extra > 0 for extra in dict(row["classic_control_extra_members"]).values())
        for row in control_rows
    )
    return {
        "paper": "jNv4sl4YZH / arXiv:2606.03600",
        "implementation": "independent finite-rank construction",
        "theorem_domain": "alpha*(n+1) in (1, infinity) and non-integer",
        "cases": rows,
        "domain_controls": domain_controls,
        "summary": {
            "case_count": len(rows),
            "domain_control_count": len(domain_controls),
            "all_theorem_domain_verified": all(
                bool(row["theorem_domain_verified"]) for row in rows
            ),
            "all_domain_controls_rejected": all(
                bool(row["rejected"]) for row in domain_controls
            ),
            "all_set_identities_pass": all_identity,
            "all_threshold_identities_pass": all_thresholds,
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

````


````json title=claim1_independent.json
{
  "cases": [
    {
      "C": 65.07722023316114,
      "alpha": 0.1,
      "alpha_times_rank_count": 1.1,
      "classic_control_extra_members": {
        "linear": 1,
        "log": 1,
        "sqrt": 1
      },
      "exact_e_expectation": 0.9999999999999997,
      "expectation_abs_error": 3.3306690738754696e-16,
      "min_log_p2e_value": -53.53719987644119,
      "min_p2e_float": 5.611636315886701e-24,
      "n_calibration": 10,
      "p2e_set_count": 10,
      "p2e_strictly_positive": true,
      "p_set_count": 10,
      "rank_count": 11,
      "s": 0.14090909090909093,
      "set_mismatches": 0,
      "theorem_domain_verified": true,
      "threshold_log_error": 0.0
    },
    {
      "C": 71.7312565275491,
      "alpha": 0.2,
      "alpha_times_rank_count": 2.2,
      "classic_control_extra_members": {
        "linear": 2,
        "log": 2,
        "sqrt": 2
      },
      "exact_e_expectation": 1.0000000000000002,
      "expectation_abs_error": 2.220446049250313e-16,
      "min_log_p2e_value": -53.09609242691801,
      "min_p2e_float": 8.722883020888222e-24,
      "n_calibration": 10,
      "p2e_set_count": 9,
      "p2e_strictly_positive": true,
      "p_set_count": 9,
      "rank_count": 11,
      "s": 0.23636363636363636,
      "set_mismatches": 0,
      "theorem_domain_verified": true,
      "threshold_log_error": 0.0
    },
    {
      "C": 143.44819268231788,
      "alpha": 0.05,
      "alpha_times_rank_count": 1.05,
      "classic_control_extra_members": {
        "linear": 1,
        "log": 1,
        "sqrt": 1
      },
      "exact_e_expectation": 1.0000000000000002,
      "expectation_abs_error": 2.220446049250313e-16,
      "min_log_p2e_value": -129.99714811937724,
      "min_p2e_float": 3.4910487108230056e-57,
      "n_calibration": 20,
      "p2e_set_count": 20,
      "p2e_strictly_positive": true,
      "p_set_count": 20,
      "rank_count": 21,
      "s": 0.07261904761904761,
      "set_mismatches": 0,
      "theorem_domain_verified": true,
      "threshold_log_error": 0.0
    },
    {
      "C": 150.24495454452904,
      "alpha": 0.1,
      "alpha_times_rank_count": 2.1,
      "classic_control_extra_members": {
        "linear": 2,
        "log": 2,
        "sqrt": 2
      },
      "exact_e_expectation": 0.9999999999999998,
      "expectation_abs_error": 2.220446049250313e-16,
      "min_log_p2e_value": -129.65914387856117,
      "min_p2e_float": 4.8949615553935044e-57,
      "n_calibration": 20,
      "p2e_set_count": 19,
      "p2e_strictly_positive": true,
      "p_set_count": 19,
      "rank_count": 21,
      "s": 0.12142857142857143,
      "set_mismatches": 0,
      "theorem_domain_verified": true,
      "threshold_log_error": 0.0
    },
    {
      "C": 166.72966641514466,
      "alpha": 0.2,
      "alpha_times_rank_count": 4.2,
      "classic_control_extra_members": {
        "linear": 4,
        "log": 4,
        "sqrt": 4
      },
      "exact_e_expectation": 1.0,
      "expectation_abs_error": 0.0,
      "min_log_p2e_value": -128.55757993160344,
      "min_p2e_float": 1.4728293460185009e-56,
      "n_calibration": 20,
      "p2e_set_count": 17,
      "p2e_strictly_positive": true,
      "p_set_count": 17,
      "rank_count": 21,
      "s": 0.21904761904761905,
      "set_mismatches": 0,
      "theorem_domain_verified": true,
      "threshold_log_error": 0.0
    },
    {
      "C": 174.17299719890627,
      "alpha": 0.05,
      "alpha_times_rank_count": 1.55,
      "classic_control_extra_members": {
        "linear": 1,
        "log": 1,
        "sqrt": 1
      },
      "exact_e_expectation": 1.0000000000000002,
      "expectation_abs_error": 2.220446049250313e-16,
      "min_log_p2e_value": -160.95566300543248,
      "min_p2e_float": 1.2526903320528512e-70,
      "n_calibration": 30,
      "p2e_set_count": 30,
      "p2e_strictly_positive": true,
      "p_set_count": 30,
      "rank_count": 31,
      "s": 0.05725806451612903,
      "set_mismatches": 0,
      "theorem_domain_verified": true,
      "threshold_log_error": 0.0
    },
    {
      "C": 245.7194104724462,
      "alpha": 0.1,
      "alpha_times_rank_count": 3.1,
      "classic_control_extra_members": {
        "linear": 3,
        "log": 3,
        "sqrt": 3
      },
      "exact_e_expectation": 1.0000000000000002,
      "expectation_abs_error": 2.220446049250313e-16,
      "min_log_p2e_value": -215.2501377324065,
      "min_p2e_float": 3.296499042243523e-94,
      "n_calibration": 30,
      "p2e_set_count": 28,
      "p2e_strictly_positive": true,
      "p_set_count": 28,
      "rank_count": 31,
      "s": 0.11451612903225807,
      "set_mismatches": 0,
      "theorem_domain_verified": true,
      "threshold_log_error": 0.0
    },
    {
      "C": 273.57509255601883,
      "alpha": 0.2,
      "alpha_times_rank_count": 6.2,
      "classic_control_extra_members": {
        "linear": 6,
        "log": 6,
        "sqrt": 6
      },
      "exact_e_expectation": 0.9999999999999999,
      "expectation_abs_error": 1.1102230246251565e-16,
      "min_log_p2e_value": -213.69175123664013,
      "min_p2e_float": 1.5662158319679543e-93,
      "n_calibration": 30,
      "p2e_set_count": 25,
      "p2e_strictly_positive": true,
      "p_set_count": 25,
      "rank_count": 31,
      "s": 0.2129032258064516,
      "set_mismatches": 0,
      "theorem_domain_verified": true,
      "threshold_log_error": 0.0
    },
    {
      "C": 331.51487676742806,
      "alpha": 0.05,
      "alpha_times_rank_count": 2.0500000000000003,
      "classic_control_extra_members": {
        "linear": 2,
        "log": 2,
        "sqrt": 2
      },
      "exact_e_expectation": 1.0000000000000002,
      "expectation_abs_error": 2.220446049250313e-16,
      "min_log_p2e_value": -308.0814288192058,
      "min_p2e_float": 1.5919722271242303e-134,
      "n_calibration": 40,
      "p2e_set_count": 39,
      "p2e_strictly_positive": true,
      "p_set_count": 39,
      "rank_count": 41,
      "s": 0.061585365853658536,
      "set_mismatches": 0,
      "theorem_domain_verified": true,
      "threshold_log_error": 0.0
    },
    {
      "C": 383.14005814359837,
      "alpha": 0.05,
      "alpha_times_rank_count": 2.5500000000000003,
      "classic_control_extra_members": {
        "linear": 2,
        "log": 2,
        "sqrt": 2
      },
      "exact_e_expectation": 1.0,
      "expectation_abs_error": 0.0,
      "min_log_p2e_value": -359.12771238068956,
      "min_p2e_float": 1.0784902283322196e-156,
      "n_calibration": 50,
      "p2e_set_count": 49,
      "p2e_strictly_positive": true,
      "p_set_count": 49,
      "rank_count": 51,
      "s": 0.054411764705882354,
      "set_mismatches": 0,
      "theorem_domain_verified": true,
      "threshold_log_error": 0.0
    },
    {
      "C": 455.93837460449174,
      "alpha": 0.1,
      "alpha_times_rank_count": 5.1000000000000005,
      "classic_control_extra_members": {
        "linear": 5,
        "log": 5,
        "sqrt": 5
      },
      "exact_e_expectation": 0.9999999999999996,
      "expectation_abs_error": 4.440892098500626e-16,
      "min_log_p2e_value": -404.0012252580513,
      "min_p2e_float": 3.503460200719301e-176,
      "n_calibration": 50,
      "p2e_set_count": 46,
      "p2e_strictly_positive": true,
      "p_set_count": 46,
      "rank_count": 51,
      "s": 0.10882352941176471,
      "set_mismatches": 0,
      "theorem_domain_verified": true,
      "threshold_log_error": 0.0
    },
    {
      "C": 509.3275927243293,
      "alpha": 0.2,
      "alpha_times_rank_count": 10.200000000000001,
      "classic_control_extra_members": {
        "linear": 10,
        "log": 10,
        "sqrt": 9
      },
      "exact_e_expectation": 1.0000000000000002,
      "expectation_abs_error": 2.220446049250313e-16,
      "min_log_p2e_value": -401.8396650202642,
      "min_p2e_float": 3.0426421118437186e-175,
      "n_calibration": 50,
      "p2e_set_count": 41,
      "p2e_strictly_positive": true,
      "p_set_count": 41,
      "rank_count": 51,
      "s": 0.20784313725490197,
      "set_mismatches": 0,
      "theorem_domain_verified": true,
      "threshold_log_error": 0.0
    },
    {
      "C": 995.0481689379562,
      "alpha": 0.05,
      "alpha_times_rank_count": 5.050000000000001,
      "classic_control_extra_members": {
        "linear": 5,
        "log": 5,
        "sqrt": 5
      },
      "exact_e_expectation": 1.0000000000000002,
      "expectation_abs_error": 2.220446049250313e-16,
      "min_log_p2e_value": -937.6111070823506,
      "min_p2e_float": 0.0,
      "n_calibration": 100,
      "p2e_set_count": 96,
      "p2e_strictly_positive": true,
      "p_set_count": 96,
      "rank_count": 101,
      "s": 0.0547029702970297,
      "set_mismatches": 0,
      "theorem_domain_verified": true,
      "threshold_log_error": 0.0
    },
    {
      "C": 1047.6009614158088,
      "alpha": 0.1,
      "alpha_times_rank_count": 10.100000000000001,
      "classic_control_extra_members": {
        "linear": 10,
        "log": 10,
        "sqrt": 10
      },
      "exact_e_expectation": 0.9999999999999997,
      "expectation_abs_error": 3.3306690738754696e-16,
      "min_log_p2e_value": -935.8613995512967,
      "min_p2e_float": 0.0,
      "n_calibration": 100,
      "p2e_set_count": 91,
      "p2e_strictly_positive": true,
      "p_set_count": 91,
      "rank_count": 101,
      "s": 0.10445544554455446,
      "set_mismatches": 0,
      "theorem_domain_verified": true,
      "threshold_log_error": 0.0
    },
    {
      "C": 1173.9359776490273,
      "alpha": 0.2,
      "alpha_times_rank_count": 20.200000000000003,
      "classic_control_extra_members": {
        "linear": 20,
        "log": 20,
        "sqrt": 18
      },
      "exact_e_expectation": 1.0,
      "expectation_abs_error": 0.0,
      "min_log_p2e_value": -932.8805695383451,
      "min_p2e_float": 0.0,
      "n_calibration": 100,
      "p2e_set_count": 81,
      "p2e_strictly_positive": true,
      "p_set_count": 81,
      "rank_count": 101,
      "s": 0.20396039603960398,
      "set_mismatches": 0,
      "theorem_domain_verified": true,
      "threshold_log_error": 0.0
    },
    {
      "C": 2259.7933820517146,
      "alpha": 0.05,
      "alpha_times_rank_count": 10.05,
      "classic_control_extra_members": {
        "linear": 10,
        "log": 10,
        "sqrt": 10
      },
      "exact_e_expectation": 1.0,
      "expectation_abs_error": 0.0,
      "min_log_p2e_value": -2138.46288999339,
      "min_p2e_float": 0.0,
      "n_calibration": 200,
      "p2e_set_count": 191,
      "p2e_strictly_positive": true,
      "p_set_count": 191,
      "rank_count": 201,
      "s": 0.05236318407960199,
      "set_mismatches": 0,
      "theorem_domain_verified": true,
      "threshold_log_error": 0.0
    },
    {
      "C": 2381.8015587265536,
      "alpha": 0.1,
      "alpha_times_rank_count": 20.1,
      "classic_control_extra_members": {
        "linear": 20,
        "log": 20,
        "sqrt": 19
      },
      "exact_e_expectation": 0.9999999999999996,
      "expectation_abs_error": 4.440892098500626e-16,
      "min_log_p2e_value": -2135.9816053515365,
      "min_p2e_float": 0.0,
      "n_calibration": 200,
      "p2e_set_count": 181,
      "p2e_strictly_positive": true,
      "p_set_count": 181,
      "rank_count": 201,
      "s": 0.10223880597014925,
      "set_mismatches": 0,
      "theorem_domain_verified": true,
      "threshold_log_error": 0.0
    },
    {
      "C": 2673.951166476484,
      "alpha": 0.2,
      "alpha_times_rank_count": 40.2,
      "classic_control_extra_members": {
        "linear": 40,
        "log": 39,
        "sqrt": 35
      },
      "exact_e_expectation": 0.9999999999999999,
      "expectation_abs_error": 1.1102230246251565e-16,
      "min_log_p2e_value": -2132.225324897319,
      "min_p2e_float": 0.0,
      "n_calibration": 200,
      "p2e_set_count": 161,
      "p2e_strictly_positive": true,
      "p_set_count": 161,
      "rank_count": 201,
      "s": 0.2019900497512438,
      "set_mismatches": 0,
      "theorem_domain_verified": true,
      "threshold_log_error": 0.0
    }
  ],
  "domain_controls": [
    {
      "alpha": 0.05,
      "alpha_times_rank_count": 0.55,
      "n_calibration": 10,
      "rejected": true
    },
    {
      "alpha": 0.1,
      "alpha_times_rank_count": 1.0,
      "n_calibration": 9,
      "rejected": true
    },
    {
      "alpha": 0.05,
      "alpha_times_rank_count": 1.0,
      "n_calibration": 19,
      "rejected": true
    },
    {
      "alpha": 0.1,
      "alpha_times_rank_count": 2.0,
      "n_calibration": 19,
      "rejected": true
    },
    {
      "alpha": 0.2,
      "alpha_times_rank_count": 4.0,
      "n_calibration": 19,
      "rejected": true
    }
  ],
  "implementation": "independent finite-rank construction",
  "paper": "jNv4sl4YZH / arXiv:2606.03600",
  "summary": {
    "all_classic_controls_inflate_sets": true,
    "all_domain_controls_rejected": true,
    "all_exact_e_expectations_pass": true,
    "all_positive_pass": true,
    "all_set_identities_pass": true,
    "all_theorem_domain_verified": true,
    "all_threshold_identities_pass": true,
    "case_count": 18,
    "classic_control_case_count": 18,
    "domain_control_count": 5
  },
  "theorem_domain": "alpha*(n+1) in (1, infinity) and non-integer"
}

````


````output
{"all_classic_controls_inflate_sets": true, "all_domain_controls_rejected": true, "all_exact_e_expectations_pass": true, "all_positive_pass": true, "all_set_identities_pass": true, "all_theorem_domain_verified": true, "all_threshold_identities_pass": true, "case_count": 18, "classic_control_case_count": 18, "domain_control_count": 5}

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_36d67edd1131", "created_at": "2026-07-19T16:05:29+00:00", "title": "Theorem-domain pinned source cross-check", "command": ["python", "repro/src/crosscheck_source_p2e.py", "--source", "upstream", "--output", "outputs/claim1_source_crosscheck.json"], "exit_code": 0, "duration_s": 2.387}
-->
````bash
$ python repro/src/crosscheck_source_p2e.py --source upstream --output outputs/claim1_source_crosscheck.json
````

exit 0 · 2.4s


````python title=crosscheck_source_p2e.py
#!/usr/bin/env python3
"""Cross-check the pinned author P2E helper without using it as verification."""

from __future__ import annotations

import argparse
import importlib
import json
import math
import sys
from pathlib import Path

from verify_p2e_identity import THEOREM_CASES, p2e_log_value, p2e_parameters


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    sys.path.insert(0, str(args.source / "e-ca"))
    source_utils = importlib.import_module("utils")
    rows = []
    for n_calibration, alpha in THEOREM_CASES:
        source_c, source_s = source_utils.get_C_s(alpha, n_calibration)
        source_fn = source_utils.get_p_to_e("P2E", alpha, n_calibration)
        clean_c, clean_s = p2e_parameters(n_calibration, alpha)
        ranks = [j / (n_calibration + 1) for j in range(1, n_calibration + 2)]
        source_values = [float(source_fn(rank)) for rank in ranks]
        source_members = [value < 1.0 / alpha for value in source_values]
        p_members = [rank > alpha for rank in ranks]
        clean_members = [
            p2e_log_value(rank, alpha, clean_c, clean_s) < -math.log(alpha)
            for rank in ranks
        ]
        rows.append(
            {
                "n_calibration": n_calibration,
                "alpha": alpha,
                "theorem_domain_verified": True,
                "source_C": source_c,
                "source_s": source_s,
                "source_mean_e": sum(source_values) / len(source_values),
                "source_set_mismatches": sum(a != b for a, b in zip(source_members, p_members)),
                "cleanroom_set_mismatches": sum(a != b for a, b in zip(clean_members, p_members)),
                "source_float_underflow_count": sum(value == 0.0 for value in source_values),
            }
        )

    result = {
        "source": str(args.source),
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "all_theorem_domain_verified": all(
                row["theorem_domain_verified"] for row in rows
            ),
            "all_source_membership_pass": all(row["source_set_mismatches"] == 0 for row in rows),
            "all_source_expectations_pass": all(abs(row["source_mean_e"] - 1.0) < 1e-11 for row in rows),
            "all_cleanroom_membership_pass": all(row["cleanroom_set_mismatches"] == 0 for row in rows),
            "underflow_is_documented": any(row["source_float_underflow_count"] > 0 for row in rows),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()

````


````json title=claim1_source_crosscheck.json
{
  "rows": [
    {
      "alpha": 0.1,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 10,
      "source_C": 68.11548520237208,
      "source_float_underflow_count": 0,
      "source_mean_e": 1.0000000000000002,
      "source_s": 0.14500000000000002,
      "source_set_mismatches": 0,
      "theorem_domain_verified": true
    },
    {
      "alpha": 0.2,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 10,
      "source_C": 70.2132429606004,
      "source_float_underflow_count": 0,
      "source_mean_e": 0.9999999999999999,
      "source_s": 0.24,
      "source_set_mismatches": 0,
      "theorem_domain_verified": true
    },
    {
      "alpha": 0.05,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 20,
      "source_C": 153.1638207934431,
      "source_float_underflow_count": 0,
      "source_mean_e": 0.9999999999999998,
      "source_s": 0.07488095238095238,
      "source_set_mismatches": 0,
      "theorem_domain_verified": true
    },
    {
      "alpha": 0.1,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 20,
      "source_C": 148.9403555297182,
      "source_float_underflow_count": 0,
      "source_mean_e": 1.0,
      "source_s": 0.12357142857142858,
      "source_set_mismatches": 0,
      "theorem_domain_verified": true
    },
    {
      "alpha": 0.2,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 20,
      "source_C": 158.63182229120778,
      "source_float_underflow_count": 0,
      "source_mean_e": 0.9999999999999998,
      "source_s": 0.22095238095238096,
      "source_set_mismatches": 0,
      "theorem_domain_verified": true
    },
    {
      "alpha": 0.05,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 30,
      "source_C": 171.33773647550407,
      "source_float_underflow_count": 0,
      "source_mean_e": 0.9999999999999998,
      "source_s": 0.057983870967741935,
      "source_set_mismatches": 0,
      "theorem_domain_verified": true
    },
    {
      "alpha": 0.1,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 30,
      "source_C": 238.19898753142024,
      "source_float_underflow_count": 0,
      "source_mean_e": 1.0,
      "source_s": 0.11596774193548387,
      "source_set_mismatches": 0,
      "theorem_domain_verified": true
    },
    {
      "alpha": 0.2,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 30,
      "source_C": 257.23510240678536,
      "source_float_underflow_count": 0,
      "source_mean_e": 0.9999999999999999,
      "source_s": 0.2141935483870968,
      "source_set_mismatches": 0,
      "theorem_domain_verified": true
    },
    {
      "alpha": 0.05,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 40,
      "source_C": 332.368003712594,
      "source_float_underflow_count": 0,
      "source_mean_e": 1.0000000000000002,
      "source_s": 0.06274390243902439,
      "source_set_mismatches": 0,
      "theorem_domain_verified": true
    },
    {
      "alpha": 0.05,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 50,
      "source_C": 368.68323974534627,
      "source_float_underflow_count": 0,
      "source_mean_e": 1.0,
      "source_s": 0.05485294117647059,
      "source_set_mismatches": 0,
      "theorem_domain_verified": true
    },
    {
      "alpha": 0.1,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 50,
      "source_C": 432.899874439994,
      "source_float_underflow_count": 0,
      "source_mean_e": 0.9999999999999999,
      "source_s": 0.10970588235294118,
      "source_set_mismatches": 0,
      "theorem_domain_verified": true
    },
    {
      "alpha": 0.2,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 50,
      "source_C": 473.6657222193878,
      "source_float_underflow_count": 0,
      "source_mean_e": 1.0,
      "source_s": 0.20862745098039218,
      "source_set_mismatches": 0,
      "theorem_domain_verified": true
    },
    {
      "alpha": 0.05,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 100,
      "source_C": 949.3460610436144,
      "source_float_underflow_count": 17,
      "source_mean_e": 1.0000000000000002,
      "source_s": 0.05517326732673268,
      "source_set_mismatches": 0,
      "theorem_domain_verified": true
    },
    {
      "alpha": 0.1,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 100,
      "source_C": 976.466583244924,
      "source_float_underflow_count": 14,
      "source_mean_e": 0.9999999999999997,
      "source_s": 0.10490099009900991,
      "source_set_mismatches": 0,
      "theorem_domain_verified": true
    },
    {
      "alpha": 0.2,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 100,
      "source_C": 1081.133680479836,
      "source_float_underflow_count": 11,
      "source_mean_e": 1.0000000000000002,
      "source_s": 0.20435643564356437,
      "source_set_mismatches": 0,
      "theorem_domain_verified": true
    },
    {
      "alpha": 0.05,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 200,
      "source_C": 2111.583645546632,
      "source_float_underflow_count": 120,
      "source_mean_e": 1.0000000000000002,
      "source_s": 0.05259950248756219,
      "source_set_mismatches": 0,
      "theorem_domain_verified": true
    },
    {
      "alpha": 0.1,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 200,
      "source_C": 2195.949372184457,
      "source_float_underflow_count": 113,
      "source_mean_e": 1.0,
      "source_s": 0.10246268656716419,
      "source_set_mismatches": 0,
      "theorem_domain_verified": true
    },
    {
      "alpha": 0.2,
      "cleanroom_set_mismatches": 0,
      "n_calibration": 200,
      "source_C": 2448.5110038263592,
      "source_float_underflow_count": 100,
      "source_mean_e": 1.0000000000000002,
      "source_s": 0.20218905472636817,
      "source_set_mismatches": 0,
      "theorem_domain_verified": true
    }
  ],
  "source": "upstream",
  "summary": {
    "all_cleanroom_membership_pass": true,
    "all_source_expectations_pass": true,
    "all_source_membership_pass": true,
    "all_theorem_domain_verified": true,
    "rows": 18,
    "underflow_is_documented": true
  }
}

````


````output
{"all_cleanroom_membership_pass": true, "all_source_expectations_pass": true, "all_source_membership_pass": true, "all_theorem_domain_verified": true, "rows": 18, "underflow_is_documented": true}

````
