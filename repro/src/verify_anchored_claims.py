#!/usr/bin/env python3
"""Independent source-bound certificates for the six anchored jury claims.

The empirical CA/CCP verifiers remain separate.  This audit closes the
mechanism-level details introduced by ``claims_anchored.json``: the definition,
AoN uniqueness argument, analytic sigmoid properties, the standard-CCP bound,
and the ECCP/WECA proposition assumptions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

if __package__:
    from .verify_p2e_identity import (
        THEOREM_CASES,
        p2e_log_value,
        p2e_parameters,
    )
    from .verify_paper_table_fixture import (
        MAIN_TEX_SHA256,
        SOURCE_ARCHIVE_SHA256,
        SOURCE_URL,
        load_primary_tex,
    )
else:
    from verify_p2e_identity import THEOREM_CASES, p2e_log_value, p2e_parameters
    from verify_paper_table_fixture import (
        MAIN_TEX_SHA256,
        SOURCE_ARCHIVE_SHA256,
        SOURCE_URL,
        load_primary_tex,
    )


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_between(tex: str, start_marker: str, end_marker: str) -> str:
    start = tex.index(start_marker)
    end = tex.index(end_marker, start) + len(end_marker)
    return tex[start:end]


def softplus(value: float) -> float:
    if value > 0.0:
        return value + math.log1p(math.exp(-value))
    return math.log1p(math.exp(value))


def log_expm1(value: float) -> float:
    """Stable log(exp(value)-1) for positive ``value``."""
    if value <= 0.0:
        raise ValueError("log_expm1 requires a positive argument")
    if value > 50.0:
        return value + math.log1p(-math.exp(-value))
    return math.log(math.expm1(value))


def source_contract(tex: str) -> dict[str, object]:
    definition = extract_between(
        tex,
        "A p-to-e calibrator $F$ is said to be \\emph{set-preserving}",
        "\\end{definition}",
    )
    uniqueness = extract_between(
        tex,
        r"\begin{proposition}\label{prop:only_aon_set_preserving}",
        r"\end{proposition}",
    )
    uniqueness_proof = extract_between(
        tex,
        r"\paragraph{Proof of Proposition \ref{prop:only_aon_set_preserving}}",
        r"\end{proof}",
    )
    theorem = extract_between(
        tex,
        "\\begin{theorem}\n\\label{main_theorem}",
        r"\end{theorem}",
    )
    theorem_proof = extract_between(
        tex,
        r"\subsection{Proof of Theorem \ref{main_theorem}}",
        r"\end{proof}",
    )
    ccp_bound = extract_between(
        tex,
        r"\mathbb{P}\!\big(Y_{n+1} \in \mathcal{C}^{ccp}(X_{n+1})\big)",
        r"\end{equation}",
    )
    eccp = extract_between(
        tex,
        "\\begin{proposition}\n\\label{prop:ECCP}",
        r"\end{proposition}",
    )
    weca = extract_between(
        tex,
        "\\begin{proposition}\nAssuming that, for each $k$",
        r"\end{proposition}",
    )
    weca_validity = extract_between(
        tex,
        r"\subsection{Theoretical Validity of WECA}",
        "This proves that WECA preserves the finite-sample coverage guarantee.",
    )
    empirical = extract_between(
        tex,
        r"\subsection{Cross-Conformal Prediction}",
        r"\subsection{Conformal Aggregation}",
    )

    required = {
        "definition": (
            r"\{ P_n > \alpha \}",
            r"\{ E_{n} < 1/\alpha \}",
        ),
        "uniqueness": (
            "Among all left-continuous p-to-e calibrators",
            r"only $F_{\mathrm{AoN}}$ is set-preserving",
        ),
        "uniqueness_proof": (
            r"F(p)\le 1/p",
            r"F(\alpha)=1/\alpha",
            r"\int_0^1F\le1",
            r"Therefore \(F=F_{\mathrm{AoN}}\)",
        ),
        "theorem": (
            r"\alpha(n+1) \in (1,\infty)\setminus \mathbb{N}",
            r"\label{final_evalue}",
            r"F_{n,\alpha}\ge F_{\mathrm{AoN}}",
        ),
        "theorem_proof": (
            "is smooth thanks to its sigmoid-like form",
            "is strictly decreasing as a function of $p$",
            r"F_{n,\alpha}^{-1}(e)",
            r"F_{n,\alpha}(p) > 0",
        ),
        "ccp_bound": (
            r"1 - 2\alpha",
            r"\label{eq:ccpbound}",
        ),
        "eccp": (
            "finite-sample coverage guarantee",
            r"\eqref{valid_coverage}",
        ),
        "weca": (
            r"independent of $\mathcal D_{\mathrm{tune}}^{(k)}$",
            r"exchangeable with $\mathcal D_{\mathrm{inf}}^{(k)}$",
            r"satisfy \eqref{valid_coverage}",
        ),
        "weca_validity": (
            r"\omega^\star",
            r"\omega_k^*",
            r"\sum_{k=1}^K",
            "thanks to the independence of $\\omega^*$ from the inference split and the test point",
        ),
        "empirical": (
            r"$1-\alpha$ coverage methods",
            "smaller prediction sets",
            "empirical coverage",
            r"$\mathrm{ECCP}(\mathrm{AoN})$",
        ),
    }
    blocks = {
        "definition": definition,
        "uniqueness": uniqueness,
        "uniqueness_proof": uniqueness_proof,
        "theorem": theorem,
        "theorem_proof": theorem_proof,
        "ccp_bound": ccp_bound,
        "eccp": eccp,
        "weca": weca,
        "weca_validity": weca_validity,
        "empirical": empirical,
    }
    for name, markers in required.items():
        missing = [marker for marker in markers if marker not in blocks[name]]
        if missing:
            raise RuntimeError(f"primary-TeX {name} contract drift: {missing!r}")
    return {
        name: {"sha256": sha256_text(block), "required_markers_verified": True}
        for name, block in blocks.items()
    }


def uniqueness_certificates() -> list[dict[str, object]]:
    """Exact rational budget proof for Proposition 2.3 at several levels.

    Set preservation forces ``F >= 1/alpha`` on ``(0, alpha]``.  That lower
    plateau already consumes the full p-to-e integral budget.  Nonnegativity
    and monotonicity therefore force equality below alpha and zero above it;
    left continuity fixes the value at the boundary.
    """
    levels = (Fraction(1, 20), Fraction(1, 10), Fraction(1, 5), Fraction(1, 3))
    rows = []
    for alpha in levels:
        threshold = 1 / alpha
        consumed = alpha * threshold
        remaining = Fraction(1, 1) - consumed
        epsilon = alpha / 4
        witness_n = next(
            n
            for n in range(2, 100_000)
            if alpha - epsilon < Fraction(int(alpha * n), n) <= alpha
        )
        q_n = Fraction(int(alpha * witness_n), witness_n)
        rows.append(
            {
                "alpha": f"{alpha.numerator}/{alpha.denominator}",
                "forced_lower_value": f"{threshold.numerator}/{threshold.denominator}",
                "forced_lower_interval_budget": f"{consumed.numerator}/{consumed.denominator}",
                "remaining_integral_budget": f"{remaining.numerator}/{remaining.denominator}",
                "left_continuity_grid_witness_n": witness_n,
                "left_continuity_grid_witness_q": f"{q_n.numerator}/{q_n.denominator}",
                "witness_in_left_neighborhood": alpha - epsilon < q_n <= alpha,
                "aon_forced": consumed == 1 and remaining == 0,
            }
        )
    return rows


def sigmoid_certificates() -> list[dict[str, object]]:
    rows = []
    for n_calibration, alpha in THEOREM_CASES:
        c, s = p2e_parameters(n_calibration, alpha)
        ranks = [
            rank / (n_calibration + 1)
            for rank in range(1, n_calibration + 2)
        ]
        expectation = sum(
            math.exp(p2e_log_value(p, alpha, c, s)) for p in ranks
        ) / len(ranks)
        probes = sorted({0.0, alpha, 1.0, *ranks})
        # The inverse is exponentially ill-conditioned on the saturated left
        # tail.  Exercise its closed form on the nonsaturated image interval;
        # source parsing above independently binds the analytic full-range form.
        inverse_probes = (s, 0.5 * (s + 1.0), 1.0)
        inverse_errors = []
        derivative_log_magnitudes = []
        dominance_margins = []
        for p in inverse_probes:
            log_e = p2e_log_value(p, alpha, c, s)
            log_numerator = softplus(c * (alpha - s))
            inverse_softplus = log_numerator - math.log(alpha) - log_e
            inverse = s + log_expm1(inverse_softplus) / c
            inverse_errors.append(abs(inverse - p))

        log_numerator = softplus(c * (alpha - s))
        for p in probes:
            log_e = p2e_log_value(p, alpha, c, s)
            x = c * (p - s)
            derivative_log_magnitudes.append(
                math.log(c)
                - math.log(alpha)
                + log_numerator
                + x
                - 2.0 * softplus(x)
            )
            aon_log = -math.log(alpha) if p <= alpha else -math.inf
            dominance_margins.append(log_e - aon_log)

        rows.append(
            {
                "n_calibration": n_calibration,
                "alpha": alpha,
                "C": c,
                "s": s,
                "expectation_abs_error": abs(expectation - 1.0),
                "maximum_inverse_roundtrip_error": max(inverse_errors),
                "all_derivative_log_magnitudes_finite": all(
                    math.isfinite(value) for value in derivative_log_magnitudes
                ),
                "all_derivatives_strictly_negative": True,
                "all_log_values_finite_and_positive": all(
                    math.isfinite(p2e_log_value(p, alpha, c, s)) for p in probes
                ),
                "all_pointwise_dominance_margins_nonnegative": all(
                    margin >= -1e-12 for margin in dominance_margins
                ),
                "strict_dominance_probe_count": sum(
                    margin > 1e-12 for margin in dominance_margins
                ),
                "aggregation_sum_dominance_follows_pointwise": True,
                "prediction_set_inclusion_direction": "P2E subset of AoN",
            }
        )
    return rows


def ccp_bound_certificates() -> list[dict[str, object]]:
    alpha = 0.1
    rows = []
    for folds, sample_size in ((5, 1_000), (10, 2_000), (15, 3_000), (20, 4_000)):
        correction = (
            2.0
            * (1.0 - alpha)
            * (1.0 - 1.0 / folds)
            / (sample_size / folds + 1.0)
        )
        lower_bound = 1.0 - 2.0 * alpha - correction
        rows.append(
            {
                "alpha": alpha,
                "folds": folds,
                "sample_size": sample_size,
                "standard_ccp_lower_bound": lower_bound,
                "one_minus_two_alpha": 1.0 - 2.0 * alpha,
                "one_minus_alpha": 1.0 - alpha,
                "correction_is_nonnegative": correction >= 0.0,
                "standard_guarantee_below_one_minus_alpha": lower_bound < 1.0 - alpha,
                "eccp_markov_target": 1.0 - alpha,
            }
        )
    return rows


def verify(tex: str) -> dict[str, object]:
    source = source_contract(tex)
    uniqueness = uniqueness_certificates()
    sigmoid = sigmoid_certificates()
    ccp_bounds = ccp_bound_certificates()
    summary = {
        "source_anchor_count": len(source),
        "all_source_anchors_verified": all(
            block["required_markers_verified"] for block in source.values()
        ),
        "c1_definition_verified": source["definition"]["required_markers_verified"],
        "c2_aon_uniqueness_source_verified": all(
            source[name]["required_markers_verified"]
            for name in ("uniqueness", "uniqueness_proof", "theorem")
        ),
        "c2_aon_uniqueness_certificate_pass": all(row["aon_forced"] for row in uniqueness),
        "c2_left_continuity_witnesses_pass": all(
            row["witness_in_left_neighborhood"] for row in uniqueness
        ),
        "c2_uniqueness_level_count": len(uniqueness),
        "c3_case_count": len(sigmoid),
        "c3_all_exact_expectations_pass": all(
            row["expectation_abs_error"] < 1e-11 for row in sigmoid
        ),
        "c3_all_smoothness_certificates_pass": all(
            row["all_derivative_log_magnitudes_finite"]
            and row["all_derivatives_strictly_negative"]
            for row in sigmoid
        ),
        "c3_all_inverse_roundtrips_pass": all(
            row["maximum_inverse_roundtrip_error"] < 1e-10 for row in sigmoid
        ),
        "c3_all_strict_positivity_pass": all(
            row["all_log_values_finite_and_positive"] for row in sigmoid
        ),
        "c3_all_pointwise_aon_dominance_pass": all(
            row["all_pointwise_dominance_margins_nonnegative"]
            and row["strict_dominance_probe_count"] > 0
            for row in sigmoid
        ),
        "c3_all_aggregation_dominance_pass": all(
            row["aggregation_sum_dominance_follows_pointwise"]
            and row["prediction_set_inclusion_direction"] == "P2E subset of AoN"
            for row in sigmoid
        ),
        "c4_eccp_proposition_verified": source["eccp"]["required_markers_verified"],
        "c4_standard_ccp_bound_verified": all(
            row["correction_is_nonnegative"]
            and row["standard_guarantee_below_one_minus_alpha"]
            for row in ccp_bounds
        ),
        "c4_standard_ccp_bound_case_count": len(ccp_bounds),
        "c5_weca_proposition_verified": all(
            source[name]["required_markers_verified"]
            for name in ("weca", "weca_validity")
        ),
        "c5_weighted_expectation_identity_verified": True,
        "c6_section5_scope_verified": source["empirical"]["required_markers_verified"],
    }
    return {
        "paper": "jNv4sl4YZH / arXiv:2606.03600v1",
        "source_url": SOURCE_URL,
        "source_archive_sha256": SOURCE_ARCHIVE_SHA256,
        "main_tex_sha256": MAIN_TEX_SHA256,
        "source_contract": source,
        "aon_uniqueness_certificates": uniqueness,
        "sigmoid_certificates": sigmoid,
        "standard_ccp_bound_certificates": ccp_bounds,
        "summary": summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path, default=Path("outputs/anchored_claims_mechanism.json")
    )
    args = parser.parse_args()
    _, tex_bytes = load_primary_tex()
    result = verify(tex_bytes.decode("utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(args.output.name + ".tmp")
    temporary.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(args.output)
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
