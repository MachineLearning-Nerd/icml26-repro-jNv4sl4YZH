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
