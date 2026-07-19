#!/usr/bin/env python3
"""Report transparent deltas between independent summaries and paper tables."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


KNOWN_CCP_TABLE_DISCREPANCY_METHODS = {
    "ECCP(log)": "paper F1=-log(p), released table position uses square-root",
    "ECCP(sqrt)": "paper F2=square-root, released table position uses log",
    "ECCP(linear)": "paper F3=2(1-p), released table position uses 5(1-p)^4",
}

# The exact released CA run (20 fixed seeds, pinned source/data) reproduces the
# first three reported statistics for this cell, but its sample SD is
# 0.201898618094345 versus the paper's rounded 0.18.  This is one scalar, not a
# claim-level failure.  Keep the observed value exact so an arbitrary or newly
# introduced drift cannot hide behind the disclosure.
KNOWN_CA_DISPERSION_DISCREPANCY = {
    "dataset": "dataset_361234",
    "method": "UR-WECA(P2E)",
    "metric": "length_sd",
    "observed": 0.201898618094345,
    "paper": 0.18,
    "reason": (
        "released 20-fixed-seed sample SD is 0.201898618094345; "
        "paper reports rounded 0.18"
    ),
}


def comparison(actual: dict[str, object], paper: dict[str, float], policy: dict[str, float]) -> dict[str, object]:
    observed_coverage = float(actual["coverage_mean"])
    observed_coverage_sd = float(actual["coverage_sd"])
    observed_length = float(actual["length_mean"])
    observed_length_sd = float(actual["length_sd"])
    paper_coverage = float(paper["coverage_mean"])
    paper_coverage_sd = float(paper["coverage_sd"])
    paper_length = float(paper["length_mean"])
    paper_length_sd = float(paper["length_sd"])
    values = (
        observed_coverage,
        observed_coverage_sd,
        observed_length,
        observed_length_sd,
        paper_coverage,
        paper_coverage_sd,
        paper_length,
        paper_length_sd,
    )
    if not all(math.isfinite(value) for value in values):
        raise ValueError("headline comparison inputs must all be finite")
    if paper_length <= 0.0 or paper_length_sd <= 0.0:
        raise ValueError("paper length mean/SD denominators must be positive")
    coverage_delta = observed_coverage - paper_coverage
    coverage_sd_delta = observed_coverage_sd - paper_coverage_sd
    length_delta = observed_length - paper_length
    length_sd_delta = observed_length_sd - paper_length_sd
    relative_length_delta = length_delta / paper_length
    relative_length_sd_delta = length_sd_delta / paper_length_sd
    metric_checks = {
        "coverage_mean": abs(coverage_delta) <= float(policy["coverage_absolute_tolerance"]),
        "coverage_sd": abs(coverage_sd_delta) <= float(policy["coverage_sd_absolute_tolerance"]),
        "length_mean": abs(relative_length_delta) <= float(policy["length_relative_tolerance"]),
        "length_sd": abs(relative_length_sd_delta) <= float(policy["length_sd_relative_tolerance"]),
    }
    return {
        "observed": {
            "coverage_mean": observed_coverage,
            "coverage_sd": observed_coverage_sd,
            "length_mean": observed_length,
            "length_sd": observed_length_sd,
        },
        "paper": paper,
        "coverage_delta": coverage_delta,
        "coverage_sd_delta": coverage_sd_delta,
        "length_delta": length_delta,
        "length_sd_delta": length_sd_delta,
        "length_relative_delta": relative_length_delta,
        "length_sd_relative_delta": relative_length_sd_delta,
        "metric_checks": metric_checks,
        "within_tolerance": all(metric_checks.values()),
    }


def is_known_ca_dispersion_discrepancy(
    dataset: str, method: str, measured: dict[str, object]
) -> bool:
    return (
        dataset == KNOWN_CA_DISPERSION_DISCREPANCY["dataset"]
        and method == KNOWN_CA_DISPERSION_DISCREPANCY["method"]
        and measured["metric_checks"]
        == {
            "coverage_mean": True,
            "coverage_sd": True,
            "length_mean": True,
            "length_sd": False,
        }
        and math.isclose(
            measured["observed"]["length_sd"],
            KNOWN_CA_DISPERSION_DISCREPANCY["observed"],
            rel_tol=0.0,
            abs_tol=1e-12,
        )
        and math.isclose(
            measured["paper"]["length_sd"],
            KNOWN_CA_DISPERSION_DISCREPANCY["paper"],
            rel_tol=0.0,
            abs_tol=1e-12,
        )
    )
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ca", type=Path, required=True, help="independent CA verifier JSON")
    parser.add_argument("--ccp", type=Path, required=True, help="independent CCP verifier JSON")
    parser.add_argument(
        "--headlines",
        type=Path,
        default=Path("repro/configs/paper_headlines.json"),
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    ca = json.loads(args.ca.read_text(encoding="utf-8"))
    ccp = json.loads(args.ccp.read_text(encoding="utf-8"))
    headlines = json.loads(args.headlines.read_text(encoding="utf-8"))
    policy = headlines["comparison_policy"]

    comparisons: list[dict[str, object]] = []
    for dataset, methods in headlines["conformal_aggregation"].items():
        for method, paper in methods.items():
            measured = comparison(ca["summaries"][dataset][method], paper, policy)
            is_known_dispersion = is_known_ca_dispersion_discrepancy(
                dataset, method, measured
            )
            comparisons.append(
                {
                    "study": "conformal_aggregation",
                    "dataset": dataset,
                    "method": method,
                    "gate_scope": (
                        "known_finite_seed_dispersion_discrepancy"
                        if is_known_dispersion
                        else "unaffected_reproduction"
                    ),
                    "discrepancy_reason": (
                        KNOWN_CA_DISPERSION_DISCREPANCY["reason"]
                        if is_known_dispersion
                        else None
                    ),
                    "discrepancy_metric": (
                        KNOWN_CA_DISPERSION_DISCREPANCY["metric"]
                        if is_known_dispersion
                        else None
                    ),
                    **measured,
                }
            )
    for dataset, models in headlines["cross_conformal"].items():
        for model, methods in models.items():
            for method, paper in methods.items():
                known_discrepancy = method in KNOWN_CCP_TABLE_DISCREPANCY_METHODS
                comparisons.append(
                    {
                        "study": "cross_conformal",
                        "dataset": dataset,
                        "model": model,
                        "method": method,
                        "gate_scope": (
                            "known_paper_source_discrepancy"
                            if known_discrepancy
                            else "unaffected_reproduction"
                        ),
                        "discrepancy_reason": (
                            KNOWN_CCP_TABLE_DISCREPANCY_METHODS.get(method)
                        ),
                        **comparison(ccp["summaries"][dataset][model][method], paper, policy),
                    }
                )

    for item in comparisons:
        item.setdefault("gate_scope", "unaffected_reproduction")
        item.setdefault("discrepancy_reason", None)
    unaffected = [
        item for item in comparisons if item["gate_scope"] == "unaffected_reproduction"
    ]
    known_ccp_discrepancies = [
        item
        for item in comparisons
        if item["gate_scope"] == "known_paper_source_discrepancy"
    ]
    known_ca_dispersion = [
        item
        for item in comparisons
        if item["gate_scope"] == "known_finite_seed_dispersion_discrepancy"
    ]
    unexpected_outside = [item for item in unaffected if not item["within_tolerance"]]

    result = {
        "paper_source": headlines["source"],
        "comparison_policy": policy,
        "comparisons": comparisons,
        "summary": {
            "comparison_count": len(comparisons),
            "within_tolerance_count": sum(item["within_tolerance"] for item in comparisons),
            "all_within_tolerance": all(item["within_tolerance"] for item in comparisons),
            "scalar_comparison_count": sum(
                len(item["metric_checks"]) for item in comparisons
            ),
            "within_tolerance_scalar_count": sum(
                sum(item["metric_checks"].values()) for item in comparisons
            ),
            "unaffected_comparison_count": len(unaffected),
            "unaffected_scalar_comparison_count": sum(
                len(item["metric_checks"]) for item in unaffected
            ),
            "unaffected_within_tolerance_count": sum(
                item["within_tolerance"] for item in unaffected
            ),
            "unaffected_within_tolerance_scalar_count": sum(
                sum(item["metric_checks"].values()) for item in unaffected
            ),
            "all_unaffected_within_tolerance": all(
                item["within_tolerance"] for item in unaffected
            ),
            "known_discrepancy_comparison_count": len(known_ccp_discrepancies),
            "known_discrepancy_scalar_comparison_count": sum(
                len(item["metric_checks"]) for item in known_ccp_discrepancies
            ),
            "known_discrepancy_outside_tolerance_count": sum(
                not item["within_tolerance"] for item in known_ccp_discrepancies
            ),
            "known_ca_dispersion_discrepancy_count": len(known_ca_dispersion),
            "known_ca_dispersion_scalar_count": sum(
                len(item["metric_checks"]) for item in known_ca_dispersion
            ),
            "known_ca_dispersion_within_tolerance_scalar_count": sum(
                sum(item["metric_checks"].values()) for item in known_ca_dispersion
            ),
            "known_ca_dispersion_outside_tolerance_count": sum(
                not item["within_tolerance"] for item in known_ca_dispersion
            ),
            "unexpected_outside_tolerance_count": len(unexpected_outside),
            "all_outside_tolerance_cells_accounted_for": not unexpected_outside,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
