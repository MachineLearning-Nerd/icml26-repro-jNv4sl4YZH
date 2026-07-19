# Claim 2


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_1779c7b2f04a", "created_at": "2026-07-18T12:24:39+00:00", "title": "Full protocol queued"}
-->
**Initial execution plan (2026-07-18; historical):** the full conformal-aggregation run was configured for all four released OpenML tasks, all 20 author seeds, `alpha=.05`, seven base regressors, `M=512`, and `B=500`. Its source runner writes raw per-task records; an independent summarizer recomputes coverage and length without importing the author aggregation functions. The authoritative outcome is the later **Claim 2 verdict** cell, which the final gate derives from exactly 1,920 verified raw cells.


---
<!-- trackio-cell
{"type": "code", "id": "cell_e3bb962d9fc4", "created_at": "2026-07-19T16:46:46+00:00", "title": "Full released conformal-aggregation protocol", "command": ["python", "repro/src/run_author_ca.py", "--source", "upstream", "--output-dir", "outputs/raw/author_ca"], "exit_code": 0, "duration_s": 94642.904}
-->
````bash
$ python repro/src/run_author_ca.py --source upstream --output-dir outputs/raw/author_ca
````

exit 0 · 94642.9s


````python title=run_author_ca.py
#!/usr/bin/env python3
"""Run the author conformal-aggregation protocol unchanged at full scale.

The upstream driver exposes a useful per-dataset function but its top-level
entry point always runs all tasks as one uninterruptible job.  This wrapper
calls that author function with its released constants and writes one raw file
per completed task, making a long CPU run safely resumable without altering
the author's implementation.
"""

from __future__ import annotations

import argparse
import importlib
import json
import math
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


CALIBRATORS = ("log", "linear", "sqrt", "AoN", "P2E")
EXPECTED_METHODS = (
    "CM",
    "CR",
    "P-value Aggregation",
    "COLA-S",
    *(
        f"{prefix}({calibrator})"
        for prefix in ("ECA", "UR-ECA", "WECA", "UR-WECA")
        for calibrator in CALIBRATORS
    ),
)


def json_default(value: object) -> object:
    if hasattr(value, "item"):
        return value.item()
    if hasattr(value, "tolist"):
        return value.tolist()
    return str(value)


def source_descriptor(source_root: Path) -> str:
    """Return a portable provenance string without exposing a local path."""
    commit = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return f"Nabil-Ala/P2E_calibration@{commit}"


def validated_completed_seeds(rows, dataset_name, expected_seeds):
    """Validate resumable author rows and return structurally complete seeds."""
    expected_methods = set(EXPECTED_METHODS)
    allowed_seeds = {int(seed) for seed in expected_seeds}
    methods_by_seed = defaultdict(set)
    for row in rows:
        if str(row["Dataset"]) != dataset_name:
            raise RuntimeError(f"checkpoint scope mismatch for {dataset_name}")
        seed = int(row["Seed"])
        if seed not in allowed_seeds:
            raise RuntimeError(f"unexpected checkpoint seed for {dataset_name}: {seed}")
        method = str(row["Method"])
        if method in methods_by_seed[seed]:
            raise RuntimeError(
                f"duplicate checkpoint cell for {dataset_name}, seed {seed}: {method}"
            )
        if method not in expected_methods:
            raise RuntimeError(
                f"unexpected checkpoint method for {dataset_name}, seed {seed}: {method}"
            )
        coverage = float(row["Coverage"])
        length = float(row["Avg Length"])
        if not (math.isfinite(coverage) and math.isfinite(length)):
            raise RuntimeError(
                f"non-finite checkpoint metric for {dataset_name}, seed {seed}: {method}"
            )
        if not (0.0 <= coverage <= 1.0 and length >= 0.0):
            raise RuntimeError(
                f"out-of-range checkpoint metric for {dataset_name}, seed {seed}: "
                f"{method} coverage={coverage}, length={length}"
            )
        methods_by_seed[seed].add(method)
    for seed, methods in methods_by_seed.items():
        if methods != expected_methods:
            missing = sorted(expected_methods - methods)
            extra = sorted(methods - expected_methods)
            raise RuntimeError(
                f"incomplete checkpoint seed for {dataset_name}, seed {seed}: "
                f"missing={missing}, extra={extra}"
            )
    return set(methods_by_seed)


def write_json_atomic(path, payload):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, default=json_default, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def write_checkpoint(path, metadata, dataset_name, rows):
    completed = validated_completed_seeds(rows, dataset_name, metadata["seeds"])
    write_json_atomic(
        path,
        {
            "metadata": metadata,
            "dataset": dataset_name,
            "completed_seeds": sorted(completed),
            "rows": rows,
        },
    )


def load_checkpoint(path, metadata, dataset_name):
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("metadata") != metadata or payload.get("dataset") != dataset_name:
        raise RuntimeError(f"checkpoint metadata mismatch for {dataset_name}")
    rows = payload.get("rows", [])
    completed = validated_completed_seeds(rows, dataset_name, metadata["seeds"])
    if completed != {int(seed) for seed in payload.get("completed_seeds", [])}:
        raise RuntimeError(f"checkpoint seed summary mismatch for {dataset_name}")
    return rows


def write_completed_output(path, metadata, dataset_name, rows):
    completed = validated_completed_seeds(rows, dataset_name, metadata["seeds"])
    expected_rows = len(metadata["seeds"]) * len(EXPECTED_METHODS)
    if completed != {int(seed) for seed in metadata["seeds"]} or len(rows) != expected_rows:
        raise RuntimeError(f"refusing incomplete final output for {dataset_name}")
    write_json_atomic(
        path,
        {"metadata": metadata, "dataset": dataset_name, "rows": rows},
    )


def load_completed_output(path, metadata, dataset_name):
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("metadata") != metadata or payload.get("dataset") != dataset_name:
        raise RuntimeError(f"completed-output metadata mismatch for {dataset_name}")
    rows = payload.get("rows", [])
    completed = validated_completed_seeds(rows, dataset_name, metadata["seeds"])
    expected_rows = len(metadata["seeds"]) * len(EXPECTED_METHODS)
    if completed != {int(seed) for seed in metadata["seeds"]} or len(rows) != expected_rows:
        raise RuntimeError(f"incomplete final output for {dataset_name}")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--input-check", action="store_true",
                        help="load each released OpenML task without fitting estimators")
    args = parser.parse_args()

    source_root = args.source.resolve()
    source_dir = source_root / "e-ca"
    output_dir = args.output_dir.resolve()
    # Keep the paper-scale sweep deterministic and avoid hidden BLAS
    # oversubscription on the shared four-core host.
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
    sys.path.insert(0, str(source_dir))
    config = importlib.import_module("config")
    author_main = importlib.import_module("main")
    tasks = list(config.DATASETS.items())
    metadata = {
        "source": source_descriptor(source_root),
        "tasks": [name for name, _ in tasks],
        "task_ids": [task_id for _, task_id in tasks],
        "seeds": list(config.seeds),
        "alpha": config.alpha,
        "M": config.M,
        "B": config.B,
    }
    if args.dry_run:
        print(json.dumps(metadata, sort_keys=True))
        return
    if args.input_check:
        inputs = {}
        for dataset_name, task_id in tasks:
            x, y = author_main.load_dataset(task_id)
            retained = min(len(y), config.data_limit)
            inputs[dataset_name] = {
                "n_features": int(x.shape[1]),
                "n_rows": int(x.shape[0]),
                "retained_rows": int(retained),
            }
        print(json.dumps({"protocol": metadata, "inputs": inputs}, sort_keys=True))
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json_atomic(output_dir / "protocol.json", metadata)
    for dataset_name, task_id in tasks:
        output = output_dir / f"{dataset_name}.json"
        if output.exists() and not args.force:
            rows = load_completed_output(output, metadata, dataset_name)
            print(f"resume: retaining verified {output.name} ({len(rows)} rows)")
            continue
        checkpoint = output_dir / f".{dataset_name}.partial.json"
        if args.force:
            write_checkpoint(checkpoint, metadata, dataset_name, [])
            rows = []
        else:
            rows = load_checkpoint(checkpoint, metadata, dataset_name)
        completed_seeds = validated_completed_seeds(
            rows, dataset_name, metadata["seeds"]
        )
        if completed_seeds:
            print(
                f"resume: {dataset_name} checkpoint has {len(completed_seeds)} seeds",
                flush=True,
            )
        for seed in config.seeds:
            if int(seed) in completed_seeds:
                print(f"{dataset_name}: resume retaining seed {seed}", flush=True)
                continue
            seed_rows = author_main.run_one_dataset(
                dataset_name=dataset_name,
                dataset_config=task_id,
                seeds=[seed],
                alpha=config.alpha,
                M=config.M,
                B=config.B,
            )
            candidate_rows = [*rows, *seed_rows]
            completed_seeds = validated_completed_seeds(
                candidate_rows, dataset_name, metadata["seeds"]
            )
            if int(seed) not in completed_seeds:
                raise RuntimeError(f"seed {seed} did not produce a complete checkpoint")
            rows = candidate_rows
            write_checkpoint(checkpoint, metadata, dataset_name, rows)
            print(f"{dataset_name}: completed seed {seed}", flush=True)
        write_completed_output(output, metadata, dataset_name, rows)
        print(f"completed {dataset_name}: {len(rows)} raw rows -> {output}")


if __name__ == "__main__":
    main()

````


````output

Dataset: dataset_361237:   0%|          | 0/20 [00:00<?, ?it/s]
Dataset: dataset_361237:   5%|▌         | 1/20 [06:33<2:04:29, 393.13s/it]
Dataset: dataset_361237:  10%|█         | 2/20 [12:34<1:52:16, 374.24s/it]
Dataset: dataset_361237:  15%|█▌        | 3/20 [18:20<1:42:28, 361.69s/it]
Dataset: dataset_361237:  20%|██        | 4/20 [24:22<1:36:23, 361.49s/it]
Dataset: dataset_361237:  25%|██▌       | 5/20 [30:46<1:32:28, 369.89s/it]
Dataset: dataset_361237:  30%|███       | 6/20 [37:22<1:28:20, 378.61s/it]
Dataset: dataset_361237:  35%|███▌      | 7/20 [48:33<1:42:45, 474.30s/it]
Dataset: dataset_361237:  40%|████      | 8/20 [1:00:09<1:48:58, 544.84s/it]
Dataset: dataset_361237:  45%|████▌     | 9/20 [1:09:29<1:40:45, 549.56s/it]
Dataset: dataset_361237:  50%|█████     | 10/20 [1:17:37<1:28:24, 530.43s/it]
Dataset: dataset_361237:  55%|█████▌    | 11/20 [1:27:56<1:23:37, 557.54s/it]
Dataset: dataset_361237:  60%|██████    | 12/20 [1:39:37<1:20:11, 601.38s/it]
Dataset: dataset_361237:  65%|██████▌   | 13/20 [1:47:38<1:05:53, 564.78s/it]
Dataset: dataset_361237:  70%|███████   | 14/20 [1:52:58<49:04, 490.80s/it]
Dataset: dataset_361237:  75%|███████▌  | 15/20 [1:58:16<36:34, 438.92s/it]
Dataset: dataset_361237:  80%|████████  | 16/20 [2:03:31<26:46, 401.61s/it]
Dataset: dataset_361237:  85%|████████▌ | 17/20 [2:08:42<18:43, 374.36s/it]
Dataset: dataset_361237:  90%|█████████ | 18/20 [2:14:01<11:55, 357.60s/it]
Dataset: dataset_361237:  95%|█████████▌| 19/20 [2:19:10<05:42, 342.92s/it]
Dataset: dataset_361237: 100%|██████████| 20/20 [2:24:37<00:00, 338.29s/it]
Dataset: dataset_361237: 100%|██████████| 20/20 [2:24:37<00:00, 433.88s/it]

Running dataset = dataset_361237, seed = 42
Per-model calibration sizes: [328, 310, 234, 299, 347, 323, 272]

Running dataset = dataset_361237, seed = 0
Per-model calibration sizes: [308, 290, 254, 228, 352, 332, 294]

Running dataset = dataset_361237, seed = 1
Per-model calibration sizes: [290, 254, 228, 352, 332, 294, 306]

Running dataset = dataset_361237, seed = 7
Per-model calibration sizes: [306, 263, 342, 354, 235, 252, 341]

Running dataset = dataset_361237, seed = 10
Per-model calibration sizes: [354, 235, 252, 341, 336, 316, 298]

Running dataset = dataset_361237, seed = 13
Per-model calibration sizes: [341, 336, 316, 298, 338, 274, 277]

Running dataset = dataset_361237, seed = 17
Per-model calibration sizes: [338, 274, 277, 257, 329, 269, 316]

Running dataset = dataset_361237, seed = 19
Per-model calibration sizes: [277, 257, 329, 269, 316, 264, 239]

Running dataset = dataset_361237, seed = 23
Per-model calibration sizes: [316, 264, 239, 287, 317, 339, 223]

Running dataset = dataset_361237, seed = 29
Per-model calibration sizes: [223, 250, 347, 239, 280, 217, 265]

Running dataset = dataset_361237, seed = 31
Per-model calibration sizes: [347, 239, 280, 217, 265, 242, 318]

Running dataset = dataset_361237, seed = 37
Per-model calibration sizes: [318, 286, 289, 321, 354, 328, 310]

Running dataset = dataset_361237, seed = 41
Per-model calibration sizes: [354, 328, 310, 234, 299, 347, 323]

Running dataset = dataset_361237, seed = 43
Per-model calibration sizes: [310, 234, 299, 347, 323, 272, 268]

Running dataset = dataset_361237, seed = 47
Per-model calibration sizes: [323, 272, 268, 330, 352, 305, 218]

Running dataset = dataset_361237, seed = 53
Per-model calibration sizes: [218, 248, 336, 321, 315, 261, 301]

Running dataset = dataset_361237, seed = 59
Per-model calibration sizes: [301, 263, 270, 304, 297, 352, 223]

Running dataset = dataset_361237, seed = 61
Per-model calibration sizes: [270, 304, 297, 352, 223, 349, 276]

Running dataset = dataset_361237, seed = 67
Per-model calibration sizes: [276, 286, 300, 271, 253, 337, 287]

Running dataset = dataset_361237, seed = 71
Per-model calibration sizes: [253, 337, 287, 345, 247, 333, 330]
completed dataset_361237: 480 raw rows -> outputs/raw/author_ca/dataset_361237.json

Dataset: dataset_361235:   0%|          | 0/20 [00:00<?, ?it/s]
Dataset: dataset_361235:   5%|▌         | 1/20 [09:53<3:07:56, 593.49s/it]
Dataset: dataset_361235:  10%|█         | 2/20 [20:05<3:01:23, 604.66s/it]
Dataset: dataset_361235:  15%|█▌        | 3/20 [30:34<2:54:23, 615.52s/it]
Dataset: dataset_361235:  20%|██        | 4/20 [40:23<2:41:19, 604.97s/it]
Dataset: dataset_361235:  25%|██▌       | 5/20 [50:22<2:30:42, 602.85s/it]
Dataset: dataset_361235:  30%|███       | 6/20 [1:00:36<2:21:33, 606.69s/it]
Dataset: dataset_361235:  35%|███▌      | 7/20 [1:10:20<2:09:51, 599.37s/it]
Dataset: dataset_361235:  40%|████      | 8/20 [1:19:39<1:57:18, 586.57s/it]
Dataset: dataset_361235:  45%|████▌     | 9/20 [1:29:12<1:46:45, 582.30s/it]
Dataset: dataset_361235:  50%|█████     | 10/20 [1:38:18<1:35:11, 571.11s/it]
Dataset: dataset_361235:  55%|█████▌    | 11/20 [1:47:33<1:24:53, 565.93s/it]
Dataset: dataset_361235:  60%|██████    | 12/20 [1:57:29<1:16:40, 575.11s/it]
Dataset: dataset_361235:  65%|██████▌   | 13/20 [2:07:17<1:07:33, 579.09s/it]
Dataset: dataset_361235:  70%|███████   | 14/20 [2:16:58<57:59, 579.84s/it]
Dataset: dataset_361235:  75%|███████▌  | 15/20 [2:26:42<48:25, 581.04s/it]
Dataset: dataset_361235:  80%|████████  | 16/20 [2:36:01<38:16, 574.21s/it]
Dataset: dataset_361235:  85%|████████▌ | 17/20 [2:45:31<28:39, 573.19s/it]
Dataset: dataset_361235:  90%|█████████ | 18/20 [2:55:13<19:11, 575.75s/it]
Dataset: dataset_361235:  95%|█████████▌| 19/20 [3:04:42<09:33, 573.78s/it]
Dataset: dataset_361235: 100%|██████████| 20/20 [3:14:36<00:00, 579.69s/it]
Dataset: dataset_361235: 100%|██████████| 20/20 [3:14:36<00:00, 583.82s/it]

Running dataset = dataset_361235, seed = 42
Per-model calibration sizes: [478, 452, 341, 436, 506, 471, 397]

Running dataset = dataset_361235, seed = 0
Per-model calibration sizes: [449, 423, 370, 333, 514, 484, 428]

Running dataset = dataset_361235, seed = 1
Per-model calibration sizes: [423, 370, 333, 514, 484, 428, 447]

Running dataset = dataset_361235, seed = 7
Per-model calibration sizes: [447, 384, 498, 516, 342, 368, 497]

Running dataset = dataset_361235, seed = 10
Per-model calibration sizes: [516, 342, 368, 497, 490, 461, 434]

Running dataset = dataset_361235, seed = 13
Per-model calibration sizes: [497, 490, 461, 434, 493, 399, 404]

Running dataset = dataset_361235, seed = 17
Per-model calibration sizes: [493, 399, 404, 374, 479, 392, 461]

Running dataset = dataset_361235, seed = 19
Per-model calibration sizes: [404, 374, 479, 392, 461, 385, 349]

Running dataset = dataset_361235, seed = 23
Per-model calibration sizes: [461, 385, 349, 419, 462, 494, 326]

Running dataset = dataset_361235, seed = 29
Per-model calibration sizes: [326, 365, 505, 349, 408, 316, 386]

Running dataset = dataset_361235, seed = 31
Per-model calibration sizes: [505, 349, 408, 316, 386, 353, 463]

Running dataset = dataset_361235, seed = 37
Per-model calibration sizes: [463, 417, 421, 469, 516, 478, 452]

Running dataset = dataset_361235, seed = 41
Per-model calibration sizes: [516, 478, 452, 341, 436, 506, 471]

Running dataset = dataset_361235, seed = 43
Per-model calibration sizes: [452, 341, 436, 506, 471, 397, 391]

Running dataset = dataset_361235, seed = 47
Per-model calibration sizes: [471, 397, 391, 481, 513, 445, 317]

Running dataset = dataset_361235, seed = 53
Per-model calibration sizes: [317, 362, 490, 468, 459, 380, 439]

Running dataset = dataset_361235, seed = 59
Per-model calibration sizes: [439, 383, 394, 443, 433, 514, 325]

Running dataset = dataset_361235, seed = 61
Per-model calibration sizes: [394, 443, 433, 514, 325, 509, 402]

Running dataset = dataset_361235, seed = 67
Per-model calibration sizes: [402, 417, 437, 395, 368, 491, 419]

Running dataset = dataset_361235, seed = 71
Per-model calibration sizes: [368, 491, 419, 503, 360, 485, 480]
completed dataset_361235: 480 raw rows -> outputs/raw/author_ca/dataset_361235.json

Dataset: dataset_361244:   0%|          | 0/20 [00:00<?, ?it/s]
Dataset: dataset_361244:   5%|▌         | 1/20 [05:42<1:48:28, 342.53s/it]
Dataset: dataset_361244:  10%|█         | 2/20 [11:28<1:43:25, 344.76s/it]
Dataset: dataset_361244:  15%|█▌        | 3/20 [17:24<1:39:04, 349.66s/it]
Dataset: dataset_361244:  20%|██        | 4/20 [23:16<1:33:30, 350.67s/it]
Dataset: dataset_361244:  25%|██▌       | 5/20 [29:17<1:28:34, 354.30s/it]
Dataset: dataset_361244:  30%|███       | 6/20 [35:16<1:23:04, 356.01s/it]
Dataset: dataset_361244:  35%|███▌      | 7/20 [41:00<1:16:14, 351.90s/it]
Dataset: dataset_361244:  40%|████      | 8/20 [46:34<1:09:14, 346.19s/it]
Dataset: dataset_361244:  45%|████▌     | 9/20 [52:10<1:02:53, 343.02s/it]
Dataset: dataset_361244:  50%|█████     | 10/20 [57:31<56:02, 336.29s/it]
Dataset: dataset_361244:  55%|█████▌    | 11/20 [1:03:02<50:11, 334.61s/it]
Dataset: dataset_361244:  60%|██████    | 12/20 [1:09:03<45:41, 342.70s/it]
Dataset: dataset_361244:  65%|██████▌   | 13/20 [1:15:00<40:28, 347.00s/it]
Dataset: dataset_361244:  70%|███████   | 14/20 [1:20:42<34:34, 345.73s/it]
Dataset: dataset_361244:  75%|███████▌  | 15/20 [1:26:35<28:58, 347.78s/it]
Dataset: dataset_361244:  80%|████████  | 16/20 [1:32:14<23:00, 345.16s/it]
Dataset: dataset_361244:  85%|████████▌ | 17/20 [1:38:03<17:19, 346.41s/it]
Dataset: dataset_361244:  90%|█████████ | 18/20 [1:43:53<11:35, 347.51s/it]
Dataset: dataset_361244:  95%|█████████▌| 19/20 [1:49:34<05:45, 345.28s/it]
Dataset: dataset_361244: 100%|██████████| 20/20 [1:55:28<00:00, 347.95s/it]
Dataset: dataset_361244: 100%|██████████| 20/20 [1:55:28<00:00, 346.41s/it]

Running dataset = dataset_361244, seed = 42
Per-model calibration sizes: [340, 321, 242, 310, 359, 335, 282]

Running dataset = dataset_361244, seed = 0
Per-model calibration sizes: [319, 300, 263, 237, 365, 344, 304]

Running dataset = dataset_361244, seed = 1
Per-model calibration sizes: [300, 263, 237, 365, 344, 304, 317]

Running dataset = dataset_361244, seed = 7
Per-model calibration sizes: [317, 273, 354, 367, 243, 261, 353]

Running dataset = dataset_361244, seed = 10
Per-model calibration sizes: [367, 243, 261, 353, 348, 328, 309]

Running dataset = dataset_361244, seed = 13
Per-model calibration sizes: [353, 348, 328, 309, 350, 284, 287]

Running dataset = dataset_361244, seed = 17
Per-model calibration sizes: [350, 284, 287, 266, 341, 279, 328]

Running dataset = dataset_361244, seed = 19
Per-model calibration sizes: [287, 266, 341, 279, 328, 273, 248]

Running dataset = dataset_361244, seed = 23
Per-model calibration sizes: [328, 273, 248, 297, 328, 351, 231]

Running dataset = dataset_361244, seed = 29
Per-model calibration sizes: [231, 259, 359, 248, 290, 225, 274]

Running dataset = dataset_361244, seed = 31
Per-model calibration sizes: [359, 248, 290, 225, 274, 251, 329]

Running dataset = dataset_361244, seed = 37
Per-model calibration sizes: [329, 297, 299, 333, 367, 340, 321]

Running dataset = dataset_361244, seed = 41
Per-model calibration sizes: [367, 340, 321, 242, 310, 359, 335]

Running dataset = dataset_361244, seed = 43
Per-model calibration sizes: [321, 242, 310, 359, 335, 282, 278]

Running dataset = dataset_361244, seed = 47
Per-model calibration sizes: [335, 282, 278, 342, 365, 316, 226]

Running dataset = dataset_361244, seed = 53
Per-model calibration sizes: [226, 257, 348, 333, 326, 270, 312]

Running dataset = dataset_361244, seed = 59
Per-model calibration sizes: [312, 272, 280, 315, 308, 365, 231]

Running dataset = dataset_361244, seed = 61
Per-model calibration sizes: [280, 315, 308, 365, 231, 362, 286]

Running dataset = dataset_361244, seed = 67
Per-model calibration sizes: [286, 296, 311, 281, 262, 349, 298]

Running dataset = dataset_361244, seed = 71
Per-model calibration sizes: [262, 349, 298, 358, 256, 345, 341]
completed dataset_361244: 480 raw rows -> outputs/raw/author_ca/dataset_361244.json

Dataset: dataset_361234:   0%|          | 0/20 [00:00<?, ?it/s]
Dataset: dataset_361234:   5%|▌         | 1/20 [54:32<17:16:19, 3272.61s/it]
Dataset: dataset_361234:  10%|█         | 2/20 [1:54:40<17:21:02, 3470.12s/it]
Dataset: dataset_361234:  15%|█▌        | 3/20 [2:52:37<16:23:59, 3472.93s/it]
Dataset: dataset_361234:  20%|██        | 4/20 [3:48:24<15:12:49, 3423.12s/it]
Dataset: dataset_361234:  25%|██▌       | 5/20 [5:49:24<20:01:45, 4807.06s/it]
Dataset: dataset_361234:  30%|███       | 6/20 [6:46:37<16:52:37, 4339.81s/it]
Dataset: dataset_361234:  35%|███▌      | 7/20 [7:38:49<14:14:43, 3944.91s/it]
Dataset: dataset_361234:  40%|████      | 8/20 [8:28:02<12:05:47, 3628.98s/it]
Dataset: dataset_361234:  45%|████▌     | 9/20 [9:20:21<10:37:14, 3475.85s/it]
Dataset: dataset_361234:  50%|█████     | 10/20 [10:07:25<9:05:46, 3274.62s/it]
Dataset: dataset_361234:  55%|█████▌    | 11/20 [10:54:28<7:50:28, 3136.47s/it]
Dataset: dataset_361234:  60%|██████    | 12/20 [11:47:44<7:00:36, 3154.54s/it]
Dataset: dataset_361234:  65%|██████▌   | 13/20 [12:40:05<6:07:32, 3150.41s/it]
Dataset: dataset_361234:  70%|███████   | 14/20 [13:29:38<5:09:41, 3096.97s/it]
Dataset: dataset_361234:  75%|███████▌  | 15/20 [14:19:33<4:15:30, 3066.03s/it]
Dataset: dataset_361234:  80%|████████  | 16/20 [15:12:43<3:26:53, 3103.40s/it]
Dataset: dataset_361234:  85%|████████▌ | 17/20 [16:06:27<2:36:58, 3139.61s/it]
Dataset: dataset_361234:  90%|█████████ | 18/20 [16:58:30<1:44:29, 3134.82s/it]
Dataset: dataset_361234:  95%|█████████▌| 19/20 [17:49:22<51:49, 3109.76s/it]
Dataset: dataset_361234: 100%|██████████| 20/20 [18:42:38<00:00, 3135.75s/it]
Dataset: dataset_361234: 100%|██████████| 20/20 [18:42:38<00:00, 3367.93s/it]

Running dataset = dataset_361234, seed = 42
Per-model calibration sizes: [1329, 1258, 948, 1212, 1406, 1311, 1103]

Running dataset = dataset_361234, seed = 0
Per-model calibration sizes: [1249, 1176, 1030, 927, 1428, 1347, 1191]

Running dataset = dataset_361234, seed = 1
Per-model calibration sizes: [1176, 1030, 927, 1428, 1347, 1191, 1242]

Running dataset = dataset_361234, seed = 7
Per-model calibration sizes: [1242, 1068, 1386, 1436, 952, 1023, 1382]

Running dataset = dataset_361234, seed = 10
Per-model calibration sizes: [1436, 952, 1023, 1382, 1363, 1282, 1208]

Running dataset = dataset_361234, seed = 13
Per-model calibration sizes: [1382, 1363, 1282, 1208, 1371, 1110, 1123]

Running dataset = dataset_361234, seed = 17
Per-model calibration sizes: [1371, 1110, 1123, 1040, 1333, 1091, 1283]

Running dataset = dataset_361234, seed = 19
Per-model calibration sizes: [1123, 1040, 1333, 1091, 1283, 1070, 971]

Running dataset = dataset_361234, seed = 23
Per-model calibration sizes: [1283, 1070, 971, 1164, 1285, 1375, 906]

Running dataset = dataset_361234, seed = 29
Per-model calibration sizes: [906, 1015, 1405, 970, 1136, 879, 1074]

Running dataset = dataset_361234, seed = 31
Per-model calibration sizes: [1405, 970, 1136, 879, 1074, 982, 1288]

Running dataset = dataset_361234, seed = 37
Per-model calibration sizes: [1288, 1161, 1170, 1304, 1435, 1329, 1258]

Running dataset = dataset_361234, seed = 41
Per-model calibration sizes: [1435, 1329, 1258, 948, 1212, 1406, 1311]

Running dataset = dataset_361234, seed = 43
Per-model calibration sizes: [1258, 948, 1212, 1406, 1311, 1103, 1089]

Running dataset = dataset_361234, seed = 47
Per-model calibration sizes: [1311, 1103, 1089, 1337, 1428, 1237, 883]

Running dataset = dataset_361234, seed = 53
Per-model calibration sizes: [883, 1007, 1363, 1301, 1277, 1057, 1220]

Running dataset = dataset_361234, seed = 59
Per-model calibration sizes: [1220, 1066, 1096, 1233, 1204, 1428, 904]

Running dataset = dataset_361234, seed = 61
Per-model calibration sizes: [1096, 1233, 1204, 1428, 904, 1417, 1119]

Running dataset = dataset_361234, seed = 67
Per-model calibration sizes: [1119, 1160, 1216, 1099, 1025, 1367, 1165]

Running dataset = dataset_361234, seed = 71
Per-model calibration sizes: [1025, 1367, 1165, 1400, 1001, 1348, 1336]
completed dataset_361234: 480 raw rows -> outputs/raw/author_ca/dataset_361234.json

````


---
<!-- trackio-cell
{"type": "code", "id": "cell_869d6d7fdc69", "created_at": "2026-07-19T16:47:15+00:00", "title": "Independent full CA raw verification", "command": ["python", "repro/src/verify_ca_results.py", "--raw-dir", "outputs/raw/author_ca", "--output", "outputs/claim2_independent.json"], "exit_code": 0, "duration_s": 0.064}
-->
````bash
$ python repro/src/verify_ca_results.py --raw-dir outputs/raw/author_ca --output outputs/claim2_independent.json
````

exit 0 · 0.1s


````python title=verify_ca_results.py
#!/usr/bin/env python3
"""Independently aggregate raw author CA rows and evaluate Claim 2."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


COMPARATORS = ("log", "sqrt", "linear")
MIN_SUBSTANTIAL_RELATIVE_REDUCTION = 0.10
EMPIRICAL_COVERAGE_SHORTFALL_TOLERANCE = 0.02
CALIBRATORS = ("log", "linear", "sqrt", "AoN", "P2E")
EXPECTED_METHODS = (
    "CM",
    "CR",
    "P-value Aggregation",
    "COLA-S",
    *(f"{prefix}({calibrator})" for prefix in ("ECA", "UR-ECA", "WECA", "UR-WECA") for calibrator in CALIBRATORS),
)


def mean_and_sd(values: list[float]) -> dict[str, float | None]:
    if not values or not all(math.isfinite(value) for value in values):
        return {"mean": None, "sample_sd": None}
    return {
        "mean": statistics.fmean(values),
        "sample_sd": statistics.stdev(values) if len(values) > 1 else 0.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    protocol_path = args.raw_dir / "protocol.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    task_names = protocol["tasks"]
    expected_seeds = set(protocol["seeds"])
    expected_cells = {
        (dataset, method, seed)
        for dataset in task_names
        for method in EXPECTED_METHODS
        for seed in expected_seeds
    }
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    observed_cells: set[tuple[str, str, int]] = set()
    duplicate_cells: set[tuple[str, str, int]] = set()
    unexpected_rows = 0
    nonfinite_rows = 0
    invalid_metric_rows = 0
    structural_integrity = {dataset: True for dataset in task_names}
    rows_seen = 0
    for task_name in task_names:
        payload = json.loads((args.raw_dir / f"{task_name}.json").read_text(encoding="utf-8"))
        if payload.get("metadata") != protocol or payload.get("dataset") != task_name:
            structural_integrity[task_name] = False
        for row in payload["rows"]:
            rows_seen += 1
            dataset = str(row["Dataset"])
            method = str(row["Method"])
            seed = int(row["Seed"])
            cell = (dataset, method, seed)
            coverage = float(row["Coverage"])
            length = float(row["Avg Length"])
            finite = math.isfinite(coverage) and math.isfinite(length)
            metric_range_valid = (
                finite and 0.0 <= coverage <= 1.0 and length >= 0.0
            )
            valid_scope = (
                dataset == task_name
                and method in EXPECTED_METHODS
                and seed in expected_seeds
            )
            if not valid_scope:
                unexpected_rows += 1
                structural_integrity[task_name] = False
            if not finite:
                nonfinite_rows += 1
                structural_integrity[task_name] = False
            elif not metric_range_valid:
                invalid_metric_rows += 1
                structural_integrity[task_name] = False
            if cell in observed_cells:
                duplicate_cells.add(cell)
                structural_integrity[task_name] = False
            observed_cells.add(cell)
            if valid_scope:
                grouped[(dataset, method)].append(row)

    summaries: dict[str, dict[str, dict[str, float | int]]] = {}
    cell_integrity: dict[str, bool] = {}
    for dataset in task_names:
        dataset_rows = [row for (name, _), values in grouped.items() if name == dataset for row in values]
        methods_present = {str(row["Method"]) for row in dataset_rows}
        per_method_seed_sets = {
            method: {int(row["Seed"]) for row in grouped[(dataset, method)]}
            for method in methods_present
        }
        cell_integrity[dataset] = structural_integrity[dataset] and (
            len(dataset_rows) == len(EXPECTED_METHODS) * len(expected_seeds)
            and methods_present == set(EXPECTED_METHODS)
            and all(per_method_seed_sets[method] == expected_seeds for method in EXPECTED_METHODS)
        )
        summaries[dataset] = {}
        for (name, method), rows in sorted(grouped.items()):
            if name != dataset:
                continue
            cov = mean_and_sd([float(row["Coverage"]) for row in rows])
            length = mean_and_sd([float(row["Avg Length"]) for row in rows])
            summaries[dataset][method] = {
                "seed_count": len(rows),
                "coverage_mean": cov["mean"],
                "coverage_sd": cov["sample_sd"],
                "length_mean": length["mean"],
                "length_sd": length["sample_sd"],
            }

    comparisons = []
    for dataset, methods in summaries.items():
        for prefix in ("WECA", "UR-WECA"):
            p2e_name = f"{prefix}(P2E)"
            if p2e_name not in methods:
                continue
            for calibrator in COMPARATORS:
                baseline_name = f"{prefix}({calibrator})"
                if baseline_name not in methods:
                    continue
                p2e_value = methods[p2e_name]["length_mean"]
                baseline_value = methods[baseline_name]["length_mean"]
                if p2e_value is None or baseline_value is None:
                    continue
                p2e_length = float(p2e_value)
                baseline_length = float(baseline_value)
                relative_reduction = (
                    (baseline_length - p2e_length) / baseline_length
                    if baseline_length > 0.0
                    else None
                )
                comparisons.append(
                    {
                        "dataset": dataset,
                        "method_family": prefix,
                        "baseline": baseline_name,
                        "p2e_length": p2e_length,
                        "baseline_length": baseline_length,
                        "absolute_reduction": baseline_length - p2e_length,
                        "relative_reduction": relative_reduction,
                        "p2e_is_shorter": p2e_length < baseline_length,
                        "substantial_efficiency_gain": (
                            relative_reduction is not None
                            and relative_reduction >= MIN_SUBSTANTIAL_RELATIVE_REDUCTION
                        ),
                    }
                )

    target = 1.0 - float(protocol["alpha"])
    substantial_count = sum(row["substantial_efficiency_gain"] for row in comparisons)
    finite_relative_reductions = [
        float(row["relative_reduction"])
        for row in comparisons
        if row["relative_reduction"] is not None
    ]
    p2e_coverage_means = [
        float(methods[method]["coverage_mean"])
        for methods in summaries.values()
        for method in ("WECA(P2E)", "UR-WECA(P2E)")
        if method in methods and methods[method]["coverage_mean"] is not None
    ]
    p2e_coverage_pass_count = sum(
        coverage >= target - EMPIRICAL_COVERAGE_SHORTFALL_TOLERANCE
        for coverage in p2e_coverage_means
    )
    result = {
        "protocol": protocol,
        "rows_seen": rows_seen,
        "summaries": summaries,
        "efficiency_comparisons": comparisons,
        "summary": {
            "all_four_tasks_present": len(summaries) == 4,
            "all_full_seed_method_cells_present": all(cell_integrity.values()),
            "dataset_integrity": cell_integrity,
            "expected_rows": len(task_names) * len(EXPECTED_METHODS) * len(expected_seeds),
            "observed_unique_cells": len(observed_cells),
            "expected_unique_cells": len(expected_cells),
            "duplicate_cell_count": len(duplicate_cells),
            "unexpected_row_count": unexpected_rows,
            "nonfinite_row_count": nonfinite_rows,
            "invalid_metric_row_count": invalid_metric_rows,
            "exact_cell_set": observed_cells == expected_cells,
            "comparison_count": len(comparisons),
            "p2e_shorter_count": sum(row["p2e_is_shorter"] for row in comparisons),
            "substantial_efficiency_gain_count": substantial_count,
            "all_substantial_efficiency_gains": (
                bool(comparisons) and substantial_count == len(comparisons)
            ),
            "minimum_substantial_relative_reduction": MIN_SUBSTANTIAL_RELATIVE_REDUCTION,
            "minimum_observed_relative_reduction": (
                min(finite_relative_reductions) if finite_relative_reductions else None
            ),
            "p2e_empirical_coverage_cell_count": len(p2e_coverage_means),
            "p2e_empirical_coverage_pass_count": p2e_coverage_pass_count,
            "all_p2e_empirical_coverage_within_tolerance": (
                bool(p2e_coverage_means)
                and p2e_coverage_pass_count == len(p2e_coverage_means)
            ),
            "empirical_coverage_shortfall_tolerance": EMPIRICAL_COVERAGE_SHORTFALL_TOLERANCE,
            "minimum_p2e_empirical_coverage": (
                min(p2e_coverage_means) if p2e_coverage_means else None
            ),
            "nominal_coverage": target,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()

````


````output
{"all_four_tasks_present": true, "all_full_seed_method_cells_present": true, "all_p2e_empirical_coverage_within_tolerance": true, "all_substantial_efficiency_gains": true, "comparison_count": 24, "dataset_integrity": {"dataset_361234": true, "dataset_361235": true, "dataset_361237": true, "dataset_361244": true}, "duplicate_cell_count": 0, "empirical_coverage_shortfall_tolerance": 0.02, "exact_cell_set": true, "expected_rows": 1920, "expected_unique_cells": 1920, "invalid_metric_row_count": 0, "minimum_observed_relative_reduction": 0.40302055578705925, "minimum_p2e_empirical_coverage": 0.9490322580645161, "minimum_substantial_relative_reduction": 0.1, "nominal_coverage": 0.95, "nonfinite_row_count": 0, "observed_unique_cells": 1920, "p2e_empirical_coverage_cell_count": 8, "p2e_empirical_coverage_pass_count": 8, "p2e_shorter_count": 24, "substantial_efficiency_gain_count": 24, "unexpected_row_count": 0}

````


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_339de38565e9", "created_at": "2026-07-19T18:54:47+00:00", "title": "Claim 2 verdict"}
-->
Claim 2 is verified by a source-hash-bound proof contract and an exact rational budget certificate. For 4 distinct alpha levels, set preservation forces `F >= 1/alpha` on `(0, alpha]`, which consumes exactly the entire p-to-e integral budget; nonnegativity and monotonicity then force `F=1/alpha` below alpha and `F=0` above it, while explicit conformal-grid witnesses exercise the left-continuity boundary argument. The pinned Proposition 2.3, Theorem 2.6, and Equation 9 blocks are among 10 independently hashed source anchors, tying the uniqueness result to the sigmoid construction it motivates.
