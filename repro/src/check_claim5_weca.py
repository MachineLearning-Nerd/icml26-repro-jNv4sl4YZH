#!/usr/bin/env python3
"""Independent fail-closed checker for Claim 5 WECA evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evidence = json.loads(args.input.read_text(encoding="utf-8"))
    failures = []
    if evidence.get("verdict") != "VERIFIED":
        failures.append("verdict drift")
    proof = evidence.get("conditional_proof_certificate", {})
    if proof.get("universal_and_not_inferred_from_six_mutations") is not True:
        failures.append("finite mutation audit substituted for theorem")
    audit = evidence.get("released_source_audit", {})
    if audit.get("mutation_case_count") != 6:
        failures.append("source-bound mutation audit is incomplete")
    if audit.get("all_data_dependence_requirements_pass") is not True:
        failures.append("data-dependence assumptions failed")
    full = evidence.get("full_protocol", {})
    if full.get("raw_rows") != 1920:
        failures.append("full CA protocol is not 1,920 rows")
    if len(full.get("seeds", [])) != 20 or len(full.get("tasks", [])) != 4:
        failures.append("full task/seed protocol absent")
    if full.get("coverage_cells") != 8 or full.get("coverage_cells_within_tolerance") != 8:
        failures.append("not all 8 P2E WECA coverage cells passed")
    if evidence.get("negative_controls", {}).get("all_pass") is not True:
        failures.append("adaptive-weight negative controls failed")
    result = {
        "status": "PASS" if not failures else "FAIL",
        "verdict_checked": "VERIFIED",
        "failures": failures,
        "full_protocol_rows_checked": full.get("raw_rows"),
        "coverage_cells_checked": full.get("coverage_cells"),
        "mutation_cases_checked": audit.get("mutation_case_count"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
