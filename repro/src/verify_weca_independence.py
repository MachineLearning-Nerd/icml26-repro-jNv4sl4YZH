#!/usr/bin/env python3
"""Audit the released WECA data split required by its coverage guarantee."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


SOURCE_COMMIT = "66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974"
METHODS_SHA256 = "dda5d2429d4ca8c77be6a3b04bb3c159360bf3af58d1087a5f31cc17ea44cf86"
WECA_FUNCTION_SHA256 = (
    "541a30601a5346d0adbcf50bb9dcfd2e5e8317f7403fb4540516680a52751bfb"
)
SEEDS = (42, 0, 1, 7, 10, 13)
REQUIRED_FLOW = (
    "idx = rng.permutation(n)",
    "i1 = idx[:n1]",
    "i2 = idx[n1:n1+n2]",
    "i3 = idx[n1+n2:]",
    "cal_scores_1 = _cal_scores(models, X_calib, y_calib, idxs_1)",
    "cal_scores_3 = _cal_scores(models, X_calib, y_calib, idxs_3)",
    "X2 = _rows(X_calib, i2)",
    "pvals = _pvals(grid_scores, cal_scores_1)",
    "w_star =  W[np.argmin(avg_lengths)]",
    "true_pvals = _pvals(true_scores, cal_scores_3)",
    "covered.append(true_evals @ w_star < threshold)",
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def source_contract(source: str) -> dict[str, object]:
    """Bind the audit to the exact released function and its split dataflow."""
    tree = ast.parse(source)
    functions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "Evalue_aggregation_weighted"
    ]
    if len(functions) != 1:
        raise RuntimeError("expected one Evalue_aggregation_weighted function")
    function = functions[0]
    segment = ast.get_source_segment(source, function)
    if segment is None:
        raise RuntimeError("could not extract WECA function source")
    function_hash = sha256_bytes(segment.encode("utf-8"))
    if function_hash != WECA_FUNCTION_SHA256:
        raise RuntimeError(f"WECA function source drift: {function_hash}")
    missing = [fragment for fragment in REQUIRED_FLOW if fragment not in segment]
    if missing:
        raise RuntimeError(f"WECA split/dataflow contract drift: {missing}")
    return {
        "function": function.name,
        "start_line": function.lineno,
        "end_line": function.end_lineno,
        "sha256": function_hash,
        "required_flow_checks": len(REQUIRED_FLOW),
        "all_required_flow_present": True,
    }


def load_methods(source_root: Path):
    source_dir = source_root / "e-ca"
    path = source_dir / "methods.py"
    spec = importlib.util.spec_from_file_location("pinned_weca_methods", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load pinned WECA methods")
    sys.path.insert(0, str(source_dir))
    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


class LinearModel:
    def __init__(self, coefficients: tuple[float, float], bias: float):
        self.coefficients = np.asarray(coefficients, dtype=float)
        self.bias = float(bias)

    def predict(self, values):
        array = np.asarray(values, dtype=float)
        return array @ self.coefficients + self.bias


def illegal_test_adaptive_weight(models, x_test, y_test) -> list[float]:
    """Forbidden negative control: pick a model after seeing test outcomes."""
    losses = [
        float(np.mean((np.asarray(model.predict(x_test)) - y_test) ** 2))
        for model in models
    ]
    weight = np.zeros(len(models), dtype=float)
    weight[int(np.argmin(losses))] = 1.0
    return weight.tolist()


def audit_case(methods, seed: int) -> dict[str, object]:
    rng = np.random.default_rng(100_000 + seed)
    n_calibration = 40
    x_calibration = rng.normal(size=(n_calibration, 2))
    y_calibration = (
        0.7 * x_calibration[:, 0]
        - 0.25 * x_calibration[:, 1]
        + rng.normal(scale=0.15, size=n_calibration)
    )
    models = [
        LinearModel((0.45, -0.10), -0.4),
        LinearModel((-0.55, 0.35), 0.7),
        LinearModel((1.10, 0.15), 0.1),
    ]
    calibration_indices = [np.arange(n_calibration) for _ in models]
    x_test = rng.normal(size=(7, 2))
    y_test = rng.normal(size=7)
    u_test = np.random.default_rng(seed).uniform(size=len(x_test))

    def run(x_cal, y_cal, x_eval, y_eval):
        return methods.Evalue_aggregation_weighted(
            models,
            x_cal,
            y_cal,
            calibration_indices,
            x_eval,
            y_eval,
            alpha=0.1,
            U_test=u_test,
            M=64,
            seed=seed,
            P_TO_E="linear",
            B=30,
            Random=False,
        )[-1]

    baseline_weight = np.asarray(
        run(x_calibration, y_calibration, x_test, y_test), dtype=float
    )
    split = np.random.default_rng(seed).permutation(n_calibration)
    n1 = n_calibration // 4
    n2 = n_calibration // 4
    i1 = split[:n1]
    i2 = split[n1 : n1 + n2]
    i3 = split[n1 + n2 :]
    if set(i1) & set(i2) or set(i1) & set(i3) or set(i2) & set(i3):
        raise RuntimeError("released WECA split is not disjoint")
    if set(np.concatenate((i1, i2, i3))) != set(range(n_calibration)):
        raise RuntimeError("released WECA split does not partition calibration rows")

    x_final_mutation = x_calibration.copy()
    y_final_mutation = y_calibration.copy()
    x_final_mutation[i3] = 100.0 + 17.0 * x_final_mutation[i3]
    y_final_mutation[i3] = -200.0 + 23.0 * y_final_mutation[i3]
    final_mutation_weight = np.asarray(
        run(x_final_mutation, y_final_mutation, x_test, y_test), dtype=float
    )

    x_test_mutation = 50.0 - 11.0 * x_test
    y_test_mutation = 300.0 + 19.0 * y_test
    test_mutation_weight = np.asarray(
        run(x_calibration, y_calibration, x_test_mutation, y_test_mutation),
        dtype=float,
    )

    adaptive_first = illegal_test_adaptive_weight(
        models, x_test, np.asarray(models[0].predict(x_test))
    )
    adaptive_second = illegal_test_adaptive_weight(
        models, x_test, np.asarray(models[1].predict(x_test))
    )
    return {
        "seed": seed,
        "split_sizes": {"weight_calibration": len(i1), "tuning": len(i2), "final_calibration": len(i3)},
        "split_is_disjoint_partition": True,
        "baseline_weight": baseline_weight.tolist(),
        "final_calibration_mutation_max_abs_weight_change": float(
            np.max(np.abs(baseline_weight - final_mutation_weight))
        ),
        "test_mutation_max_abs_weight_change": float(
            np.max(np.abs(baseline_weight - test_mutation_weight))
        ),
        "illegal_test_adaptive_weights": [adaptive_first, adaptive_second],
        "illegal_test_adaptive_control_changes": adaptive_first != adaptive_second,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source_root = args.source.resolve()
    commit = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if commit != SOURCE_COMMIT:
        raise RuntimeError(f"source commit drift: {commit}")
    methods_path = source_root / "e-ca/methods.py"
    methods_bytes = methods_path.read_bytes()
    methods_hash = sha256_bytes(methods_bytes)
    if methods_hash != METHODS_SHA256:
        raise RuntimeError(f"methods.py source drift: {methods_hash}")
    contract = source_contract(methods_bytes.decode("utf-8"))
    methods = load_methods(source_root)
    cases = [audit_case(methods, seed) for seed in SEEDS]
    summary = {
        "case_count": len(cases),
        "all_split_partitions_disjoint": all(
            case["split_is_disjoint_partition"] for case in cases
        ),
        "all_weights_independent_of_final_calibration": all(
            case["final_calibration_mutation_max_abs_weight_change"] == 0.0
            for case in cases
        ),
        "all_weights_independent_of_test_data_and_outcomes": all(
            case["test_mutation_max_abs_weight_change"] == 0.0 for case in cases
        ),
        "all_illegal_test_adaptive_controls_change": all(
            case["illegal_test_adaptive_control_changes"] for case in cases
        ),
        "all_required_flow_present": contract["all_required_flow_present"],
    }
    if not all(summary.values()):
        raise RuntimeError(f"WECA independence audit failed: {summary}")
    result = {
        "source": f"Nabil-Ala/P2E_calibration@{commit}",
        "methods_sha256": methods_hash,
        "function_contract": contract,
        "cases": cases,
        "summary": summary,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(args.output.name + ".tmp")
    temporary.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(args.output)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
