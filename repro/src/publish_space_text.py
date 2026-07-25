#!/usr/bin/env python3
"""Publish an exact text-only allowlist to the existing Hugging Face Space."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from huggingface_hub import CommitOperationAdd, HfApi


DEFAULT_REPO = "DineshAI/jNv4sl4YZH"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_manifest(path: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split(maxsplit=1)
        records[relative] = digest
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-root", type=Path, required=True)
    parser.add_argument("--expected-parent", required=True)
    parser.add_argument("--repo-id", default=DEFAULT_REPO)
    parser.add_argument(
        "--commit-message",
        default="Publish audited claim-by-claim reproduction evidence",
    )
    args = parser.parse_args()
    if args.repo_id != DEFAULT_REPO:
        raise SystemExit(f"only the existing Space {DEFAULT_REPO} is authorized")

    root = args.release_root.resolve()
    allowlist_path = root / "evidence/current/release/upload_allowlist.txt"
    manifest_path = root / "evidence/current/release/upload_manifest.sha256"
    paths = allowlist_path.read_text(encoding="utf-8").splitlines()
    if not paths or paths != sorted(set(paths)):
        raise SystemExit("allowlist must be nonempty, sorted, and unique")
    actual = sorted(
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file()
    )
    if paths != actual:
        raise SystemExit("allowlist does not exactly match release-root files")

    for relative in paths:
        path = root / relative
        content = path.read_text(encoding="utf-8")
        if "\x00" in content:
            raise SystemExit(f"NUL byte rejected: {relative}")

    manifest = parse_manifest(manifest_path)
    expected_manifest_paths = set(paths) - {
        "evidence/current/release/upload_manifest.sha256"
    }
    if set(manifest) != expected_manifest_paths:
        raise SystemExit("manifest coverage does not match the allowlist")
    for relative, expected in manifest.items():
        if sha256(root / relative) != expected:
            raise SystemExit(f"manifest mismatch: {relative}")

    api = HfApi()
    current = api.repo_info(repo_id=args.repo_id, repo_type="space").sha
    if current != args.expected_parent:
        raise SystemExit(
            f"Space head changed: expected {args.expected_parent}, observed {current}"
        )
    operations = [
        CommitOperationAdd(path_in_repo=relative, path_or_fileobj=str(root / relative))
        for relative in paths
    ]
    result = api.create_commit(
        repo_id=args.repo_id,
        repo_type="space",
        operations=operations,
        commit_message=args.commit_message,
        parent_commit=args.expected_parent,
    )
    print(
        f"space_publish_status=PASS repo={args.repo_id} "
        f"files={len(paths)} revision={result.oid}"
    )


if __name__ == "__main__":
    main()
