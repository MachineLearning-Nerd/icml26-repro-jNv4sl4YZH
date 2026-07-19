"""Exercise the independent raw-row completeness checks with tiny fixtures."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_ca_methods() -> tuple[str, ...]:
    spec = importlib.util.spec_from_file_location(
        "verify_ca_results", ROOT / "repro/src/verify_ca_results.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.EXPECTED_METHODS


def invoke(script: str, raw_dir: Path, output: Path) -> dict[str, object]:
    subprocess.run(
        [
            sys.executable,
            f"repro/src/{script}",
            "--raw-dir", str(raw_dir),
            "--output", str(output),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(output.read_text(encoding="utf-8"))


class RawVerifierTests(unittest.TestCase):
    def test_paper_headline_comparison_reports_matching_and_drifted_cells(self):
        headlines = json.loads(
            (ROOT / "repro/configs/paper_headlines.json").read_text(encoding="utf-8")
        )
        ca = {"summaries": {}}
        for dataset, methods in headlines["conformal_aggregation"].items():
            ca["summaries"][dataset] = {
                method: dict(values) for method, values in methods.items()
            }
        ccp = {"summaries": {}}
        for dataset, models in headlines["cross_conformal"].items():
            ccp["summaries"][dataset] = {
                model: {method: dict(values) for method, values in methods.items()}
                for model, methods in models.items()
            }
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            ca_path, ccp_path, output = path / "ca.json", path / "ccp.json", path / "comparison.json"
            ca_path.write_text(json.dumps(ca), encoding="utf-8")
            ccp_path.write_text(json.dumps(ccp), encoding="utf-8")
            command = [
                sys.executable,
                "repro/src/compare_paper_headlines.py",
                "--ca", str(ca_path),
                "--ccp", str(ccp_path),
                "--output", str(output),
            ]
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
            matching = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(matching["summary"]["all_within_tolerance"])
            self.assertEqual(matching["summary"]["comparison_count"], 122)
            self.assertEqual(matching["summary"]["scalar_comparison_count"], 488)
            self.assertEqual(matching["summary"]["within_tolerance_scalar_count"], 488)
            self.assertTrue(matching["summary"]["all_unaffected_within_tolerance"])
            self.assertEqual(matching["summary"]["unaffected_comparison_count"], 95)
            self.assertEqual(matching["summary"]["unaffected_scalar_comparison_count"], 380)
            self.assertEqual(matching["summary"]["known_discrepancy_comparison_count"], 27)
            self.assertEqual(matching["summary"]["known_discrepancy_scalar_comparison_count"], 108)

            original_known = dict(
                ccp["summaries"]["boston"]["OLS"]["ECCP(log)"]
            )
            ccp["summaries"]["boston"]["OLS"]["ECCP(log)"]["length_mean"] *= 2
            ccp_path.write_text(json.dumps(ccp), encoding="utf-8")
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
            known = json.loads(output.read_text(encoding="utf-8"))
            self.assertFalse(known["summary"]["all_within_tolerance"])
            self.assertTrue(known["summary"]["all_unaffected_within_tolerance"])
            self.assertTrue(known["summary"]["all_outside_tolerance_cells_accounted_for"])
            self.assertEqual(known["summary"]["unexpected_outside_tolerance_count"], 0)
            self.assertEqual(known["summary"]["known_discrepancy_outside_tolerance_count"], 1)
            ccp["summaries"]["boston"]["OLS"]["ECCP(log)"] = original_known
            ccp_path.write_text(json.dumps(ccp), encoding="utf-8")

            ca["summaries"]["dataset_361234"]["WECA(P2E)"]["length_mean"] = 99.0
            ca_path.write_text(json.dumps(ca), encoding="utf-8")
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
            drifted = json.loads(output.read_text(encoding="utf-8"))
            self.assertFalse(drifted["summary"]["all_within_tolerance"])
            self.assertEqual(drifted["summary"]["within_tolerance_count"], 121)
            self.assertEqual(drifted["summary"]["within_tolerance_scalar_count"], 487)

            ca["summaries"]["dataset_361234"]["WECA(P2E)"] = dict(
                headlines["conformal_aggregation"]["dataset_361234"]["WECA(P2E)"]
            )
            ca["summaries"]["dataset_361234"]["WECA(P2E)"]["coverage_sd"] = 99.0
            ca_path.write_text(json.dumps(ca), encoding="utf-8")
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
            drifted_sd = json.loads(output.read_text(encoding="utf-8"))
            self.assertFalse(drifted_sd["summary"]["all_within_tolerance"])
            self.assertEqual(drifted_sd["summary"]["within_tolerance_count"], 121)
            self.assertEqual(drifted_sd["summary"]["within_tolerance_scalar_count"], 487)

            ca["summaries"]["dataset_361234"]["WECA(P2E)"] = dict(
                headlines["conformal_aggregation"]["dataset_361234"]["WECA(P2E)"]
            )
            ca["summaries"]["dataset_361234"]["WECA(P2E)"]["coverage_mean"] = float("nan")
            ca_path.write_text(json.dumps(ca), encoding="utf-8")
            with self.assertRaises(subprocess.CalledProcessError):
                subprocess.run(
                    command, cwd=ROOT, check=True, capture_output=True, text=True
                )

    def test_ca_verifier_requires_each_method_seed_cell(self):
        with tempfile.TemporaryDirectory() as temp:
            raw = Path(temp)
            protocol = {"tasks": ["toy"], "seeds": [1, 2], "alpha": 0.05}
            rows = [
                {
                    "Dataset": "toy",
                    "Method": method,
                    "Seed": seed,
                    "Coverage": 0.95,
                    "Avg Length": 0.8 if method.endswith("(P2E)") else 1.0,
                }
                for method in load_ca_methods()
                for seed in protocol["seeds"]
            ]
            (raw / "protocol.json").write_text(json.dumps(protocol), encoding="utf-8")
            payload = {"metadata": protocol, "dataset": "toy", "rows": rows}
            (raw / "toy.json").write_text(json.dumps(payload), encoding="utf-8")
            passed = invoke("verify_ca_results.py", raw, raw / "passed.json")
            self.assertTrue(passed["summary"]["all_full_seed_method_cells_present"])
            self.assertEqual(passed["summary"]["expected_rows"], 48)
            self.assertTrue(passed["summary"]["exact_cell_set"])
            self.assertEqual(passed["summary"]["duplicate_cell_count"], 0)
            self.assertEqual(passed["summary"]["unexpected_row_count"], 0)
            self.assertEqual(passed["summary"]["nonfinite_row_count"], 0)
            self.assertEqual(passed["summary"]["invalid_metric_row_count"], 0)
            self.assertEqual(passed["summary"]["comparison_count"], 6)
            self.assertEqual(passed["summary"]["p2e_shorter_count"], 6)
            self.assertEqual(
                passed["summary"]["substantial_efficiency_gain_count"], 6
            )
            self.assertTrue(passed["summary"]["all_substantial_efficiency_gains"])
            self.assertAlmostEqual(
                passed["summary"]["minimum_observed_relative_reduction"], 0.2
            )
            self.assertEqual(passed["summary"]["p2e_empirical_coverage_cell_count"], 2)
            self.assertEqual(passed["summary"]["p2e_empirical_coverage_pass_count"], 2)
            self.assertTrue(
                passed["summary"]["all_p2e_empirical_coverage_within_tolerance"]
            )

            payload["rows"] = [
                {
                    **row,
                    "Avg Length": 0.95
                    if str(row["Method"]).endswith("(P2E)")
                    else row["Avg Length"],
                }
                for row in rows
            ]
            (raw / "toy.json").write_text(json.dumps(payload), encoding="utf-8")
            merely_shorter = invoke(
                "verify_ca_results.py", raw, raw / "merely_shorter.json"
            )
            self.assertEqual(merely_shorter["summary"]["p2e_shorter_count"], 6)
            self.assertEqual(
                merely_shorter["summary"]["substantial_efficiency_gain_count"], 0
            )
            self.assertFalse(
                merely_shorter["summary"]["all_substantial_efficiency_gains"]
            )

            payload["rows"] = [
                {
                    **row,
                    "Coverage": 0.90
                    if str(row["Method"]).endswith("(P2E)")
                    else row["Coverage"],
                }
                for row in rows
            ]
            (raw / "toy.json").write_text(json.dumps(payload), encoding="utf-8")
            undercoverage = invoke(
                "verify_ca_results.py", raw, raw / "undercoverage.json"
            )
            self.assertEqual(
                undercoverage["summary"]["p2e_empirical_coverage_pass_count"], 0
            )
            self.assertFalse(
                undercoverage["summary"]["all_p2e_empirical_coverage_within_tolerance"]
            )

            invalid_range_rows = [
                {
                    **row,
                    "Coverage": 1.01 if index == 0 else row["Coverage"],
                    "Avg Length": -0.01 if index == 1 else row["Avg Length"],
                }
                for index, row in enumerate(rows)
            ]
            payload["rows"] = invalid_range_rows
            (raw / "toy.json").write_text(json.dumps(payload), encoding="utf-8")
            rejected_range = invoke(
                "verify_ca_results.py", raw, raw / "rejected_range.json"
            )
            self.assertFalse(
                rejected_range["summary"]["all_full_seed_method_cells_present"]
            )
            self.assertEqual(rejected_range["summary"]["invalid_metric_row_count"], 2)

            payload["rows"] = rows[:-1]
            (raw / "toy.json").write_text(json.dumps(payload), encoding="utf-8")
            rejected = invoke("verify_ca_results.py", raw, raw / "rejected.json")
            self.assertFalse(rejected["summary"]["all_full_seed_method_cells_present"])

            payload["rows"] = [rows[0], {**rows[0], "Coverage": float("nan")}]
            (raw / "toy.json").write_text(json.dumps(payload), encoding="utf-8")
            rejected = invoke("verify_ca_results.py", raw, raw / "rejected.json")
            self.assertFalse(rejected["summary"]["all_full_seed_method_cells_present"])
            self.assertEqual(rejected["summary"]["duplicate_cell_count"], 1)
            self.assertEqual(rejected["summary"]["nonfinite_row_count"], 1)

            payload["rows"] = rows
            payload["dataset"] = "wrong"
            (raw / "toy.json").write_text(json.dumps(payload), encoding="utf-8")
            rejected = invoke("verify_ca_results.py", raw, raw / "rejected.json")
            self.assertFalse(rejected["summary"]["all_full_seed_method_cells_present"])

    def test_ccp_verifier_requires_each_model_method_seed_cell(self):
        with tempfile.TemporaryDirectory() as temp:
            raw = Path(temp)
            methods = [
                "ECCP",
                "ECCP_exch",
                "UR-ECCP_exch",
                "ECCP(ind)",
                "ECCP(sqrt)",
                "ECCP(log)",
                "ECCP(linear)",
            ]
            protocol = {
                "datasets": {"toy": 3},
                "seeds": [45, 46],
                "models": ["OLS"],
                "methods": methods,
                "alpha": 0.1,
            }
            rows = [
                {
                    "dataset_key": "toy",
                    "folds": 3,
                    "seed": seed,
                    "model": "OLS",
                    "method": method,
                    "coverage": 0.9,
                    "length": (
                        1.0
                        if method == "ECCP"
                        else 1.1
                        if method == "ECCP(ind)"
                        else 2.0
                    ),
                }
                for seed in protocol["seeds"]
                for method in methods
            ]
            (raw / "protocol.json").write_text(json.dumps(protocol), encoding="utf-8")
            payload = {
                "protocol": protocol,
                "dataset_key": "toy",
                "folds": 3,
                "rows": rows,
            }
            (raw / "toy.json").write_text(json.dumps(payload), encoding="utf-8")
            passed = invoke("verify_ccp_results.py", raw, raw / "passed.json")
            self.assertTrue(passed["summary"]["all_full_seed_cells_present"])
            self.assertEqual(passed["summary"]["expected_rows"], 14)
            self.assertTrue(passed["summary"]["exact_cell_set"])
            self.assertEqual(passed["summary"]["duplicate_cell_count"], 0)
            self.assertEqual(passed["summary"]["unexpected_row_count"], 0)
            self.assertEqual(passed["summary"]["nonfinite_row_count"], 0)
            self.assertEqual(passed["summary"]["invalid_metric_row_count"], 0)
            self.assertEqual(passed["summary"]["eccp_empirical_coverage_cell_count"], 1)
            self.assertEqual(passed["summary"]["eccp_empirical_coverage_pass_count"], 1)
            self.assertTrue(
                passed["summary"]["all_eccp_empirical_coverage_within_tolerance"]
            )
            self.assertEqual(passed["summary"]["p2e_empirical_coverage_cell_count"], 3)
            self.assertEqual(passed["summary"]["p2e_empirical_coverage_pass_count"], 3)
            self.assertTrue(
                passed["summary"]["all_p2e_empirical_coverage_within_tolerance"]
            )
            self.assertEqual(
                passed["summary"]["calibrator_efficiency_comparison_count"], 4
            )
            self.assertEqual(passed["summary"]["p2e_strictly_shorter_count"], 4)
            self.assertTrue(
                passed["summary"]["all_p2e_not_longer_than_existing_calibrators"]
            )
            self.assertEqual(passed["summary"]["aon_strictly_shorter_count"], 1)
            self.assertTrue(
                passed["summary"]["all_p2e_strictly_shorter_than_aon"]
            )
            self.assertEqual(
                passed["summary"]["classical_substantial_gain_count"], 3
            )
            self.assertTrue(
                passed["summary"]["all_classical_efficiency_gains_substantial"]
            )

            aon_better_rows = [
                {
                    **row,
                    "length": 0.9 if row["method"] == "ECCP(ind)" else row["length"],
                }
                for row in rows
            ]
            payload["rows"] = aon_better_rows
            (raw / "toy.json").write_text(json.dumps(payload), encoding="utf-8")
            aon_failure = invoke(
                "verify_ccp_results.py", raw, raw / "aon_failure.json"
            )
            self.assertFalse(
                aon_failure["summary"]["all_p2e_not_longer_than_existing_calibrators"]
            )
            self.assertFalse(
                aon_failure["summary"]["all_p2e_strictly_shorter_than_aon"]
            )

            aon_equal_rows = [
                {
                    **row,
                    "length": 1.0 if row["method"] == "ECCP(ind)" else row["length"],
                }
                for row in rows
            ]
            payload["rows"] = aon_equal_rows
            (raw / "toy.json").write_text(json.dumps(payload), encoding="utf-8")
            aon_equality = invoke(
                "verify_ccp_results.py", raw, raw / "aon_equality.json"
            )
            self.assertTrue(
                aon_equality["summary"]["all_p2e_not_longer_than_existing_calibrators"]
            )
            self.assertFalse(
                aon_equality["summary"]["all_p2e_strictly_shorter_than_aon"]
            )

            weak_classical_rows = [
                {
                    **row,
                    "length": (
                        1.05
                        if row["method"] in {"ECCP(sqrt)", "ECCP(log)", "ECCP(linear)"}
                        else row["length"]
                    ),
                }
                for row in rows
            ]
            payload["rows"] = weak_classical_rows
            (raw / "toy.json").write_text(json.dumps(payload), encoding="utf-8")
            weak_classical = invoke(
                "verify_ccp_results.py", raw, raw / "weak_classical.json"
            )
            self.assertEqual(
                weak_classical["summary"]["classical_substantial_gain_count"], 0
            )
            self.assertFalse(
                weak_classical["summary"]["all_classical_efficiency_gains_substantial"]
            )

            payload["rows"] = [{**row, "coverage": 0.85} for row in rows]
            (raw / "toy.json").write_text(json.dumps(payload), encoding="utf-8")
            undercoverage = invoke(
                "verify_ccp_results.py", raw, raw / "undercoverage.json"
            )
            self.assertEqual(
                undercoverage["summary"]["eccp_empirical_coverage_pass_count"], 0
            )
            self.assertFalse(
                undercoverage["summary"]["all_eccp_empirical_coverage_within_tolerance"]
            )
            self.assertEqual(
                undercoverage["summary"]["p2e_empirical_coverage_pass_count"], 0
            )
            self.assertFalse(
                undercoverage["summary"]["all_p2e_empirical_coverage_within_tolerance"]
            )

            invalid_range_rows = [
                {
                    **row,
                    "coverage": 1.01 if index == 0 else row["coverage"],
                    "length": -0.01 if index == 1 else row["length"],
                }
                for index, row in enumerate(rows)
            ]
            payload["rows"] = invalid_range_rows
            (raw / "toy.json").write_text(json.dumps(payload), encoding="utf-8")
            rejected_range = invoke(
                "verify_ccp_results.py", raw, raw / "rejected_range.json"
            )
            self.assertFalse(rejected_range["summary"]["all_full_seed_cells_present"])
            self.assertEqual(rejected_range["summary"]["invalid_metric_row_count"], 2)

            payload["rows"] = rows[:-1]
            (raw / "toy.json").write_text(json.dumps(payload), encoding="utf-8")
            rejected = invoke("verify_ccp_results.py", raw, raw / "rejected.json")
            self.assertFalse(rejected["summary"]["all_full_seed_cells_present"])

            payload["rows"] = [rows[0], {**rows[0], "coverage": float("nan")}]
            (raw / "toy.json").write_text(json.dumps(payload), encoding="utf-8")
            rejected = invoke("verify_ccp_results.py", raw, raw / "rejected.json")
            self.assertFalse(rejected["summary"]["all_full_seed_cells_present"])
            self.assertEqual(rejected["summary"]["duplicate_cell_count"], 1)
            self.assertEqual(rejected["summary"]["nonfinite_row_count"], 1)

            payload["rows"] = rows
            payload["folds"] = 4
            (raw / "toy.json").write_text(json.dumps(payload), encoding="utf-8")
            rejected = invoke("verify_ccp_results.py", raw, raw / "rejected.json")
            self.assertFalse(rejected["summary"]["all_full_seed_cells_present"])


if __name__ == "__main__":
    unittest.main()
