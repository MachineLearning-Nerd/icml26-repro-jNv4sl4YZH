#!/usr/bin/env python3
"""Reproduce the live judge's page ordering and 120k-character truncation.

This is a release-gate audit, not a scientific claim verifier.  It proves that
the compact current evidence capsule is visible to the evaluator while the
immutable historical Space tree remains an exact subset of the candidate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

from huggingface_hub import snapshot_download


SPACE_ID = "DineshAI/jNv4sl4YZH"
PARENT_REVISION = "a7496ba32db672e7aa46c42edb3b7c3c45ff6725"
MAX_LOGBOOK_CHARS = 120_000
CAPSULE_PATH = "pages/00-current-evidence/page.md"
CAPSULE_MARKER = "JUDGE_FIRST_EVIDENCE_V2"
CAPSULE_END_MARKER = "END_JUDGE_FIRST_EVIDENCE_V2"
CLAIM_MARKERS = [f"EXACT_CLAIM_{index}_EVIDENCE" for index in range(1, 7)]
MUTABLE_RELEASE_PATHS = {
    "README.md",
    "logbook.json",
    "pages/index.md",
    "evidence/current/release/upload_allowlist.txt",
    "evidence/current/release/upload_manifest.sha256",
    "evidence/current/shared/campaign_run.json",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strip_figure_payloads(text: str) -> str:
    """Mirror the public live-judge implementation exactly."""

    def repl(match: re.Match[str]) -> str:
        fence, info, body = match.group(1), match.group(2).strip(), match.group(3)
        lang = (info.split() or [""])[0].lower()
        if lang == "html":
            return f"[figure html omitted: {len(body)} chars]"
        if lang == "raw" and len(body) > 4000:
            return (
                f"{fence}raw\n{body[:4000]}\n"
                f"[... raw data truncated ...]\n{fence}"
            )
        return match.group(0)

    return re.sub(r"(`{3,4}|~{3,4})([^\n]*)\n([\s\S]*?)\n\1", repl, text)


def judge_prompt(root: Path) -> tuple[str, list[dict[str, object]]]:
    pages = sorted(
        str(path.relative_to(root))
        for path in root.glob("pages/**/*.md")
        if path.is_file()
    )
    pages = [page for page in pages if page == "pages/index.md"] + [
        page for page in pages if page != "pages/index.md"
    ]
    parts: list[str] = []
    trace: list[dict[str, object]] = []
    total = 0
    for page in pages:
        text = (root / page).read_text(encoding="utf-8")
        text = re.sub(r"<!-- trackio-cell\n[\s\S]*?\n-->", "", text)
        text = strip_figure_payloads(text)
        block = f"\n\n===== FILE {page} =====\n{text}"
        remaining = MAX_LOGBOOK_CHARS - total
        if remaining <= 0:
            break
        truncated = len(block) > remaining
        if truncated:
            block = block[:remaining] + "\n[... page truncated for length ...]"
        parts.append(block)
        trace.append(
            {
                "path": page,
                "source_characters": len(text),
                "prompt_characters": len(block),
                "truncated": truncated,
            }
        )
        total += len(block)
    return "".join(parts), trace


def historical_subset(parent: Path, candidate: Path) -> dict[str, object]:
    parent_files = sorted(
        str(path.relative_to(parent))
        for path in parent.rglob("*")
        if path.is_file() and ".cache" not in path.relative_to(parent).parts
    )
    missing: list[str] = []
    changed: list[str] = []
    protected_changed: list[str] = []
    for relative in parent_files:
        candidate_path = candidate / relative
        if not candidate_path.is_file():
            missing.append(relative)
        elif sha256(parent / relative) != sha256(candidate_path):
            changed.append(relative)
            if relative not in MUTABLE_RELEASE_PATHS:
                protected_changed.append(relative)
    return {
        "parent_file_count": len(parent_files),
        "missing": missing,
        "changed": changed,
        "allowed_changed": sorted(set(changed) & MUTABLE_RELEASE_PATHS),
        "protected_changed": protected_changed,
        "path_subset": not missing,
        "protected_content_unchanged": not protected_changed,
    }


def materialize_candidate(parent: Path, overlay: Path, destination: Path) -> Path:
    """Model the text-only additive Hub commit without deleting parent paths."""

    shutil.copytree(
        parent,
        destination,
        ignore=shutil.ignore_patterns(".cache"),
        dirs_exist_ok=True,
    )
    shutil.copytree(overlay, destination, dirs_exist_ok=True)
    return destination


def resolve_parent(parent_root: Path | None, temporary: Path) -> Path:
    if parent_root is not None:
        return parent_root.resolve()
    return Path(
        snapshot_download(
            repo_id=SPACE_ID,
            repo_type="space",
            revision=PARENT_REVISION,
            local_dir=temporary / "parent",
        )
    )


def audit(candidate: Path, parent: Path) -> dict[str, object]:
    parent_prompt, parent_trace = judge_prompt(parent)
    candidate_prompt, candidate_trace = judge_prompt(candidate)
    subset = historical_subset(parent, candidate)
    capsule = candidate / CAPSULE_PATH
    failures: list[str] = []
    if not capsule.is_file():
        failures.append(f"missing compact evidence capsule: {CAPSULE_PATH}")
    if CAPSULE_MARKER in parent_prompt:
        failures.append("historical negative control unexpectedly contains capsule marker")
    if CAPSULE_MARKER not in candidate_prompt:
        failures.append("candidate prompt omits capsule marker")
    if CAPSULE_END_MARKER not in candidate_prompt:
        failures.append("candidate prompt truncates the compact evidence capsule")
    missing_claim_markers = [
        marker for marker in CLAIM_MARKERS if marker not in candidate_prompt
    ]
    if missing_claim_markers:
        failures.append(
            "candidate prompt omits claim markers: " + ", ".join(missing_claim_markers)
        )
    if not subset["path_subset"]:
        failures.append("historical parent file set is not a path subset")
    if not subset["protected_content_unchanged"]:
        failures.append("protected historical content changed")
    candidate_paths = [row["path"] for row in candidate_trace]
    if len(candidate_paths) < 2 or candidate_paths[:2] != [
        "pages/index.md",
        CAPSULE_PATH,
    ]:
        failures.append(
            "candidate judge order does not begin with index then compact capsule"
        )
    historical_current_markers = {
        marker: marker in parent_prompt for marker in CLAIM_MARKERS
    }
    if any(historical_current_markers.values()):
        failures.append("historical prompt unexpectedly contains new exact-claim markers")
    return {
        "status": "PASS" if not failures else "FAIL",
        "space_id": SPACE_ID,
        "parent_revision": PARENT_REVISION,
        "judge_max_logbook_characters": MAX_LOGBOOK_CHARS,
        "capsule_path": CAPSULE_PATH,
        "capsule_marker": CAPSULE_MARKER,
        "claim_markers": CLAIM_MARKERS,
        "historical_negative_control": {
            "prompt_characters": len(parent_prompt),
            "trace": parent_trace,
            "capsule_absent": CAPSULE_MARKER not in parent_prompt,
            "exact_claim_markers_absent": not any(
                historical_current_markers.values()
            ),
        },
        "candidate": {
            "prompt_characters": len(candidate_prompt),
            "trace": candidate_trace,
            "capsule_complete_before_truncation": (
                CAPSULE_MARKER in candidate_prompt
                and CAPSULE_END_MARKER in candidate_prompt
            ),
            "all_six_claim_markers_visible": not missing_claim_markers,
        },
        "historical_subset": subset,
        "failures": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-root", type=Path, default=Path("space_release"))
    parser.add_argument("--parent-root", type=Path)
    parser.add_argument(
        "--output", type=Path, default=Path("outputs/judge_prompt_visibility.json")
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=Path(".openresearch/artifacts/judge-visibility"),
    )
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="judge-visibility-") as directory:
        temporary = Path(directory)
        parent = resolve_parent(args.parent_root, temporary)
        candidate = materialize_candidate(
            parent, args.candidate_root.resolve(), temporary / "candidate"
        )
        result = audit(candidate, parent)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.write_text(payload, encoding="utf-8")
    (args.artifact_dir / "raw_visibility_audit.json").write_text(
        payload, encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
