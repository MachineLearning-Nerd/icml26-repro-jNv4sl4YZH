#!/usr/bin/env python3
"""Independent, fail-closed release checker for Claim 1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def check(cleanroom: dict[str, object], source: dict[str, object]) -> dict[str, object]:
    failures: list[str] = []
    clean_summary = cleanroom.get("summary", {})
    source_summary = source.get("summary", {})

    required_clean = (
        "all_set_identities_pass",
        "all_threshold_identities_pass",
        "all_exact_e_expectations_pass",
        "all_theorem_domain_verified",
        "all_domain_controls_rejected",
        "all_classic_controls_inflate_sets",
    )
    for key in required_clean:
        if clean_summary.get(key) is not True:
            failures.append(f"clean-room condition failed: {key}")
    if clean_summary.get("case_count") != 18:
        failures.append("clean-room grid is not the exact 18-cell contract")
    if clean_summary.get("domain_control_count") != 5:
        failures.append("excluded-domain negative controls are incomplete")
    if len(cleanroom.get("cases", [])) != 18:
        failures.append("clean-room raw case rows are incomplete")
    if any(row.get("set_mismatches") != 0 for row in cleanroom.get("cases", [])):
        failures.append("clean-room membership mismatch detected")

    required_source = (
        "all_source_membership_pass",
        "all_cleanroom_membership_pass",
        "all_source_expectations_pass",
        "all_theorem_domain_verified",
    )
    for key in required_source:
        if source_summary.get(key) is not True:
            failures.append(f"source cross-check condition failed: {key}")
    if source_summary.get("rows") != 18 or len(source.get("rows", [])) != 18:
        failures.append("author-source cross-check is not 18 cells")
    if any(row.get("source_set_mismatches") != 0 for row in source.get("rows", [])):
        failures.append("author-source membership mismatch detected")

    maximum_expectation_error = max(
        abs(float(row["exact_e_expectation"]) - 1.0)
        for row in cleanroom.get("cases", [])
    )
    result = {
        "status": "PASS" if not failures else "FAIL",
        "verdict_checked": "VERIFIED",
        "failures": failures,
        "cleanroom_cells_checked": len(cleanroom.get("cases", [])),
        "source_cells_checked": len(source.get("rows", [])),
        "maximum_expectation_abs_error": maximum_expectation_error,
        "membership_mismatches": sum(
            int(row["set_mismatches"]) for row in cleanroom.get("cases", [])
        ),
        "negative_controls_checked": (
            int(clean_summary.get("domain_control_count", 0))
            + int(clean_summary.get("classic_control_case_count", 0))
        ),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cleanroom", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = check(
        json.loads(args.cleanroom.read_text(encoding="utf-8")),
        json.loads(args.source.read_text(encoding="utf-8")),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))
    if result["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
