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
