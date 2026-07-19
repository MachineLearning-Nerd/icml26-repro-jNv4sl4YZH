import json
import tempfile
import unittest
from pathlib import Path

from repro.src.prepublish_gate import (
    EXPECTED_CA_PROTOCOL,
    EXPECTED_CCP_PROTOCOL,
    assert_exact_ca_protocol,
    assert_exact_ccp_protocol,
    hygiene_gate,
    sha256,
    validate_artifact_bundle,
    validate_local_path_artifacts,
    validate_required_local_artifact,
    write_artifact_bundle,
)
from repro.src.render_final_logbook import build_cells
from repro.src.run_author_ccp import EXECUTION_ADAPTER, METHOD_KEYS, PAPER_DATASETS
from repro.src.verify_ccp_results import CALIBRATOR_BASELINES
from repro.src.verify_paper_table_fixture import (
    MAIN_TEX_SHA256,
    SOURCE_ARCHIVE_SHA256,
    SOURCE_URL,
    mismatch_paths,
)


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
            valid["local_path_artifacts"][0]["size"] = artifact.stat().st_size
            valid["local_path_artifacts"][0]["artifact_type"] = "dataset"
            self.assertEqual(
                validate_required_local_artifact(
                    valid, "outputs/evidence.jsonl", directory
                )["path"],
                "outputs/evidence.jsonl",
            )
            valid["local_path_artifacts"][0]["size"] += 1
            with self.assertRaises(AssertionError):
                validate_required_local_artifact(
                    valid, "outputs/evidence.jsonl", directory
                )
            valid["local_path_artifacts"][0]["size"] = artifact.stat().st_size
            valid["local_path_artifacts"][0]["abs_path"] = str(directory / "wrong")
            with self.assertRaises(AssertionError):
                validate_local_path_artifacts(valid, directory)

    def test_shared_queue_handoff_follows_initial_github_push(self):
        root = Path(__file__).resolve().parents[2]
        publisher = (root / "repro/src/publish_after_gate.sh").read_text(
            encoding="utf-8"
        )
        initial_push = publisher.index('git push -u origin main')
        enqueue = publisher.index('scripts/enqueue_backlog.py')
        wait_for_space = publisher.index('until hf spaces info "$hf_space"')
        self.assertLess(initial_push, enqueue)
        self.assertLess(enqueue, wait_for_space)

    def test_protocol_matches_released_paper_scale(self):
        root = Path(__file__).resolve().parents[2]
        protocol = json.loads((root / "repro/configs/full_protocol.json").read_text())
        self.assertEqual(protocol["claim_2_conformal_aggregation"]["seeds"], 20)
        self.assertEqual(protocol["claim_2_conformal_aggregation"]["openml_task_ids"], [361234, 361235, 361237, 361244])
        self.assertEqual(protocol["claim_3_cross_conformal"]["seeds"], 100)
        self.assertEqual(PAPER_DATASETS, {"boston": 15, "abalone": 15, "parkinson": 20})
        self.assertEqual(
            tuple(name for name, _ in METHOD_KEYS),
            (
                "mod-cross",
                "e-mod-cross",
                "u-mod-cross",
                "eu-mod-cross",
                "cross",
                "ECCP",
                "ECCP_exch",
                "UR-ECCP_exch",
                "ECCP(ind)",
                "ECCP(sqrt)",
                "ECCP(log)",
                "ECCP(linear)",
                "ECCP (2α)",
            ),
        )
        self.assertEqual(
            CALIBRATOR_BASELINES,
            {
                "AoN": "ECCP(ind)",
                "sqrt": "ECCP(sqrt)",
                "log": "ECCP(log)",
                "linear": "ECCP(linear)",
            },
        )

        headlines = json.loads(
            (root / "repro/configs/paper_headlines.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            headlines["source"],
            "arXiv:2606.03600, Table 2 and Appendix Tables 6-8",
        )
        self.assertEqual(
            {
                key: headlines["comparison_policy"][key]
                for key in (
                    "coverage_absolute_tolerance",
                    "coverage_sd_absolute_tolerance",
                    "length_relative_tolerance",
                    "length_sd_relative_tolerance",
                )
            },
            {
                "coverage_absolute_tolerance": 0.01,
                "coverage_sd_absolute_tolerance": 0.01,
                "length_relative_tolerance": 0.05,
                "length_sd_relative_tolerance": 0.10,
            },
        )
        self.assertEqual(
            sum(len(methods) for methods in headlines["conformal_aggregation"].values()),
            8,
        )
        self.assertEqual(
            sum(
                len(methods)
                for models in headlines["cross_conformal"].values()
                for methods in models.values()
            ),
            90,
        )

    def test_expected_ccp_raw_cell_count(self):
        self.assertEqual(len(PAPER_DATASETS) * 3 * len(METHOD_KEYS) * 100, 11700)
        self.assertEqual(EXECUTION_ADAPTER, "vectorized-exact-postprocessing-v1")
        expected = {
            "source": "Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974",
            "datasets": PAPER_DATASETS,
            "seeds": list(range(45, 145)),
            "models": ["OLS", "RF", "Lasso"],
            "methods": [name for name, _ in METHOD_KEYS],
            "alpha": 0.1,
            "grid_points": 300,
            "execution_adapter": EXECUTION_ADAPTER,
        }
        self.assertEqual(EXPECTED_CCP_PROTOCOL, expected)
        assert_exact_ccp_protocol(expected)
        for key, drifted_value in (
            ("source", "Nabil-Ala/P2E_calibration@wrong-sha"),
            ("datasets", {"boston": 15, "abalone": 15}),
            ("seeds", list(range(45, 144))),
            ("models", ["OLS", "RF"]),
            ("methods", expected["methods"][:-1]),
            ("alpha", 0.2),
            ("grid_points", 299),
            ("execution_adapter", "literal-source"),
        ):
            with self.subTest(key=key), self.assertRaises(AssertionError):
                assert_exact_ccp_protocol({**expected, key: drifted_value})

    def test_exact_ca_protocol_contract(self):
        expected = {
            "source": "Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974",
            "tasks": [
                "dataset_361237",
                "dataset_361235",
                "dataset_361244",
                "dataset_361234",
            ],
            "task_ids": [361237, 361235, 361244, 361234],
            "seeds": [
                42, 0, 1, 7, 10, 13, 17, 19, 23, 29,
                31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
            ],
            "alpha": 0.05,
            "M": 512,
            "B": 500,
        }
        self.assertEqual(EXPECTED_CA_PROTOCOL, expected)
        assert_exact_ca_protocol(expected)
        for key, drifted_value in (
            ("source", "Nabil-Ala/P2E_calibration@wrong-sha"),
            ("tasks", expected["tasks"][:-1]),
            ("task_ids", expected["task_ids"][:-1]),
            ("seeds", expected["seeds"][:-1]),
            ("alpha", 0.10),
            ("M", 256),
            ("B", 250),
        ):
            with self.subTest(key=key), self.assertRaises(AssertionError):
                assert_exact_ca_protocol({**expected, key: drifted_value})

    def test_paper_table_fixture_is_bound_to_primary_tex(self):
        root = Path(__file__).resolve().parents[2]
        audit = json.loads(
            (root / "outputs/paper_table_fixture_audit.json").read_text(encoding="utf-8")
        )
        self.assertEqual(audit["source_url"], SOURCE_URL)
        self.assertEqual(audit["source_archive_sha256"], SOURCE_ARCHIVE_SHA256)
        self.assertEqual(audit["main_tex_sha256"], MAIN_TEX_SHA256)
        self.assertEqual(
            audit["config_sha256"],
            sha256("repro/configs/paper_headlines.json"),
        )
        self.assertEqual(
            audit["summary"],
            {
                "all_fields_match": True,
                "ca_cell_count": 8,
                "ccp_cell_count": 90,
                "mismatch_count": 0,
                "mismatch_paths": [],
                "parsed_values_sha256": "4fc44baae9e052b59a4184aa297fe5af2aad8484c881352e3a91a616f7b50b7c",
                "scalar_count": 392,
                "total_cell_count": 98,
            },
        )
        self.assertEqual(mismatch_paths({"cell": 1.0}, {"cell": 2.0}), ["cell"])
        self.assertEqual(mismatch_paths({"cell": 1.0}, {"cell": 1.0}), [])

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
            self.assertEqual(
                validate_artifact_bundle(bundle_relative, (source_relative,)),
                bundle_hash,
            )

            source.write_text(
                json.dumps({"claim": 3, "passed": False}), encoding="utf-8"
            )
            with self.assertRaises(AssertionError):
                validate_artifact_bundle(bundle_relative, (source_relative,))

            source.write_text(
                json.dumps({"claim": 3, "passed": True}), encoding="utf-8"
            )
            tampered = json.loads(bundle.read_text(encoding="utf-8"))
            tampered["payload"]["passed"] = False
            bundle.write_text(json.dumps(tampered) + "\n", encoding="utf-8")
            with self.assertRaises(AssertionError):
                validate_artifact_bundle(bundle_relative, (source_relative,))

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
                "substantial_efficiency_gain_count": 24,
                "all_substantial_efficiency_gains": True,
                "all_p2e_empirical_coverage_within_tolerance": True,
                "p2e_empirical_coverage_cell_count": 8,
                "p2e_empirical_coverage_pass_count": 8,
                "empirical_coverage_shortfall_tolerance": 0.02,
                "minimum_substantial_relative_reduction": 0.10,
                "minimum_observed_relative_reduction": 0.90,
            },
            "efficiency_comparisons": [
                {
                    "absolute_reduction": 9.0,
                    "baseline_length": 10.0,
                    "relative_reduction": 0.90,
                }
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
                "case_count": 8,
                "equal_weight_case_count": 2,
                "nonuniform_weight_case_count": 6,
                "all_merged_expectations_exact": True,
                "all_markov_coverage_events_pass": True,
                "all_arbitrary_dependence_coverage_pass": True,
                "invalid_scaling_control_detected": True,
                "invalid_arbitrary_dependence_detected": True,
                "adaptive_weight_control_detected": True,
                "invalid_scaling_control_rejection_count": 2,
                "invalid_arbitrary_dependence_rejection_count": 4,
                "adaptive_weight_rejection_count": 8,
                "maximum_valid_tail_to_alpha_ratio": 0.95,
            }
        }
        claim3 = {
            "protocol": {"execution_adapter": "vectorized-exact-postprocessing-v1"},
            "rows_seen": 11_700,
            "summary": {
                "all_full_seed_cells_present": True,
                "exact_cell_set": True,
                "all_eccp_empirical_coverage_within_tolerance": True,
                "all_p2e_not_longer_than_existing_calibrators": True,
                "all_p2e_strictly_shorter_than_aon": True,
                "all_classical_efficiency_gains_substantial": True,
                "eccp_empirical_coverage_cell_count": 9,
                "eccp_empirical_coverage_pass_count": 9,
                "empirical_coverage_shortfall_tolerance": 0.02,
                "expected_rows": 11_700,
                "calibrator_efficiency_comparison_count": 36,
                "p2e_not_longer_count": 36,
                "p2e_strictly_shorter_count": 36,
                "aon_comparison_count": 9,
                "aon_strictly_shorter_count": 9,
                "classical_comparison_count": 27,
                "classical_substantial_gain_count": 27,
                "minimum_substantial_relative_reduction": 0.10,
                "minimum_classical_relative_reduction": 0.50,
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
                "comparison_count": 98,
                "scalar_comparison_count": 392,
                "within_tolerance_scalar_count": 392,
            }
        }

        cells = build_cells(claim1, claim2, mechanism, claim3, headlines)
        self.assertIn("FULL_GATE_READY: jNv4sl4YZH", cells["conclusion"])
        self.assertIn("24/24", cells["claim_2"])
        self.assertEqual(cells["summary"]["headline_scalars"], 392)

        claim2["summary"]["p2e_shorter_count"] = 23
        with self.assertRaises(RuntimeError):
            build_cells(claim1, claim2, mechanism, claim3, headlines)
