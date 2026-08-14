#!/usr/bin/env python3
"""Validate the checked-in reproduction evidence without external writes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_COMMIT = "66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974"
PAPER_ID = "2606.03600"
OPENREVIEW_ID = "jNv4sl4YZH"
SOURCE_NAME = f"Nabil-Ala/P2E_calibration@{SOURCE_COMMIT}"
ANCHORED_CLAIMS_URL = (
    "https://huggingface.co/spaces/ICML-2026-agent-repro/challenge/"
    "resolve/main/claims_anchored.json"
)
DEFAULT_CLAIMS_URL = (
    "https://huggingface.co/spaces/ICML-2026-agent-repro/challenge/"
    "resolve/main/claims.json"
)
JURY_CLAIM_TEXTS = (
    "A calibrator is defined as set-preserving when converting conformal p-values at level alpha into e-values yields prediction sets identical to thresholding the e-values directly at 1/alpha (Section 2.1, Definition 2.2)",
    "Among left-continuous p-to-e calibrators, only the all-or-nothing calibrator can be exactly set-preserving, which motivates a new sigmoid-based P2E construction (Proposition 2.3, Theorem 2.6, Equation 9)",
    "The proposed sigmoid-based P2E calibrator is exact (expectation equal to 1), smooth, invertible, strictly positive, and strictly dominates the all-or-nothing calibrator in aggregation settings (Theorem 2.6)",
    "Applied to e-Cross-Conformal Prediction (ECCP), the P2E calibrator preserves exact 1-alpha coverage, whereas standard cross-conformal-prediction variants only guarantee approximate 1-2alpha coverage (Proposition 4.1)",
    "Applied to Weighted Conformal Aggregation (WECA), data-dependent weighted merging of e-values across multiple models retains valid coverage (Proposition 4.2)",
    "Empirically, ECCP using the proposed P2E calibrator produces smaller prediction sets than baseline p-to-e conversion methods while maintaining valid coverage (Section 5)",
)
EXPECTED_CA_PROTOCOL = {
    "source": SOURCE_NAME,
    "tasks": [
        "dataset_361237",
        "dataset_361235",
        "dataset_361244",
        "dataset_361234",
    ],
    "task_ids": [361237, 361235, 361244, 361234],
    "seeds": [42, 0, 1, 7, 10, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71],
    "alpha": 0.05,
    "M": 512,
    "B": 500,
}
EXPECTED_CCP_PROTOCOL = {
    "source": SOURCE_NAME,
    "datasets": {"boston": 15, "abalone": 15, "parkinson": 20},
    "seeds": list(range(45, 145)),
    "models": ["OLS", "RF", "Lasso"],
    "methods": [
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
    ],
    "alpha": 0.1,
    "grid_points": 300,
    "execution_adapter": "vectorized-exact-postprocessing-v1",
}
EVIDENCE_ARTIFACTS = (
    "repro/configs/jury_claims.json",
    "repro/configs/source_manifest.json",
    "repro/configs/ca_input_manifest.json",
    "repro/configs/full_protocol.json",
    "repro/configs/paper_headlines.json",
    "outputs/claim1_source_crosscheck.json",
    "outputs/claim1_independent.json",
    "outputs/claim2_endpoint_counterexample.json",
    "outputs/anchored_claims_mechanism.json",
    "outputs/claim3_properties_fullscale.json",
    "outputs/claim3_independent_e_merge.json",
    "outputs/claim4_eccp_full_protocol.json",
    "outputs/claim5_weca_full_protocol.json",
    "outputs/claim2_independent.json",
    "outputs/claim3_independent.json",
    "outputs/weca_independence_audit.json",
    "outputs/claim6_full_protocol.json",
    "outputs/paper_headline_comparison.json",
    "outputs/ccp_calibrator_contract_audit.json",
    "outputs/ca_p2e_domain_audit.json",
    "outputs/ca_input_audit.json",
    "outputs/source_manifest_audit.json",
    "outputs/paper_table_fixture_audit.json",
    "outputs/final_logbook_cells.json",
)
SOURCE_ARTIFACTS = (
    "sources/arxiv-v1/source.tar.gz",
    "sources/arxiv-v1/main.tex",
    "sources/arxiv-v1/paper.pdf",
    "sources.json",
)
SECRET_PATTERNS = (
    re.compile(r"hf_[A-Za-z0-9]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[A-Z0-9]{16}"),
)


def load_json(relative: str) -> dict[str, object]:
    payload = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"{relative} is not a JSON object")
    return payload


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with (ROOT / relative).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def require_true(payload: dict[str, object], *keys: str) -> None:
    summary = payload.get("summary")
    require(isinstance(summary, dict), "evidence summary is missing")
    for key in keys:
        require(summary.get(key) is True, f"{key}={summary.get(key)!r}")


def assert_exact_ca_protocol(protocol: dict[str, object]) -> None:
    require(protocol == EXPECTED_CA_PROTOCOL, "CA protocol drift")


def assert_exact_ccp_protocol(protocol: dict[str, object]) -> None:
    require(protocol == EXPECTED_CCP_PROTOCOL, "CCP protocol drift")


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [item.decode() for item in result.stdout.split(b"\0") if item]


def hygiene_gate() -> dict[str, object]:
    files = tracked_files()
    forbidden_paths = [
        item
        for item in files
        if item == ".trackio"
        or item.startswith(".trackio/")
        or item in {
            "repro/src/publish_after_gate.sh",
            "repro/src/publish_space_text.py",
            "repro/src/prepublish_gate.py",
        }
    ]
    env_files = [item for item in files if Path(item).name.startswith(".env")]
    secret_hits: list[str] = []
    absolute_path_hits: list[str] = []
    binary_suffixes = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".svg"}
    for relative in files:
        path = ROOT / relative
        if path.suffix.lower() in binary_suffixes or path.stat().st_size > 20_000_000:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(content):
                secret_hits.append(relative)
        absolute_prefixes = ("/" + "Users/", "/" + "home/")
        if any(prefix in content for prefix in absolute_prefixes):
            absolute_path_hits.append(relative)
    require(not forbidden_paths, f"forbidden publication paths: {forbidden_paths}")
    require(not env_files, f"environment files: {env_files}")
    require(not secret_hits, f"secret-like values: {secret_hits}")
    require(not absolute_path_hits, f"absolute local paths: {absolute_path_hits}")
    return {
        "tracked_files": len(files),
        "forbidden_paths": forbidden_paths,
        "env_files": env_files,
        "secret_hits": secret_hits,
        "absolute_path_hits": absolute_path_hits,
    }


def write_bundle() -> tuple[str, list[str]]:
    output = ROOT / "outputs/evidence_bundle.jsonl"
    temporary = output.with_name(output.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for relative in EVIDENCE_ARTIFACTS:
            path = ROOT / relative
            require(path.is_file(), f"missing evidence artifact: {relative}")
            handle.write(
                json.dumps(
                    {
                        "path": relative,
                        "sha256": sha256(relative),
                        "payload": json.loads(path.read_text(encoding="utf-8")),
                    },
                    sort_keys=True,
                )
                + "\n"
            )
    temporary.replace(output)
    return str(output.relative_to(ROOT)), list(EVIDENCE_ARTIFACTS)


def validate_bundle(relative: str, artifacts: tuple[str, ...]) -> str:
    lines = (ROOT / relative).read_text(encoding="utf-8").splitlines()
    require(len(lines) == len(artifacts), "evidence bundle record count drift")
    for line, artifact in zip(lines, artifacts, strict=True):
        record = json.loads(line)
        require(set(record) == {"path", "sha256", "payload"}, "bundle schema drift")
        require(record["path"] == artifact, f"bundle path drift: {artifact}")
        require(record["sha256"] == sha256(artifact), f"bundle hash drift: {artifact}")
        require(
            record["payload"] == json.loads((ROOT / artifact).read_text(encoding="utf-8")),
            f"bundle payload drift: {artifact}",
        )
    return sha256(relative)


def write_manifest(bundle_relative: str) -> tuple[str, str]:
    paths = [*EVIDENCE_ARTIFACTS, *SOURCE_ARTIFACTS, bundle_relative]
    manifest = {
        "files": [
            {
                "path": relative,
                "bytes": (ROOT / relative).stat().st_size,
                "sha256": sha256(relative),
            }
            for relative in paths
        ]
    }
    output = ROOT / "outputs/artifact_manifest.json"
    temporary = output.with_name(output.name + ".tmp")
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(output)
    return str(output.relative_to(ROOT)), sha256(str(output.relative_to(ROOT)))


def validate_evidence() -> dict[str, object]:
    jury = load_json("repro/configs/jury_claims.json")
    require(jury.get("openreview_id") == OPENREVIEW_ID, "OpenReview ID drift")
    require(jury.get("source_url") == ANCHORED_CLAIMS_URL, "anchored claim URL drift")
    require(jury.get("fallback_source_url") == DEFAULT_CLAIMS_URL, "fallback claim URL drift")
    require(jury.get("maximum_points") == 12, "maximum points drift")
    claims = jury.get("claims")
    require(isinstance(claims, list) and len(claims) == 6, "claim count drift")
    require(tuple(item["text"] for item in claims) == JURY_CLAIM_TEXTS, "claim wording drift")

    source_config = load_json("repro/configs/source_manifest.json")
    require(source_config.get("git_commit") == SOURCE_COMMIT, "source manifest commit drift")
    require(source_config.get("source") == SOURCE_NAME, "source manifest name drift")
    protocol_config = load_json("repro/configs/full_protocol.json")
    require(protocol_config.get("source_commit") == SOURCE_COMMIT, "protocol source drift")
    ca_config = protocol_config["claim_2_conformal_aggregation"]
    require(ca_config["openml_task_ids"] == [361234, 361235, 361237, 361244], "CA task configuration drift")
    require(ca_config["seeds"] == 20 and ca_config["alpha"] == 0.05, "CA seed/alpha configuration drift")
    require(ca_config["grid_points"] == 512 and ca_config["weight_samples"] == 500, "CA grid configuration drift")
    ccp_config = protocol_config["claim_3_cross_conformal"]
    require(ccp_config["seeds"] == 100 and ccp_config["datasets"] == {"boston": 15, "abalone": 15, "parkinson": 20}, "CCP configuration drift")

    source_audit = load_json("outputs/source_manifest_audit.json")
    require(source_audit.get("source") == SOURCE_NAME, "source audit name drift")
    require(source_audit.get("git_commit") == SOURCE_COMMIT, "source audit commit drift")
    require(source_audit.get("manifest_sha256") == sha256("repro/configs/source_manifest.json"), "source manifest hash drift")
    require(
        source_audit.get("summary") == {
            "all_dataset_shapes_verified": True,
            "all_files_git_blob_verified": True,
            "all_files_hash_verified": True,
            "all_loader_outputs_verified": True,
            "dataset_count": 3,
            "file_count": 10,
            "source_worktree_clean": True,
            "total_dataset_rows": 10558,
            "total_source_input_bytes": 1181454,
        },
        "source audit summary drift",
    )
    ca_inputs = load_json("outputs/ca_input_audit.json")
    require(ca_inputs.get("source") == SOURCE_NAME, "CA input source drift")
    require(
        ca_inputs.get("summary") == {
            "all_processed_array_hashes_verified": True,
            "all_processed_values_finite": True,
            "all_task_metadata_verified": True,
            "source_worktree_clean": True,
            "task_count": 4,
            "total_feature_values": 47126,
            "total_rows": 7776,
        },
        "CA input summary drift",
    )

    claim1 = load_json("outputs/claim1_independent.json")
    require_true(
        claim1,
        "all_set_identities_pass",
        "all_threshold_identities_pass",
        "all_exact_e_expectations_pass",
        "all_positive_pass",
        "all_classic_controls_inflate_sets",
        "all_theorem_domain_verified",
        "all_domain_controls_rejected",
    )
    require(claim1["summary"]["case_count"] == 18, "C1 cell count drift")
    require_true(claim1, "all_set_identities_pass")
    source_crosscheck = load_json("outputs/claim1_source_crosscheck.json")
    require_true(source_crosscheck, "all_cleanroom_membership_pass", "all_source_expectations_pass", "all_source_membership_pass", "all_theorem_domain_verified")

    endpoint = load_json("outputs/claim2_endpoint_counterexample.json")
    require(endpoint.get("verdict") == "FALSIFIED", "C2 endpoint verdict drift")
    counterexample = endpoint.get("counterexample")
    corrected = endpoint.get("corrected_theorem")
    require(isinstance(counterexample, dict) and isinstance(corrected, dict), "C2 endpoint evidence missing")
    for key in ("contradicts_uniqueness", "satisfies_every_printed_assumption", "works_for_every_alpha_in_(0,1)"):
        require(counterexample.get(key) is True, f"C2 counterexample control failed: {key}")
    require(corrected.get("paper_proof_itself_concludes_only_positive_intervals") is True, "C2 correction missing")

    anchored = load_json("outputs/anchored_claims_mechanism.json")
    require_true(anchored, "all_source_anchors_verified", "c1_definition_verified", "c2_aon_uniqueness_source_verified", "c2_aon_uniqueness_certificate_pass", "c2_left_continuity_witnesses_pass", "c3_all_exact_expectations_pass", "c3_all_smoothness_certificates_pass", "c3_all_inverse_roundtrips_pass", "c3_all_strict_positivity_pass", "c3_all_pointwise_aon_dominance_pass", "c3_all_aggregation_dominance_pass", "c4_eccp_proposition_verified", "c4_standard_ccp_bound_verified", "c5_weca_proposition_verified", "c5_weighted_expectation_identity_verified", "c6_section5_scope_verified")

    claim3_properties = load_json("outputs/claim3_properties_fullscale.json")
    require(claim3_properties.get("verdict") == "VERIFIED" and claim3_properties.get("all_claim_components_pass") is True, "C3 analytic verdict drift")
    claim3 = load_json("outputs/claim3_independent.json")
    require(claim3.get("rows_seen") == 11700 and claim3["summary"].get("expected_rows") == 11700, "CCP row count drift")
    require_true(claim3, "all_full_seed_cells_present", "exact_cell_set", "all_eccp_empirical_coverage_within_tolerance", "all_p2e_empirical_coverage_within_tolerance", "all_p2e_not_longer_than_existing_calibrators", "all_p2e_strictly_shorter_than_aon", "all_classical_efficiency_gains_substantial")
    assert_exact_ccp_protocol(claim3["protocol"])

    merge = load_json("outputs/claim3_independent_e_merge.json")
    require_true(merge, "all_merged_expectations_exact", "all_markov_coverage_events_pass", "all_arbitrary_dependence_coverage_pass", "all_exchangeable_prefix_coverage_pass", "all_exchangeable_randomized_prefix_coverage_pass", "all_randomized_uniform_coverage_events_pass", "all_randomized_arbitrary_dependence_coverage_pass", "invalid_scaling_control_detected", "invalid_arbitrary_dependence_detected", "invalid_randomized_arbitrary_dependence_detected", "adaptive_weight_control_detected", "adaptive_randomized_weight_control_detected")
    claim4 = load_json("outputs/claim4_eccp_full_protocol.json")
    require(claim4.get("verdict") == "VERIFIED" and claim4.get("all_claim_components_pass") is True, "C4 verdict drift")

    independence = load_json("outputs/weca_independence_audit.json")
    require_true(independence, "all_required_flow_present", "all_split_partitions_disjoint", "all_weights_independent_of_final_calibration", "all_weights_independent_of_test_data_and_outcomes", "all_illegal_test_adaptive_controls_change")
    require(independence["summary"].get("case_count") == 6, "WECA case count drift")
    claim5 = load_json("outputs/claim5_weca_full_protocol.json")
    require(claim5.get("verdict") == "VERIFIED" and claim5.get("all_claim_components_pass") is True, "C5 verdict drift")
    ca = load_json("outputs/claim2_independent.json")
    require(ca.get("rows_seen") == 1920 and ca["summary"].get("expected_rows") == 1920, "CA row count drift")
    require_true(ca, "all_four_tasks_present", "all_full_seed_method_cells_present", "exact_cell_set", "all_substantial_efficiency_gains", "all_p2e_empirical_coverage_within_tolerance")
    assert_exact_ca_protocol(ca["protocol"])

    claim6 = load_json("outputs/claim6_full_protocol.json")
    require(claim6.get("verdict") == "VERIFIED" and claim6.get("all_claim_components_pass") is True, "C6 verdict drift")
    require(ca["summary"].get("p2e_shorter_count") == 24, "CA efficiency count drift")
    require(claim3["summary"].get("p2e_strictly_shorter_count") == 36, "CCP efficiency count drift")
    require(claim3["summary"].get("aon_strictly_shorter_count") == 9, "AoN efficiency count drift")

    headline = load_json("outputs/paper_headline_comparison.json")
    headline_summary = headline["summary"]
    require(headline_summary.get("comparison_count") == 122 and headline_summary.get("scalar_comparison_count") == 488, "headline count drift")
    require_true(headline, "all_unaffected_within_tolerance", "all_outside_tolerance_cells_accounted_for", "all_source_table_replays_within_tolerance")
    require(headline_summary.get("unaffected_comparison_count") == 94 and headline_summary.get("unaffected_scalar_comparison_count") == 376, "unaffected headline drift")
    require(headline_summary.get("known_discrepancy_comparison_count") == 27 and headline_summary.get("known_discrepancy_scalar_comparison_count") == 108, "source discrepancy drift")
    require(headline_summary.get("known_ca_dispersion_discrepancy_count") == 1 and headline_summary.get("known_ca_dispersion_outside_tolerance_count") == 1, "CA dispersion disclosure drift")
    contract = load_json("outputs/ccp_calibrator_contract_audit.json")
    require_true(contract, "paper_formula_contract_verified", "released_formula_contract_verified", "released_column_order_verified_for_all_models", "paper_source_column_mismatch_verified", "all_numerical_witness_values_differ")

    final_cells = load_json("outputs/final_logbook_cells.json")
    require(final_cells["summary"].get("verified_claims") == 5 and final_cells["summary"].get("falsified_claims") == 1, "rendered verdict accounting drift")
    require("FALSIFIED" in final_cells["claim_2"] and "FULL_GATE_READY" in final_cells["conclusion"], "rendered claim summary drift")

    for relative, expected in {
        "sources/arxiv-v1/source.tar.gz": "f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db",
        "sources/arxiv-v1/main.tex": "49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857",
        "sources/arxiv-v1/paper.pdf": "702dbea68adb646d41255420c67122b63f879c66b333684f904fc39d11c718e2",
    }.items():
        require(sha256(relative) == expected, f"paper artifact hash drift: {relative}")

    return {
        "paper": PAPER_ID,
        "openreview_id": OPENREVIEW_ID,
        "source_commit": SOURCE_COMMIT,
        "claims": {
            "C1": "VERIFIED",
            "C2": "FALSIFIED_LITERAL_CORRECTED_POSITIVE_DOMAIN",
            "C3": "VERIFIED",
            "C4": "VERIFIED",
            "C5": "VERIFIED",
            "C6": "VERIFIED",
        },
        "ca_rows": 1920,
        "ccp_rows": 11700,
        "headline_cells": 122,
        "headline_scalars": 488,
        "verified_claims": 5,
        "falsified_claims": 1,
        "maximum_points": 12,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-producers", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("outputs/publication_gate.json"))
    args = parser.parse_args()

    hygiene = hygiene_gate()
    evidence = validate_evidence()
    bundle_relative, artifacts = write_bundle()
    bundle_hash = validate_bundle(bundle_relative, tuple(artifacts))
    manifest_relative, manifest_hash = write_manifest(bundle_relative)
    result = {
        **evidence,
        "hygiene": hygiene,
        "evidence_artifacts": list(EVIDENCE_ARTIFACTS),
        "bundle": {"path": bundle_relative, "records": len(artifacts), "sha256": bundle_hash},
        "artifact_manifest": {"path": manifest_relative, "sha256": manifest_hash},
        "producers_skipped": args.skip_producers,
        "publication_gate_passed": True,
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    temporary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(output)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
