#!/usr/bin/env python3
"""Independent fail-closed checker for the Claim 2 counterexample output."""

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
    if evidence.get("verdict") != "FALSIFIED":
        failures.append("verdict is not FALSIFIED")
    counterexample = evidence.get("counterexample", {})
    for key in (
        "works_for_every_alpha_in_(0,1)",
        "satisfies_every_printed_assumption",
        "contradicts_uniqueness",
    ):
        if counterexample.get(key) is not True:
            failures.append(f"counterexample.{key} is not true")
    rows = evidence.get("finite_exact_cross_checks", [])
    if len(rows) != 7:
        failures.append(f"expected 7 exact cross-checks, found {len(rows)}")
    for row in rows:
        if row.get("exact_integral") != "1":
            failures.append(f"integral drift at alpha={row.get('alpha')}")
        if row.get("conformal_membership_mismatches_n_1_through_500") != 0:
            failures.append(f"membership mismatch at alpha={row.get('alpha')}")
        if row.get("candidate_differs_from_aon_at_zero") is not True:
            failures.append(f"no endpoint contradiction at alpha={row.get('alpha')}")
    if evidence.get("negative_controls_pass") is not True:
        failures.append("negative controls did not pass")
    non_circularity = evidence.get("non_circularity", {})
    if non_circularity.get("universal_counterexample_is_symbolic") is not True:
        failures.append("finite sweep improperly substituted for symbolic route")
    if non_circularity.get("finite_sweep_is_not_the_proof") is not True:
        failures.append("finite sweep improperly marked as proof")

    output = {
        "status": "PASS" if not failures else "FAIL",
        "verdict_checked": "FALSIFIED",
        "failures": failures,
        "checked_alpha_rows": len(rows),
        "checker_is_independent_of_verifier_implementation": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
