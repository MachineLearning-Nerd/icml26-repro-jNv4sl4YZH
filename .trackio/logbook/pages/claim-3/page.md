# Claim 3


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_6c5d46256087", "created_at": "2026-07-18T12:24:40+00:00", "title": "Full protocol queued"}
-->
The full cross-conformal protocol will run the three bundled paper datasets with 100 seeds each and the paper fold counts: Boston `K=15`, Abalone `K=15`, Parkinson `K=20`. The source estimators remain unmodified; the wrapper only supplies the paper configuration and persists raw rows for independent aggregation. Results are pending execution.


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
A clean-room enumeration of six finite rank/fold configurations confirms that arithmetic e-merging retains exact mean one and that the Markov prediction-set event reaches at least `1-alpha` in every case. A deliberately invalid 2x scaling falls below the required coverage in 2/6 configurations (for example, `.8264 < .9` at `n=10`, two folds), while being accidentally conservative in the other configurations. This is retained as a control result, not generalized. The full 100-seed source CCP protocol is still required and remains pending.
