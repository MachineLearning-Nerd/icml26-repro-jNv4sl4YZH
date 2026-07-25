#!/usr/bin/env python3
"""Compose a fresh candidate from the immutable judged tree plus text overrides."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def copy_tree(source: Path, target: Path, *, exclude_cache: bool = False) -> None:
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        if exclude_cache and relative.parts and relative.parts[0] == ".cache":
            continue
        destination = target / relative
        if path.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--judged-dir", type=Path, required=True)
    parser.add_argument("--overrides", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if not args.judged_dir.is_dir() or not args.overrides.is_dir():
        raise SystemExit("judged directory and overrides directory must exist")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if any(args.output_dir.iterdir()):
        raise SystemExit("output directory must be empty")
    copy_tree(args.judged_dir, args.output_dir, exclude_cache=True)
    copy_tree(args.overrides, args.output_dir)
    files = [path for path in args.output_dir.rglob("*") if path.is_file()]
    print(f"composed_files={len(files)} output={args.output_dir}")


if __name__ == "__main__":
    main()
