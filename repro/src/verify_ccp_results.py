#!/usr/bin/env python3
"""Independent raw-row aggregation for the full author CCP protocol."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


EMPIRICAL_COVERAGE_SHORTFALL_TOLERANCE = 0.02


def mean_and_sd(values: list[float]) -> tuple[float | None, float | None]:
    if not values or not all(math.isfinite(value) for value in values):
        return None, None
    return statistics.fmean(values), statistics.stdev(values) if len(values) > 1 else 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    protocol = json.loads((args.raw_dir / "protocol.json").read_text(encoding="utf-8"))
    expected_seeds = set(protocol["seeds"])
    expected_models = set(protocol["models"])
    expected_methods = set(protocol["methods"])
    expected_cells = {
        (dataset_key, model, method, seed)
        for dataset_key in protocol["datasets"]
        for model in expected_models
        for method in expected_methods
        for seed in expected_seeds
    }
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    observed_cells: set[tuple[str, str, str, int]] = set()
    duplicate_cells: set[tuple[str, str, str, int]] = set()
    unexpected_rows = 0
    nonfinite_rows = 0
    structural_integrity = {dataset_key: True for dataset_key in protocol["datasets"]}
    total_rows = 0
    for dataset_key, folds in protocol["datasets"].items():
        payload = json.loads((args.raw_dir / f"{dataset_key}.json").read_text(encoding="utf-8"))
        if (
            payload.get("protocol") != protocol
            or payload.get("dataset_key") != dataset_key
            or int(payload.get("folds", -1)) != folds
        ):
            structural_integrity[dataset_key] = False
        for row in payload["rows"]:
            total_rows += 1
            row_dataset = str(row["dataset_key"])
            model = str(row["model"])
            method = str(row["method"])
            seed = int(row["seed"])
            cell = (row_dataset, model, method, seed)
            finite = math.isfinite(float(row["coverage"])) and math.isfinite(float(row["length"]))
            valid_scope = (
                row_dataset == dataset_key
                and model in expected_models
                and method in expected_methods
                and seed in expected_seeds
                and int(row["folds"]) == folds
            )
            if not valid_scope:
                unexpected_rows += 1
                structural_integrity[dataset_key] = False
            if not finite:
                nonfinite_rows += 1
                structural_integrity[dataset_key] = False
            if cell in observed_cells:
                duplicate_cells.add(cell)
                structural_integrity[dataset_key] = False
            observed_cells.add(cell)
            if valid_scope:
                grouped[(row_dataset, model, method)].append(row)

    summaries = {}
    integrity = {}
    for dataset_key, folds in protocol["datasets"].items():
        summaries[dataset_key] = {}
        integrity[dataset_key] = structural_integrity[dataset_key]
        for model in expected_models:
            summaries[dataset_key][model] = {}
            for method in expected_methods:
                rows = grouped[(dataset_key, model, method)]
                seed_set = {int(row["seed"]) for row in rows}
                valid = len(rows) == len(expected_seeds) and seed_set == expected_seeds and all(int(row["folds"]) == folds for row in rows)
                integrity[dataset_key] = integrity[dataset_key] and valid
                coverages = [float(row["coverage"]) for row in rows]
                lengths = [float(row["length"]) for row in rows]
                coverage_mean, coverage_sd = mean_and_sd(coverages)
                length_mean, length_sd = mean_and_sd(lengths)
                summaries[dataset_key][model][method] = {
                    "seed_count": len(rows),
                    "coverage_mean": coverage_mean,
                    "coverage_sd": coverage_sd,
                    "length_mean": length_mean,
                    "length_sd": length_sd,
                }

    nominal_coverage = 1.0 - protocol["alpha"]
    eccp_coverage_means = [
        float(methods["ECCP"]["coverage_mean"])
        for models in summaries.values()
        for methods in models.values()
        if "ECCP" in methods and methods["ECCP"]["coverage_mean"] is not None
    ]
    eccp_coverage_pass_count = sum(
        coverage >= nominal_coverage - EMPIRICAL_COVERAGE_SHORTFALL_TOLERANCE
        for coverage in eccp_coverage_means
    )
    result = {
        "protocol": protocol,
        "rows_seen": total_rows,
        "summaries": summaries,
        "summary": {
            "all_full_seed_cells_present": all(integrity.values()),
            "dataset_integrity": integrity,
            "expected_rows": len(protocol["datasets"]) * len(expected_models) * len(expected_methods) * len(expected_seeds),
            "observed_unique_cells": len(observed_cells),
            "expected_unique_cells": len(expected_cells),
            "duplicate_cell_count": len(duplicate_cells),
            "unexpected_row_count": unexpected_rows,
            "nonfinite_row_count": nonfinite_rows,
            "exact_cell_set": observed_cells == expected_cells,
            "eccp_empirical_coverage_cell_count": len(eccp_coverage_means),
            "eccp_empirical_coverage_pass_count": eccp_coverage_pass_count,
            "all_eccp_empirical_coverage_within_tolerance": (
                bool(eccp_coverage_means)
                and eccp_coverage_pass_count == len(eccp_coverage_means)
            ),
            "empirical_coverage_shortfall_tolerance": EMPIRICAL_COVERAGE_SHORTFALL_TOLERANCE,
            "minimum_eccp_empirical_coverage": (
                min(eccp_coverage_means) if eccp_coverage_means else None
            ),
            "nominal_coverage": nominal_coverage,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
