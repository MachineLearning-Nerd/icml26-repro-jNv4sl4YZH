#!/usr/bin/env python3
"""Independent fail-closed checker for the judge-prompt visibility audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


EXPECTED_CLAIMS = {f"EXACT_CLAIM_{index}_EVIDENCE" for index in range(1, 7)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    failures: list[str] = []
    if data.get("status") != "PASS":
        failures.append("upstream audit status is not PASS")
    if data.get("judge_max_logbook_characters") != 120_000:
        failures.append("judge prompt cap changed")
    if set(data.get("claim_markers", [])) != EXPECTED_CLAIMS:
        failures.append("claim marker set is incomplete")
    historical = data.get("historical_negative_control", {})
    if not historical.get("capsule_absent"):
        failures.append("historical negative control did not exclude the capsule")
    if not historical.get("exact_claim_markers_absent"):
        failures.append("historical negative control contains current claim markers")
    candidate = data.get("candidate", {})
    if not candidate.get("capsule_complete_before_truncation"):
        failures.append("candidate capsule is incomplete before truncation")
    if not candidate.get("all_six_claim_markers_visible"):
        failures.append("not all six claim markers are evaluator-visible")
    trace = candidate.get("trace", [])
    visible_paths = [row.get("path") for row in trace]
    expected_prefix = [
        "pages/index.md",
        "pages/00-current-evidence/page.md",
    ]
    if visible_paths[:2] != expected_prefix:
        failures.append("candidate prompt ordering prefix is wrong")
    capsule_rows = [
        row for row in trace if row.get("path") == expected_prefix[1]
    ]
    if len(capsule_rows) != 1 or capsule_rows[0].get("truncated"):
        failures.append("capsule trace is absent, duplicated, or truncated")
    subset = data.get("historical_subset", {})
    if (
        not subset.get("path_subset")
        or not subset.get("protected_content_unchanged")
        or subset.get("missing")
        or subset.get("protected_changed")
    ):
        failures.append("historical file subset check failed")
    result = {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "independent_contract_checks": 10,
        "all_six_claim_markers_visible": not failures
        and candidate.get("all_six_claim_markers_visible") is True,
        "historical_tree_path_subset": not failures
        and subset.get("path_subset") is True,
        "protected_historical_content_unchanged": not failures
        and subset.get("protected_content_unchanged") is True,
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
