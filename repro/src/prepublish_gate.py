#!/usr/bin/env python3
"""Fail-closed local publication gate for the complete three-claim artifact."""

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
CLAIMS_URL = (
    "https://huggingface.co/spaces/ICML-2026-agent-repro/challenge/"
    "resolve/main/claims.json"
)
REQUIRED_TAGS = {"icml2026-repro", "paper-jNv4sl4YZH"}
JURY_CLAIM_TEXTS = (
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
    """Require the live challenge entry to retain the exact three pinned claims."""
    assert isinstance(claims, list), "live jury entry is not a claim list"
    assert len(claims) == 3, "live jury claim count changed"
    texts = tuple(
        claim.get("text") if isinstance(claim, dict) else None for claim in claims
    )
    assert texts == JURY_CLAIM_TEXTS, "live jury claim wording changed"


def fetch_live_jury_claims() -> list[dict[str, object]]:
    request = urllib.request.Request(
        CLAIMS_URL, headers={"User-Agent": "icml2026-reproduction-gate/1"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    assert isinstance(payload, dict), "live claims payload is not a mapping"
    claims = payload.get("jNv4sl4YZH")
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
    assert jury["maximum_points"] == 6
    assert tuple(claim["text"] for claim in jury["claims"]) == JURY_CLAIM_TEXTS
    assert [claim["claim"] for claim in jury["claims"]] == [1, 2, 3]
    assert [claim["possible_points"] for claim in jury["claims"]] == [2, 2, 2]
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
        [sys.executable, "repro/src/verify_p2e_identity.py", "--output", "outputs/claim1_independent.json"],
        [sys.executable, "repro/src/crosscheck_source_p2e.py", "--source", "upstream", "--output", "outputs/claim1_source_crosscheck.json"],
        [sys.executable, "repro/src/verify_e_merge_coverage.py", "--output", "outputs/claim3_independent_e_merge.json"],
        [sys.executable, "repro/src/verify_weca_independence.py", "--source", "upstream", "--output", "outputs/weca_independence_audit.json"],
        [sys.executable, "repro/src/verify_ca_results.py", "--raw-dir", "outputs/raw/author_ca", "--output", "outputs/claim2_independent.json"],
        [sys.executable, "repro/src/verify_ccp_results.py", "--raw-dir", "outputs/raw/author_ccp", "--output", "outputs/claim3_independent.json"],
        [sys.executable, "repro/src/verify_paper_table_fixture.py", "--output", "outputs/paper_table_fixture_audit.json"],
        [sys.executable, "repro/src/compare_paper_headlines.py", "--ca", "outputs/claim2_independent.json", "--ccp", "outputs/claim3_independent.json", "--output", "outputs/paper_headline_comparison.json"],
        [sys.executable, "-m", "unittest", "discover", "-s", "repro/tests", "-v"],
    )
    command_outputs = [run(command) for command in commands]

    claim1 = load_json("outputs/claim1_independent.json")
    assert_summary(
        claim1,
        (
            "all_classic_controls_inflate_sets",
            "all_exact_e_expectations_pass",
            "all_positive_pass",
            "all_set_identities_pass",
        ),
    )
    claim1_source = load_json("outputs/claim1_source_crosscheck.json")
    assert_summary(
        claim1_source,
        (
            "all_cleanroom_membership_pass",
            "all_source_expectations_pass",
            "all_source_membership_pass",
            "underflow_is_documented",
        ),
    )
    mechanism = load_json("outputs/claim3_independent_e_merge.json")
    assert_summary(
        mechanism,
        (
            "all_arbitrary_dependence_coverage_pass",
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
    assert mechanism["summary"]["invalid_arbitrary_dependence_rejection_count"] == 4
    assert mechanism["summary"]["invalid_randomized_arbitrary_dependence_rejection_count"] == 8
    assert mechanism["summary"]["invalid_scaling_control_rejection_count"] == 2
    assert mechanism["summary"]["adaptive_weight_rejection_count"] == 8
    assert mechanism["summary"]["adaptive_randomized_weight_rejection_count"] == 8

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
    fixture_summary = fixture_audit["summary"]
    assert fixture_summary["all_fields_match"] is True
    assert fixture_summary["mismatch_count"] == 0
    assert fixture_summary["mismatch_paths"] == []
    assert fixture_summary["ca_cell_count"] == 32
    assert fixture_summary["ccp_cell_count"] == 90
    assert fixture_summary["total_cell_count"] == 122
    assert fixture_summary["scalar_count"] == 488

    headlines = load_json("outputs/paper_headline_comparison.json")
    assert_summary(headlines, ("all_within_tolerance",))
    assert headlines["paper_source"] == headline_config["source"]
    assert all(
        headlines["comparison_policy"].get(key) == value
        for key, value in HEADLINE_TOLERANCES.items()
    )
    assert headlines["summary"]["comparison_count"] == 122
    assert headlines["summary"]["within_tolerance_count"] == 122
    assert headlines["summary"]["scalar_comparison_count"] == 488
    assert headlines["summary"]["within_tolerance_scalar_count"] == 488

    required_trackio_text = {
        ".trackio/logbook/pages/claim-2/page.md": (
            "Independent full CA raw verification",
        ),
        ".trackio/logbook/pages/claim-3/page.md": (
            "Independent full CCP raw verification",
            "Deterministic and randomized arbitrary-dependence coupling LP",
        ),
        ".trackio/logbook/pages/methods-source-audit/page.md": (
            "Primary TeX table fixture audit",
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
        "outputs/claim1_independent.json",
        "outputs/claim1_source_crosscheck.json",
        "outputs/claim2_independent.json",
        "outputs/claim3_independent_e_merge.json",
        "outputs/weca_independence_audit.json",
        "outputs/claim3_independent.json",
        "outputs/paper_table_fixture_audit.json",
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
        "claims_source_url": CLAIMS_URL,
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
