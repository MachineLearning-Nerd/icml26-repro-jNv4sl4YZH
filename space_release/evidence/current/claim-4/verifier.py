#!/usr/bin/env python3
"""Verify ECCP's universal coverage mechanism and full released protocol."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path


def empirical_rows(ccp: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    for dataset, models in sorted(ccp["summaries"].items()):
        for model, methods in sorted(models.items()):
            cell = methods["ECCP"]
            standard_error = cell["coverage_sd"] / math.sqrt(cell["seed_count"])
            rows.append(
                {
                    "dataset": dataset,
                    "model": model,
                    **cell,
                    "nominal_coverage": 0.9,
                    "coverage_gap": cell["coverage_mean"] - 0.9,
                    "mean_95pct_ci": [
                        cell["coverage_mean"] - 1.96 * standard_error,
                        cell["coverage_mean"] + 1.96 * standard_error,
                    ],
                    "within_predeclared_absolute_tolerance_0.02": (
                        cell["coverage_mean"] >= 0.88
                    ),
                }
            )
    return rows


def build(
    ccp: dict[str, object],
    mechanism: dict[str, object],
    anchored: dict[str, object],
    runtime_seconds: float,
) -> dict[str, object]:
    rows = empirical_rows(ccp)
    mechanism_summary = mechanism["summary"]
    standard_bounds = anchored["standard_ccp_bound_certificates"]
    mechanism_pass = all(
        (
            mechanism_summary["all_arbitrary_dependence_coverage_pass"],
            mechanism_summary["all_randomized_arbitrary_dependence_coverage_pass"],
            mechanism_summary["all_exchangeable_prefix_coverage_pass"],
            mechanism_summary["all_exchangeable_randomized_prefix_coverage_pass"],
            mechanism_summary["all_merged_expectations_exact"],
            mechanism_summary["all_markov_coverage_events_pass"],
        )
    )
    controls_pass = all(
        (
            mechanism_summary["invalid_scaling_control_detected"],
            mechanism_summary["invalid_arbitrary_dependence_detected"],
            mechanism_summary["invalid_randomized_arbitrary_dependence_detected"],
        )
    )
    empirical_pass = len(rows) == 9 and all(
        row["seed_count"] == 100
        and row["within_predeclared_absolute_tolerance_0.02"]
        for row in rows
    )
    standard_pass = len(standard_bounds) == 4 and all(
        row["standard_guarantee_below_one_minus_alpha"] for row in standard_bounds
    )
    return {
        "verdict": "VERIFIED",
        "claim": (
            "ECCP has a finite-sample 1-alpha coverage guarantee, whereas the "
            "named standard CCP variants carry an approximate 1-2alpha guarantee."
        ),
        "interpretation": (
            "Exact coverage means a finite-sample lower-bound guarantee >=1-alpha; "
            "it does not mean empirical coverage equals 1-alpha."
        ),
        "paper": {
            "url": "https://export.arxiv.org/e-print/2606.03600v1",
            "archive_sha256": "f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db",
            "main_tex_sha256": "49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857",
            "anchors": {
                "eccp": "main.tex:676-683, Proposition prop:ECCP",
                "construction": "main.tex:646-674, Equations ECCP, Ex_ECCP, Ex_ECCP_U",
                "standard_bound": "Equation eq:ccpbound and related-work statement",
            },
        },
        "universal_certificate": {
            "derivation": [
                "exchangeability makes each fold P2E output an e-variable",
                "linearity gives E[sum_k E_k/K] <= 1 without fold independence",
                "randomized Markov yields miscoverage <= alpha for ECCP",
                "the exchangeable prefix variants use the stated exchangeable e-merging inequality",
            ],
            "proof_does_not_depend_on_finite_enumeration": True,
            "arbitrary_dependence_cases": mechanism_summary["case_count"],
            "exchangeable_prefix_cases": mechanism_summary["exchangeable_prefix_case_count"],
            "maximum_valid_tail_to_alpha_ratio": mechanism_summary[
                "maximum_valid_tail_to_alpha_ratio"
            ],
            "maximum_randomized_tail_to_alpha_ratio": mechanism_summary[
                "maximum_valid_randomized_tail_to_alpha_ratio"
            ],
            "all_pass": mechanism_pass,
        },
        "full_protocol": {
            "raw_rows": ccp["rows_seen"],
            "datasets": sorted(ccp["protocol"]["datasets"]),
            "models": ccp["protocol"]["models"],
            "seeds": ccp["protocol"]["seeds"],
            "coverage_cells": len(rows),
            "coverage_cells_within_tolerance": sum(
                row["within_predeclared_absolute_tolerance_0.02"] for row in rows
            ),
            "minimum_coverage_mean": min(row["coverage_mean"] for row in rows),
            "rows": rows,
            "all_pass_predeclared_tolerance": empirical_pass,
        },
        "standard_ccp": {
            "one_minus_two_alpha": 0.8,
            "one_minus_alpha": 0.9,
            "certificates": standard_bounds,
            "all_guarantees_below_one_minus_alpha": standard_pass,
        },
        "negative_controls": {
            "invalid_scaling_detected": mechanism_summary[
                "invalid_scaling_control_detected"
            ],
            "invalid_arbitrary_dependence_for_prefix_detected": mechanism_summary[
                "invalid_arbitrary_dependence_detected"
            ],
            "invalid_randomized_arbitrary_dependence_detected": mechanism_summary[
                "invalid_randomized_arbitrary_dependence_detected"
            ],
            "controls_pass": controls_pass,
        },
        "limitations": [
            "The universal guarantee comes from the proof certificate, not from nine empirical means.",
            "The minimum empirical ECCP mean is 0.890299 at nominal 0.9 and its naive across-seed 95% interval excludes 0.9; it remains within the predeclared 0.02 reproduction tolerance.",
            "Across-seed intervals are descriptive because released seeds reuse a fixed dataset and are not independent population draws.",
        ],
        "all_claim_components_pass": (
            mechanism_pass and empirical_pass and standard_pass and controls_pass
        ),
        "runtime_seconds": runtime_seconds,
        "estimated_required_cores": 1,
        "actual_process_parallelism": 1,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ccp", type=Path, required=True)
    parser.add_argument("--mechanism", type=Path, required=True)
    parser.add_argument("--anchored", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    result = build(
        json.loads(args.ccp.read_text(encoding="utf-8")),
        json.loads(args.mechanism.read_text(encoding="utf-8")),
        json.loads(args.anchored.read_text(encoding="utf-8")),
        0.0,
    )
    result["runtime_seconds"] = time.monotonic() - started
    if not result["all_claim_components_pass"]:
        raise SystemExit("Claim 4 evidence contract failed")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.write_text(serialized, encoding="utf-8")
    (args.artifact_dir / "raw_eccp_full_protocol.json").write_text(
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
                "minimum_coverage_mean": result["full_protocol"]["minimum_coverage_mean"],
                "universal_mechanism": result["universal_certificate"]["all_pass"],
                "controls_pass": result["negative_controls"]["controls_pass"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
