#!/usr/bin/env python3
"""Verify every released source/data input used by the full reproduction."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import subprocess
import warnings
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_SOURCE = (
    "Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974"
)
EXPECTED_FILE_PATHS = {
    "e-ca/config.py",
    "e-ca/main.py",
    "e-ca/methods.py",
    "e-ca/utils.py",
    "e-ccp/data_loader.py",
    "e-ccp/eccp_utils.py",
    "e-ccp/main.py",
    "e-ccp/datasets/Boston.csv",
    "e-ccp/datasets/abalone.csv",
    "e-ccp/datasets/merged_dataset.csv",
}
EXPECTED_DATASETS = {"boston", "abalone", "parkinson"}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(source: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(source), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def validate_relative_path(value: str) -> Path:
    relative = Path(value)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise AssertionError(f"unsafe source-manifest path: {value!r}")
    return relative


def validate_manifest(source: Path, manifest: dict) -> dict:
    source = source.resolve(strict=True)
    commit = git(source, "rev-parse", "HEAD")
    assert manifest["source"] == EXPECTED_SOURCE
    assert manifest["git_commit"] == commit == EXPECTED_SOURCE.rsplit("@", 1)[1]
    assert git(source, "status", "--porcelain") == ""

    entries = manifest["files"]
    assert isinstance(entries, list)
    paths = [entry["path"] for entry in entries]
    assert len(paths) == len(set(paths)) == len(EXPECTED_FILE_PATHS)
    assert set(paths) == EXPECTED_FILE_PATHS

    verified_files = []
    total_bytes = 0
    for entry in entries:
        assert set(entry) == {
            "path", "role", "byte_size", "sha256", "git_blob_sha1"
        }
        assert isinstance(entry["role"], str) and entry["role"].strip()
        relative = validate_relative_path(entry["path"])
        path = source / relative
        assert path.is_file(), f"missing released source input: {relative}"
        assert path.stat().st_size == entry["byte_size"]
        assert file_sha256(path) == entry["sha256"]
        blob = git(source, "rev-parse", f"HEAD:{relative.as_posix()}")
        assert blob == entry["git_blob_sha1"]
        total_bytes += path.stat().st_size
        verified_files.append(
            {
                "path": relative.as_posix(),
                "byte_size": path.stat().st_size,
                "sha256": entry["sha256"],
                "git_blob_sha1": blob,
            }
        )

    datasets = manifest["datasets"]
    assert set(datasets) == EXPECTED_DATASETS
    verified_datasets = {}
    for name, expected in datasets.items():
        assert set(expected) == {
            "path", "data_rows", "columns", "header",
            "loaded_feature_count", "target", "loader_config",
        }
        relative = validate_relative_path(expected["path"])
        assert relative.as_posix() in EXPECTED_FILE_PATHS
        with (source / relative).open(newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            header = next(reader)
            data_rows = list(reader)
        assert header == expected["header"]
        assert len(header) == expected["columns"]
        assert len(data_rows) == expected["data_rows"]
        assert all(len(row) == len(header) for row in data_rows)
        assert expected["target"] in header
        verified_datasets[name] = {
            "path": relative.as_posix(),
            "data_rows": len(data_rows),
            "columns": len(header),
            "loaded_feature_count": expected["loaded_feature_count"],
            "target": expected["target"],
        }

    loader_path = source / "e-ccp/data_loader.py"
    spec = importlib.util.spec_from_file_location("_p2e_source_data_loader", loader_path)
    assert spec is not None and spec.loader is not None
    loader = importlib.util.module_from_spec(spec)
    original_cwd = Path.cwd()
    try:
        os.chdir(source / "e-ccp")
        spec.loader.exec_module(loader)
        for name, expected in datasets.items():
            # The pinned loader intentionally relies on a Pandas-2 assignment
            # that emits a FutureWarning containing its absolute local path.
            # The behavior is separately documented and pinned; suppress only
            # that warning so a Trackio command cannot publish a host path.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", FutureWarning)
                features, targets, config = loader.load_dataset(name)
            assert features.shape == (
                expected["data_rows"], expected["loaded_feature_count"]
            )
            assert targets.shape == (expected["data_rows"],)
            assert loader.np.isfinite(features).all()
            assert loader.np.isfinite(targets).all()
            assert config == expected["loader_config"]
            verified_datasets[name]["loaded_shape"] = list(features.shape)
            verified_datasets[name]["loader_config"] = config
    finally:
        os.chdir(original_cwd)

    return {
        "source": manifest["source"],
        "git_commit": commit,
        "files": verified_files,
        "datasets": verified_datasets,
        "summary": {
            "all_files_hash_verified": True,
            "all_files_git_blob_verified": True,
            "all_dataset_shapes_verified": True,
            "all_loader_outputs_verified": True,
            "source_worktree_clean": True,
            "file_count": len(verified_files),
            "dataset_count": len(verified_datasets),
            "total_source_input_bytes": total_bytes,
            "total_dataset_rows": sum(
                dataset["data_rows"] for dataset in verified_datasets.values()
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument(
        "--manifest", type=Path,
        default=Path("repro/configs/source_manifest.json"),
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_path = args.manifest if args.manifest.is_absolute() else ROOT / args.manifest
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    result = validate_manifest(args.source, manifest)
    result["manifest_sha256"] = file_sha256(manifest_path)

    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    temporary.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(output)
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
