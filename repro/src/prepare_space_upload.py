#!/usr/bin/env python3
"""Prepare and verify a fail-closed, text-only Space upload allowlist."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path


ALLOWLIST_PATH = Path("evidence/current/release/upload_allowlist.txt")
MANIFEST_PATH = Path("evidence/current/release/upload_manifest.sha256")
PLACEHOLDER_PATTERN = re.compile(r"\{\{[A-Z0-9_]+\}\}")
SECRET_PATTERNS = {
    "hf_token": re.compile(r"\bhf_[A-Za-z0-9]{30,}\b"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "private_key": re.compile(r"BEGIN (?:RSA |OPENSSH )?PRIVATE KEY"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def all_files(root: Path) -> list[str]:
    return sorted(
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file()
    )


def validate_text(root: Path, relative_paths: list[str]) -> None:
    failures: list[str] = []
    for relative in relative_paths:
        path = root / relative
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            failures.append(f"non-UTF-8 file: {relative}")
            continue
        if "\x00" in content:
            failures.append(f"NUL byte in text file: {relative}")
        if PLACEHOLDER_PATTERN.search(content):
            failures.append(f"release placeholder in: {relative}")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(content):
                failures.append(f"{label} pattern in: {relative}")
    if failures:
        raise SystemExit("\n".join(failures))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.release_root.resolve()
    if not root.is_dir():
        raise SystemExit("release root must exist")

    allowlist = root / ALLOWLIST_PATH
    manifest = root / MANIFEST_PATH
    allowlist.parent.mkdir(parents=True, exist_ok=True)
    allowlist.unlink(missing_ok=True)
    manifest.unlink(missing_ok=True)

    paths = all_files(root)
    paths.extend((str(ALLOWLIST_PATH), str(MANIFEST_PATH)))
    paths = sorted(set(paths))
    allowlist.write_text("\n".join(paths) + "\n", encoding="utf-8")

    # A digest file cannot include its own digest. It covers every other
    # uploaded path, including the exact allowlist that names the digest file.
    manifest_paths = [relative for relative in paths if relative != str(MANIFEST_PATH)]
    manifest.write_text(
        "".join(f"{sha256(root / relative)}  {relative}\n" for relative in manifest_paths),
        encoding="utf-8",
    )

    actual = all_files(root)
    if paths != actual:
        raise SystemExit("allowlist is not an exact listing of release-root files")
    validate_text(root, actual)
    print(
        f"upload_allowlist_status=PASS files={len(actual)} "
        f"manifest_entries={len(manifest_paths)} manifest_self_excluded=true"
    )


if __name__ == "__main__":
    main()
