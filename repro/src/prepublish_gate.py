#!/usr/bin/env python3
"""Fail-closed local publication gate for the complete three-claim artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_COMMIT = "66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974"
REQUIRED_TAGS = {"icml2026-repro", "paper-jNv4sl4YZH"}
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

    commands = (
        [sys.executable, "repro/src/verify_p2e_identity.py", "--output", "outputs/claim1_independent.json"],
        [sys.executable, "repro/src/crosscheck_source_p2e.py", "--source", "upstream", "--output", "outputs/claim1_source_crosscheck.json"],
        [sys.executable, "repro/src/verify_e_merge_coverage.py", "--output", "outputs/claim3_independent_e_merge.json"],
        [sys.executable, "repro/src/verify_ca_results.py", "--raw-dir", "outputs/raw/author_ca", "--output", "outputs/claim2_independent.json"],
        [sys.executable, "repro/src/verify_ccp_results.py", "--raw-dir", "outputs/raw/author_ccp", "--output", "outputs/claim3_independent.json"],
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
            "adaptive_weight_control_detected",
            "invalid_arbitrary_dependence_detected",
            "invalid_scaling_control_detected",
        ),
    )
    assert mechanism["summary"]["invalid_arbitrary_dependence_rejection_count"] == 2
    assert mechanism["summary"]["invalid_scaling_control_rejection_count"] == 1
    assert mechanism["summary"]["adaptive_weight_rejection_count"] == 6

    claim2 = load_json("outputs/claim2_independent.json")
    assert_summary(
        claim2,
        ("all_four_tasks_present", "all_full_seed_method_cells_present", "exact_cell_set"),
    )
    claim2_summary = claim2["summary"]
    assert claim2["rows_seen"] == claim2_summary["expected_rows"] == 1_920
    assert claim2_summary["observed_unique_cells"] == 1_920
    assert claim2_summary["comparison_count"] == claim2_summary["p2e_shorter_count"] == 24
    assert claim2_summary["duplicate_cell_count"] == 0
    assert claim2_summary["unexpected_row_count"] == 0
    assert claim2_summary["nonfinite_row_count"] == 0

    claim3 = load_json("outputs/claim3_independent.json")
    assert_summary(claim3, ("all_full_seed_cells_present", "exact_cell_set"))
    claim3_summary = claim3["summary"]
    assert claim3["rows_seen"] == claim3_summary["expected_rows"] == 11_700
    assert claim3_summary["observed_unique_cells"] == 11_700
    assert claim3_summary["duplicate_cell_count"] == 0
    assert claim3_summary["unexpected_row_count"] == 0
    assert claim3_summary["nonfinite_row_count"] == 0

    headlines = load_json("outputs/paper_headline_comparison.json")
    assert_summary(headlines, ("all_within_tolerance",))
    assert headlines["summary"]["comparison_count"] == 17
    assert headlines["summary"]["within_tolerance_count"] == 17
    assert headlines["summary"]["scalar_comparison_count"] == 68
    assert headlines["summary"]["within_tolerance_scalar_count"] == 68

    required_trackio_text = {
        ".trackio/logbook/pages/claim-2/page.md": "Independent full CA raw verification",
        ".trackio/logbook/pages/claim-3/page.md": "Independent full CCP raw verification",
        ".trackio/logbook/pages/methods-source-audit/page.md": "Paper headline comparison",
        ".trackio/logbook/pages/conclusion/page.md": "FULL_GATE_READY: jNv4sl4YZH",
    }
    for relative, marker in required_trackio_text.items():
        content = (ROOT / relative).read_text(encoding="utf-8")
        assert marker in content, f"missing Trackio marker {marker!r} in {relative}"

    hygiene = hygiene_gate()
    artifacts = (
        "outputs/claim1_independent.json",
        "outputs/claim1_source_crosscheck.json",
        "outputs/claim2_independent.json",
        "outputs/claim3_independent_e_merge.json",
        "outputs/claim3_independent.json",
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
        "claims": 3,
        "maximum_points": 6,
        "tests_passed": True,
        "command_count": len(command_outputs),
        "hygiene": hygiene,
        "artifact_sha256": artifact_hashes,
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
