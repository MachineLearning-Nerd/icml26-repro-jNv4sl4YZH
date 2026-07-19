# Claim 3


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_6c5d46256087", "created_at": "2026-07-18T12:24:40+00:00", "title": "Full protocol queued"}
-->
**Initial execution plan (2026-07-18; historical):** the full cross-conformal protocol was configured for the three bundled paper datasets with 100 seeds each and the paper fold counts: Boston `K=15`, Abalone `K=15`, Parkinson `K=20`. The source estimators remain unmodified; the wrapper only supplies the paper configuration and persists raw rows for independent aggregation. The authoritative outcome is the later **Claim 3 verdict** cell, which the final gate derives from exactly 11,700 verified raw cells plus the exact mechanism certificate.


---
<!-- trackio-cell
{"type": "code", "id": "cell_fe7ada827530", "created_at": "2026-07-18T12:27:18+00:00", "title": "Independent e-merge coverage enumeration", "command": ["python", "repro/src/verify_e_merge_coverage.py", "--output", "outputs/claim3_independent_e_merge.json"], "exit_code": 0, "duration_s": 0.058}
-->
````bash
$ python repro/src/verify_e_merge_coverage.py --output outputs/claim3_independent_e_merge.json
````

exit 0 · 0.1s


````python title=verify_e_merge_coverage.py
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

try:  # Supports both ``python repro/src/...`` and package-based test imports.
    from .verify_p2e_identity import p2e_parameters, p2e_value
except ImportError:  # pragma: no cover - exercised by the CLI entry point.
    from verify_p2e_identity import p2e_parameters, p2e_value


def evaluate_case(n_calibration: int, alpha: float, folds: int) -> dict[str, float | int | bool]:
    c, s = p2e_parameters(n_calibration, alpha)
    ranks = [j / (n_calibration + 1) for j in range(1, n_calibration + 2)]
    values = [p2e_value(rank, alpha, c, s) for rank in ranks]
    merged = [sum(combo) / folds for combo in itertools.product(values, repeat=folds)]
    scaled_invalid = [2.0 * value for value in merged]
    threshold = 1.0 / alpha
    coverage = sum(value < threshold for value in merged) / len(merged)
    invalid_coverage = sum(value < threshold for value in scaled_invalid) / len(scaled_invalid)
    return {
        "n_calibration": n_calibration,
        "alpha": alpha,
        "folds": folds,
        "rank_tuple_count": len(merged),
        "mean_merged_e": sum(merged) / len(merged),
        "mean_merged_e_abs_error": abs(sum(merged) / len(merged) - 1.0),
        "coverage_event_probability": coverage,
        "required_coverage": 1.0 - alpha,
        "coverage_pass": coverage >= 1.0 - alpha,
        "invalid_scaled_coverage": invalid_coverage,
        "invalid_control_rejected": invalid_coverage < 1.0 - alpha,
    }


def run_cases() -> dict[str, object]:
    cases = [
        evaluate_case(10, 0.1, 2),
        evaluate_case(10, 0.1, 3),
        evaluate_case(10, 0.1, 4),
        evaluate_case(20, 0.1, 2),
        evaluate_case(20, 0.1, 3),
        evaluate_case(20, 0.2, 3),
    ]
    return {
        "implementation": "independent exact enumeration of discrete rank tuples",
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "all_merged_expectations_exact": all(row["mean_merged_e_abs_error"] < 1e-11 for row in cases),
            "all_markov_coverage_events_pass": all(row["coverage_pass"] for row in cases),
            "invalid_scaling_control_rejection_count": sum(row["invalid_control_rejected"] for row in cases),
            "invalid_scaling_control_detected": any(row["invalid_control_rejected"] for row in cases),
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


````json title=claim3_independent_e_merge.json
{
  "cases": [
    {
      "alpha": 0.1,
      "coverage_event_probability": 0.9917355371900827,
      "coverage_pass": true,
      "folds": 2,
      "invalid_control_rejected": true,
      "invalid_scaled_coverage": 0.8264462809917356,
      "mean_merged_e": 0.9999999999999998,
      "mean_merged_e_abs_error": 2.220446049250313e-16,
      "n_calibration": 10,
      "rank_tuple_count": 121,
      "required_coverage": 0.9
    },
    {
      "alpha": 0.1,
      "coverage_event_probability": 0.9992486851990984,
      "coverage_pass": true,
      "folds": 3,
      "invalid_control_rejected": false,
      "invalid_scaled_coverage": 0.976709241172051,
      "mean_merged_e": 0.9999999999999998,
      "mean_merged_e_abs_error": 2.220446049250313e-16,
      "n_calibration": 10,
      "rank_tuple_count": 1331,
      "required_coverage": 0.9
    },
    {
      "alpha": 0.1,
      "coverage_event_probability": 0.9999316986544635,
      "coverage_pass": true,
      "folds": 4,
      "invalid_control_rejected": false,
      "invalid_scaled_coverage": 0.9562188375110989,
      "mean_merged_e": 0.9999999999999998,
      "mean_merged_e_abs_error": 2.220446049250313e-16,
      "n_calibration": 10,
      "rank_tuple_count": 14641,
      "required_coverage": 0.9
    },
    {
      "alpha": 0.1,
      "coverage_event_probability": 0.9909297052154195,
      "coverage_pass": true,
      "folds": 2,
      "invalid_control_rejected": true,
      "invalid_scaled_coverage": 0.81859410430839,
      "mean_merged_e": 0.9999999999999999,
      "mean_merged_e_abs_error": 1.1102230246251565e-16,
      "n_calibration": 20,
      "rank_tuple_count": 441,
      "required_coverage": 0.9
    },
    {
      "alpha": 0.1,
      "coverage_event_probability": 0.9991361624014685,
      "coverage_pass": true,
      "folds": 3,
      "invalid_control_rejected": false,
      "invalid_scaled_coverage": 0.9745167908433214,
      "mean_merged_e": 0.9999999999999998,
      "mean_merged_e_abs_error": 2.220446049250313e-16,
      "n_calibration": 20,
      "rank_tuple_count": 9261,
      "required_coverage": 0.9
    },
    {
      "alpha": 0.2,
      "coverage_event_probability": 0.9930892992117482,
      "coverage_pass": true,
      "folds": 3,
      "invalid_control_rejected": false,
      "invalid_scaled_coverage": 0.9049778641615376,
      "mean_merged_e": 1.0,
      "mean_merged_e_abs_error": 0.0,
      "n_calibration": 20,
      "rank_tuple_count": 9261,
      "required_coverage": 0.8
    }
  ],
  "implementation": "independent exact enumeration of discrete rank tuples",
  "summary": {
    "all_markov_coverage_events_pass": true,
    "all_merged_expectations_exact": true,
    "case_count": 6,
    "invalid_scaling_control_detected": true,
    "invalid_scaling_control_rejection_count": 2
  }
}

````


````output
{"all_markov_coverage_events_pass": true, "all_merged_expectations_exact": true, "case_count": 6, "invalid_scaling_control_detected": true, "invalid_scaling_control_rejection_count": 2}

````


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_71325b8b46f5", "created_at": "2026-07-18T12:27:18+00:00", "title": "Mechanism check result"}
-->
**Initial six-case nonuniform audit (historical):** this first clean-room enumeration confirmed that arithmetic e-merging retains exact mean one and that the Markov prediction-set event reaches at least `1-alpha` in six WECA-style configurations. The later **Expanded mechanism verdict** adds two explicit equal-weight ECCP cases and is authoritative: 8/8 valid cases pass and outcome-adaptive weighting fails 8/8. Neither mechanism cell replaces the separately required 11,700-cell empirical CCP verdict.


---
<!-- trackio-cell
{"type": "code", "id": "cell_132b3e45fb89", "created_at": "2026-07-19T07:11:52+00:00", "title": "Expanded equal-weight ECCP and nonuniform WECA coupling LP", "command": ["python", "repro/src/verify_e_merge_coverage.py", "--output", "outputs/claim3_independent_e_merge.json"], "exit_code": 0, "duration_s": 1.485}
-->
````bash
$ python repro/src/verify_e_merge_coverage.py --output outputs/claim3_independent_e_merge.json
````

exit 0 · 1.5s


````python title=verify_e_merge_coverage.py
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

````


````json title=claim3_independent_e_merge.json
{
  "cases": [
    {
      "adaptive_max_coverage": 0.8264462809917356,
      "adaptive_max_worst_case_dependent_tail_probability": 0.18181818181818182,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.1,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 121,
      "coverage_event_probability": 0.9917355371900827,
      "coverage_pass": true,
      "folds": 2,
      "invalid_arbitrary_dependence_control_rejected": true,
      "invalid_control_rejected": true,
      "invalid_scaled_coverage": 0.8264462809917356,
      "invalid_worst_case_dependent_tail_probability": 0.18181818181818182,
      "mean_merged_e": 0.9999999999999998,
      "mean_merged_e_abs_error": 2.220446049250313e-16,
      "n_calibration": 10,
      "rank_tuple_count": 121,
      "required_coverage": 0.9,
      "weights": [
        0.5,
        0.5
      ],
      "worst_case_dependent_coverage": 0.9090909090909091,
      "worst_case_dependent_tail_probability": 0.09090909090909091
    },
    {
      "adaptive_max_coverage": 0.7513148009015778,
      "adaptive_max_worst_case_dependent_tail_probability": 0.2727272727272728,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.1,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 1331,
      "coverage_event_probability": 0.9992486851990984,
      "coverage_pass": true,
      "folds": 3,
      "invalid_arbitrary_dependence_control_rejected": true,
      "invalid_control_rejected": false,
      "invalid_scaled_coverage": 0.976709241172051,
      "invalid_worst_case_dependent_tail_probability": 0.13636363636363635,
      "mean_merged_e": 0.9999999999999997,
      "mean_merged_e_abs_error": 3.3306690738754696e-16,
      "n_calibration": 10,
      "rank_tuple_count": 1331,
      "required_coverage": 0.9,
      "weights": [
        0.3333333333333333,
        0.3333333333333333,
        0.3333333333333333
      ],
      "worst_case_dependent_coverage": 0.9090909090909091,
      "worst_case_dependent_tail_probability": 0.09090909090909091
    },
    {
      "adaptive_max_coverage": 0.8264462809917356,
      "adaptive_max_worst_case_dependent_tail_probability": 0.18181818181818182,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.1,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 121,
      "coverage_event_probability": 0.9917355371900827,
      "coverage_pass": true,
      "folds": 2,
      "invalid_arbitrary_dependence_control_rejected": false,
      "invalid_control_rejected": false,
      "invalid_scaled_coverage": 0.9090909090909091,
      "invalid_worst_case_dependent_tail_probability": 0.09090909090909091,
      "mean_merged_e": 0.9999999999999998,
      "mean_merged_e_abs_error": 2.220446049250313e-16,
      "n_calibration": 10,
      "rank_tuple_count": 121,
      "required_coverage": 0.9,
      "weights": [
        0.25,
        0.75
      ],
      "worst_case_dependent_coverage": 0.9090909090909091,
      "worst_case_dependent_tail_probability": 0.09090909090909091
    },
    {
      "adaptive_max_coverage": 0.7513148009015778,
      "adaptive_max_worst_case_dependent_tail_probability": 0.2727272727272728,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.1,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 1331,
      "coverage_event_probability": 0.9992486851990984,
      "coverage_pass": true,
      "folds": 3,
      "invalid_arbitrary_dependence_control_rejected": false,
      "invalid_control_rejected": false,
      "invalid_scaled_coverage": 0.9090909090909091,
      "invalid_worst_case_dependent_tail_probability": 0.09090909090909091,
      "mean_merged_e": 0.9999999999999998,
      "mean_merged_e_abs_error": 2.220446049250313e-16,
      "n_calibration": 10,
      "rank_tuple_count": 1331,
      "required_coverage": 0.9,
      "weights": [
        0.1,
        0.3,
        0.6
      ],
      "worst_case_dependent_coverage": 0.9090909090909091,
      "worst_case_dependent_tail_probability": 0.09090909090909091
    },
    {
      "adaptive_max_coverage": 0.6830134553650707,
      "adaptive_max_worst_case_dependent_tail_probability": 0.36363636363636254,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.1,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 14641,
      "coverage_event_probability": 0.9999316986544635,
      "coverage_pass": true,
      "folds": 4,
      "invalid_arbitrary_dependence_control_rejected": true,
      "invalid_control_rejected": false,
      "invalid_scaled_coverage": 0.9083395942900075,
      "invalid_worst_case_dependent_tail_probability": 0.18181818181818185,
      "mean_merged_e": 0.9999999999999998,
      "mean_merged_e_abs_error": 2.220446049250313e-16,
      "n_calibration": 10,
      "rank_tuple_count": 14641,
      "required_coverage": 0.9,
      "weights": [
        0.05,
        0.15,
        0.3,
        0.5
      ],
      "worst_case_dependent_coverage": 0.9090909090909091,
      "worst_case_dependent_tail_probability": 0.09090909090909091
    },
    {
      "adaptive_max_coverage": 0.81859410430839,
      "adaptive_max_worst_case_dependent_tail_probability": 0.19047619047619047,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.1,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 441,
      "coverage_event_probability": 0.9909297052154195,
      "coverage_pass": true,
      "folds": 2,
      "invalid_arbitrary_dependence_control_rejected": false,
      "invalid_control_rejected": false,
      "invalid_scaled_coverage": 0.9047619047619048,
      "invalid_worst_case_dependent_tail_probability": 0.09523809523809523,
      "mean_merged_e": 0.9999999999999999,
      "mean_merged_e_abs_error": 1.1102230246251565e-16,
      "n_calibration": 20,
      "rank_tuple_count": 441,
      "required_coverage": 0.9,
      "weights": [
        0.2,
        0.8
      ],
      "worst_case_dependent_coverage": 0.9047619047619048,
      "worst_case_dependent_tail_probability": 0.09523809523809523
    },
    {
      "adaptive_max_coverage": 0.7406327610409243,
      "adaptive_max_worst_case_dependent_tail_probability": 0.28571428571428575,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.1,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 9261,
      "coverage_event_probability": 0.9991361624014685,
      "coverage_pass": true,
      "folds": 3,
      "invalid_arbitrary_dependence_control_rejected": false,
      "invalid_control_rejected": false,
      "invalid_scaled_coverage": 0.9047619047619048,
      "invalid_worst_case_dependent_tail_probability": 0.09523809523809523,
      "mean_merged_e": 0.9999999999999998,
      "mean_merged_e_abs_error": 2.220446049250313e-16,
      "n_calibration": 20,
      "rank_tuple_count": 9261,
      "required_coverage": 0.9,
      "weights": [
        0.1,
        0.2,
        0.7
      ],
      "worst_case_dependent_coverage": 0.9047619047619048,
      "worst_case_dependent_tail_probability": 0.09523809523809523
    },
    {
      "adaptive_max_coverage": 0.5305042651981428,
      "adaptive_max_worst_case_dependent_tail_probability": 0.5714285714285713,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.2,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 9261,
      "coverage_event_probability": 0.9930892992117482,
      "coverage_pass": true,
      "folds": 3,
      "invalid_arbitrary_dependence_control_rejected": true,
      "invalid_control_rejected": true,
      "invalid_scaled_coverage": 0.7801533311737393,
      "invalid_worst_case_dependent_tail_probability": 0.3809523809523808,
      "mean_merged_e": 1.0,
      "mean_merged_e_abs_error": 0.0,
      "n_calibration": 20,
      "rank_tuple_count": 9261,
      "required_coverage": 0.8,
      "weights": [
        0.15,
        0.35,
        0.5
      ],
      "worst_case_dependent_coverage": 0.8095238095238095,
      "worst_case_dependent_tail_probability": 0.19047619047619047
    }
  ],
  "implementation": "independent exact enumeration and coupling LP for fixed weighted e-merges",
  "scope": "fixed or tuning-independent weights; adaptive inference-dependent weights are an invalid control",
  "summary": {
    "adaptive_weight_control_detected": true,
    "adaptive_weight_rejection_count": 8,
    "all_arbitrary_dependence_coverage_pass": true,
    "all_markov_coverage_events_pass": true,
    "all_merged_expectations_exact": true,
    "case_count": 8,
    "equal_weight_case_count": 2,
    "invalid_arbitrary_dependence_detected": true,
    "invalid_arbitrary_dependence_rejection_count": 4,
    "invalid_scaling_control_detected": true,
    "invalid_scaling_control_rejection_count": 2,
    "maximum_valid_tail_to_alpha_ratio": 0.9523809523809523,
    "maximum_valid_worst_case_tail_probability": 0.19047619047619047,
    "minimum_adaptive_tail_to_alpha_ratio": 1.8181818181818181,
    "nonuniform_weight_case_count": 6
  }
}

````


````output
{"adaptive_weight_control_detected": true, "adaptive_weight_rejection_count": 8, "all_arbitrary_dependence_coverage_pass": true, "all_markov_coverage_events_pass": true, "all_merged_expectations_exact": true, "case_count": 8, "equal_weight_case_count": 2, "invalid_arbitrary_dependence_detected": true, "invalid_arbitrary_dependence_rejection_count": 4, "invalid_scaling_control_detected": true, "invalid_scaling_control_rejection_count": 2, "maximum_valid_tail_to_alpha_ratio": 0.9523809523809523, "maximum_valid_worst_case_tail_probability": 0.19047619047619047, "minimum_adaptive_tail_to_alpha_ratio": 1.8181818181818181, "nonuniform_weight_case_count": 6}

````


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_11f7ed8ba9e9", "created_at": "2026-07-19T07:12:01+00:00", "title": "Expanded mechanism verdict"}
-->
The mechanism audit now covers **8/8 fixed-weight cases**: two explicit equal-weight ECCP constructions and six nonuniform tuning-independent WECA constructions. Every valid arbitrary-dependence LP optimum stays at or below alpha (maximum tail/alpha ratio `0.952381`). Invalid 2x scaling violates 4/8 adversarial-coupling cases, while forbidden inference-outcome-adaptive max weighting violates 8/8 (minimum tail/alpha ratio `1.818182`). The equal-weight additions close the explicit ECCP scope gap; the full 11,700-cell empirical CCP run remains independently required.


---
<!-- trackio-cell
{"type": "code", "id": "cell_7974c204513d", "created_at": "2026-07-19T15:32:15+00:00", "title": "Deterministic and randomized arbitrary-dependence coupling LP", "command": ["python", "repro/src/verify_e_merge_coverage.py", "--output", "outputs/claim3_independent_e_merge.json"], "exit_code": 0, "duration_s": 2.568}
-->
````bash
$ python repro/src/verify_e_merge_coverage.py --output outputs/claim3_independent_e_merge.json
````

exit 0 · 2.6s


````python title=verify_e_merge_coverage.py
#!/usr/bin/env python3
"""Independent finite enumeration of the e-merge coverage mechanism.

For independent discrete conformal ranks, each clean-room P2E value has exact
mean one. Their arithmetic merge is consequently an e-value. This checker
enumerates every rank tuple in small non-trivial configurations and verifies
both the deterministic Markov prediction-set event and the independent-uniform
randomized threshold used by the paper's ECCP and UR-WECA constructions. It is
a mechanism check for Claim 3, not a substitute for the released 100-seed
empirical CCP protocol.
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
    randomized_uniform_threshold: bool = False,
) -> tuple[float, int]:
    """Maximize failure over all couplings with uniform rank marginals.

    With ``randomized_uniform_threshold``, the prediction set uses the paper's
    independent ``U / alpha`` threshold. Conditional on a merged e-value
    ``e``, its failure probability is ``min(e / threshold, 1)``. Otherwise the
    deterministic failure event is ``e >= threshold``.
    """
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
    failure_cost = (
        np.minimum(merged / threshold, 1.0)
        if randomized_uniform_threshold
        else (merged >= threshold).astype(float)
    )
    constraints = lil_matrix(
        (folds * len(values), len(rank_tuples)), dtype=float
    )
    for fold in range(folds):
        for rank in range(len(values)):
            columns = np.flatnonzero(rank_tuples[:, fold] == rank)
            constraints[fold * len(values) + rank, columns] = 1.0
    marginals = np.full(folds * len(values), 1.0 / len(values))
    solution = linprog(
        -failure_cost,
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
    randomized_failure = sum(min(value / threshold, 1.0) for value in merged) / len(merged)
    invalid_randomized_failure = sum(
        min(value / threshold, 1.0) for value in scaled_invalid
    ) / len(scaled_invalid)
    adaptive_randomized_failure = sum(
        min(value / threshold, 1.0) for value in adaptive_max
    ) / len(adaptive_max)
    worst_tail, lp_variables = worst_case_tail_probability(
        values, folds, threshold, weights=weights
    )
    invalid_worst_tail, _ = worst_case_tail_probability(
        [2.0 * value for value in values], folds, threshold, weights=weights
    )
    adaptive_worst_tail, _ = worst_case_tail_probability(
        values, folds, threshold, weights=weights, adaptive_max=True
    )
    randomized_worst_tail, _ = worst_case_tail_probability(
        values,
        folds,
        threshold,
        weights=weights,
        randomized_uniform_threshold=True,
    )
    invalid_randomized_worst_tail, _ = worst_case_tail_probability(
        [2.0 * value for value in values],
        folds,
        threshold,
        weights=weights,
        randomized_uniform_threshold=True,
    )
    adaptive_randomized_worst_tail, _ = worst_case_tail_probability(
        values,
        folds,
        threshold,
        weights=weights,
        adaptive_max=True,
        randomized_uniform_threshold=True,
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
        "randomized_uniform_failure_probability": randomized_failure,
        "randomized_uniform_coverage": 1.0 - randomized_failure,
        "randomized_uniform_coverage_pass": randomized_failure <= alpha + 1e-10,
        "coupling_lp_variables": lp_variables,
        "worst_case_dependent_tail_probability": worst_tail,
        "worst_case_dependent_coverage": 1.0 - worst_tail,
        "arbitrary_dependence_coverage_pass": worst_tail <= alpha + 1e-10,
        "randomized_worst_case_dependent_failure_probability": randomized_worst_tail,
        "randomized_worst_case_dependent_coverage": 1.0 - randomized_worst_tail,
        "randomized_arbitrary_dependence_coverage_pass": (
            randomized_worst_tail <= alpha + 1e-10
        ),
        "invalid_scaled_coverage": invalid_coverage,
        "invalid_control_rejected": invalid_coverage < 1.0 - alpha,
        "invalid_worst_case_dependent_tail_probability": invalid_worst_tail,
        "invalid_arbitrary_dependence_control_rejected": invalid_worst_tail > alpha + 1e-10,
        "invalid_randomized_uniform_failure_probability": invalid_randomized_failure,
        "invalid_randomized_worst_case_dependent_failure_probability": (
            invalid_randomized_worst_tail
        ),
        "invalid_randomized_arbitrary_dependence_control_rejected": (
            invalid_randomized_worst_tail > alpha + 1e-10
        ),
        "adaptive_max_coverage": adaptive_coverage,
        "adaptive_max_worst_case_dependent_tail_probability": adaptive_worst_tail,
        "adaptive_weight_control_rejected": adaptive_worst_tail > alpha + 1e-10,
        "adaptive_randomized_uniform_failure_probability": (
            adaptive_randomized_failure
        ),
        "adaptive_randomized_worst_case_dependent_failure_probability": (
            adaptive_randomized_worst_tail
        ),
        "adaptive_randomized_weight_control_rejected": (
            adaptive_randomized_worst_tail > alpha + 1e-10
        ),
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
        "implementation": (
            "independent exact enumeration and coupling LP for deterministic "
            "and independent-uniform randomized fixed weighted e-merges"
        ),
        "scope": (
            "fixed or tuning-independent weights under arbitrary dependence; "
            "adaptive inference-dependent weights are an invalid control"
        ),
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
            "all_randomized_uniform_coverage_events_pass": all(
                row["randomized_uniform_coverage_pass"] for row in cases
            ),
            "all_arbitrary_dependence_coverage_pass": all(
                row["arbitrary_dependence_coverage_pass"] for row in cases
            ),
            "all_randomized_arbitrary_dependence_coverage_pass": all(
                row["randomized_arbitrary_dependence_coverage_pass"]
                for row in cases
            ),
            "maximum_valid_worst_case_tail_probability": max(
                row["worst_case_dependent_tail_probability"] for row in cases
            ),
            "maximum_valid_tail_to_alpha_ratio": max(
                row["worst_case_dependent_tail_probability"] / row["alpha"]
                for row in cases
            ),
            "maximum_valid_randomized_worst_case_failure_probability": max(
                row["randomized_worst_case_dependent_failure_probability"]
                for row in cases
            ),
            "maximum_valid_randomized_tail_to_alpha_ratio": max(
                row["randomized_worst_case_dependent_failure_probability"]
                / row["alpha"]
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
            "invalid_randomized_arbitrary_dependence_rejection_count": sum(
                row["invalid_randomized_arbitrary_dependence_control_rejected"]
                for row in cases
            ),
            "invalid_randomized_arbitrary_dependence_detected": any(
                row["invalid_randomized_arbitrary_dependence_control_rejected"]
                for row in cases
            ),
            "adaptive_weight_rejection_count": sum(
                row["adaptive_weight_control_rejected"] for row in cases
            ),
            "adaptive_weight_control_detected": any(
                row["adaptive_weight_control_rejected"] for row in cases
            ),
            "adaptive_randomized_weight_rejection_count": sum(
                row["adaptive_randomized_weight_control_rejected"] for row in cases
            ),
            "adaptive_randomized_weight_control_detected": any(
                row["adaptive_randomized_weight_control_rejected"] for row in cases
            ),
            "minimum_adaptive_tail_to_alpha_ratio": min(
                row["adaptive_max_worst_case_dependent_tail_probability"] / row["alpha"]
                for row in cases
            ),
            "minimum_adaptive_randomized_tail_to_alpha_ratio": min(
                row["adaptive_randomized_worst_case_dependent_failure_probability"]
                / row["alpha"]
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

````


````json title=claim3_independent_e_merge.json
{
  "cases": [
    {
      "adaptive_max_coverage": 0.8264462809917356,
      "adaptive_max_worst_case_dependent_tail_probability": 0.18181818181818182,
      "adaptive_randomized_uniform_failure_probability": 0.18454097836730804,
      "adaptive_randomized_weight_control_rejected": true,
      "adaptive_randomized_worst_case_dependent_failure_probability": 0.19454414352118643,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.1,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 121,
      "coverage_event_probability": 0.9917355371900827,
      "coverage_pass": true,
      "folds": 2,
      "invalid_arbitrary_dependence_control_rejected": true,
      "invalid_control_rejected": true,
      "invalid_randomized_arbitrary_dependence_control_rejected": true,
      "invalid_randomized_uniform_failure_probability": 0.18512277522310025,
      "invalid_randomized_worst_case_dependent_failure_probability": 0.19454414365450118,
      "invalid_scaled_coverage": 0.8264462809917356,
      "invalid_worst_case_dependent_tail_probability": 0.18181818181818182,
      "mean_merged_e": 0.9999999999999998,
      "mean_merged_e_abs_error": 2.220446049250313e-16,
      "n_calibration": 10,
      "randomized_arbitrary_dependence_coverage_pass": true,
      "randomized_uniform_coverage": 0.90024799347025,
      "randomized_uniform_coverage_pass": true,
      "randomized_uniform_failure_probability": 0.09975200652975003,
      "randomized_worst_case_dependent_coverage": 0.9,
      "randomized_worst_case_dependent_failure_probability": 0.09999999999999996,
      "rank_tuple_count": 121,
      "required_coverage": 0.9,
      "weights": [
        0.5,
        0.5
      ],
      "worst_case_dependent_coverage": 0.9090909090909091,
      "worst_case_dependent_tail_probability": 0.09090909090909091
    },
    {
      "adaptive_max_coverage": 0.7513148009015778,
      "adaptive_max_worst_case_dependent_tail_probability": 0.2727272727272728,
      "adaptive_randomized_uniform_failure_probability": 0.2629279672453386,
      "adaptive_randomized_weight_control_rejected": true,
      "adaptive_randomized_worst_case_dependent_failure_probability": 0.291816165760236,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.1,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 1331,
      "coverage_event_probability": 0.9992486851990984,
      "coverage_pass": true,
      "folds": 3,
      "invalid_arbitrary_dependence_control_rejected": true,
      "invalid_control_rejected": false,
      "invalid_randomized_arbitrary_dependence_control_rejected": true,
      "invalid_randomized_uniform_failure_probability": 0.19068347979262973,
      "invalid_randomized_worst_case_dependent_failure_probability": 0.19999999999999996,
      "invalid_scaled_coverage": 0.976709241172051,
      "invalid_worst_case_dependent_tail_probability": 0.13636363636363635,
      "mean_merged_e": 0.9999999999999997,
      "mean_merged_e_abs_error": 3.3306690738754696e-16,
      "n_calibration": 10,
      "randomized_arbitrary_dependence_coverage_pass": true,
      "randomized_uniform_coverage": 0.9000225448609318,
      "randomized_uniform_coverage_pass": true,
      "randomized_uniform_failure_probability": 0.09997745513906815,
      "randomized_worst_case_dependent_coverage": 0.9,
      "randomized_worst_case_dependent_failure_probability": 0.09999999999999995,
      "rank_tuple_count": 1331,
      "required_coverage": 0.9,
      "weights": [
        0.3333333333333333,
        0.3333333333333333,
        0.3333333333333333
      ],
      "worst_case_dependent_coverage": 0.9090909090909091,
      "worst_case_dependent_tail_probability": 0.09090909090909091
    },
    {
      "adaptive_max_coverage": 0.8264462809917356,
      "adaptive_max_worst_case_dependent_tail_probability": 0.18181818181818182,
      "adaptive_randomized_uniform_failure_probability": 0.18454097836730804,
      "adaptive_randomized_weight_control_rejected": true,
      "adaptive_randomized_worst_case_dependent_failure_probability": 0.19454414352118643,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.1,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 121,
      "coverage_event_probability": 0.9917355371900827,
      "coverage_pass": true,
      "folds": 2,
      "invalid_arbitrary_dependence_control_rejected": false,
      "invalid_control_rejected": false,
      "invalid_randomized_arbitrary_dependence_control_rejected": true,
      "invalid_randomized_uniform_failure_probability": 0.14590810774087587,
      "invalid_randomized_worst_case_dependent_failure_probability": 0.15045356228633044,
      "invalid_scaled_coverage": 0.9090909090909091,
      "invalid_worst_case_dependent_tail_probability": 0.09090909090909091,
      "mean_merged_e": 0.9999999999999998,
      "mean_merged_e_abs_error": 2.220446049250313e-16,
      "n_calibration": 10,
      "randomized_arbitrary_dependence_coverage_pass": true,
      "randomized_uniform_coverage": 0.90024799347025,
      "randomized_uniform_coverage_pass": true,
      "randomized_uniform_failure_probability": 0.09975200652975003,
      "randomized_worst_case_dependent_coverage": 0.9,
      "randomized_worst_case_dependent_failure_probability": 0.09999999999999996,
      "rank_tuple_count": 121,
      "required_coverage": 0.9,
      "weights": [
        0.25,
        0.75
      ],
      "worst_case_dependent_coverage": 0.9090909090909091,
      "worst_case_dependent_tail_probability": 0.09090909090909091
    },
    {
      "adaptive_max_coverage": 0.7513148009015778,
      "adaptive_max_worst_case_dependent_tail_probability": 0.2727272727272728,
      "adaptive_randomized_uniform_failure_probability": 0.2629279672453386,
      "adaptive_randomized_weight_control_rejected": true,
      "adaptive_randomized_worst_case_dependent_failure_probability": 0.291816165760236,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.1,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 1331,
      "coverage_event_probability": 0.9992486851990984,
      "coverage_pass": true,
      "folds": 3,
      "invalid_arbitrary_dependence_control_rejected": false,
      "invalid_control_rejected": false,
      "invalid_randomized_arbitrary_dependence_control_rejected": true,
      "invalid_randomized_uniform_failure_probability": 0.17127194073815524,
      "invalid_randomized_worst_case_dependent_failure_probability": 0.17854466801088242,
      "invalid_scaled_coverage": 0.9090909090909091,
      "invalid_worst_case_dependent_tail_probability": 0.09090909090909091,
      "mean_merged_e": 0.9999999999999998,
      "mean_merged_e_abs_error": 2.220446049250313e-16,
      "n_calibration": 10,
      "randomized_arbitrary_dependence_coverage_pass": true,
      "randomized_uniform_coverage": 0.9000225448609318,
      "randomized_uniform_coverage_pass": true,
      "randomized_uniform_failure_probability": 0.09997745513906815,
      "randomized_worst_case_dependent_coverage": 0.9,
      "randomized_worst_case_dependent_failure_probability": 0.09999999999999998,
      "rank_tuple_count": 1331,
      "required_coverage": 0.9,
      "weights": [
        0.1,
        0.3,
        0.6
      ],
      "worst_case_dependent_coverage": 0.9090909090909091,
      "worst_case_dependent_tail_probability": 0.09090909090909091
    },
    {
      "adaptive_max_coverage": 0.6830134553650707,
      "adaptive_max_worst_case_dependent_tail_probability": 0.36363636363636254,
      "adaptive_randomized_uniform_failure_probability": 0.3334135825525855,
      "adaptive_randomized_weight_control_rejected": true,
      "adaptive_randomized_worst_case_dependent_failure_probability": 0.38906979628512295,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.1,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 14641,
      "coverage_event_probability": 0.9999316986544635,
      "coverage_pass": true,
      "folds": 4,
      "invalid_arbitrary_dependence_control_rejected": true,
      "invalid_control_rejected": false,
      "invalid_randomized_arbitrary_dependence_control_rejected": true,
      "invalid_randomized_uniform_failure_probability": 0.18815562885880951,
      "invalid_randomized_worst_case_dependent_failure_probability": 0.19727207177918907,
      "invalid_scaled_coverage": 0.9083395942900075,
      "invalid_worst_case_dependent_tail_probability": 0.18181818181818185,
      "mean_merged_e": 0.9999999999999998,
      "mean_merged_e_abs_error": 2.220446049250313e-16,
      "n_calibration": 10,
      "randomized_arbitrary_dependence_coverage_pass": true,
      "randomized_uniform_coverage": 0.900002049532812,
      "randomized_uniform_coverage_pass": true,
      "randomized_uniform_failure_probability": 0.09999795046718798,
      "randomized_worst_case_dependent_coverage": 0.9,
      "randomized_worst_case_dependent_failure_probability": 0.09999999999999999,
      "rank_tuple_count": 14641,
      "required_coverage": 0.9,
      "weights": [
        0.05,
        0.15,
        0.3,
        0.5
      ],
      "worst_case_dependent_coverage": 0.9090909090909091,
      "worst_case_dependent_tail_probability": 0.09090909090909091
    },
    {
      "adaptive_max_coverage": 0.81859410430839,
      "adaptive_max_worst_case_dependent_tail_probability": 0.19047619047619047,
      "adaptive_randomized_uniform_failure_probability": 0.18476227382655455,
      "adaptive_randomized_weight_control_rejected": true,
      "adaptive_randomized_worst_case_dependent_failure_probability": 0.19428630069079045,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.1,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 441,
      "coverage_event_probability": 0.9909297052154195,
      "coverage_pass": true,
      "folds": 2,
      "invalid_arbitrary_dependence_control_rejected": false,
      "invalid_control_rejected": false,
      "invalid_randomized_arbitrary_dependence_control_rejected": true,
      "invalid_randomized_uniform_failure_probability": 0.13447665960100735,
      "invalid_randomized_worst_case_dependent_failure_probability": 0.13828618292714043,
      "invalid_scaled_coverage": 0.9047619047619048,
      "invalid_worst_case_dependent_tail_probability": 0.09523809523809523,
      "mean_merged_e": 0.9999999999999999,
      "mean_merged_e_abs_error": 1.1102230246251565e-16,
      "n_calibration": 20,
      "randomized_arbitrary_dependence_coverage_pass": true,
      "randomized_uniform_coverage": 0.9002720809194412,
      "randomized_uniform_coverage_pass": true,
      "randomized_uniform_failure_probability": 0.09972791908055882,
      "randomized_worst_case_dependent_coverage": 0.9,
      "randomized_worst_case_dependent_failure_probability": 0.09999999999999999,
      "rank_tuple_count": 441,
      "required_coverage": 0.9,
      "weights": [
        0.2,
        0.8
      ],
      "worst_case_dependent_coverage": 0.9047619047619048,
      "worst_case_dependent_tail_probability": 0.09523809523809523
    },
    {
      "adaptive_max_coverage": 0.7406327610409243,
      "adaptive_max_worst_case_dependent_tail_probability": 0.28571428571428575,
      "adaptive_randomized_uniform_failure_probability": 0.2638033484888897,
      "adaptive_randomized_weight_control_rejected": true,
      "adaptive_randomized_worst_case_dependent_failure_probability": 0.2914294482565785,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.1,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 9261,
      "coverage_event_probability": 0.9991361624014685,
      "coverage_pass": true,
      "folds": 3,
      "invalid_arbitrary_dependence_control_rejected": false,
      "invalid_control_rejected": false,
      "invalid_randomized_arbitrary_dependence_control_rejected": true,
      "invalid_randomized_uniform_failure_probability": 0.15219088667469094,
      "invalid_randomized_worst_case_dependent_failure_probability": 0.157905172344055,
      "invalid_scaled_coverage": 0.9047619047619048,
      "invalid_worst_case_dependent_tail_probability": 0.09523809523809523,
      "mean_merged_e": 0.9999999999999998,
      "mean_merged_e_abs_error": 2.220446049250313e-16,
      "n_calibration": 20,
      "randomized_arbitrary_dependence_coverage_pass": true,
      "randomized_uniform_coverage": 0.9000259124685183,
      "randomized_uniform_coverage_pass": true,
      "randomized_uniform_failure_probability": 0.09997408753148178,
      "randomized_worst_case_dependent_coverage": 0.9,
      "randomized_worst_case_dependent_failure_probability": 0.09999999999999995,
      "rank_tuple_count": 9261,
      "required_coverage": 0.9,
      "weights": [
        0.1,
        0.2,
        0.7
      ],
      "worst_case_dependent_coverage": 0.9047619047619048,
      "worst_case_dependent_tail_probability": 0.09523809523809523
    },
    {
      "adaptive_max_coverage": 0.5305042651981428,
      "adaptive_max_worst_case_dependent_tail_probability": 0.5714285714285713,
      "adaptive_randomized_uniform_failure_probability": 0.47318103347825835,
      "adaptive_randomized_weight_control_rejected": true,
      "adaptive_randomized_worst_case_dependent_failure_probability": 0.577396579293704,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.2,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 9261,
      "coverage_event_probability": 0.9930892992117482,
      "coverage_pass": true,
      "folds": 3,
      "invalid_arbitrary_dependence_control_rejected": true,
      "invalid_control_rejected": true,
      "invalid_randomized_arbitrary_dependence_control_rejected": true,
      "invalid_randomized_uniform_failure_probability": 0.3531363348706932,
      "invalid_randomized_worst_case_dependent_failure_probability": 0.3924655266043606,
      "invalid_scaled_coverage": 0.7801533311737393,
      "invalid_worst_case_dependent_tail_probability": 0.3809523809523808,
      "mean_merged_e": 1.0,
      "mean_merged_e_abs_error": 0.0,
      "n_calibration": 20,
      "randomized_arbitrary_dependence_coverage_pass": true,
      "randomized_uniform_coverage": 0.8002733595779199,
      "randomized_uniform_coverage_pass": true,
      "randomized_uniform_failure_probability": 0.19972664042208013,
      "randomized_worst_case_dependent_coverage": 0.8,
      "randomized_worst_case_dependent_failure_probability": 0.19999999999999998,
      "rank_tuple_count": 9261,
      "required_coverage": 0.8,
      "weights": [
        0.15,
        0.35,
        0.5
      ],
      "worst_case_dependent_coverage": 0.8095238095238095,
      "worst_case_dependent_tail_probability": 0.19047619047619047
    }
  ],
  "implementation": "independent exact enumeration and coupling LP for deterministic and independent-uniform randomized fixed weighted e-merges",
  "scope": "fixed or tuning-independent weights under arbitrary dependence; adaptive inference-dependent weights are an invalid control",
  "summary": {
    "adaptive_randomized_weight_control_detected": true,
    "adaptive_randomized_weight_rejection_count": 8,
    "adaptive_weight_control_detected": true,
    "adaptive_weight_rejection_count": 8,
    "all_arbitrary_dependence_coverage_pass": true,
    "all_markov_coverage_events_pass": true,
    "all_merged_expectations_exact": true,
    "all_randomized_arbitrary_dependence_coverage_pass": true,
    "all_randomized_uniform_coverage_events_pass": true,
    "case_count": 8,
    "equal_weight_case_count": 2,
    "invalid_arbitrary_dependence_detected": true,
    "invalid_arbitrary_dependence_rejection_count": 4,
    "invalid_randomized_arbitrary_dependence_detected": true,
    "invalid_randomized_arbitrary_dependence_rejection_count": 8,
    "invalid_scaling_control_detected": true,
    "invalid_scaling_control_rejection_count": 2,
    "maximum_valid_randomized_tail_to_alpha_ratio": 0.9999999999999999,
    "maximum_valid_randomized_worst_case_failure_probability": 0.19999999999999998,
    "maximum_valid_tail_to_alpha_ratio": 0.9523809523809523,
    "maximum_valid_worst_case_tail_probability": 0.19047619047619047,
    "minimum_adaptive_randomized_tail_to_alpha_ratio": 1.9428630069079045,
    "minimum_adaptive_tail_to_alpha_ratio": 1.8181818181818181,
    "nonuniform_weight_case_count": 6
  }
}

````


````output
{"adaptive_randomized_weight_control_detected": true, "adaptive_randomized_weight_rejection_count": 8, "adaptive_weight_control_detected": true, "adaptive_weight_rejection_count": 8, "all_arbitrary_dependence_coverage_pass": true, "all_markov_coverage_events_pass": true, "all_merged_expectations_exact": true, "all_randomized_arbitrary_dependence_coverage_pass": true, "all_randomized_uniform_coverage_events_pass": true, "case_count": 8, "equal_weight_case_count": 2, "invalid_arbitrary_dependence_detected": true, "invalid_arbitrary_dependence_rejection_count": 4, "invalid_randomized_arbitrary_dependence_detected": true, "invalid_randomized_arbitrary_dependence_rejection_count": 8, "invalid_scaling_control_detected": true, "invalid_scaling_control_rejection_count": 2, "maximum_valid_randomized_tail_to_alpha_ratio": 0.9999999999999999, "maximum_valid_randomized_worst_case_failure_probability": 0.19999999999999998, "maximum_valid_tail_to_alpha_ratio": 0.9523809523809523, "maximum_valid_worst_case_tail_probability": 0.19047619047619047, "minimum_adaptive_randomized_tail_to_alpha_ratio": 1.9428630069079045, "minimum_adaptive_tail_to_alpha_ratio": 1.8181818181818181, "nonuniform_weight_case_count": 6}

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_049ebce9f553", "created_at": "2026-07-19T15:40:32+00:00", "title": "Exchangeable and randomized e-merge coverage certificate", "command": ["python", "repro/src/verify_e_merge_coverage.py", "--output", "outputs/claim3_independent_e_merge.json"], "exit_code": 0, "duration_s": 3.995}
-->
````bash
$ python repro/src/verify_e_merge_coverage.py --output outputs/claim3_independent_e_merge.json
````

exit 0 · 4.0s


````python title=verify_e_merge_coverage.py
#!/usr/bin/env python3
"""Independent finite enumeration of the e-merge coverage mechanism.

For independent discrete conformal ranks, each clean-room P2E value has exact
mean one. Their arithmetic merge is consequently an e-value. This checker
enumerates every rank tuple in small non-trivial configurations and verifies
both the deterministic Markov prediction-set event and the independent-uniform
randomized threshold used by the paper's ECCP and UR-WECA constructions. It is
a mechanism check for Claim 3, not a substitute for the released 100-seed
empirical CCP protocol.
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
    randomized_uniform_threshold: bool = False,
) -> tuple[float, int]:
    """Maximize failure over all couplings with uniform rank marginals.

    With ``randomized_uniform_threshold``, the prediction set uses the paper's
    independent ``U / alpha`` threshold. Conditional on a merged e-value
    ``e``, its failure probability is ``min(e / threshold, 1)``. Otherwise the
    deterministic failure event is ``e >= threshold``.
    """
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
    failure_cost = (
        np.minimum(merged / threshold, 1.0)
        if randomized_uniform_threshold
        else (merged >= threshold).astype(float)
    )
    constraints = lil_matrix(
        (folds * len(values), len(rank_tuples)), dtype=float
    )
    for fold in range(folds):
        for rank in range(len(values)):
            columns = np.flatnonzero(rank_tuples[:, fold] == rank)
            constraints[fold * len(values) + rank, columns] = 1.0
    marginals = np.full(folds * len(values), 1.0 / len(values))
    solution = linprog(
        -failure_cost,
        A_eq=constraints.tocsr(),
        b_eq=marginals,
        bounds=(0.0, None),
        method="highs",
    )
    if not solution.success:
        raise RuntimeError(f"coupling LP failed: {solution.message}")
    return float(-solution.fun), len(rank_tuples)


def worst_case_exchangeable_prefix_failure_probability(
    values: list[float],
    folds: int,
    threshold: float,
    *,
    randomized_first: bool = False,
) -> tuple[float, int]:
    """Maximize ECCP-Exch failure over exchangeable rank couplings.

    One LP variable is the total probability of an unordered rank multiset.
    Conditional on that orbit, every distinct ordering has equal probability,
    which enforces fold exchangeability exactly. ``randomized_first`` adds the
    paper's independent-uniform ``E_1 / U`` rejection rule used by
    UR-ECCP-Exch whenever the prefix maximum has not already rejected.
    """
    if folds < 1:
        raise ValueError("folds must be positive")
    rank_count = len(values)
    if rank_count < 1:
        raise ValueError("values must be nonempty")
    orbits = list(itertools.combinations_with_replacement(range(rank_count), folds))
    costs = []
    constraints = lil_matrix((rank_count, len(orbits)), dtype=float)
    value_array = np.asarray(values, dtype=float)
    for column, orbit in enumerate(orbits):
        for rank in set(orbit):
            constraints[rank, column] = orbit.count(rank) / folds
        orderings = set(itertools.permutations(orbit))
        ordering_costs = []
        for ordering in orderings:
            ordered_values = value_array[list(ordering)]
            prefix_maximum = float(
                np.max(
                    np.cumsum(ordered_values)
                    / np.arange(1, folds + 1, dtype=float)
                )
            )
            if prefix_maximum >= threshold:
                ordering_costs.append(1.0)
            elif randomized_first:
                ordering_costs.append(min(float(ordered_values[0]) / threshold, 1.0))
            else:
                ordering_costs.append(0.0)
        costs.append(sum(ordering_costs) / len(ordering_costs))
    solution = linprog(
        -np.asarray(costs),
        A_eq=constraints.tocsr(),
        b_eq=np.full(rank_count, 1.0 / rank_count),
        bounds=(0.0, None),
        method="highs",
    )
    if not solution.success:
        raise RuntimeError(f"exchangeable coupling LP failed: {solution.message}")
    return float(-solution.fun), len(orbits)


def evaluate_exchangeable_case(
    n_calibration: int,
    alpha: float,
    folds: int,
) -> dict[str, float | int | bool]:
    c, s = p2e_parameters(n_calibration, alpha)
    ranks = [j / (n_calibration + 1) for j in range(1, n_calibration + 2)]
    values = [p2e_value(rank, alpha, c, s) for rank in ranks]
    threshold = 1.0 / alpha
    prefix_failure, orbit_count = worst_case_exchangeable_prefix_failure_probability(
        values, folds, threshold
    )
    randomized_prefix_failure, randomized_orbit_count = (
        worst_case_exchangeable_prefix_failure_probability(
            values, folds, threshold, randomized_first=True
        )
    )
    invalid_values = [2.0 * value for value in values]
    invalid_prefix_failure, _ = worst_case_exchangeable_prefix_failure_probability(
        invalid_values, folds, threshold
    )
    invalid_randomized_prefix_failure, _ = (
        worst_case_exchangeable_prefix_failure_probability(
            invalid_values, folds, threshold, randomized_first=True
        )
    )
    if randomized_orbit_count != orbit_count:
        raise RuntimeError("exchangeable LP orbit count drift")
    return {
        "n_calibration": n_calibration,
        "alpha": alpha,
        "folds": folds,
        "exchangeable_orbit_count": orbit_count,
        "eccp_exch_worst_case_failure_probability": prefix_failure,
        "eccp_exch_coverage_pass": prefix_failure <= alpha + 1e-10,
        "ur_eccp_exch_worst_case_failure_probability": randomized_prefix_failure,
        "ur_eccp_exch_coverage_pass": randomized_prefix_failure <= alpha + 1e-10,
        "invalid_eccp_exch_worst_case_failure_probability": invalid_prefix_failure,
        "invalid_eccp_exch_control_rejected": invalid_prefix_failure > alpha + 1e-10,
        "invalid_ur_eccp_exch_worst_case_failure_probability": (
            invalid_randomized_prefix_failure
        ),
        "invalid_ur_eccp_exch_control_rejected": (
            invalid_randomized_prefix_failure > alpha + 1e-10
        ),
    }


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
    randomized_failure = sum(min(value / threshold, 1.0) for value in merged) / len(merged)
    invalid_randomized_failure = sum(
        min(value / threshold, 1.0) for value in scaled_invalid
    ) / len(scaled_invalid)
    adaptive_randomized_failure = sum(
        min(value / threshold, 1.0) for value in adaptive_max
    ) / len(adaptive_max)
    worst_tail, lp_variables = worst_case_tail_probability(
        values, folds, threshold, weights=weights
    )
    invalid_worst_tail, _ = worst_case_tail_probability(
        [2.0 * value for value in values], folds, threshold, weights=weights
    )
    adaptive_worst_tail, _ = worst_case_tail_probability(
        values, folds, threshold, weights=weights, adaptive_max=True
    )
    randomized_worst_tail, _ = worst_case_tail_probability(
        values,
        folds,
        threshold,
        weights=weights,
        randomized_uniform_threshold=True,
    )
    invalid_randomized_worst_tail, _ = worst_case_tail_probability(
        [2.0 * value for value in values],
        folds,
        threshold,
        weights=weights,
        randomized_uniform_threshold=True,
    )
    adaptive_randomized_worst_tail, _ = worst_case_tail_probability(
        values,
        folds,
        threshold,
        weights=weights,
        adaptive_max=True,
        randomized_uniform_threshold=True,
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
        "randomized_uniform_failure_probability": randomized_failure,
        "randomized_uniform_coverage": 1.0 - randomized_failure,
        "randomized_uniform_coverage_pass": randomized_failure <= alpha + 1e-10,
        "coupling_lp_variables": lp_variables,
        "worst_case_dependent_tail_probability": worst_tail,
        "worst_case_dependent_coverage": 1.0 - worst_tail,
        "arbitrary_dependence_coverage_pass": worst_tail <= alpha + 1e-10,
        "randomized_worst_case_dependent_failure_probability": randomized_worst_tail,
        "randomized_worst_case_dependent_coverage": 1.0 - randomized_worst_tail,
        "randomized_arbitrary_dependence_coverage_pass": (
            randomized_worst_tail <= alpha + 1e-10
        ),
        "invalid_scaled_coverage": invalid_coverage,
        "invalid_control_rejected": invalid_coverage < 1.0 - alpha,
        "invalid_worst_case_dependent_tail_probability": invalid_worst_tail,
        "invalid_arbitrary_dependence_control_rejected": invalid_worst_tail > alpha + 1e-10,
        "invalid_randomized_uniform_failure_probability": invalid_randomized_failure,
        "invalid_randomized_worst_case_dependent_failure_probability": (
            invalid_randomized_worst_tail
        ),
        "invalid_randomized_arbitrary_dependence_control_rejected": (
            invalid_randomized_worst_tail > alpha + 1e-10
        ),
        "adaptive_max_coverage": adaptive_coverage,
        "adaptive_max_worst_case_dependent_tail_probability": adaptive_worst_tail,
        "adaptive_weight_control_rejected": adaptive_worst_tail > alpha + 1e-10,
        "adaptive_randomized_uniform_failure_probability": (
            adaptive_randomized_failure
        ),
        "adaptive_randomized_worst_case_dependent_failure_probability": (
            adaptive_randomized_worst_tail
        ),
        "adaptive_randomized_weight_control_rejected": (
            adaptive_randomized_worst_tail > alpha + 1e-10
        ),
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
    exchangeable_prefix_cases = [
        evaluate_exchangeable_case(10, 0.1, 2),
        evaluate_exchangeable_case(10, 0.1, 3),
        evaluate_exchangeable_case(10, 0.1, 4),
        evaluate_exchangeable_case(20, 0.1, 3),
        evaluate_exchangeable_case(20, 0.2, 3),
    ]
    return {
        "implementation": (
            "independent exact enumeration and coupling LP for deterministic "
            "and independent-uniform randomized fixed weighted e-merges"
        ),
        "scope": (
            "fixed or tuning-independent weights under arbitrary dependence; "
            "adaptive inference-dependent weights are an invalid control"
        ),
        "cases": cases,
        "exchangeable_prefix_cases": exchangeable_prefix_cases,
        "summary": {
            "case_count": len(cases),
            "equal_weight_case_count": sum(
                max(row["weights"]) - min(row["weights"]) < 1e-12 for row in cases
            ),
            "nonuniform_weight_case_count": sum(
                max(row["weights"]) - min(row["weights"]) >= 1e-12 for row in cases
            ),
            "exchangeable_prefix_case_count": len(exchangeable_prefix_cases),
            "all_exchangeable_prefix_coverage_pass": all(
                row["eccp_exch_coverage_pass"] for row in exchangeable_prefix_cases
            ),
            "all_exchangeable_randomized_prefix_coverage_pass": all(
                row["ur_eccp_exch_coverage_pass"]
                for row in exchangeable_prefix_cases
            ),
            "maximum_exchangeable_prefix_tail_to_alpha_ratio": max(
                row["eccp_exch_worst_case_failure_probability"] / row["alpha"]
                for row in exchangeable_prefix_cases
            ),
            "maximum_exchangeable_randomized_prefix_tail_to_alpha_ratio": max(
                row["ur_eccp_exch_worst_case_failure_probability"] / row["alpha"]
                for row in exchangeable_prefix_cases
            ),
            "invalid_exchangeable_prefix_rejection_count": sum(
                row["invalid_eccp_exch_control_rejected"]
                for row in exchangeable_prefix_cases
            ),
            "invalid_exchangeable_randomized_prefix_rejection_count": sum(
                row["invalid_ur_eccp_exch_control_rejected"]
                for row in exchangeable_prefix_cases
            ),
            "all_merged_expectations_exact": all(row["mean_merged_e_abs_error"] < 1e-11 for row in cases),
            "all_markov_coverage_events_pass": all(row["coverage_pass"] for row in cases),
            "all_randomized_uniform_coverage_events_pass": all(
                row["randomized_uniform_coverage_pass"] for row in cases
            ),
            "all_arbitrary_dependence_coverage_pass": all(
                row["arbitrary_dependence_coverage_pass"] for row in cases
            ),
            "all_randomized_arbitrary_dependence_coverage_pass": all(
                row["randomized_arbitrary_dependence_coverage_pass"]
                for row in cases
            ),
            "maximum_valid_worst_case_tail_probability": max(
                row["worst_case_dependent_tail_probability"] for row in cases
            ),
            "maximum_valid_tail_to_alpha_ratio": max(
                row["worst_case_dependent_tail_probability"] / row["alpha"]
                for row in cases
            ),
            "maximum_valid_randomized_worst_case_failure_probability": max(
                row["randomized_worst_case_dependent_failure_probability"]
                for row in cases
            ),
            "maximum_valid_randomized_tail_to_alpha_ratio": max(
                row["randomized_worst_case_dependent_failure_probability"]
                / row["alpha"]
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
            "invalid_randomized_arbitrary_dependence_rejection_count": sum(
                row["invalid_randomized_arbitrary_dependence_control_rejected"]
                for row in cases
            ),
            "invalid_randomized_arbitrary_dependence_detected": any(
                row["invalid_randomized_arbitrary_dependence_control_rejected"]
                for row in cases
            ),
            "adaptive_weight_rejection_count": sum(
                row["adaptive_weight_control_rejected"] for row in cases
            ),
            "adaptive_weight_control_detected": any(
                row["adaptive_weight_control_rejected"] for row in cases
            ),
            "adaptive_randomized_weight_rejection_count": sum(
                row["adaptive_randomized_weight_control_rejected"] for row in cases
            ),
            "adaptive_randomized_weight_control_detected": any(
                row["adaptive_randomized_weight_control_rejected"] for row in cases
            ),
            "minimum_adaptive_tail_to_alpha_ratio": min(
                row["adaptive_max_worst_case_dependent_tail_probability"] / row["alpha"]
                for row in cases
            ),
            "minimum_adaptive_randomized_tail_to_alpha_ratio": min(
                row["adaptive_randomized_worst_case_dependent_failure_probability"]
                / row["alpha"]
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

````


````json title=claim3_independent_e_merge.json
{
  "cases": [
    {
      "adaptive_max_coverage": 0.8264462809917356,
      "adaptive_max_worst_case_dependent_tail_probability": 0.18181818181818182,
      "adaptive_randomized_uniform_failure_probability": 0.18454097836730804,
      "adaptive_randomized_weight_control_rejected": true,
      "adaptive_randomized_worst_case_dependent_failure_probability": 0.19454414352118643,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.1,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 121,
      "coverage_event_probability": 0.9917355371900827,
      "coverage_pass": true,
      "folds": 2,
      "invalid_arbitrary_dependence_control_rejected": true,
      "invalid_control_rejected": true,
      "invalid_randomized_arbitrary_dependence_control_rejected": true,
      "invalid_randomized_uniform_failure_probability": 0.18512277522310025,
      "invalid_randomized_worst_case_dependent_failure_probability": 0.19454414365450118,
      "invalid_scaled_coverage": 0.8264462809917356,
      "invalid_worst_case_dependent_tail_probability": 0.18181818181818182,
      "mean_merged_e": 0.9999999999999998,
      "mean_merged_e_abs_error": 2.220446049250313e-16,
      "n_calibration": 10,
      "randomized_arbitrary_dependence_coverage_pass": true,
      "randomized_uniform_coverage": 0.90024799347025,
      "randomized_uniform_coverage_pass": true,
      "randomized_uniform_failure_probability": 0.09975200652975003,
      "randomized_worst_case_dependent_coverage": 0.9,
      "randomized_worst_case_dependent_failure_probability": 0.09999999999999996,
      "rank_tuple_count": 121,
      "required_coverage": 0.9,
      "weights": [
        0.5,
        0.5
      ],
      "worst_case_dependent_coverage": 0.9090909090909091,
      "worst_case_dependent_tail_probability": 0.09090909090909091
    },
    {
      "adaptive_max_coverage": 0.7513148009015778,
      "adaptive_max_worst_case_dependent_tail_probability": 0.2727272727272728,
      "adaptive_randomized_uniform_failure_probability": 0.2629279672453386,
      "adaptive_randomized_weight_control_rejected": true,
      "adaptive_randomized_worst_case_dependent_failure_probability": 0.291816165760236,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.1,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 1331,
      "coverage_event_probability": 0.9992486851990984,
      "coverage_pass": true,
      "folds": 3,
      "invalid_arbitrary_dependence_control_rejected": true,
      "invalid_control_rejected": false,
      "invalid_randomized_arbitrary_dependence_control_rejected": true,
      "invalid_randomized_uniform_failure_probability": 0.19068347979262973,
      "invalid_randomized_worst_case_dependent_failure_probability": 0.19999999999999996,
      "invalid_scaled_coverage": 0.976709241172051,
      "invalid_worst_case_dependent_tail_probability": 0.13636363636363635,
      "mean_merged_e": 0.9999999999999997,
      "mean_merged_e_abs_error": 3.3306690738754696e-16,
      "n_calibration": 10,
      "randomized_arbitrary_dependence_coverage_pass": true,
      "randomized_uniform_coverage": 0.9000225448609318,
      "randomized_uniform_coverage_pass": true,
      "randomized_uniform_failure_probability": 0.09997745513906815,
      "randomized_worst_case_dependent_coverage": 0.9,
      "randomized_worst_case_dependent_failure_probability": 0.09999999999999995,
      "rank_tuple_count": 1331,
      "required_coverage": 0.9,
      "weights": [
        0.3333333333333333,
        0.3333333333333333,
        0.3333333333333333
      ],
      "worst_case_dependent_coverage": 0.9090909090909091,
      "worst_case_dependent_tail_probability": 0.09090909090909091
    },
    {
      "adaptive_max_coverage": 0.8264462809917356,
      "adaptive_max_worst_case_dependent_tail_probability": 0.18181818181818182,
      "adaptive_randomized_uniform_failure_probability": 0.18454097836730804,
      "adaptive_randomized_weight_control_rejected": true,
      "adaptive_randomized_worst_case_dependent_failure_probability": 0.19454414352118643,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.1,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 121,
      "coverage_event_probability": 0.9917355371900827,
      "coverage_pass": true,
      "folds": 2,
      "invalid_arbitrary_dependence_control_rejected": false,
      "invalid_control_rejected": false,
      "invalid_randomized_arbitrary_dependence_control_rejected": true,
      "invalid_randomized_uniform_failure_probability": 0.14590810774087587,
      "invalid_randomized_worst_case_dependent_failure_probability": 0.15045356228633044,
      "invalid_scaled_coverage": 0.9090909090909091,
      "invalid_worst_case_dependent_tail_probability": 0.09090909090909091,
      "mean_merged_e": 0.9999999999999998,
      "mean_merged_e_abs_error": 2.220446049250313e-16,
      "n_calibration": 10,
      "randomized_arbitrary_dependence_coverage_pass": true,
      "randomized_uniform_coverage": 0.90024799347025,
      "randomized_uniform_coverage_pass": true,
      "randomized_uniform_failure_probability": 0.09975200652975003,
      "randomized_worst_case_dependent_coverage": 0.9,
      "randomized_worst_case_dependent_failure_probability": 0.09999999999999996,
      "rank_tuple_count": 121,
      "required_coverage": 0.9,
      "weights": [
        0.25,
        0.75
      ],
      "worst_case_dependent_coverage": 0.9090909090909091,
      "worst_case_dependent_tail_probability": 0.09090909090909091
    },
    {
      "adaptive_max_coverage": 0.7513148009015778,
      "adaptive_max_worst_case_dependent_tail_probability": 0.2727272727272728,
      "adaptive_randomized_uniform_failure_probability": 0.2629279672453386,
      "adaptive_randomized_weight_control_rejected": true,
      "adaptive_randomized_worst_case_dependent_failure_probability": 0.291816165760236,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.1,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 1331,
      "coverage_event_probability": 0.9992486851990984,
      "coverage_pass": true,
      "folds": 3,
      "invalid_arbitrary_dependence_control_rejected": false,
      "invalid_control_rejected": false,
      "invalid_randomized_arbitrary_dependence_control_rejected": true,
      "invalid_randomized_uniform_failure_probability": 0.17127194073815524,
      "invalid_randomized_worst_case_dependent_failure_probability": 0.17854466801088242,
      "invalid_scaled_coverage": 0.9090909090909091,
      "invalid_worst_case_dependent_tail_probability": 0.09090909090909091,
      "mean_merged_e": 0.9999999999999998,
      "mean_merged_e_abs_error": 2.220446049250313e-16,
      "n_calibration": 10,
      "randomized_arbitrary_dependence_coverage_pass": true,
      "randomized_uniform_coverage": 0.9000225448609318,
      "randomized_uniform_coverage_pass": true,
      "randomized_uniform_failure_probability": 0.09997745513906815,
      "randomized_worst_case_dependent_coverage": 0.9,
      "randomized_worst_case_dependent_failure_probability": 0.09999999999999998,
      "rank_tuple_count": 1331,
      "required_coverage": 0.9,
      "weights": [
        0.1,
        0.3,
        0.6
      ],
      "worst_case_dependent_coverage": 0.9090909090909091,
      "worst_case_dependent_tail_probability": 0.09090909090909091
    },
    {
      "adaptive_max_coverage": 0.6830134553650707,
      "adaptive_max_worst_case_dependent_tail_probability": 0.36363636363636254,
      "adaptive_randomized_uniform_failure_probability": 0.3334135825525855,
      "adaptive_randomized_weight_control_rejected": true,
      "adaptive_randomized_worst_case_dependent_failure_probability": 0.38906979628512295,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.1,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 14641,
      "coverage_event_probability": 0.9999316986544635,
      "coverage_pass": true,
      "folds": 4,
      "invalid_arbitrary_dependence_control_rejected": true,
      "invalid_control_rejected": false,
      "invalid_randomized_arbitrary_dependence_control_rejected": true,
      "invalid_randomized_uniform_failure_probability": 0.18815562885880951,
      "invalid_randomized_worst_case_dependent_failure_probability": 0.19727207177918907,
      "invalid_scaled_coverage": 0.9083395942900075,
      "invalid_worst_case_dependent_tail_probability": 0.18181818181818185,
      "mean_merged_e": 0.9999999999999998,
      "mean_merged_e_abs_error": 2.220446049250313e-16,
      "n_calibration": 10,
      "randomized_arbitrary_dependence_coverage_pass": true,
      "randomized_uniform_coverage": 0.900002049532812,
      "randomized_uniform_coverage_pass": true,
      "randomized_uniform_failure_probability": 0.09999795046718798,
      "randomized_worst_case_dependent_coverage": 0.9,
      "randomized_worst_case_dependent_failure_probability": 0.09999999999999999,
      "rank_tuple_count": 14641,
      "required_coverage": 0.9,
      "weights": [
        0.05,
        0.15,
        0.3,
        0.5
      ],
      "worst_case_dependent_coverage": 0.9090909090909091,
      "worst_case_dependent_tail_probability": 0.09090909090909091
    },
    {
      "adaptive_max_coverage": 0.81859410430839,
      "adaptive_max_worst_case_dependent_tail_probability": 0.19047619047619047,
      "adaptive_randomized_uniform_failure_probability": 0.18476227382655455,
      "adaptive_randomized_weight_control_rejected": true,
      "adaptive_randomized_worst_case_dependent_failure_probability": 0.19428630069079045,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.1,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 441,
      "coverage_event_probability": 0.9909297052154195,
      "coverage_pass": true,
      "folds": 2,
      "invalid_arbitrary_dependence_control_rejected": false,
      "invalid_control_rejected": false,
      "invalid_randomized_arbitrary_dependence_control_rejected": true,
      "invalid_randomized_uniform_failure_probability": 0.13447665960100735,
      "invalid_randomized_worst_case_dependent_failure_probability": 0.13828618292714043,
      "invalid_scaled_coverage": 0.9047619047619048,
      "invalid_worst_case_dependent_tail_probability": 0.09523809523809523,
      "mean_merged_e": 0.9999999999999999,
      "mean_merged_e_abs_error": 1.1102230246251565e-16,
      "n_calibration": 20,
      "randomized_arbitrary_dependence_coverage_pass": true,
      "randomized_uniform_coverage": 0.9002720809194412,
      "randomized_uniform_coverage_pass": true,
      "randomized_uniform_failure_probability": 0.09972791908055882,
      "randomized_worst_case_dependent_coverage": 0.9,
      "randomized_worst_case_dependent_failure_probability": 0.09999999999999999,
      "rank_tuple_count": 441,
      "required_coverage": 0.9,
      "weights": [
        0.2,
        0.8
      ],
      "worst_case_dependent_coverage": 0.9047619047619048,
      "worst_case_dependent_tail_probability": 0.09523809523809523
    },
    {
      "adaptive_max_coverage": 0.7406327610409243,
      "adaptive_max_worst_case_dependent_tail_probability": 0.28571428571428575,
      "adaptive_randomized_uniform_failure_probability": 0.2638033484888897,
      "adaptive_randomized_weight_control_rejected": true,
      "adaptive_randomized_worst_case_dependent_failure_probability": 0.2914294482565785,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.1,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 9261,
      "coverage_event_probability": 0.9991361624014685,
      "coverage_pass": true,
      "folds": 3,
      "invalid_arbitrary_dependence_control_rejected": false,
      "invalid_control_rejected": false,
      "invalid_randomized_arbitrary_dependence_control_rejected": true,
      "invalid_randomized_uniform_failure_probability": 0.15219088667469094,
      "invalid_randomized_worst_case_dependent_failure_probability": 0.157905172344055,
      "invalid_scaled_coverage": 0.9047619047619048,
      "invalid_worst_case_dependent_tail_probability": 0.09523809523809523,
      "mean_merged_e": 0.9999999999999998,
      "mean_merged_e_abs_error": 2.220446049250313e-16,
      "n_calibration": 20,
      "randomized_arbitrary_dependence_coverage_pass": true,
      "randomized_uniform_coverage": 0.9000259124685183,
      "randomized_uniform_coverage_pass": true,
      "randomized_uniform_failure_probability": 0.09997408753148178,
      "randomized_worst_case_dependent_coverage": 0.9,
      "randomized_worst_case_dependent_failure_probability": 0.09999999999999995,
      "rank_tuple_count": 9261,
      "required_coverage": 0.9,
      "weights": [
        0.1,
        0.2,
        0.7
      ],
      "worst_case_dependent_coverage": 0.9047619047619048,
      "worst_case_dependent_tail_probability": 0.09523809523809523
    },
    {
      "adaptive_max_coverage": 0.5305042651981428,
      "adaptive_max_worst_case_dependent_tail_probability": 0.5714285714285713,
      "adaptive_randomized_uniform_failure_probability": 0.47318103347825835,
      "adaptive_randomized_weight_control_rejected": true,
      "adaptive_randomized_worst_case_dependent_failure_probability": 0.577396579293704,
      "adaptive_weight_control_rejected": true,
      "alpha": 0.2,
      "arbitrary_dependence_coverage_pass": true,
      "coupling_lp_variables": 9261,
      "coverage_event_probability": 0.9930892992117482,
      "coverage_pass": true,
      "folds": 3,
      "invalid_arbitrary_dependence_control_rejected": true,
      "invalid_control_rejected": true,
      "invalid_randomized_arbitrary_dependence_control_rejected": true,
      "invalid_randomized_uniform_failure_probability": 0.3531363348706932,
      "invalid_randomized_worst_case_dependent_failure_probability": 0.3924655266043606,
      "invalid_scaled_coverage": 0.7801533311737393,
      "invalid_worst_case_dependent_tail_probability": 0.3809523809523808,
      "mean_merged_e": 1.0,
      "mean_merged_e_abs_error": 0.0,
      "n_calibration": 20,
      "randomized_arbitrary_dependence_coverage_pass": true,
      "randomized_uniform_coverage": 0.8002733595779199,
      "randomized_uniform_coverage_pass": true,
      "randomized_uniform_failure_probability": 0.19972664042208013,
      "randomized_worst_case_dependent_coverage": 0.8,
      "randomized_worst_case_dependent_failure_probability": 0.19999999999999998,
      "rank_tuple_count": 9261,
      "required_coverage": 0.8,
      "weights": [
        0.15,
        0.35,
        0.5
      ],
      "worst_case_dependent_coverage": 0.8095238095238095,
      "worst_case_dependent_tail_probability": 0.19047619047619047
    }
  ],
  "exchangeable_prefix_cases": [
    {
      "alpha": 0.1,
      "eccp_exch_coverage_pass": true,
      "eccp_exch_worst_case_failure_probability": 0.09090909090909091,
      "exchangeable_orbit_count": 66,
      "folds": 2,
      "invalid_eccp_exch_control_rejected": true,
      "invalid_eccp_exch_worst_case_failure_probability": 0.18181818181818182,
      "invalid_ur_eccp_exch_control_rejected": true,
      "invalid_ur_eccp_exch_worst_case_failure_probability": 0.19454414365450118,
      "n_calibration": 10,
      "ur_eccp_exch_coverage_pass": true,
      "ur_eccp_exch_worst_case_failure_probability": 0.09727207182725059
    },
    {
      "alpha": 0.1,
      "eccp_exch_coverage_pass": true,
      "eccp_exch_worst_case_failure_probability": 0.09090909090909091,
      "exchangeable_orbit_count": 286,
      "folds": 3,
      "invalid_eccp_exch_control_rejected": true,
      "invalid_eccp_exch_worst_case_failure_probability": 0.18181818181818182,
      "invalid_ur_eccp_exch_control_rejected": true,
      "invalid_ur_eccp_exch_worst_case_failure_probability": 0.1945441436545002,
      "n_calibration": 10,
      "ur_eccp_exch_coverage_pass": true,
      "ur_eccp_exch_worst_case_failure_probability": 0.09727207182725059
    },
    {
      "alpha": 0.1,
      "eccp_exch_coverage_pass": true,
      "eccp_exch_worst_case_failure_probability": 0.09090909090909091,
      "exchangeable_orbit_count": 1001,
      "folds": 4,
      "invalid_eccp_exch_control_rejected": true,
      "invalid_eccp_exch_worst_case_failure_probability": 0.18181818181818182,
      "invalid_ur_eccp_exch_control_rejected": true,
      "invalid_ur_eccp_exch_worst_case_failure_probability": 0.19454414365450115,
      "n_calibration": 10,
      "ur_eccp_exch_coverage_pass": true,
      "ur_eccp_exch_worst_case_failure_probability": 0.09727207182725059
    },
    {
      "alpha": 0.1,
      "eccp_exch_coverage_pass": true,
      "eccp_exch_worst_case_failure_probability": 0.09523809523809523,
      "exchangeable_orbit_count": 1771,
      "folds": 3,
      "invalid_eccp_exch_control_rejected": true,
      "invalid_eccp_exch_worst_case_failure_probability": 0.19047619047619047,
      "invalid_ur_eccp_exch_control_rejected": true,
      "invalid_ur_eccp_exch_worst_case_failure_probability": 0.19428629948325857,
      "n_calibration": 20,
      "ur_eccp_exch_coverage_pass": true,
      "ur_eccp_exch_worst_case_failure_probability": 0.0971431503458677
    },
    {
      "alpha": 0.2,
      "eccp_exch_coverage_pass": true,
      "eccp_exch_worst_case_failure_probability": 0.19047619047619047,
      "exchangeable_orbit_count": 1771,
      "folds": 3,
      "invalid_eccp_exch_control_rejected": true,
      "invalid_eccp_exch_worst_case_failure_probability": 0.38095238095238093,
      "invalid_ur_eccp_exch_control_rejected": true,
      "invalid_ur_eccp_exch_worst_case_failure_probability": 0.3849310530040518,
      "n_calibration": 20,
      "ur_eccp_exch_coverage_pass": true,
      "ur_eccp_exch_worst_case_failure_probability": 0.19246552663358346
    }
  ],
  "implementation": "independent exact enumeration and coupling LP for deterministic and independent-uniform randomized fixed weighted e-merges",
  "scope": "fixed or tuning-independent weights under arbitrary dependence; adaptive inference-dependent weights are an invalid control",
  "summary": {
    "adaptive_randomized_weight_control_detected": true,
    "adaptive_randomized_weight_rejection_count": 8,
    "adaptive_weight_control_detected": true,
    "adaptive_weight_rejection_count": 8,
    "all_arbitrary_dependence_coverage_pass": true,
    "all_exchangeable_prefix_coverage_pass": true,
    "all_exchangeable_randomized_prefix_coverage_pass": true,
    "all_markov_coverage_events_pass": true,
    "all_merged_expectations_exact": true,
    "all_randomized_arbitrary_dependence_coverage_pass": true,
    "all_randomized_uniform_coverage_events_pass": true,
    "case_count": 8,
    "equal_weight_case_count": 2,
    "exchangeable_prefix_case_count": 5,
    "invalid_arbitrary_dependence_detected": true,
    "invalid_arbitrary_dependence_rejection_count": 4,
    "invalid_exchangeable_prefix_rejection_count": 5,
    "invalid_exchangeable_randomized_prefix_rejection_count": 5,
    "invalid_randomized_arbitrary_dependence_detected": true,
    "invalid_randomized_arbitrary_dependence_rejection_count": 8,
    "invalid_scaling_control_detected": true,
    "invalid_scaling_control_rejection_count": 2,
    "maximum_exchangeable_prefix_tail_to_alpha_ratio": 0.9523809523809523,
    "maximum_exchangeable_randomized_prefix_tail_to_alpha_ratio": 0.9727207182725058,
    "maximum_valid_randomized_tail_to_alpha_ratio": 0.9999999999999999,
    "maximum_valid_randomized_worst_case_failure_probability": 0.19999999999999998,
    "maximum_valid_tail_to_alpha_ratio": 0.9523809523809523,
    "maximum_valid_worst_case_tail_probability": 0.19047619047619047,
    "minimum_adaptive_randomized_tail_to_alpha_ratio": 1.9428630069079045,
    "minimum_adaptive_tail_to_alpha_ratio": 1.8181818181818181,
    "nonuniform_weight_case_count": 6
  }
}

````


````output
{"adaptive_randomized_weight_control_detected": true, "adaptive_randomized_weight_rejection_count": 8, "adaptive_weight_control_detected": true, "adaptive_weight_rejection_count": 8, "all_arbitrary_dependence_coverage_pass": true, "all_exchangeable_prefix_coverage_pass": true, "all_exchangeable_randomized_prefix_coverage_pass": true, "all_markov_coverage_events_pass": true, "all_merged_expectations_exact": true, "all_randomized_arbitrary_dependence_coverage_pass": true, "all_randomized_uniform_coverage_events_pass": true, "case_count": 8, "equal_weight_case_count": 2, "exchangeable_prefix_case_count": 5, "invalid_arbitrary_dependence_detected": true, "invalid_arbitrary_dependence_rejection_count": 4, "invalid_exchangeable_prefix_rejection_count": 5, "invalid_exchangeable_randomized_prefix_rejection_count": 5, "invalid_randomized_arbitrary_dependence_detected": true, "invalid_randomized_arbitrary_dependence_rejection_count": 8, "invalid_scaling_control_detected": true, "invalid_scaling_control_rejection_count": 2, "maximum_exchangeable_prefix_tail_to_alpha_ratio": 0.9523809523809523, "maximum_exchangeable_randomized_prefix_tail_to_alpha_ratio": 0.9727207182725058, "maximum_valid_randomized_tail_to_alpha_ratio": 0.9999999999999999, "maximum_valid_randomized_worst_case_failure_probability": 0.19999999999999998, "maximum_valid_tail_to_alpha_ratio": 0.9523809523809523, "maximum_valid_worst_case_tail_probability": 0.19047619047619047, "minimum_adaptive_randomized_tail_to_alpha_ratio": 1.9428630069079045, "minimum_adaptive_tail_to_alpha_ratio": 1.8181818181818181, "nonuniform_weight_case_count": 6}

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_c795c04eb742", "created_at": "2026-07-19T18:54:05+00:00", "title": "Full released cross-conformal protocol", "command": ["python", "repro/src/run_author_ccp.py", "--source", "upstream", "--output-dir", "outputs/raw/author_ccp"], "exit_code": 0, "duration_s": 7609.076}
-->
````bash
$ python repro/src/run_author_ccp.py --source upstream --output-dir outputs/raw/author_ccp
````

exit 0 · 7609.1s


````python title=run_author_ccp.py
#!/usr/bin/env python3
"""Run the author CCP primitives at the paper's full reported protocol.

The upstream ``e-ccp/main.py`` hard-codes one dataset and five folds.  This
wrapper leaves every author estimator untouched and supplies the paper's three
reported dataset/fold configurations (Boston/Abalone K=15, Parkinson K=20)
and its 100 released seeds. The source calls its fourth classical calibrator
``ECCP(pow)`` and implements ``5(1-p)^4``, while the paper defines F3 as
``2(1-p)``. The wrapper reconstructs that paper-specified linear calibrator
from the returned author p-values and identical randomization stream. It writes
one resumable raw file per data set.
"""

from __future__ import annotations

import argparse
import importlib
import json
import math
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


METHOD_KEYS = (
    ("mod-cross", "int_cc"),
    ("e-mod-cross", "int_cce"),
    ("u-mod-cross", "int_ccu"),
    ("eu-mod-cross", "int_cceu"),
    ("cross", "int_ccs"),
    ("ECCP", "int_cc_eval"),
    ("ECCP_exch", "int_cc_ev_exch"),
    ("UR-ECCP_exch", "int_cc_ev_exch_U"),
    ("ECCP(ind)", "int_cc_eval_ind"),
    ("ECCP(sqrt)", "int_cc_eval_sqrt"),
    ("ECCP(log)", "int_cc_eval_log"),
    ("ECCP(linear)", "int_cc_eval_linear"),
    ("ECCP (2α)", "int_cc_eval_2alpha"),
)
PAPER_DATASETS = {"boston": 15, "abalone": 15, "parkinson": 20}
MODELS = ("OLS", "RF", "Lasso")
SEEDS = tuple(range(45, 145))
EXECUTION_ADAPTER = "vectorized-exact-postprocessing-v1"


def source_descriptor(source_root: Path) -> str:
    """Return portable source provenance rather than an absolute local path."""
    commit = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return f"Nabil-Ala/P2E_calibration@{commit}"


def attach_paper_linear_calibrator(
    result, functions, *, n_train: int, k: int, alpha: float, seed: int
):
    """Add paper F3=2(1-p) intervals to an unchanged author model result.

    Each released model function returns the foldwise p-values and candidate
    grid. Replaying its local RNG through the fold permutation recovers the
    exact U-values used for every other randomized e-value baseline.
    """
    if "int_cc_eval_linear" in result:
        return result
    p_values = np.asarray(result["p_vals"], dtype=float)
    y_grid = np.asarray(result["ys"], dtype=float)
    if p_values.ndim != 3 or p_values.shape[0] != len(y_grid):
        raise RuntimeError("unexpected author p-value/grid shape")
    if p_values.shape[1] != k:
        raise RuntimeError(f"unexpected author fold count: {p_values.shape[1]} != {k}")
    if not np.isfinite(p_values).all() or np.any((p_values < 0.0) | (p_values > 1.0)):
        raise RuntimeError("author p-values are non-finite or outside [0,1]")

    rng = np.random.default_rng(seed)
    rng.permutation(n_train)
    u_values = rng.random(p_values.shape[2])
    if np.any(u_values <= 0.0):
        raise RuntimeError("zero randomization draw prevents finite linear e-values")
    linear_e_values = 2.0 * (1.0 - p_values)
    merged = linear_e_values.mean(axis=1) / u_values[None, :]
    intervals = [
        functions.set_cc_eval(merged[:, index], y_grid, alpha)
        for index in range(p_values.shape[2])
    ]
    augmented = dict(result)
    augmented["int_cc_eval_linear"] = intervals
    return augmented


def call_literal_author_model(
    name, functions, y_train, x_train, x_test, *, k, alpha, config, seed,
    n_grid=300,
):
    """Run the pinned source function literally; retained as a parity oracle."""
    if name == "OLS":
        result = functions.cc_ols(
            y=y_train, X=x_train, x_test=x_test, K=k, alpha=alpha,
            n_grid=n_grid, grid_factor=1.0, random_state=seed,
        )
    elif name == "RF":
        result = functions.cc_rf(
            y=y_train, X=x_train, x_test=x_test, K=k, alpha=alpha,
            ntree=config["ntree"], n_grid=n_grid, grid_factor=1.0, random_state=seed,
        )
    elif name == "Lasso":
        result = functions.cc_lasso(
            y=y_train, X=x_train, x_test=x_test, K=k, alpha=alpha,
            n_grid=n_grid, grid_factor=1.0, random_state=seed,
            lambda_=config["lambda_"],
        )
    else:
        raise ValueError(name)
    return attach_paper_linear_calibrator(
        result,
        functions,
        n_train=len(y_train),
        k=k,
        alpha=alpha,
        seed=seed,
    )


def intervals_from_p_values(
    p_values, grid, *, functions, alpha: float, m: int, used: int, u_values
):
    """Vectorize only the source's deterministic p/e aggregation stage.

    The pinned implementation loops over every grid/test pair in Python. This
    function evaluates the same formulas over NumPy arrays while retaining the
    fold axis and its reduction order. Large temporary arrays are created one
    calibrator at a time to keep the Parkinson peak memory bounded.
    """
    p_values = np.asarray(p_values, dtype=float)
    grid = np.asarray(grid, dtype=float)
    u_values = np.asarray(u_values, dtype=float)
    if p_values.ndim != 3 or p_values.shape[0] != len(grid):
        raise RuntimeError("unexpected p-value/grid shape in vectorized adapter")
    if p_values.shape[2] != len(u_values):
        raise RuntimeError("unexpected p-value/randomization shape")
    if not np.isfinite(p_values).all() or np.any((p_values <= 0.0) | (p_values > 1.0)):
        raise RuntimeError("p-values must be finite and in (0,1]")
    if not np.isfinite(u_values).all() or np.any((u_values <= 0.0) | (u_values >= 1.0)):
        raise RuntimeError("randomization draws must be finite and in (0,1)")

    folds = p_values.shape[1]
    fold_denominators = np.arange(1, folds + 1, dtype=float)[None, :, None]
    randomizer = u_values[None, :]
    pv_cc = np.mean(p_values, axis=1)

    cumulative_p = np.cumsum(p_values, axis=1) / fold_denominators
    pv_ecc = np.min(cumulative_p, axis=1)
    del cumulative_p
    pv_ucc = pv_cc / (2.0 - randomizer)
    pv_eucc = np.minimum(p_values[:, 0, :] / (2.0 - randomizer), pv_ecc)
    pv_ccs = (
        1.0 + np.sum(p_values * (m + 1.0) - 1.0, axis=1)
    ) / (used + 1.0)

    e_ind = np.mean((p_values <= alpha).astype(float) / alpha, axis=1) / randomizer
    e_log = np.mean(-np.log(p_values), axis=1) / randomizer
    e_power = np.mean(5.0 * (1.0 - p_values) ** 4, axis=1) / randomizer
    e_sqrt = np.mean(p_values ** (-0.5) - 1.0, axis=1) / randomizer
    e_linear = np.mean(2.0 * (1.0 - p_values), axis=1) / randomizer

    c_value, location = functions.get_C_s(alpha, m)
    e_values = functions.f_p_to_e(p_values, alpha, c_value, location)
    e_mean = np.mean(e_values, axis=1) / randomizer
    cumulative_e = np.cumsum(e_values, axis=1) / fold_denominators
    e_exch = np.max(cumulative_e, axis=1)
    e_exch_u = np.maximum(e_exch, e_values[:, 0, :] / randomizer)
    del cumulative_e, e_values

    c_value_2, location_2 = functions.get_C_s(2.0 * alpha, m)
    e_values_2 = functions.f_p_to_e(
        p_values, 2.0 * alpha, c_value_2, location_2
    )
    e_mean_2 = np.mean(e_values_2, axis=1) / randomizer
    del e_values_2

    def p_intervals(values):
        return [
            functions.set_cc(values[:, index], grid, alpha)
            for index in range(values.shape[1])
        ]

    def e_intervals(values, level=alpha):
        return [
            functions.set_cc_eval(values[:, index], grid, level)
            for index in range(values.shape[1])
        ]

    return {
        "p_vals": p_values,
        "ys": grid,
        "int_cc": p_intervals(pv_cc),
        "int_cce": p_intervals(pv_ecc),
        "int_ccu": p_intervals(pv_ucc),
        "int_cceu": p_intervals(pv_eucc),
        "int_ccs": p_intervals(pv_ccs),
        "int_cc_eval": e_intervals(e_mean),
        "int_cc_ev_exch": e_intervals(e_exch),
        "int_cc_ev_exch_U": e_intervals(e_exch_u),
        "int_cc_eval_2alpha": e_intervals(e_mean_2, 2.0 * alpha),
        "int_cc_eval_ind": e_intervals(e_ind),
        "int_cc_eval_sqrt": e_intervals(e_sqrt),
        "int_cc_eval_log": e_intervals(e_log),
        "int_cc_eval_pow": e_intervals(e_power),
        "int_cc_eval_linear": e_intervals(e_linear),
    }


def call_vectorized_author_model(
    name, functions, y_train, x_train, x_test, *, k, alpha, config, seed,
    n_grid=300,
):
    """Reproduce the source estimator/p-value core with vectorized aggregation."""
    y_train = np.asarray(y_train).ravel()
    x_train = np.asarray(x_train)
    x_test = np.asarray(x_test)
    if x_test.ndim == 1:
        x_test = x_test.reshape(1, -1)
    n_train = len(y_train)
    n_test = x_test.shape[0]
    grid = np.linspace(-np.max(np.abs(y_train)), np.max(np.abs(y_train)), num=n_grid)
    m = n_train // k
    if m == 0:
        raise ValueError("n < K: cannot form equal-size folds")
    used = m * k
    rng = np.random.default_rng(seed)
    indices = rng.permutation(n_train)[:used]
    folds = indices.reshape(k, m)
    p_values = np.empty((n_grid, k, n_test), dtype=float)

    for fold in range(k):
        calibration_idx = folds[fold]
        fit_idx = np.setdiff1d(indices, calibration_idx)
        if name == "OLS":
            fitted = functions.ols_pseudo(x_train[fit_idx, :], y_train[fit_idx])
            calibration_prediction = functions.ols_pseudo_predict(
                fitted, x_train[calibration_idx, :]
            )
            test_prediction = functions.ols_pseudo_predict(fitted, x_test)
        elif name == "RF":
            fitted = functions.RandomForestRegressor(
                n_estimators=config["ntree"],
                max_features=1.0,
                n_jobs=-1,
                random_state=seed,
            )
            fitted.fit(x_train[fit_idx, :], y_train[fit_idx])
            calibration_prediction = fitted.predict(x_train[calibration_idx, :])
            test_prediction = fitted.predict(x_test)
        elif name == "Lasso":
            fitted = functions.Lasso(
                alpha=config["lambda_"],
                fit_intercept=True,
                max_iter=10000,
                random_state=seed,
            )
            fitted.fit(x_train[fit_idx, :], y_train[fit_idx])
            calibration_prediction = fitted.predict(x_train[calibration_idx, :])
            test_prediction = fitted.predict(x_test)
        else:
            raise ValueError(name)

        calibration_errors = np.abs(
            y_train[calibration_idx] - np.asarray(calibration_prediction).ravel()
        )
        candidate_errors = np.abs(
            grid[:, None] - np.asarray(test_prediction).ravel()[None, :]
        )
        comparisons = (
            calibration_errors[:, None, None] >= candidate_errors[None, :, :]
        )
        p_values[:, fold, :] = (1.0 + comparisons.sum(axis=0)) / (m + 1.0)

    # Do not retain the largest foldwise comparison tensor while constructing
    # the full set of aggregated e/p arrays (material for Parkinson memory).
    del comparisons, candidate_errors, calibration_errors
    del calibration_prediction, test_prediction, fitted
    u_values = rng.random(n_test)
    return intervals_from_p_values(
        p_values,
        grid,
        functions=functions,
        alpha=alpha,
        m=m,
        used=used,
        u_values=u_values,
    )


def call_author_model(
    name, functions, y_train, x_train, x_test, *, k, alpha, config, seed
):
    return call_vectorized_author_model(
        name,
        functions,
        y_train,
        x_train,
        x_test,
        k=k,
        alpha=alpha,
        config=config,
        seed=seed,
    )


def validated_completed_seeds(rows, dataset_key, k):
    """Validate a resumable checkpoint and return its complete seed set."""
    expected_cells = {(model, method) for model in MODELS for method, _ in METHOD_KEYS}
    cells_by_seed = defaultdict(set)
    for row in rows:
        if str(row["dataset_key"]) != dataset_key or int(row["folds"]) != k:
            raise RuntimeError(f"checkpoint scope mismatch for {dataset_key}")
        seed = int(row["seed"])
        if seed not in SEEDS:
            raise RuntimeError(f"unexpected checkpoint seed for {dataset_key}: {seed}")
        cell = (str(row["model"]), str(row["method"]))
        if cell in cells_by_seed[seed]:
            raise RuntimeError(f"duplicate checkpoint cell for {dataset_key}, seed {seed}: {cell}")
        coverage = float(row["coverage"])
        length = float(row["length"])
        if not (math.isfinite(coverage) and math.isfinite(length)):
            raise RuntimeError(
                f"non-finite checkpoint metric for {dataset_key}, seed {seed}: {cell}"
            )
        if not (0.0 <= coverage <= 1.0 and length >= 0.0):
            raise RuntimeError(
                f"out-of-range checkpoint metric for {dataset_key}, seed {seed}: "
                f"{cell} coverage={coverage}, length={length}"
            )
        cells_by_seed[seed].add(cell)
    for seed, cells in cells_by_seed.items():
        if cells != expected_cells:
            missing = sorted(expected_cells - cells)
            extra = sorted(cells - expected_cells)
            raise RuntimeError(
                f"incomplete checkpoint seed for {dataset_key}, seed {seed}: "
                f"missing={missing}, extra={extra}"
            )
    return set(cells_by_seed)


def write_json_atomic(path, payload):
    """Atomically replace a JSON artifact so an interrupted write cannot look complete."""
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def write_checkpoint(path, protocol, dataset_key, k, rows):
    completed = validated_completed_seeds(rows, dataset_key, k)
    payload = {
        "protocol": protocol,
        "dataset_key": dataset_key,
        "folds": k,
        "completed_seeds": sorted(completed),
        "rows": rows,
    }
    write_json_atomic(path, payload)


def load_checkpoint(path, protocol, dataset_key, k):
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("protocol") != protocol:
        raise RuntimeError(f"checkpoint protocol mismatch for {dataset_key}")
    if payload.get("dataset_key") != dataset_key or int(payload.get("folds")) != k:
        raise RuntimeError(f"checkpoint metadata mismatch for {dataset_key}")
    rows = payload.get("rows", [])
    completed = validated_completed_seeds(rows, dataset_key, k)
    if completed != {int(seed) for seed in payload.get("completed_seeds", [])}:
        raise RuntimeError(f"checkpoint seed summary mismatch for {dataset_key}")
    return rows


def write_completed_output(path, protocol, dataset_key, k, rows):
    completed = validated_completed_seeds(rows, dataset_key, k)
    expected_rows = len(SEEDS) * len(MODELS) * len(METHOD_KEYS)
    if completed != set(SEEDS) or len(rows) != expected_rows:
        raise RuntimeError(f"refusing incomplete final output for {dataset_key}")
    write_json_atomic(
        path,
        {
            "protocol": protocol,
            "dataset_key": dataset_key,
            "folds": k,
            "rows": rows,
        },
    )


def load_completed_output(path, protocol, dataset_key, k):
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("protocol") != protocol:
        raise RuntimeError(f"completed-output protocol mismatch for {dataset_key}")
    if payload.get("dataset_key") != dataset_key or int(payload.get("folds")) != k:
        raise RuntimeError(f"completed-output metadata mismatch for {dataset_key}")
    rows = payload.get("rows", [])
    completed = validated_completed_seeds(rows, dataset_key, k)
    expected_rows = len(SEEDS) * len(MODELS) * len(METHOD_KEYS)
    if completed != set(SEEDS) or len(rows) != expected_rows:
        raise RuntimeError(f"incomplete final output for {dataset_key}")
    return rows


def run_dataset(
    dataset_key,
    k,
    data_loader,
    functions,
    *,
    protocol,
    checkpoint,
    existing_rows,
    model_runner=call_author_model,
):
    x, y, config = data_loader.load_dataset(dataset_key)
    n_train = config["n_train"]
    n_test = config["n_test"] if config["n_test"] is not None else y.shape[0] - n_train
    alpha = 0.1
    rows = list(existing_rows)
    completed_seeds = validated_completed_seeds(rows, dataset_key, k)
    for seed in SEEDS:
        if seed in completed_seeds:
            print(f"{dataset_key}: resume retaining seed {seed}", flush=True)
            continue
        rng = np.random.default_rng(seed)
        indices = np.arange(y.shape[0])
        train_idx = rng.choice(indices, size=n_train, replace=False)
        test_idx = np.setdiff1d(indices, train_idx)
        if len(test_idx) != n_test:
            raise RuntimeError(f"unexpected test size for {dataset_key}: {len(test_idx)} != {n_test}")
        y_train, x_train = y[train_idx], x[train_idx, :]
        y_test, x_test = y[test_idx], x[test_idx, :]
        for model_name in MODELS:
            result = model_runner(
                model_name, functions, y_train, x_train, x_test,
                k=k, alpha=alpha, config=config, seed=seed,
            )
            for method_name, interval_key in METHOD_KEYS:
                intervals = result[interval_key]
                if len(intervals) != len(y_test):
                    raise RuntimeError(
                        f"unexpected interval count for {dataset_key}, seed {seed}, "
                        f"{model_name}/{method_name}: {len(intervals)} != {len(y_test)}"
                    )
                coverage = float(
                    np.nanmean(
                        [
                            functions.cov_int(interval, truth)
                            for interval, truth in zip(intervals, y_test)
                        ]
                    )
                )
                length = float(
                    np.nanmean([functions.len_int(interval) for interval in intervals])
                )
                rows.append(
                    {
                        "dataset_key": dataset_key,
                        "dataset": config["name"],
                        "folds": k,
                        "seed": seed,
                        "model": model_name,
                        "method": method_name,
                        "coverage": coverage,
                        "length": length,
                    }
                )
        completed_seeds = validated_completed_seeds(rows, dataset_key, k)
        if seed not in completed_seeds:
            raise RuntimeError(f"seed {seed} did not produce a complete checkpoint")
        write_checkpoint(checkpoint, protocol, dataset_key, k, rows)
        print(f"{dataset_key}: completed seed {seed}", flush=True)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--input-check", action="store_true",
                        help="load all bundled author datasets without running estimators")
    args = parser.parse_args()

    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
    source_root = args.source.resolve()
    source_dir = source_root / "e-ccp"
    output_dir = args.output_dir.resolve()
    # The released loader accesses its bundled CSVs through paths relative to
    # e-ccp/.  Keep this wrapper outside the source tree, but reproduce that
    # working-directory contract exactly before invoking author functions.
    os.chdir(source_dir)
    sys.path.insert(0, str(source_dir))
    data_loader = importlib.import_module("data_loader")
    functions = importlib.import_module("eccp_utils")
    protocol = {
        "source": source_descriptor(source_root),
        "datasets": PAPER_DATASETS,
        "seeds": list(SEEDS),
        "models": list(MODELS),
        "methods": [name for name, _ in METHOD_KEYS],
        "alpha": 0.1,
        "grid_points": 300,
        "execution_adapter": EXECUTION_ADAPTER,
    }
    if args.dry_run:
        print(json.dumps(protocol, sort_keys=True))
        return
    if args.input_check:
        inputs = {}
        for dataset_key, folds in PAPER_DATASETS.items():
            x, y, config = data_loader.load_dataset(dataset_key)
            inputs[dataset_key] = {
                "folds": folds,
                "n_features": int(x.shape[1]),
                "n_rows": int(x.shape[0]),
                "n_train": int(config["n_train"]),
            }
        print(json.dumps({"protocol": protocol, "inputs": inputs}, sort_keys=True))
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json_atomic(output_dir / "protocol.json", protocol)
    for dataset_key, k in PAPER_DATASETS.items():
        output = output_dir / f"{dataset_key}.json"
        if output.exists() and not args.force:
            rows = load_completed_output(output, protocol, dataset_key, k)
            print(f"resume: retaining verified {output.name} ({len(rows)} rows)")
            continue
        checkpoint = output_dir / f".{dataset_key}.partial.json"
        if args.force:
            write_checkpoint(checkpoint, protocol, dataset_key, k, [])
            existing_rows = []
        else:
            existing_rows = load_checkpoint(checkpoint, protocol, dataset_key, k)
        if existing_rows:
            print(
                f"resume: {dataset_key} checkpoint has "
                f"{len(validated_completed_seeds(existing_rows, dataset_key, k))} seeds",
                flush=True,
            )
        rows = run_dataset(
            dataset_key,
            k,
            data_loader,
            functions,
            protocol=protocol,
            checkpoint=checkpoint,
            existing_rows=existing_rows,
        )
        completed = validated_completed_seeds(rows, dataset_key, k)
        if completed != set(SEEDS) or len(rows) != len(SEEDS) * len(MODELS) * len(METHOD_KEYS):
            raise RuntimeError(f"full raw-row integrity failed for {dataset_key}")
        write_completed_output(output, protocol, dataset_key, k, rows)
        display_output = args.output_dir / output.name
        print(f"completed {dataset_key}: {len(rows)} raw rows -> {display_output}")


if __name__ == "__main__":
    main()

````


````output
boston: completed seed 45
boston: completed seed 46
boston: completed seed 47
boston: completed seed 48
boston: completed seed 49
boston: completed seed 50
boston: completed seed 51
boston: completed seed 52
boston: completed seed 53
boston: completed seed 54
boston: completed seed 55
boston: completed seed 56
boston: completed seed 57
boston: completed seed 58
boston: completed seed 59
boston: completed seed 60
boston: completed seed 61
boston: completed seed 62
boston: completed seed 63
boston: completed seed 64
boston: completed seed 65
boston: completed seed 66
boston: completed seed 67
boston: completed seed 68
boston: completed seed 69
boston: completed seed 70
boston: completed seed 71
boston: completed seed 72
boston: completed seed 73
boston: completed seed 74
boston: completed seed 75
boston: completed seed 76
boston: completed seed 77
boston: completed seed 78
boston: completed seed 79
boston: completed seed 80
boston: completed seed 81
boston: completed seed 82
boston: completed seed 83
boston: completed seed 84
boston: completed seed 85
boston: completed seed 86
boston: completed seed 87
boston: completed seed 88
boston: completed seed 89
boston: completed seed 90
boston: completed seed 91
boston: completed seed 92
boston: completed seed 93
boston: completed seed 94
boston: completed seed 95
boston: completed seed 96
boston: completed seed 97
boston: completed seed 98
boston: completed seed 99
boston: completed seed 100
boston: completed seed 101
boston: completed seed 102
boston: completed seed 103
boston: completed seed 104
boston: completed seed 105
boston: completed seed 106
boston: completed seed 107
boston: completed seed 108
boston: completed seed 109
boston: completed seed 110
boston: completed seed 111
boston: completed seed 112
boston: completed seed 113
boston: completed seed 114
boston: completed seed 115
boston: completed seed 116
boston: completed seed 117
boston: completed seed 118
boston: completed seed 119
boston: completed seed 120
boston: completed seed 121
boston: completed seed 122
boston: completed seed 123
boston: completed seed 124
boston: completed seed 125
boston: completed seed 126
boston: completed seed 127
boston: completed seed 128
boston: completed seed 129
boston: completed seed 130
boston: completed seed 131
boston: completed seed 132
boston: completed seed 133
boston: completed seed 134
boston: completed seed 135
boston: completed seed 136
boston: completed seed 137
boston: completed seed 138
boston: completed seed 139
boston: completed seed 140
boston: completed seed 141
boston: completed seed 142
boston: completed seed 143
boston: completed seed 144
completed boston: 3900 raw rows -> outputs/raw/author_ccp/boston.json
abalone: completed seed 45
abalone: completed seed 46
abalone: completed seed 47
abalone: completed seed 48
abalone: completed seed 49
abalone: completed seed 50
abalone: completed seed 51
abalone: completed seed 52
abalone: completed seed 53
abalone: completed seed 54
abalone: completed seed 55
abalone: completed seed 56
abalone: completed seed 57
abalone: completed seed 58
abalone: completed seed 59
abalone: completed seed 60
abalone: completed seed 61
abalone: completed seed 62
abalone: completed seed 63
abalone: completed seed 64
abalone: completed seed 65
abalone: completed seed 66
abalone: completed seed 67
abalone: completed seed 68
abalone: completed seed 69
abalone: completed seed 70
abalone: completed seed 71
abalone: completed seed 72
abalone: completed seed 73
abalone: completed seed 74
abalone: completed seed 75
abalone: completed seed 76
abalone: completed seed 77
abalone: completed seed 78
abalone: completed seed 79
abalone: completed seed 80
abalone: completed seed 81
abalone: completed seed 82
abalone: completed seed 83
abalone: completed seed 84
abalone: completed seed 85
abalone: completed seed 86
abalone: completed seed 87
abalone: completed seed 88
abalone: completed seed 89
abalone: completed seed 90
abalone: completed seed 91
abalone: completed seed 92
abalone: completed seed 93
abalone: completed seed 94
abalone: completed seed 95
abalone: completed seed 96
abalone: completed seed 97
abalone: completed seed 98
abalone: completed seed 99
abalone: completed seed 100
abalone: completed seed 101
abalone: completed seed 102
abalone: completed seed 103
abalone: completed seed 104
abalone: completed seed 105
abalone: completed seed 106
abalone: completed seed 107
abalone: completed seed 108
abalone: completed seed 109
abalone: completed seed 110
abalone: completed seed 111
abalone: completed seed 112
abalone: completed seed 113
abalone: completed seed 114
abalone: completed seed 115
abalone: completed seed 116
abalone: completed seed 117
abalone: completed seed 118
abalone: completed seed 119
abalone: completed seed 120
abalone: completed seed 121
abalone: completed seed 122
abalone: completed seed 123
abalone: completed seed 124
abalone: completed seed 125
abalone: completed seed 126
abalone: completed seed 127
abalone: completed seed 128
abalone: completed seed 129
abalone: completed seed 130
abalone: completed seed 131
abalone: completed seed 132
abalone: completed seed 133
abalone: completed seed 134
abalone: completed seed 135
abalone: completed seed 136
abalone: completed seed 137
abalone: completed seed 138
abalone: completed seed 139
abalone: completed seed 140
abalone: completed seed 141
abalone: completed seed 142
abalone: completed seed 143
abalone: completed seed 144
upstream/e-ccp/data_loader.py:32: FutureWarning: Setting an item of incompatible dtype is deprecated and will raise in a future error of pandas. Value '[ 0.81569539  0.81569539  0.81569539 ... -0.43136086 -0.43136086
 -0.43136086]' has dtype incompatible with int64, please explicitly cast to a compatible dtype first.
  Xdf.iloc[:, 0:12] = scaler.fit_transform(Xdf.iloc[:, 0:12])
completed abalone: 3900 raw rows -> outputs/raw/author_ccp/abalone.json
parkinson: completed seed 45
parkinson: completed seed 46
parkinson: completed seed 47
parkinson: completed seed 48
parkinson: completed seed 49
parkinson: completed seed 50
parkinson: completed seed 51
parkinson: completed seed 52
parkinson: completed seed 53
parkinson: completed seed 54
parkinson: completed seed 55
parkinson: completed seed 56
parkinson: completed seed 57
parkinson: completed seed 58
parkinson: completed seed 59
parkinson: completed seed 60
parkinson: completed seed 61
parkinson: completed seed 62
parkinson: completed seed 63
parkinson: completed seed 64
parkinson: completed seed 65
parkinson: completed seed 66
parkinson: completed seed 67
parkinson: completed seed 68
parkinson: completed seed 69
parkinson: completed seed 70
parkinson: completed seed 71
parkinson: completed seed 72
parkinson: completed seed 73
parkinson: completed seed 74
parkinson: completed seed 75
parkinson: completed seed 76
parkinson: completed seed 77
parkinson: completed seed 78
parkinson: completed seed 79
parkinson: completed seed 80
parkinson: completed seed 81
parkinson: completed seed 82
parkinson: completed seed 83
parkinson: completed seed 84
parkinson: completed seed 85
parkinson: completed seed 86
parkinson: completed seed 87
parkinson: completed seed 88
parkinson: completed seed 89
parkinson: completed seed 90
parkinson: completed seed 91
parkinson: completed seed 92
parkinson: completed seed 93
parkinson: completed seed 94
parkinson: completed seed 95
parkinson: completed seed 96
parkinson: completed seed 97
parkinson: completed seed 98
parkinson: completed seed 99
parkinson: completed seed 100
parkinson: completed seed 101
parkinson: completed seed 102
parkinson: completed seed 103
parkinson: completed seed 104
parkinson: completed seed 105
parkinson: completed seed 106
parkinson: completed seed 107
parkinson: completed seed 108
parkinson: completed seed 109
parkinson: completed seed 110
parkinson: completed seed 111
parkinson: completed seed 112
parkinson: completed seed 113
parkinson: completed seed 114
parkinson: completed seed 115
parkinson: completed seed 116
parkinson: completed seed 117
parkinson: completed seed 118
parkinson: completed seed 119
parkinson: completed seed 120
parkinson: completed seed 121
parkinson: completed seed 122
parkinson: completed seed 123
parkinson: completed seed 124
parkinson: completed seed 125
parkinson: completed seed 126
parkinson: completed seed 127
parkinson: completed seed 128
parkinson: completed seed 129
parkinson: completed seed 130
parkinson: completed seed 131
parkinson: completed seed 132
parkinson: completed seed 133
parkinson: completed seed 134
parkinson: completed seed 135
parkinson: completed seed 136
parkinson: completed seed 137
parkinson: completed seed 138
parkinson: completed seed 139
parkinson: completed seed 140
parkinson: completed seed 141
parkinson: completed seed 142
parkinson: completed seed 143
parkinson: completed seed 144
completed parkinson: 3900 raw rows -> outputs/raw/author_ccp/parkinson.json

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_b65e5caaabf2", "created_at": "2026-07-19T18:54:34+00:00", "title": "Independent full CCP raw verification", "command": ["python", "repro/src/verify_ccp_results.py", "--raw-dir", "outputs/raw/author_ccp", "--output", "outputs/claim3_independent.json"], "exit_code": 0, "duration_s": 0.139}
-->
````bash
$ python repro/src/verify_ccp_results.py --raw-dir outputs/raw/author_ccp --output outputs/claim3_independent.json
````

exit 0 · 0.1s


````python title=verify_ccp_results.py
#!/usr/bin/env python3
"""Independent raw-row aggregation for the full author CCP protocol."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


EMPIRICAL_COVERAGE_SHORTFALL_TOLERANCE = 0.02
MIN_SUBSTANTIAL_RELATIVE_REDUCTION = 0.10
P2E_METHOD = "ECCP"
P2E_COVERAGE_METHODS = ("ECCP", "ECCP_exch", "UR-ECCP_exch")
CALIBRATOR_BASELINES = {
    "AoN": "ECCP(ind)",
    "sqrt": "ECCP(sqrt)",
    "log": "ECCP(log)",
    "linear": "ECCP(linear)",
}


def mean_and_sd(values: list[float]) -> tuple[float | None, float | None]:
    if not values or not all(math.isfinite(value) for value in values):
        return None, None
    return statistics.fmean(values), statistics.stdev(values) if len(values) > 1 else 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    protocol = json.loads((args.raw_dir / "protocol.json").read_text(encoding="utf-8"))
    expected_seeds = set(protocol["seeds"])
    expected_models = set(protocol["models"])
    expected_methods = set(protocol["methods"])
    expected_cells = {
        (dataset_key, model, method, seed)
        for dataset_key in protocol["datasets"]
        for model in expected_models
        for method in expected_methods
        for seed in expected_seeds
    }
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    observed_cells: set[tuple[str, str, str, int]] = set()
    duplicate_cells: set[tuple[str, str, str, int]] = set()
    unexpected_rows = 0
    nonfinite_rows = 0
    invalid_metric_rows = 0
    structural_integrity = {dataset_key: True for dataset_key in protocol["datasets"]}
    total_rows = 0
    for dataset_key, folds in protocol["datasets"].items():
        payload = json.loads((args.raw_dir / f"{dataset_key}.json").read_text(encoding="utf-8"))
        if (
            payload.get("protocol") != protocol
            or payload.get("dataset_key") != dataset_key
            or int(payload.get("folds", -1)) != folds
        ):
            structural_integrity[dataset_key] = False
        for row in payload["rows"]:
            total_rows += 1
            row_dataset = str(row["dataset_key"])
            model = str(row["model"])
            method = str(row["method"])
            seed = int(row["seed"])
            cell = (row_dataset, model, method, seed)
            coverage = float(row["coverage"])
            length = float(row["length"])
            finite = math.isfinite(coverage) and math.isfinite(length)
            metric_range_valid = (
                finite and 0.0 <= coverage <= 1.0 and length >= 0.0
            )
            valid_scope = (
                row_dataset == dataset_key
                and model in expected_models
                and method in expected_methods
                and seed in expected_seeds
                and int(row["folds"]) == folds
            )
            if not valid_scope:
                unexpected_rows += 1
                structural_integrity[dataset_key] = False
            if not finite:
                nonfinite_rows += 1
                structural_integrity[dataset_key] = False
            elif not metric_range_valid:
                invalid_metric_rows += 1
                structural_integrity[dataset_key] = False
            if cell in observed_cells:
                duplicate_cells.add(cell)
                structural_integrity[dataset_key] = False
            observed_cells.add(cell)
            if valid_scope:
                grouped[(row_dataset, model, method)].append(row)

    summaries = {}
    integrity = {}
    for dataset_key, folds in protocol["datasets"].items():
        summaries[dataset_key] = {}
        integrity[dataset_key] = structural_integrity[dataset_key]
        for model in expected_models:
            summaries[dataset_key][model] = {}
            for method in expected_methods:
                rows = grouped[(dataset_key, model, method)]
                seed_set = {int(row["seed"]) for row in rows}
                valid = len(rows) == len(expected_seeds) and seed_set == expected_seeds and all(int(row["folds"]) == folds for row in rows)
                integrity[dataset_key] = integrity[dataset_key] and valid
                coverages = [float(row["coverage"]) for row in rows]
                lengths = [float(row["length"]) for row in rows]
                coverage_mean, coverage_sd = mean_and_sd(coverages)
                length_mean, length_sd = mean_and_sd(lengths)
                summaries[dataset_key][model][method] = {
                    "seed_count": len(rows),
                    "coverage_mean": coverage_mean,
                    "coverage_sd": coverage_sd,
                    "length_mean": length_mean,
                    "length_sd": length_sd,
                }

    nominal_coverage = 1.0 - protocol["alpha"]
    eccp_coverage_means = [
        float(methods["ECCP"]["coverage_mean"])
        for models in summaries.values()
        for methods in models.values()
        if "ECCP" in methods and methods["ECCP"]["coverage_mean"] is not None
    ]
    eccp_coverage_pass_count = sum(
        coverage >= nominal_coverage - EMPIRICAL_COVERAGE_SHORTFALL_TOLERANCE
        for coverage in eccp_coverage_means
    )
    p2e_coverage_means = [
        float(methods[method]["coverage_mean"])
        for models in summaries.values()
        for methods in models.values()
        for method in P2E_COVERAGE_METHODS
        if method in methods and methods[method]["coverage_mean"] is not None
    ]
    p2e_coverage_pass_count = sum(
        coverage >= nominal_coverage - EMPIRICAL_COVERAGE_SHORTFALL_TOLERANCE
        for coverage in p2e_coverage_means
    )
    efficiency_comparisons = []
    for dataset_key, models in summaries.items():
        for model, methods in models.items():
            p2e = methods.get(P2E_METHOD, {})
            p2e_value = p2e.get("length_mean")
            if p2e_value is None:
                continue
            p2e_length = float(p2e_value)
            for calibrator, baseline_method in CALIBRATOR_BASELINES.items():
                baseline_value = methods.get(baseline_method, {}).get("length_mean")
                if baseline_value is None:
                    continue
                baseline_length = float(baseline_value)
                relative_reduction = (
                    (baseline_length - p2e_length) / baseline_length
                    if baseline_length > 0.0
                    else None
                )
                is_classical = calibrator != "AoN"
                efficiency_comparisons.append(
                    {
                        "dataset": dataset_key,
                        "model": model,
                        "calibrator": calibrator,
                        "p2e_method": P2E_METHOD,
                        "baseline_method": baseline_method,
                        "p2e_length": p2e_length,
                        "baseline_length": baseline_length,
                        "absolute_reduction": baseline_length - p2e_length,
                        "relative_reduction": relative_reduction,
                        "p2e_not_longer": p2e_length <= baseline_length,
                        "p2e_strictly_shorter": p2e_length < baseline_length,
                        "classical_substantial_gain": (
                            is_classical
                            and relative_reduction is not None
                            and relative_reduction >= MIN_SUBSTANTIAL_RELATIVE_REDUCTION
                        ),
                    }
                )

    aon_comparisons = [
        row for row in efficiency_comparisons if row["calibrator"] == "AoN"
    ]
    classical_comparisons = [
        row for row in efficiency_comparisons if row["calibrator"] != "AoN"
    ]
    finite_reductions = [
        float(row["relative_reduction"])
        for row in efficiency_comparisons
        if row["relative_reduction"] is not None
    ]
    classical_finite_reductions = [
        float(row["relative_reduction"])
        for row in classical_comparisons
        if row["relative_reduction"] is not None
    ]
    not_longer_count = sum(row["p2e_not_longer"] for row in efficiency_comparisons)
    strictly_shorter_count = sum(
        row["p2e_strictly_shorter"] for row in efficiency_comparisons
    )
    aon_strictly_shorter_count = sum(
        row["p2e_strictly_shorter"] for row in aon_comparisons
    )
    classical_substantial_count = sum(
        row["classical_substantial_gain"] for row in classical_comparisons
    )
    result = {
        "protocol": protocol,
        "rows_seen": total_rows,
        "summaries": summaries,
        "calibrator_efficiency_comparisons": efficiency_comparisons,
        "summary": {
            "all_full_seed_cells_present": all(integrity.values()),
            "dataset_integrity": integrity,
            "expected_rows": len(protocol["datasets"]) * len(expected_models) * len(expected_methods) * len(expected_seeds),
            "observed_unique_cells": len(observed_cells),
            "expected_unique_cells": len(expected_cells),
            "duplicate_cell_count": len(duplicate_cells),
            "unexpected_row_count": unexpected_rows,
            "nonfinite_row_count": nonfinite_rows,
            "invalid_metric_row_count": invalid_metric_rows,
            "exact_cell_set": observed_cells == expected_cells,
            "eccp_empirical_coverage_cell_count": len(eccp_coverage_means),
            "eccp_empirical_coverage_pass_count": eccp_coverage_pass_count,
            "all_eccp_empirical_coverage_within_tolerance": (
                bool(eccp_coverage_means)
                and eccp_coverage_pass_count == len(eccp_coverage_means)
            ),
            "empirical_coverage_shortfall_tolerance": EMPIRICAL_COVERAGE_SHORTFALL_TOLERANCE,
            "minimum_eccp_empirical_coverage": (
                min(eccp_coverage_means) if eccp_coverage_means else None
            ),
            "p2e_empirical_coverage_cell_count": len(p2e_coverage_means),
            "p2e_empirical_coverage_pass_count": p2e_coverage_pass_count,
            "all_p2e_empirical_coverage_within_tolerance": (
                bool(p2e_coverage_means)
                and p2e_coverage_pass_count == len(p2e_coverage_means)
            ),
            "minimum_p2e_empirical_coverage": (
                min(p2e_coverage_means) if p2e_coverage_means else None
            ),
            "nominal_coverage": nominal_coverage,
            "calibrator_efficiency_comparison_count": len(efficiency_comparisons),
            "p2e_not_longer_count": not_longer_count,
            "p2e_strictly_shorter_count": strictly_shorter_count,
            "all_p2e_not_longer_than_existing_calibrators": (
                bool(efficiency_comparisons)
                and not_longer_count == len(efficiency_comparisons)
            ),
            "aon_comparison_count": len(aon_comparisons),
            "aon_strictly_shorter_count": aon_strictly_shorter_count,
            "all_p2e_strictly_shorter_than_aon": (
                bool(aon_comparisons)
                and aon_strictly_shorter_count == len(aon_comparisons)
            ),
            "classical_comparison_count": len(classical_comparisons),
            "classical_substantial_gain_count": classical_substantial_count,
            "all_classical_efficiency_gains_substantial": (
                bool(classical_comparisons)
                and classical_substantial_count == len(classical_comparisons)
            ),
            "minimum_substantial_relative_reduction": MIN_SUBSTANTIAL_RELATIVE_REDUCTION,
            "minimum_observed_relative_reduction": (
                min(finite_reductions) if finite_reductions else None
            ),
            "minimum_classical_relative_reduction": (
                min(classical_finite_reductions)
                if classical_finite_reductions
                else None
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()

````


````output
{"all_classical_efficiency_gains_substantial": true, "all_eccp_empirical_coverage_within_tolerance": true, "all_full_seed_cells_present": true, "all_p2e_empirical_coverage_within_tolerance": true, "all_p2e_not_longer_than_existing_calibrators": true, "all_p2e_strictly_shorter_than_aon": true, "aon_comparison_count": 9, "aon_strictly_shorter_count": 9, "calibrator_efficiency_comparison_count": 36, "classical_comparison_count": 27, "classical_substantial_gain_count": 27, "dataset_integrity": {"abalone": true, "boston": true, "parkinson": true}, "duplicate_cell_count": 0, "eccp_empirical_coverage_cell_count": 9, "eccp_empirical_coverage_pass_count": 9, "empirical_coverage_shortfall_tolerance": 0.02, "exact_cell_set": true, "expected_rows": 11700, "expected_unique_cells": 11700, "invalid_metric_row_count": 0, "minimum_classical_relative_reduction": 0.23664123574004337, "minimum_eccp_empirical_coverage": 0.8902991304347826, "minimum_observed_relative_reduction": 0.0017866878285227466, "minimum_p2e_empirical_coverage": 0.8902991304347826, "minimum_substantial_relative_reduction": 0.1, "nominal_coverage": 0.9, "nonfinite_row_count": 0, "observed_unique_cells": 11700, "p2e_empirical_coverage_cell_count": 27, "p2e_empirical_coverage_pass_count": 27, "p2e_not_longer_count": 36, "p2e_strictly_shorter_count": 36, "unexpected_row_count": 0}

````


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_c4c0578d3fce", "created_at": "2026-07-19T18:54:47+00:00", "title": "Claim 3 verdict"}
-->
Claim 3 is verified in 18 independent theorem-domain cases. The normalized sigmoid has expectation one, finite log-values (strict positivity), a strictly negative analytic derivative (smoothness and invertibility), and a closed-form inverse that round-trips numerically. Pointwise P2E values dominate AoN, so every weighted or unweighted aggregate P2E e-value is at least the corresponding AoN aggregate and the P2E prediction set is a subset. The full released CCP results additionally show strict empirical improvement over AoN in 9/9 matched dataset/model cells.
