# Conclusion


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_eb2f15259b0e", "created_at": "2026-07-18T12:24:41+00:00", "title": "Current outcome"}
-->
**Initial gate state (2026-07-18; historical):** Claim 1 was verified by two independent paths, while Claims 2 and 3 were intentionally not asserted before their paper-scale runs. This scaffold-time note is superseded only by the later pinned **Final outcome** cell containing `FULL_GATE_READY: jNv4sl4YZH`; without that marker, publication remains prohibited.

## Scope & cost

| Item | This reproduction | Full replication |
| --- | --- | --- |
| C1 | 18 exact finite-rank cells + source cross-check | Covered |
| C2 | Four OpenML tasks x 20 seeds, queued | Same released source protocol |
| C3 | Three datasets x 100 seeds, queued | Same released source protocol |
| Hardware | Local CPU; no GPU required | Local CPU |
| Outcome at scaffold time | In progress; no publication claim | Superseded only by the later pinned full-gate verdict |


---
<!-- trackio-cell
{"type": "code", "id": "cell_f484927920d5", "created_at": "2026-07-19T19:00:33+00:00", "title": "Build evidence-derived final summary", "command": ["python", "repro/src/render_final_logbook.py", "--output", "outputs/final_logbook_cells.json"], "exit_code": 0, "duration_s": 0.041}
-->
````bash
$ python repro/src/render_final_logbook.py --output outputs/final_logbook_cells.json
````

exit 0 · 0.0s


````python title=render_final_logbook.py
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
        "all_source_table_replays_within_tolerance",
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
        or headline_summary["source_table_replay_comparison_count"] != 18
        or headline_summary["source_table_replay_within_tolerance_count"] != 18
        or headline_summary["source_table_replay_scalar_comparison_count"] != 72
        or headline_summary["source_table_replay_within_tolerance_scalar_count"] != 72
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
        "headline_source_replay_cells": int(
            headline_summary["source_table_replay_comparison_count"]
        ),
        "headline_source_replay_scalars": int(
            headline_summary["source_table_replay_scalar_comparison_count"]
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

    claim6_markdown = f"""Claim 6 is verified at the complete released empirical scale. The CCP run contains exactly {summary['claim3_raw_rows']:,} unique finite cells (three datasets, 100 seeds, three models, 13 methods) using the parity-checked `{summary['claim3_execution_adapter']}` adapter. P2E is strictly shorter in {summary['claim2_ccp_efficiency_wins']}/{summary['claim2_ccp_efficiency_comparisons']} matched baseline comparisons: 9/9 AoN cells and {summary['claim2_ccp_classical_material_wins']}/27 formula-faithful log, square-root, and linear calibrator cells, with every classical reduction exceeding the predeclared 10% threshold. The independent CA evidence adds {summary['claim2_efficiency_wins']}/{summary['claim2_efficiency_comparisons']} material P2E wins, ranging from {100 * summary['claim2_minimum_relative_reduction']:.2f}% to {100 * summary['claim2_maximum_relative_reduction']:.2f}% reduction. All {summary['headline_unaffected_scalars']} unaffected reported scalars across {summary['headline_unaffected_cells']} paper-table cells pass the fixed drift tolerances. One additional CA cell passes coverage mean/SD and length mean but reproduces length SD as `0.201898618094345` versus the paper's rounded `0.18`; this single finite-seed dispersion scalar is explicitly disclosed and does not alter any efficiency or coverage verdict. The remaining {summary['headline_discrepancy_cells']} cells ({summary['headline_discrepancy_scalars']} scalars) are explicitly classified by a hash-bound audit: the paper defines F1/F2/F3 as log/square-root/linear, while the released CCP table driver fills those positions with square-root/log/power. The reversible log/square-root swap is also replayed numerically: all {summary['headline_source_replay_scalars']} scalars in {summary['headline_source_replay_cells']} source-position cells match the paper table under the released mapping. No result is relabeled to conceal either discrepancy, and all P2E coverage checks remain valid."""

    claim5_markdown += f""" A source-bound audit accounts for all {summary['ca_p2e_contexts']:,} internal CA calibration contexts: {summary['ca_p2e_theorem_contexts']:,} satisfy the theorem domain and {summary['ca_p2e_boundary_contexts']} exact-rank boundary contexts use the released `C=1e6` AoN limit. Those boundary sets remain identical, with maximum numerical deviation {summary['ca_p2e_boundary_max_aon_deviation']:.3g}; they are not mislabeled as positive exact-P2E theorem instances."""

    controls_markdown = f"""The controls fail in the intended direction. All {summary['claim1_domain_controls']} excluded theorem-domain boundary cases are rejected, and classical p-to-e calibrators inflate the conformal set in all {c1_summary['classic_control_case_count']} valid finite-rank cases. Invalid 2x e-value scaling violates the arbitrary-dependence deterministic bound in {mechanism_summary['invalid_arbitrary_dependence_rejection_count']}/{mechanism_summary['case_count']} cases and the randomized bound in {mechanism_summary['invalid_randomized_arbitrary_dependence_rejection_count']}/{mechanism_summary['case_count']} cases. It also violates the exchangeable ECCP-Exch and UR-ECCP-Exch orbit bounds in {mechanism_summary['invalid_exchangeable_prefix_rejection_count']}/{mechanism_summary['exchangeable_prefix_case_count']} and {mechanism_summary['invalid_exchangeable_randomized_prefix_rejection_count']}/{mechanism_summary['exchangeable_prefix_case_count']} cases. Inference-adaptive one-hot weights fail both weighted-merge bounds in {mechanism_summary['adaptive_weight_rejection_count']}/{mechanism_summary['case_count']} and {mechanism_summary['adaptive_randomized_weight_rejection_count']}/{mechanism_summary['case_count']} cases. All raw verifiers separately reject protocol drift, missing, duplicate, unexpected or non-finite cells, invalid metric ranges, and insufficient efficiency gains."""

    conclusion_markdown = f"""All six anchored jury claims are verified at the declared scope. The source-bound mechanism audit covers Definition 2.2, Proposition 2.3, Theorem 2.6/Equation 9, Propositions 4.1–4.2, and Section 5; independent exact/numerical certificates verify set preservation, AoN uniqueness, sigmoid properties and dominance, ECCP coverage, and tuning-independent WECA validity. Complete released CA and CCP runs supply {summary['claim2_raw_rows']:,} + {summary['claim3_raw_rows']:,} raw cells. All {summary['headline_unaffected_scalars']} unaffected table scalars reproduce within fixed tolerances; one CA finite-seed length-SD scalar is `0.201898618094345` versus `0.18`, and the paper/released-code F1/F2/F3 inconsistency affecting {summary['headline_discrepancy_scalars']} scalars is source-hash-bound, numerically witnessed, and disclosed rather than force-fit. The reversible released log/square-root column swap independently replays all {summary['headline_source_replay_scalars']} affected scalars within the same fixed tolerances.

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

````


````json title=final_logbook_cells.json
{
  "claim_1": "Claim 1 is verified from both the pinned Definition 2.2 source block and an independent finite-rank construction. At every one of 18 theorem-valid `(n, alpha)` cells, membership under `P_n > alpha` is identical to membership under `F(P_n) < 1/alpha`; the threshold identity also passes exactly. The constructed e-variable has maximum expectation error 4.44e-16. This directly reproduces the definition of set preservation rather than inferring it from empirical coverage.",
  "claim_2": "Claim 2 is verified by a source-hash-bound proof contract and an exact rational budget certificate. For 4 distinct alpha levels, set preservation forces `F >= 1/alpha` on `(0, alpha]`, which consumes exactly the entire p-to-e integral budget; nonnegativity and monotonicity then force `F=1/alpha` below alpha and `F=0` above it, while explicit conformal-grid witnesses exercise the left-continuity boundary argument. The pinned Proposition 2.3, Theorem 2.6, and Equation 9 blocks are among 10 independently hashed source anchors, tying the uniqueness result to the sigmoid construction it motivates.",
  "claim_3": "Claim 3 is verified in 18 independent theorem-domain cases. The normalized sigmoid has expectation one, finite log-values (strict positivity), a strictly negative analytic derivative (smoothness and invertibility), and a closed-form inverse that round-trips numerically. Pointwise P2E values dominate AoN, so every weighted or unweighted aggregate P2E e-value is at least the corresponding AoN aggregate and the P2E prediction set is a subset. The full released CCP results additionally show strict empirical improvement over AoN in 9/9 matched dataset/model cells.",
  "claim_4": "Claim 4 is verified by exact coverage certificates plus the complete released CCP protocol. Sparse LPs maximize deterministic and randomized rejection over every joint conformal-rank coupling in the equal-weight ECCP cases; all valid cases stay at or below alpha (maximum failure/alpha ratios 0.952381 and 1.000000). A separate exchangeable-orbit LP verifies ECCP-Exch and UR-ECCP-Exch in 5/5 cases. The pinned standard-CCP formula is checked in 4 parameter cases and yields a lower guarantee below `1-alpha`, centered on `1-2alpha` with its finite-sample correction. Empirically, all 27 P2E CCP coverage cells pass the fixed two-percentage-point shortfall sanity threshold and span 0.8903\u20130.9187; the exact guarantee comes from the e-value certificate, not that empirical check.",
  "claim_5": "Claim 5 is verified for data-dependent WECA weights under the proposition's required split independence. The released routine's tuning and final-inference partitions are disjoint, and selected weights remain bit-identical after arbitrary final-calibration or test-data/outcome mutations in 6/6 seeded cases; the forbidden test-adaptive control changes in 6/6. Exact arbitrary-dependence LPs accept all six nonuniform fixed-weight cases under both deterministic and randomized thresholds, while outcome-adaptive max weighting fails. The full CA verifier accepts exactly 1,920 unique finite cells, and all eight P2E CA coverage means pass the fixed empirical sanity check (0.9490\u20130.9634). A source-bound audit accounts for all 1,680 internal CA calibration contexts: 1,600 satisfy the theorem domain and 80 exact-rank boundary contexts use the released `C=1e6` AoN limit. Those boundary sets remain identical, with maximum numerical deviation 6.42e-174; they are not mislabeled as positive exact-P2E theorem instances.",
  "claim_6": "Claim 6 is verified at the complete released empirical scale. The CCP run contains exactly 11,700 unique finite cells (three datasets, 100 seeds, three models, 13 methods) using the parity-checked `vectorized-exact-postprocessing-v1` adapter. P2E is strictly shorter in 36/36 matched baseline comparisons: 9/9 AoN cells and 27/27 formula-faithful log, square-root, and linear calibrator cells, with every classical reduction exceeding the predeclared 10% threshold. The independent CA evidence adds 24/24 material P2E wins, ranging from 40.30% to 95.96% reduction. All 376 unaffected reported scalars across 94 paper-table cells pass the fixed drift tolerances. One additional CA cell passes coverage mean/SD and length mean but reproduces length SD as `0.201898618094345` versus the paper's rounded `0.18`; this single finite-seed dispersion scalar is explicitly disclosed and does not alter any efficiency or coverage verdict. The remaining 27 cells (108 scalars) are explicitly classified by a hash-bound audit: the paper defines F1/F2/F3 as log/square-root/linear, while the released CCP table driver fills those positions with square-root/log/power. The reversible log/square-root swap is also replayed numerically: all 72 scalars in 18 source-position cells match the paper table under the released mapping. No result is relabeled to conceal either discrepancy, and all P2E coverage checks remain valid.",
  "conclusion": "All six anchored jury claims are verified at the declared scope. The source-bound mechanism audit covers Definition 2.2, Proposition 2.3, Theorem 2.6/Equation 9, Propositions 4.1\u20134.2, and Section 5; independent exact/numerical certificates verify set preservation, AoN uniqueness, sigmoid properties and dominance, ECCP coverage, and tuning-independent WECA validity. Complete released CA and CCP runs supply 1,920 + 11,700 raw cells. All 376 unaffected table scalars reproduce within fixed tolerances; one CA finite-seed length-SD scalar is `0.201898618094345` versus `0.18`, and the paper/released-code F1/F2/F3 inconsistency affecting 108 scalars is source-hash-bound, numerically witnessed, and disclosed rather than force-fit. The reversible released log/square-root column swap independently replays all 72 affected scalars within the same fixed tolerances.\n\n## Scope & cost\n\n| Item | This reproduction | Paper protocol |\n| --- | --- | --- |\n| Claims 1-3 | 18 finite-rank identities + 4 exact uniqueness budgets + 18 sigmoid cases | Full stated mechanisms and theorem domain |\n| Claims 4 and 6 / CCP | 11,700 raw cells; three datasets x 100 seeds x three models x 13 methods; exact coupling/orbit LPs | Same released data, seeds, models, and K=15/15/20 |\n| Claim 5 / CA | 1,920 raw cells; four tasks x 20 seeds x 24 methods; source-bound split audit | Same released tasks, seeds, methods, M=512, B=500 |\n| Hardware | Local CPU; no GPU | CPU-compatible released implementation |\n| External compute cost | $0 | No cloud run required |\n| Outcome | 6/6 anchored claims verified; 12 possible points | Full challenge-claim scope |\n\nSource float underflow for already-excluded extreme e-values is disclosed; stable log-e arithmetic confirms strict positivity and leaves every threshold decision unchanged.\n\nFULL_GATE_READY: jNv4sl4YZH",
  "negative_controls": "The controls fail in the intended direction. All 5 excluded theorem-domain boundary cases are rejected, and classical p-to-e calibrators inflate the conformal set in all 18 valid finite-rank cases. Invalid 2x e-value scaling violates the arbitrary-dependence deterministic bound in 4/8 cases and the randomized bound in 8/8 cases. It also violates the exchangeable ECCP-Exch and UR-ECCP-Exch orbit bounds in 5/5 and 5/5 cases. Inference-adaptive one-hot weights fail both weighted-merge bounds in 8/8 and 8/8 cases. All raw verifiers separately reject protocol drift, missing, duplicate, unexpected or non-finite cells, invalid metric ranges, and insufficient efficiency gains.",
  "summary": {
    "anchored_claims": 6,
    "aon_uniqueness_levels": 4,
    "ca_p2e_boundary_contexts": 80,
    "ca_p2e_boundary_max_aon_deviation": 6.422607377437694e-174,
    "ca_p2e_contexts": 1680,
    "ca_p2e_theorem_contexts": 1600,
    "claim1_cells": 18,
    "claim1_domain_controls": 5,
    "claim1_maximum_expectation_error": 4.440892098500626e-16,
    "claim2_ccp_aon_wins": 9,
    "claim2_ccp_classical_material_wins": 27,
    "claim2_ccp_efficiency_comparisons": 36,
    "claim2_ccp_efficiency_wins": 36,
    "claim2_ccp_minimum_classical_relative_reduction": 0.23664123574004337,
    "claim2_efficiency_comparisons": 24,
    "claim2_efficiency_wins": 24,
    "claim2_maximum_relative_reduction": 0.959609208072499,
    "claim2_minimum_relative_reduction": 0.40302055578705925,
    "claim2_p2e_coverage_max": 0.9634375000000001,
    "claim2_p2e_coverage_min": 0.9490322580645161,
    "claim2_raw_rows": 1920,
    "claim3_eccp_coverage_max": 0.904622641509434,
    "claim3_eccp_coverage_min": 0.8902991304347826,
    "claim3_exchangeable_prefix_cases": 5,
    "claim3_exchangeable_prefix_tail_to_alpha_max": 0.9523809523809523,
    "claim3_exchangeable_randomized_tail_to_alpha_max": 0.9727207182725058,
    "claim3_execution_adapter": "vectorized-exact-postprocessing-v1",
    "claim3_p2e_coverage_max": 0.9186792452830188,
    "claim3_p2e_coverage_min": 0.8902991304347826,
    "claim3_raw_rows": 11700,
    "claim3_valid_randomized_tail_to_alpha_max": 0.9999999999999999,
    "claim3_valid_tail_to_alpha_max": 0.9523809523809523,
    "claim3_weca_independence_cases": 6,
    "headline_ca_dispersion_cells": 1,
    "headline_ca_dispersion_passing_scalars": 3,
    "headline_ca_dispersion_scalars": 4,
    "headline_cells": 122,
    "headline_discrepancy_cells": 27,
    "headline_discrepancy_scalars": 108,
    "headline_scalars": 488,
    "headline_source_replay_cells": 18,
    "headline_source_replay_scalars": 72,
    "headline_unaffected_cells": 94,
    "headline_unaffected_scalars": 376,
    "maximum_points": 12,
    "sigmoid_mechanism_cases": 18,
    "source_anchors": 10,
    "standard_ccp_bound_cases": 4
  }
}

````


````output
{"anchored_claims": 6, "aon_uniqueness_levels": 4, "ca_p2e_boundary_contexts": 80, "ca_p2e_boundary_max_aon_deviation": 6.422607377437694e-174, "ca_p2e_contexts": 1680, "ca_p2e_theorem_contexts": 1600, "claim1_cells": 18, "claim1_domain_controls": 5, "claim1_maximum_expectation_error": 4.440892098500626e-16, "claim2_ccp_aon_wins": 9, "claim2_ccp_classical_material_wins": 27, "claim2_ccp_efficiency_comparisons": 36, "claim2_ccp_efficiency_wins": 36, "claim2_ccp_minimum_classical_relative_reduction": 0.23664123574004337, "claim2_efficiency_comparisons": 24, "claim2_efficiency_wins": 24, "claim2_maximum_relative_reduction": 0.959609208072499, "claim2_minimum_relative_reduction": 0.40302055578705925, "claim2_p2e_coverage_max": 0.9634375000000001, "claim2_p2e_coverage_min": 0.9490322580645161, "claim2_raw_rows": 1920, "claim3_eccp_coverage_max": 0.904622641509434, "claim3_eccp_coverage_min": 0.8902991304347826, "claim3_exchangeable_prefix_cases": 5, "claim3_exchangeable_prefix_tail_to_alpha_max": 0.9523809523809523, "claim3_exchangeable_randomized_tail_to_alpha_max": 0.9727207182725058, "claim3_execution_adapter": "vectorized-exact-postprocessing-v1", "claim3_p2e_coverage_max": 0.9186792452830188, "claim3_p2e_coverage_min": 0.8902991304347826, "claim3_raw_rows": 11700, "claim3_valid_randomized_tail_to_alpha_max": 0.9999999999999999, "claim3_valid_tail_to_alpha_max": 0.9523809523809523, "claim3_weca_independence_cases": 6, "headline_ca_dispersion_cells": 1, "headline_ca_dispersion_passing_scalars": 3, "headline_ca_dispersion_scalars": 4, "headline_cells": 122, "headline_discrepancy_cells": 27, "headline_discrepancy_scalars": 108, "headline_scalars": 488, "headline_source_replay_cells": 18, "headline_source_replay_scalars": 72, "headline_unaffected_cells": 94, "headline_unaffected_scalars": 376, "maximum_points": 12, "sigmoid_mechanism_cases": 18, "source_anchors": 10, "standard_ccp_bound_cases": 4}

````


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_75bc7afe0889", "created_at": "2026-07-19T19:00:34+00:00", "title": "Final outcome", "pinned": true, "pinned_at": "2026-07-19T19:00:35+00:00"}
-->
All six anchored jury claims are verified at the declared scope. The source-bound mechanism audit covers Definition 2.2, Proposition 2.3, Theorem 2.6/Equation 9, Propositions 4.1–4.2, and Section 5; independent exact/numerical certificates verify set preservation, AoN uniqueness, sigmoid properties and dominance, ECCP coverage, and tuning-independent WECA validity. Complete released CA and CCP runs supply 1,920 + 11,700 raw cells. All 376 unaffected table scalars reproduce within fixed tolerances; one CA finite-seed length-SD scalar is `0.201898618094345` versus `0.18`, and the paper/released-code F1/F2/F3 inconsistency affecting 108 scalars is source-hash-bound, numerically witnessed, and disclosed rather than force-fit. The reversible released log/square-root column swap independently replays all 72 affected scalars within the same fixed tolerances.

## Scope & cost

| Item | This reproduction | Paper protocol |
| --- | --- | --- |
| Claims 1-3 | 18 finite-rank identities + 4 exact uniqueness budgets + 18 sigmoid cases | Full stated mechanisms and theorem domain |
| Claims 4 and 6 / CCP | 11,700 raw cells; three datasets x 100 seeds x three models x 13 methods; exact coupling/orbit LPs | Same released data, seeds, models, and K=15/15/20 |
| Claim 5 / CA | 1,920 raw cells; four tasks x 20 seeds x 24 methods; source-bound split audit | Same released tasks, seeds, methods, M=512, B=500 |
| Hardware | Local CPU; no GPU | CPU-compatible released implementation |
| External compute cost | $0 | No cloud run required |
| Outcome | 6/6 anchored claims verified; 12 possible points | Full challenge-claim scope |

Source float underflow for already-excluded extreme e-values is disclosed; stable log-e arithmetic confirms strict positivity and leaves every threshold decision unchanged.

FULL_GATE_READY: jNv4sl4YZH


---
<!-- trackio-cell
{"type": "code", "id": "cell_65ba18bfb646", "created_at": "2026-07-19T19:03:20+00:00", "title": "Fail-closed full publication gate", "command": ["python", "repro/src/prepublish_gate.py", "--output", "outputs/prepublish_gate.json"], "exit_code": 0, "duration_s": 30.799}
-->
````bash
$ python repro/src/prepublish_gate.py --output outputs/prepublish_gate.json
````

exit 0 · 30.8s


````python title=prepublish_gate.py
#!/usr/bin/env python3
"""Fail-closed local publication gate for the complete six-claim artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_COMMIT = "66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974"
DEFAULT_CLAIMS_URL = (
    "https://huggingface.co/spaces/ICML-2026-agent-repro/challenge/"
    "resolve/main/claims.json"
)
ANCHORED_CLAIMS_URL = (
    "https://huggingface.co/spaces/ICML-2026-agent-repro/challenge/"
    "resolve/main/claims_anchored.json"
)
# Anchored claims override the broad fallback claims in the challenge frontend.
# Keep this alias for callers that need the effective scoring source.
CLAIMS_URL = ANCHORED_CLAIMS_URL
REQUIRED_TAGS = {"icml2026-repro", "paper-jNv4sl4YZH"}
JURY_CLAIM_TEXTS = (
    "A calibrator is defined as set-preserving when converting conformal p-values at level alpha into e-values yields prediction sets identical to thresholding the e-values directly at 1/alpha (Section 2.1, Definition 2.2)",
    "Among left-continuous p-to-e calibrators, only the all-or-nothing calibrator can be exactly set-preserving, which motivates a new sigmoid-based P2E construction (Proposition 2.3, Theorem 2.6, Equation 9)",
    "The proposed sigmoid-based P2E calibrator is exact (expectation equal to 1), smooth, invertible, strictly positive, and strictly dominates the all-or-nothing calibrator in aggregation settings (Theorem 2.6)",
    "Applied to e-Cross-Conformal Prediction (ECCP), the P2E calibrator preserves exact 1-alpha coverage, whereas standard cross-conformal-prediction variants only guarantee approximate 1-2alpha coverage (Proposition 4.1)",
    "Applied to Weighted Conformal Aggregation (WECA), data-dependent weighted merging of e-values across multiple models retains valid coverage (Proposition 4.2)",
    "Empirically, ECCP using the proposed P2E calibrator produces smaller prediction sets than baseline p-to-e conversion methods while maintaining valid coverage (Section 5)",
)
FALLBACK_JURY_CLAIM_TEXTS = (
    "P2E calibrator converts conformal p-values to e-values without altering the induced prediction set",
    "Yields substantial efficiency gains over existing p-to-e methods in conformal inference",
    "Enables exact 1-α coverage in cross-conformal prediction and conformal aggregation",
)
HEADLINE_TOLERANCES = {
    "coverage_absolute_tolerance": 0.01,
    "coverage_sd_absolute_tolerance": 0.01,
    "length_relative_tolerance": 0.05,
    "length_sd_relative_tolerance": 0.10,
}
EXPECTED_CA_PROTOCOL = {
    "source": "Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974",
    "tasks": [
        "dataset_361237",
        "dataset_361235",
        "dataset_361244",
        "dataset_361234",
    ],
    "task_ids": [361237, 361235, 361244, 361234],
    "seeds": [
        42, 0, 1, 7, 10, 13, 17, 19, 23, 29,
        31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    ],
    "alpha": 0.05,
    "M": 512,
    "B": 500,
}
EXPECTED_CCP_PROTOCOL = {
    "source": "Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974",
    "datasets": {"boston": 15, "abalone": 15, "parkinson": 20},
    "seeds": list(range(45, 145)),
    "models": ["OLS", "RF", "Lasso"],
    "methods": [
        "mod-cross",
        "e-mod-cross",
        "u-mod-cross",
        "eu-mod-cross",
        "cross",
        "ECCP",
        "ECCP_exch",
        "UR-ECCP_exch",
        "ECCP(ind)",
        "ECCP(sqrt)",
        "ECCP(log)",
        "ECCP(linear)",
        "ECCP (2α)",
    ],
    "alpha": 0.1,
    "grid_points": 300,
    "execution_adapter": "vectorized-exact-postprocessing-v1",
}
TEXT_SUFFIXES = {
    "", ".cfg", ".csv", ".gitignore", ".ini", ".json", ".md", ".py",
    ".sh", ".toml", ".txt", ".yaml", ".yml",
}
SKIP_PARTS = {".git", ".venv", "__pycache__"}
SECRET_PATTERNS = (
    re.compile("hf" + r"_[A-Za-z0-9]{20,}"),
    re.compile("gh" + r"[pousr]_[A-Za-z0-9]{20,}"),
    re.compile("AKIA" + r"[A-Z0-9]{16}"),
)


def run(command: list[str]) -> str:
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    display_command = list(command)
    if display_command and display_command[0] == sys.executable:
        display_command[0] = "python"
    print(f"$ {' '.join(display_command)}")
    print(output.rstrip())
    result.check_returncode()
    return output


def load_json(relative: str) -> dict[str, object]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def assert_summary(payload: dict[str, object], required_true: tuple[str, ...]) -> None:
    summary = payload["summary"]
    assert isinstance(summary, dict)
    for key in required_true:
        assert summary.get(key) is True, f"summary gate failed: {key}={summary.get(key)!r}"


def assert_exact_ccp_protocol(protocol: dict[str, object]) -> None:
    """Reject self-consistent CCP output produced at any non-paper scope."""
    assert protocol == EXPECTED_CCP_PROTOCOL, "CCP paper protocol drift"


def assert_exact_ca_protocol(protocol: dict[str, object]) -> None:
    """Reject self-consistent CA output produced at any non-paper scope."""
    assert protocol == EXPECTED_CA_PROTOCOL, "CA paper protocol drift"


def assert_live_jury_claims(claims: object) -> None:
    """Require the effective anchored entry to retain all six pinned claims."""
    assert isinstance(claims, list), "live jury entry is not a claim list"
    assert len(claims) == 6, "live anchored jury claim count changed"
    texts = tuple(
        claim.get("text") if isinstance(claim, dict) else None for claim in claims
    )
    assert texts == JURY_CLAIM_TEXTS, "live jury claim wording changed"


def fetch_claim_payload(url: str) -> dict[str, object]:
    request = urllib.request.Request(
        url, headers={"User-Agent": "icml2026-reproduction-gate/1"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    assert isinstance(payload, dict), "live claims payload is not a mapping"
    return payload


def fetch_live_jury_claims() -> list[dict[str, object]]:
    """Mirror the frontend merge and prove the anchored override is live."""
    fallback_payload = fetch_claim_payload(DEFAULT_CLAIMS_URL)
    anchored_payload = fetch_claim_payload(ANCHORED_CLAIMS_URL)
    fallback = fallback_payload.get("jNv4sl4YZH")
    assert isinstance(fallback, list), "fallback jury entry is not a claim list"
    fallback_texts = tuple(
        claim.get("text") if isinstance(claim, dict) else None for claim in fallback
    )
    assert fallback_texts == FALLBACK_JURY_CLAIM_TEXTS, (
        "fallback jury claim wording changed"
    )
    claims = anchored_payload.get("jNv4sl4YZH")
    assert_live_jury_claims(claims)
    return claims


def text_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES and path.stat().st_size <= 20_000_000:
            files.append(path)
    return files


def validate_local_path_artifacts(
    metadata: dict[str, object], root: Path = ROOT
) -> int:
    """Validate Trackio's local-only artifact map without publishing its paths."""
    local_path_artifacts = metadata.get("local_path_artifacts", [])
    assert isinstance(local_path_artifacts, list)
    for entry in local_path_artifacts:
        assert isinstance(entry, dict)
        relative_text = str(entry.get("path", ""))
        relative = Path(relative_text)
        assert relative_text and relative_text != "."
        assert not relative.is_absolute() and ".." not in relative.parts
        expected = (root / relative).resolve()
        recorded = Path(str(entry.get("abs_path", ""))).resolve()
        assert recorded == expected, f"Trackio artifact path mismatch: {relative}"
        assert expected.is_file(), f"Trackio artifact is missing: {relative}"
    return len(local_path_artifacts)


def validate_required_local_artifact(
    metadata: dict[str, object], relative: str, root: Path = ROOT
) -> dict[str, object]:
    """Require one exact Trackio path-artifact entry for the final bundle."""
    validate_local_path_artifacts(metadata, root)
    entries = metadata.get("local_path_artifacts", [])
    assert isinstance(entries, list)
    matches = [entry for entry in entries if entry.get("path") == relative]
    assert len(matches) == 1, f"required Trackio artifact is not registered: {relative}"
    entry = matches[0]
    path = root / relative
    assert entry.get("artifact_type") == "dataset"
    assert entry.get("size") == path.stat().st_size
    return entry


def hygiene_gate() -> dict[str, object]:
    env_files = [
        str(path.relative_to(ROOT))
        for path in ROOT.rglob(".env*")
        if path.is_file() and not any(part in SKIP_PARTS for part in path.parts)
    ]
    secret_hits = []
    absolute_path_hits = []
    sensitive_name = "HF" + "_" + "TOKEN"
    absolute_prefix = "/home/" + "dineshai/"
    scanned_files = text_files()
    for path in scanned_files:
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative = str(path.relative_to(ROOT))
        if sensitive_name in content:
            secret_hits.append({"file": relative, "kind": "sensitive variable name"})
        for pattern in SECRET_PATTERNS:
            if pattern.search(content):
                secret_hits.append({"file": relative, "kind": "token-like value"})
        # Trackio needs an absolute source path in its *local-only* metadata to
        # upload a path artifact.  That file is gitignored and is never part of
        # the published Space; validate its mapping separately below.  Every
        # publishable file remains subject to the absolute-path prohibition.
        if absolute_prefix in content and relative != ".trackio/metadata.json":
            absolute_path_hits.append(relative)
    metadata = load_json(".trackio/metadata.json")
    local_path_artifact_count = validate_local_path_artifacts(metadata)
    assert not env_files, f"environment files present: {env_files}"
    assert not secret_hits, f"secret-like content present: {secret_hits}"
    assert not absolute_path_hits, f"absolute local paths present: {absolute_path_hits}"
    return {
        "env_files": env_files,
        "secret_hits": secret_hits,
        "absolute_path_hits": absolute_path_hits,
        "local_path_artifact_count": local_path_artifact_count,
        "text_files_scanned": len(scanned_files),
    }


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with (ROOT / relative).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_artifact_bundle(relative: str, artifacts: tuple[str, ...]) -> str:
    output = ROOT / relative
    temporary = output.with_name(output.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for artifact in artifacts:
            path = ROOT / artifact
            record = {
                "path": artifact,
                "sha256": sha256(artifact),
                "payload": json.loads(path.read_text(encoding="utf-8")),
            }
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    temporary.replace(output)
    return validate_artifact_bundle(relative, artifacts)


def validate_artifact_bundle(relative: str, artifacts: tuple[str, ...]) -> str:
    """Re-parse every JSONL record and bind it to the current source artifact."""
    bundle = ROOT / relative
    lines = bundle.read_text(encoding="utf-8").splitlines()
    assert len(lines) == len(artifacts), (
        f"bundle record count mismatch: {len(lines)} != {len(artifacts)}"
    )
    for line, artifact in zip(lines, artifacts, strict=True):
        record = json.loads(line)
        assert set(record) == {"path", "sha256", "payload"}
        assert record["path"] == artifact
        source = ROOT / artifact
        assert record["sha256"] == sha256(artifact)
        assert record["payload"] == json.loads(source.read_text(encoding="utf-8"))
    return sha256(relative)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("outputs/prepublish_gate.json"))
    args = parser.parse_args()

    source_commit = run(["git", "-C", "upstream", "rev-parse", "HEAD"]).strip()
    assert source_commit == SOURCE_COMMIT
    assert run(["git", "-C", "upstream", "status", "--porcelain"]).strip() == ""

    metadata = load_json(".trackio/metadata.json")
    assert metadata["openreview_id"] == "jNv4sl4YZH"
    assert metadata["arxiv_id"] == "2606.03600"
    assert metadata["paper"] == {
        "arxiv_id": "2606.03600",
        "openreview_id": "jNv4sl4YZH",
    }
    assert REQUIRED_TAGS <= set(metadata["tags"])

    jury = load_json("repro/configs/jury_claims.json")
    assert jury["openreview_id"] == "jNv4sl4YZH"
    assert jury["source_url"] == ANCHORED_CLAIMS_URL
    assert jury["fallback_source_url"] == DEFAULT_CLAIMS_URL
    assert jury["maximum_points"] == 12
    assert tuple(claim["text"] for claim in jury["claims"]) == JURY_CLAIM_TEXTS
    assert [claim["claim"] for claim in jury["claims"]] == [1, 2, 3, 4, 5, 6]
    assert [claim["possible_points"] for claim in jury["claims"]] == [2] * 6
    live_jury_claims = fetch_live_jury_claims()

    headline_config = load_json("repro/configs/paper_headlines.json")
    assert headline_config["source"] == (
        "arXiv:2606.03600v1, Table 2, CA alternative-calibrator table, "
        "and Appendix Tables 6-8"
    )
    assert all(
        headline_config["comparison_policy"].get(key) == value
        for key, value in HEADLINE_TOLERANCES.items()
    )
    assert sum(
        len(methods)
        for methods in headline_config["conformal_aggregation"].values()
    ) == 32
    assert sum(
        len(methods)
        for models in headline_config["cross_conformal"].values()
        for methods in models.values()
    ) == 90

    commands = (
        [sys.executable, "repro/src/verify_source_manifest.py", "--source", "upstream", "--output", "outputs/source_manifest_audit.json"],
        [sys.executable, "repro/src/verify_ca_inputs.py", "--source", "upstream", "--output", "outputs/ca_input_audit.json"],
        [sys.executable, "repro/src/verify_ca_p2e_domains.py", "--source", "upstream", "--output", "outputs/ca_p2e_domain_audit.json"],
        [sys.executable, "repro/src/verify_p2e_identity.py", "--output", "outputs/claim1_independent.json"],
        [sys.executable, "repro/src/crosscheck_source_p2e.py", "--source", "upstream", "--output", "outputs/claim1_source_crosscheck.json"],
        [sys.executable, "repro/src/verify_anchored_claims.py", "--output", "outputs/anchored_claims_mechanism.json"],
        [sys.executable, "repro/src/verify_e_merge_coverage.py", "--output", "outputs/claim3_independent_e_merge.json"],
        [sys.executable, "repro/src/verify_weca_independence.py", "--source", "upstream", "--output", "outputs/weca_independence_audit.json"],
        [sys.executable, "repro/src/verify_ca_results.py", "--raw-dir", "outputs/raw/author_ca", "--output", "outputs/claim2_independent.json"],
        [sys.executable, "repro/src/verify_ccp_results.py", "--raw-dir", "outputs/raw/author_ccp", "--output", "outputs/claim3_independent.json"],
        [sys.executable, "repro/src/verify_paper_table_fixture.py", "--output", "outputs/paper_table_fixture_audit.json"],
        [sys.executable, "repro/src/verify_ccp_calibrator_contract.py", "--source", "upstream", "--output", "outputs/ccp_calibrator_contract_audit.json"],
        [sys.executable, "repro/src/compare_paper_headlines.py", "--ca", "outputs/claim2_independent.json", "--ccp", "outputs/claim3_independent.json", "--output", "outputs/paper_headline_comparison.json"],
        [sys.executable, "-m", "unittest", "discover", "-s", "repro/tests", "-v"],
    )
    command_outputs = [run(command) for command in commands]

    source_manifest = load_json("outputs/source_manifest_audit.json")
    assert source_manifest["source"] == (
        "Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974"
    )
    assert source_manifest["git_commit"] == SOURCE_COMMIT
    assert source_manifest["manifest_sha256"] == sha256(
        "repro/configs/source_manifest.json"
    )
    assert source_manifest["summary"] == {
        "all_dataset_shapes_verified": True,
        "all_files_git_blob_verified": True,
        "all_files_hash_verified": True,
        "all_loader_outputs_verified": True,
        "dataset_count": 3,
        "file_count": 10,
        "source_worktree_clean": True,
        "total_dataset_rows": 10_558,
        "total_source_input_bytes": 1_181_454,
    }

    ca_inputs = load_json("outputs/ca_input_audit.json")
    assert ca_inputs["source"] == (
        "Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974"
    )
    assert ca_inputs["loader_sha256"] == (
        "7aa2daf12c176af1679a5553fe903d594bc721f1b8c5e231de5a1fd8fc26a82f"
    )
    assert ca_inputs["manifest_sha256"] == sha256(
        "repro/configs/ca_input_manifest.json"
    )
    assert ca_inputs["summary"] == {
        "all_processed_array_hashes_verified": True,
        "all_processed_values_finite": True,
        "all_task_metadata_verified": True,
        "source_worktree_clean": True,
        "task_count": 4,
        "total_feature_values": 47_126,
        "total_rows": 7_776,
    }

    ca_domains = load_json("outputs/ca_p2e_domain_audit.json")
    assert ca_domains["source"] == (
        "Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974"
    )
    assert ca_domains["context_counts"] == {
        "eca": 560, "weca_final": 560, "weca_tune": 560
    }
    assert ca_domains["boundary_context_counts"] == {
        "eca": 33, "weca_final": 22, "weca_tune": 25
    }
    assert ca_domains["summary"] == {
        "all_boundary_source_float_expectations_pass": True,
        "all_boundary_source_set_identities_pass": True,
        "all_boundary_source_uses_upper_bracket": True,
        "all_contexts_accounted_for": True,
        "all_exact_aon_repairs_pass": True,
        "all_low_level_conditions_pass": True,
        "all_theorem_contexts_in_domain": True,
        "boundary_context_count": 80,
        "boundary_unique_size_count": 27,
        "context_count": 1_680,
        "maximum_boundary_float_deviation_from_aon": 6.422607377437694e-174,
        "positive_exact_boundary_calibrator_impossible": True,
        "theorem_context_count": 1_600,
    }

    claim1 = load_json("outputs/claim1_independent.json")
    assert_summary(
        claim1,
        (
            "all_classic_controls_inflate_sets",
            "all_domain_controls_rejected",
            "all_exact_e_expectations_pass",
            "all_positive_pass",
            "all_set_identities_pass",
            "all_theorem_domain_verified",
            "all_threshold_identities_pass",
        ),
    )
    assert claim1["summary"]["case_count"] == 18
    assert claim1["summary"]["classic_control_case_count"] == 18
    assert claim1["summary"]["domain_control_count"] == 5
    claim1_source = load_json("outputs/claim1_source_crosscheck.json")
    assert_summary(
        claim1_source,
        (
            "all_cleanroom_membership_pass",
            "all_source_expectations_pass",
            "all_source_membership_pass",
            "all_theorem_domain_verified",
            "underflow_is_documented",
        ),
    )
    assert claim1_source["summary"]["rows"] == 18
    anchored = load_json("outputs/anchored_claims_mechanism.json")
    assert anchored["source_url"] == "https://export.arxiv.org/e-print/2606.03600v1"
    assert anchored["source_archive_sha256"] == (
        "f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db"
    )
    assert anchored["main_tex_sha256"] == (
        "49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857"
    )
    assert anchored["summary"] == {
        "all_source_anchors_verified": True,
        "c1_definition_verified": True,
        "c2_aon_uniqueness_certificate_pass": True,
        "c2_aon_uniqueness_source_verified": True,
        "c2_left_continuity_witnesses_pass": True,
        "c2_uniqueness_level_count": 4,
        "c3_all_aggregation_dominance_pass": True,
        "c3_all_exact_expectations_pass": True,
        "c3_all_inverse_roundtrips_pass": True,
        "c3_all_pointwise_aon_dominance_pass": True,
        "c3_all_smoothness_certificates_pass": True,
        "c3_all_strict_positivity_pass": True,
        "c3_case_count": 18,
        "c4_eccp_proposition_verified": True,
        "c4_standard_ccp_bound_case_count": 4,
        "c4_standard_ccp_bound_verified": True,
        "c5_weca_proposition_verified": True,
        "c5_weighted_expectation_identity_verified": True,
        "c6_section5_scope_verified": True,
        "source_anchor_count": 10,
    }
    mechanism = load_json("outputs/claim3_independent_e_merge.json")
    assert_summary(
        mechanism,
        (
            "all_arbitrary_dependence_coverage_pass",
            "all_exchangeable_prefix_coverage_pass",
            "all_exchangeable_randomized_prefix_coverage_pass",
            "all_markov_coverage_events_pass",
            "all_merged_expectations_exact",
            "all_randomized_arbitrary_dependence_coverage_pass",
            "all_randomized_uniform_coverage_events_pass",
            "adaptive_randomized_weight_control_detected",
            "adaptive_weight_control_detected",
            "invalid_arbitrary_dependence_detected",
            "invalid_randomized_arbitrary_dependence_detected",
            "invalid_scaling_control_detected",
        ),
    )
    assert mechanism["summary"]["case_count"] == 8
    assert mechanism["summary"]["equal_weight_case_count"] == 2
    assert mechanism["summary"]["nonuniform_weight_case_count"] == 6
    assert mechanism["summary"]["exchangeable_prefix_case_count"] == 5
    assert mechanism["summary"]["invalid_arbitrary_dependence_rejection_count"] == 4
    assert mechanism["summary"]["invalid_randomized_arbitrary_dependence_rejection_count"] == 8
    assert mechanism["summary"]["invalid_scaling_control_rejection_count"] == 2
    assert mechanism["summary"]["adaptive_weight_rejection_count"] == 8
    assert mechanism["summary"]["adaptive_randomized_weight_rejection_count"] == 8
    assert mechanism["summary"]["invalid_exchangeable_prefix_rejection_count"] == 5
    assert mechanism["summary"]["invalid_exchangeable_randomized_prefix_rejection_count"] == 5

    weca_independence = load_json("outputs/weca_independence_audit.json")
    assert weca_independence["source"] == (
        "Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974"
    )
    assert weca_independence["methods_sha256"] == (
        "dda5d2429d4ca8c77be6a3b04bb3c159360bf3af58d1087a5f31cc17ea44cf86"
    )
    assert weca_independence["function_contract"]["sha256"] == (
        "541a30601a5346d0adbcf50bb9dcfd2e5e8317f7403fb4540516680a52751bfb"
    )
    assert weca_independence["summary"] == {
        "all_illegal_test_adaptive_controls_change": True,
        "all_required_flow_present": True,
        "all_split_partitions_disjoint": True,
        "all_weights_independent_of_final_calibration": True,
        "all_weights_independent_of_test_data_and_outcomes": True,
        "case_count": 6,
    }

    claim2 = load_json("outputs/claim2_independent.json")
    assert_exact_ca_protocol(claim2["protocol"])
    assert_summary(
        claim2,
        (
            "all_four_tasks_present",
            "all_full_seed_method_cells_present",
            "exact_cell_set",
            "all_substantial_efficiency_gains",
            "all_p2e_empirical_coverage_within_tolerance",
        ),
    )
    claim2_summary = claim2["summary"]
    assert claim2["rows_seen"] == claim2_summary["expected_rows"] == 1_920
    assert claim2_summary["observed_unique_cells"] == 1_920
    assert claim2_summary["comparison_count"] == claim2_summary["p2e_shorter_count"] == 24
    assert claim2_summary["substantial_efficiency_gain_count"] == 24
    assert claim2_summary["minimum_substantial_relative_reduction"] == 0.10
    assert claim2_summary["minimum_observed_relative_reduction"] >= 0.10
    assert claim2_summary["p2e_empirical_coverage_cell_count"] == 8
    assert claim2_summary["p2e_empirical_coverage_pass_count"] == 8
    assert claim2_summary["empirical_coverage_shortfall_tolerance"] == 0.02
    assert claim2_summary["duplicate_cell_count"] == 0
    assert claim2_summary["unexpected_row_count"] == 0
    assert claim2_summary["nonfinite_row_count"] == 0
    assert claim2_summary["invalid_metric_row_count"] == 0

    claim3 = load_json("outputs/claim3_independent.json")
    assert_summary(
        claim3,
        (
            "all_full_seed_cells_present",
            "exact_cell_set",
            "all_eccp_empirical_coverage_within_tolerance",
            "all_p2e_empirical_coverage_within_tolerance",
            "all_p2e_not_longer_than_existing_calibrators",
            "all_p2e_strictly_shorter_than_aon",
            "all_classical_efficiency_gains_substantial",
        ),
    )
    claim3_summary = claim3["summary"]
    assert_exact_ccp_protocol(claim3["protocol"])
    assert claim3["rows_seen"] == claim3_summary["expected_rows"] == 11_700
    assert claim3_summary["observed_unique_cells"] == 11_700
    assert claim3_summary["duplicate_cell_count"] == 0
    assert claim3_summary["unexpected_row_count"] == 0
    assert claim3_summary["nonfinite_row_count"] == 0
    assert claim3_summary["invalid_metric_row_count"] == 0
    assert claim3_summary["eccp_empirical_coverage_cell_count"] == 9
    assert claim3_summary["eccp_empirical_coverage_pass_count"] == 9
    assert claim3_summary["p2e_empirical_coverage_cell_count"] == 27
    assert claim3_summary["p2e_empirical_coverage_pass_count"] == 27
    assert claim3_summary["empirical_coverage_shortfall_tolerance"] == 0.02
    assert claim3_summary["calibrator_efficiency_comparison_count"] == 36
    assert claim3_summary["p2e_not_longer_count"] == 36
    assert claim3_summary["p2e_strictly_shorter_count"] == 36
    assert claim3_summary["aon_comparison_count"] == 9
    assert claim3_summary["aon_strictly_shorter_count"] == 9
    assert claim3_summary["classical_comparison_count"] == 27
    assert claim3_summary["classical_substantial_gain_count"] == 27
    assert claim3_summary["minimum_substantial_relative_reduction"] == 0.10
    assert claim3_summary["minimum_classical_relative_reduction"] >= 0.10

    fixture_audit = load_json("outputs/paper_table_fixture_audit.json")
    assert fixture_audit["source_url"] == "https://export.arxiv.org/e-print/2606.03600v1"
    assert fixture_audit["source_archive_sha256"] == (
        "f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db"
    )
    assert fixture_audit["main_tex_sha256"] == (
        "49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857"
    )
    assert fixture_audit["config_sha256"] == sha256(
        "repro/configs/paper_headlines.json"
    )
    assert fixture_audit["claim1_theorem_contract"] == {
        "label": "main_theorem",
        "alpha_rank_domain": "alpha*(n+1) > 1 and non-integer",
        "strict_s_interval_verified": True,
        "normalized_logistic_formula_verified": True,
        "theorem_block_sha256": (
            "86e98bc09083541aa2b908c96db4c460d78904929e64b6cf21bf1c435181ba71"
        ),
    }
    fixture_summary = fixture_audit["summary"]
    assert fixture_summary["all_fields_match"] is True
    assert fixture_summary["mismatch_count"] == 0
    assert fixture_summary["mismatch_paths"] == []
    assert fixture_summary["ca_cell_count"] == 32
    assert fixture_summary["ccp_cell_count"] == 90
    assert fixture_summary["total_cell_count"] == 122
    assert fixture_summary["scalar_count"] == 488

    calibrator_contract = load_json("outputs/ccp_calibrator_contract_audit.json")
    assert calibrator_contract["paper_source_archive_sha256"] == (
        "f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db"
    )
    assert calibrator_contract["paper_main_tex_sha256"] == (
        "49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857"
    )
    assert calibrator_contract["released_main_py_sha256"] == (
        "4bfabc2a937a633db3d95a70f76e961a5541319b332e1452617ca6f64a8a57d6"
    )
    assert calibrator_contract["released_eccp_utils_sha256"] == (
        "7ef06bed7bef7c72dae5f760cf0f0c2b4cf4318af44f87763ac8cc0ab0687593"
    )
    assert calibrator_contract["summary"] == {
        "paper_formula_contract_verified": True,
        "released_formula_contract_verified": True,
        "released_column_order_verified_for_all_models": True,
        "paper_source_column_mismatch_verified": True,
        "discrepant_method_count": 3,
        "affected_paper_table_cells": 27,
        "affected_paper_table_scalars": 108,
        "all_numerical_witness_values_differ": True,
    }

    headlines = load_json("outputs/paper_headline_comparison.json")
    assert_summary(
        headlines,
        (
            "all_unaffected_within_tolerance",
            "all_outside_tolerance_cells_accounted_for",
            "all_source_table_replays_within_tolerance",
        ),
    )
    assert headlines["paper_source"] == headline_config["source"]
    assert all(
        headlines["comparison_policy"].get(key) == value
        for key, value in HEADLINE_TOLERANCES.items()
    )
    assert headlines["summary"]["comparison_count"] == 122
    assert headlines["summary"]["scalar_comparison_count"] == 488
    assert headlines["summary"]["unaffected_comparison_count"] == 94
    assert headlines["summary"]["unaffected_within_tolerance_count"] == 94
    assert headlines["summary"]["unaffected_scalar_comparison_count"] == 376
    assert headlines["summary"]["unaffected_within_tolerance_scalar_count"] == 376
    assert headlines["summary"]["known_discrepancy_comparison_count"] == 27
    assert headlines["summary"]["known_discrepancy_scalar_comparison_count"] == 108
    replay_contract = {
        (dataset, model, paper_method, released_method)
        for dataset in ("boston", "abalone", "parkinson")
        for model in ("OLS", "RF", "Lasso")
        for paper_method, released_method in (
            ("ECCP(log)", "ECCP(sqrt)"),
            ("ECCP(sqrt)", "ECCP(log)"),
        )
    }
    assert {
        (
            row["dataset"],
            row["model"],
            row["paper_method"],
            row["released_method"],
        )
        for row in headlines["source_table_replay_comparisons"]
    } == replay_contract
    assert headlines["summary"]["source_table_replay_comparison_count"] == 18
    assert headlines["summary"]["source_table_replay_within_tolerance_count"] == 18
    assert headlines["summary"]["source_table_replay_scalar_comparison_count"] == 72
    assert (
        headlines["summary"]["source_table_replay_within_tolerance_scalar_count"]
        == 72
    )
    assert headlines["summary"]["known_ca_dispersion_discrepancy_count"] == 1
    assert headlines["summary"]["known_ca_dispersion_scalar_count"] == 4
    assert headlines["summary"]["known_ca_dispersion_within_tolerance_scalar_count"] == 3
    assert headlines["summary"]["known_ca_dispersion_outside_tolerance_count"] == 1
    assert headlines["summary"]["unexpected_outside_tolerance_count"] == 0

    required_trackio_text = {
        ".trackio/logbook/pages/claim-1/page.md": (
            "Claim 1 verdict",
        ),
        ".trackio/logbook/pages/claim-2/page.md": (
            "Independent full CA raw verification",
            "Claim 2 verdict",
        ),
        ".trackio/logbook/pages/claim-3/page.md": (
            "Independent full CCP raw verification",
            "Claim 3 verdict",
        ),
        ".trackio/logbook/pages/claim-4/page.md": (
            "Exchangeable and randomized e-merge coverage certificate",
            "Claim 4 verdict",
        ),
        ".trackio/logbook/pages/claim-5/page.md": (
            "Claim 5 verdict",
        ),
        ".trackio/logbook/pages/claim-6/page.md": (
            "Claim 6 verdict",
        ),
        ".trackio/logbook/pages/methods-source-audit/page.md": (
            "Six anchored-claim theorem and mechanism audit",
            "Released CA P2E theorem-domain audit",
            "Released OpenML CA input fingerprint audit",
            "Released source and dataset manifest audit",
            "Primary TeX table fixture audit",
            "Paper and released-code calibrator contract audit",
            "WECA independent-tuning audit",
        ),
        ".trackio/logbook/pages/conclusion/page.md": (
            "FULL_GATE_READY: jNv4sl4YZH",
        ),
    }
    for relative, markers in required_trackio_text.items():
        content = (ROOT / relative).read_text(encoding="utf-8")
        for marker in markers:
            assert marker in content, f"missing Trackio marker {marker!r} in {relative}"

    hygiene = hygiene_gate()
    artifacts = (
        "outputs/ca_p2e_domain_audit.json",
        "outputs/ca_input_audit.json",
        "outputs/source_manifest_audit.json",
        "outputs/claim1_independent.json",
        "outputs/claim1_source_crosscheck.json",
        "outputs/anchored_claims_mechanism.json",
        "outputs/claim2_independent.json",
        "outputs/claim3_independent_e_merge.json",
        "outputs/weca_independence_audit.json",
        "outputs/claim3_independent.json",
        "outputs/paper_table_fixture_audit.json",
        "outputs/ccp_calibrator_contract_audit.json",
        "outputs/paper_headline_comparison.json",
        "outputs/final_logbook_cells.json",
        *(f"outputs/raw/author_ca/dataset_{task}.json" for task in (361237, 361235, 361244, 361234)),
        *(f"outputs/raw/author_ccp/{dataset}.json" for dataset in ("boston", "abalone", "parkinson")),
    )
    artifact_hashes = {relative: sha256(relative) for relative in artifacts}
    bundle = "outputs/jNv4sl4YZH_full_evidence_bundle.jsonl"
    bundle_hash = write_artifact_bundle(bundle, artifacts)
    result = {
        "paper": "jNv4sl4YZH",
        "source_commit": source_commit,
        "claims": len(jury["claims"]),
        "claims_source_url": ANCHORED_CLAIMS_URL,
        "claims_source_urls": {
            "anchored": ANCHORED_CLAIMS_URL,
            "fallback": DEFAULT_CLAIMS_URL,
        },
        "live_claims_verified": len(live_jury_claims),
        "maximum_points": jury["maximum_points"],
        "tests_passed": True,
        "command_count": len(command_outputs),
        "hygiene": hygiene,
        "artifact_sha256": artifact_hashes,
        "artifact_paths": list(artifacts),
        "trackio_artifact_bundle": bundle,
        "trackio_artifact_bundle_sha256": bundle_hash,
        "publication_gate_passed": True,
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".tmp")
    temporary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(output)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

````


````json title=prepublish_gate.json
{
  "artifact_paths": [
    "outputs/ca_p2e_domain_audit.json",
    "outputs/ca_input_audit.json",
    "outputs/source_manifest_audit.json",
    "outputs/claim1_independent.json",
    "outputs/claim1_source_crosscheck.json",
    "outputs/anchored_claims_mechanism.json",
    "outputs/claim2_independent.json",
    "outputs/claim3_independent_e_merge.json",
    "outputs/weca_independence_audit.json",
    "outputs/claim3_independent.json",
    "outputs/paper_table_fixture_audit.json",
    "outputs/ccp_calibrator_contract_audit.json",
    "outputs/paper_headline_comparison.json",
    "outputs/final_logbook_cells.json",
    "outputs/raw/author_ca/dataset_361237.json",
    "outputs/raw/author_ca/dataset_361235.json",
    "outputs/raw/author_ca/dataset_361244.json",
    "outputs/raw/author_ca/dataset_361234.json",
    "outputs/raw/author_ccp/boston.json",
    "outputs/raw/author_ccp/abalone.json",
    "outputs/raw/author_ccp/parkinson.json"
  ],
  "artifact_sha256": {
    "outputs/anchored_claims_mechanism.json": "9b6c4163fd164be241123c12beea1a00c8f0c1a3565c01e0f4c7f95a2078994e",
    "outputs/ca_input_audit.json": "ccdfff3c7c7723c7d4707f1825cd098cef933628fe64e32c12947435816ab1e7",
    "outputs/ca_p2e_domain_audit.json": "bd2784e4d4ef04a14f723ffde8dbaa86f678930d808d5dafb7bc03090f71b41b",
    "outputs/ccp_calibrator_contract_audit.json": "fde3e9dbf47eac2275237db7ceb314b588df132a448fc5d4d10e2196804f7a14",
    "outputs/claim1_independent.json": "f9c17dd53546ab5d78387f8f91e8d44fe45cf16886554cb3d810a476ff80e0bb",
    "outputs/claim1_source_crosscheck.json": "e86dc02f33bd1b27d0ded95b3b74186b6b014273eb5651b13aa385e0df11cd04",
    "outputs/claim2_independent.json": "7eaf8410f54c57ac4c82972c6a8d3cb97f701cc39ecd1c74c14a6273c52a9d03",
    "outputs/claim3_independent.json": "97a5aa171de3f9767fe5d3478621b317db88dc70e5409a5dce94baf76e6a6533",
    "outputs/claim3_independent_e_merge.json": "deea168006396145de5361fe2cb96788e97f093826691e125e27f5dab02a3efe",
    "outputs/final_logbook_cells.json": "0c5d25948d4eddfc514deda8d11e55433cfea11bca4860a320fa83da07f225dc",
    "outputs/paper_headline_comparison.json": "b57db17c209f6da34ffbc110ea86abe9f75e1996086096bb2f93b511393085c8",
    "outputs/paper_table_fixture_audit.json": "b2ccba2f76b937a9e086ced4cdbbd610cf1225c4a598164424d30673bf5fe85c",
    "outputs/raw/author_ca/dataset_361234.json": "149ae7b7ae2c93d94f2a2d29b1eb75403a3283b70cc026f7236504176cc71441",
    "outputs/raw/author_ca/dataset_361235.json": "9d758888f6b6b3788204e6859be122ebfee1f00ff7b48eebce3314b7e43cff7b",
    "outputs/raw/author_ca/dataset_361237.json": "668325f55a76b669b3ecf142d4dd1aaa527ad74a0e6ea83f85b4930a84973981",
    "outputs/raw/author_ca/dataset_361244.json": "d566945c9fafba712708c7f3c13a96781f53e9d3148fddc94d8cc9c054cca188",
    "outputs/raw/author_ccp/abalone.json": "fac6af8455aab8aa28e0f3bfd6feb0f033db3636902fa0a09e9a0a44331f0e05",
    "outputs/raw/author_ccp/boston.json": "31b8a6c5c81b468e50d23b6d55b91e3b6f5da91f4f8a3c413a1e657b7d2ca4b0",
    "outputs/raw/author_ccp/parkinson.json": "d128fa66a8e2c4bd1f40cae95b3bfc07ef27daf3449064a220ef79b72898a108",
    "outputs/source_manifest_audit.json": "ef34215e7c921fd5204287452fc7b365d7e9d6a9422f695f1a3e01ce60c4e461",
    "outputs/weca_independence_audit.json": "77546ac8887504af6891cb9892f8f8728782fce17bd2d653bedc2fd0504ed4d9"
  },
  "claims": 6,
  "claims_source_url": "https://huggingface.co/spaces/ICML-2026-agent-repro/challenge/resolve/main/claims_anchored.json",
  "claims_source_urls": {
    "anchored": "https://huggingface.co/spaces/ICML-2026-agent-repro/challenge/resolve/main/claims_anchored.json",
    "fallback": "https://huggingface.co/spaces/ICML-2026-agent-repro/challenge/resolve/main/claims.json"
  },
  "command_count": 14,
  "hygiene": {
    "absolute_path_hits": [],
    "env_files": [],
    "local_path_artifact_count": 0,
    "secret_hits": [],
    "text_files_scanned": 97
  },
  "live_claims_verified": 6,
  "maximum_points": 12,
  "paper": "jNv4sl4YZH",
  "publication_gate_passed": true,
  "source_commit": "66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974",
  "tests_passed": true,
  "trackio_artifact_bundle": "outputs/jNv4sl4YZH_full_evidence_bundle.jsonl",
  "trackio_artifact_bundle_sha256": "1cd1115ee4fefc260c79512eb1a4bea61f342ebca5bb9acf3cc5b8ca91f90359"
}

````


````output
$ git -C upstream rev-parse HEAD
66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974
$ git -C upstream status --porcelain

$ python repro/src/verify_source_manifest.py --source upstream --output outputs/source_manifest_audit.json
{"all_dataset_shapes_verified": true, "all_files_git_blob_verified": true, "all_files_hash_verified": true, "all_loader_outputs_verified": true, "dataset_count": 3, "file_count": 10, "source_worktree_clean": true, "total_dataset_rows": 10558, "total_source_input_bytes": 1181454}
$ python repro/src/verify_ca_inputs.py --source upstream --output outputs/ca_input_audit.json
{"all_processed_array_hashes_verified": true, "all_processed_values_finite": true, "all_task_metadata_verified": true, "source_worktree_clean": true, "task_count": 4, "total_feature_values": 47126, "total_rows": 7776}
$ python repro/src/verify_ca_p2e_domains.py --source upstream --output outputs/ca_p2e_domain_audit.json
{"all_boundary_source_float_expectations_pass": true, "all_boundary_source_set_identities_pass": true, "all_boundary_source_uses_upper_bracket": true, "all_contexts_accounted_for": true, "all_exact_aon_repairs_pass": true, "all_low_level_conditions_pass": true, "all_theorem_contexts_in_domain": true, "boundary_context_count": 80, "boundary_unique_size_count": 27, "context_count": 1680, "maximum_boundary_float_deviation_from_aon": 6.422607377437694e-174, "positive_exact_boundary_calibrator_impossible": true, "theorem_context_count": 1600}
$ python repro/src/verify_p2e_identity.py --output outputs/claim1_independent.json
{"all_classic_controls_inflate_sets": true, "all_domain_controls_rejected": true, "all_exact_e_expectations_pass": true, "all_positive_pass": true, "all_set_identities_pass": true, "all_theorem_domain_verified": true, "all_threshold_identities_pass": true, "case_count": 18, "classic_control_case_count": 18, "domain_control_count": 5}
$ python repro/src/crosscheck_source_p2e.py --source upstream --output outputs/claim1_source_crosscheck.json
{"all_cleanroom_membership_pass": true, "all_source_expectations_pass": true, "all_source_membership_pass": true, "all_theorem_domain_verified": true, "rows": 18, "underflow_is_documented": true}
$ python repro/src/verify_anchored_claims.py --output outputs/anchored_claims_mechanism.json
{"all_source_anchors_verified": true, "c1_definition_verified": true, "c2_aon_uniqueness_certificate_pass": true, "c2_aon_uniqueness_source_verified": true, "c2_left_continuity_witnesses_pass": true, "c2_uniqueness_level_count": 4, "c3_all_aggregation_dominance_pass": true, "c3_all_exact_expectations_pass": true, "c3_all_inverse_roundtrips_pass": true, "c3_all_pointwise_aon_dominance_pass": true, "c3_all_smoothness_certificates_pass": true, "c3_all_strict_positivity_pass": true, "c3_case_count": 18, "c4_eccp_proposition_verified": true, "c4_standard_ccp_bound_case_count": 4, "c4_standard_ccp_bound_verified": true, "c5_weca_proposition_verified": true, "c5_weighted_expectation_identity_verified": true, "c6_section5_scope_verified": true, "source_anchor_count": 10}
$ python repro/src/verify_e_merge_coverage.py --output outputs/claim3_independent_e_merge.json
{"adaptive_randomized_weight_control_detected": true, "adaptive_randomized_weight_rejection_count": 8, "adaptive_weight_control_detected": true, "adaptive_weight_rejection_count": 8, "all_arbitrary_dependence_coverage_pass": true, "all_exchangeable_prefix_coverage_pass": true, "all_exchangeable_randomized_prefix_coverage_pass": true, "all_markov_coverage_events_pass": true, "all_merged_expectations_exact": true, "all_randomized_arbitrary_dependence_coverage_pass": true, "all_randomized_uniform_coverage_events_pass": true, "case_count": 8, "equal_weight_case_count": 2, "exchangeable_prefix_case_count": 5, "invalid_arbitrary_dependence_detected": true, "invalid_arbitrary_dependence_rejection_count": 4, "invalid_exchangeable_prefix_rejection_count": 5, "invalid_exchangeable_randomized_prefix_rejection_count": 5, "invalid_randomized_arbitrary_dependence_detected": true, "invalid_randomized_arbitrary_dependence_rejection_count": 8, "invalid_scaling_control_detected": true, "invalid_scaling_control_rejection_count": 2, "maximum_exchangeable_prefix_tail_to_alpha_ratio": 0.9523809523809523, "maximum_exchangeable_randomized_prefix_tail_to_alpha_ratio": 0.9727207182725058, "maximum_valid_randomized_tail_to_alpha_ratio": 0.9999999999999999, "maximum_valid_randomized_worst_case_failure_probability": 0.19999999999999998, "maximum_valid_tail_to_alpha_ratio": 0.9523809523809523, "maximum_valid_worst_case_tail_probability": 0.19047619047619047, "minimum_adaptive_randomized_tail_to_alpha_ratio": 1.9428630069079045, "minimum_adaptive_tail_to_alpha_ratio": 1.8181818181818181, "nonuniform_weight_case_count": 6}
$ python repro/src/verify_weca_independence.py --source upstream --output outputs/weca_independence_audit.json
{"all_illegal_test_adaptive_controls_change": true, "all_required_flow_present": true, "all_split_partitions_disjoint": true, "all_weights_independent_of_final_calibration": true, "all_weights_independent_of_test_data_and_outcomes": true, "case_count": 6}
$ python repro/src/verify_ca_results.py --raw-dir outputs/raw/author_ca --output outputs/claim2_independent.json
{"all_four_tasks_present": true, "all_full_seed_method_cells_present": true, "all_p2e_empirical_coverage_within_tolerance": true, "all_substantial_efficiency_gains": true, "comparison_count": 24, "dataset_integrity": {"dataset_361234": true, "dataset_361235": true, "dataset_361237": true, "dataset_361244": true}, "duplicate_cell_count": 0, "empirical_coverage_shortfall_tolerance": 0.02, "exact_cell_set": true, "expected_rows": 1920, "expected_unique_cells": 1920, "invalid_metric_row_count": 0, "minimum_observed_relative_reduction": 0.40302055578705925, "minimum_p2e_empirical_coverage": 0.9490322580645161, "minimum_substantial_relative_reduction": 0.1, "nominal_coverage": 0.95, "nonfinite_row_count": 0, "observed_unique_cells": 1920, "p2e_empirical_coverage_cell_count": 8, "p2e_empirical_coverage_pass_count": 8, "p2e_shorter_count": 24, "substantial_efficiency_gain_count": 24, "unexpected_row_count": 0}
$ python repro/src/verify_ccp_results.py --raw-dir outputs/raw/author_ccp --output outputs/claim3_independent.json
{"all_classical_efficiency_gains_substantial": true, "all_eccp_empirical_coverage_within_tolerance": true, "all_full_seed_cells_present": true, "all_p2e_empirical_coverage_within_tolerance": true, "all_p2e_not_longer_than_existing_calibrators": true, "all_p2e_strictly_shorter_than_aon": true, "aon_comparison_count": 9, "aon_strictly_shorter_count": 9, "calibrator_efficiency_comparison_count": 36, "classical_comparison_count": 27, "classical_substantial_gain_count": 27, "dataset_integrity": {"abalone": true, "boston": true, "parkinson": true}, "duplicate_cell_count": 0, "eccp_empirical_coverage_cell_count": 9, "eccp_empirical_coverage_pass_count": 9, "empirical_coverage_shortfall_tolerance": 0.02, "exact_cell_set": true, "expected_rows": 11700, "expected_unique_cells": 11700, "invalid_metric_row_count": 0, "minimum_classical_relative_reduction": 0.23664123574004337, "minimum_eccp_empirical_coverage": 0.8902991304347826, "minimum_observed_relative_reduction": 0.0017866878285227466, "minimum_p2e_empirical_coverage": 0.8902991304347826, "minimum_substantial_relative_reduction": 0.1, "nominal_coverage": 0.9, "nonfinite_row_count": 0, "observed_unique_cells": 11700, "p2e_empirical_coverage_cell_count": 27, "p2e_empirical_coverage_pass_count": 27, "p2e_not_longer_count": 36, "p2e_strictly_shorter_count": 36, "unexpected_row_count": 0}
$ python repro/src/verify_paper_table_fixture.py --output outputs/paper_table_fixture_audit.json
{"all_fields_match": true, "ca_cell_count": 32, "ccp_cell_count": 90, "mismatch_count": 0, "mismatch_paths": [], "parsed_values_sha256": "a412b883aebd9aa128293cf5308db45cd89ae69eb50b868a71551d7a05124b14", "scalar_count": 488, "total_cell_count": 122}
$ python repro/src/verify_ccp_calibrator_contract.py --source upstream --output outputs/ccp_calibrator_contract_audit.json
{"affected_paper_table_cells": 27, "affected_paper_table_scalars": 108, "all_numerical_witness_values_differ": true, "discrepant_method_count": 3, "paper_formula_contract_verified": true, "paper_source_column_mismatch_verified": true, "released_column_order_verified_for_all_models": true, "released_formula_contract_verified": true}
$ python repro/src/compare_paper_headlines.py --ca outputs/claim2_independent.json --ccp outputs/claim3_independent.json --output outputs/paper_headline_comparison.json
{"all_outside_tolerance_cells_accounted_for": true, "all_source_table_replays_within_tolerance": true, "all_unaffected_within_tolerance": true, "all_within_tolerance": false, "comparison_count": 122, "known_ca_dispersion_discrepancy_count": 1, "known_ca_dispersion_outside_tolerance_count": 1, "known_ca_dispersion_scalar_count": 4, "known_ca_dispersion_within_tolerance_scalar_count": 3, "known_discrepancy_comparison_count": 27, "known_discrepancy_outside_tolerance_count": 27, "known_discrepancy_scalar_comparison_count": 108, "scalar_comparison_count": 488, "source_table_replay_comparison_count": 18, "source_table_replay_scalar_comparison_count": 72, "source_table_replay_within_tolerance_count": 18, "source_table_replay_within_tolerance_scalar_count": 72, "unaffected_comparison_count": 94, "unaffected_scalar_comparison_count": 376, "unaffected_within_tolerance_count": 94, "unaffected_within_tolerance_scalar_count": 376, "unexpected_outside_tolerance_count": 0, "within_tolerance_count": 94, "within_tolerance_scalar_count": 433}
$ python -m unittest discover -s repro/tests -v
boston: completed seed 45
test_ca_dry_run_uses_released_full_protocol_and_portable_provenance (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ca_dry_run_uses_released_full_protocol_and_portable_provenance) ... ok
test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_input_preflight_loads_author_bundles_at_paper_fold_counts) ... ok
test_ccp_rng_replay_matches_real_source_power_intervals (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_rng_replay_matches_real_source_power_intervals) ... ok
test_ccp_seed_checkpoint_accepts_complete_cells_and_rejects_partial_cells (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_seed_checkpoint_accepts_complete_cells_and_rejects_partial_cells) ... ok
test_ccp_wrapper_reconstructs_the_paper_f3_linear_calibrator (test_author_runner_preflight.AuthorRunnerPreflightTests.test_ccp_wrapper_reconstructs_the_paper_f3_linear_calibrator) ... ok
test_vectorized_aggregation_matches_scalar_oracle_at_paper_fold_counts (test_author_runner_preflight.AuthorRunnerPreflightTests.test_vectorized_aggregation_matches_scalar_oracle_at_paper_fold_counts) ... ok
test_vectorized_ccp_adapter_matches_all_literal_source_model_paths (test_author_runner_preflight.AuthorRunnerPreflightTests.test_vectorized_ccp_adapter_matches_all_literal_source_model_paths) ... ok
test_exact_enumerations_pass_and_invalid_control_fails (test_e_merge_coverage.EMergeCoverageTests.test_exact_enumerations_pass_and_invalid_control_fails) ... ok
test_exchangeable_orbit_lp_matches_two_rank_closed_form (test_e_merge_coverage.EMergeCoverageTests.test_exchangeable_orbit_lp_matches_two_rank_closed_form) ... ok
test_lp_rejects_invalid_weight_vectors (test_e_merge_coverage.EMergeCoverageTests.test_lp_rejects_invalid_weight_vectors) ... ok
test_two_fold_lp_matches_independent_permutation_enumeration (test_e_merge_coverage.EMergeCoverageTests.test_two_fold_lp_matches_independent_permutation_enumeration) ... ok
test_alternative_ca_parser_rejects_dataset_and_method_drift (test_full_protocol.FullProtocolTests.test_alternative_ca_parser_rejects_dataset_and_method_drift) ... ok
test_anchored_claim_mechanism_controls_cover_new_scopes (test_full_protocol.FullProtocolTests.test_anchored_claim_mechanism_controls_cover_new_scopes) ... ok
test_ca_dispersion_disclosure_is_exact_and_cannot_mask_new_drift (test_full_protocol.FullProtocolTests.test_ca_dispersion_disclosure_is_exact_and_cannot_mask_new_drift) ... ok
test_ca_p2e_domain_audit_accounts_for_every_released_context (test_full_protocol.FullProtocolTests.test_ca_p2e_domain_audit_accounts_for_every_released_context) ... ok
test_exact_ca_protocol_contract (test_full_protocol.FullProtocolTests.test_exact_ca_protocol_contract) ... ok
test_expected_ccp_raw_cell_count (test_full_protocol.FullProtocolTests.test_expected_ccp_raw_cell_count) ... ok
test_final_logbook_renderer_fails_closed_and_emits_gate_marker (test_full_protocol.FullProtocolTests.test_final_logbook_renderer_fails_closed_and_emits_gate_marker) ... ok
test_live_jury_contract_rejects_count_and_wording_drift (test_full_protocol.FullProtocolTests.test_live_jury_contract_rejects_count_and_wording_drift) ... ok
test_official_jury_claim_snapshot_has_six_claims_and_twelve_points (test_full_protocol.FullProtocolTests.test_official_jury_claim_snapshot_has_six_claims_and_twelve_points) ... ok
test_openml_ca_inputs_are_content_pinned (test_full_protocol.FullProtocolTests.test_openml_ca_inputs_are_content_pinned) ... ok
test_paper_table_fixture_is_bound_to_primary_tex (test_full_protocol.FullProtocolTests.test_paper_table_fixture_is_bound_to_primary_tex) ... ok
test_protocol_matches_released_paper_scale (test_full_protocol.FullProtocolTests.test_protocol_matches_released_paper_scale) ... ok
test_publication_metadata_and_local_artifact_hygiene (test_full_protocol.FullProtocolTests.test_publication_metadata_and_local_artifact_hygiene) ... ok
test_released_source_and_dataset_manifest_is_exact (test_full_protocol.FullProtocolTests.test_released_source_and_dataset_manifest_is_exact) ... ok
test_shared_queue_handoff_follows_initial_github_push (test_full_protocol.FullProtocolTests.test_shared_queue_handoff_follows_initial_github_push) ... ok
test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json (test_full_protocol.FullProtocolTests.test_trackio_evidence_bundle_is_hash_indexed_and_roundtrips_json) ... ok
test_weca_independence_audit_is_bound_to_released_source (test_full_protocol.FullProtocolTests.test_weca_independence_audit_is_bound_to_released_source) ... ok
test_classic_calibrator_controls_expand_the_set (test_p2e_identity.P2EIdentityTests.test_classic_calibrator_controls_expand_the_set) ... ok
test_full_grid_summary_passes (test_p2e_identity.P2EIdentityTests.test_full_grid_summary_passes) ... ok
test_p2e_exactly_preserves_each_finite_rank_set (test_p2e_identity.P2EIdentityTests.test_p2e_exactly_preserves_each_finite_rank_set) ... ok
test_paper_theorem_domain_is_fail_closed (test_p2e_identity.P2EIdentityTests.test_paper_theorem_domain_is_fail_closed) ... ok
test_ca_verifier_requires_each_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ca_verifier_requires_each_method_seed_cell) ... ok
test_ccp_verifier_requires_each_model_method_seed_cell (test_raw_verifiers.RawVerifierTests.test_ccp_verifier_requires_each_model_method_seed_cell) ... ok
test_paper_headline_comparison_reports_matching_and_drifted_cells (test_raw_verifiers.RawVerifierTests.test_paper_headline_comparison_reports_matching_and_drifted_cells) ... ok

----------------------------------------------------------------------
Ran 35 tests in 10.024s

OK
{"artifact_paths": ["outputs/ca_p2e_domain_audit.json", "outputs/ca_input_audit.json", "outputs/source_manifest_audit.json", "outputs/claim1_independent.json", "outputs/claim1_source_crosscheck.json", "outputs/anchored_claims_mechanism.json", "outputs/claim2_independent.json", "outputs/claim3_independent_e_merge.json", "outputs/weca_independence_audit.json", "outputs/claim3_independent.json", "outputs/paper_table_fixture_audit.json", "outputs/ccp_calibrator_contract_audit.json", "outputs/paper_headline_comparison.json", "outputs/final_logbook_cells.json", "outputs/raw/author_ca/dataset_361237.json", "outputs/raw/author_ca/dataset_361235.json", "outputs/raw/author_ca/dataset_361244.json", "outputs/raw/author_ca/dataset_361234.json", "outputs/raw/author_ccp/boston.json", "outputs/raw/author_ccp/abalone.json", "outputs/raw/author_ccp/parkinson.json"], "artifact_sha256": {"outputs/anchored_claims_mechanism.json": "9b6c4163fd164be241123c12beea1a00c8f0c1a3565c01e0f4c7f95a2078994e", "outputs/ca_input_audit.json": "ccdfff3c7c7723c7d4707f1825cd098cef933628fe64e32c12947435816ab1e7", "outputs/ca_p2e_domain_audit.json": "bd2784e4d4ef04a14f723ffde8dbaa86f678930d808d5dafb7bc03090f71b41b", "outputs/ccp_calibrator_contract_audit.json": "fde3e9dbf47eac2275237db7ceb314b588df132a448fc5d4d10e2196804f7a14", "outputs/claim1_independent.json": "f9c17dd53546ab5d78387f8f91e8d44fe45cf16886554cb3d810a476ff80e0bb", "outputs/claim1_source_crosscheck.json": "e86dc02f33bd1b27d0ded95b3b74186b6b014273eb5651b13aa385e0df11cd04", "outputs/claim2_independent.json": "7eaf8410f54c57ac4c82972c6a8d3cb97f701cc39ecd1c74c14a6273c52a9d03", "outputs/claim3_independent.json": "97a5aa171de3f9767fe5d3478621b317db88dc70e5409a5dce94baf76e6a6533", "outputs/claim3_independent_e_merge.json": "deea168006396145de5361fe2cb96788e97f093826691e125e27f5dab02a3efe", "outputs/final_logbook_cells.json": "0c5d25948d4eddfc514deda8d11e55433cfea11bca4860a320fa83da07f225dc", "outputs/paper_headline_comparison.json": "b57db17c209f6da34ffbc110ea86abe9f75e1996086096bb2f93b511393085c8", "outputs/paper_table_fixture_audit.json": "b2ccba2f76b937a9e086ced4cdbbd610cf1225c4a598164424d30673bf5fe85c", "outputs/raw/author_ca/dataset_361234.json": "149ae7b7ae2c93d94f2a2d29b1eb75403a3283b70cc026f7236504176cc71441", "outputs/raw/author_ca/dataset_361235.json": "9d758888f6b6b3788204e6859be122ebfee1f00ff7b48eebce3314b7e43cff7b", "outputs/raw/author_ca/dataset_361237.json": "668325f55a76b669b3ecf142d4dd1aaa527ad74a0e6ea83f85b4930a84973981", "outputs/raw/author_ca/dataset_361244.json": "d566945c9fafba712708c7f3c13a96781f53e9d3148fddc94d8cc9c054cca188", "outputs/raw/author_ccp/abalone.json": "fac6af8455aab8aa28e0f3bfd6feb0f033db3636902fa0a09e9a0a44331f0e05", "outputs/raw/author_ccp/boston.json": "31b8a6c5c81b468e50d23b6d55b91e3b6f5da91f4f8a3c413a1e657b7d2ca4b0", "outputs/raw/author_ccp/parkinson.json": "d128fa66a8e2c4bd1f40cae95b3bfc07ef27daf3449064a220ef79b72898a108", "outputs/source_manifest_audit.json": "ef34215e7c921fd5204287452fc7b365d7e9d6a9422f695f1a3e01ce60c4e461", "outputs/weca_independence_audit.json": "77546ac8887504af6891cb9892f8f8728782fce17bd2d653bedc2fd0504ed4d9"}, "claims": 6, "claims_source_url": "https://huggingface.co/spaces/ICML-2026-agent-repro/challenge/resolve/main/claims_anchored.json", "claims_source_urls": {"anchored": "https://huggingface.co/spaces/ICML-2026-agent-repro/challenge/resolve/main/claims_anchored.json", "fallback": "https://huggingface.co/spaces/ICML-2026-agent-repro/challenge/resolve/main/claims.json"}, "command_count": 14, "hygiene": {"absolute_path_hits": [], "env_files": [], "local_path_artifact_count": 0, "secret_hits": [], "text_files_scanned": 97}, "live_claims_verified": 6, "maximum_points": 12, "paper": "jNv4sl4YZH", "publication_gate_passed": true, "source_commit": "66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974", "tests_passed": true, "trackio_artifact_bundle": "outputs/jNv4sl4YZH_full_evidence_bundle.jsonl", "trackio_artifact_bundle_sha256": "1cd1115ee4fefc260c79512eb1a4bea61f342ebca5bb9acf3cc5b8ca91f90359"}

````


---
<!-- trackio-cell
{"type": "artifact", "id": "cell_806f451780be", "created_at": "2026-07-19T19:03:20+00:00", "title": "Artifact: jNv4sl4YZH_full_evidence_bundle.jsonl", "path": "outputs/jNv4sl4YZH_full_evidence_bundle.jsonl", "size": 2781144, "artifact_type": "dataset", "auto": true}
-->
**📦 Artifact** `outputs/jNv4sl4YZH_full_evidence_bundle.jsonl` · dataset · 2.8 MB

https://huggingface.co/buckets/DineshAI/jNv4sl4YZH-artifacts#logbook-files/outputs/jNv4sl4YZH_full_evidence_bundle.jsonl
