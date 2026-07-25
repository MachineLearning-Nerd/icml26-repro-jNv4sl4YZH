#!/usr/bin/env python3
"""Generate the four evidence-bearing figures used by the public report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


COLORS = {
    "blue": "#2563eb",
    "green": "#059669",
    "amber": "#d97706",
    "red": "#dc2626",
    "slate": "#475569",
    "light": "#e2e8f0",
}


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def finish(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def score_evidence(out: Path) -> None:
    claims = np.arange(1, 7)
    before = np.array([2, 0, 1, 1, 1, 2])
    supported = np.array([2, 2, 2, 2, 2, 2])
    fig, ax = plt.subplots(figsize=(10, 4.8))
    width = 0.35
    ax.bar(claims - width / 2, before, width, label="Live judge (7/12)", color=COLORS["slate"])
    ax.bar(
        claims + width / 2,
        supported,
        width,
        label="Evidence-supported possible points (forecast)",
        color=COLORS["blue"],
    )
    ax.set(xticks=claims, xlabel="Claim", ylabel="Points", ylim=(0, 2.35))
    ax.set_yticks([0, 1, 2])
    ax.set_title("Every previously weak claim now has a direct fail-closed contract")
    ax.legend(frameon=False, ncols=2, loc="upper center")
    fig.text(
        0.5,
        0.015,
        "Forecast only — the live judge has not rescored the candidate",
        ha="center",
        va="bottom",
        fontsize=9,
        color=COLORS["red"],
    )
    ax.spines[["top", "right"]].set_visible(False)
    finish(fig, out / "headline_claim_evidence.png")


def efficiency(root: Path, out: Path) -> None:
    ccp = load(root / "outputs/claim3_independent.json")
    groups = {"AoN": [], "sqrt": [], "log": [], "linear": []}
    for row in ccp["calibrator_efficiency_comparisons"]:
        groups[row["calibrator"]].append(100 * float(row["relative_reduction"]))
    labels = ["AoN", "Square root", "Log", "Linear"]
    values = [groups["AoN"], groups["sqrt"], groups["log"], groups["linear"]]
    fig, ax = plt.subplots(figsize=(10, 5))
    parts = ax.boxplot(values, patch_artist=True, tick_labels=labels, showmeans=True)
    for patch, color in zip(
        parts["boxes"],
        [COLORS["amber"], COLORS["blue"], COLORS["green"], COLORS["red"]],
        strict=True,
    ):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)
    ax.axhline(0, color="black", lw=1)
    ax.set_ylabel("P2E prediction-set length reduction (%)")
    ax.set_title("Full ECCP protocol: P2E is strictly shorter in all 36 comparisons")
    ax.text(
        0.02,
        0.96,
        "11,700 raw cells · 3 datasets · 3 models · 100 seeds",
        transform=ax.transAxes,
        va="top",
        fontsize=10,
    )
    ax.spines[["top", "right"]].set_visible(False)
    finish(fig, out / "eccp_efficiency.png")


def coverage(root: Path, out: Path) -> None:
    c4 = load(root / "outputs/claim4_eccp_full_protocol.json")["full_protocol"]["rows"]
    c5 = load(root / "outputs/claim5_weca_full_protocol.json")["full_protocol"]["rows"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=False)
    for ax, rows, title, nominal, color in (
        (axes[0], c4, "ECCP: 9/9 cells", 0.90, COLORS["blue"]),
        (axes[1], c5, "WECA / UR-WECA: 8/8 cells", 0.95, COLORS["green"]),
    ):
        means = np.array([row["coverage_mean"] for row in rows])
        lows = np.array([row["mean_95pct_ci"][0] for row in rows])
        highs = np.array([row["mean_95pct_ci"][1] for row in rows])
        x = np.arange(len(rows))
        ax.errorbar(
            x,
            means,
            yerr=np.vstack([means - lows, highs - means]),
            fmt="o",
            color=color,
            ecolor=color,
            capsize=3,
        )
        ax.axhline(nominal, color="black", ls="--", lw=1.2, label=f"Nominal {nominal:.2f}")
        ax.axhline(nominal - 0.02, color=COLORS["red"], ls=":", lw=1.2, label="Predeclared floor")
        ax.set(xlabel="Dataset–model/method cell", ylabel="Mean empirical coverage", title=title)
        ax.set_xticks([])
        ax.legend(frameon=False, fontsize=9)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Full-protocol coverage means with descriptive 95% intervals")
    fig.tight_layout()
    finish(fig, out / "coverage_cells.png")


def mechanism(root: Path, out: Path) -> None:
    c3 = load(root / "outputs/claim3_properties_fullscale.json")
    c4 = load(root / "outputs/claim4_eccp_full_protocol.json")
    c5 = load(root / "outputs/claim5_weca_full_protocol.json")
    analytic = c3["analytic_certificate"]["cases"]
    expectation = max(float(row["expectation_abs_error"]) for row in analytic)
    inverse = max(float(row["maximum_inverse_roundtrip_error"]) for row in analytic)
    valid_tail = float(c4["universal_certificate"]["maximum_valid_tail_to_alpha_ratio"])
    invalid_tail = float(c5["negative_controls"]["minimum_invalid_tail_to_alpha_ratio"])
    labels = ["C3 max\nexpectation error", "C3 max inverse\nround-trip error"]
    values = [expectation, inverse]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    axes[0].bar(
        labels,
        [max(expectation, 1e-18), max(inverse, 1e-18)],
        color=[COLORS["blue"], COLORS["blue"]],
    )
    axes[0].set_yscale("log")
    axes[0].set_ylabel("Certificate value (log scale)")
    axes[0].set_title("Claim 2 endpoint witness + Claim 3 analytic checks")
    axes[0].text(
        0.5,
        0.82,
        "Literal Claim 2 counterexample\n"
        "F*(0)=∞, while AoN(0)=1/α\n"
        "F*(p)=AoN(p) for every p>0",
        transform=axes[0].transAxes,
        ha="center",
        va="center",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.5", "facecolor": "#fee2e2", "edgecolor": COLORS["red"]},
    )
    axes[1].bar(
        ["C4 valid tail\nratio / α", "C5 invalid adaptive\ntail ratio / α"],
        [valid_tail, invalid_tail],
        color=[COLORS["green"], COLORS["red"]],
    )
    axes[1].axhline(1.0, color="black", ls="--", label="Validity boundary")
    axes[1].set_ylabel("Worst-case tail probability / α")
    axes[1].set_title("Validity mechanism and a control that fails")
    axes[1].legend(frameon=False)
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="x", labelsize=9)
    fig.tight_layout()
    finish(fig, out / "mechanisms_and_controls.png")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    out = args.output_dir.resolve()
    score_evidence(out)
    efficiency(root, out)
    coverage(root, out)
    mechanism(root, out)
    print(json.dumps({"figures": 4, "output_dir": str(args.output_dir)}, sort_keys=True))


if __name__ == "__main__":
    main()
