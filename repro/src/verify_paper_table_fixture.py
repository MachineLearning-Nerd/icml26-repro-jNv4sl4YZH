#!/usr/bin/env python3
"""Verify the paper-number fixture directly against pinned primary arXiv TeX."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import tarfile
import urllib.request
from pathlib import Path


SOURCE_URL = "https://export.arxiv.org/e-print/2606.03600v1"
SOURCE_ARCHIVE_SHA256 = "f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db"
MAIN_TEX_SHA256 = "49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857"
DATASETS = ("boston", "abalone", "parkinson")
MODELS = ("OLS", "RF", "Lasso")
FIRST_PANEL_METHODS = (
    "cross",
    "e-mod-cross",
    "u-mod-cross",
    "eu-mod-cross",
    "ECCP (2α)",
)
SECOND_PANEL_METHODS = (
    "ECCP",
    "ECCP(ind)",
    "ECCP(log)",
    "ECCP(sqrt)",
    "ECCP(linear)",
)
PAIR_PATTERN = re.compile(
    r"\$?\s*(-?\d+(?:\.\d+)?)\s*\$?\s*\\pm\s*\$?\s*"
    r"(-?\d+(?:\.\d+)?)\s*\$?"
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_primary_tex(source_url: str = SOURCE_URL) -> tuple[bytes, bytes]:
    request = urllib.request.Request(
        source_url,
        headers={"User-Agent": "icml26-reproduction-audit/1.0"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        archive = response.read()
    if sha256_bytes(archive) != SOURCE_ARCHIVE_SHA256:
        raise RuntimeError("arXiv source archive hash drift")
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:*") as bundle:
        matches = [member for member in bundle.getmembers() if member.name == "main.tex"]
        if len(matches) != 1:
            raise RuntimeError(f"expected one main.tex, found {len(matches)}")
        extracted = bundle.extractfile(matches[0])
        if extracted is None:
            raise RuntimeError("main.tex is not a regular archive member")
        tex = extracted.read()
    if sha256_bytes(tex) != MAIN_TEX_SHA256:
        raise RuntimeError("main.tex hash drift")
    return archive, tex


def parse_pairs(line: str, expected: int) -> list[tuple[float, float]]:
    pairs = [(float(mean), float(sd)) for mean, sd in PAIR_PATTERN.findall(line)]
    if len(pairs) != expected:
        raise RuntimeError(
            f"expected {expected} mean/SD pairs, found {len(pairs)} in {line!r}"
        )
    return pairs


def parse_ca_table(tex: str) -> dict[str, dict[str, dict[str, float]]]:
    label = tex.index(r"\label{table:e-CA_results}")
    start = tex.rindex(r"\begin{table*}", 0, label)
    end = tex.index(r"\end{table*}", label)
    block = tex[start:end]
    expected_header = (
        r"Method & \multicolumn{2}{c}{361234} & \multicolumn{2}{c}{361235} & "
        r"\multicolumn{2}{c}{361237} & \multicolumn{2}{c}{361244}"
    )
    if expected_header not in block:
        raise RuntimeError("CA paper-table dataset order drift")
    dataset_keys = (
        "dataset_361234",
        "dataset_361235",
        "dataset_361237",
        "dataset_361244",
    )
    output = {dataset: {} for dataset in dataset_keys}
    for source_method, config_method in (
        ("WECA", "WECA(P2E)"),
        ("UR-WECA", "UR-WECA(P2E)"),
    ):
        rows = [
            line.strip()
            for line in block.splitlines()
            if line.strip().startswith(source_method + " &")
        ]
        if len(rows) != 1:
            raise RuntimeError(f"expected one active {source_method} paper row")
        pairs = parse_pairs(rows[0], 8)
        for index, dataset in enumerate(dataset_keys):
            coverage, length = pairs[2 * index : 2 * index + 2]
            output[dataset][config_method] = {
                "coverage_mean": coverage[0],
                "coverage_sd": coverage[1],
                "length_mean": length[0],
                "length_sd": length[1],
            }
    return output


def dataset_section(tex: str, dataset: str) -> str:
    markers = {
        "boston": ("% boston K=15", "% Abalone K=15"),
        "abalone": ("% Abalone K=15", "% parkinson K=20"),
        "parkinson": ("% parkinson K=20", r"\section{Details on the P2E calibrator}"),
    }
    start_marker, end_marker = markers[dataset]
    start = tex.index(start_marker)
    end = tex.index(end_marker, start + len(start_marker))
    return tex[start:end]


def parse_ccp_panel(
    block: str, methods: tuple[str, ...]
) -> dict[str, dict[str, dict[str, float]]]:
    output = {model: {method: {} for method in methods} for model in MODELS}
    current_model: str | None = None
    row_count = 0
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if "& Size &" not in line and "& Cov. &" not in line:
            continue
        fields = [field.strip() for field in line.split("&")]
        if fields[0] in MODELS:
            current_model = fields[0]
        if current_model is None:
            raise RuntimeError("CCP metric row appears before a base model")
        metric = fields[1]
        pairs = parse_pairs(line, len(methods))
        mean_key, sd_key = (
            ("length_mean", "length_sd")
            if metric == "Size"
            else ("coverage_mean", "coverage_sd")
        )
        for method, (mean, sd) in zip(methods, pairs):
            output[current_model][method][mean_key] = mean
            output[current_model][method][sd_key] = sd
        row_count += 1
    if row_count != len(MODELS) * 2:
        raise RuntimeError(f"expected six model/metric rows, found {row_count}")
    if not all(
        set(metrics) == {"coverage_mean", "coverage_sd", "length_mean", "length_sd"}
        for model in output.values()
        for metrics in model.values()
    ):
        raise RuntimeError("incomplete CCP method metrics")
    return output


def normalized_ccp_header(block: str) -> list[str]:
    rows = [line.strip() for line in block.splitlines() if line.strip().startswith("Base &")]
    if len(rows) != 1:
        raise RuntimeError(f"expected one CCP header, found {len(rows)}")
    fields = [field.strip() for field in rows[0].removesuffix(r"\\").split("&")]
    return [re.sub(r"_\{([0-9])\}", r"_\1", field) for field in fields]


def parse_ccp_tables(tex: str) -> dict[str, dict[str, dict[str, dict[str, float]]]]:
    output = {}
    for dataset in DATASETS:
        tables = re.findall(
            r"\\begin\{table\}\[H\](.*?)\\end\{table\}",
            dataset_section(tex, dataset),
            flags=re.DOTALL,
        )
        if len(tables) != 2:
            raise RuntimeError(f"expected two CCP panels for {dataset}, found {len(tables)}")
        expected_first_header = [
            "Base", "Metric", "CCP", "e-mod-cross", "u-mod-cross",
            "eu-mod-cross", r"ECCP$(2\alpha)$",
        ]
        expected_second_header = [
            "Base", "Metric", "ECCP", r"ECCP($F_{\text{AoN}}$)",
            r"ECCP($F_1$)", r"ECCP($F_2$)", r"ECCP($F_3$)",
        ]
        if normalized_ccp_header(tables[0]) != expected_first_header:
            raise RuntimeError(f"first CCP method order drift for {dataset}")
        if normalized_ccp_header(tables[1]) != expected_second_header:
            raise RuntimeError(f"second CCP method order drift for {dataset}")
        first = parse_ccp_panel(tables[0], FIRST_PANEL_METHODS)
        second = parse_ccp_panel(tables[1], SECOND_PANEL_METHODS)
        output[dataset] = {
            model: {**first[model], **second[model]}
            for model in MODELS
        }
    return output


def mismatch_paths(expected: object, observed: object, prefix: str = "") -> list[str]:
    if isinstance(expected, dict) and isinstance(observed, dict):
        paths = []
        for key in sorted(set(expected) | set(observed)):
            path = f"{prefix}.{key}" if prefix else str(key)
            if key not in expected or key not in observed:
                paths.append(path)
            else:
                paths.extend(mismatch_paths(expected[key], observed[key], path))
        return paths
    return [] if expected == observed else [prefix]


def audit_fixture(tex: str, config: dict[str, object]) -> dict[str, object]:
    parsed_ca = parse_ca_table(tex)
    parsed_ccp = parse_ccp_tables(tex)
    mismatches = mismatch_paths(config["conformal_aggregation"], parsed_ca)
    mismatches += mismatch_paths(config["cross_conformal"], parsed_ccp)
    ca_cells = sum(len(methods) for methods in parsed_ca.values())
    ccp_cells = sum(
        len(methods) for models in parsed_ccp.values() for methods in models.values()
    )
    return {
        "all_fields_match": not mismatches,
        "mismatch_count": len(mismatches),
        "mismatch_paths": mismatches,
        "ca_cell_count": ca_cells,
        "ccp_cell_count": ccp_cells,
        "total_cell_count": ca_cells + ccp_cells,
        "scalar_count": 4 * (ca_cells + ccp_cells),
        "parsed_values_sha256": sha256_bytes(
            json.dumps(
                {"conformal_aggregation": parsed_ca, "cross_conformal": parsed_ccp},
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("repro/configs/paper_headlines.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    archive, tex_bytes = load_primary_tex()
    config_bytes = args.config.read_bytes()
    config = json.loads(config_bytes)
    audit = audit_fixture(tex_bytes.decode("utf-8"), config)
    result = {
        "source_url": SOURCE_URL,
        "source_archive_sha256": sha256_bytes(archive),
        "main_tex_sha256": sha256_bytes(tex_bytes),
        "config_sha256": sha256_bytes(config_bytes),
        "summary": audit,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not (
        audit["all_fields_match"]
        and audit["ca_cell_count"] == 8
        and audit["ccp_cell_count"] == 90
        and audit["scalar_count"] == 392
    ):
        raise SystemExit("paper table fixture audit failed")
    print(json.dumps(audit, sort_keys=True))


if __name__ == "__main__":
    main()
