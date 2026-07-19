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
