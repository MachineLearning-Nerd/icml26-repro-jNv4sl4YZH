#!/usr/bin/env python3
"""Evaluator-blind, fail-closed audit of the composed Hugging Face candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import deque
from pathlib import Path


SPACE_RESOLVE = (
    "https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/"
)
SLUG_PATTERN = re.compile(r"\]\(#/([a-z0-9-]+)\)")
ABSOLUTE_LINK_PATTERN = re.compile(
    r"https://huggingface\.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/([^)\s]+)"
)
PLACEHOLDER_PATTERN = re.compile(r"\{\{[A-Z0-9_]+\}\}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_manifest(path: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split(maxsplit=1)
        records[relative.removeprefix("./")] = digest
    return records


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--judged-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-placeholders", action="store_true")
    args = parser.parse_args()
    root = args.candidate
    failures: list[str] = []
    warnings: list[str] = []
    opened: list[str] = []

    required_roots = ("README.md", "logbook.json", "pages/index.md")
    for relative in required_roots:
        if not (root / relative).is_file():
            failures.append(f"missing canonical file: {relative}")
    if failures:
        result = {"status": "FAIL", "failures": failures, "opened_files": opened}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        raise SystemExit(1)

    logbook = json.loads(text(root / "logbook.json"))
    slug_to_file = {
        child["slug"]: child["file"] for child in logbook["root"]["children"]
    }
    queue = deque(["README.md"])
    visited: set[str] = set()
    while queue:
        relative = queue.popleft()
        if relative in visited:
            continue
        path = root / relative
        if not path.is_file():
            failures.append(f"reachable path missing: {relative}")
            continue
        visited.add(relative)
        opened.append(relative)
        if path.suffix not in {".md", ".json", ".py", ".toml", ".lock"}:
            continue
        content = text(path)
        for slug in SLUG_PATTERN.findall(content):
            mapped = slug_to_file.get(slug)
            if mapped is None:
                failures.append(f"reachable slug absent from logbook: {slug}")
            else:
                queue.append(mapped)
        for linked in ABSOLUTE_LINK_PATTERN.findall(content):
            linked_path = root / linked
            if not linked_path.is_file():
                failures.append(f"linked Space evidence missing: {linked}")

    canonical = [
        "pages/00-current-evidence/page.md",
        "pages/current-overview/page.md",
        *(f"pages/current-claim-{claim}/page.md" for claim in range(1, 7)),
        "pages/visibility-matrix/page.md",
        "pages/release-report/page.md",
        "pages/red-team-review/page.md",
    ]
    for relative in canonical:
        if relative not in visited:
            failures.append(f"canonical page not reachable from README: {relative}")

    capsule = text(root / "pages/00-current-evidence/page.md")
    for claim in range(1, 7):
        marker = f"EXACT_CLAIM_{claim}_EVIDENCE"
        if marker not in capsule:
            failures.append(f"judge-first capsule missing marker: {marker}")
    if "END_JUDGE_FIRST_EVIDENCE_V2" not in capsule:
        failures.append("judge-first capsule is incomplete")

    exact_claim_tokens = {
        1: ("Exact source claim", "Assumptions audited", "Direct result", "membership mismatches"),
        2: ("Exact source claim", "Assumptions audited", "Direct result", "F*(0)=infinity"),
        3: ("Exact source claim", "Assumptions audited", "Direct result", "9/9"),
        4: ("Exact source claim", "Assumptions audited", "Direct result", "11,700"),
        5: ("Exact source claim", "Assumptions audited", "Direct result", "1,920"),
        6: ("Exact source claim", "Assumptions audited", "Direct result", "36/36"),
    }
    required_page_tokens = (
        "Run provenance",
        "uv run --frozen python repro/src/run_campaign.py",
        "uv.lock",
        "actual allocation",
        "Executable verifier",
        "Independent checker",
        "Checker output",
        "Negative",
        "Limitations",
    )
    for claim, claim_tokens in exact_claim_tokens.items():
        relative = f"pages/current-claim-{claim}/page.md"
        content = text(root / relative)
        for token in (*claim_tokens, *required_page_tokens):
            if token not in content:
                failures.append(f"Claim {claim} page missing token: {token}")
        if "Full " not in content and "Raw " not in content:
            failures.append(f"Claim {claim} page has no discoverable raw-data label")

    placeholders = []
    for relative in opened:
        path = root / relative
        if path.suffix in {".md", ".json", ".py", ".toml", ".lock"}:
            placeholders.extend(
                f"{relative}:{match.group(0)}"
                for match in PLACEHOLDER_PATTERN.finditer(text(path))
            )
    if placeholders and not args.allow_placeholders:
        failures.append(f"unresolved release placeholders: {len(placeholders)}")
    elif placeholders:
        warnings.append(f"unresolved release placeholders: {len(placeholders)}")

    judged = read_manifest(args.judged_manifest)
    candidate_paths = {
        str(path.relative_to(root)) for path in root.rglob("*") if path.is_file()
    }
    missing_historical = sorted(set(judged) - candidate_paths)
    if missing_historical:
        failures.append(f"historical path subset failed: {missing_historical}")
    immutable_historical_paths = [
        relative
        for relative in judged
        if relative
        not in {
            "README.md",
            "logbook.json",
            "pages/index.md",
        }
    ]
    modified_historical = [
        relative
        for relative in immutable_historical_paths
        if sha256(root / relative) != judged[relative]
    ]
    if modified_historical:
        failures.append(f"historical evidence content changed: {modified_historical}")
    historical_copy = (
        root
        / "evidence/historical/judged-7f87ab976b2ab93d25dbc77586cbff61c4746f1e"
    )
    for relative in ("README.md", "logbook.json", "index.md"):
        if not (historical_copy / relative).is_file():
            failures.append(f"missing exact historical navigation copy: {relative}")

    visibility = text(root / "pages/visibility-matrix/page.md")
    for claim in range(1, 7):
        row_pattern = re.compile(rf"^\| {claim} \|.*\| READY \|$", re.MULTILINE)
        if not row_pattern.search(visibility):
            failures.append(f"visibility matrix row incomplete: Claim {claim}")

    secret_patterns = {
        "hf_token": re.compile(r"\bhf_[A-Za-z0-9]{30,}\b"),
        "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
        "private_key": re.compile(r"BEGIN (?:RSA |OPENSSH )?PRIVATE KEY"),
    }
    secret_hits: list[str] = []
    text_files_scanned = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        try:
            content = text(path)
        except UnicodeDecodeError:
            continue
        text_files_scanned += 1
        for label, pattern in secret_patterns.items():
            if pattern.search(content):
                secret_hits.append(f"{path.relative_to(root)}:{label}")
    if secret_hits:
        failures.append(f"secret-like content found: {secret_hits}")

    result = {
        "status": "PASS" if not failures else "FAIL",
        "canonical_entrypoint": "README.md",
        "opened_files": opened,
        "opened_file_count": len(opened),
        "failures": failures,
        "warnings": warnings,
        "placeholders": placeholders,
        "claim_pages_checked": 6,
        "visibility_rows_complete": len(
            [claim for claim in range(1, 7) if f"| {claim} |" in visibility]
        ),
        "historical_path_count": len(judged),
        "candidate_path_count": len(candidate_paths),
        "historical_path_subset": not missing_historical,
        "immutable_historical_content_unchanged": not modified_historical,
        "navigation_files_superseded": ["README.md", "logbook.json", "pages/index.md"],
        "text_files_scanned": text_files_scanned,
        "secret_hits": secret_hits,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: result[key] for key in ("status", "opened_file_count", "failures", "warnings")}, sort_keys=True))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
