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
    def test_vectorized_aggregation_matches_scalar_oracle_at_paper_fold_counts(self):
        import numpy as np

        runner = load_ccp_runner()
        source_path = ROOT / "upstream/e-ccp/eccp_utils.py"
        spec = importlib.util.spec_from_file_location(
            "pinned_eccp_utils_scalar_oracle", source_path
        )
        assert spec and spec.loader
        functions = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(functions)

        def normalized(intervals):
            return [
                None if value is None else np.asarray(value).tolist()
                for value in intervals
            ]

        for folds, m, seed in ((15, 26, 1), (15, 266, 2), (20, 150, 3)):
            rng = np.random.default_rng(seed)
            grid = np.linspace(-3.0, 3.0, 41)
            p_values = rng.integers(
                1, m + 2, size=(len(grid), folds, 7)
            ).astype(float) / (m + 1.0)
            # Include draws close to relevant rejection boundaries as well as
            # generic uniform values.
            u_values = rng.random(7)
            u_values[:3] = np.array([0.1, 0.2, 0.5])
            vectorized = runner.intervals_from_p_values(
                p_values,
                grid,
                functions=functions,
                alpha=0.1,
                m=m,
                used=m * folds,
                u_values=u_values,
            )

            scalar_arrays = {
                key: np.empty((len(grid), 7), dtype=float)
                for key in (
                    "int_cc", "int_cce", "int_ccu", "int_cceu", "int_ccs",
                    "int_cc_eval", "int_cc_ev_exch", "int_cc_ev_exch_U",
                    "int_cc_eval_2alpha", "int_cc_eval_ind",
                    "int_cc_eval_sqrt", "int_cc_eval_log",
                    "int_cc_eval_pow", "int_cc_eval_linear",
                )
            }
            c1, s1 = functions.get_C_s(0.1, m)
            c2, s2 = functions.get_C_s(0.2, m)
            for test_index, u_value in enumerate(u_values):
                for grid_index in range(len(grid)):
                    values = p_values[grid_index, :, test_index]
                    cumulative_p = np.cumsum(values) / np.arange(1, folds + 1)
                    p_mean = np.mean(values)
                    scalar_arrays["int_cc"][grid_index, test_index] = p_mean
                    scalar_arrays["int_cce"][grid_index, test_index] = np.min(cumulative_p)
                    scalar_arrays["int_ccu"][grid_index, test_index] = p_mean / (2.0 - u_value)
                    scalar_arrays["int_cceu"][grid_index, test_index] = min(
                        values[0] / (2.0 - u_value), np.min(cumulative_p)
                    )
                    scalar_arrays["int_ccs"][grid_index, test_index] = (
                        1.0 + np.sum(values * (m + 1.0) - 1.0)
                    ) / (m * folds + 1.0)

                    e_values = functions.f_p_to_e(values, 0.1, c1, s1)
                    cumulative_e = np.cumsum(e_values) / np.arange(1, folds + 1)
                    scalar_arrays["int_cc_eval"][grid_index, test_index] = np.mean(e_values) / u_value
                    scalar_arrays["int_cc_ev_exch"][grid_index, test_index] = np.max(cumulative_e)
                    scalar_arrays["int_cc_ev_exch_U"][grid_index, test_index] = max(
                        np.max(cumulative_e), e_values[0] / u_value
                    )
                    scalar_arrays["int_cc_eval_2alpha"][grid_index, test_index] = (
                        np.mean(functions.f_p_to_e(values, 0.2, c2, s2)) / u_value
                    )
                    scalar_arrays["int_cc_eval_ind"][grid_index, test_index] = np.mean(
                        (values <= 0.1).astype(float) / 0.1
                    ) / u_value
                    scalar_arrays["int_cc_eval_sqrt"][grid_index, test_index] = np.mean(
                        values ** (-0.5) - 1.0
                    ) / u_value
                    scalar_arrays["int_cc_eval_log"][grid_index, test_index] = np.mean(
                        -np.log(values)
                    ) / u_value
                    scalar_arrays["int_cc_eval_pow"][grid_index, test_index] = np.mean(
                        5.0 * (1.0 - values) ** 4
                    ) / u_value
                    scalar_arrays["int_cc_eval_linear"][grid_index, test_index] = np.mean(
                        2.0 * (1.0 - values)
                    ) / u_value

            p_keys = {"int_cc", "int_cce", "int_ccu", "int_cceu", "int_ccs"}
            for key, values in scalar_arrays.items():
                level = 0.2 if key == "int_cc_eval_2alpha" else 0.1
                expected = [
                    (
                        functions.set_cc(values[:, index], grid, 0.1)
                        if key in p_keys
                        else functions.set_cc_eval(values[:, index], grid, level)
                    )
                    for index in range(values.shape[1])
                ]
                self.assertEqual(
                    normalized(vectorized[key]),
                    normalized(expected),
                    f"K={folds},m={m},{key}",
                )

    def test_vectorized_ccp_adapter_matches_all_literal_source_model_paths(self):
        import numpy as np

        runner = load_ccp_runner()
        source_path = ROOT / "upstream/e-ccp/eccp_utils.py"
        spec = importlib.util.spec_from_file_location(
            "pinned_eccp_utils_vectorized_parity", source_path
        )
        assert spec and spec.loader
        functions = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(functions)

        rng = np.random.default_rng(20260719)
        x_train = rng.normal(size=(36, 4))
        y_train = (
            0.8 * x_train[:, 0]
            - 0.3 * x_train[:, 1]
            + 0.1 * x_train[:, 2] ** 2
            + rng.normal(scale=0.08, size=36)
        )
        x_test = rng.normal(size=(5, 4))
        config = {"ntree": 5, "lambda_": 0.01}

        def normalized(intervals):
            return [
                None if value is None else np.asarray(value).tolist()
                for value in intervals
            ]

        for model in runner.MODELS:
            literal = runner.call_literal_author_model(
                model,
                functions,
                y_train,
                x_train,
                x_test,
                k=3,
                alpha=0.1,
                config=config,
                seed=45,
                n_grid=37,
            )
            vectorized = runner.call_vectorized_author_model(
                model,
                functions,
                y_train,
                x_train,
                x_test,
                k=3,
                alpha=0.1,
                config=config,
                seed=45,
                n_grid=37,
            )
            np.testing.assert_array_equal(vectorized["ys"], literal["ys"])
            np.testing.assert_array_equal(vectorized["p_vals"], literal["p_vals"])
            for _, interval_key in runner.METHOD_KEYS:
                self.assertEqual(
                    normalized(vectorized[interval_key]),
                    normalized(literal[interval_key]),
                    f"{model}/{interval_key}",
                )

    def test_ccp_rng_replay_matches_real_source_power_intervals(self):
        import numpy as np

        runner = load_ccp_runner()
        source_path = ROOT / "upstream/e-ccp/eccp_utils.py"
        spec = importlib.util.spec_from_file_location("pinned_eccp_utils", source_path)
        assert spec and spec.loader
        functions = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(functions)

        rng = np.random.default_rng(2026)
        x_train = rng.normal(size=(30, 3))
        y_train = 0.7 * x_train[:, 0] - 0.2 * x_train[:, 1] + rng.normal(
            scale=0.1, size=30
        )
        x_test = rng.normal(size=(4, 3))
        seed = 45
        alpha = 0.1
        folds = 3
        result = functions.cc_ols(
            y=y_train,
            X=x_train,
            x_test=x_test,
            K=folds,
            alpha=alpha,
            n_grid=31,
            grid_factor=1.0,
            random_state=seed,
        )

        replay = np.random.default_rng(seed)
        replay.permutation(len(y_train))
        u_values = replay.random(len(x_test))
        p_values = np.asarray(result["p_vals"])
        source_power_merged = (5.0 * (1.0 - p_values) ** 4).mean(axis=1) / u_values[None, :]
        expected_power_intervals = [
            functions.set_cc_eval(source_power_merged[:, index], result["ys"], alpha)
            for index in range(len(x_test))
        ]

        def normalized(intervals):
            return [None if value is None else np.asarray(value).tolist() for value in intervals]

        self.assertEqual(
            normalized(result["int_cc_eval_pow"]),
            normalized(expected_power_intervals),
        )
        corrected = runner.attach_paper_linear_calibrator(
            result,
            functions,
            n_train=len(y_train),
            k=folds,
            alpha=alpha,
            seed=seed,
        )
        self.assertEqual(len(corrected["int_cc_eval_linear"]), len(x_test))
        paper_linear_merged = (2.0 * (1.0 - p_values)).mean(axis=1) / u_values[None, :]
        self.assertGreater(
            float(np.max(np.abs(source_power_merged - paper_linear_merged))), 0.1
        )

    def test_ccp_wrapper_reconstructs_the_paper_f3_linear_calibrator(self):
        import numpy as np

        runner = load_ccp_runner()
        p_values = np.array(
            [
                [[0.10, 0.20], [0.30, 0.40]],
                [[0.50, 0.60], [0.70, 0.80]],
                [[0.90, 1.00], [0.20, 0.30]],
            ],
            dtype=float,
        )
        grid = np.array([-1.0, 0.0, 1.0])

        class IntervalFunctions:
            @staticmethod
            def set_cc_eval(e_values, y_values, alpha):
                return tuple(np.asarray(y_values)[np.asarray(e_values) < 1.0 / alpha])

        result = runner.attach_paper_linear_calibrator(
            {"p_vals": p_values, "ys": grid},
            IntervalFunctions,
            n_train=7,
            k=2,
            alpha=0.1,
            seed=45,
        )
        rng = np.random.default_rng(45)
        rng.permutation(7)
        u_values = rng.random(2)
        expected_e_values = (2.0 * (1.0 - p_values)).mean(axis=1) / u_values[None, :]
        expected = [
            IntervalFunctions.set_cc_eval(expected_e_values[:, index], grid, 0.1)
            for index in range(2)
        ]
        self.assertEqual(result["int_cc_eval_linear"], expected)
        source_power = 5.0 * (1.0 - p_values) ** 4
        self.assertGreater(float(np.max(np.abs(source_power - 2.0 * (1.0 - p_values)))), 0.1)

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
                    model_runner=lambda *_args, **_kwargs: TinyFunctions._result(),
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
            result["protocol"]["execution_adapter"],
            "vectorized-exact-postprocessing-v1",
        )
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
