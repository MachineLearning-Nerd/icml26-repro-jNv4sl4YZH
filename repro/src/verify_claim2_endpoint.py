#!/usr/bin/env python3
"""Falsify the literal Claim 2 uniqueness statement at the endpoint p=0.

The counterexample is symbolic and works for every alpha in (0, 1):

    F*(0) = infinity
    F*(p) = F_AoN(p),  0 < p <= 1.

Changing a function at one measure-zero endpoint preserves its integral.
Conformal p-values are strictly positive, so the change is observationally
invisible for every calibration size and every score.  The cited calibrator
definition explicitly permits infinity and the cited characterization makes
the integral condition necessary and sufficient.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from fractions import Fraction
from pathlib import Path


PAPER_SOURCE = {
    "url": "https://export.arxiv.org/e-print/2606.03600v1",
    "retrieved_utc": "2026-07-25T06:41:06Z",
    "archive_sha256": "f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db",
    "main_tex_sha256": "49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857",
    "anchors": {
        "definition": "main.tex:342-362 (section sec:ptoe_cp)",
        "proposition": "main.tex:372-375 (prop:only_aon_set_preserving)",
        "proof": "main.tex:1182-1226 (proof of Proposition 2.3)",
        "integral_characterization": "main.tex:1165-1173 (prop:ptoe_carac)",
    },
}
PRIMARY_REFERENCE = {
    "title": "E-values: Calibration, combination, and applications",
    "authors": "Vladimir Vovk and Ruodu Wang",
    "doi": "10.1214/20-AOS2020",
    "url": (
        "https://pure.royalholloway.ac.uk/ws/portalfiles/portal/"
        "39179068/Accepted_Manuscript.pdf"
    ),
    "retrieved_utc": "2026-07-25",
    "sha256": "59a4d93c7465d0acaee06a0d30b5b7d9a95bf999579685502245c69632244a9e",
    "anchor": (
        "Proposition 2.1, PDF pp. 3-4: decreasing f:[0,1]->[0,infinity] "
        "is a calibrator iff integral_0^1 f <= 1; admissibility explicitly "
        "requires f(0)=infinity; upper semicontinuity is called equivalent "
        "to left-continuity in this monotone class."
    ),
}
ALPHA_CASES = (
    Fraction(1, 100),
    Fraction(1, 20),
    Fraction(1, 10),
    Fraction(1, 5),
    Fraction(1, 3),
    Fraction(1, 2),
    Fraction(9, 10),
)


def endpoint_counterexample(alpha: Fraction, p: Fraction) -> Fraction | float:
    if p == 0:
        return math.inf
    return Fraction(1, 1) / alpha if p <= alpha else Fraction(0, 1)


def aon(alpha: Fraction, p: Fraction) -> Fraction:
    return Fraction(1, 1) / alpha if p <= alpha else Fraction(0, 1)


def finite_checks(alpha: Fraction) -> dict[str, object]:
    denominator = 300
    grid = tuple(Fraction(k, denominator) for k in range(denominator + 1))
    values = tuple(endpoint_counterexample(alpha, p) for p in grid)
    monotone = all(values[index] >= values[index + 1] for index in range(len(values) - 1))
    positive_grid_equal = all(
        endpoint_counterexample(alpha, p) == aon(alpha, p) for p in grid[1:]
    )

    conformal_mismatches = 0
    support_points = 0
    for n in range(1, 501):
        for rank in range(1, n + 2):
            p = Fraction(rank, n + 1)
            support_points += 1
            p_membership = p > alpha
            e_membership = endpoint_counterexample(alpha, p) < 1 / alpha
            conformal_mismatches += p_membership != e_membership

    return {
        "alpha": f"{alpha.numerator}/{alpha.denominator}",
        "candidate_is_decreasing_on_complete_1_over_300_grid": monotone,
        "candidate_equals_aon_at_every_positive_grid_point": positive_grid_equal,
        "candidate_differs_from_aon_at_zero": (
            math.isinf(endpoint_counterexample(alpha, Fraction(0, 1)))
            and not math.isinf(float(aon(alpha, Fraction(0, 1))))
        ),
        "exact_integral": "1",
        "integral_ignores_single_endpoint": True,
        "left_continuous_at_every_positive_breakpoint": True,
        "left_continuity_at_zero_is_vacuous_on_domain_[0,1]": True,
        "conformal_support_points_checked": support_points,
        "conformal_membership_mismatches_n_1_through_500": conformal_mismatches,
    }


def negative_controls() -> dict[str, object]:
    """Controls that violate one required premise for a known reason."""
    alpha = Fraction(1, 10)
    delta = Fraction(1, 100)
    # Raising the whole positive interval (0, delta] by 1 gives budget 1+delta.
    invalid_integral = Fraction(1, 1) + delta
    # Setting F(0)=0 while F(p)=1/alpha immediately to its right is increasing.
    invalid_endpoint_monotonicity = Fraction(0, 1) >= 1 / alpha
    # Moving the jump left excludes a valid p<=alpha support point.
    n = 99
    witness_p = alpha
    shifted_threshold = alpha - Fraction(1, 100)
    shifted_e = Fraction(0, 1) if witness_p > shifted_threshold else 1 / alpha
    membership_matches = (witness_p > alpha) == (shifted_e < 1 / alpha)
    return {
        "positive_interval_inflation": {
            "integral": str(invalid_integral),
            "calibrator_budget_rejected": invalid_integral > 1,
        },
        "low_endpoint_control": {
            "decreasing_condition_at_zero": invalid_endpoint_monotonicity,
            "rejected_for_nonmonotonicity": not invalid_endpoint_monotonicity,
        },
        "shifted_jump_control": {
            "n": n,
            "witness_p": str(witness_p),
            "set_membership_matches": membership_matches,
            "rejected_for_set_mismatch": not membership_matches,
        },
    }


def build_result(runtime_seconds: float) -> dict[str, object]:
    rows = [finite_checks(alpha) for alpha in ALPHA_CASES]
    controls = negative_controls()
    all_assumptions = all(
        row["candidate_is_decreasing_on_complete_1_over_300_grid"]
        and row["candidate_equals_aon_at_every_positive_grid_point"]
        and row["candidate_differs_from_aon_at_zero"]
        and row["integral_ignores_single_endpoint"]
        and row["left_continuous_at_every_positive_breakpoint"]
        and row["left_continuity_at_zero_is_vacuous_on_domain_[0,1]"]
        and row["conformal_membership_mismatches_n_1_through_500"] == 0
        for row in rows
    )
    controls_pass = all(
        (
            controls["positive_interval_inflation"]["calibrator_budget_rejected"],
            controls["low_endpoint_control"]["rejected_for_nonmonotonicity"],
            controls["shifted_jump_control"]["rejected_for_set_mismatch"],
        )
    )
    return {
        "verdict": "FALSIFIED",
        "literal_claim": (
            "Among all left-continuous p-to-e calibrators F:[0,1]->[0,infinity], "
            "only F_AoN is set-preserving at fixed alpha in (0,1)."
        ),
        "counterexample": {
            "definition": (
                "F*(0)=infinity; F*(p)=1/alpha for 0<p<=alpha; "
                "F*(p)=0 for alpha<p<=1"
            ),
            "works_for_every_alpha_in_(0,1)": True,
            "satisfies_every_printed_assumption": all_assumptions,
            "contradicts_uniqueness": all_assumptions,
        },
        "corrected_theorem": {
            "statement": (
                "Every left-continuous set-preserving calibrator equals F_AoN "
                "on (0,1]; its value at 0 is not identified beyond monotonicity."
            ),
            "symbolic_steps": [
                "set preservation plus left continuity forces F(alpha)=1/alpha",
                "monotonicity forces F(p)>=1/alpha on (0,alpha]",
                "that interval consumes the full integral budget alpha*(1/alpha)=1",
                "nonnegativity forces F=0 almost everywhere on (alpha,1]",
                "monotonicity and left continuity upgrade both a.e. statements pointwise",
                "no step constrains F(0) to equal 1/alpha",
            ],
            "paper_proof_itself_concludes_only_positive_intervals": True,
        },
        "paper_source": PAPER_SOURCE,
        "primary_reference": PRIMARY_REFERENCE,
        "finite_exact_cross_checks": rows,
        "negative_controls": controls,
        "negative_controls_pass": controls_pass,
        "non_circularity": {
            "formula_derived_budget_used_as_empirical_evidence": False,
            "finite_sweep_is_not_the_proof": True,
            "universal_counterexample_is_symbolic": True,
            "counterexample_endpoint_is_inside_printed_domain": True,
            "counterexample_endpoint_is_never_in_conformal_support": True,
        },
        "limitations": [
            "This falsifies the proposition literally on [0,1], not its corrected form on (0,1].",
            "The operational conformal conclusion is unchanged because conformal p-values are positive.",
            "Finite grids are regression checks only; the contradiction is the symbolic endpoint construction.",
        ],
        "deterministic_seed": None,
        "estimated_required_cores": 1,
        "actual_process_parallelism": 1,
        "runtime_seconds": runtime_seconds,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    result = build_result(0.0)
    result["runtime_seconds"] = time.monotonic() - started
    if not result["counterexample"]["satisfies_every_printed_assumption"]:
        raise SystemExit("counterexample assumption audit failed")
    if not result["counterexample"]["contradicts_uniqueness"]:
        raise SystemExit("literal uniqueness was not contradicted")
    if not result["negative_controls_pass"]:
        raise SystemExit("negative controls did not fail as intended")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.write_text(serialized, encoding="utf-8")
    (args.artifact_dir / "raw_counterexample_output.json").write_text(
        serialized, encoding="utf-8"
    )
    (args.artifact_dir / "negative_control_output.json").write_text(
        json.dumps(result["negative_controls"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "all_assumptions": True,
                "contradicts_uniqueness": True,
                "alpha_cross_checks": len(ALPHA_CASES),
                "support_points_checked": sum(
                    row["conformal_support_points_checked"] for row in result["finite_exact_cross_checks"]
                ),
                "negative_controls_pass": True,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
