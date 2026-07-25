#!/usr/bin/env python3
"""Independent fail-closed checker for dedicated Claim 3 evidence."""

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
    analytic = evidence.get("analytic_certificate", {})
    cases = analytic.get("cases", [])
    if analytic.get("all_pass") is not True or len(cases) != 18:
        failures.append("analytic certificate is incomplete")
    for row in cases:
        if row.get("expectation_abs_error", 1.0) >= 1e-11:
            failures.append(f"expectation error: {row.get('n_calibration')}")
        if row.get("all_derivatives_strictly_negative") is not True:
            failures.append(f"derivative failure: {row.get('n_calibration')}")
        if row.get("maximum_inverse_roundtrip_error", 1.0) >= 1e-10:
            failures.append(f"inverse error: {row.get('n_calibration')}")
        if row.get("all_values_strictly_positive") is not True:
            failures.append(f"positivity failure: {row.get('n_calibration')}")
    fullscale = evidence.get("fullscale_direct_AoN", {})
    if fullscale.get("protocol_rows") != 11700:
        failures.append("full-scale raw-row count is not 11,700")
    if fullscale.get("comparison_count") != 9:
        failures.append("AoN comparison count is not 9")
    if fullscale.get("strictly_shorter_count") != 9:
        failures.append("P2E was not strictly shorter in all 9 AoN comparisons")
    if evidence.get("negative_controls_pass") is not True:
        failures.append("negative controls failed")
    scope = evidence.get("scope_calibration", {})
    if scope.get("prediction_set_relation_is_non_strict_subset_in_theorem") is not True:
        failures.append("set inclusion scope is overstated")

    result = {
        "status": "PASS" if not failures else "FAIL",
        "verdict_checked": "VERIFIED",
        "failures": failures,
        "analytic_cases_checked": len(cases),
        "fullscale_AoN_comparisons_checked": fullscale.get("comparison_count"),
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
