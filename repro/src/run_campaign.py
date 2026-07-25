#!/usr/bin/env python3
"""Run the fixed, non-publishing cumulative reproduction contract.

The OpenResearch experiment command is intentionally constant across the tree.
Children change committed checkers and ``repro/configs/campaign_run.json``;
this entrypoint always restores the immutable judged raw evidence, reruns every
accepted checker, runs any stage-specific additions, and prints a compact
machine-readable result block for ``orx logs``.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "repro/configs/campaign_run.json"
SOURCE_REPOSITORY = "https://github.com/Nabil-Ala/P2E_calibration.git"
SOURCE_COMMIT = "66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974"
EVIDENCE_BUNDLE_URI = (
    "hf://buckets/DineshAI/jNv4sl4YZH-artifacts/"
    "logbook-files/outputs/jNv4sl4YZH_full_evidence_bundle.jsonl"
)
EVIDENCE_BUNDLE_SHA256 = (
    "1cd1115ee4fefc260c79512eb1a4bea61f342ebca5bb9acf3cc5b8ca91f90359"
)
EXPECTED_BUNDLE_RECORDS = 21
TRACKIO_METADATA = {
    "schema_version": 1,
    "title": "Repro - Set-Preserving Calibration from Conformal P-Values to E-Values",
    "space_id": "DineshAI/jNv4sl4YZH",
    "openreview_id": "jNv4sl4YZH",
    "arxiv_id": "2606.03600",
    "paper": {
        "arxiv_id": "2606.03600",
        "openreview_id": "jNv4sl4YZH",
    },
    "tags": ["icml2026-repro", "paper-jNv4sl4YZH"],
    "artifacts_bucket": "hf://buckets/DineshAI/jNv4sl4YZH-artifacts",
    "local_path_artifacts": [],
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def run(command: list[str]) -> dict[str, object]:
    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    runtime = time.monotonic() - started
    print(f"$ {' '.join(command)}")
    if completed.stdout:
        print(completed.stdout.rstrip())
    if completed.stderr:
        print(completed.stderr.rstrip())
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed with exit {completed.returncode}: {' '.join(command)}"
        )
    return {
        "command": command,
        "exit_code": completed.returncode,
        "runtime_seconds": runtime,
    }


def git_value(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def prepare_source() -> dict[str, object]:
    source = ROOT / "upstream"
    if not (source / ".git").is_dir():
        subprocess.run(
            ["git", "clone", "--filter=blob:none", SOURCE_REPOSITORY, str(source)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    subprocess.run(
        ["git", "-C", str(source), "fetch", "origin", SOURCE_COMMIT],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "-C", str(source), "checkout", "--detach", SOURCE_COMMIT],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    observed = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if observed != SOURCE_COMMIT:
        raise RuntimeError(f"source revision mismatch: {observed}")
    return {"repository": SOURCE_REPOSITORY, "commit": observed}


def restore_historical_evidence() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="jnv4-evidence-") as temporary:
        bundle = Path(temporary) / "evidence.jsonl"
        completed = subprocess.run(
            ["hf", "buckets", "cp", EVIDENCE_BUNDLE_URI, str(bundle)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "failed to retrieve immutable historical evidence bundle: "
                f"{completed.stderr.strip()}"
            )
        payload = bundle.read_bytes()
    observed_bundle_sha = sha256_bytes(payload)
    if observed_bundle_sha != EVIDENCE_BUNDLE_SHA256:
        raise RuntimeError(
            "historical evidence bundle hash mismatch: "
            f"{observed_bundle_sha} != {EVIDENCE_BUNDLE_SHA256}"
        )

    records = [json.loads(line) for line in payload.splitlines() if line.strip()]
    if len(records) != EXPECTED_BUNDLE_RECORDS:
        raise RuntimeError(
            f"historical evidence record count mismatch: {len(records)}"
        )
    payload_by_path = {record["path"]: record["payload"] for record in records}

    restored = 0
    exact_existing = 0
    for record in records:
        relative = Path(record["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError(f"unsafe evidence path: {relative}")
        destination = ROOT / relative
        if destination.is_file():
            observed = sha256_bytes(destination.read_bytes())
            if observed == record["sha256"]:
                exact_existing += 1
                continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(record["payload"], indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        if json.loads(destination.read_text(encoding="utf-8")) != record["payload"]:
            raise RuntimeError(f"semantic restoration failed: {relative}")
        restored += 1

    # The immutable bundle contains the complete author-run protocol inside the
    # independently verified claim summaries, but the historical uploader did
    # not include the two raw-directory sidecars consumed by the verifiers.
    # Reconstruct only those redundant sidecars from the hash-bound summaries.
    sidecars = {
        "outputs/raw/author_ca/protocol.json": (
            "outputs/claim2_independent.json",
            "protocol",
        ),
        "outputs/raw/author_ccp/protocol.json": (
            "outputs/claim3_independent.json",
            "protocol",
        ),
    }
    reconstructed_sidecars = 0
    for destination_path, (summary_path, key) in sidecars.items():
        try:
            sidecar_payload = payload_by_path[summary_path][key]
        except KeyError as error:
            raise RuntimeError(
                f"historical evidence lacks {summary_path}:{key}"
            ) from error
        destination = ROOT / destination_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(sidecar_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        if json.loads(destination.read_text(encoding="utf-8")) != sidecar_payload:
            raise RuntimeError(f"sidecar reconstruction failed: {destination_path}")
        reconstructed_sidecars += 1
    return {
        "bundle_sha256": observed_bundle_sha,
        "records": len(records),
        "exact_existing_files": exact_existing,
        "semantically_restored_files": restored,
        "reconstructed_protocol_sidecars": reconstructed_sidecars,
    }


def cpu_allocation() -> dict[str, object]:
    affinity_count = None
    if hasattr(os, "sched_getaffinity"):
        affinity_count = len(os.sched_getaffinity(0))
    return {
        "os_cpu_count": os.cpu_count(),
        "affinity_cpu_count": affinity_count,
    }


def prepare_trackio_metadata() -> None:
    """Restore ignored, non-secret publication metadata in every fresh clone."""
    destination = ROOT / ".trackio/metadata.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(TRACKIO_METADATA, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    started_wall = time.time()
    started = time.monotonic()
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    provenance = {
        "stage": config["stage"],
        "git_sha": git_value("rev-parse", "HEAD"),
        "git_branch": git_value("rev-parse", "--abbrev-ref", "HEAD"),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "estimated_required_cores": config["estimated_required_cores"],
        "selected_backend": config["selected_backend"],
        "selected_flavor": config["selected_flavor"],
        "actual_cpu_allocation": cpu_allocation(),
        "started_unix_seconds": started_wall,
    }
    print("CAMPAIGN_PROVENANCE=" + json.dumps(provenance, sort_keys=True))

    source = prepare_source()
    evidence = restore_historical_evidence()
    prepare_trackio_metadata()
    python = sys.executable
    commands = [
        [python, "repro/src/verify_p2e_identity.py", "--output", "outputs/claim1_independent.json"],
        [python, "repro/src/crosscheck_source_p2e.py", "--source", "upstream", "--output", "outputs/claim1_source_crosscheck.json"],
        [python, "repro/src/verify_anchored_claims.py", "--output", "outputs/anchored_claims_mechanism.json"],
        [python, "repro/src/verify_source_manifest.py", "--source", "upstream", "--output", "outputs/source_manifest_audit.json"],
        [python, "repro/src/verify_ca_inputs.py", "--source", "upstream", "--output", "outputs/ca_input_audit.json"],
        [python, "repro/src/verify_ca_p2e_domains.py", "--source", "upstream", "--output", "outputs/ca_p2e_domain_audit.json"],
        [python, "repro/src/verify_ca_results.py", "--raw-dir", "outputs/raw/author_ca", "--output", "outputs/claim2_independent.json"],
        [python, "repro/src/verify_e_merge_coverage.py", "--output", "outputs/claim3_independent_e_merge.json"],
        [python, "repro/src/verify_weca_independence.py", "--source", "upstream", "--output", "outputs/weca_independence_audit.json"],
        [python, "repro/src/verify_ccp_results.py", "--raw-dir", "outputs/raw/author_ccp", "--output", "outputs/claim3_independent.json"],
        [python, "repro/src/verify_paper_table_fixture.py", "--output", "outputs/paper_table_fixture_audit.json"],
        [python, "repro/src/verify_ccp_calibrator_contract.py", "--source", "upstream", "--output", "outputs/ccp_calibrator_contract_audit.json"],
        [python, "repro/src/compare_paper_headlines.py", "--ca", "outputs/claim2_independent.json", "--ccp", "outputs/claim3_independent.json", "--output", "outputs/paper_headline_comparison.json"],
        [python, "-m", "unittest", "discover", "-s", "repro/tests", "-v"],
    ]
    for extra in config.get("extra_commands", []):
        if not isinstance(extra, list) or not all(isinstance(item, str) for item in extra):
            raise RuntimeError(f"invalid extra command: {extra!r}")
        commands.append(extra)

    command_results = [run(command) for command in commands]
    total_runtime = time.monotonic() - started
    result = {
        "status": "VERIFIED",
        "stage": config["stage"],
        "git_sha": provenance["git_sha"],
        "source": source,
        "historical_evidence": evidence,
        "command_count": len(command_results),
        "all_exit_codes_zero": all(
            row["exit_code"] == 0 for row in command_results
        ),
        "actual_cpu_allocation": provenance["actual_cpu_allocation"],
        "runtime_seconds": total_runtime,
        "command_results": command_results,
    }
    artifact_dir = ROOT / ".openresearch/artifacts" / config["stage"]
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "runtime.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("CAMPAIGN_RESULT=" + json.dumps(result, sort_keys=True))
    print(
        f"EVAL status=VERIFIED stage={config['stage']} "
        f"commands={len(command_results)} runtime_seconds={total_runtime:.3f}"
    )


if __name__ == "__main__":
    main()
