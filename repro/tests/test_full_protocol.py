import json
import tempfile
import unittest
from pathlib import Path

from repro.src.prepublish_gate import (
    hygiene_gate,
    sha256,
    validate_local_path_artifacts,
    write_artifact_bundle,
)
from repro.src.render_final_logbook import build_cells
from repro.src.run_author_ccp import METHOD_KEYS, PAPER_DATASETS


class FullProtocolTests(unittest.TestCase):
    def test_official_jury_claim_snapshot_has_three_claims_and_six_points(self):
        root = Path(__file__).resolve().parents[2]
        jury = json.loads(
            (root / "repro/configs/jury_claims.json").read_text(encoding="utf-8")
        )
        self.assertEqual(jury["openreview_id"], "jNv4sl4YZH")
        self.assertEqual(jury["maximum_points"], 6)
        self.assertEqual([claim["claim"] for claim in jury["claims"]], [1, 2, 3])
        self.assertEqual(
            [claim["possible_points"] for claim in jury["claims"]], [2, 2, 2]
        )
        self.assertEqual(
            [claim["text"] for claim in jury["claims"]],
            [
                "P2E calibrator converts conformal p-values to e-values without altering the induced prediction set",
                "Yields substantial efficiency gains over existing p-to-e methods in conformal inference",
                "Enables exact 1-α coverage in cross-conformal prediction and conformal aggregation",
            ],
        )

    def test_publication_metadata_and_local_artifact_hygiene(self):
        root = Path(__file__).resolve().parents[2]
        metadata = json.loads((root / ".trackio/metadata.json").read_text())
        self.assertEqual(
            metadata["paper"],
            {"arxiv_id": "2606.03600", "openreview_id": "jNv4sl4YZH"},
        )
        gitignore_lines = (root / ".gitignore").read_text().splitlines()
        self.assertIn(".trackio/metadata.json", gitignore_lines)
        self.assertIn("upstream/", gitignore_lines)
        self.assertNotIn("upstream/.git/", gitignore_lines)
        self.assertEqual(hygiene_gate()["absolute_path_hits"], [])

        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            artifact = directory / "outputs/evidence.jsonl"
            artifact.parent.mkdir()
            artifact.write_text("{}\n", encoding="utf-8")
            valid = {
                "local_path_artifacts": [
                    {
                        "path": "outputs/evidence.jsonl",
                        "abs_path": str(artifact),
                    }
                ]
            }
            self.assertEqual(validate_local_path_artifacts(valid, directory), 1)
            valid["local_path_artifacts"][0]["abs_path"] = str(directory / "wrong")
            with self.assertRaises(AssertionError):
                validate_local_path_artifacts(valid, directory)

    def test_protocol_matches_released_paper_scale(self):
        root = Path(__file__).resolve().parents[2]
        protocol = json.loads((root / "repro/configs/full_protocol.json").read_text())
        self.assertEqual(protocol["claim_2_conformal_aggregation"]["seeds"], 20)
        self.assertEqual(protocol["claim_2_conformal_aggregation"]["openml_task_ids"], [361234, 361235, 361237, 361244])
        self.assertEqual(protocol["claim_3_cross_conformal"]["seeds"], 100)
        self.assertEqual(PAPER_DATASETS, {"boston": 15, "abalone": 15, "parkinson": 20})
        self.assertEqual(len(METHOD_KEYS), 13)

    def test_expected_ccp_raw_cell_count(self):
        self.assertEqual(len(PAPER_DATASETS) * 3 * len(METHOD_KEYS) * 100, 11700)

    def test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory(dir=root / "outputs") as temp:
            directory = Path(temp)
            source = directory / "source.json"
            bundle = directory / "bundle.jsonl"
            source.write_text(json.dumps({"claim": 3, "passed": True}), encoding="utf-8")
            source_relative = str(source.relative_to(root))
            bundle_relative = str(bundle.relative_to(root))
            bundle_hash = write_artifact_bundle(bundle_relative, (source_relative,))
            record = json.loads(bundle.read_text(encoding="utf-8"))
            self.assertEqual(record["path"], source_relative)
            self.assertEqual(record["sha256"], sha256(source_relative))
            self.assertEqual(record["payload"], {"claim": 3, "passed": True})
            self.assertEqual(bundle_hash, sha256(bundle_relative))

    def test_final_logbook_renderer_fails_closed_and_emits_gate_marker(self):
        claim1 = {
            "summary": {
                "all_set_identities_pass": True,
                "all_exact_e_expectations_pass": True,
                "all_positive_pass": True,
                "all_classic_controls_inflate_sets": True,
                "case_count": 18,
                "classic_control_case_count": 17,
            },
            "cases": [{"expectation_abs_error": 1e-15}],
        }
        claim2 = {
            "rows_seen": 1_920,
            "summary": {
                "all_four_tasks_present": True,
                "all_full_seed_method_cells_present": True,
                "exact_cell_set": True,
                "expected_rows": 1_920,
                "comparison_count": 24,
                "p2e_shorter_count": 24,
            },
            "efficiency_comparisons": [
                {"absolute_reduction": 9.0, "baseline_length": 10.0}
                for _ in range(24)
            ],
            "summaries": {
                f"dataset_{task}": {
                    "WECA(P2E)": {"coverage_mean": 0.95},
                    "UR-WECA(P2E)": {"coverage_mean": 0.95},
                }
                for task in (361234, 361235, 361237, 361244)
            },
        }
        mechanism = {
            "summary": {
                "all_merged_expectations_exact": True,
                "all_markov_coverage_events_pass": True,
                "all_arbitrary_dependence_coverage_pass": True,
                "invalid_scaling_control_detected": True,
                "invalid_arbitrary_dependence_detected": True,
                "adaptive_weight_control_detected": True,
                "invalid_scaling_control_rejection_count": 2,
                "invalid_arbitrary_dependence_rejection_count": 6,
                "adaptive_weight_rejection_count": 6,
                "maximum_valid_tail_to_alpha_ratio": 0.95,
            }
        }
        claim3 = {
            "rows_seen": 11_700,
            "summary": {
                "all_full_seed_cells_present": True,
                "exact_cell_set": True,
                "expected_rows": 11_700,
            },
            "summaries": {
                dataset: {
                    model: {"ECCP": {"coverage_mean": 0.9}}
                    for model in ("OLS", "RF", "Lasso")
                }
                for dataset in ("boston", "abalone", "parkinson")
            },
        }
        headlines = {
            "summary": {
                "all_within_tolerance": True,
                "comparison_count": 17,
                "scalar_comparison_count": 68,
                "within_tolerance_scalar_count": 68,
            }
        }

        cells = build_cells(claim1, claim2, mechanism, claim3, headlines)
        self.assertIn("FULL_GATE_READY: jNv4sl4YZH", cells["conclusion"])
        self.assertIn("24/24", cells["claim_2"])
        self.assertEqual(cells["summary"]["headline_scalars"], 68)

        claim2["summary"]["p2e_shorter_count"] = 23
        with self.assertRaises(RuntimeError):
            build_cells(claim1, claim2, mechanism, claim3, headlines)
