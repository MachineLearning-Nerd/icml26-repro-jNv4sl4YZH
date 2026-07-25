#!/usr/bin/env python3
"""Verify Claim 6 directly on both full released empirical protocols."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


def build(ca: dict[str, object], ccp: dict[str, object], runtime_seconds: float) -> dict[str, object]:
    ca_summary = ca["summary"]
    ccp_summary = ccp["summary"]
    ca_comparisons = ca["efficiency_comparisons"]
    ccp_comparisons = ccp["calibrator_efficiency_comparisons"]

    ca_pass = all(
        (
            ca_summary["exact_cell_set"],
            ca_summary["expected_rows"] == 1920,
            ca_summary["comparison_count"] == 24,
            ca_summary["p2e_shorter_count"] == 24,
            ca_summary["all_substantial_efficiency_gains"],
            ca_summary["p2e_empirical_coverage_pass_count"] == 8,
        )
    )
    ccp_pass = all(
        (
            ccp_summary["exact_cell_set"],
            ccp_summary["expected_rows"] == 11700,
            ccp_summary["calibrator_efficiency_comparison_count"] == 36,
            ccp_summary["p2e_strictly_shorter_count"] == 36,
            ccp_summary["aon_strictly_shorter_count"] == 9,
            ccp_summary["classical_substantial_gain_count"] == 27,
            ccp_summary["eccp_empirical_coverage_pass_count"] == 9,
        )
    )
    control = {
        "reversed_efficiency_rule_would_fail": any(
            float(row["p2e_length"]) < float(row["baseline_length"])
            for row in ccp_comparisons
        ),
        "coverage_tolerance_cannot_be_vacuous": (
            float(ccp_summary["empirical_coverage_shortfall_tolerance"]) < 0.1
            and float(ca_summary["empirical_coverage_shortfall_tolerance"]) < 0.1
        ),
        "missing_cell_contract_is_fail_closed": (
            ca_summary["observed_unique_cells"] == ca_summary["expected_unique_cells"]
            and ccp_summary["observed_unique_cells"] == ccp_summary["expected_unique_cells"]
        ),
    }
    controls_pass = all(control.values())
    return {
        "verdict": "VERIFIED",
        "claim": (
            "At the released Section 5 protocols, P2E produces smaller aggregation "
            "prediction sets than the named p-to-e baselines while empirical coverage "
            "remains within the predeclared absolute shortfall tolerance."
        ),
        "paper": {
            "url": "https://export.arxiv.org/e-print/2606.03600v1",
            "archive_sha256": "f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db",
            "main_tex_sha256": "49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857",
            "anchors": {
                "section": "main.tex Section Experiments",
                "ca_tables": "main.tex tables covering ECA/WECA/UR-WECA",
                "ccp_tables": "main.tex tables covering CCP/ECCP",
            },
        },
        "ca_full_protocol": {
            "raw_rows": ca_summary["expected_rows"],
            "tasks": ca["protocol"]["tasks"],
            "seed_count": len(ca["protocol"]["seeds"]),
            "comparison_count": len(ca_comparisons),
            "p2e_shorter_count": sum(row["p2e_is_shorter"] for row in ca_comparisons),
            "minimum_relative_reduction": min(
                float(row["relative_reduction"]) for row in ca_comparisons
            ),
            "coverage_cells_passed": ca_summary["p2e_empirical_coverage_pass_count"],
            "coverage_cells": ca_summary["p2e_empirical_coverage_cell_count"],
            "minimum_p2e_coverage": ca_summary["minimum_p2e_empirical_coverage"],
            "nominal_coverage": ca_summary["nominal_coverage"],
            "pass": ca_pass,
        },
        "eccp_full_protocol": {
            "raw_rows": ccp_summary["expected_rows"],
            "datasets": ccp["protocol"]["datasets"],
            "seed_count": len(ccp["protocol"]["seeds"]),
            "comparison_count": len(ccp_comparisons),
            "p2e_strictly_shorter_count": sum(
                row["p2e_strictly_shorter"] for row in ccp_comparisons
            ),
            "aon_comparisons": ccp_summary["aon_comparison_count"],
            "minimum_aon_relative_reduction": min(
                float(row["relative_reduction"])
                for row in ccp_comparisons
                if row["calibrator"] == "AoN"
            ),
            "minimum_classical_relative_reduction": ccp_summary[
                "minimum_classical_relative_reduction"
            ],
            "coverage_cells_passed": ccp_summary["eccp_empirical_coverage_pass_count"],
            "coverage_cells": ccp_summary["eccp_empirical_coverage_cell_count"],
            "minimum_p2e_coverage": ccp_summary["minimum_p2e_empirical_coverage"],
            "nominal_coverage": ccp_summary["nominal_coverage"],
            "pass": ccp_pass,
        },
        "negative_controls": {**control, "all_pass": controls_pass},
        "limitations": [
            "Coverage means are empirical sanity checks; Claims 4 and 5 contain the finite-sample validity certificates.",
            "The CA and CCP baselines are reported separately because their nominal levels and protocols differ.",
            "The paper/released-code F1/F2/F3 labeling drift is source-hash-bound and disclosed; formula-faithful log, square-root, and linear comparisons are used.",
        ],
        "all_claim_components_pass": ca_pass and ccp_pass and controls_pass,
        "runtime_seconds": runtime_seconds,
        "estimated_required_cores": 1,
        "actual_process_parallelism": 1,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ca", type=Path, required=True)
    parser.add_argument("--ccp", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    result = build(
        json.loads(args.ca.read_text(encoding="utf-8")),
        json.loads(args.ccp.read_text(encoding="utf-8")),
        0.0,
    )
    result["runtime_seconds"] = time.monotonic() - started
    if not result["all_claim_components_pass"]:
        raise SystemExit("Claim 6 evidence contract failed")
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized, encoding="utf-8")
    (args.artifact_dir / "raw_full_protocol_summary.json").write_text(
        serialized, encoding="utf-8"
    )
    (args.artifact_dir / "negative_control_output.json").write_text(
        json.dumps(result["negative_controls"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "ca_rows": result["ca_full_protocol"]["raw_rows"],
                "ca_comparisons": result["ca_full_protocol"]["comparison_count"],
                "eccp_rows": result["eccp_full_protocol"]["raw_rows"],
                "eccp_comparisons": result["eccp_full_protocol"]["comparison_count"],
                "controls_pass": result["negative_controls"]["all_pass"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
