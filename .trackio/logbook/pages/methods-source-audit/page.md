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


---
<!-- trackio-cell
{"type": "code", "id": "cell_cf51d44ea9d8", "created_at": "2026-07-19T14:57:23+00:00", "title": "Race-free shared HF queue handoff", "command": ["python", "-m", "unittest", "discover", "-s", "repro/tests", "-v"], "exit_code": 0, "duration_s": 8.486}
-->
````bash
$ python -m unittest discover -s repro/tests -v
````

exit 0 · 8.5s


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
test_shared_queue_handoff_follows_initial_github_push (test_full_protocol.FullProtocolTests.test_shared_queue_handoff_follows_initial_github_push) ... ok
test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json (test_full_protocol.FullProtocolTests.test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json) ... ok
test_classic_calibrator_controls_expand_the_set (test_p2e_identity.P2EIdentityTests.test_classic_calibrator_controls_expand_the_set) ... ok
test_full_grid_summary_passes (test_p2e_identity.P2EIdentityTests.test_full_grid_summary_passes) ... ok
test_p2e_exactly_preserves_each_finite_rank_set (test_p2e_identity.P2EIdentityTests.test_p2e_exactly_preserves_each_finite_rank_set) ... ok
test_ca_verifier_requires_each_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ca_verifier_requires_each_method_seed_cell) ... ok
test_ccp_verifier_requires_each_model_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ccp_verifier_requires_each_model_method_seed_cell) ... ok
test_paper_headline_comparison_reports_matching_and_drifted_cells (test_raw_verifiers.RawVerifierTests.test_paper_headline_comparison_reports_matching_and_drifted_cells) ... ok

----------------------------------------------------------------------
Ran 25 tests in 7.819s

OK

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_2d8d19031590", "created_at": "2026-07-19T15:00:43+00:00", "title": "Reject out-of-domain raw metrics", "command": ["python", "-m", "unittest", "discover", "-s", "repro/tests", "-v"], "exit_code": 0, "duration_s": 8.645}
-->
````bash
$ python -m unittest discover -s repro/tests -v
````

exit 0 · 8.6s


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
test_shared_queue_handoff_follows_initial_github_push (test_full_protocol.FullProtocolTests.test_shared_queue_handoff_follows_initial_github_push) ... ok
test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json (test_full_protocol.FullProtocolTests.test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json) ... ok
test_classic_calibrator_controls_expand_the_set (test_p2e_identity.P2EIdentityTests.test_classic_calibrator_controls_expand_the_set) ... ok
test_full_grid_summary_passes (test_p2e_identity.P2EIdentityTests.test_full_grid_summary_passes) ... ok
test_p2e_exactly_preserves_each_finite_rank_set (test_p2e_identity.P2EIdentityTests.test_p2e_exactly_preserves_each_finite_rank_set) ... ok
test_ca_verifier_requires_each_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ca_verifier_requires_each_method_seed_cell) ... ok
test_ccp_verifier_requires_each_model_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ccp_verifier_requires_each_model_method_seed_cell) ... ok
test_paper_headline_comparison_reports_matching_and_drifted_cells (test_raw_verifiers.RawVerifierTests.test_paper_headline_comparison_reports_matching_and_drifted_cells) ... ok

----------------------------------------------------------------------
Ran 25 tests in 7.929s

OK

````


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_9334fb20342f", "created_at": "2026-07-19T15:01:24+00:00", "title": "Raw metric domain contract"}
-->
Both resumable runners and both independent raw-artifact verifiers reject coverage outside [0,1] and negative interval length, in addition to non-finite metrics. The CA-to-CCP transition, post-CCP gate, and final publication gate explicitly require zero out-of-domain rows. Negative fixtures inject coverage 1.01, coverage -0.01, and length -0.01 in both protocols and are rejected.


---
<!-- trackio-cell
{"type": "code", "id": "cell_a944728eabf0", "created_at": "2026-07-19T15:03:41+00:00", "title": "Live jury contract drift controls", "command": ["python", "-m", "unittest", "discover", "-s", "repro/tests", "-v"], "exit_code": 0, "duration_s": 8.514}
-->
````bash
$ python -m unittest discover -s repro/tests -v
````

exit 0 · 8.5s


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
test_live_jury_contract_rejects_count_and_wording_drift (test_full_protocol.FullProtocolTests.test_live_jury_contract_rejects_count_and_wording_drift) ... ok
test_official_jury_claim_snapshot_has_three_claims_and_six_points (test_full_protocol.FullProtocolTests.test_official_jury_claim_snapshot_has_three_claims_and_six_points) ... ok
test_paper_table_fixture_is_bound_to_primary_tex (test_full_protocol.FullProtocolTests.test_paper_table_fixture_is_bound_to_primary_tex) ... ok
test_protocol_matches_released_paper_scale (test_full_protocol.FullProtocolTests.test_protocol_matches_released_paper_scale) ... ok
test_publication_metadata_and_local_artifact_hygiene (test_full_protocol.FullProtocolTests.test_publication_metadata_and_local_artifact_hygiene) ... ok
test_shared_queue_handoff_follows_initial_github_push (test_full_protocol.FullProtocolTests.test_shared_queue_handoff_follows_initial_github_push) ... ok
test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json (test_full_protocol.FullProtocolTests.test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json) ... ok
test_classic_calibrator_controls_expand_the_set (test_p2e_identity.P2EIdentityTests.test_classic_calibrator_controls_expand_the_set) ... ok
test_full_grid_summary_passes (test_p2e_identity.P2EIdentityTests.test_full_grid_summary_passes) ... ok
test_p2e_exactly_preserves_each_finite_rank_set (test_p2e_identity.P2EIdentityTests.test_p2e_exactly_preserves_each_finite_rank_set) ... ok
test_ca_verifier_requires_each_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ca_verifier_requires_each_method_seed_cell) ... ok
test_ccp_verifier_requires_each_model_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ccp_verifier_requires_each_model_method_seed_cell) ... ok
test_paper_headline_comparison_reports_matching_and_drifted_cells (test_raw_verifiers.RawVerifierTests.test_paper_headline_comparison_reports_matching_and_drifted_cells) ... ok

----------------------------------------------------------------------
Ran 26 tests in 7.842s

OK

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_047bca10865a", "created_at": "2026-07-19T15:03:43+00:00", "title": "Live jury claim refresh", "command": ["python", "-c", "from repro.src.prepublish_gate import fetch_live_jury_claims; claims=fetch_live_jury_claims(); print(f\"live_claims={len(claims)} exact_wording=true possible_points=6\")"], "exit_code": 0, "duration_s": 1.056}
-->
````bash
$ python -c 'from repro.src.prepublish_gate import fetch_live_jury_claims; claims=fetch_live_jury_claims(); print(f"live_claims={len(claims)} exact_wording=true possible_points=6")'
````

exit 0 · 1.1s


````output
live_claims=3 exact_wording=true possible_points=6

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_cfe4de2e26d8", "created_at": "2026-07-19T15:11:20+00:00", "title": "WECA independent-tuning audit", "command": ["python", "repro/src/verify_weca_independence.py", "--source", "upstream", "--output", "outputs/weca_independence_audit.json"], "exit_code": 0, "duration_s": 2.339}
-->
````bash
$ python repro/src/verify_weca_independence.py --source upstream --output outputs/weca_independence_audit.json
````

exit 0 · 2.3s


````python title=verify_weca_independence.py
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

````


````json title=weca_independence_audit.json
{
  "cases": [
    {
      "baseline_weight": [
        0.3374252443136454,
        0.3278789386574905,
        0.33469581702886425
      ],
      "final_calibration_mutation_max_abs_weight_change": 0.0,
      "illegal_test_adaptive_control_changes": true,
      "illegal_test_adaptive_weights": [
        [
          1.0,
          0.0,
          0.0
        ],
        [
          0.0,
          1.0,
          0.0
        ]
      ],
      "seed": 42,
      "split_is_disjoint_partition": true,
      "split_sizes": {
        "final_calibration": 20,
        "tuning": 10,
        "weight_calibration": 10
      },
      "test_mutation_max_abs_weight_change": 0.0
    },
    {
      "baseline_weight": [
        0.39546198954297845,
        0.5930180594914135,
        0.011519950965607977
      ],
      "final_calibration_mutation_max_abs_weight_change": 0.0,
      "illegal_test_adaptive_control_changes": true,
      "illegal_test_adaptive_weights": [
        [
          1.0,
          0.0,
          0.0
        ],
        [
          0.0,
          1.0,
          0.0
        ]
      ],
      "seed": 0,
      "split_is_disjoint_partition": true,
      "split_sizes": {
        "final_calibration": 20,
        "tuning": 10,
        "weight_calibration": 10
      },
      "test_mutation_max_abs_weight_change": 0.0
    },
    {
      "baseline_weight": [
        0.15880448167679984,
        0.04564996889225682,
        0.7955455494309432
      ],
      "final_calibration_mutation_max_abs_weight_change": 0.0,
      "illegal_test_adaptive_control_changes": true,
      "illegal_test_adaptive_weights": [
        [
          1.0,
          0.0,
          0.0
        ],
        [
          0.0,
          1.0,
          0.0
        ]
      ],
      "seed": 1,
      "split_is_disjoint_partition": true,
      "split_sizes": {
        "final_calibration": 20,
        "tuning": 10,
        "weight_calibration": 10
      },
      "test_mutation_max_abs_weight_change": 0.0
    },
    {
      "baseline_weight": [
        0.30745014424701217,
        0.4454924156641316,
        0.24705744008885633
      ],
      "final_calibration_mutation_max_abs_weight_change": 0.0,
      "illegal_test_adaptive_control_changes": true,
      "illegal_test_adaptive_weights": [
        [
          1.0,
          0.0,
          0.0
        ],
        [
          0.0,
          1.0,
          0.0
        ]
      ],
      "seed": 7,
      "split_is_disjoint_partition": true,
      "split_sizes": {
        "final_calibration": 20,
        "tuning": 10,
        "weight_calibration": 10
      },
      "test_mutation_max_abs_weight_change": 0.0
    },
    {
      "baseline_weight": [
        0.24801565616967766,
        0.14895724156125947,
        0.6030271022690629
      ],
      "final_calibration_mutation_max_abs_weight_change": 0.0,
      "illegal_test_adaptive_control_changes": true,
      "illegal_test_adaptive_weights": [
        [
          1.0,
          0.0,
          0.0
        ],
        [
          0.0,
          1.0,
          0.0
        ]
      ],
      "seed": 10,
      "split_is_disjoint_partition": true,
      "split_sizes": {
        "final_calibration": 20,
        "tuning": 10,
        "weight_calibration": 10
      },
      "test_mutation_max_abs_weight_change": 0.0
    },
    {
      "baseline_weight": [
        0.3614311367971118,
        0.29961196346993363,
        0.3389568997329545
      ],
      "final_calibration_mutation_max_abs_weight_change": 0.0,
      "illegal_test_adaptive_control_changes": true,
      "illegal_test_adaptive_weights": [
        [
          1.0,
          0.0,
          0.0
        ],
        [
          0.0,
          1.0,
          0.0
        ]
      ],
      "seed": 13,
      "split_is_disjoint_partition": true,
      "split_sizes": {
        "final_calibration": 20,
        "tuning": 10,
        "weight_calibration": 10
      },
      "test_mutation_max_abs_weight_change": 0.0
    }
  ],
  "function_contract": {
    "all_required_flow_present": true,
    "end_line": 509,
    "function": "Evalue_aggregation_weighted",
    "required_flow_checks": 11,
    "sha256": "541a30601a5346d0adbcf50bb9dcfd2e5e8317f7403fb4540516680a52751bfb",
    "start_line": 388
  },
  "methods_sha256": "dda5d2429d4ca8c77be6a3b04bb3c159360bf3af58d1087a5f31cc17ea44cf86",
  "source": "Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974",
  "summary": {
    "all_illegal_test_adaptive_controls_change": true,
    "all_required_flow_present": true,
    "all_split_partitions_disjoint": true,
    "all_weights_independent_of_final_calibration": true,
    "all_weights_independent_of_test_data_and_outcomes": true,
    "case_count": 6
  }
}

````


````output
{"all_illegal_test_adaptive_controls_change": true, "all_required_flow_present": true, "all_split_partitions_disjoint": true, "all_weights_independent_of_final_calibration": true, "all_weights_independent_of_test_data_and_outcomes": true, "case_count": 6}

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_5f37e55acef6", "created_at": "2026-07-19T15:11:29+00:00", "title": "WECA source-bound independence gate suite", "command": ["python", "-m", "unittest", "discover", "-s", "repro/tests", "-v"], "exit_code": 0, "duration_s": 8.6}
-->
````bash
$ python -m unittest discover -s repro/tests -v
````

exit 0 · 8.6s


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
test_live_jury_contract_rejects_count_and_wording_drift (test_full_protocol.FullProtocolTests.test_live_jury_contract_rejects_count_and_wording_drift) ... ok
test_official_jury_claim_snapshot_has_three_claims_and_six_points (test_full_protocol.FullProtocolTests.test_official_jury_claim_snapshot_has_three_claims_and_six_points) ... ok
test_paper_table_fixture_is_bound_to_primary_tex (test_full_protocol.FullProtocolTests.test_paper_table_fixture_is_bound_to_primary_tex) ... ok
test_protocol_matches_released_paper_scale (test_full_protocol.FullProtocolTests.test_protocol_matches_released_paper_scale) ... ok
test_publication_metadata_and_local_artifact_hygiene (test_full_protocol.FullProtocolTests.test_publication_metadata_and_local_artifact_hygiene) ... ok
test_shared_queue_handoff_follows_initial_github_push (test_full_protocol.FullProtocolTests.test_shared_queue_handoff_follows_initial_github_push) ... ok
test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json (test_full_protocol.FullProtocolTests.test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json) ... ok
test_weca_independence_audit_is_bound_to_released_source (test_full_protocol.FullProtocolTests.test_weca_independence_audit_is_bound_to_released_source) ... ok
test_classic_calibrator_controls_expand_the_set (test_p2e_identity.P2EIdentityTests.test_classic_calibrator_controls_expand_the_set) ... ok
test_full_grid_summary_passes (test_p2e_identity.P2EIdentityTests.test_full_grid_summary_passes) ... ok
test_p2e_exactly_preserves_each_finite_rank_set (test_p2e_identity.P2EIdentityTests.test_p2e_exactly_preserves_each_finite_rank_set) ... ok
test_ca_verifier_requires_each_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ca_verifier_requires_each_method_seed_cell) ... ok
test_ccp_verifier_requires_each_model_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ccp_verifier_requires_each_model_method_seed_cell) ... ok
test_paper_headline_comparison_reports_matching_and_drifted_cells (test_raw_verifiers.RawVerifierTests.test_paper_headline_comparison_reports_matching_and_drifted_cells) ... ok

----------------------------------------------------------------------
Ran 27 tests in 7.884s

OK

````


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_4802396b6bd4", "created_at": "2026-07-19T15:13:18+00:00", "title": "WECA independence result"}
-->
The audit pins methods.py SHA-256 dda5d2429d4ca8c77be6a3b04bb3c159360bf3af58d1087a5f31cc17ea44cf86 and Evalue_aggregation_weighted SHA-256 541a30601a5346d0adbcf50bb9dcfd2e5e8317f7403fb4540516680a52751bfb. Across six released seed values, i1/i2/i3 are disjoint partitions; replacing every final-calibration row or every test covariate/outcome changes the selected WECA weight by exactly 0.0. A forbidden test-outcome-adaptive selector changes in 6/6 controls. The final gate and 16-record bundle require this artifact.


---
<!-- trackio-cell
{"type": "code", "id": "cell_7486f422eef9", "created_at": "2026-07-19T15:24:13+00:00", "title": "Expanded primary TeX table fixture audit", "command": ["python", "repro/src/verify_paper_table_fixture.py", "--output", "outputs/paper_table_fixture_audit.json"], "exit_code": 0, "duration_s": 0.553}
-->
````bash
$ python repro/src/verify_paper_table_fixture.py --output outputs/paper_table_fixture_audit.json
````

exit 0 · 0.6s


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
CA_DATASET_KEYS = (
    "dataset_361234",
    "dataset_361235",
    "dataset_361237",
    "dataset_361244",
)
ALTERNATIVE_CA_METHODS = (
    (r"WECA($F_1$)", "WECA(log)"),
    (r"UR-WECA($F_1$)", "UR-WECA(log)"),
    (r"WECA($F_2$)", "WECA(sqrt)"),
    (r"UR-WECA($F_2$)", "UR-WECA(sqrt)"),
    (r"WECA($F_3$)", "WECA(linear)"),
    (r"UR-WECA($F_3$)", "UR-WECA(linear)"),
)
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
    output = {dataset: {} for dataset in CA_DATASET_KEYS}
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
        for index, dataset in enumerate(CA_DATASET_KEYS):
            coverage, length = pairs[2 * index : 2 * index + 2]
            output[dataset][config_method] = {
                "coverage_mean": coverage[0],
                "coverage_sd": coverage[1],
                "length_mean": length[0],
                "length_sd": length[1],
            }
    alternatives = parse_ca_alternative_table(tex)
    for dataset in CA_DATASET_KEYS:
        output[dataset].update(alternatives[dataset])
    return output


def parse_ca_alternative_table(
    tex: str,
) -> dict[str, dict[str, dict[str, float]]]:
    label = tex.index(r"\label{tab:weca_rotated}")
    start = tex.rindex(r"\begin{table}[t]", 0, label)
    end = tex.index(r"\end{table}", label)
    block = tex[start:end]
    if "& Method & Cov.  & Len." not in block:
        raise RuntimeError("alternative CA metric header drift")

    expected_ids = [dataset.removeprefix("dataset_") for dataset in CA_DATASET_KEYS]
    observed_ids = re.findall(r"\\textbf\{(\d+)\}", block)
    if observed_ids != expected_ids:
        raise RuntimeError(
            f"alternative CA dataset order drift: {observed_ids!r}"
        )

    method_map = dict(ALTERNATIVE_CA_METHODS)
    expected_method_order = [source for source, _ in ALTERNATIVE_CA_METHODS]
    output = {dataset: {} for dataset in CA_DATASET_KEYS}
    current_dataset: str | None = None
    observed_method_order: dict[str, list[str]] = {
        dataset: [] for dataset in CA_DATASET_KEYS
    }
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if "&" not in line or not any(source in line for source in method_map):
            continue
        dataset_match = re.search(r"\\textbf\{(\d+)\}", line)
        if dataset_match:
            current_dataset = f"dataset_{dataset_match.group(1)}"
        if current_dataset not in output:
            raise RuntimeError("alternative CA row appears before a known dataset")
        fields = [field.strip() for field in line.split("&")]
        if len(fields) != 4:
            raise RuntimeError(f"malformed alternative CA row: {line!r}")
        source_method = fields[1]
        if source_method not in method_map:
            raise RuntimeError(f"unexpected alternative CA method: {source_method!r}")
        coverage, length = parse_pairs(line, 2)
        output[current_dataset][method_map[source_method]] = {
            "coverage_mean": coverage[0],
            "coverage_sd": coverage[1],
            "length_mean": length[0],
            "length_sd": length[1],
        }
        observed_method_order[current_dataset].append(source_method)

    for dataset in CA_DATASET_KEYS:
        if observed_method_order[dataset] != expected_method_order:
            raise RuntimeError(
                f"alternative CA method order drift for {dataset}: "
                f"{observed_method_order[dataset]!r}"
            )
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
        and audit["ca_cell_count"] == 32
        and audit["ccp_cell_count"] == 90
        and audit["scalar_count"] == 488
    ):
        raise SystemExit("paper table fixture audit failed")
    print(json.dumps(audit, sort_keys=True))


if __name__ == "__main__":
    main()

````


````json title=paper_table_fixture_audit.json
{
  "config_sha256": "8c437380b9c5569f71b1e9923f3f6d074298e92b70efa9b2fbbff3969bb48a78",
  "main_tex_sha256": "49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857",
  "source_archive_sha256": "f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db",
  "source_url": "https://export.arxiv.org/e-print/2606.03600v1",
  "summary": {
    "all_fields_match": true,
    "ca_cell_count": 32,
    "ccp_cell_count": 90,
    "mismatch_count": 0,
    "mismatch_paths": [],
    "parsed_values_sha256": "a412b883aebd9aa128293cf5308db45cd89ae69eb50b868a71551d7a05124b14",
    "scalar_count": 488,
    "total_cell_count": 122
  }
}

````


````output
{"all_fields_match": true, "ca_cell_count": 32, "ccp_cell_count": 90, "mismatch_count": 0, "mismatch_paths": [], "parsed_values_sha256": "a412b883aebd9aa128293cf5308db45cd89ae69eb50b868a71551d7a05124b14", "scalar_count": 488, "total_cell_count": 122}

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_0e003382f985", "created_at": "2026-07-19T15:53:18+00:00", "title": "Released source and dataset manifest audit", "command": ["python", "repro/src/verify_source_manifest.py", "--source", "upstream", "--output", "outputs/source_manifest_audit.json"], "exit_code": 0, "duration_s": 1.482}
-->
````bash
$ python repro/src/verify_source_manifest.py --source upstream --output outputs/source_manifest_audit.json
````

exit 0 · 1.5s


````python title=verify_source_manifest.py
#!/usr/bin/env python3
"""Verify every released source/data input used by the full reproduction."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import subprocess
import warnings
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_SOURCE = (
    "Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974"
)
EXPECTED_FILE_PATHS = {
    "e-ca/config.py",
    "e-ca/main.py",
    "e-ca/methods.py",
    "e-ca/utils.py",
    "e-ccp/data_loader.py",
    "e-ccp/eccp_utils.py",
    "e-ccp/main.py",
    "e-ccp/datasets/Boston.csv",
    "e-ccp/datasets/abalone.csv",
    "e-ccp/datasets/merged_dataset.csv",
}
EXPECTED_DATASETS = {"boston", "abalone", "parkinson"}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(source: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(source), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def validate_relative_path(value: str) -> Path:
    relative = Path(value)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise AssertionError(f"unsafe source-manifest path: {value!r}")
    return relative


def validate_manifest(source: Path, manifest: dict) -> dict:
    source = source.resolve(strict=True)
    commit = git(source, "rev-parse", "HEAD")
    assert manifest["source"] == EXPECTED_SOURCE
    assert manifest["git_commit"] == commit == EXPECTED_SOURCE.rsplit("@", 1)[1]
    assert git(source, "status", "--porcelain") == ""

    entries = manifest["files"]
    assert isinstance(entries, list)
    paths = [entry["path"] for entry in entries]
    assert len(paths) == len(set(paths)) == len(EXPECTED_FILE_PATHS)
    assert set(paths) == EXPECTED_FILE_PATHS

    verified_files = []
    total_bytes = 0
    for entry in entries:
        assert set(entry) == {
            "path", "role", "byte_size", "sha256", "git_blob_sha1"
        }
        assert isinstance(entry["role"], str) and entry["role"].strip()
        relative = validate_relative_path(entry["path"])
        path = source / relative
        assert path.is_file(), f"missing released source input: {relative}"
        assert path.stat().st_size == entry["byte_size"]
        assert file_sha256(path) == entry["sha256"]
        blob = git(source, "rev-parse", f"HEAD:{relative.as_posix()}")
        assert blob == entry["git_blob_sha1"]
        total_bytes += path.stat().st_size
        verified_files.append(
            {
                "path": relative.as_posix(),
                "byte_size": path.stat().st_size,
                "sha256": entry["sha256"],
                "git_blob_sha1": blob,
            }
        )

    datasets = manifest["datasets"]
    assert set(datasets) == EXPECTED_DATASETS
    verified_datasets = {}
    for name, expected in datasets.items():
        assert set(expected) == {
            "path", "data_rows", "columns", "header",
            "loaded_feature_count", "target", "loader_config",
        }
        relative = validate_relative_path(expected["path"])
        assert relative.as_posix() in EXPECTED_FILE_PATHS
        with (source / relative).open(newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            header = next(reader)
            data_rows = list(reader)
        assert header == expected["header"]
        assert len(header) == expected["columns"]
        assert len(data_rows) == expected["data_rows"]
        assert all(len(row) == len(header) for row in data_rows)
        assert expected["target"] in header
        verified_datasets[name] = {
            "path": relative.as_posix(),
            "data_rows": len(data_rows),
            "columns": len(header),
            "loaded_feature_count": expected["loaded_feature_count"],
            "target": expected["target"],
        }

    loader_path = source / "e-ccp/data_loader.py"
    spec = importlib.util.spec_from_file_location("_p2e_source_data_loader", loader_path)
    assert spec is not None and spec.loader is not None
    loader = importlib.util.module_from_spec(spec)
    original_cwd = Path.cwd()
    try:
        os.chdir(source / "e-ccp")
        spec.loader.exec_module(loader)
        for name, expected in datasets.items():
            # The pinned loader intentionally relies on a Pandas-2 assignment
            # that emits a FutureWarning containing its absolute local path.
            # The behavior is separately documented and pinned; suppress only
            # that warning so a Trackio command cannot publish a host path.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", FutureWarning)
                features, targets, config = loader.load_dataset(name)
            assert features.shape == (
                expected["data_rows"], expected["loaded_feature_count"]
            )
            assert targets.shape == (expected["data_rows"],)
            assert loader.np.isfinite(features).all()
            assert loader.np.isfinite(targets).all()
            assert config == expected["loader_config"]
            verified_datasets[name]["loaded_shape"] = list(features.shape)
            verified_datasets[name]["loader_config"] = config
    finally:
        os.chdir(original_cwd)

    return {
        "source": manifest["source"],
        "git_commit": commit,
        "files": verified_files,
        "datasets": verified_datasets,
        "summary": {
            "all_files_hash_verified": True,
            "all_files_git_blob_verified": True,
            "all_dataset_shapes_verified": True,
            "all_loader_outputs_verified": True,
            "source_worktree_clean": True,
            "file_count": len(verified_files),
            "dataset_count": len(verified_datasets),
            "total_source_input_bytes": total_bytes,
            "total_dataset_rows": sum(
                dataset["data_rows"] for dataset in verified_datasets.values()
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument(
        "--manifest", type=Path,
        default=Path("repro/configs/source_manifest.json"),
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_path = args.manifest if args.manifest.is_absolute() else ROOT / args.manifest
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    result = validate_manifest(args.source, manifest)
    result["manifest_sha256"] = file_sha256(manifest_path)

    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    temporary.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(output)
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()

````


````json title=source_manifest_audit.json
{
  "datasets": {
    "abalone": {
      "columns": 9,
      "data_rows": 4177,
      "loaded_feature_count": 10,
      "loaded_shape": [
        4177,
        10
      ],
      "loader_config": {
        "K": 10,
        "alpha": 0.1,
        "lambda_": 0.01,
        "n_test": null,
        "n_train": 4000,
        "name": "Abalone",
        "ntree": 200
      },
      "path": "e-ccp/datasets/abalone.csv",
      "target": "Rings"
    },
    "boston": {
      "columns": 15,
      "data_rows": 506,
      "loaded_feature_count": 14,
      "loaded_shape": [
        506,
        14
      ],
      "loader_config": {
        "K": 5,
        "alpha": 0.1,
        "lambda_": 0.01,
        "n_test": null,
        "n_train": 400,
        "name": "Boston",
        "ntree": 200
      },
      "path": "e-ccp/datasets/Boston.csv",
      "target": "medv"
    },
    "parkinson": {
      "columns": 21,
      "data_rows": 5875,
      "loaded_feature_count": 13,
      "loaded_shape": [
        5875,
        13
      ],
      "loader_config": {
        "K": 5,
        "alpha": 0.1,
        "lambda_": 0.01,
        "n_test": null,
        "n_train": 3000,
        "name": "Parkinsons_UPDRS",
        "ntree": 200
      },
      "path": "e-ccp/datasets/merged_dataset.csv",
      "target": "total_UPDRS"
    }
  },
  "files": [
    {
      "byte_size": 1676,
      "git_blob_sha1": "2a21927b019bc01fe22948d0416eeda700e6dc47",
      "path": "e-ca/config.py",
      "sha256": "f4e7e7b174ce34a2dcb1a0b154a8f0f3adb7598d8d6328df2b62d0c2bbec34be"
    },
    {
      "byte_size": 7208,
      "git_blob_sha1": "66e67d19550e9468c8aa90e309418d9cc02737d3",
      "path": "e-ca/main.py",
      "sha256": "eec7b936cc62ec3ee55e6e73bad3644da5bc0573ecee2423b1d5fe2a51f3e643"
    },
    {
      "byte_size": 13479,
      "git_blob_sha1": "b0a9b14cd964ae5bb412520cdd87f729779eb04b",
      "path": "e-ca/methods.py",
      "sha256": "dda5d2429d4ca8c77be6a3b04bb3c159360bf3af58d1087a5f31cc17ea44cf86"
    },
    {
      "byte_size": 4925,
      "git_blob_sha1": "4468d16f02ed17f2147ebbf445fc96b726ba7fef",
      "path": "e-ca/utils.py",
      "sha256": "7aa2daf12c176af1679a5553fe903d594bc721f1b8c5e231de5a1fd8fc26a82f"
    },
    {
      "byte_size": 3710,
      "git_blob_sha1": "7a79954269b41c2dbde87ba62f2c71504bccb060",
      "path": "e-ccp/data_loader.py",
      "sha256": "85a3425c010cba6c47218974d5aeea7a66d3af529ddea6caa81ba425191034bc"
    },
    {
      "byte_size": 23016,
      "git_blob_sha1": "8df647cd5548212157622abad5ba615a90acd780",
      "path": "e-ccp/eccp_utils.py",
      "sha256": "7ef06bed7bef7c72dae5f760cf0f0c2b4cf4318af44f87763ac8cc0ab0687593"
    },
    {
      "byte_size": 12051,
      "git_blob_sha1": "8593e1c48524128546ba1775985a9ecc170f3fe4",
      "path": "e-ccp/main.py",
      "sha256": "4bfabc2a937a633db3d95a70f76e961a5541319b332e1452617ca6f64a8a57d6"
    },
    {
      "byte_size": 37658,
      "git_blob_sha1": "8c2d22a1cd9f06135b9a2fe2a379630e1d1d60dd",
      "path": "e-ccp/datasets/Boston.csv",
      "sha256": "a73bba75b82b2ffea542da3752edb63ea583620842d09810f0780fa2e8da9011"
    },
    {
      "byte_size": 191968,
      "git_blob_sha1": "e6d25ff2909d2afe82f0c0f0529eed8a252f2fdc",
      "path": "e-ccp/datasets/abalone.csv",
      "sha256": "50126af5ea3554ef637579b40f120be68e26aaa1d354df1e1f0e90775f629b44"
    },
    {
      "byte_size": 885763,
      "git_blob_sha1": "1c10affe990d8bbbb9befb02c4d91453783d01ee",
      "path": "e-ccp/datasets/merged_dataset.csv",
      "sha256": "81d62a8862e5f2faaab2f07fbac5feef5afbf2864f4d49b68134fdc2ca13c618"
    }
  ],
  "git_commit": "66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974",
  "manifest_sha256": "5178f48f40f3d707783bbc1679f0c5148088c3e7de850cbcbcc6e15bdf3388f9",
  "source": "Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974",
  "summary": {
    "all_dataset_shapes_verified": true,
    "all_files_git_blob_verified": true,
    "all_files_hash_verified": true,
    "all_loader_outputs_verified": true,
    "dataset_count": 3,
    "file_count": 10,
    "source_worktree_clean": true,
    "total_dataset_rows": 10558,
    "total_source_input_bytes": 1181454
  }
}

````


````output
{"all_dataset_shapes_verified": true, "all_files_git_blob_verified": true, "all_files_hash_verified": true, "all_loader_outputs_verified": true, "dataset_count": 3, "file_count": 10, "source_worktree_clean": true, "total_dataset_rows": 10558, "total_source_input_bytes": 1181454}

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_e5ee1304ecc2", "created_at": "2026-07-19T16:05:30+00:00", "title": "Primary TeX table fixture audit", "command": ["python", "repro/src/verify_paper_table_fixture.py", "--output", "outputs/paper_table_fixture_audit.json"], "exit_code": 0, "duration_s": 0.556}
-->
````bash
$ python repro/src/verify_paper_table_fixture.py --output outputs/paper_table_fixture_audit.json
````

exit 0 · 0.6s


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
CA_DATASET_KEYS = (
    "dataset_361234",
    "dataset_361235",
    "dataset_361237",
    "dataset_361244",
)
ALTERNATIVE_CA_METHODS = (
    (r"WECA($F_1$)", "WECA(log)"),
    (r"UR-WECA($F_1$)", "UR-WECA(log)"),
    (r"WECA($F_2$)", "WECA(sqrt)"),
    (r"UR-WECA($F_2$)", "UR-WECA(sqrt)"),
    (r"WECA($F_3$)", "WECA(linear)"),
    (r"UR-WECA($F_3$)", "UR-WECA(linear)"),
)
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
    output = {dataset: {} for dataset in CA_DATASET_KEYS}
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
        for index, dataset in enumerate(CA_DATASET_KEYS):
            coverage, length = pairs[2 * index : 2 * index + 2]
            output[dataset][config_method] = {
                "coverage_mean": coverage[0],
                "coverage_sd": coverage[1],
                "length_mean": length[0],
                "length_sd": length[1],
            }
    alternatives = parse_ca_alternative_table(tex)
    for dataset in CA_DATASET_KEYS:
        output[dataset].update(alternatives[dataset])
    return output


def parse_ca_alternative_table(
    tex: str,
) -> dict[str, dict[str, dict[str, float]]]:
    label = tex.index(r"\label{tab:weca_rotated}")
    start = tex.rindex(r"\begin{table}[t]", 0, label)
    end = tex.index(r"\end{table}", label)
    block = tex[start:end]
    if "& Method & Cov.  & Len." not in block:
        raise RuntimeError("alternative CA metric header drift")

    expected_ids = [dataset.removeprefix("dataset_") for dataset in CA_DATASET_KEYS]
    observed_ids = re.findall(r"\\textbf\{(\d+)\}", block)
    if observed_ids != expected_ids:
        raise RuntimeError(
            f"alternative CA dataset order drift: {observed_ids!r}"
        )

    method_map = dict(ALTERNATIVE_CA_METHODS)
    expected_method_order = [source for source, _ in ALTERNATIVE_CA_METHODS]
    output = {dataset: {} for dataset in CA_DATASET_KEYS}
    current_dataset: str | None = None
    observed_method_order: dict[str, list[str]] = {
        dataset: [] for dataset in CA_DATASET_KEYS
    }
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if "&" not in line or not any(source in line for source in method_map):
            continue
        dataset_match = re.search(r"\\textbf\{(\d+)\}", line)
        if dataset_match:
            current_dataset = f"dataset_{dataset_match.group(1)}"
        if current_dataset not in output:
            raise RuntimeError("alternative CA row appears before a known dataset")
        fields = [field.strip() for field in line.split("&")]
        if len(fields) != 4:
            raise RuntimeError(f"malformed alternative CA row: {line!r}")
        source_method = fields[1]
        if source_method not in method_map:
            raise RuntimeError(f"unexpected alternative CA method: {source_method!r}")
        coverage, length = parse_pairs(line, 2)
        output[current_dataset][method_map[source_method]] = {
            "coverage_mean": coverage[0],
            "coverage_sd": coverage[1],
            "length_mean": length[0],
            "length_sd": length[1],
        }
        observed_method_order[current_dataset].append(source_method)

    for dataset in CA_DATASET_KEYS:
        if observed_method_order[dataset] != expected_method_order:
            raise RuntimeError(
                f"alternative CA method order drift for {dataset}: "
                f"{observed_method_order[dataset]!r}"
            )
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


def parse_claim1_theorem_contract(tex: str) -> dict[str, object]:
    """Bind the numerical Claim-1 grid to the main theorem's exact domain."""
    marker = re.search(
        r"\\begin\{theorem\}\s*\\label\{main_theorem\}", tex
    )
    if marker is None:
        raise RuntimeError("Claim-1 main theorem is missing")
    start = marker.start()
    end = tex.index(r"\end{theorem}", start)
    block = tex[start:end]
    normalized = " ".join(block.split())
    domain = r"\alpha(n+1) \in (1,\infty)\setminus \mathbb{N}"
    s_interval = (
        r"s \in \left(\alpha, \frac{\lceil \alpha(n+1)\rceil}{n+1}\right)"
    )
    exact_formula = r"F_{n,\alpha}(p) : = \frac{1}{\alpha}"
    if (
        domain not in normalized
        or s_interval not in normalized
        or exact_formula not in normalized
    ):
        raise RuntimeError("Claim-1 main-theorem contract drift")
    return {
        "label": "main_theorem",
        "alpha_rank_domain": "alpha*(n+1) > 1 and non-integer",
        "strict_s_interval_verified": True,
        "normalized_logistic_formula_verified": True,
        "theorem_block_sha256": sha256_bytes(block.encode("utf-8")),
    }


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
    theorem_contract = parse_claim1_theorem_contract(tex_bytes.decode("utf-8"))
    result = {
        "source_url": SOURCE_URL,
        "source_archive_sha256": sha256_bytes(archive),
        "main_tex_sha256": sha256_bytes(tex_bytes),
        "config_sha256": sha256_bytes(config_bytes),
        "claim1_theorem_contract": theorem_contract,
        "summary": audit,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not (
        audit["all_fields_match"]
        and audit["ca_cell_count"] == 32
        and audit["ccp_cell_count"] == 90
        and audit["scalar_count"] == 488
    ):
        raise SystemExit("paper table fixture audit failed")
    print(json.dumps(audit, sort_keys=True))


if __name__ == "__main__":
    main()

````


````json title=paper_table_fixture_audit.json
{
  "claim1_theorem_contract": {
    "alpha_rank_domain": "alpha*(n+1) > 1 and non-integer",
    "label": "main_theorem",
    "normalized_logistic_formula_verified": true,
    "strict_s_interval_verified": true,
    "theorem_block_sha256": "86e98bc09083541aa2b908c96db4c460d78904929e64b6cf21bf1c435181ba71"
  },
  "config_sha256": "8c437380b9c5569f71b1e9923f3f6d074298e92b70efa9b2fbbff3969bb48a78",
  "main_tex_sha256": "49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857",
  "source_archive_sha256": "f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db",
  "source_url": "https://export.arxiv.org/e-print/2606.03600v1",
  "summary": {
    "all_fields_match": true,
    "ca_cell_count": 32,
    "ccp_cell_count": 90,
    "mismatch_count": 0,
    "mismatch_paths": [],
    "parsed_values_sha256": "a412b883aebd9aa128293cf5308db45cd89ae69eb50b868a71551d7a05124b14",
    "scalar_count": 488,
    "total_cell_count": 122
  }
}

````


````output
{"all_fields_match": true, "ca_cell_count": 32, "ccp_cell_count": 90, "mismatch_count": 0, "mismatch_paths": [], "parsed_values_sha256": "a412b883aebd9aa128293cf5308db45cd89ae69eb50b868a71551d7a05124b14", "scalar_count": 488, "total_cell_count": 122}

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_7e01054aac00", "created_at": "2026-07-19T16:10:04+00:00", "title": "Released OpenML CA input fingerprint audit", "command": ["python", "repro/src/verify_ca_inputs.py", "--source", "upstream", "--output", "outputs/ca_input_audit.json"], "exit_code": 0, "duration_s": 1.8}
-->
````bash
$ python repro/src/verify_ca_inputs.py --source upstream --output outputs/ca_input_audit.json
````

exit 0 · 1.8s


````python title=verify_ca_inputs.py
#!/usr/bin/env python3
"""Content-pin the live OpenML task inputs used by the released CA loader."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import numpy as np
import openml


ROOT = Path(__file__).resolve().parents[2]
SOURCE_COMMIT = "66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974"
EXPECTED_TASK_ORDER = [361237, 361235, 361244, 361234]
TASK_FIELDS = {
    "task_id", "dataset_id", "dataset_name", "dataset_version", "target_name",
    "X_shape", "y_shape", "X_sha256", "y_sha256",
}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def array_sha256(array: np.ndarray) -> str:
    canonical = np.ascontiguousarray(array, dtype="<f8")
    descriptor = json.dumps(
        {"dtype": "float64-le", "shape": list(canonical.shape)},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    digest = hashlib.sha256()
    digest.update(descriptor)
    digest.update(b"\0")
    digest.update(canonical.tobytes(order="C"))
    return digest.hexdigest()


def validate_manifest_contract(manifest: dict) -> None:
    assert set(manifest) == {
        "source", "loader_path", "loader_sha256", "array_hash_encoding", "tasks"
    }
    assert manifest["source"] == f"Nabil-Ala/P2E_calibration@{SOURCE_COMMIT}"
    assert manifest["loader_path"] == "e-ca/utils.py"
    assert manifest["array_hash_encoding"] == (
        "sha256(canonical-json(shape,dtype=float64-le) + NUL + C-order-bytes)"
    )
    tasks = manifest["tasks"]
    assert [task["task_id"] for task in tasks] == EXPECTED_TASK_ORDER
    assert len({task["task_id"] for task in tasks}) == len(tasks) == 4
    for task in tasks:
        assert set(task) == TASK_FIELDS
        assert len(task["X_sha256"]) == len(task["y_sha256"]) == 64
        assert task["X_shape"][0] == task["y_shape"][0]


def load_released_utils(source: Path, loader_path: str):
    path = source / loader_path
    spec = importlib.util.spec_from_file_location("_p2e_ca_source_utils", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_inputs(source: Path, manifest: dict) -> dict:
    validate_manifest_contract(manifest)
    source = source.resolve(strict=True)
    commit = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    assert commit == SOURCE_COMMIT
    status = subprocess.run(
        ["git", "-C", str(source), "status", "--porcelain"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    assert status == ""
    loader_path = source / manifest["loader_path"]
    assert file_sha256(loader_path) == manifest["loader_sha256"]
    loader = load_released_utils(source, manifest["loader_path"])

    verified = []
    for expected in manifest["tasks"]:
        task_id = expected["task_id"]
        task = openml.tasks.get_task(task_id)
        dataset = openml.datasets.get_dataset(task.dataset_id, download_data=False)
        features, targets = loader.load_dataset(task_id)
        observed = {
            "task_id": task_id,
            "dataset_id": task.dataset_id,
            "dataset_name": dataset.name,
            "dataset_version": dataset.version,
            "target_name": task.target_name,
            "X_shape": list(features.shape),
            "y_shape": list(targets.shape),
            "X_sha256": array_sha256(features),
            "y_sha256": array_sha256(targets),
        }
        assert observed == expected, f"OpenML input drift for task {task_id}"
        assert np.isfinite(features).all() and np.isfinite(targets).all()
        verified.append(observed)

    return {
        "source": manifest["source"],
        "loader_sha256": manifest["loader_sha256"],
        "tasks": verified,
        "summary": {
            "all_task_metadata_verified": True,
            "all_processed_array_hashes_verified": True,
            "all_processed_values_finite": True,
            "source_worktree_clean": True,
            "task_count": len(verified),
            "total_rows": sum(task["X_shape"][0] for task in verified),
            "total_feature_values": sum(
                task["X_shape"][0] * task["X_shape"][1] for task in verified
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument(
        "--manifest", type=Path,
        default=Path("repro/configs/ca_input_manifest.json"),
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_path = args.manifest if args.manifest.is_absolute() else ROOT / args.manifest
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    result = verify_inputs(args.source, manifest)
    result["manifest_sha256"] = file_sha256(manifest_path)
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    temporary.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(output)
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()

````


````json title=ca_input_audit.json
{
  "loader_sha256": "7aa2daf12c176af1679a5553fe903d594bc721f1b8c5e231de5a1fd8fc26a82f",
  "manifest_sha256": "0948d0059e4e0663a079257374363ef245ff71305b8ac9a7e472b2046706eca9",
  "source": "Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974",
  "summary": {
    "all_processed_array_hashes_verified": true,
    "all_processed_values_finite": true,
    "all_task_metadata_verified": true,
    "source_worktree_clean": true,
    "task_count": 4,
    "total_feature_values": 47126,
    "total_rows": 7776
  },
  "tasks": [
    {
      "X_sha256": "5e1b1a2b2a9de2b2b397d0145476a77c81a884faa5f038c390f652bc02173d82",
      "X_shape": [
        1030,
        8
      ],
      "dataset_id": 44959,
      "dataset_name": "concrete_compressive_strength",
      "dataset_version": 7,
      "target_name": "strength",
      "task_id": 361237,
      "y_sha256": "e709a1c0fefc715248a41ab1c184d00ec7f024f8ba274f613716414c730280e7",
      "y_shape": [
        1030
      ]
    },
    {
      "X_sha256": "8a1026e8e5c8852dff15f9e35b302f32eed9dbed73ea7c2c2f48fe0d570144b7",
      "X_shape": [
        1503,
        5
      ],
      "dataset_id": 44957,
      "dataset_name": "airfoil_self_noise",
      "dataset_version": 8,
      "target_name": "sound_pressure",
      "task_id": 361235,
      "y_sha256": "18723b318b20d127390b0c3797d4a670bf14ae56f1f9aed3adfdc1fcd170e13c",
      "y_shape": [
        1503
      ]
    },
    {
      "X_sha256": "197312760018900048c99403c277b56bcc2236a959dcfa1edb76ff1b729b8c57",
      "X_shape": [
        1066,
        2
      ],
      "dataset_id": 44966,
      "dataset_name": "solar_flare",
      "dataset_version": 7,
      "target_name": "c_class_flares",
      "task_id": 361244,
      "y_sha256": "d49d7c568e5508fe19a10cabe5882ef52fe2b14d1c57eed4f543035a5225efbf",
      "y_shape": [
        1066
      ]
    },
    {
      "X_sha256": "ffff896d7a215e8da58462b9849493c8553b0b1a8edc1ebccffb5580479a47fc",
      "X_shape": [
        4177,
        7
      ],
      "dataset_id": 44956,
      "dataset_name": "abalone",
      "dataset_version": 15,
      "target_name": "rings",
      "task_id": 361234,
      "y_sha256": "6e8fb2c54afc1b10153c3a12bb53176aef5b351ab11f9c8dee1494c571071ef2",
      "y_shape": [
        4177
      ]
    }
  ]
}

````


````output
{"all_processed_array_hashes_verified": true, "all_processed_values_finite": true, "all_task_metadata_verified": true, "source_worktree_clean": true, "task_count": 4, "total_feature_values": 47126, "total_rows": 7776}

````
