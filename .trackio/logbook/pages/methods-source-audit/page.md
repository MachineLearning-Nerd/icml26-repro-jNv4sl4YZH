# Methods & source audit


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_9458ae2f6635", "created_at": "2026-07-18T12:24:40+00:00", "title": "Pinned source and inputs"}
-->
Official source: `Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974`. The CA input tasks `361234`, `361235`, `361237`, and `361244` were queried successfully from OpenML. Boston, Abalone, and Parkinson/UPDRS CCP inputs are bundled in the author tree. Python `3.12.13` environment uses direct snapshot `numpy 2.5.1`, `scipy 1.18.0`, `pandas 2.3.3`, `scikit-learn 1.9.0`, and `openml 0.15.1`. Pandas is deliberately pinned below 3 because the released Parkinson loader assigns standardized floats into integer-backed columns; Pandas 3 rejects that formerly permitted assignment.


---
<!-- trackio-cell
{"type": "code", "id": "cell_56fcbb1f159b", "created_at": "2026-07-18T12:31:29+00:00", "title": "Fresh protocol and mechanism test suite", "command": ["python", "-m", "unittest", "discover", "-s", "repro/tests", "-v"], "exit_code": 0, "duration_s": 0.324}
-->
````bash
$ python -m unittest discover -s repro/tests -v
````

exit 0 · 0.3s


````output
test_exact_enumerations_pass_and_invalid_control_fails (test_e_merge_coverage.EMergeCoverageTests.test_exact_enumerations_pass_and_invalid_control_fails) ... ok
test_expected_ccp_raw_cell_count (test_full_protocol.FullProtocolTests.test_expected_ccp_raw_cell_count) ... ok
test_protocol_matches_released_paper_scale (test_full_protocol.FullProtocolTests.test_protocol_matches_released_paper_scale) ... ok
test_classic_calibrator_controls_expand_the_set (test_p2e_identity.P2EIdentityTests.test_classic_calibrator_controls_expand_the_set) ... ok
test_full_grid_summary_passes (test_p2e_identity.P2EIdentityTests.test_full_grid_summary_passes) ... ok
test_p2e_exactly_preserves_each_finite_rank_set (test_p2e_identity.P2EIdentityTests.test_p2e_exactly_preserves_each_finite_rank_set) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.154s

OK

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_e3aa743f5f54", "created_at": "2026-07-18T12:36:37+00:00", "title": "Author launcher and bundled-data compatibility suite", "command": ["python", "-m", "unittest", "discover", "-s", "repro/tests", "-v"], "exit_code": 0, "duration_s": 3.741}
-->
````bash
$ python -m unittest discover -s repro/tests -v
````

exit 0 · 3.7s


````output
test_ca_dry_run_uses_released_full_protocol_and_portable_provenance (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ca_dry_run_uses_released_full_protocol_and_portable_provenance) ... ok
test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts) ... ok
test_exact_enumerations_pass_and_invalid_control_fails (test_e_merge_coverage.EMergeCoverageTests.test_exact_enumerations_pass_and_invalid_control_fails) ... ok
test_expected_ccp_raw_cell_count (test_full_protocol.FullProtocolTests.test_expected_ccp_raw_cell_count) ... ok
test_protocol_matches_released_paper_scale (test_full_protocol.FullProtocolTests.test_protocol_matches_released_paper_scale) ... ok
test_classic_calibrator_controls_expand_the_set (test_p2e_identity.P2EIdentityTests.test_classic_calibrator_controls_expand_the_set) ... ok
test_full_grid_summary_passes (test_p2e_identity.P2EIdentityTests.test_full_grid_summary_passes) ... ok
test_p2e_exactly_preserves_each_finite_rank_set (test_p2e_identity.P2EIdentityTests.test_p2e_exactly_preserves_each_finite_rank_set) ... ok

----------------------------------------------------------------------
Ran 8 tests in 3.618s

OK

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_08ee035de220", "created_at": "2026-07-18T12:38:35+00:00", "title": "Released CA OpenML input preflight", "command": ["python", "repro/src/run_author_ca.py", "--source", "upstream", "--output-dir", "outputs/raw/author_ca", "--input-check"], "exit_code": 0, "duration_s": 2.101}
-->
````bash
$ python repro/src/run_author_ca.py --source upstream --output-dir outputs/raw/author_ca --input-check
````

exit 0 · 2.1s


````python title=run_author_ca.py
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
import subprocess
import sys
from pathlib import Path


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
    (output_dir / "protocol.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for dataset_name, task_id in tasks:
        output = output_dir / f"{dataset_name}.json"
        if output.exists() and not args.force:
            print(f"resume: retaining completed {output.name}")
            continue
        rows = author_main.run_one_dataset(
            dataset_name=dataset_name,
            dataset_config=task_id,
            seeds=config.seeds,
            alpha=config.alpha,
            M=config.M,
            B=config.B,
        )
        payload = {"metadata": metadata, "dataset": dataset_name, "rows": rows}
        output.write_text(
            json.dumps(payload, default=json_default, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"completed {dataset_name}: {len(rows)} raw rows -> {output}")


if __name__ == "__main__":
    main()

````


````output
{"inputs": {"dataset_361234": {"n_features": 7, "n_rows": 4177, "retained_rows": 4177}, "dataset_361235": {"n_features": 5, "n_rows": 1503, "retained_rows": 1503}, "dataset_361237": {"n_features": 8, "n_rows": 1030, "retained_rows": 1030}, "dataset_361244": {"n_features": 2, "n_rows": 1066, "retained_rows": 1066}}, "protocol": {"B": 500, "M": 512, "alpha": 0.05, "seeds": [42, 0, 1, 7, 10, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71], "source": "Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974", "task_ids": [361237, 361235, 361244, 361234], "tasks": ["dataset_361237", "dataset_361235", "dataset_361244", "dataset_361234"]}}

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_dee668277f35", "created_at": "2026-07-18T12:41:20+00:00", "title": "Independent raw-verifier completeness controls", "command": ["python", "-m", "unittest", "discover", "-s", "repro/tests", "-v"], "exit_code": 0, "duration_s": 4.696}
-->
````bash
$ python -m unittest discover -s repro/tests -v
````

exit 0 · 4.7s


````output
test_ca_dry_run_uses_released_full_protocol_and_portable_provenance (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ca_dry_run_uses_released_full_protocol_and_portable_provenance) ... ok
test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts) ... ok
test_exact_enumerations_pass_and_invalid_control_fails (test_e_merge_coverage.EMergeCoverageTests.test_exact_enumerations_pass_and_invalid_control_fails) ... ok
test_expected_ccp_raw_cell_count (test_full_protocol.FullProtocolTests.test_expected_ccp_raw_cell_count) ... ok
test_protocol_matches_released_paper_scale (test_full_protocol.FullProtocolTests.test_protocol_matches_released_paper_scale) ... ok
test_classic_calibrator_controls_expand_the_set (test_p2e_identity.P2EIdentityTests.test_classic_calibrator_controls_expand_the_set) ... ok
test_full_grid_summary_passes (test_p2e_identity.P2EIdentityTests.test_full_grid_summary_passes) ... ok
test_p2e_exactly_preserves_each_finite_rank_set (test_p2e_identity.P2EIdentityTests.test_p2e_exactly_preserves_each_finite_rank_set) ... ok
test_ca_verifier_requires_each_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ca_verifier_requires_each_method_seed_cell) ... ok
test_ccp_verifier_requires_each_model_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ccp_verifier_requires_each_model_method_seed_cell) ... ok

----------------------------------------------------------------------
Ran 10 tests in 4.512s

OK

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_227eb925f5d2", "created_at": "2026-07-18T12:49:31+00:00", "title": "Paper-headline comparison and drift control", "command": ["python", "-m", "unittest", "discover", "-s", "repro/tests", "-v"], "exit_code": 0, "duration_s": 4.042}
-->
````bash
$ python -m unittest discover -s repro/tests -v
````

exit 0 · 4.0s


````output
test_ca_dry_run_uses_released_full_protocol_and_portable_provenance (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ca_dry_run_uses_released_full_protocol_and_portable_provenance) ... ok
test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts) ... ok
test_exact_enumerations_pass_and_invalid_control_fails (test_e_merge_coverage.EMergeCoverageTests.test_exact_enumerations_pass_and_invalid_control_fails) ... ok
test_expected_ccp_raw_cell_count (test_full_protocol.FullProtocolTests.test_expected_ccp_raw_cell_count) ... ok
test_protocol_matches_released_paper_scale (test_full_protocol.FullProtocolTests.test_protocol_matches_released_paper_scale) ... ok
test_classic_calibrator_controls_expand_the_set (test_p2e_identity.P2EIdentityTests.test_classic_calibrator_controls_expand_the_set) ... ok
test_full_grid_summary_passes (test_p2e_identity.P2EIdentityTests.test_full_grid_summary_passes) ... ok
test_p2e_exactly_preserves_each_finite_rank_set (test_p2e_identity.P2EIdentityTests.test_p2e_exactly_preserves_each_finite_rank_set) ... ok
test_ca_verifier_requires_each_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ca_verifier_requires_each_method_seed_cell) ... ok
test_ccp_verifier_requires_each_model_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ccp_verifier_requires_each_model_method_seed_cell) ... ok
test_paper_headline_comparison_reports_matching_and_drifted_cells (test_raw_verifiers.RawVerifierTests.test_paper_headline_comparison_reports_matching_and_drifted_cells) ... ok

----------------------------------------------------------------------
Ran 11 tests in 3.904s

OK

````


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_d48f487509ba", "created_at": "2026-07-19T13:25:01+00:00", "title": "CCP F3 paper/source drift and correction"}
-->
The paper defines its third classical CCP p-to-e calibrator as `F3(p)=2(1-p)` in Section 2.1 and Appendix Tables 6–8. The pinned released `e-ccp/eccp_utils.py` instead exposes `int_cc_eval_pow` computed from `5(1-p)^4`. This reproduction does not relabel that different source formula. It leaves every author estimator, split, foldwise p-value, seed, fold count, grid, and randomization stream unchanged, then reconstructs the paper-specified F3 intervals as `ECCP(linear)` from the returned author p-values. The scored protocol remains 13 methods and exactly 11,700 seed/model/method cells. A unit falsifier numerically distinguishes the two formulas.


---
<!-- trackio-cell
{"type": "code", "id": "cell_55ac7e834387", "created_at": "2026-07-19T13:25:09+00:00", "title": "Corrected CCP calibrator and full gate suite", "command": ["python", "-m", "unittest", "discover", "-s", "repro/tests", "-v"], "exit_code": 0, "duration_s": 6.959}
-->
````bash
$ python -m unittest discover -s repro/tests -v
````

exit 0 · 7.0s


````output
test_ca_dry_run_uses_released_full_protocol_and_portable_provenance (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ca_dry_run_uses_released_full_protocol_and_portable_provenance) ... ok
test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts) ... ok
test_ccp_seed_checkpoint_accepts_complete_cells_and_rejects_partial_cells (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_seed_checkpoint_accepts_complete_cells_and_rejects_partial_cells) ... boston: completed seed 45
ok
test_ccp_wrapper_reconstructs_the_paper_f3_linear_calibrator (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_wrapper_reconstructs_the_paper_f3_linear_calibrator) ... ok
test_exact_enumerations_pass_and_invalid_control_fails (test_e_merge_coverage.EMergeCoverageTests.test_exact_enumerations_pass_and_invalid_control_fails) ... ok
test_lp_rejects_invalid_weight_vectors (test_e_merge_coverage.EMergeCoverageTests.test_lp_rejects_invalid_weight_vectors) ... ok
test_two_fold_lp_matches_independent_permutation_enumeration (test_e_merge_coverage.EMergeCoverageTests.test_two_fold_lp_matches_independent_permutation_enumeration) ... ok
test_expected_ccp_raw_cell_count (test_full_protocol.FullProtocolTests.test_expected_ccp_raw_cell_count) ... ok
test_final_logbook_renderer_fails_closed_and_emits_gate_marker (test_full_protocol.FullProtocolTests.test_final_logbook_renderer_fails_closed_and_emits_gate_marker) ... ok
test_official_jury_claim_snapshot_has_three_claims_and_six_points (test_full_protocol.FullProtocolTests.test_official_jury_claim_snapshot_has_three_claims_and_six_points) ... ok
test_protocol_matches_released_paper_scale (test_full_protocol.FullProtocolTests.test_protocol_matches_released_paper_scale) ... ok
test_publication_metadata_and_local_artifact_hygiene (test_full_protocol.FullProtocolTests.test_publication_metadata_and_local_artifact_hygiene) ... ok
test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json (test_full_protocol.FullProtocolTests.test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json) ... ok
test_classic_calibrator_controls_expand_the_set (test_p2e_identity.P2EIdentityTests.test_classic_calibrator_controls_expand_the_set) ... ok
test_full_grid_summary_passes (test_p2e_identity.P2EIdentityTests.test_full_grid_summary_passes) ... ok
test_p2e_exactly_preserves_each_finite_rank_set (test_p2e_identity.P2EIdentityTests.test_p2e_exactly_preserves_each_finite_rank_set) ... ok
test_ca_verifier_requires_each_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ca_verifier_requires_each_method_seed_cell) ... ok
test_ccp_verifier_requires_each_model_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ccp_verifier_requires_each_model_method_seed_cell) ... ok
test_paper_headline_comparison_reports_matching_and_drifted_cells (test_raw_verifiers.RawVerifierTests.test_paper_headline_comparison_reports_matching_and_drifted_cells) ... ok

----------------------------------------------------------------------
Ran 19 tests in 6.333s

OK

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_616ea8d9b7db", "created_at": "2026-07-19T13:26:45+00:00", "title": "Pinned-source CCP randomization replay", "command": ["python", "-m", "unittest", "-v", "repro.tests.test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_rng_replay_matches_real_source_power_intervals"], "exit_code": 0, "duration_s": 1.59}
-->
````bash
$ python -m unittest -v repro.tests.test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_rng_replay_matches_real_source_power_intervals
````

exit 0 · 1.6s


````output
test_ccp_rng_replay_matches_real_source_power_intervals (repro.tests.test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_rng_replay_matches_real_source_power_intervals) ... ok

----------------------------------------------------------------------
Ran 1 test in 1.367s

OK

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_d86aaed01837", "created_at": "2026-07-19T13:29:06+00:00", "title": "Exact-method and two-application efficiency gate suite", "command": ["python", "-m", "unittest", "discover", "-s", "repro/tests", "-v"], "exit_code": 0, "duration_s": 7.505}
-->
````bash
$ python -m unittest discover -s repro/tests -v
````

exit 0 · 7.5s


````output
test_ca_dry_run_uses_released_full_protocol_and_portable_provenance (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ca_dry_run_uses_released_full_protocol_and_portable_provenance) ... ok
test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts) ... ok
test_ccp_rng_replay_matches_real_source_power_intervals (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_rng_replay_matches_real_source_power_intervals) ... ok
test_ccp_seed_checkpoint_accepts_complete_cells_and_rejects_partial_cells (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_seed_checkpoint_accepts_complete_cells_and_rejects_partial_cells) ... boston: completed seed 45
ok
test_ccp_wrapper_reconstructs_the_paper_f3_linear_calibrator (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_wrapper_reconstructs_the_paper_f3_linear_calibrator) ... ok
test_exact_enumerations_pass_and_invalid_control_fails (test_e_merge_coverage.EMergeCoverageTests.test_exact_enumerations_pass_and_invalid_control_fails) ... ok
test_lp_rejects_invalid_weight_vectors (test_e_merge_coverage.EMergeCoverageTests.test_lp_rejects_invalid_weight_vectors) ... ok
test_two_fold_lp_matches_independent_permutation_enumeration (test_e_merge_coverage.EMergeCoverageTests.test_two_fold_lp_matches_independent_permutation_enumeration) ... ok
test_expected_ccp_raw_cell_count (test_full_protocol.FullProtocolTests.test_expected_ccp_raw_cell_count) ... ok
test_final_logbook_renderer_fails_closed_and_emits_gate_marker (test_full_protocol.FullProtocolTests.test_final_logbook_renderer_fails_closed_and_emits_gate_marker) ... ok
test_official_jury_claim_snapshot_has_three_claims_and_six_points (test_full_protocol.FullProtocolTests.test_official_jury_claim_snapshot_has_three_claims_and_six_points) ... ok
test_protocol_matches_released_paper_scale (test_full_protocol.FullProtocolTests.test_protocol_matches_released_paper_scale) ... ok
test_publication_metadata_and_local_artifact_hygiene (test_full_protocol.FullProtocolTests.test_publication_metadata_and_local_artifact_hygiene) ... ok
test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json (test_full_protocol.FullProtocolTests.test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json) ... ok
test_classic_calibrator_controls_expand_the_set (test_p2e_identity.P2EIdentityTests.test_classic_calibrator_controls_expand_the_set) ... ok
test_full_grid_summary_passes (test_p2e_identity.P2EIdentityTests.test_full_grid_summary_passes) ... ok
test_p2e_exactly_preserves_each_finite_rank_set (test_p2e_identity.P2EIdentityTests.test_p2e_exactly_preserves_each_finite_rank_set) ... ok
test_ca_verifier_requires_each_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ca_verifier_requires_each_method_seed_cell) ... ok
test_ccp_verifier_requires_each_model_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ccp_verifier_requires_each_model_method_seed_cell) ... ok
test_paper_headline_comparison_reports_matching_and_drifted_cells (test_raw_verifiers.RawVerifierTests.test_paper_headline_comparison_reports_matching_and_drifted_cells) ... ok

----------------------------------------------------------------------
Ran 20 tests in 6.890s

OK

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_05caf6cce5a6", "created_at": "2026-07-19T13:33:15+00:00", "title": "Complete 392-scalar paper-table gate", "command": ["python", "-m", "unittest", "discover", "-s", "repro/tests", "-v"], "exit_code": 0, "duration_s": 9.962}
-->
````bash
$ python -m unittest discover -s repro/tests -v
````

exit 0 · 10.0s


````output
test_ca_dry_run_uses_released_full_protocol_and_portable_provenance (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ca_dry_run_uses_released_full_protocol_and_portable_provenance) ... ok
test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts) ... ok
test_ccp_rng_replay_matches_real_source_power_intervals (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_rng_replay_matches_real_source_power_intervals) ... ok
test_ccp_seed_checkpoint_accepts_complete_cells_and_rejects_partial_cells (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_seed_checkpoint_accepts_complete_cells_and_rejects_partial_cells) ... boston: completed seed 45
ok
test_ccp_wrapper_reconstructs_the_paper_f3_linear_calibrator (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_wrapper_reconstructs_the_paper_f3_linear_calibrator) ... ok
test_exact_enumerations_pass_and_invalid_control_fails (test_e_merge_coverage.EMergeCoverageTests.test_exact_enumerations_pass_and_invalid_control_fails) ... ok
test_lp_rejects_invalid_weight_vectors (test_e_merge_coverage.EMergeCoverageTests.test_lp_rejects_invalid_weight_vectors) ... ok
test_two_fold_lp_matches_independent_permutation_enumeration (test_e_merge_coverage.EMergeCoverageTests.test_two_fold_lp_matches_independent_permutation_enumeration) ... ok
test_expected_ccp_raw_cell_count (test_full_protocol.FullProtocolTests.test_expected_ccp_raw_cell_count) ... ok
test_final_logbook_renderer_fails_closed_and_emits_gate_marker (test_full_protocol.FullProtocolTests.test_final_logbook_renderer_fails_closed_and_emits_gate_marker) ... ok
test_official_jury_claim_snapshot_has_three_claims_and_six_points (test_full_protocol.FullProtocolTests.test_official_jury_claim_snapshot_has_three_claims_and_six_points) ... ok
test_protocol_matches_released_paper_scale (test_full_protocol.FullProtocolTests.test_protocol_matches_released_paper_scale) ... ok
test_publication_metadata_and_local_artifact_hygiene (test_full_protocol.FullProtocolTests.test_publication_metadata_and_local_artifact_hygiene) ... ok
test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json (test_full_protocol.FullProtocolTests.test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json) ... ok
test_classic_calibrator_controls_expand_the_set (test_p2e_identity.P2EIdentityTests.test_classic_calibrator_controls_expand_the_set) ... ok
test_full_grid_summary_passes (test_p2e_identity.P2EIdentityTests.test_full_grid_summary_passes) ... ok
test_p2e_exactly_preserves_each_finite_rank_set (test_p2e_identity.P2EIdentityTests.test_p2e_exactly_preserves_each_finite_rank_set) ... ok
test_ca_verifier_requires_each_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ca_verifier_requires_each_method_seed_cell) ... ok
test_ccp_verifier_requires_each_model_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ccp_verifier_requires_each_model_method_seed_cell) ... ok
test_paper_headline_comparison_reports_matching_and_drifted_cells (test_raw_verifiers.RawVerifierTests.test_paper_headline_comparison_reports_matching_and_drifted_cells) ... ok

----------------------------------------------------------------------
Ran 20 tests in 9.134s

OK

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_d33060a58c6b", "created_at": "2026-07-19T13:45:10+00:00", "title": "Parity-checked CCP vectorization benchmark", "command": ["python", "repro/src/benchmark_ccp_postprocessing.py", "--source", "upstream"], "exit_code": 0, "duration_s": 2.009}
-->
````bash
$ python repro/src/benchmark_ccp_postprocessing.py --source upstream
````

exit 0 · 2.0s


````python title=benchmark_ccp_postprocessing.py
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

````


````output
{"literal_seconds": 0.32446587714366615, "max_abs_error": 1.4210854715202004e-14, "projected_parkinson_literal_kernel_hours": 7.773661639900335, "projected_parkinson_vectorized_kernel_hours": 0.2797201787567853, "projection_scope": "calibrator kernel only; excludes model fitting and interval extraction", "shape": {"folds": 20, "grid_points": 300, "test_points": 10}, "speedup": 27.79085039359809, "vectorized_seconds": 0.011675277026370168}

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_167eaa1d956c", "created_at": "2026-07-19T13:45:36+00:00", "title": "Vectorized CCP parity and adversarial audit", "command": ["python", "-m", "unittest", "discover", "-s", "repro/tests", "-v"], "exit_code": 0, "duration_s": 8.424}
-->
````bash
$ python -m unittest discover -s repro/tests -v
````

exit 0 · 8.4s


````output
test_ca_dry_run_uses_released_full_protocol_and_portable_provenance (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ca_dry_run_uses_released_full_protocol_and_portable_provenance) ... ok
test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts) ... ok
test_ccp_rng_replay_matches_real_source_power_intervals (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_rng_replay_matches_real_source_power_intervals) ... ok
test_ccp_seed_checkpoint_accepts_complete_cells_and_rejects_partial_cells (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_seed_checkpoint_accepts_complete_cells_and_rejects_partial_cells) ... boston: completed seed 45
ok
test_ccp_wrapper_reconstructs_the_paper_f3_linear_calibrator (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_wrapper_reconstructs_the_paper_f3_linear_calibrator) ... ok
test_vectorized_aggregation_matches_scalar_oracle_at_paper_fold_counts (test_author_runner_preflight.AuthorRunnerPreflightTests.test_vectorized_aggregation_matches_scalar_oracle_at_paper_fold_counts) ... ok
test_vectorized_ccp_adapter_matches_all_literal_source_model_paths (test_author_runner_preflight.AuthorRunnerPreflightTests.test_vectorized_ccp_adapter_matches_all_literal_source_model_paths) ... ok
test_exact_enumerations_pass_and_invalid_control_fails (test_e_merge_coverage.EMergeCoverageTests.test_exact_enumerations_pass_and_invalid_control_fails) ... ok
test_lp_rejects_invalid_weight_vectors (test_e_merge_coverage.EMergeCoverageTests.test_lp_rejects_invalid_weight_vectors) ... ok
test_two_fold_lp_matches_independent_permutation_enumeration (test_e_merge_coverage.EMergeCoverageTests.test_two_fold_lp_matches_independent_permutation_enumeration) ... ok
test_expected_ccp_raw_cell_count (test_full_protocol.FullProtocolTests.test_expected_ccp_raw_cell_count) ... ok
test_final_logbook_renderer_fails_closed_and_emits_gate_marker (test_full_protocol.FullProtocolTests.test_final_logbook_renderer_fails_closed_and_emits_gate_marker) ... ok
test_official_jury_claim_snapshot_has_three_claims_and_six_points (test_full_protocol.FullProtocolTests.test_official_jury_claim_snapshot_has_three_claims_and_six_points) ... ok
test_protocol_matches_released_paper_scale (test_full_protocol.FullProtocolTests.test_protocol_matches_released_paper_scale) ... ok
test_publication_metadata_and_local_artifact_hygiene (test_full_protocol.FullProtocolTests.test_publication_metadata_and_local_artifact_hygiene) ... ok
test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json (test_full_protocol.FullProtocolTests.test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json) ... ok
test_classic_calibrator_controls_expand_the_set (test_p2e_identity.P2EIdentityTests.test_classic_calibrator_controls_expand_the_set) ... ok
test_full_grid_summary_passes (test_p2e_identity.P2EIdentityTests.test_full_grid_summary_passes) ... ok
test_p2e_exactly_preserves_each_finite_rank_set (test_p2e_identity.P2EIdentityTests.test_p2e_exactly_preserves_each_finite_rank_set) ... ok
test_ca_verifier_requires_each_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ca_verifier_requires_each_method_seed_cell) ... ok
test_ccp_verifier_requires_each_model_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ccp_verifier_requires_each_model_method_seed_cell) ... ok
test_paper_headline_comparison_reports_matching_and_drifted_cells (test_raw_verifiers.RawVerifierTests.test_paper_headline_comparison_reports_matching_and_drifted_cells) ... ok

----------------------------------------------------------------------
Ran 22 tests in 7.734s

OK

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_7eaabb5bf6ef", "created_at": "2026-07-19T13:58:30+00:00", "title": "Exact CCP parity and full-scope gate", "command": [".venv/bin/python", "-m", "unittest", "discover", "-s", "repro/tests", "-v"], "exit_code": 0, "duration_s": 8.345}
-->
````bash
$ .venv/bin/python -m unittest discover -s repro/tests -v
````

exit 0 · 8.3s


````output
test_ca_dry_run_uses_released_full_protocol_and_portable_provenance (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ca_dry_run_uses_released_full_protocol_and_portable_provenance) ... ok
test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts) ... ok
test_ccp_rng_replay_matches_real_source_power_intervals (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_rng_replay_matches_real_source_power_intervals) ... ok
test_ccp_seed_checkpoint_accepts_complete_cells_and_rejects_partial_cells (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_seed_checkpoint_accepts_complete_cells_and_rejects_partial_cells) ... boston: completed seed 45
ok
test_ccp_wrapper_reconstructs_the_paper_f3_linear_calibrator (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_wrapper_reconstructs_the_paper_f3_linear_calibrator) ... ok
test_vectorized_aggregation_matches_scalar_oracle_at_paper_fold_counts (test_author_runner_preflight.AuthorRunnerPreflightTests.test_vectorized_aggregation_matches_scalar_oracle_at_paper_fold_counts) ... ok
test_vectorized_ccp_adapter_matches_all_literal_source_model_paths (test_author_runner_preflight.AuthorRunnerPreflightTests.test_vectorized_ccp_adapter_matches_all_literal_source_model_paths) ... ok
test_exact_enumerations_pass_and_invalid_control_fails (test_e_merge_coverage.EMergeCoverageTests.test_exact_enumerations_pass_and_invalid_control_fails) ... ok
test_lp_rejects_invalid_weight_vectors (test_e_merge_coverage.EMergeCoverageTests.test_lp_rejects_invalid_weight_vectors) ... ok
test_two_fold_lp_matches_independent_permutation_enumeration (test_e_merge_coverage.EMergeCoverageTests.test_two_fold_lp_matches_independent_permutation_enumeration) ... ok
test_expected_ccp_raw_cell_count (test_full_protocol.FullProtocolTests.test_expected_ccp_raw_cell_count) ... ok
test_final_logbook_renderer_fails_closed_and_emits_gate_marker (test_full_protocol.FullProtocolTests.test_final_logbook_renderer_fails_closed_and_emits_gate_marker) ... ok
test_official_jury_claim_snapshot_has_three_claims_and_six_points (test_full_protocol.FullProtocolTests.test_official_jury_claim_snapshot_has_three_claims_and_six_points) ... ok
test_protocol_matches_released_paper_scale (test_full_protocol.FullProtocolTests.test_protocol_matches_released_paper_scale) ... ok
test_publication_metadata_and_local_artifact_hygiene (test_full_protocol.FullProtocolTests.test_publication_metadata_and_local_artifact_hygiene) ... ok
test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json (test_full_protocol.FullProtocolTests.test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json) ... ok
test_classic_calibrator_controls_expand_the_set (test_p2e_identity.P2EIdentityTests.test_classic_calibrator_controls_expand_the_set) ... ok
test_full_grid_summary_passes (test_p2e_identity.P2EIdentityTests.test_full_grid_summary_passes) ... ok
test_p2e_exactly_preserves_each_finite_rank_set (test_p2e_identity.P2EIdentityTests.test_p2e_exactly_preserves_each_finite_rank_set) ... ok
test_ca_verifier_requires_each_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ca_verifier_requires_each_method_seed_cell) ... ok
test_ccp_verifier_requires_each_model_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ccp_verifier_requires_each_model_method_seed_cell) ... ok
test_paper_headline_comparison_reports_matching_and_drifted_cells (test_raw_verifiers.RawVerifierTests.test_paper_headline_comparison_reports_matching_and_drifted_cells) ... ok

----------------------------------------------------------------------
Ran 22 tests in 7.740s

OK

````


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_06bb691e7c93", "created_at": "2026-07-19T13:58:38+00:00", "title": "CCP execution and scope contract"}
-->
The full CCP runner uses `vectorized-exact-postprocessing-v1` only after reproducing the pinned source fold permutation, OLS/RF/Lasso fits, candidate grids, foldwise p-values, and RNG draws. Literal-source parity requires bit-identical grids/p-values and exact equality for all 13 scored intervals; an independent scalar oracle also checks K=15 and K=20 aggregation. The post-CCP and prepublication gates reject any evidence unless the complete protocol exactly equals the pinned source SHA, Boston/Abalone K=15, Parkinson K=20, seeds 45-144, OLS/RF/Lasso, the ordered 13-method tuple, alpha=0.1, 300 grid points, and this adapter. Negative controls cover source, dataset, seed, model, method, alpha, grid, and adapter drift. This changes runtime only; the required result remains all 11,700 raw cells.


---
<!-- trackio-cell
{"type": "code", "id": "cell_a313e9d6b3dc", "created_at": "2026-07-19T14:32:42+00:00", "title": "Primary TeX table fixture audit", "command": [".venv/bin/python", "repro/src/verify_paper_table_fixture.py", "--output", "outputs/paper_table_fixture_audit.json"], "exit_code": 0, "duration_s": 0.538}
-->
````bash
$ .venv/bin/python repro/src/verify_paper_table_fixture.py --output outputs/paper_table_fixture_audit.json
````

exit 0 · 0.5s


````python title=verify_paper_table_fixture.py
#!/usr/bin/env python3
"""Verify the paper-number fixture directly against pinned primary arXiv TeX."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import tarfile
import urllib.request
from pathlib import Path


SOURCE_URL = "https://export.arxiv.org/e-print/2606.03600v1"
SOURCE_ARCHIVE_SHA256 = "f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db"
MAIN_TEX_SHA256 = "49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857"
DATASETS = ("boston", "abalone", "parkinson")
MODELS = ("OLS", "RF", "Lasso")
FIRST_PANEL_METHODS = (
    "cross",
    "e-mod-cross",
    "u-mod-cross",
    "eu-mod-cross",
    "ECCP (2α)",
)
SECOND_PANEL_METHODS = (
    "ECCP",
    "ECCP(ind)",
    "ECCP(log)",
    "ECCP(sqrt)",
    "ECCP(linear)",
)
PAIR_PATTERN = re.compile(
    r"\$?\s*(-?\d+(?:\.\d+)?)\s*\$?\s*\\pm\s*\$?\s*"
    r"(-?\d+(?:\.\d+)?)\s*\$?"
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_primary_tex(source_url: str = SOURCE_URL) -> tuple[bytes, bytes]:
    request = urllib.request.Request(
        source_url,
        headers={"User-Agent": "icml26-reproduction-audit/1.0"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        archive = response.read()
    if sha256_bytes(archive) != SOURCE_ARCHIVE_SHA256:
        raise RuntimeError("arXiv source archive hash drift")
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:*") as bundle:
        matches = [member for member in bundle.getmembers() if member.name == "main.tex"]
        if len(matches) != 1:
            raise RuntimeError(f"expected one main.tex, found {len(matches)}")
        extracted = bundle.extractfile(matches[0])
        if extracted is None:
            raise RuntimeError("main.tex is not a regular archive member")
        tex = extracted.read()
    if sha256_bytes(tex) != MAIN_TEX_SHA256:
        raise RuntimeError("main.tex hash drift")
    return archive, tex


def parse_pairs(line: str, expected: int) -> list[tuple[float, float]]:
    pairs = [(float(mean), float(sd)) for mean, sd in PAIR_PATTERN.findall(line)]
    if len(pairs) != expected:
        raise RuntimeError(
            f"expected {expected} mean/SD pairs, found {len(pairs)} in {line!r}"
        )
    return pairs


def parse_ca_table(tex: str) -> dict[str, dict[str, dict[str, float]]]:
    label = tex.index(r"\label{table:e-CA_results}")
    start = tex.rindex(r"\begin{table*}", 0, label)
    end = tex.index(r"\end{table*}", label)
    block = tex[start:end]
    expected_header = (
        r"Method & \multicolumn{2}{c}{361234} & \multicolumn{2}{c}{361235} & "
        r"\multicolumn{2}{c}{361237} & \multicolumn{2}{c}{361244}"
    )
    if expected_header not in block:
        raise RuntimeError("CA paper-table dataset order drift")
    dataset_keys = (
        "dataset_361234",
        "dataset_361235",
        "dataset_361237",
        "dataset_361244",
    )
    output = {dataset: {} for dataset in dataset_keys}
    for source_method, config_method in (
        ("WECA", "WECA(P2E)"),
        ("UR-WECA", "UR-WECA(P2E)"),
    ):
        rows = [
            line.strip()
            for line in block.splitlines()
            if line.strip().startswith(source_method + " &")
        ]
        if len(rows) != 1:
            raise RuntimeError(f"expected one active {source_method} paper row")
        pairs = parse_pairs(rows[0], 8)
        for index, dataset in enumerate(dataset_keys):
            coverage, length = pairs[2 * index : 2 * index + 2]
            output[dataset][config_method] = {
                "coverage_mean": coverage[0],
                "coverage_sd": coverage[1],
                "length_mean": length[0],
                "length_sd": length[1],
            }
    return output


def dataset_section(tex: str, dataset: str) -> str:
    markers = {
        "boston": ("% boston K=15", "% Abalone K=15"),
        "abalone": ("% Abalone K=15", "% parkinson K=20"),
        "parkinson": ("% parkinson K=20", r"\section{Details on the P2E calibrator}"),
    }
    start_marker, end_marker = markers[dataset]
    start = tex.index(start_marker)
    end = tex.index(end_marker, start + len(start_marker))
    return tex[start:end]


def parse_ccp_panel(
    block: str, methods: tuple[str, ...]
) -> dict[str, dict[str, dict[str, float]]]:
    output = {model: {method: {} for method in methods} for model in MODELS}
    current_model: str | None = None
    row_count = 0
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if "& Size &" not in line and "& Cov. &" not in line:
            continue
        fields = [field.strip() for field in line.split("&")]
        if fields[0] in MODELS:
            current_model = fields[0]
        if current_model is None:
            raise RuntimeError("CCP metric row appears before a base model")
        metric = fields[1]
        pairs = parse_pairs(line, len(methods))
        mean_key, sd_key = (
            ("length_mean", "length_sd")
            if metric == "Size"
            else ("coverage_mean", "coverage_sd")
        )
        for method, (mean, sd) in zip(methods, pairs):
            output[current_model][method][mean_key] = mean
            output[current_model][method][sd_key] = sd
        row_count += 1
    if row_count != len(MODELS) * 2:
        raise RuntimeError(f"expected six model/metric rows, found {row_count}")
    if not all(
        set(metrics) == {"coverage_mean", "coverage_sd", "length_mean", "length_sd"}
        for model in output.values()
        for metrics in model.values()
    ):
        raise RuntimeError("incomplete CCP method metrics")
    return output


def normalized_ccp_header(block: str) -> list[str]:
    rows = [line.strip() for line in block.splitlines() if line.strip().startswith("Base &")]
    if len(rows) != 1:
        raise RuntimeError(f"expected one CCP header, found {len(rows)}")
    fields = [field.strip() for field in rows[0].removesuffix(r"\\").split("&")]
    return [re.sub(r"_\{([0-9])\}", r"_\1", field) for field in fields]


def parse_ccp_tables(tex: str) -> dict[str, dict[str, dict[str, dict[str, float]]]]:
    output = {}
    for dataset in DATASETS:
        tables = re.findall(
            r"\\begin\{table\}\[H\](.*?)\\end\{table\}",
            dataset_section(tex, dataset),
            flags=re.DOTALL,
        )
        if len(tables) != 2:
            raise RuntimeError(f"expected two CCP panels for {dataset}, found {len(tables)}")
        expected_first_header = [
            "Base", "Metric", "CCP", "e-mod-cross", "u-mod-cross",
            "eu-mod-cross", r"ECCP$(2\alpha)$",
        ]
        expected_second_header = [
            "Base", "Metric", "ECCP", r"ECCP($F_{\text{AoN}}$)",
            r"ECCP($F_1$)", r"ECCP($F_2$)", r"ECCP($F_3$)",
        ]
        if normalized_ccp_header(tables[0]) != expected_first_header:
            raise RuntimeError(f"first CCP method order drift for {dataset}")
        if normalized_ccp_header(tables[1]) != expected_second_header:
            raise RuntimeError(f"second CCP method order drift for {dataset}")
        first = parse_ccp_panel(tables[0], FIRST_PANEL_METHODS)
        second = parse_ccp_panel(tables[1], SECOND_PANEL_METHODS)
        output[dataset] = {
            model: {**first[model], **second[model]}
            for model in MODELS
        }
    return output


def mismatch_paths(expected: object, observed: object, prefix: str = "") -> list[str]:
    if isinstance(expected, dict) and isinstance(observed, dict):
        paths = []
        for key in sorted(set(expected) | set(observed)):
            path = f"{prefix}.{key}" if prefix else str(key)
            if key not in expected or key not in observed:
                paths.append(path)
            else:
                paths.extend(mismatch_paths(expected[key], observed[key], path))
        return paths
    return [] if expected == observed else [prefix]


def audit_fixture(tex: str, config: dict[str, object]) -> dict[str, object]:
    parsed_ca = parse_ca_table(tex)
    parsed_ccp = parse_ccp_tables(tex)
    mismatches = mismatch_paths(config["conformal_aggregation"], parsed_ca)
    mismatches += mismatch_paths(config["cross_conformal"], parsed_ccp)
    ca_cells = sum(len(methods) for methods in parsed_ca.values())
    ccp_cells = sum(
        len(methods) for models in parsed_ccp.values() for methods in models.values()
    )
    return {
        "all_fields_match": not mismatches,
        "mismatch_count": len(mismatches),
        "mismatch_paths": mismatches,
        "ca_cell_count": ca_cells,
        "ccp_cell_count": ccp_cells,
        "total_cell_count": ca_cells + ccp_cells,
        "scalar_count": 4 * (ca_cells + ccp_cells),
        "parsed_values_sha256": sha256_bytes(
            json.dumps(
                {"conformal_aggregation": parsed_ca, "cross_conformal": parsed_ccp},
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("repro/configs/paper_headlines.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    archive, tex_bytes = load_primary_tex()
    config_bytes = args.config.read_bytes()
    config = json.loads(config_bytes)
    audit = audit_fixture(tex_bytes.decode("utf-8"), config)
    result = {
        "source_url": SOURCE_URL,
        "source_archive_sha256": sha256_bytes(archive),
        "main_tex_sha256": sha256_bytes(tex_bytes),
        "config_sha256": sha256_bytes(config_bytes),
        "summary": audit,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not (
        audit["all_fields_match"]
        and audit["ca_cell_count"] == 8
        and audit["ccp_cell_count"] == 90
        and audit["scalar_count"] == 392
    ):
        raise SystemExit("paper table fixture audit failed")
    print(json.dumps(audit, sort_keys=True))


if __name__ == "__main__":
    main()

````


````json title=paper_table_fixture_audit.json
{
  "config_sha256": "195b86080d3995559af433c86c1a450aca90dbd710e26155b7d7783cd43458f3",
  "main_tex_sha256": "49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857",
  "source_archive_sha256": "f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db",
  "source_url": "https://export.arxiv.org/e-print/2606.03600v1",
  "summary": {
    "all_fields_match": true,
    "ca_cell_count": 8,
    "ccp_cell_count": 90,
    "mismatch_count": 0,
    "mismatch_paths": [],
    "parsed_values_sha256": "4fc44baae9e052b59a4184aa297fe5af2aad8484c881352e3a91a616f7b50b7c",
    "scalar_count": 392,
    "total_cell_count": 98
  }
}

````


````output
{"all_fields_match": true, "ca_cell_count": 8, "ccp_cell_count": 90, "mismatch_count": 0, "mismatch_paths": [], "parsed_values_sha256": "4fc44baae9e052b59a4184aa297fe5af2aad8484c881352e3a91a616f7b50b7c", "scalar_count": 392, "total_cell_count": 98}

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_c08399629f79", "created_at": "2026-07-19T14:32:51+00:00", "title": "Primary-source-bound full gate suite", "command": [".venv/bin/python", "-m", "unittest", "discover", "-s", "repro/tests", "-v"], "exit_code": 0, "duration_s": 8.404}
-->
````bash
$ .venv/bin/python -m unittest discover -s repro/tests -v
````

exit 0 · 8.4s


````output
test_ca_dry_run_uses_released_full_protocol_and_portable_provenance (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ca_dry_run_uses_released_full_protocol_and_portable_provenance) ... ok
test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts) ... ok
test_ccp_rng_replay_matches_real_source_power_intervals (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_rng_replay_matches_real_source_power_intervals) ... ok
test_ccp_seed_checkpoint_accepts_complete_cells_and_rejects_partial_cells (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_seed_checkpoint_accepts_complete_cells_and_rejects_partial_cells) ... boston: completed seed 45
ok
test_ccp_wrapper_reconstructs_the_paper_f3_linear_calibrator (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_wrapper_reconstructs_the_paper_f3_linear_calibrator) ... ok
test_vectorized_aggregation_matches_scalar_oracle_at_paper_fold_counts (test_author_runner_preflight.AuthorRunnerPreflightTests.test_vectorized_aggregation_matches_scalar_oracle_at_paper_fold_counts) ... ok
test_vectorized_ccp_adapter_matches_all_literal_source_model_paths (test_author_runner_preflight.AuthorRunnerPreflightTests.test_vectorized_ccp_adapter_matches_all_literal_source_model_paths) ... ok
test_exact_enumerations_pass_and_invalid_control_fails (test_e_merge_coverage.EMergeCoverageTests.test_exact_enumerations_pass_and_invalid_control_fails) ... ok
test_lp_rejects_invalid_weight_vectors (test_e_merge_coverage.EMergeCoverageTests.test_lp_rejects_invalid_weight_vectors) ... ok
test_two_fold_lp_matches_independent_permutation_enumeration (test_e_merge_coverage.EMergeCoverageTests.test_two_fold_lp_matches_independent_permutation_enumeration) ... ok
test_expected_ccp_raw_cell_count (test_full_protocol.FullProtocolTests.test_expected_ccp_raw_cell_count) ... ok
test_final_logbook_renderer_fails_closed_and_emits_gate_marker (test_full_protocol.FullProtocolTests.test_final_logbook_renderer_fails_closed_and_emits_gate_marker) ... ok
test_official_jury_claim_snapshot_has_three_claims_and_six_points (test_full_protocol.FullProtocolTests.test_official_jury_claim_snapshot_has_three_claims_and_six_points) ... ok
test_paper_table_fixture_is_bound_to_primary_tex (test_full_protocol.FullProtocolTests.test_paper_table_fixture_is_bound_to_primary_tex) ... ok
test_protocol_matches_released_paper_scale (test_full_protocol.FullProtocolTests.test_protocol_matches_released_paper_scale) ... ok
test_publication_metadata_and_local_artifact_hygiene (test_full_protocol.FullProtocolTests.test_publication_metadata_and_local_artifact_hygiene) ... ok
test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json (test_full_protocol.FullProtocolTests.test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json) ... ok
test_classic_calibrator_controls_expand_the_set (test_p2e_identity.P2EIdentityTests.test_classic_calibrator_controls_expand_the_set) ... ok
test_full_grid_summary_passes (test_p2e_identity.P2EIdentityTests.test_full_grid_summary_passes) ... ok
test_p2e_exactly_preserves_each_finite_rank_set (test_p2e_identity.P2EIdentityTests.test_p2e_exactly_preserves_each_finite_rank_set) ... ok
test_ca_verifier_requires_each_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ca_verifier_requires_each_method_seed_cell) ... ok
test_ccp_verifier_requires_each_model_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ccp_verifier_requires_each_model_method_seed_cell) ... ok
test_paper_headline_comparison_reports_matching_and_drifted_cells (test_raw_verifiers.RawVerifierTests.test_paper_headline_comparison_reports_matching_and_drifted_cells) ... ok

----------------------------------------------------------------------
Ran 23 tests in 7.773s

OK

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_e739f330a9ac", "created_at": "2026-07-19T14:52:21+00:00", "title": "Exact CA and CCP protocol contracts", "command": [".venv/bin/python", "-m", "unittest", "discover", "-s", "repro/tests", "-v"], "exit_code": 0, "duration_s": 8.449}
-->
````bash
$ .venv/bin/python -m unittest discover -s repro/tests -v
````

exit 0 · 8.4s


````output
test_ca_dry_run_uses_released_full_protocol_and_portable_provenance (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ca_dry_run_uses_released_full_protocol_and_portable_provenance) ... ok
test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts) ... ok
test_ccp_rng_replay_matches_real_source_power_intervals (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_rng_replay_matches_real_source_power_intervals) ... ok
test_ccp_seed_checkpoint_accepts_complete_cells_and_rejects_partial_cells (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_seed_checkpoint_accepts_complete_cells_and_rejects_partial_cells) ... boston: completed seed 45
ok
test_ccp_wrapper_reconstructs_the_paper_f3_linear_calibrator (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_wrapper_reconstructs_the_paper_f3_linear_calibrator) ... ok
test_vectorized_aggregation_matches_scalar_oracle_at_paper_fold_counts (test_author_runner_preflight.AuthorRunnerPreflightTests.test_vectorized_aggregation_matches_scalar_oracle_at_paper_fold_counts) ... ok
test_vectorized_ccp_adapter_matches_all_literal_source_model_paths (test_author_runner_preflight.AuthorRunnerPreflightTests.test_vectorized_ccp_adapter_matches_all_literal_source_model_paths) ... ok
test_exact_enumerations_pass_and_invalid_control_fails (test_e_merge_coverage.EMergeCoverageTests.test_exact_enumerations_pass_and_invalid_control_fails) ... ok
test_lp_rejects_invalid_weight_vectors (test_e_merge_coverage.EMergeCoverageTests.test_lp_rejects_invalid_weight_vectors) ... ok
test_two_fold_lp_matches_independent_permutation_enumeration (test_e_merge_coverage.EMergeCoverageTests.test_two_fold_lp_matches_independent_permutation_enumeration) ... ok
test_exact_ca_protocol_contract (test_full_protocol.FullProtocolTests.test_exact_ca_protocol_contract) ... ok
test_expected_ccp_raw_cell_count (test_full_protocol.FullProtocolTests.test_expected_ccp_raw_cell_count) ... ok
test_final_logbook_renderer_fails_closed_and_emits_gate_marker (test_full_protocol.FullProtocolTests.test_final_logbook_renderer_fails_closed_and_emits_gate_marker) ... ok
test_official_jury_claim_snapshot_has_three_claims_and_six_points (test_full_protocol.FullProtocolTests.test_official_jury_claim_snapshot_has_three_claims_and_six_points) ... ok
test_paper_table_fixture_is_bound_to_primary_tex (test_full_protocol.FullProtocolTests.test_paper_table_fixture_is_bound_to_primary_tex) ... ok
test_protocol_matches_released_paper_scale (test_full_protocol.FullProtocolTests.test_protocol_matches_released_paper_scale) ... ok
test_publication_metadata_and_local_artifact_hygiene (test_full_protocol.FullProtocolTests.test_publication_metadata_and_local_artifact_hygiene) ... ok
test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json (test_full_protocol.FullProtocolTests.test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json) ... ok
test_classic_calibrator_controls_expand_the_set (test_p2e_identity.P2EIdentityTests.test_classic_calibrator_controls_expand_the_set) ... ok
test_full_grid_summary_passes (test_p2e_identity.P2EIdentityTests.test_full_grid_summary_passes) ... ok
test_p2e_exactly_preserves_each_finite_rank_set (test_p2e_identity.P2EIdentityTests.test_p2e_exactly_preserves_each_finite_rank_set) ... ok
test_ca_verifier_requires_each_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ca_verifier_requires_each_method_seed_cell) ... ok
test_ccp_verifier_requires_each_model_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ccp_verifier_requires_each_model_method_seed_cell) ... ok
test_paper_headline_comparison_reports_matching_and_drifted_cells (test_raw_verifiers.RawVerifierTests.test_paper_headline_comparison_reports_matching_and_drifted_cells) ... ok

----------------------------------------------------------------------
Ran 24 tests in 7.804s

OK

````


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_1e09970bfb65", "created_at": "2026-07-19T14:52:22+00:00", "title": "Exact CA scope contract"}
-->
Claim 2 raw evidence is accepted only when its complete protocol exactly equals the pinned source SHA, ordered OpenML tasks 361237/361235/361244/361234, the released 20-seed tuple, alpha=0.05, M=512, and B=500. Both the CA-to-CCP transition and final publication gate enforce this contract. Negative controls alter source, tasks, task IDs, seeds, alpha, M, and B; each is rejected, so a self-consistent reduced or changed 1,920-cell protocol cannot pass.
