#!/usr/bin/env python3
"""Content-pin the live OpenML task inputs used by the released CA loader."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import numpy as np
import openml


ROOT = Path(__file__).resolve().parents[2]
SOURCE_COMMIT = "66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974"
EXPECTED_TASK_ORDER = [361237, 361235, 361244, 361234]
TASK_FIELDS = {
    "task_id", "dataset_id", "dataset_name", "dataset_version", "target_name",
    "X_shape", "y_shape", "X_sha256", "y_sha256",
}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def array_sha256(array: np.ndarray) -> str:
    canonical = np.ascontiguousarray(array, dtype="<f8")
    descriptor = json.dumps(
        {"dtype": "float64-le", "shape": list(canonical.shape)},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    digest = hashlib.sha256()
    digest.update(descriptor)
    digest.update(b"\0")
    digest.update(canonical.tobytes(order="C"))
    return digest.hexdigest()


def validate_manifest_contract(manifest: dict) -> None:
    assert set(manifest) == {
        "source", "loader_path", "loader_sha256", "array_hash_encoding", "tasks"
    }
    assert manifest["source"] == f"Nabil-Ala/P2E_calibration@{SOURCE_COMMIT}"
    assert manifest["loader_path"] == "e-ca/utils.py"
    assert manifest["array_hash_encoding"] == (
        "sha256(canonical-json(shape,dtype=float64-le) + NUL + C-order-bytes)"
    )
    tasks = manifest["tasks"]
    assert [task["task_id"] for task in tasks] == EXPECTED_TASK_ORDER
    assert len({task["task_id"] for task in tasks}) == len(tasks) == 4
    for task in tasks:
        assert set(task) == TASK_FIELDS
        assert len(task["X_sha256"]) == len(task["y_sha256"]) == 64
        assert task["X_shape"][0] == task["y_shape"][0]


def load_released_utils(source: Path, loader_path: str):
    path = source / loader_path
    spec = importlib.util.spec_from_file_location("_p2e_ca_source_utils", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_inputs(source: Path, manifest: dict) -> dict:
    validate_manifest_contract(manifest)
    source = source.resolve(strict=True)
    commit = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    assert commit == SOURCE_COMMIT
    status = subprocess.run(
        ["git", "-C", str(source), "status", "--porcelain"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    assert status == ""
    loader_path = source / manifest["loader_path"]
    assert file_sha256(loader_path) == manifest["loader_sha256"]
    loader = load_released_utils(source, manifest["loader_path"])

    verified = []
    for expected in manifest["tasks"]:
        task_id = expected["task_id"]
        task = openml.tasks.get_task(task_id)
        dataset = openml.datasets.get_dataset(task.dataset_id, download_data=False)
        features, targets = loader.load_dataset(task_id)
        observed = {
            "task_id": task_id,
            "dataset_id": task.dataset_id,
            "dataset_name": dataset.name,
            "dataset_version": dataset.version,
            "target_name": task.target_name,
            "X_shape": list(features.shape),
            "y_shape": list(targets.shape),
            "X_sha256": array_sha256(features),
            "y_sha256": array_sha256(targets),
        }
        assert observed == expected, f"OpenML input drift for task {task_id}"
        assert np.isfinite(features).all() and np.isfinite(targets).all()
        verified.append(observed)

    return {
        "source": manifest["source"],
        "loader_sha256": manifest["loader_sha256"],
        "tasks": verified,
        "summary": {
            "all_task_metadata_verified": True,
            "all_processed_array_hashes_verified": True,
            "all_processed_values_finite": True,
            "source_worktree_clean": True,
            "task_count": len(verified),
            "total_rows": sum(task["X_shape"][0] for task in verified),
            "total_feature_values": sum(
                task["X_shape"][0] * task["X_shape"][1] for task in verified
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument(
        "--manifest", type=Path,
        default=Path("repro/configs/ca_input_manifest.json"),
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_path = args.manifest if args.manifest.is_absolute() else ROOT / args.manifest
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    result = verify_inputs(args.source, manifest)
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
