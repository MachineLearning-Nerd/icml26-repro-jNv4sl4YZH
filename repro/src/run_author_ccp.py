#!/usr/bin/env python3
"""Run the author CCP primitives at the paper's full reported protocol.

The upstream ``e-ccp/main.py`` hard-codes one dataset and five folds.  This
wrapper leaves every author estimator untouched and only supplies the paper's
three reported dataset/fold configurations (Boston/Abalone K=15, Parkinson
K=20) and its 100 released seeds.  It writes one resumable raw file per data
set.
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

import numpy as np


METHOD_KEYS = (
    ("mod-cross", "int_cc"),
    ("e-mod-cross", "int_cce"),
    ("u-mod-cross", "int_ccu"),
    ("eu-mod-cross", "int_cceu"),
    ("cross", "int_ccs"),
    ("ECCP", "int_cc_eval"),
    ("ECCP_exch", "int_cc_ev_exch"),
    ("UR-ECCP_exch", "int_cc_ev_exch_U"),
    ("ECCP(ind)", "int_cc_eval_ind"),
    ("ECCP(sqrt)", "int_cc_eval_sqrt"),
    ("ECCP(log)", "int_cc_eval_log"),
    ("ECCP(pow)", "int_cc_eval_pow"),
    ("ECCP (2α)", "int_cc_eval_2alpha"),
)
PAPER_DATASETS = {"boston": 15, "abalone": 15, "parkinson": 20}
MODELS = ("OLS", "RF", "Lasso")
SEEDS = tuple(range(45, 145))


def source_descriptor(source_root: Path) -> str:
    """Return portable source provenance rather than an absolute local path."""
    commit = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return f"Nabil-Ala/P2E_calibration@{commit}"


def call_author_model(name, functions, y_train, x_train, x_test, *, k, alpha, config, seed):
    if name == "OLS":
        return functions.cc_ols(
            y=y_train, X=x_train, x_test=x_test, K=k, alpha=alpha,
            n_grid=300, grid_factor=1.0, random_state=seed,
        )
    if name == "RF":
        return functions.cc_rf(
            y=y_train, X=x_train, x_test=x_test, K=k, alpha=alpha,
            ntree=config["ntree"], n_grid=300, grid_factor=1.0, random_state=seed,
        )
    if name == "Lasso":
        return functions.cc_lasso(
            y=y_train, X=x_train, x_test=x_test, K=k, alpha=alpha,
            n_grid=300, grid_factor=1.0, random_state=seed, lambda_=config["lambda_"],
        )
    raise ValueError(name)


def validated_completed_seeds(rows, dataset_key, k):
    """Validate a resumable checkpoint and return its complete seed set."""
    expected_cells = {(model, method) for model in MODELS for method, _ in METHOD_KEYS}
    cells_by_seed = defaultdict(set)
    for row in rows:
        if str(row["dataset_key"]) != dataset_key or int(row["folds"]) != k:
            raise RuntimeError(f"checkpoint scope mismatch for {dataset_key}")
        seed = int(row["seed"])
        if seed not in SEEDS:
            raise RuntimeError(f"unexpected checkpoint seed for {dataset_key}: {seed}")
        cell = (str(row["model"]), str(row["method"]))
        if cell in cells_by_seed[seed]:
            raise RuntimeError(f"duplicate checkpoint cell for {dataset_key}, seed {seed}: {cell}")
        if not (
            math.isfinite(float(row["coverage"]))
            and math.isfinite(float(row["length"]))
        ):
            raise RuntimeError(
                f"non-finite checkpoint metric for {dataset_key}, seed {seed}: {cell}"
            )
        cells_by_seed[seed].add(cell)
    for seed, cells in cells_by_seed.items():
        if cells != expected_cells:
            missing = sorted(expected_cells - cells)
            extra = sorted(cells - expected_cells)
            raise RuntimeError(
                f"incomplete checkpoint seed for {dataset_key}, seed {seed}: "
                f"missing={missing}, extra={extra}"
            )
    return set(cells_by_seed)


def write_json_atomic(path, payload):
    """Atomically replace a JSON artifact so an interrupted write cannot look complete."""
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def write_checkpoint(path, protocol, dataset_key, k, rows):
    completed = validated_completed_seeds(rows, dataset_key, k)
    payload = {
        "protocol": protocol,
        "dataset_key": dataset_key,
        "folds": k,
        "completed_seeds": sorted(completed),
        "rows": rows,
    }
    write_json_atomic(path, payload)


def load_checkpoint(path, protocol, dataset_key, k):
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("protocol") != protocol:
        raise RuntimeError(f"checkpoint protocol mismatch for {dataset_key}")
    if payload.get("dataset_key") != dataset_key or int(payload.get("folds")) != k:
        raise RuntimeError(f"checkpoint metadata mismatch for {dataset_key}")
    rows = payload.get("rows", [])
    completed = validated_completed_seeds(rows, dataset_key, k)
    if completed != {int(seed) for seed in payload.get("completed_seeds", [])}:
        raise RuntimeError(f"checkpoint seed summary mismatch for {dataset_key}")
    return rows


def write_completed_output(path, protocol, dataset_key, k, rows):
    completed = validated_completed_seeds(rows, dataset_key, k)
    expected_rows = len(SEEDS) * len(MODELS) * len(METHOD_KEYS)
    if completed != set(SEEDS) or len(rows) != expected_rows:
        raise RuntimeError(f"refusing incomplete final output for {dataset_key}")
    write_json_atomic(
        path,
        {
            "protocol": protocol,
            "dataset_key": dataset_key,
            "folds": k,
            "rows": rows,
        },
    )


def load_completed_output(path, protocol, dataset_key, k):
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("protocol") != protocol:
        raise RuntimeError(f"completed-output protocol mismatch for {dataset_key}")
    if payload.get("dataset_key") != dataset_key or int(payload.get("folds")) != k:
        raise RuntimeError(f"completed-output metadata mismatch for {dataset_key}")
    rows = payload.get("rows", [])
    completed = validated_completed_seeds(rows, dataset_key, k)
    expected_rows = len(SEEDS) * len(MODELS) * len(METHOD_KEYS)
    if completed != set(SEEDS) or len(rows) != expected_rows:
        raise RuntimeError(f"incomplete final output for {dataset_key}")
    return rows


def run_dataset(dataset_key, k, data_loader, functions, *, protocol, checkpoint, existing_rows):
    x, y, config = data_loader.load_dataset(dataset_key)
    n_train = config["n_train"]
    n_test = config["n_test"] if config["n_test"] is not None else y.shape[0] - n_train
    alpha = 0.1
    rows = list(existing_rows)
    completed_seeds = validated_completed_seeds(rows, dataset_key, k)
    for seed in SEEDS:
        if seed in completed_seeds:
            print(f"{dataset_key}: resume retaining seed {seed}", flush=True)
            continue
        rng = np.random.default_rng(seed)
        indices = np.arange(y.shape[0])
        train_idx = rng.choice(indices, size=n_train, replace=False)
        test_idx = np.setdiff1d(indices, train_idx)
        if len(test_idx) != n_test:
            raise RuntimeError(f"unexpected test size for {dataset_key}: {len(test_idx)} != {n_test}")
        y_train, x_train = y[train_idx], x[train_idx, :]
        y_test, x_test = y[test_idx], x[test_idx, :]
        for model_name in MODELS:
            result = call_author_model(
                model_name, functions, y_train, x_train, x_test,
                k=k, alpha=alpha, config=config, seed=seed,
            )
            for method_name, interval_key in METHOD_KEYS:
                intervals = result[interval_key]
                if len(intervals) != len(y_test):
                    raise RuntimeError(
                        f"unexpected interval count for {dataset_key}, seed {seed}, "
                        f"{model_name}/{method_name}: {len(intervals)} != {len(y_test)}"
                    )
                coverage = float(
                    np.nanmean(
                        [
                            functions.cov_int(interval, truth)
                            for interval, truth in zip(intervals, y_test)
                        ]
                    )
                )
                length = float(
                    np.nanmean([functions.len_int(interval) for interval in intervals])
                )
                rows.append(
                    {
                        "dataset_key": dataset_key,
                        "dataset": config["name"],
                        "folds": k,
                        "seed": seed,
                        "model": model_name,
                        "method": method_name,
                        "coverage": coverage,
                        "length": length,
                    }
                )
        completed_seeds = validated_completed_seeds(rows, dataset_key, k)
        if seed not in completed_seeds:
            raise RuntimeError(f"seed {seed} did not produce a complete checkpoint")
        write_checkpoint(checkpoint, protocol, dataset_key, k, rows)
        print(f"{dataset_key}: completed seed {seed}", flush=True)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--input-check", action="store_true",
                        help="load all bundled author datasets without running estimators")
    args = parser.parse_args()

    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
    source_root = args.source.resolve()
    source_dir = source_root / "e-ccp"
    output_dir = args.output_dir.resolve()
    # The released loader accesses its bundled CSVs through paths relative to
    # e-ccp/.  Keep this wrapper outside the source tree, but reproduce that
    # working-directory contract exactly before invoking author functions.
    os.chdir(source_dir)
    sys.path.insert(0, str(source_dir))
    data_loader = importlib.import_module("data_loader")
    functions = importlib.import_module("eccp_utils")
    protocol = {
        "source": source_descriptor(source_root),
        "datasets": PAPER_DATASETS,
        "seeds": list(SEEDS),
        "models": list(MODELS),
        "methods": [name for name, _ in METHOD_KEYS],
        "alpha": 0.1,
        "grid_points": 300,
    }
    if args.dry_run:
        print(json.dumps(protocol, sort_keys=True))
        return
    if args.input_check:
        inputs = {}
        for dataset_key, folds in PAPER_DATASETS.items():
            x, y, config = data_loader.load_dataset(dataset_key)
            inputs[dataset_key] = {
                "folds": folds,
                "n_features": int(x.shape[1]),
                "n_rows": int(x.shape[0]),
                "n_train": int(config["n_train"]),
            }
        print(json.dumps({"protocol": protocol, "inputs": inputs}, sort_keys=True))
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json_atomic(output_dir / "protocol.json", protocol)
    for dataset_key, k in PAPER_DATASETS.items():
        output = output_dir / f"{dataset_key}.json"
        if output.exists() and not args.force:
            rows = load_completed_output(output, protocol, dataset_key, k)
            print(f"resume: retaining verified {output.name} ({len(rows)} rows)")
            continue
        checkpoint = output_dir / f".{dataset_key}.partial.json"
        if args.force:
            write_checkpoint(checkpoint, protocol, dataset_key, k, [])
            existing_rows = []
        else:
            existing_rows = load_checkpoint(checkpoint, protocol, dataset_key, k)
        if existing_rows:
            print(
                f"resume: {dataset_key} checkpoint has "
                f"{len(validated_completed_seeds(existing_rows, dataset_key, k))} seeds",
                flush=True,
            )
        rows = run_dataset(
            dataset_key,
            k,
            data_loader,
            functions,
            protocol=protocol,
            checkpoint=checkpoint,
            existing_rows=existing_rows,
        )
        completed = validated_completed_seeds(rows, dataset_key, k)
        if completed != set(SEEDS) or len(rows) != len(SEEDS) * len(MODELS) * len(METHOD_KEYS):
            raise RuntimeError(f"full raw-row integrity failed for {dataset_key}")
        write_completed_output(output, protocol, dataset_key, k, rows)
        print(f"completed {dataset_key}: {len(rows)} raw rows -> {output}")


if __name__ == "__main__":
    main()
