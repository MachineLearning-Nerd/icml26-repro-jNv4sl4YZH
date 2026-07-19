"""Cheap launch-contract checks for the unmodified author protocols."""

from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = "Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974"


def run_preflight(script: str, flag: str) -> dict[str, object]:
    result = subprocess.run(
        [
            sys.executable,
            f"repro/src/{script}",
            "--source", "upstream",
            "--output-dir", "outputs/raw/preflight",
            flag,
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def load_ccp_runner():
    spec = importlib.util.spec_from_file_location(
        "run_author_ccp", ROOT / "repro/src/run_author_ccp.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_ca_runner():
    spec = importlib.util.spec_from_file_location(
        "run_author_ca", ROOT / "repro/src/run_author_ca.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AuthorRunnerPreflightTests(unittest.TestCase):
    def test_ccp_seed_checkpoint_accepts_complete_cells_and_rejects_partial_cells(self):
        runner = load_ccp_runner()
        protocol = {
            "source": SOURCE,
            "datasets": {"boston": 15},
            "seeds": list(runner.SEEDS),
            "models": list(runner.MODELS),
            "methods": [name for name, _ in runner.METHOD_KEYS],
            "alpha": 0.1,
            "grid_points": 300,
        }
        rows = [
            {
                "dataset_key": "boston",
                "dataset": "Boston",
                "folds": 15,
                "seed": 45,
                "model": model,
                "method": method,
                "coverage": 0.9,
                "length": 1.0,
            }
            for model in runner.MODELS
            for method, _ in runner.METHOD_KEYS
        ]
        self.assertEqual(runner.validated_completed_seeds(rows, "boston", 15), {45})
        with self.assertRaises(RuntimeError):
            runner.validated_completed_seeds(rows[:-1], "boston", 15)
        with self.assertRaises(RuntimeError):
            runner.validated_completed_seeds(
                [{**rows[0], "coverage": float("nan")}, *rows[1:]],
                "boston",
                15,
            )
        with tempfile.TemporaryDirectory() as temp:
            checkpoint = Path(temp) / ".boston.partial.json"
            runner.write_checkpoint(checkpoint, protocol, "boston", 15, rows)
            self.assertEqual(
                runner.load_checkpoint(checkpoint, protocol, "boston", 15), rows
            )
            all_rows = [
                {**row, "seed": seed}
                for seed in runner.SEEDS
                for row in rows
            ]
            completed = Path(temp) / "boston.json"
            runner.write_completed_output(
                completed, protocol, "boston", 15, all_rows
            )
            self.assertEqual(
                runner.load_completed_output(
                    completed, protocol, "boston", 15
                ),
                all_rows,
            )
            runner.write_json_atomic(
                completed,
                {
                    "protocol": protocol,
                    "dataset_key": "boston",
                    "folds": 15,
                    "rows": all_rows[:-1],
                },
            )
            with self.assertRaises(RuntimeError):
                runner.load_completed_output(completed, protocol, "boston", 15)

            class TinyLoader:
                @staticmethod
                def load_dataset(_dataset_key):
                    import numpy as np

                    return (
                        np.arange(8, dtype=float).reshape(4, 2),
                        np.arange(4, dtype=float),
                        {
                            "name": "Boston",
                            "n_train": 2,
                            "n_test": 2,
                            "ntree": 3,
                            "lambda_": 0.01,
                        },
                    )

            class TinyFunctions:
                @staticmethod
                def _result(**_kwargs):
                    return {
                        key: [(0.0, 0.0), (1.0, 1.0)]
                        for _, key in runner.METHOD_KEYS
                    }

                cc_ols = _result
                cc_rf = _result
                cc_lasso = _result

                @staticmethod
                def cov_int(interval, _truth):
                    return float("nan") if interval[0] == 0.0 else 1.0

                @staticmethod
                def len_int(interval):
                    return float("nan") if interval[0] == 0.0 else 2.0

            original_seeds = runner.SEEDS
            runner.SEEDS = (45,)
            try:
                mini_protocol = {**protocol, "seeds": [45]}
                source_rows = runner.run_dataset(
                    "boston",
                    15,
                    TinyLoader,
                    TinyFunctions,
                    protocol=mini_protocol,
                    checkpoint=Path(temp) / ".tiny.partial.json",
                    existing_rows=[],
                )
            finally:
                runner.SEEDS = original_seeds
            self.assertEqual(len(source_rows), 39)
            self.assertTrue(all(row["coverage"] == 1.0 for row in source_rows))
            self.assertTrue(all(row["length"] == 2.0 for row in source_rows))

    def test_ca_dry_run_uses_released_full_protocol_and_portable_provenance(self):
        protocol = run_preflight("run_author_ca.py", "--dry-run")
        self.assertEqual(protocol["source"], SOURCE)
        self.assertEqual(protocol["task_ids"], [361237, 361235, 361244, 361234])
        self.assertEqual(len(protocol["seeds"]), 20)
        self.assertEqual((protocol["alpha"], protocol["M"], protocol["B"]), (0.05, 512, 500))
        self.assertNotIn(str(ROOT), json.dumps(protocol))
        runner = load_ca_runner()
        rows = [
            {
                "Dataset": "dataset_361237",
                "Seed": 42,
                "Method": method,
                "Coverage": 0.95,
                "Avg Length": 1.0,
            }
            for method in runner.EXPECTED_METHODS
        ]
        self.assertEqual(
            runner.validated_completed_seeds(rows, "dataset_361237", [42]),
            {42},
        )
        with self.assertRaises(RuntimeError):
            runner.validated_completed_seeds(rows[:-1], "dataset_361237", [42])
        mini_protocol = {
            **protocol,
            "tasks": ["dataset_361237"],
            "task_ids": [361237],
            "seeds": [42],
        }
        with tempfile.TemporaryDirectory() as temp:
            checkpoint = Path(temp) / ".dataset_361237.partial.json"
            runner.write_checkpoint(
                checkpoint, mini_protocol, "dataset_361237", rows
            )
            self.assertEqual(
                runner.load_checkpoint(
                    checkpoint, mini_protocol, "dataset_361237"
                ),
                rows,
            )
            completed = Path(temp) / "dataset_361237.json"
            runner.write_completed_output(
                completed, mini_protocol, "dataset_361237", rows
            )
            self.assertEqual(
                runner.load_completed_output(
                    completed, mini_protocol, "dataset_361237"
                ),
                rows,
            )

    def test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts(self):
        result = run_preflight("run_author_ccp.py", "--input-check")
        self.assertEqual(result["protocol"]["source"], SOURCE)
        self.assertEqual(
            result["inputs"],
            {
                "boston": {"folds": 15, "n_rows": 506, "n_features": 14, "n_train": 400},
                "abalone": {"folds": 15, "n_rows": 4177, "n_features": 10, "n_train": 4000},
                "parkinson": {"folds": 20, "n_rows": 5875, "n_features": 13, "n_train": 3000},
            },
        )
        self.assertNotIn(str(ROOT), json.dumps(result))


if __name__ == "__main__":
    unittest.main()
