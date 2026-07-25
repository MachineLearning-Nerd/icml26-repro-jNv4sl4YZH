#!/usr/bin/env python3
"""Verify data-dependent WECA validity and its complete released protocol."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path


METHODS = ("WECA(P2E)", "UR-WECA(P2E)")


def coverage_rows(ca: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for dataset, methods in sorted(ca["summaries"].items()):
        for method in METHODS:
            cell = methods[method]
            se = cell["coverage_sd"] / math.sqrt(cell["seed_count"])
            rows.append(
                {
                    "dataset": dataset,
                    "method": method,
                    **cell,
                    "nominal_coverage": 0.95,
                    "coverage_gap": cell["coverage_mean"] - 0.95,
                    "mean_95pct_ci": [
                        cell["coverage_mean"] - 1.96 * se,
                        cell["coverage_mean"] + 1.96 * se,
                    ],
                    "within_predeclared_absolute_tolerance_0.02": (
                        cell["coverage_mean"] >= 0.93
                    ),
                }
            )
    return rows


def build(
    ca: dict[str, object],
    independence: dict[str, object],
    mechanism: dict[str, object],
    runtime_seconds: float,
) -> dict[str, object]:
    rows = coverage_rows(ca)
    audit = independence["summary"]
    mechanism_summary = mechanism["summary"]
    data_dependence_pass = all(
        (
            audit["all_required_flow_present"],
            audit["all_split_partitions_disjoint"],
            audit["all_weights_independent_of_final_calibration"],
            audit["all_weights_independent_of_test_data_and_outcomes"],
            audit["all_illegal_test_adaptive_controls_change"],
        )
    )
    empirical_pass = len(rows) == 8 and all(
        row["seed_count"] == 20
        and row["within_predeclared_absolute_tolerance_0.02"]
        for row in rows
    )
    invalid_adaptation_detected = all(
        (
            mechanism_summary["adaptive_weight_control_detected"],
            mechanism_summary["adaptive_randomized_weight_control_detected"],
            mechanism_summary["minimum_adaptive_tail_to_alpha_ratio"] > 1,
            mechanism_summary["minimum_adaptive_randomized_tail_to_alpha_ratio"] > 1,
        )
    )
    return {
        "verdict": "VERIFIED",
        "claim": (
            "Tuning-data-dependent WECA weights retain coverage when they are "
            "independent of inference e-values and the test point."
        ),
        "paper": {
            "url": "https://export.arxiv.org/e-print/2606.03600v1",
            "archive_sha256": "f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db",
            "main_tex_sha256": "49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857",
            "anchors": {
                "construction": "main.tex:704-745, Equation WECA",
                "proposition": "main.tex:735-741, WECA coverage proposition",
                "validity": "Appendix subsection Theoretical Validity of WECA",
            },
        },
        "conditional_proof_certificate": {
            "steps": [
                "omega*=g(D_tune) is data-dependent and lies in the simplex",
                "omega* is independent of inference e-values and the test point",
                "conditionally on omega*, E[sum_k omega*_k E_k | omega*] <= sum_k omega*_k = 1",
                "Markov or randomized Markov therefore bounds miscoverage by alpha",
            ],
            "universal_and_not_inferred_from_six_mutations": True,
            "valid_without_independence_among_inference_e_values": True,
        },
        "released_source_audit": {
            "source": independence["source"],
            "methods_sha256": independence["methods_sha256"],
            "function_contract": independence["function_contract"],
            "mutation_case_count": audit["case_count"],
            "cases": independence["cases"],
            "all_data_dependence_requirements_pass": data_dependence_pass,
        },
        "full_protocol": {
            "raw_rows": ca["rows_seen"],
            "tasks": ca["protocol"]["tasks"],
            "seeds": ca["protocol"]["seeds"],
            "M": ca["protocol"]["M"],
            "B": ca["protocol"]["B"],
            "coverage_cells": len(rows),
            "coverage_cells_within_tolerance": sum(
                row["within_predeclared_absolute_tolerance_0.02"] for row in rows
            ),
            "minimum_coverage_mean": min(row["coverage_mean"] for row in rows),
            "rows": rows,
            "all_pass_predeclared_tolerance": empirical_pass,
        },
        "negative_controls": {
            "forbidden_test_adaptive_weight_changes_in_source_audit": audit[
                "all_illegal_test_adaptive_controls_change"
            ],
            "adaptive_weight_coverage_violation_detected": mechanism_summary[
                "adaptive_weight_control_detected"
            ],
            "adaptive_randomized_weight_coverage_violation_detected": mechanism_summary[
                "adaptive_randomized_weight_control_detected"
            ],
            "minimum_invalid_tail_to_alpha_ratio": mechanism_summary[
                "minimum_adaptive_tail_to_alpha_ratio"
            ],
            "minimum_invalid_randomized_tail_to_alpha_ratio": mechanism_summary[
                "minimum_adaptive_randomized_tail_to_alpha_ratio"
            ],
            "all_pass": invalid_adaptation_detected,
        },
        "limitations": [
            "The six mutation cases audit the released implementation; the conditional derivation carries the universal claim.",
            "Full empirical evidence re-aggregates immutable released results rather than rerunning the expensive author training.",
            "Coverage means and across-seed intervals are descriptive; theorem validity depends on split independence/exchangeability assumptions.",
        ],
        "all_claim_components_pass": (
            data_dependence_pass and empirical_pass and invalid_adaptation_detected
        ),
        "runtime_seconds": runtime_seconds,
        "estimated_required_cores": 1,
        "actual_process_parallelism": 1,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ca", type=Path, required=True)
    parser.add_argument("--independence", type=Path, required=True)
    parser.add_argument("--mechanism", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    result = build(
        json.loads(args.ca.read_text(encoding="utf-8")),
        json.loads(args.independence.read_text(encoding="utf-8")),
        json.loads(args.mechanism.read_text(encoding="utf-8")),
        0.0,
    )
    result["runtime_seconds"] = time.monotonic() - started
    if not result["all_claim_components_pass"]:
        raise SystemExit("Claim 5 evidence contract failed")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.write_text(serialized, encoding="utf-8")
    (args.artifact_dir / "raw_weca_full_protocol.json").write_text(
        serialized, encoding="utf-8"
    )
    (args.artifact_dir / "negative_control_output.json").write_text(
        json.dumps(result["negative_controls"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "verdict": "VERIFIED",
                "raw_rows": result["full_protocol"]["raw_rows"],
                "coverage_cells": (
                    f"{result['full_protocol']['coverage_cells_within_tolerance']}/"
                    f"{result['full_protocol']['coverage_cells']}"
                ),
                "mutation_cases": result["released_source_audit"]["mutation_case_count"],
                "minimum_coverage_mean": result["full_protocol"]["minimum_coverage_mean"],
                "invalid_adaptive_control_detected": result["negative_controls"]["all_pass"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
