#!/usr/bin/env python3
"""Independent fail-closed checker for Claim 4 ECCP evidence."""

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
    universal = evidence.get("universal_certificate", {})
    if universal.get("proof_does_not_depend_on_finite_enumeration") is not True:
        failures.append("finite enumeration was substituted for universal proof")
    if universal.get("all_pass") is not True:
        failures.append("universal mechanism failed")
    full = evidence.get("full_protocol", {})
    if full.get("raw_rows") != 11700:
        failures.append("raw protocol is not 11,700 rows")
    if full.get("coverage_cells") != 9 or full.get("coverage_cells_within_tolerance") != 9:
        failures.append("not all 9 ECCP coverage cells passed")
    if len(full.get("seeds", [])) != 100:
        failures.append("full 100-seed protocol absent")
    if evidence.get("standard_ccp", {}).get(
        "all_guarantees_below_one_minus_alpha"
    ) is not True:
        failures.append("standard CCP comparison failed")
    if evidence.get("negative_controls", {}).get("controls_pass") is not True:
        failures.append("negative controls failed")
    if not evidence.get("interpretation", "").startswith(
        "Exact coverage means a finite-sample lower-bound"
    ):
        failures.append("exact coverage was misinterpreted as equality")
    result = {
        "status": "PASS" if not failures else "FAIL",
        "verdict_checked": "VERIFIED",
        "failures": failures,
        "full_protocol_rows_checked": full.get("raw_rows"),
        "coverage_cells_checked": full.get("coverage_cells"),
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
