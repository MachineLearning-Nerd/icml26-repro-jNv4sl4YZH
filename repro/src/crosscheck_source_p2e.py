#!/usr/bin/env python3
"""Cross-check the pinned author P2E helper without using it as verification."""

from __future__ import annotations

import argparse
import importlib
import json
import math
import sys
from pathlib import Path

from verify_p2e_identity import p2e_log_value, p2e_parameters


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    sys.path.insert(0, str(args.source / "e-ca"))
    source_utils = importlib.import_module("utils")
    rows = []
    for n_calibration in (10, 20, 30, 50, 100, 200):
        for alpha in (0.05, 0.1, 0.2):
            source_c, source_s = source_utils.get_C_s(alpha, n_calibration)
            source_fn = source_utils.get_p_to_e("P2E", alpha, n_calibration)
            clean_c, clean_s = p2e_parameters(n_calibration, alpha)
            ranks = [j / (n_calibration + 1) for j in range(1, n_calibration + 2)]
            source_values = [float(source_fn(rank)) for rank in ranks]
            source_members = [value < 1.0 / alpha for value in source_values]
            p_members = [rank > alpha for rank in ranks]
            clean_members = [
                p2e_log_value(rank, alpha, clean_c, clean_s) < -math.log(alpha)
                for rank in ranks
            ]
            rows.append(
                {
                    "n_calibration": n_calibration,
                    "alpha": alpha,
                    "source_C": source_c,
                    "source_s": source_s,
                    "source_mean_e": sum(source_values) / len(source_values),
                    "source_set_mismatches": sum(a != b for a, b in zip(source_members, p_members)),
                    "cleanroom_set_mismatches": sum(a != b for a, b in zip(clean_members, p_members)),
                    "source_float_underflow_count": sum(value == 0.0 for value in source_values),
                }
            )

    result = {
        "source": str(args.source),
        "rows": rows,
        "summary": {
            "rows": len(rows),
            "all_source_membership_pass": all(row["source_set_mismatches"] == 0 for row in rows),
            "all_source_expectations_pass": all(abs(row["source_mean_e"] - 1.0) < 1e-11 for row in rows),
            "all_cleanroom_membership_pass": all(row["cleanroom_set_mismatches"] == 0 for row in rows),
            "underflow_is_documented": any(row["source_float_underflow_count"] > 0 for row in rows),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
