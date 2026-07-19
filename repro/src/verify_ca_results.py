#!/usr/bin/env python3
"""Independently aggregate raw author CA rows and evaluate Claim 2."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


COMPARATORS = ("log", "sqrt", "linear")
CALIBRATORS = ("log", "linear", "sqrt", "AoN", "P2E")
EXPECTED_METHODS = (
    "CM",
    "CR",
    "P-value Aggregation",
    "COLA-S",
    *(f"{prefix}({calibrator})" for prefix in ("ECA", "UR-ECA", "WECA", "UR-WECA") for calibrator in CALIBRATORS),
)


def mean_and_sd(values: list[float]) -> dict[str, float | None]:
    if not values or not all(math.isfinite(value) for value in values):
        return {"mean": None, "sample_sd": None}
    return {
        "mean": statistics.fmean(values),
        "sample_sd": statistics.stdev(values) if len(values) > 1 else 0.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    protocol_path = args.raw_dir / "protocol.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    task_names = protocol["tasks"]
    expected_seeds = set(protocol["seeds"])
    expected_cells = {
        (dataset, method, seed)
        for dataset in task_names
        for method in EXPECTED_METHODS
        for seed in expected_seeds
    }
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    observed_cells: set[tuple[str, str, int]] = set()
    duplicate_cells: set[tuple[str, str, int]] = set()
    unexpected_rows = 0
    nonfinite_rows = 0
    structural_integrity = {dataset: True for dataset in task_names}
    rows_seen = 0
    for task_name in task_names:
        payload = json.loads((args.raw_dir / f"{task_name}.json").read_text(encoding="utf-8"))
        if payload.get("metadata") != protocol or payload.get("dataset") != task_name:
            structural_integrity[task_name] = False
        for row in payload["rows"]:
            rows_seen += 1
            dataset = str(row["Dataset"])
            method = str(row["Method"])
            seed = int(row["Seed"])
            cell = (dataset, method, seed)
            finite = math.isfinite(float(row["Coverage"])) and math.isfinite(float(row["Avg Length"]))
            valid_scope = (
                dataset == task_name
                and method in EXPECTED_METHODS
                and seed in expected_seeds
            )
            if not valid_scope:
                unexpected_rows += 1
                structural_integrity[task_name] = False
            if not finite:
                nonfinite_rows += 1
                structural_integrity[task_name] = False
            if cell in observed_cells:
                duplicate_cells.add(cell)
                structural_integrity[task_name] = False
            observed_cells.add(cell)
            if valid_scope:
                grouped[(dataset, method)].append(row)

    summaries: dict[str, dict[str, dict[str, float | int]]] = {}
    cell_integrity: dict[str, bool] = {}
    for dataset in task_names:
        dataset_rows = [row for (name, _), values in grouped.items() if name == dataset for row in values]
        methods_present = {str(row["Method"]) for row in dataset_rows}
        per_method_seed_sets = {
            method: {int(row["Seed"]) for row in grouped[(dataset, method)]}
            for method in methods_present
        }
        cell_integrity[dataset] = structural_integrity[dataset] and (
            len(dataset_rows) == len(EXPECTED_METHODS) * len(expected_seeds)
            and methods_present == set(EXPECTED_METHODS)
            and all(per_method_seed_sets[method] == expected_seeds for method in EXPECTED_METHODS)
        )
        summaries[dataset] = {}
        for (name, method), rows in sorted(grouped.items()):
            if name != dataset:
                continue
            cov = mean_and_sd([float(row["Coverage"]) for row in rows])
            length = mean_and_sd([float(row["Avg Length"]) for row in rows])
            summaries[dataset][method] = {
                "seed_count": len(rows),
                "coverage_mean": cov["mean"],
                "coverage_sd": cov["sample_sd"],
                "length_mean": length["mean"],
                "length_sd": length["sample_sd"],
            }

    comparisons = []
    for dataset, methods in summaries.items():
        for prefix in ("WECA", "UR-WECA"):
            p2e_name = f"{prefix}(P2E)"
            if p2e_name not in methods:
                continue
            for calibrator in COMPARATORS:
                baseline_name = f"{prefix}({calibrator})"
                if baseline_name not in methods:
                    continue
                p2e_value = methods[p2e_name]["length_mean"]
                baseline_value = methods[baseline_name]["length_mean"]
                if p2e_value is None or baseline_value is None:
                    continue
                p2e_length = float(p2e_value)
                baseline_length = float(baseline_value)
                comparisons.append(
                    {
                        "dataset": dataset,
                        "method_family": prefix,
                        "baseline": baseline_name,
                        "p2e_length": p2e_length,
                        "baseline_length": baseline_length,
                        "absolute_reduction": baseline_length - p2e_length,
                        "p2e_is_shorter": p2e_length < baseline_length,
                    }
                )

    target = 1.0 - float(protocol["alpha"])
    result = {
        "protocol": protocol,
        "rows_seen": rows_seen,
        "summaries": summaries,
        "efficiency_comparisons": comparisons,
        "summary": {
            "all_four_tasks_present": len(summaries) == 4,
            "all_full_seed_method_cells_present": all(cell_integrity.values()),
            "dataset_integrity": cell_integrity,
            "expected_rows": len(task_names) * len(EXPECTED_METHODS) * len(expected_seeds),
            "observed_unique_cells": len(observed_cells),
            "expected_unique_cells": len(expected_cells),
            "duplicate_cell_count": len(duplicate_cells),
            "unexpected_row_count": unexpected_rows,
            "nonfinite_row_count": nonfinite_rows,
            "exact_cell_set": observed_cells == expected_cells,
            "comparison_count": len(comparisons),
            "p2e_shorter_count": sum(row["p2e_is_shorter"] for row in comparisons),
            "nominal_coverage": target,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
