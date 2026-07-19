#!/usr/bin/env python3
"""Render final Trackio markdown only from fully validated evidence artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load(relative: str) -> dict[str, object]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def require_true(summary: dict[str, object], *keys: str) -> None:
    for key in keys:
        if summary.get(key) is not True:
            raise RuntimeError(f"cannot render final summary: {key}={summary.get(key)!r}")


def build_cells(
    claim1: dict[str, object],
    anchored: dict[str, object],
    claim2: dict[str, object],
    mechanism: dict[str, object],
    weca_independence: dict[str, object],
    ca_domains: dict[str, object],
    claim3: dict[str, object],
    calibrator_contract: dict[str, object],
    headlines: dict[str, object],
) -> dict[str, object]:
    c1_summary = claim1["summary"]
    anchored_summary = anchored["summary"]
    c2_summary = claim2["summary"]
    mechanism_summary = mechanism["summary"]
    weca_summary = weca_independence["summary"]
    ca_domain_summary = ca_domains["summary"]
    c3_summary = claim3["summary"]
    contract_summary = calibrator_contract["summary"]
    headline_summary = headlines["summary"]
    assert isinstance(c1_summary, dict)
    assert isinstance(anchored_summary, dict)
    assert isinstance(c2_summary, dict)
    assert isinstance(mechanism_summary, dict)
    assert isinstance(weca_summary, dict)
    assert isinstance(ca_domain_summary, dict)
    assert isinstance(c3_summary, dict)
    assert isinstance(contract_summary, dict)
    assert isinstance(headline_summary, dict)

    require_true(
        c1_summary,
        "all_set_identities_pass",
        "all_threshold_identities_pass",
        "all_exact_e_expectations_pass",
        "all_positive_pass",
        "all_classic_controls_inflate_sets",
        "all_theorem_domain_verified",
        "all_domain_controls_rejected",
    )
    require_true(
        anchored_summary,
        "all_source_anchors_verified",
        "c1_definition_verified",
        "c2_aon_uniqueness_source_verified",
        "c2_aon_uniqueness_certificate_pass",
        "c2_left_continuity_witnesses_pass",
        "c3_all_exact_expectations_pass",
        "c3_all_smoothness_certificates_pass",
        "c3_all_inverse_roundtrips_pass",
        "c3_all_strict_positivity_pass",
        "c3_all_pointwise_aon_dominance_pass",
        "c3_all_aggregation_dominance_pass",
        "c4_eccp_proposition_verified",
        "c4_standard_ccp_bound_verified",
        "c5_weca_proposition_verified",
        "c5_weighted_expectation_identity_verified",
        "c6_section5_scope_verified",
    )
    if (
        anchored_summary.get("source_anchor_count") != 10
        or anchored_summary.get("c2_uniqueness_level_count") != 4
        or anchored_summary.get("c3_case_count") != 18
        or anchored_summary.get("c4_standard_ccp_bound_case_count") != 4
    ):
        raise RuntimeError("anchored-claim mechanism accounting is incomplete")
    require_true(
        c2_summary,
        "all_four_tasks_present",
        "all_full_seed_method_cells_present",
        "exact_cell_set",
        "all_substantial_efficiency_gains",
        "all_p2e_empirical_coverage_within_tolerance",
    )
    require_true(
        mechanism_summary,
        "all_merged_expectations_exact",
        "all_markov_coverage_events_pass",
        "all_arbitrary_dependence_coverage_pass",
        "all_exchangeable_prefix_coverage_pass",
        "all_exchangeable_randomized_prefix_coverage_pass",
        "all_randomized_uniform_coverage_events_pass",
        "all_randomized_arbitrary_dependence_coverage_pass",
        "invalid_scaling_control_detected",
        "invalid_arbitrary_dependence_detected",
        "invalid_randomized_arbitrary_dependence_detected",
        "adaptive_weight_control_detected",
        "adaptive_randomized_weight_control_detected",
    )
    require_true(
        weca_summary,
        "all_required_flow_present",
        "all_split_partitions_disjoint",
        "all_weights_independent_of_final_calibration",
        "all_weights_independent_of_test_data_and_outcomes",
        "all_illegal_test_adaptive_controls_change",
    )
    if weca_summary.get("case_count") != 6:
        raise RuntimeError("WECA independence audit does not contain all six cases")
    require_true(
        ca_domain_summary,
        "all_contexts_accounted_for",
        "all_low_level_conditions_pass",
        "all_theorem_contexts_in_domain",
        "all_boundary_source_set_identities_pass",
        "all_boundary_source_float_expectations_pass",
        "all_boundary_source_uses_upper_bracket",
        "all_exact_aon_repairs_pass",
        "positive_exact_boundary_calibrator_impossible",
    )
    if (
        ca_domain_summary.get("context_count") != 1_680
        or ca_domain_summary.get("theorem_context_count") != 1_600
        or ca_domain_summary.get("boundary_context_count") != 80
    ):
        raise RuntimeError("CA P2E theorem-domain accounting is incomplete")
    require_true(
        c3_summary,
        "all_full_seed_cells_present",
        "exact_cell_set",
        "all_eccp_empirical_coverage_within_tolerance",
        "all_p2e_empirical_coverage_within_tolerance",
        "all_p2e_not_longer_than_existing_calibrators",
        "all_p2e_strictly_shorter_than_aon",
        "all_classical_efficiency_gains_substantial",
    )
    require_true(
        contract_summary,
        "paper_formula_contract_verified",
        "released_formula_contract_verified",
        "released_column_order_verified_for_all_models",
        "paper_source_column_mismatch_verified",
        "all_numerical_witness_values_differ",
    )
    require_true(
        headline_summary,
        "all_unaffected_within_tolerance",
        "all_outside_tolerance_cells_accounted_for",
    )
    if claim3.get("protocol", {}).get("execution_adapter") != "vectorized-exact-postprocessing-v1":
        raise RuntimeError("CCP execution adapter is missing or unverified")

    if claim2["rows_seen"] != 1_920 or c2_summary["expected_rows"] != 1_920:
        raise RuntimeError("Claim 2 raw-row count is not 1,920")
    if c2_summary["comparison_count"] != 24 or c2_summary["p2e_shorter_count"] != 24:
        raise RuntimeError("Claim 2 does not pass all 24 efficiency comparisons")
    if c2_summary["substantial_efficiency_gain_count"] != 24:
        raise RuntimeError("Claim 2 does not pass all 24 substantial-gain checks")
    if c2_summary["minimum_substantial_relative_reduction"] != 0.10:
        raise RuntimeError("Claim 2 materiality threshold drifted from 10%")
    if c2_summary["p2e_empirical_coverage_pass_count"] != 8:
        raise RuntimeError("Claim 2 does not pass all eight P2E coverage sanity checks")
    if claim3["rows_seen"] != 11_700 or c3_summary["expected_rows"] != 11_700:
        raise RuntimeError("Claim 3 raw-row count is not 11,700")
    if c3_summary["eccp_empirical_coverage_pass_count"] != 9:
        raise RuntimeError("Claim 3 does not pass all nine ECCP coverage sanity checks")
    if c3_summary["p2e_empirical_coverage_pass_count"] != 27:
        raise RuntimeError("Claim 3 does not pass all 27 P2E-method coverage checks")
    if c3_summary["calibrator_efficiency_comparison_count"] != 36:
        raise RuntimeError("CCP does not contain all 36 calibrator comparisons")
    if c3_summary["p2e_strictly_shorter_count"] != 36:
        raise RuntimeError("P2E is not strictly shorter in all 36 CCP comparisons")
    if c3_summary["aon_strictly_shorter_count"] != 9:
        raise RuntimeError("P2E does not strictly dominate AoN in all nine CCP cells")
    if c3_summary["classical_substantial_gain_count"] != 27:
        raise RuntimeError("P2E does not clear all 27 classical CCP materiality checks")
    if c3_summary["minimum_substantial_relative_reduction"] != 0.10:
        raise RuntimeError("CCP materiality threshold drifted from 10%")
    if headline_summary["comparison_count"] != 122:
        raise RuntimeError("headline cell count is not 122")
    if headline_summary["scalar_comparison_count"] != 488:
        raise RuntimeError("headline scalar count is not 488")
    if (
        headline_summary["unaffected_comparison_count"] != 94
        or headline_summary["unaffected_within_tolerance_count"] != 94
        or headline_summary["unaffected_scalar_comparison_count"] != 376
        or headline_summary["unaffected_within_tolerance_scalar_count"] != 376
    ):
        raise RuntimeError("not all 94 unaffected paper-table cells pass")
    if (
        contract_summary.get("discrepant_method_count") != 3
        or contract_summary.get("affected_paper_table_cells") != 27
        or contract_summary.get("affected_paper_table_scalars") != 108
        or headline_summary["known_discrepancy_comparison_count"] != 27
        or headline_summary["known_discrepancy_scalar_comparison_count"] != 108
        or headline_summary["known_ca_dispersion_discrepancy_count"] != 1
        or headline_summary["known_ca_dispersion_scalar_count"] != 4
        or headline_summary["known_ca_dispersion_within_tolerance_scalar_count"] != 3
        or headline_summary["known_ca_dispersion_outside_tolerance_count"] != 1
        or headline_summary["unexpected_outside_tolerance_count"] != 0
    ):
        raise RuntimeError("paper/source calibrator discrepancy accounting is incomplete")

    efficiency = claim2["efficiency_comparisons"]
    assert isinstance(efficiency, list)
    relative_reductions = [float(row["relative_reduction"]) for row in efficiency]
    ca_coverages = [
        float(methods[method]["coverage_mean"])
        for methods in claim2["summaries"].values()
        for method in ("WECA(P2E)", "UR-WECA(P2E)")
    ]
    ccp_coverages = [
        float(methods["ECCP"]["coverage_mean"])
        for models in claim3["summaries"].values()
        for methods in models.values()
    ]
    ccp_p2e_coverages = [
        float(methods[method]["coverage_mean"])
        for models in claim3["summaries"].values()
        for methods in models.values()
        for method in ("ECCP", "ECCP_exch", "UR-ECCP_exch")
    ]
    maximum_expectation_error = max(
        float(row["expectation_abs_error"]) for row in claim1["cases"]
    )
    valid_tail_ratio = float(mechanism_summary["maximum_valid_tail_to_alpha_ratio"])
    randomized_tail_ratio = float(
        mechanism_summary["maximum_valid_randomized_tail_to_alpha_ratio"]
    )
    exchangeable_prefix_tail_ratio = float(
        mechanism_summary["maximum_exchangeable_prefix_tail_to_alpha_ratio"]
    )
    exchangeable_randomized_tail_ratio = float(
        mechanism_summary[
            "maximum_exchangeable_randomized_prefix_tail_to_alpha_ratio"
        ]
    )

    summary = {
        "anchored_claims": 6,
        "maximum_points": 12,
        "source_anchors": int(anchored_summary["source_anchor_count"]),
        "aon_uniqueness_levels": int(
            anchored_summary["c2_uniqueness_level_count"]
        ),
        "sigmoid_mechanism_cases": int(anchored_summary["c3_case_count"]),
        "standard_ccp_bound_cases": int(
            anchored_summary["c4_standard_ccp_bound_case_count"]
        ),
        "claim1_cells": int(c1_summary["case_count"]),
        "claim1_domain_controls": int(c1_summary["domain_control_count"]),
        "claim1_maximum_expectation_error": maximum_expectation_error,
        "claim2_raw_rows": int(claim2["rows_seen"]),
        "claim2_efficiency_wins": int(c2_summary["p2e_shorter_count"]),
        "claim2_efficiency_comparisons": int(c2_summary["comparison_count"]),
        "claim2_minimum_relative_reduction": min(relative_reductions),
        "claim2_maximum_relative_reduction": max(relative_reductions),
        "claim2_p2e_coverage_min": min(ca_coverages),
        "claim2_p2e_coverage_max": max(ca_coverages),
        "claim3_raw_rows": int(claim3["rows_seen"]),
        "claim3_execution_adapter": str(claim3["protocol"]["execution_adapter"]),
        "claim3_eccp_coverage_min": min(ccp_coverages),
        "claim3_eccp_coverage_max": max(ccp_coverages),
        "claim3_p2e_coverage_min": min(ccp_p2e_coverages),
        "claim3_p2e_coverage_max": max(ccp_p2e_coverages),
        "claim3_valid_tail_to_alpha_max": valid_tail_ratio,
        "claim3_valid_randomized_tail_to_alpha_max": randomized_tail_ratio,
        "claim3_exchangeable_prefix_cases": int(
            mechanism_summary["exchangeable_prefix_case_count"]
        ),
        "claim3_exchangeable_prefix_tail_to_alpha_max": (
            exchangeable_prefix_tail_ratio
        ),
        "claim3_exchangeable_randomized_tail_to_alpha_max": (
            exchangeable_randomized_tail_ratio
        ),
        "claim3_weca_independence_cases": int(weca_summary["case_count"]),
        "ca_p2e_contexts": int(ca_domain_summary["context_count"]),
        "ca_p2e_theorem_contexts": int(
            ca_domain_summary["theorem_context_count"]
        ),
        "ca_p2e_boundary_contexts": int(
            ca_domain_summary["boundary_context_count"]
        ),
        "ca_p2e_boundary_max_aon_deviation": float(
            ca_domain_summary["maximum_boundary_float_deviation_from_aon"]
        ),
        "claim2_ccp_efficiency_wins": int(c3_summary["p2e_strictly_shorter_count"]),
        "claim2_ccp_efficiency_comparisons": int(
            c3_summary["calibrator_efficiency_comparison_count"]
        ),
        "claim2_ccp_aon_wins": int(c3_summary["aon_strictly_shorter_count"]),
        "claim2_ccp_classical_material_wins": int(
            c3_summary["classical_substantial_gain_count"]
        ),
        "claim2_ccp_minimum_classical_relative_reduction": float(
            c3_summary["minimum_classical_relative_reduction"]
        ),
        "headline_cells": int(headline_summary["comparison_count"]),
        "headline_scalars": int(headline_summary["scalar_comparison_count"]),
        "headline_unaffected_cells": int(
            headline_summary["unaffected_comparison_count"]
        ),
        "headline_unaffected_scalars": int(
            headline_summary["unaffected_scalar_comparison_count"]
        ),
        "headline_discrepancy_cells": int(
            headline_summary["known_discrepancy_comparison_count"]
        ),
        "headline_discrepancy_scalars": int(
            headline_summary["known_discrepancy_scalar_comparison_count"]
        ),
        "headline_ca_dispersion_cells": int(
            headline_summary["known_ca_dispersion_discrepancy_count"]
        ),
        "headline_ca_dispersion_scalars": int(
            headline_summary["known_ca_dispersion_scalar_count"]
        ),
        "headline_ca_dispersion_passing_scalars": int(
            headline_summary["known_ca_dispersion_within_tolerance_scalar_count"]
        ),
    }

    claim1_markdown = f"""Claim 1 is verified from both the pinned Definition 2.2 source block and an independent finite-rank construction. At every one of {summary['claim1_cells']} theorem-valid `(n, alpha)` cells, membership under `P_n > alpha` is identical to membership under `F(P_n) < 1/alpha`; the threshold identity also passes exactly. The constructed e-variable has maximum expectation error {summary['claim1_maximum_expectation_error']:.3g}. This directly reproduces the definition of set preservation rather than inferring it from empirical coverage."""

    claim2_markdown = f"""Claim 2 is verified by a source-hash-bound proof contract and an exact rational budget certificate. For {summary['aon_uniqueness_levels']} distinct alpha levels, set preservation forces `F >= 1/alpha` on `(0, alpha]`, which consumes exactly the entire p-to-e integral budget; nonnegativity and monotonicity then force `F=1/alpha` below alpha and `F=0` above it, while explicit conformal-grid witnesses exercise the left-continuity boundary argument. The pinned Proposition 2.3, Theorem 2.6, and Equation 9 blocks are among {summary['source_anchors']} independently hashed source anchors, tying the uniqueness result to the sigmoid construction it motivates."""

    claim3_markdown = f"""Claim 3 is verified in {summary['sigmoid_mechanism_cases']} independent theorem-domain cases. The normalized sigmoid has expectation one, finite log-values (strict positivity), a strictly negative analytic derivative (smoothness and invertibility), and a closed-form inverse that round-trips numerically. Pointwise P2E values dominate AoN, so every weighted or unweighted aggregate P2E e-value is at least the corresponding AoN aggregate and the P2E prediction set is a subset. The full released CCP results additionally show strict empirical improvement over AoN in {summary['claim2_ccp_aon_wins']}/9 matched dataset/model cells."""

    claim4_markdown = f"""Claim 4 is verified by exact coverage certificates plus the complete released CCP protocol. Sparse LPs maximize deterministic and randomized rejection over every joint conformal-rank coupling in the equal-weight ECCP cases; all valid cases stay at or below alpha (maximum failure/alpha ratios {summary['claim3_valid_tail_to_alpha_max']:.6f} and {summary['claim3_valid_randomized_tail_to_alpha_max']:.6f}). A separate exchangeable-orbit LP verifies ECCP-Exch and UR-ECCP-Exch in {summary['claim3_exchangeable_prefix_cases']}/5 cases. The pinned standard-CCP formula is checked in {summary['standard_ccp_bound_cases']} parameter cases and yields a lower guarantee below `1-alpha`, centered on `1-2alpha` with its finite-sample correction. Empirically, all 27 P2E CCP coverage cells pass the fixed two-percentage-point shortfall sanity threshold and span {summary['claim3_p2e_coverage_min']:.4f}–{summary['claim3_p2e_coverage_max']:.4f}; the exact guarantee comes from the e-value certificate, not that empirical check."""

    claim5_markdown = f"""Claim 5 is verified for data-dependent WECA weights under the proposition's required split independence. The released routine's tuning and final-inference partitions are disjoint, and selected weights remain bit-identical after arbitrary final-calibration or test-data/outcome mutations in {summary['claim3_weca_independence_cases']}/6 seeded cases; the forbidden test-adaptive control changes in 6/6. Exact arbitrary-dependence LPs accept all six nonuniform fixed-weight cases under both deterministic and randomized thresholds, while outcome-adaptive max weighting fails. The full CA verifier accepts exactly {summary['claim2_raw_rows']:,} unique finite cells, and all eight P2E CA coverage means pass the fixed empirical sanity check ({summary['claim2_p2e_coverage_min']:.4f}–{summary['claim2_p2e_coverage_max']:.4f})."""

    claim6_markdown = f"""Claim 6 is verified at the complete released empirical scale. The CCP run contains exactly {summary['claim3_raw_rows']:,} unique finite cells (three datasets, 100 seeds, three models, 13 methods) using the parity-checked `{summary['claim3_execution_adapter']}` adapter. P2E is strictly shorter in {summary['claim2_ccp_efficiency_wins']}/{summary['claim2_ccp_efficiency_comparisons']} matched baseline comparisons: 9/9 AoN cells and {summary['claim2_ccp_classical_material_wins']}/27 formula-faithful log, square-root, and linear calibrator cells, with every classical reduction exceeding the predeclared 10% threshold. The independent CA evidence adds {summary['claim2_efficiency_wins']}/{summary['claim2_efficiency_comparisons']} material P2E wins, ranging from {100 * summary['claim2_minimum_relative_reduction']:.2f}% to {100 * summary['claim2_maximum_relative_reduction']:.2f}% reduction. All {summary['headline_unaffected_scalars']} unaffected reported scalars across {summary['headline_unaffected_cells']} paper-table cells pass the fixed drift tolerances. One additional CA cell passes coverage mean/SD and length mean but reproduces length SD as `0.201898618094345` versus the paper's rounded `0.18`; this single finite-seed dispersion scalar is explicitly disclosed and does not alter any efficiency or coverage verdict. The remaining {summary['headline_discrepancy_cells']} cells ({summary['headline_discrepancy_scalars']} scalars) are explicitly classified by a hash-bound audit: the paper defines F1/F2/F3 as log/square-root/linear, while the released CCP table driver fills those positions with square-root/log/power. No result is relabeled to conceal either discrepancy, and all P2E coverage checks remain valid."""

    claim5_markdown += f""" A source-bound audit accounts for all {summary['ca_p2e_contexts']:,} internal CA calibration contexts: {summary['ca_p2e_theorem_contexts']:,} satisfy the theorem domain and {summary['ca_p2e_boundary_contexts']} exact-rank boundary contexts use the released `C=1e6` AoN limit. Those boundary sets remain identical, with maximum numerical deviation {summary['ca_p2e_boundary_max_aon_deviation']:.3g}; they are not mislabeled as positive exact-P2E theorem instances."""

    controls_markdown = f"""The controls fail in the intended direction. All {summary['claim1_domain_controls']} excluded theorem-domain boundary cases are rejected, and classical p-to-e calibrators inflate the conformal set in all {c1_summary['classic_control_case_count']} valid finite-rank cases. Invalid 2x e-value scaling violates the arbitrary-dependence deterministic bound in {mechanism_summary['invalid_arbitrary_dependence_rejection_count']}/{mechanism_summary['case_count']} cases and the randomized bound in {mechanism_summary['invalid_randomized_arbitrary_dependence_rejection_count']}/{mechanism_summary['case_count']} cases. It also violates the exchangeable ECCP-Exch and UR-ECCP-Exch orbit bounds in {mechanism_summary['invalid_exchangeable_prefix_rejection_count']}/{mechanism_summary['exchangeable_prefix_case_count']} and {mechanism_summary['invalid_exchangeable_randomized_prefix_rejection_count']}/{mechanism_summary['exchangeable_prefix_case_count']} cases. Inference-adaptive one-hot weights fail both weighted-merge bounds in {mechanism_summary['adaptive_weight_rejection_count']}/{mechanism_summary['case_count']} and {mechanism_summary['adaptive_randomized_weight_rejection_count']}/{mechanism_summary['case_count']} cases. All raw verifiers separately reject protocol drift, missing, duplicate, unexpected or non-finite cells, invalid metric ranges, and insufficient efficiency gains."""

    conclusion_markdown = f"""All six anchored jury claims are verified at the declared scope. The source-bound mechanism audit covers Definition 2.2, Proposition 2.3, Theorem 2.6/Equation 9, Propositions 4.1–4.2, and Section 5; independent exact/numerical certificates verify set preservation, AoN uniqueness, sigmoid properties and dominance, ECCP coverage, and tuning-independent WECA validity. Complete released CA and CCP runs supply {summary['claim2_raw_rows']:,} + {summary['claim3_raw_rows']:,} raw cells. All {summary['headline_unaffected_scalars']} unaffected table scalars reproduce within fixed tolerances; one CA finite-seed length-SD scalar is `0.201898618094345` versus `0.18`, and the paper/released-code F1/F2/F3 inconsistency affecting {summary['headline_discrepancy_scalars']} scalars is source-hash-bound, numerically witnessed, and disclosed rather than force-fit.

## Scope & cost

| Item | This reproduction | Paper protocol |
| --- | --- | --- |
| Claims 1-3 | {summary['claim1_cells']} finite-rank identities + {summary['aon_uniqueness_levels']} exact uniqueness budgets + {summary['sigmoid_mechanism_cases']} sigmoid cases | Full stated mechanisms and theorem domain |
| Claims 4 and 6 / CCP | {summary['claim3_raw_rows']:,} raw cells; three datasets x 100 seeds x three models x 13 methods; exact coupling/orbit LPs | Same released data, seeds, models, and K=15/15/20 |
| Claim 5 / CA | {summary['claim2_raw_rows']:,} raw cells; four tasks x 20 seeds x 24 methods; source-bound split audit | Same released tasks, seeds, methods, M=512, B=500 |
| Hardware | Local CPU; no GPU | CPU-compatible released implementation |
| External compute cost | $0 | No cloud run required |
| Outcome | 6/6 anchored claims verified; 12 possible points | Full challenge-claim scope |

Source float underflow for already-excluded extreme e-values is disclosed; stable log-e arithmetic confirms strict positivity and leaves every threshold decision unchanged.

FULL_GATE_READY: jNv4sl4YZH"""

    return {
        "summary": summary,
        "claim_1": claim1_markdown,
        "claim_2": claim2_markdown,
        "claim_3": claim3_markdown,
        "claim_4": claim4_markdown,
        "claim_5": claim5_markdown,
        "claim_6": claim6_markdown,
        "negative_controls": controls_markdown,
        "conclusion": conclusion_markdown,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path, default=Path("outputs/final_logbook_cells.json")
    )
    args = parser.parse_args()
    cells = build_cells(
        load("outputs/claim1_independent.json"),
        load("outputs/anchored_claims_mechanism.json"),
        load("outputs/claim2_independent.json"),
        load("outputs/claim3_independent_e_merge.json"),
        load("outputs/weca_independence_audit.json"),
        load("outputs/ca_p2e_domain_audit.json"),
        load("outputs/claim3_independent.json"),
        load("outputs/ccp_calibrator_contract_audit.json"),
        load("outputs/paper_headline_comparison.json"),
    )
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    temporary.write_text(json.dumps(cells, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(output)
    print(json.dumps(cells["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
