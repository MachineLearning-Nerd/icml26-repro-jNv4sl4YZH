#!/usr/bin/env python3
"""Run the author conformal-aggregation protocol unchanged at full scale.

The upstream driver exposes a useful per-dataset function but its top-level
entry point always runs all tasks as one uninterruptible job.  This wrapper
calls that author function with its released constants and writes one raw file
per completed task, making a long CPU run safely resumable without altering
the author's implementation.
"""

from __future__ import annotations

import argparse
import importlib
import json
import math
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


CALIBRATORS = ("log", "linear", "sqrt", "AoN", "P2E")
EXPECTED_METHODS = (
    "CM",
    "CR",
    "P-value Aggregation",
    "COLA-S",
    *(
        f"{prefix}({calibrator})"
        for prefix in ("ECA", "UR-ECA", "WECA", "UR-WECA")
        for calibrator in CALIBRATORS
    ),
)


def json_default(value: object) -> object:
    if hasattr(value, "item"):
        return value.item()
    if hasattr(value, "tolist"):
        return value.tolist()
    return str(value)


def source_descriptor(source_root: Path) -> str:
    """Return a portable provenance string without exposing a local path."""
    commit = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return f"Nabil-Ala/P2E_calibration@{commit}"


def validated_completed_seeds(rows, dataset_name, expected_seeds):
    """Validate resumable author rows and return structurally complete seeds."""
    expected_methods = set(EXPECTED_METHODS)
    allowed_seeds = {int(seed) for seed in expected_seeds}
    methods_by_seed = defaultdict(set)
    for row in rows:
        if str(row["Dataset"]) != dataset_name:
            raise RuntimeError(f"checkpoint scope mismatch for {dataset_name}")
        seed = int(row["Seed"])
        if seed not in allowed_seeds:
            raise RuntimeError(f"unexpected checkpoint seed for {dataset_name}: {seed}")
        method = str(row["Method"])
        if method in methods_by_seed[seed]:
            raise RuntimeError(
                f"duplicate checkpoint cell for {dataset_name}, seed {seed}: {method}"
            )
        if method not in expected_methods:
            raise RuntimeError(
                f"unexpected checkpoint method for {dataset_name}, seed {seed}: {method}"
            )
        coverage = float(row["Coverage"])
        length = float(row["Avg Length"])
        if not (math.isfinite(coverage) and math.isfinite(length)):
            raise RuntimeError(
                f"non-finite checkpoint metric for {dataset_name}, seed {seed}: {method}"
            )
        if not (0.0 <= coverage <= 1.0 and length >= 0.0):
            raise RuntimeError(
                f"out-of-range checkpoint metric for {dataset_name}, seed {seed}: "
                f"{method} coverage={coverage}, length={length}"
            )
        methods_by_seed[seed].add(method)
    for seed, methods in methods_by_seed.items():
        if methods != expected_methods:
            missing = sorted(expected_methods - methods)
            extra = sorted(methods - expected_methods)
            raise RuntimeError(
                f"incomplete checkpoint seed for {dataset_name}, seed {seed}: "
                f"missing={missing}, extra={extra}"
            )
    return set(methods_by_seed)


def write_json_atomic(path, payload):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, default=json_default, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def write_checkpoint(path, metadata, dataset_name, rows):
    completed = validated_completed_seeds(rows, dataset_name, metadata["seeds"])
    write_json_atomic(
        path,
        {
            "metadata": metadata,
            "dataset": dataset_name,
            "completed_seeds": sorted(completed),
            "rows": rows,
        },
    )


def load_checkpoint(path, metadata, dataset_name):
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("metadata") != metadata or payload.get("dataset") != dataset_name:
        raise RuntimeError(f"checkpoint metadata mismatch for {dataset_name}")
    rows = payload.get("rows", [])
    completed = validated_completed_seeds(rows, dataset_name, metadata["seeds"])
    if completed != {int(seed) for seed in payload.get("completed_seeds", [])}:
        raise RuntimeError(f"checkpoint seed summary mismatch for {dataset_name}")
    return rows


def write_completed_output(path, metadata, dataset_name, rows):
    completed = validated_completed_seeds(rows, dataset_name, metadata["seeds"])
    expected_rows = len(metadata["seeds"]) * len(EXPECTED_METHODS)
    if completed != {int(seed) for seed in metadata["seeds"]} or len(rows) != expected_rows:
        raise RuntimeError(f"refusing incomplete final output for {dataset_name}")
    write_json_atomic(
        path,
        {"metadata": metadata, "dataset": dataset_name, "rows": rows},
    )


def load_completed_output(path, metadata, dataset_name):
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("metadata") != metadata or payload.get("dataset") != dataset_name:
        raise RuntimeError(f"completed-output metadata mismatch for {dataset_name}")
    rows = payload.get("rows", [])
    completed = validated_completed_seeds(rows, dataset_name, metadata["seeds"])
    expected_rows = len(metadata["seeds"]) * len(EXPECTED_METHODS)
    if completed != {int(seed) for seed in metadata["seeds"]} or len(rows) != expected_rows:
        raise RuntimeError(f"incomplete final output for {dataset_name}")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--input-check", action="store_true",
                        help="load each released OpenML task without fitting estimators")
    args = parser.parse_args()

    source_root = args.source.resolve()
    source_dir = source_root / "e-ca"
    output_dir = args.output_dir.resolve()
    # Keep the paper-scale sweep deterministic and avoid hidden BLAS
    # oversubscription on the shared four-core host.
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
    sys.path.insert(0, str(source_dir))
    config = importlib.import_module("config")
    author_main = importlib.import_module("main")
    tasks = list(config.DATASETS.items())
    metadata = {
        "source": source_descriptor(source_root),
        "tasks": [name for name, _ in tasks],
        "task_ids": [task_id for _, task_id in tasks],
        "seeds": list(config.seeds),
        "alpha": config.alpha,
        "M": config.M,
        "B": config.B,
    }
    if args.dry_run:
        print(json.dumps(metadata, sort_keys=True))
        return
    if args.input_check:
        inputs = {}
        for dataset_name, task_id in tasks:
            x, y = author_main.load_dataset(task_id)
            retained = min(len(y), config.data_limit)
            inputs[dataset_name] = {
                "n_features": int(x.shape[1]),
                "n_rows": int(x.shape[0]),
                "retained_rows": int(retained),
            }
        print(json.dumps({"protocol": metadata, "inputs": inputs}, sort_keys=True))
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json_atomic(output_dir / "protocol.json", metadata)
    for dataset_name, task_id in tasks:
        output = output_dir / f"{dataset_name}.json"
        if output.exists() and not args.force:
            rows = load_completed_output(output, metadata, dataset_name)
            print(f"resume: retaining verified {output.name} ({len(rows)} rows)")
            continue
        checkpoint = output_dir / f".{dataset_name}.partial.json"
        if args.force:
            write_checkpoint(checkpoint, metadata, dataset_name, [])
            rows = []
        else:
            rows = load_checkpoint(checkpoint, metadata, dataset_name)
        completed_seeds = validated_completed_seeds(
            rows, dataset_name, metadata["seeds"]
        )
        if completed_seeds:
            print(
                f"resume: {dataset_name} checkpoint has {len(completed_seeds)} seeds",
                flush=True,
            )
        for seed in config.seeds:
            if int(seed) in completed_seeds:
                print(f"{dataset_name}: resume retaining seed {seed}", flush=True)
                continue
            seed_rows = author_main.run_one_dataset(
                dataset_name=dataset_name,
                dataset_config=task_id,
                seeds=[seed],
                alpha=config.alpha,
                M=config.M,
                B=config.B,
            )
            candidate_rows = [*rows, *seed_rows]
            completed_seeds = validated_completed_seeds(
                candidate_rows, dataset_name, metadata["seeds"]
            )
            if int(seed) not in completed_seeds:
                raise RuntimeError(f"seed {seed} did not produce a complete checkpoint")
            rows = candidate_rows
            write_checkpoint(checkpoint, metadata, dataset_name, rows)
            print(f"{dataset_name}: completed seed {seed}", flush=True)
        write_completed_output(output, metadata, dataset_name, rows)
        display_output = args.output_dir / output.name
        print(f"completed {dataset_name}: {len(rows)} raw rows -> {display_output}")


if __name__ == "__main__":
    main()
