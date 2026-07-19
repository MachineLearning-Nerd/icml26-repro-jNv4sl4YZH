#!/usr/bin/env python3
"""Independent finite enumeration of the e-merge coverage mechanism.

For independent discrete conformal ranks, each clean-room P2E value has exact
mean one. Their arithmetic merge is consequently an e-value.  This checker
enumerates every rank tuple in small non-trivial configurations and verifies
the Markov prediction-set event directly.  It is a mechanism check for Claim
3, not a substitute for the released 100-seed empirical CCP protocol.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix

try:  # Supports both ``python repro/src/...`` and package-based test imports.
    from .verify_p2e_identity import p2e_parameters, p2e_value
except ImportError:  # pragma: no cover - exercised by the CLI entry point.
    from verify_p2e_identity import p2e_parameters, p2e_value


def worst_case_tail_probability(
    values: list[float],
    folds: int,
    threshold: float,
    *,
    weights: tuple[float, ...] | None = None,
    adaptive_max: bool = False,
) -> tuple[float, int]:
    """Maximize threshold failure over all couplings with uniform marginals."""
    if weights is None:
        weights = tuple(1.0 / folds for _ in range(folds))
    if len(weights) != folds or any(weight < 0.0 for weight in weights):
        raise ValueError("weights must be nonnegative and match the fold count")
    if abs(sum(weights) - 1.0) > 1e-12:
        raise ValueError("weights must sum to one")
    rank_tuples = np.asarray(
        list(itertools.product(range(len(values)), repeat=folds)), dtype=np.int16
    )
    tuple_values = np.asarray(values)[rank_tuples]
    merged = (
        tuple_values.max(axis=1)
        if adaptive_max
        else tuple_values @ np.asarray(weights, dtype=float)
    )
    failure_indicator = (merged >= threshold).astype(float)
    constraints = lil_matrix(
        (folds * len(values), len(rank_tuples)), dtype=float
    )
    for fold in range(folds):
        for rank in range(len(values)):
            columns = np.flatnonzero(rank_tuples[:, fold] == rank)
            constraints[fold * len(values) + rank, columns] = 1.0
    marginals = np.full(folds * len(values), 1.0 / len(values))
    solution = linprog(
        -failure_indicator,
        A_eq=constraints.tocsr(),
        b_eq=marginals,
        bounds=(0.0, None),
        method="highs",
    )
    if not solution.success:
        raise RuntimeError(f"coupling LP failed: {solution.message}")
    return float(-solution.fun), len(rank_tuples)


def evaluate_case(
    n_calibration: int,
    alpha: float,
    weights: tuple[float, ...],
) -> dict[str, float | int | bool | list[float]]:
    folds = len(weights)
    c, s = p2e_parameters(n_calibration, alpha)
    ranks = [j / (n_calibration + 1) for j in range(1, n_calibration + 2)]
    values = [p2e_value(rank, alpha, c, s) for rank in ranks]
    tuples = list(itertools.product(values, repeat=folds))
    merged = [sum(weight * value for weight, value in zip(weights, combo)) for combo in tuples]
    scaled_invalid = [2.0 * value for value in merged]
    adaptive_max = [max(combo) for combo in tuples]
    threshold = 1.0 / alpha
    coverage = sum(value < threshold for value in merged) / len(merged)
    invalid_coverage = sum(value < threshold for value in scaled_invalid) / len(scaled_invalid)
    adaptive_coverage = sum(value < threshold for value in adaptive_max) / len(adaptive_max)
    worst_tail, lp_variables = worst_case_tail_probability(
        values, folds, threshold, weights=weights
    )
    invalid_worst_tail, _ = worst_case_tail_probability(
        [2.0 * value for value in values], folds, threshold, weights=weights
    )
    adaptive_worst_tail, _ = worst_case_tail_probability(
        values, folds, threshold, weights=weights, adaptive_max=True
    )
    return {
        "n_calibration": n_calibration,
        "alpha": alpha,
        "folds": folds,
        "weights": list(weights),
        "rank_tuple_count": len(merged),
        "mean_merged_e": sum(merged) / len(merged),
        "mean_merged_e_abs_error": abs(sum(merged) / len(merged) - 1.0),
        "coverage_event_probability": coverage,
        "required_coverage": 1.0 - alpha,
        "coverage_pass": coverage >= 1.0 - alpha,
        "coupling_lp_variables": lp_variables,
        "worst_case_dependent_tail_probability": worst_tail,
        "worst_case_dependent_coverage": 1.0 - worst_tail,
        "arbitrary_dependence_coverage_pass": worst_tail <= alpha + 1e-10,
        "invalid_scaled_coverage": invalid_coverage,
        "invalid_control_rejected": invalid_coverage < 1.0 - alpha,
        "invalid_worst_case_dependent_tail_probability": invalid_worst_tail,
        "invalid_arbitrary_dependence_control_rejected": invalid_worst_tail > alpha + 1e-10,
        "adaptive_max_coverage": adaptive_coverage,
        "adaptive_max_worst_case_dependent_tail_probability": adaptive_worst_tail,
        "adaptive_weight_control_rejected": adaptive_worst_tail > alpha + 1e-10,
    }


def run_cases() -> dict[str, object]:
    cases = [
        # Equal-weight merges explicitly exercise ECCP's released construction.
        evaluate_case(10, 0.1, (0.50, 0.50)),
        evaluate_case(10, 0.1, (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)),
        # Nonuniform, fixed weights exercise tuning-independent WECA.
        evaluate_case(10, 0.1, (0.25, 0.75)),
        evaluate_case(10, 0.1, (0.10, 0.30, 0.60)),
        evaluate_case(10, 0.1, (0.05, 0.15, 0.30, 0.50)),
        evaluate_case(20, 0.1, (0.20, 0.80)),
        evaluate_case(20, 0.1, (0.10, 0.20, 0.70)),
        evaluate_case(20, 0.2, (0.15, 0.35, 0.50)),
    ]
    return {
        "implementation": "independent exact enumeration and coupling LP for fixed weighted e-merges",
        "scope": "fixed or tuning-independent weights; adaptive inference-dependent weights are an invalid control",
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "equal_weight_case_count": sum(
                max(row["weights"]) - min(row["weights"]) < 1e-12 for row in cases
            ),
            "nonuniform_weight_case_count": sum(
                max(row["weights"]) - min(row["weights"]) >= 1e-12 for row in cases
            ),
            "all_merged_expectations_exact": all(row["mean_merged_e_abs_error"] < 1e-11 for row in cases),
            "all_markov_coverage_events_pass": all(row["coverage_pass"] for row in cases),
            "all_arbitrary_dependence_coverage_pass": all(
                row["arbitrary_dependence_coverage_pass"] for row in cases
            ),
            "maximum_valid_worst_case_tail_probability": max(
                row["worst_case_dependent_tail_probability"] for row in cases
            ),
            "maximum_valid_tail_to_alpha_ratio": max(
                row["worst_case_dependent_tail_probability"] / row["alpha"]
                for row in cases
            ),
            "invalid_scaling_control_rejection_count": sum(row["invalid_control_rejected"] for row in cases),
            "invalid_scaling_control_detected": any(row["invalid_control_rejected"] for row in cases),
            "invalid_arbitrary_dependence_rejection_count": sum(
                row["invalid_arbitrary_dependence_control_rejected"] for row in cases
            ),
            "invalid_arbitrary_dependence_detected": any(
                row["invalid_arbitrary_dependence_control_rejected"] for row in cases
            ),
            "adaptive_weight_rejection_count": sum(
                row["adaptive_weight_control_rejected"] for row in cases
            ),
            "adaptive_weight_control_detected": any(
                row["adaptive_weight_control_rejected"] for row in cases
            ),
            "minimum_adaptive_tail_to_alpha_ratio": min(
                row["adaptive_max_worst_case_dependent_tail_probability"] / row["alpha"]
                for row in cases
            ),
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
