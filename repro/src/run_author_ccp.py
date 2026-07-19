#!/usr/bin/env python3
"""Run the author CCP primitives at the paper's full reported protocol.

The upstream ``e-ccp/main.py`` hard-codes one dataset and five folds.  This
wrapper leaves every author estimator untouched and supplies the paper's three
reported dataset/fold configurations (Boston/Abalone K=15, Parkinson K=20)
and its 100 released seeds. The source calls its fourth classical calibrator
``ECCP(pow)`` and implements ``5(1-p)^4``, while the paper defines F3 as
``2(1-p)``. The wrapper reconstructs that paper-specified linear calibrator
from the returned author p-values and identical randomization stream. It writes
one resumable raw file per data set.
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
    ("ECCP(linear)", "int_cc_eval_linear"),
    ("ECCP (2α)", "int_cc_eval_2alpha"),
)
PAPER_DATASETS = {"boston": 15, "abalone": 15, "parkinson": 20}
MODELS = ("OLS", "RF", "Lasso")
SEEDS = tuple(range(45, 145))
EXECUTION_ADAPTER = "vectorized-exact-postprocessing-v1"


def source_descriptor(source_root: Path) -> str:
    """Return portable source provenance rather than an absolute local path."""
    commit = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return f"Nabil-Ala/P2E_calibration@{commit}"


def attach_paper_linear_calibrator(
    result, functions, *, n_train: int, k: int, alpha: float, seed: int
):
    """Add paper F3=2(1-p) intervals to an unchanged author model result.

    Each released model function returns the foldwise p-values and candidate
    grid. Replaying its local RNG through the fold permutation recovers the
    exact U-values used for every other randomized e-value baseline.
    """
    if "int_cc_eval_linear" in result:
        return result
    p_values = np.asarray(result["p_vals"], dtype=float)
    y_grid = np.asarray(result["ys"], dtype=float)
    if p_values.ndim != 3 or p_values.shape[0] != len(y_grid):
        raise RuntimeError("unexpected author p-value/grid shape")
    if p_values.shape[1] != k:
        raise RuntimeError(f"unexpected author fold count: {p_values.shape[1]} != {k}")
    if not np.isfinite(p_values).all() or np.any((p_values < 0.0) | (p_values > 1.0)):
        raise RuntimeError("author p-values are non-finite or outside [0,1]")

    rng = np.random.default_rng(seed)
    rng.permutation(n_train)
    u_values = rng.random(p_values.shape[2])
    if np.any(u_values <= 0.0):
        raise RuntimeError("zero randomization draw prevents finite linear e-values")
    linear_e_values = 2.0 * (1.0 - p_values)
    merged = linear_e_values.mean(axis=1) / u_values[None, :]
    intervals = [
        functions.set_cc_eval(merged[:, index], y_grid, alpha)
        for index in range(p_values.shape[2])
    ]
    augmented = dict(result)
    augmented["int_cc_eval_linear"] = intervals
    return augmented


def call_literal_author_model(
    name, functions, y_train, x_train, x_test, *, k, alpha, config, seed,
    n_grid=300,
):
    """Run the pinned source function literally; retained as a parity oracle."""
    if name == "OLS":
        result = functions.cc_ols(
            y=y_train, X=x_train, x_test=x_test, K=k, alpha=alpha,
            n_grid=n_grid, grid_factor=1.0, random_state=seed,
        )
    elif name == "RF":
        result = functions.cc_rf(
            y=y_train, X=x_train, x_test=x_test, K=k, alpha=alpha,
            ntree=config["ntree"], n_grid=n_grid, grid_factor=1.0, random_state=seed,
        )
    elif name == "Lasso":
        result = functions.cc_lasso(
            y=y_train, X=x_train, x_test=x_test, K=k, alpha=alpha,
            n_grid=n_grid, grid_factor=1.0, random_state=seed,
            lambda_=config["lambda_"],
        )
    else:
        raise ValueError(name)
    return attach_paper_linear_calibrator(
        result,
        functions,
        n_train=len(y_train),
        k=k,
        alpha=alpha,
        seed=seed,
    )


def intervals_from_p_values(
    p_values, grid, *, functions, alpha: float, m: int, used: int, u_values
):
    """Vectorize only the source's deterministic p/e aggregation stage.

    The pinned implementation loops over every grid/test pair in Python. This
    function evaluates the same formulas over NumPy arrays while retaining the
    fold axis and its reduction order. Large temporary arrays are created one
    calibrator at a time to keep the Parkinson peak memory bounded.
    """
    p_values = np.asarray(p_values, dtype=float)
    grid = np.asarray(grid, dtype=float)
    u_values = np.asarray(u_values, dtype=float)
    if p_values.ndim != 3 or p_values.shape[0] != len(grid):
        raise RuntimeError("unexpected p-value/grid shape in vectorized adapter")
    if p_values.shape[2] != len(u_values):
        raise RuntimeError("unexpected p-value/randomization shape")
    if not np.isfinite(p_values).all() or np.any((p_values <= 0.0) | (p_values > 1.0)):
        raise RuntimeError("p-values must be finite and in (0,1]")
    if not np.isfinite(u_values).all() or np.any((u_values <= 0.0) | (u_values >= 1.0)):
        raise RuntimeError("randomization draws must be finite and in (0,1)")

    folds = p_values.shape[1]
    fold_denominators = np.arange(1, folds + 1, dtype=float)[None, :, None]
    randomizer = u_values[None, :]
    pv_cc = np.mean(p_values, axis=1)

    cumulative_p = np.cumsum(p_values, axis=1) / fold_denominators
    pv_ecc = np.min(cumulative_p, axis=1)
    del cumulative_p
    pv_ucc = pv_cc / (2.0 - randomizer)
    pv_eucc = np.minimum(p_values[:, 0, :] / (2.0 - randomizer), pv_ecc)
    pv_ccs = (
        1.0 + np.sum(p_values * (m + 1.0) - 1.0, axis=1)
    ) / (used + 1.0)

    e_ind = np.mean((p_values <= alpha).astype(float) / alpha, axis=1) / randomizer
    e_log = np.mean(-np.log(p_values), axis=1) / randomizer
    e_power = np.mean(5.0 * (1.0 - p_values) ** 4, axis=1) / randomizer
    e_sqrt = np.mean(p_values ** (-0.5) - 1.0, axis=1) / randomizer
    e_linear = np.mean(2.0 * (1.0 - p_values), axis=1) / randomizer

    c_value, location = functions.get_C_s(alpha, m)
    e_values = functions.f_p_to_e(p_values, alpha, c_value, location)
    e_mean = np.mean(e_values, axis=1) / randomizer
    cumulative_e = np.cumsum(e_values, axis=1) / fold_denominators
    e_exch = np.max(cumulative_e, axis=1)
    e_exch_u = np.maximum(e_exch, e_values[:, 0, :] / randomizer)
    del cumulative_e, e_values

    c_value_2, location_2 = functions.get_C_s(2.0 * alpha, m)
    e_values_2 = functions.f_p_to_e(
        p_values, 2.0 * alpha, c_value_2, location_2
    )
    e_mean_2 = np.mean(e_values_2, axis=1) / randomizer
    del e_values_2

    def p_intervals(values):
        return [
            functions.set_cc(values[:, index], grid, alpha)
            for index in range(values.shape[1])
        ]

    def e_intervals(values, level=alpha):
        return [
            functions.set_cc_eval(values[:, index], grid, level)
            for index in range(values.shape[1])
        ]

    return {
        "p_vals": p_values,
        "ys": grid,
        "int_cc": p_intervals(pv_cc),
        "int_cce": p_intervals(pv_ecc),
        "int_ccu": p_intervals(pv_ucc),
        "int_cceu": p_intervals(pv_eucc),
        "int_ccs": p_intervals(pv_ccs),
        "int_cc_eval": e_intervals(e_mean),
        "int_cc_ev_exch": e_intervals(e_exch),
        "int_cc_ev_exch_U": e_intervals(e_exch_u),
        "int_cc_eval_2alpha": e_intervals(e_mean_2, 2.0 * alpha),
        "int_cc_eval_ind": e_intervals(e_ind),
        "int_cc_eval_sqrt": e_intervals(e_sqrt),
        "int_cc_eval_log": e_intervals(e_log),
        "int_cc_eval_pow": e_intervals(e_power),
        "int_cc_eval_linear": e_intervals(e_linear),
    }


def call_vectorized_author_model(
    name, functions, y_train, x_train, x_test, *, k, alpha, config, seed,
    n_grid=300,
):
    """Reproduce the source estimator/p-value core with vectorized aggregation."""
    y_train = np.asarray(y_train).ravel()
    x_train = np.asarray(x_train)
    x_test = np.asarray(x_test)
    if x_test.ndim == 1:
        x_test = x_test.reshape(1, -1)
    n_train = len(y_train)
    n_test = x_test.shape[0]
    grid = np.linspace(-np.max(np.abs(y_train)), np.max(np.abs(y_train)), num=n_grid)
    m = n_train // k
    if m == 0:
        raise ValueError("n < K: cannot form equal-size folds")
    used = m * k
    rng = np.random.default_rng(seed)
    indices = rng.permutation(n_train)[:used]
    folds = indices.reshape(k, m)
    p_values = np.empty((n_grid, k, n_test), dtype=float)

    for fold in range(k):
        calibration_idx = folds[fold]
        fit_idx = np.setdiff1d(indices, calibration_idx)
        if name == "OLS":
            fitted = functions.ols_pseudo(x_train[fit_idx, :], y_train[fit_idx])
            calibration_prediction = functions.ols_pseudo_predict(
                fitted, x_train[calibration_idx, :]
            )
            test_prediction = functions.ols_pseudo_predict(fitted, x_test)
        elif name == "RF":
            fitted = functions.RandomForestRegressor(
                n_estimators=config["ntree"],
                max_features=1.0,
                n_jobs=-1,
                random_state=seed,
            )
            fitted.fit(x_train[fit_idx, :], y_train[fit_idx])
            calibration_prediction = fitted.predict(x_train[calibration_idx, :])
            test_prediction = fitted.predict(x_test)
        elif name == "Lasso":
            fitted = functions.Lasso(
                alpha=config["lambda_"],
                fit_intercept=True,
                max_iter=10000,
                random_state=seed,
            )
            fitted.fit(x_train[fit_idx, :], y_train[fit_idx])
            calibration_prediction = fitted.predict(x_train[calibration_idx, :])
            test_prediction = fitted.predict(x_test)
        else:
            raise ValueError(name)

        calibration_errors = np.abs(
            y_train[calibration_idx] - np.asarray(calibration_prediction).ravel()
        )
        candidate_errors = np.abs(
            grid[:, None] - np.asarray(test_prediction).ravel()[None, :]
        )
        comparisons = (
            calibration_errors[:, None, None] >= candidate_errors[None, :, :]
        )
        p_values[:, fold, :] = (1.0 + comparisons.sum(axis=0)) / (m + 1.0)

    # Do not retain the largest foldwise comparison tensor while constructing
    # the full set of aggregated e/p arrays (material for Parkinson memory).
    del comparisons, candidate_errors, calibration_errors
    del calibration_prediction, test_prediction, fitted
    u_values = rng.random(n_test)
    return intervals_from_p_values(
        p_values,
        grid,
        functions=functions,
        alpha=alpha,
        m=m,
        used=used,
        u_values=u_values,
    )


def call_author_model(
    name, functions, y_train, x_train, x_test, *, k, alpha, config, seed
):
    return call_vectorized_author_model(
        name,
        functions,
        y_train,
        x_train,
        x_test,
        k=k,
        alpha=alpha,
        config=config,
        seed=seed,
    )


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
        coverage = float(row["coverage"])
        length = float(row["length"])
        if not (math.isfinite(coverage) and math.isfinite(length)):
            raise RuntimeError(
                f"non-finite checkpoint metric for {dataset_key}, seed {seed}: {cell}"
            )
        if not (0.0 <= coverage <= 1.0 and length >= 0.0):
            raise RuntimeError(
                f"out-of-range checkpoint metric for {dataset_key}, seed {seed}: "
                f"{cell} coverage={coverage}, length={length}"
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


def run_dataset(
    dataset_key,
    k,
    data_loader,
    functions,
    *,
    protocol,
    checkpoint,
    existing_rows,
    model_runner=call_author_model,
):
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
            result = model_runner(
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
        "execution_adapter": EXECUTION_ADAPTER,
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
