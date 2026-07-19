#!/usr/bin/env python3
"""Reproducible microbenchmark for literal versus vectorized CCP calibration."""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
from pathlib import Path

import numpy as np


def load_functions(source: Path):
    path = source.resolve() / "e-ccp/eccp_utils.py"
    spec = importlib.util.spec_from_file_location("benchmark_eccp_utils", path)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot import pinned source from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def literal_kernel(p_values, u_values, functions, c1, s1, c2, s2):
    grid_points, folds, test_points = p_values.shape
    outputs = np.empty((8, grid_points, test_points), dtype=float)
    denominators = np.arange(1, folds + 1)
    for test_index in range(test_points):
        u_value = u_values[test_index]
        for grid_index in range(grid_points):
            values = p_values[grid_index, :, test_index]
            e_values = functions.f_p_to_e(values, 0.1, c1, s1)
            cumulative = np.cumsum(e_values) / denominators
            outputs[:, grid_index, test_index] = (
                np.mean((values <= 0.1).astype(float) / 0.1) / u_value,
                np.mean(-np.log(values)) / u_value,
                np.mean(5.0 * (1.0 - values) ** 4) / u_value,
                np.mean(values ** (-0.5) - 1.0) / u_value,
                np.mean(e_values) / u_value,
                np.max(cumulative),
                max(np.max(cumulative), e_values[0] / u_value),
                np.mean(functions.f_p_to_e(values, 0.2, c2, s2)) / u_value,
            )
    return outputs


def vectorized_kernel(p_values, u_values, functions, c1, s1, c2, s2):
    folds = p_values.shape[1]
    randomizer = u_values[None, :]
    e_values = functions.f_p_to_e(p_values, 0.1, c1, s1)
    cumulative = np.cumsum(e_values, axis=1) / np.arange(
        1, folds + 1, dtype=float
    )[None, :, None]
    return np.stack(
        (
            np.mean((p_values <= 0.1).astype(float) / 0.1, axis=1) / randomizer,
            np.mean(-np.log(p_values), axis=1) / randomizer,
            np.mean(5.0 * (1.0 - p_values) ** 4, axis=1) / randomizer,
            np.mean(p_values ** (-0.5) - 1.0, axis=1) / randomizer,
            np.mean(e_values, axis=1) / randomizer,
            np.max(cumulative, axis=1),
            np.maximum(np.max(cumulative, axis=1), e_values[:, 0, :] / randomizer),
            np.mean(functions.f_p_to_e(p_values, 0.2, c2, s2), axis=1)
            / randomizer,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    functions = load_functions(args.source)

    folds, calibration_per_fold = 20, 150
    grid_points, test_points = 300, 10
    rng = np.random.default_rng(20260719)
    p_values = rng.integers(
        1,
        calibration_per_fold + 2,
        size=(grid_points, folds, test_points),
    ).astype(float) / (calibration_per_fold + 1.0)
    u_values = rng.random(test_points)
    c1, s1 = functions.get_C_s(0.1, calibration_per_fold)
    c2, s2 = functions.get_C_s(0.2, calibration_per_fold)

    started = time.perf_counter()
    literal = literal_kernel(p_values, u_values, functions, c1, s1, c2, s2)
    literal_seconds = time.perf_counter() - started
    started = time.perf_counter()
    vectorized = vectorized_kernel(p_values, u_values, functions, c1, s1, c2, s2)
    vectorized_seconds = time.perf_counter() - started
    max_abs_error = float(np.max(np.abs(literal - vectorized)))
    if max_abs_error > 1e-12:
        raise RuntimeError(f"vectorized kernel parity failed: {max_abs_error}")

    scale = (2_875 / test_points) * 3 * 100
    result = {
        "shape": {
            "grid_points": grid_points,
            "folds": folds,
            "test_points": test_points,
        },
        "literal_seconds": literal_seconds,
        "vectorized_seconds": vectorized_seconds,
        "speedup": literal_seconds / vectorized_seconds,
        "max_abs_error": max_abs_error,
        "projected_parkinson_literal_kernel_hours": literal_seconds * scale / 3600,
        "projected_parkinson_vectorized_kernel_hours": vectorized_seconds * scale / 3600,
        "projection_scope": "calibrator kernel only; excludes model fitting and interval extraction",
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
