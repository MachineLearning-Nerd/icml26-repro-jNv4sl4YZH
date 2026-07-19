#!/usr/bin/env python3
"""Certify the paper/released-code CCP calibrator-column discrepancy.

The paper defines F1/F2/F3 as log/square-root/linear calibrators.  The pinned
released CCP driver instead fills the three corresponding result columns with
square-root/log/power outputs.  This audit binds both sides to immutable source
hashes so the empirical gate can report the discrepancy without silently
renaming formula-faithful reproduction rows.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

try:
    from .verify_paper_table_fixture import (
        MAIN_TEX_SHA256,
        SOURCE_ARCHIVE_SHA256,
        SOURCE_URL,
        load_primary_tex,
    )
except ImportError:
    from verify_paper_table_fixture import (
        MAIN_TEX_SHA256,
        SOURCE_ARCHIVE_SHA256,
        SOURCE_URL,
        load_primary_tex,
    )


MAIN_PY_SHA256 = "4bfabc2a937a633db3d95a70f76e961a5541319b332e1452617ca6f64a8a57d6"
ECCP_UTILS_SHA256 = "7ef06bed7bef7c72dae5f760cf0f0c2b4cf4318af44f87763ac8cc0ab0687593"
PAPER_DEFINITION = (
    r"Examples of p-to-e calibrators include $F_1(p):=-\log(p)$, "
    r"$F_2(p):=p^{-1/2}-1$, and $F_3(p):=2(1-p)$."
)
PAPER_METHOD_TEXT = (
    r"$F_1(p)=-\log p$, $F_2(p)=p^{-1/2}-1$, "
    r"$F_3(p):=2(1-p)$ and $F_{\mathrm{AoN}}$"
)
PAPER_TABLE_HEADER = (
    r"ECCP($F_{\text{AoN}}$) & ECCP($F_{1}$) & ECCP($F_2$) & ECCP($F_3$)"
)
RELEASED_METHOD_ORDER = (
    '"ECCP(ind)", "ECCP(sqrt)", "ECCP(log)", "ECCP(pow)", "ECCP (2α)"'
)
SOURCE_FORMULA_FRAGMENTS = (
    "evals_log = -np.log(vals)",
    "evals_pow = 5*(1-vals)**4",
    "evals_sqrt= vals**(-0.5) -1",
)
SOURCE_COLUMN_FRAGMENTS = (
    "cov_ols[i, 9] = cov_int(cr_ols['int_cc_eval_sqrt'][i], ytest[i])",
    "cov_ols[i, 10] = cov_int(cr_ols['int_cc_eval_log'][i], ytest[i])",
    "cov_ols[i, 11] = cov_int(cr_ols['int_cc_eval_pow'][i], ytest[i])",
    "cov_rf[i, 9] = cov_int(cr_rf['int_cc_eval_sqrt'][i], ytest[i])",
    "cov_rf[i, 10] = cov_int(cr_rf['int_cc_eval_log'][i], ytest[i])",
    "cov_rf[i, 11] = cov_int(cr_rf['int_cc_eval_pow'][i], ytest[i])",
    "cov_lasso[i, 9] = cov_int(cr_lasso['int_cc_eval_sqrt'][i], ytest[i])",
    "cov_lasso[i, 10] = cov_int(cr_lasso['int_cc_eval_log'][i], ytest[i])",
    "cov_lasso[i, 11] = cov_int(cr_lasso['int_cc_eval_pow'][i], ytest[i])",
)
DISCREPANCY_MAP = {
    "ECCP(log)": {
        "paper_column": "F1",
        "paper_formula": "-log(p)",
        "released_column_index": 9,
        "released_method": "ECCP(sqrt)",
        "released_formula": "p**(-0.5)-1",
    },
    "ECCP(sqrt)": {
        "paper_column": "F2",
        "paper_formula": "p**(-0.5)-1",
        "released_column_index": 10,
        "released_method": "ECCP(log)",
        "released_formula": "-log(p)",
    },
    "ECCP(linear)": {
        "paper_column": "F3",
        "paper_formula": "2*(1-p)",
        "released_column_index": 11,
        "released_method": "ECCP(pow)",
        "released_formula": "5*(1-p)**4",
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def numerical_witnesses() -> list[dict[str, object]]:
    p = np.array([0.05, 0.10, 0.20, 0.40, 0.80], dtype=float)
    formulas = {
        "ECCP(log)": (-np.log(p), p ** (-0.5) - 1.0),
        "ECCP(sqrt)": (p ** (-0.5) - 1.0, -np.log(p)),
        "ECCP(linear)": (2.0 * (1.0 - p), 5.0 * (1.0 - p) ** 4),
    }
    rows = []
    for method, (paper_values, released_values) in formulas.items():
        absolute_delta = np.abs(paper_values - released_values)
        rows.append(
            {
                "paper_method": method,
                "p_values": p.tolist(),
                "paper_values": paper_values.tolist(),
                "released_values": released_values.tolist(),
                "minimum_absolute_difference": float(np.min(absolute_delta)),
                "maximum_absolute_difference": float(np.max(absolute_delta)),
                "all_witness_values_differ": bool(np.all(absolute_delta > 0.0)),
            }
        )
    return rows


def audit(source_root: Path) -> dict[str, object]:
    source_root = source_root.resolve()
    main_path = source_root / "e-ccp/main.py"
    utils_path = source_root / "e-ccp/eccp_utils.py"
    main_hash = sha256(main_path)
    utils_hash = sha256(utils_path)
    if main_hash != MAIN_PY_SHA256 or utils_hash != ECCP_UTILS_SHA256:
        raise RuntimeError("pinned released CCP source hash drift")

    main_text = main_path.read_text(encoding="utf-8")
    utils_text = utils_path.read_text(encoding="utf-8")
    if RELEASED_METHOD_ORDER not in main_text:
        raise RuntimeError("released CCP method order drift")
    missing_columns = [text for text in SOURCE_COLUMN_FRAGMENTS if text not in main_text]
    missing_formulas = [text for text in SOURCE_FORMULA_FRAGMENTS if text not in utils_text]
    if missing_columns or missing_formulas:
        raise RuntimeError(
            f"released CCP contract drift: columns={missing_columns}, formulas={missing_formulas}"
        )

    archive, tex_bytes = load_primary_tex()
    tex = tex_bytes.decode("utf-8")
    missing_paper = [
        text
        for text in (PAPER_DEFINITION, PAPER_METHOD_TEXT, PAPER_TABLE_HEADER)
        if text not in tex
    ]
    if missing_paper:
        raise RuntimeError(f"paper CCP calibrator contract drift: {missing_paper}")

    witnesses = numerical_witnesses()
    summary = {
        "paper_formula_contract_verified": True,
        "released_formula_contract_verified": True,
        "released_column_order_verified_for_all_models": True,
        "paper_source_column_mismatch_verified": True,
        "discrepant_method_count": len(DISCREPANCY_MAP),
        "affected_paper_table_cells": 27,
        "affected_paper_table_scalars": 108,
        "all_numerical_witness_values_differ": all(
            row["all_witness_values_differ"] for row in witnesses
        ),
    }
    return {
        "paper_source_url": SOURCE_URL,
        "paper_source_archive_sha256": hashlib.sha256(archive).hexdigest(),
        "paper_main_tex_sha256": hashlib.sha256(tex_bytes).hexdigest(),
        "released_main_py_sha256": main_hash,
        "released_eccp_utils_sha256": utils_hash,
        "paper_definitions": {
            "F1": "-log(p)",
            "F2": "p**(-0.5)-1",
            "F3": "2*(1-p)",
        },
        "released_result_columns": {
            "F1_table_position": "p**(-0.5)-1",
            "F2_table_position": "-log(p)",
            "F3_table_position": "5*(1-p)**4",
        },
        "formula_faithful_reproduction_methods": list(DISCREPANCY_MAP),
        "discrepancy_map": DISCREPANCY_MAP,
        "numerical_witnesses": witnesses,
        "summary": summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("upstream"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.source)
    if result["paper_source_archive_sha256"] != SOURCE_ARCHIVE_SHA256:
        raise SystemExit("paper source archive hash drift")
    if result["paper_main_tex_sha256"] != MAIN_TEX_SHA256:
        raise SystemExit("paper main.tex hash drift")
    if not all(result["summary"].values()):
        raise SystemExit("CCP calibrator contract audit failed")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
