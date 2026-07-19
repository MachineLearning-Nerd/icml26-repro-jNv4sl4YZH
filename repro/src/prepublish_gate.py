#!/usr/bin/env python3
"""Fail-closed local publication gate for the complete six-claim artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_COMMIT = "66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974"
DEFAULT_CLAIMS_URL = (
    "https://huggingface.co/spaces/ICML-2026-agent-repro/challenge/"
    "resolve/main/claims.json"
)
ANCHORED_CLAIMS_URL = (
    "https://huggingface.co/spaces/ICML-2026-agent-repro/challenge/"
    "resolve/main/claims_anchored.json"
)
# Anchored claims override the broad fallback claims in the challenge frontend.
# Keep this alias for callers that need the effective scoring source.
CLAIMS_URL = ANCHORED_CLAIMS_URL
REQUIRED_TAGS = {"icml2026-repro", "paper-jNv4sl4YZH"}
JURY_CLAIM_TEXTS = (
    "A calibrator is defined as set-preserving when converting conformal p-values at level alpha into e-values yields prediction sets identical to thresholding the e-values directly at 1/alpha (Section 2.1, Definition 2.2)",
    "Among left-continuous p-to-e calibrators, only the all-or-nothing calibrator can be exactly set-preserving, which motivates a new sigmoid-based P2E construction (Proposition 2.3, Theorem 2.6, Equation 9)",
    "The proposed sigmoid-based P2E calibrator is exact (expectation equal to 1), smooth, invertible, strictly positive, and strictly dominates the all-or-nothing calibrator in aggregation settings (Theorem 2.6)",
    "Applied to e-Cross-Conformal Prediction (ECCP), the P2E calibrator preserves exact 1-alpha coverage, whereas standard cross-conformal-prediction variants only guarantee approximate 1-2alpha coverage (Proposition 4.1)",
    "Applied to Weighted Conformal Aggregation (WECA), data-dependent weighted merging of e-values across multiple models retains valid coverage (Proposition 4.2)",
    "Empirically, ECCP using the proposed P2E calibrator produces smaller prediction sets than baseline p-to-e conversion methods while maintaining valid coverage (Section 5)",
)
FALLBACK_JURY_CLAIM_TEXTS = (
    "P2E calibrator converts conformal p-values to e-values without altering the induced prediction set",
    "Yields substantial efficiency gains over existing p-to-e methods in conformal inference",
    "Enables exact 1-α coverage in cross-conformal prediction and conformal aggregation",
)
HEADLINE_TOLERANCES = {
    "coverage_absolute_tolerance": 0.01,
    "coverage_sd_absolute_tolerance": 0.01,
    "length_relative_tolerance": 0.05,
    "length_sd_relative_tolerance": 0.10,
}
EXPECTED_CA_PROTOCOL = {
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
EXPECTED_CCP_PROTOCOL = {
    "source": "Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974",
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
TEXT_SUFFIXES = {
    "", ".cfg", ".csv", ".gitignore", ".ini", ".json", ".md", ".py",
    ".sh", ".toml", ".txt", ".yaml", ".yml",
}
SKIP_PARTS = {".git", ".venv", "__pycache__"}
SECRET_PATTERNS = (
    re.compile("hf" + r"_[A-Za-z0-9]{20,}"),
    re.compile("gh" + r"[pousr]_[A-Za-z0-9]{20,}"),
    re.compile("AKIA" + r"[A-Z0-9]{16}"),
)


def run(command: list[str]) -> str:
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    print(f"$ {' '.join(command)}")
    print(output.rstrip())
    return output


def load_json(relative: str) -> dict[str, object]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def assert_summary(payload: dict[str, object], required_true: tuple[str, ...]) -> None:
    summary = payload["summary"]
    assert isinstance(summary, dict)
    for key in required_true:
        assert summary.get(key) is True, f"summary gate failed: {key}={summary.get(key)!r}"


def assert_exact_ccp_protocol(protocol: dict[str, object]) -> None:
    """Reject self-consistent CCP output produced at any non-paper scope."""
    assert protocol == EXPECTED_CCP_PROTOCOL, "CCP paper protocol drift"


def assert_exact_ca_protocol(protocol: dict[str, object]) -> None:
    """Reject self-consistent CA output produced at any non-paper scope."""
    assert protocol == EXPECTED_CA_PROTOCOL, "CA paper protocol drift"


def assert_live_jury_claims(claims: object) -> None:
    """Require the effective anchored entry to retain all six pinned claims."""
    assert isinstance(claims, list), "live jury entry is not a claim list"
    assert len(claims) == 6, "live anchored jury claim count changed"
    texts = tuple(
        claim.get("text") if isinstance(claim, dict) else None for claim in claims
    )
    assert texts == JURY_CLAIM_TEXTS, "live jury claim wording changed"


def fetch_claim_payload(url: str) -> dict[str, object]:
    request = urllib.request.Request(
        url, headers={"User-Agent": "icml2026-reproduction-gate/1"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    assert isinstance(payload, dict), "live claims payload is not a mapping"
    return payload


def fetch_live_jury_claims() -> list[dict[str, object]]:
    """Mirror the frontend merge and prove the anchored override is live."""
    fallback_payload = fetch_claim_payload(DEFAULT_CLAIMS_URL)
    anchored_payload = fetch_claim_payload(ANCHORED_CLAIMS_URL)
    fallback = fallback_payload.get("jNv4sl4YZH")
    assert isinstance(fallback, list), "fallback jury entry is not a claim list"
    fallback_texts = tuple(
        claim.get("text") if isinstance(claim, dict) else None for claim in fallback
    )
    assert fallback_texts == FALLBACK_JURY_CLAIM_TEXTS, (
        "fallback jury claim wording changed"
    )
    claims = anchored_payload.get("jNv4sl4YZH")
    assert_live_jury_claims(claims)
    return claims


def text_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES and path.stat().st_size <= 20_000_000:
            files.append(path)
    return files


def validate_local_path_artifacts(
    metadata: dict[str, object], root: Path = ROOT
) -> int:
    """Validate Trackio's local-only artifact map without publishing its paths."""
    local_path_artifacts = metadata.get("local_path_artifacts", [])
    assert isinstance(local_path_artifacts, list)
    for entry in local_path_artifacts:
        assert isinstance(entry, dict)
        relative_text = str(entry.get("path", ""))
        relative = Path(relative_text)
        assert relative_text and relative_text != "."
        assert not relative.is_absolute() and ".." not in relative.parts
        expected = (root / relative).resolve()
        recorded = Path(str(entry.get("abs_path", ""))).resolve()
        assert recorded == expected, f"Trackio artifact path mismatch: {relative}"
        assert expected.is_file(), f"Trackio artifact is missing: {relative}"
    return len(local_path_artifacts)


def validate_required_local_artifact(
    metadata: dict[str, object], relative: str, root: Path = ROOT
) -> dict[str, object]:
    """Require one exact Trackio path-artifact entry for the final bundle."""
    validate_local_path_artifacts(metadata, root)
    entries = metadata.get("local_path_artifacts", [])
    assert isinstance(entries, list)
    matches = [entry for entry in entries if entry.get("path") == relative]
    assert len(matches) == 1, f"required Trackio artifact is not registered: {relative}"
    entry = matches[0]
    path = root / relative
    assert entry.get("artifact_type") == "dataset"
    assert entry.get("size") == path.stat().st_size
    return entry


def hygiene_gate() -> dict[str, object]:
    env_files = [
        str(path.relative_to(ROOT))
        for path in ROOT.rglob(".env*")
        if path.is_file() and not any(part in SKIP_PARTS for part in path.parts)
    ]
    secret_hits = []
    absolute_path_hits = []
    sensitive_name = "HF" + "_" + "TOKEN"
    absolute_prefix = "/home/" + "dineshai/"
    scanned_files = text_files()
    for path in scanned_files:
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative = str(path.relative_to(ROOT))
        if sensitive_name in content:
            secret_hits.append({"file": relative, "kind": "sensitive variable name"})
        for pattern in SECRET_PATTERNS:
            if pattern.search(content):
                secret_hits.append({"file": relative, "kind": "token-like value"})
        # Trackio needs an absolute source path in its *local-only* metadata to
        # upload a path artifact.  That file is gitignored and is never part of
        # the published Space; validate its mapping separately below.  Every
        # publishable file remains subject to the absolute-path prohibition.
        if absolute_prefix in content and relative != ".trackio/metadata.json":
            absolute_path_hits.append(relative)
    metadata = load_json(".trackio/metadata.json")
    local_path_artifact_count = validate_local_path_artifacts(metadata)
    assert not env_files, f"environment files present: {env_files}"
    assert not secret_hits, f"secret-like content present: {secret_hits}"
    assert not absolute_path_hits, f"absolute local paths present: {absolute_path_hits}"
    return {
        "env_files": env_files,
        "secret_hits": secret_hits,
        "absolute_path_hits": absolute_path_hits,
        "local_path_artifact_count": local_path_artifact_count,
        "text_files_scanned": len(scanned_files),
    }


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with (ROOT / relative).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_artifact_bundle(relative: str, artifacts: tuple[str, ...]) -> str:
    output = ROOT / relative
    temporary = output.with_name(output.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for artifact in artifacts:
            path = ROOT / artifact
            record = {
                "path": artifact,
                "sha256": sha256(artifact),
                "payload": json.loads(path.read_text(encoding="utf-8")),
            }
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    temporary.replace(output)
    return validate_artifact_bundle(relative, artifacts)


def validate_artifact_bundle(relative: str, artifacts: tuple[str, ...]) -> str:
    """Re-parse every JSONL record and bind it to the current source artifact."""
    bundle = ROOT / relative
    lines = bundle.read_text(encoding="utf-8").splitlines()
    assert len(lines) == len(artifacts), (
        f"bundle record count mismatch: {len(lines)} != {len(artifacts)}"
    )
    for line, artifact in zip(lines, artifacts, strict=True):
        record = json.loads(line)
        assert set(record) == {"path", "sha256", "payload"}
        assert record["path"] == artifact
        source = ROOT / artifact
        assert record["sha256"] == sha256(artifact)
        assert record["payload"] == json.loads(source.read_text(encoding="utf-8"))
    return sha256(relative)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("outputs/prepublish_gate.json"))
    args = parser.parse_args()

    source_commit = run(["git", "-C", "upstream", "rev-parse", "HEAD"]).strip()
    assert source_commit == SOURCE_COMMIT
    assert run(["git", "-C", "upstream", "status", "--porcelain"]).strip() == ""

    metadata = load_json(".trackio/metadata.json")
    assert metadata["openreview_id"] == "jNv4sl4YZH"
    assert metadata["arxiv_id"] == "2606.03600"
    assert metadata["paper"] == {
        "arxiv_id": "2606.03600",
        "openreview_id": "jNv4sl4YZH",
    }
    assert REQUIRED_TAGS <= set(metadata["tags"])

    jury = load_json("repro/configs/jury_claims.json")
    assert jury["openreview_id"] == "jNv4sl4YZH"
    assert jury["source_url"] == ANCHORED_CLAIMS_URL
    assert jury["fallback_source_url"] == DEFAULT_CLAIMS_URL
    assert jury["maximum_points"] == 12
    assert tuple(claim["text"] for claim in jury["claims"]) == JURY_CLAIM_TEXTS
    assert [claim["claim"] for claim in jury["claims"]] == [1, 2, 3, 4, 5, 6]
    assert [claim["possible_points"] for claim in jury["claims"]] == [2] * 6
    live_jury_claims = fetch_live_jury_claims()

    headline_config = load_json("repro/configs/paper_headlines.json")
    assert headline_config["source"] == (
        "arXiv:2606.03600v1, Table 2, CA alternative-calibrator table, "
        "and Appendix Tables 6-8"
    )
    assert all(
        headline_config["comparison_policy"].get(key) == value
        for key, value in HEADLINE_TOLERANCES.items()
    )
    assert sum(
        len(methods)
        for methods in headline_config["conformal_aggregation"].values()
    ) == 32
    assert sum(
        len(methods)
        for models in headline_config["cross_conformal"].values()
        for methods in models.values()
    ) == 90

    commands = (
        [sys.executable, "repro/src/verify_source_manifest.py", "--source", "upstream", "--output", "outputs/source_manifest_audit.json"],
        [sys.executable, "repro/src/verify_ca_inputs.py", "--source", "upstream", "--output", "outputs/ca_input_audit.json"],
        [sys.executable, "repro/src/verify_ca_p2e_domains.py", "--source", "upstream", "--output", "outputs/ca_p2e_domain_audit.json"],
        [sys.executable, "repro/src/verify_p2e_identity.py", "--output", "outputs/claim1_independent.json"],
        [sys.executable, "repro/src/crosscheck_source_p2e.py", "--source", "upstream", "--output", "outputs/claim1_source_crosscheck.json"],
        [sys.executable, "repro/src/verify_anchored_claims.py", "--output", "outputs/anchored_claims_mechanism.json"],
        [sys.executable, "repro/src/verify_e_merge_coverage.py", "--output", "outputs/claim3_independent_e_merge.json"],
        [sys.executable, "repro/src/verify_weca_independence.py", "--source", "upstream", "--output", "outputs/weca_independence_audit.json"],
        [sys.executable, "repro/src/verify_ca_results.py", "--raw-dir", "outputs/raw/author_ca", "--output", "outputs/claim2_independent.json"],
        [sys.executable, "repro/src/verify_ccp_results.py", "--raw-dir", "outputs/raw/author_ccp", "--output", "outputs/claim3_independent.json"],
        [sys.executable, "repro/src/verify_paper_table_fixture.py", "--output", "outputs/paper_table_fixture_audit.json"],
        [sys.executable, "repro/src/verify_ccp_calibrator_contract.py", "--source", "upstream", "--output", "outputs/ccp_calibrator_contract_audit.json"],
        [sys.executable, "repro/src/compare_paper_headlines.py", "--ca", "outputs/claim2_independent.json", "--ccp", "outputs/claim3_independent.json", "--output", "outputs/paper_headline_comparison.json"],
        [sys.executable, "-m", "unittest", "discover", "-s", "repro/tests", "-v"],
    )
    command_outputs = [run(command) for command in commands]

    source_manifest = load_json("outputs/source_manifest_audit.json")
    assert source_manifest["source"] == (
        "Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974"
    )
    assert source_manifest["git_commit"] == SOURCE_COMMIT
    assert source_manifest["manifest_sha256"] == sha256(
        "repro/configs/source_manifest.json"
    )
    assert source_manifest["summary"] == {
        "all_dataset_shapes_verified": True,
        "all_files_git_blob_verified": True,
        "all_files_hash_verified": True,
        "all_loader_outputs_verified": True,
        "dataset_count": 3,
        "file_count": 10,
        "source_worktree_clean": True,
        "total_dataset_rows": 10_558,
        "total_source_input_bytes": 1_181_454,
    }

    ca_inputs = load_json("outputs/ca_input_audit.json")
    assert ca_inputs["source"] == (
        "Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974"
    )
    assert ca_inputs["loader_sha256"] == (
        "7aa2daf12c176af1679a5553fe903d594bc721f1b8c5e231de5a1fd8fc26a82f"
    )
    assert ca_inputs["manifest_sha256"] == sha256(
        "repro/configs/ca_input_manifest.json"
    )
    assert ca_inputs["summary"] == {
        "all_processed_array_hashes_verified": True,
        "all_processed_values_finite": True,
        "all_task_metadata_verified": True,
        "source_worktree_clean": True,
        "task_count": 4,
        "total_feature_values": 47_126,
        "total_rows": 7_776,
    }

    ca_domains = load_json("outputs/ca_p2e_domain_audit.json")
    assert ca_domains["source"] == (
        "Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974"
    )
    assert ca_domains["context_counts"] == {
        "eca": 560, "weca_final": 560, "weca_tune": 560
    }
    assert ca_domains["boundary_context_counts"] == {
        "eca": 33, "weca_final": 22, "weca_tune": 25
    }
    assert ca_domains["summary"] == {
        "all_boundary_source_float_expectations_pass": True,
        "all_boundary_source_set_identities_pass": True,
        "all_boundary_source_uses_upper_bracket": True,
        "all_contexts_accounted_for": True,
        "all_exact_aon_repairs_pass": True,
        "all_low_level_conditions_pass": True,
        "all_theorem_contexts_in_domain": True,
        "boundary_context_count": 80,
        "boundary_unique_size_count": 27,
        "context_count": 1_680,
        "maximum_boundary_float_deviation_from_aon": 6.422607377437694e-174,
        "positive_exact_boundary_calibrator_impossible": True,
        "theorem_context_count": 1_600,
    }

    claim1 = load_json("outputs/claim1_independent.json")
    assert_summary(
        claim1,
        (
            "all_classic_controls_inflate_sets",
            "all_domain_controls_rejected",
            "all_exact_e_expectations_pass",
            "all_positive_pass",
            "all_set_identities_pass",
            "all_theorem_domain_verified",
            "all_threshold_identities_pass",
        ),
    )
    assert claim1["summary"]["case_count"] == 18
    assert claim1["summary"]["classic_control_case_count"] == 18
    assert claim1["summary"]["domain_control_count"] == 5
    claim1_source = load_json("outputs/claim1_source_crosscheck.json")
    assert_summary(
        claim1_source,
        (
            "all_cleanroom_membership_pass",
            "all_source_expectations_pass",
            "all_source_membership_pass",
            "all_theorem_domain_verified",
            "underflow_is_documented",
        ),
    )
    assert claim1_source["summary"]["rows"] == 18
    anchored = load_json("outputs/anchored_claims_mechanism.json")
    assert anchored["source_url"] == "https://export.arxiv.org/e-print/2606.03600v1"
    assert anchored["source_archive_sha256"] == (
        "f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db"
    )
    assert anchored["main_tex_sha256"] == (
        "49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857"
    )
    assert anchored["summary"] == {
        "all_source_anchors_verified": True,
        "c1_definition_verified": True,
        "c2_aon_uniqueness_certificate_pass": True,
        "c2_aon_uniqueness_source_verified": True,
        "c2_left_continuity_witnesses_pass": True,
        "c2_uniqueness_level_count": 4,
        "c3_all_aggregation_dominance_pass": True,
        "c3_all_exact_expectations_pass": True,
        "c3_all_inverse_roundtrips_pass": True,
        "c3_all_pointwise_aon_dominance_pass": True,
        "c3_all_smoothness_certificates_pass": True,
        "c3_all_strict_positivity_pass": True,
        "c3_case_count": 18,
        "c4_eccp_proposition_verified": True,
        "c4_standard_ccp_bound_case_count": 4,
        "c4_standard_ccp_bound_verified": True,
        "c5_weca_proposition_verified": True,
        "c5_weighted_expectation_identity_verified": True,
        "c6_section5_scope_verified": True,
        "source_anchor_count": 10,
    }
    mechanism = load_json("outputs/claim3_independent_e_merge.json")
    assert_summary(
        mechanism,
        (
            "all_arbitrary_dependence_coverage_pass",
            "all_exchangeable_prefix_coverage_pass",
            "all_exchangeable_randomized_prefix_coverage_pass",
            "all_markov_coverage_events_pass",
            "all_merged_expectations_exact",
            "all_randomized_arbitrary_dependence_coverage_pass",
            "all_randomized_uniform_coverage_events_pass",
            "adaptive_randomized_weight_control_detected",
            "adaptive_weight_control_detected",
            "invalid_arbitrary_dependence_detected",
            "invalid_randomized_arbitrary_dependence_detected",
            "invalid_scaling_control_detected",
        ),
    )
    assert mechanism["summary"]["case_count"] == 8
    assert mechanism["summary"]["equal_weight_case_count"] == 2
    assert mechanism["summary"]["nonuniform_weight_case_count"] == 6
    assert mechanism["summary"]["exchangeable_prefix_case_count"] == 5
    assert mechanism["summary"]["invalid_arbitrary_dependence_rejection_count"] == 4
    assert mechanism["summary"]["invalid_randomized_arbitrary_dependence_rejection_count"] == 8
    assert mechanism["summary"]["invalid_scaling_control_rejection_count"] == 2
    assert mechanism["summary"]["adaptive_weight_rejection_count"] == 8
    assert mechanism["summary"]["adaptive_randomized_weight_rejection_count"] == 8
    assert mechanism["summary"]["invalid_exchangeable_prefix_rejection_count"] == 5
    assert mechanism["summary"]["invalid_exchangeable_randomized_prefix_rejection_count"] == 5

    weca_independence = load_json("outputs/weca_independence_audit.json")
    assert weca_independence["source"] == (
        "Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974"
    )
    assert weca_independence["methods_sha256"] == (
        "dda5d2429d4ca8c77be6a3b04bb3c159360bf3af58d1087a5f31cc17ea44cf86"
    )
    assert weca_independence["function_contract"]["sha256"] == (
        "541a30601a5346d0adbcf50bb9dcfd2e5e8317f7403fb4540516680a52751bfb"
    )
    assert weca_independence["summary"] == {
        "all_illegal_test_adaptive_controls_change": True,
        "all_required_flow_present": True,
        "all_split_partitions_disjoint": True,
        "all_weights_independent_of_final_calibration": True,
        "all_weights_independent_of_test_data_and_outcomes": True,
        "case_count": 6,
    }

    claim2 = load_json("outputs/claim2_independent.json")
    assert_exact_ca_protocol(claim2["protocol"])
    assert_summary(
        claim2,
        (
            "all_four_tasks_present",
            "all_full_seed_method_cells_present",
            "exact_cell_set",
            "all_substantial_efficiency_gains",
            "all_p2e_empirical_coverage_within_tolerance",
        ),
    )
    claim2_summary = claim2["summary"]
    assert claim2["rows_seen"] == claim2_summary["expected_rows"] == 1_920
    assert claim2_summary["observed_unique_cells"] == 1_920
    assert claim2_summary["comparison_count"] == claim2_summary["p2e_shorter_count"] == 24
    assert claim2_summary["substantial_efficiency_gain_count"] == 24
    assert claim2_summary["minimum_substantial_relative_reduction"] == 0.10
    assert claim2_summary["minimum_observed_relative_reduction"] >= 0.10
    assert claim2_summary["p2e_empirical_coverage_cell_count"] == 8
    assert claim2_summary["p2e_empirical_coverage_pass_count"] == 8
    assert claim2_summary["empirical_coverage_shortfall_tolerance"] == 0.02
    assert claim2_summary["duplicate_cell_count"] == 0
    assert claim2_summary["unexpected_row_count"] == 0
    assert claim2_summary["nonfinite_row_count"] == 0
    assert claim2_summary["invalid_metric_row_count"] == 0

    claim3 = load_json("outputs/claim3_independent.json")
    assert_summary(
        claim3,
        (
            "all_full_seed_cells_present",
            "exact_cell_set",
            "all_eccp_empirical_coverage_within_tolerance",
            "all_p2e_empirical_coverage_within_tolerance",
            "all_p2e_not_longer_than_existing_calibrators",
            "all_p2e_strictly_shorter_than_aon",
            "all_classical_efficiency_gains_substantial",
        ),
    )
    claim3_summary = claim3["summary"]
    assert_exact_ccp_protocol(claim3["protocol"])
    assert claim3["rows_seen"] == claim3_summary["expected_rows"] == 11_700
    assert claim3_summary["observed_unique_cells"] == 11_700
    assert claim3_summary["duplicate_cell_count"] == 0
    assert claim3_summary["unexpected_row_count"] == 0
    assert claim3_summary["nonfinite_row_count"] == 0
    assert claim3_summary["invalid_metric_row_count"] == 0
    assert claim3_summary["eccp_empirical_coverage_cell_count"] == 9
    assert claim3_summary["eccp_empirical_coverage_pass_count"] == 9
    assert claim3_summary["p2e_empirical_coverage_cell_count"] == 27
    assert claim3_summary["p2e_empirical_coverage_pass_count"] == 27
    assert claim3_summary["empirical_coverage_shortfall_tolerance"] == 0.02
    assert claim3_summary["calibrator_efficiency_comparison_count"] == 36
    assert claim3_summary["p2e_not_longer_count"] == 36
    assert claim3_summary["p2e_strictly_shorter_count"] == 36
    assert claim3_summary["aon_comparison_count"] == 9
    assert claim3_summary["aon_strictly_shorter_count"] == 9
    assert claim3_summary["classical_comparison_count"] == 27
    assert claim3_summary["classical_substantial_gain_count"] == 27
    assert claim3_summary["minimum_substantial_relative_reduction"] == 0.10
    assert claim3_summary["minimum_classical_relative_reduction"] >= 0.10

    fixture_audit = load_json("outputs/paper_table_fixture_audit.json")
    assert fixture_audit["source_url"] == "https://export.arxiv.org/e-print/2606.03600v1"
    assert fixture_audit["source_archive_sha256"] == (
        "f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db"
    )
    assert fixture_audit["main_tex_sha256"] == (
        "49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857"
    )
    assert fixture_audit["config_sha256"] == sha256(
        "repro/configs/paper_headlines.json"
    )
    assert fixture_audit["claim1_theorem_contract"] == {
        "label": "main_theorem",
        "alpha_rank_domain": "alpha*(n+1) > 1 and non-integer",
        "strict_s_interval_verified": True,
        "normalized_logistic_formula_verified": True,
        "theorem_block_sha256": (
            "86e98bc09083541aa2b908c96db4c460d78904929e64b6cf21bf1c435181ba71"
        ),
    }
    fixture_summary = fixture_audit["summary"]
    assert fixture_summary["all_fields_match"] is True
    assert fixture_summary["mismatch_count"] == 0
    assert fixture_summary["mismatch_paths"] == []
    assert fixture_summary["ca_cell_count"] == 32
    assert fixture_summary["ccp_cell_count"] == 90
    assert fixture_summary["total_cell_count"] == 122
    assert fixture_summary["scalar_count"] == 488

    calibrator_contract = load_json("outputs/ccp_calibrator_contract_audit.json")
    assert calibrator_contract["paper_source_archive_sha256"] == (
        "f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db"
    )
    assert calibrator_contract["paper_main_tex_sha256"] == (
        "49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857"
    )
    assert calibrator_contract["released_main_py_sha256"] == (
        "4bfabc2a937a633db3d95a70f76e961a5541319b332e1452617ca6f64a8a57d6"
    )
    assert calibrator_contract["released_eccp_utils_sha256"] == (
        "7ef06bed7bef7c72dae5f760cf0f0c2b4cf4318af44f87763ac8cc0ab0687593"
    )
    assert calibrator_contract["summary"] == {
        "paper_formula_contract_verified": True,
        "released_formula_contract_verified": True,
        "released_column_order_verified_for_all_models": True,
        "paper_source_column_mismatch_verified": True,
        "discrepant_method_count": 3,
        "affected_paper_table_cells": 27,
        "affected_paper_table_scalars": 108,
        "all_numerical_witness_values_differ": True,
    }

    headlines = load_json("outputs/paper_headline_comparison.json")
    assert_summary(
        headlines,
        (
            "all_unaffected_within_tolerance",
            "all_outside_tolerance_cells_accounted_for",
            "all_source_table_replays_within_tolerance",
        ),
    )
    assert headlines["paper_source"] == headline_config["source"]
    assert all(
        headlines["comparison_policy"].get(key) == value
        for key, value in HEADLINE_TOLERANCES.items()
    )
    assert headlines["summary"]["comparison_count"] == 122
    assert headlines["summary"]["scalar_comparison_count"] == 488
    assert headlines["summary"]["unaffected_comparison_count"] == 94
    assert headlines["summary"]["unaffected_within_tolerance_count"] == 94
    assert headlines["summary"]["unaffected_scalar_comparison_count"] == 376
    assert headlines["summary"]["unaffected_within_tolerance_scalar_count"] == 376
    assert headlines["summary"]["known_discrepancy_comparison_count"] == 27
    assert headlines["summary"]["known_discrepancy_scalar_comparison_count"] == 108
    assert headlines["summary"]["source_table_replay_comparison_count"] == 18
    assert headlines["summary"]["source_table_replay_within_tolerance_count"] == 18
    assert headlines["summary"]["source_table_replay_scalar_comparison_count"] == 72
    assert (
        headlines["summary"]["source_table_replay_within_tolerance_scalar_count"]
        == 72
    )
    assert headlines["summary"]["known_ca_dispersion_discrepancy_count"] == 1
    assert headlines["summary"]["known_ca_dispersion_scalar_count"] == 4
    assert headlines["summary"]["known_ca_dispersion_within_tolerance_scalar_count"] == 3
    assert headlines["summary"]["known_ca_dispersion_outside_tolerance_count"] == 1
    assert headlines["summary"]["unexpected_outside_tolerance_count"] == 0

    required_trackio_text = {
        ".trackio/logbook/pages/claim-1/page.md": (
            "Claim 1 verdict",
        ),
        ".trackio/logbook/pages/claim-2/page.md": (
            "Independent full CA raw verification",
            "Claim 2 verdict",
        ),
        ".trackio/logbook/pages/claim-3/page.md": (
            "Independent full CCP raw verification",
            "Claim 3 verdict",
        ),
        ".trackio/logbook/pages/claim-4/page.md": (
            "Exchangeable and randomized e-merge coverage certificate",
            "Claim 4 verdict",
        ),
        ".trackio/logbook/pages/claim-5/page.md": (
            "Claim 5 verdict",
        ),
        ".trackio/logbook/pages/claim-6/page.md": (
            "Claim 6 verdict",
        ),
        ".trackio/logbook/pages/methods-source-audit/page.md": (
            "Six anchored-claim theorem and mechanism audit",
            "Released CA P2E theorem-domain audit",
            "Released OpenML CA input fingerprint audit",
            "Released source and dataset manifest audit",
            "Primary TeX table fixture audit",
            "Paper and released-code calibrator contract audit",
            "WECA independent-tuning audit",
        ),
        ".trackio/logbook/pages/conclusion/page.md": (
            "FULL_GATE_READY: jNv4sl4YZH",
        ),
    }
    for relative, markers in required_trackio_text.items():
        content = (ROOT / relative).read_text(encoding="utf-8")
        for marker in markers:
            assert marker in content, f"missing Trackio marker {marker!r} in {relative}"

    hygiene = hygiene_gate()
    artifacts = (
        "outputs/ca_p2e_domain_audit.json",
        "outputs/ca_input_audit.json",
        "outputs/source_manifest_audit.json",
        "outputs/claim1_independent.json",
        "outputs/claim1_source_crosscheck.json",
        "outputs/anchored_claims_mechanism.json",
        "outputs/claim2_independent.json",
        "outputs/claim3_independent_e_merge.json",
        "outputs/weca_independence_audit.json",
        "outputs/claim3_independent.json",
        "outputs/paper_table_fixture_audit.json",
        "outputs/ccp_calibrator_contract_audit.json",
        "outputs/paper_headline_comparison.json",
        "outputs/final_logbook_cells.json",
        *(f"outputs/raw/author_ca/dataset_{task}.json" for task in (361237, 361235, 361244, 361234)),
        *(f"outputs/raw/author_ccp/{dataset}.json" for dataset in ("boston", "abalone", "parkinson")),
    )
    artifact_hashes = {relative: sha256(relative) for relative in artifacts}
    bundle = "outputs/jNv4sl4YZH_full_evidence_bundle.jsonl"
    bundle_hash = write_artifact_bundle(bundle, artifacts)
    result = {
        "paper": "jNv4sl4YZH",
        "source_commit": source_commit,
        "claims": len(jury["claims"]),
        "claims_source_url": ANCHORED_CLAIMS_URL,
        "claims_source_urls": {
            "anchored": ANCHORED_CLAIMS_URL,
            "fallback": DEFAULT_CLAIMS_URL,
        },
        "live_claims_verified": len(live_jury_claims),
        "maximum_points": jury["maximum_points"],
        "tests_passed": True,
        "command_count": len(command_outputs),
        "hygiene": hygiene,
        "artifact_sha256": artifact_hashes,
        "artifact_paths": list(artifacts),
        "trackio_artifact_bundle": bundle,
        "trackio_artifact_bundle_sha256": bundle_hash,
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
