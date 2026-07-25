#!/usr/bin/env python3
"""Independent, fail-closed checker for Claim 6 release evidence."""

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
    failures: list[str] = []
    if evidence.get("verdict") != "VERIFIED":
        failures.append("verdict drift")
    ca = evidence.get("ca_full_protocol", {})
    if (ca.get("raw_rows"), ca.get("comparison_count"), ca.get("p2e_shorter_count")) != (
        1920,
        24,
        24,
    ):
        failures.append("CA full-protocol count or efficiency contract failed")
    if (ca.get("coverage_cells_passed"), ca.get("coverage_cells")) != (8, 8):
        failures.append("CA coverage-cell contract failed")
    eccp = evidence.get("eccp_full_protocol", {})
    if (
        eccp.get("raw_rows"),
        eccp.get("comparison_count"),
        eccp.get("p2e_strictly_shorter_count"),
    ) != (11700, 36, 36):
        failures.append("ECCP full-protocol count or efficiency contract failed")
    if (eccp.get("coverage_cells_passed"), eccp.get("coverage_cells")) != (9, 9):
        failures.append("ECCP coverage-cell contract failed")
    if eccp.get("aon_comparisons") != 9:
        failures.append("AoN comparison contract failed")
    if evidence.get("negative_controls", {}).get("all_pass") is not True:
        failures.append("negative controls failed")
    result = {
        "status": "PASS" if not failures else "FAIL",
        "verdict_checked": "VERIFIED",
        "failures": failures,
        "ca_rows_checked": ca.get("raw_rows"),
        "ca_comparisons_checked": ca.get("comparison_count"),
        "eccp_rows_checked": eccp.get("raw_rows"),
        "eccp_comparisons_checked": eccp.get("comparison_count"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
