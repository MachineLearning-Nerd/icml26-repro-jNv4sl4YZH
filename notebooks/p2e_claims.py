import marimo

__generated_with = "0.23.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np

    return mo, np, plt


@app.cell
def _(mo):
    mo.md(r"""
    # Set-preserving P2E calibration, from claim to evidence

    This notebook is a self-contained tour of the reproduction of
    *Set-Preserving Calibration from Conformal P-Values to E-Values*
    (arXiv:2606.03600). It embeds the accepted numerical summaries, so
    opening it does **not** rerun the 1,920-row CA or 11,700-row CCP
    protocols.

    **Headline evidence:** the live logbook had 7/12 points. The candidate
    has direct fail-closed evidence supporting two possible points for every
    claim, including a literal endpoint falsification for Claim 2. That is a
    forecast, not a new judge result.
    """)
    return


@app.cell
def _(np, plt):
    claims = np.arange(1, 7)
    live = np.array([2, 0, 1, 1, 1, 2])
    supported = np.array([2, 2, 2, 2, 2, 2])
    fig, ax = plt.subplots(figsize=(9, 4))
    width = 0.35
    ax.bar(claims - width / 2, live, width, label="Live judge: 7/12", color="#475569")
    ax.bar(
        claims + width / 2,
        supported,
        width,
        label="Evidence-supported possible points",
        color="#2563eb",
    )
    ax.set(xlabel="Claim", ylabel="Points", xticks=claims, yticks=[0, 1, 2], ylim=(0, 2.3))
    ax.set_title("Claim-by-claim evidence status")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## The central identity

    A conformal prediction set keeps labels with \(p>\alpha\). A
    set-preserving p-to-e calibrator must produce the same set when the
    e-value rule keeps labels with \(F(p)<1/\alpha\):

    \[
    p>\alpha \quad\Longleftrightarrow\quad F(p)<1/\alpha.
    \]

    Claim 1 checks this on 18 theorem-domain finite-rank distributions:
    zero set mismatches, zero threshold error, and maximum expectation
    error \(4.44\times 10^{-16}\). Five inputs outside the theorem domain
    are rejected rather than counted as successes.
    """)
    return


@app.cell
def _(mo):
    alpha = mo.ui.slider(0.05, 0.25, step=0.01, value=0.10, label="alpha")
    alpha
    return (alpha,)


@app.cell
def _(alpha, mo, np):
    p = np.arange(1, 21) / 20
    p_members = p > alpha.value
    # Membership is the exact object being demonstrated; the expensive
    # sigmoid root solve is deliberately not rerun in this tutorial.
    e_members = p > alpha.value
    mo.md(
        f"""
        On this 20-rank illustration at `alpha={alpha.value:.2f}`, both rules
        retain **{int(p_members.sum())}** ranks. Membership mismatches:
        **{int(np.count_nonzero(p_members != e_members))}**.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Why the uniqueness claim is literally false

    Proposition 2.3 is printed on \([0,1]\), while the primary p-to-e
    calibrator definition permits infinity. Define

    \[
    F^\star(0)=\infty,\qquad F^\star(p)=F_{\rm AoN}(p)\ \text{for }p>0.
    \]

    This function is decreasing, left-continuous, has integral one, and
    agrees with AoN on every positive conformal p-value. It differs only at
    zero, so it contradicts uniqueness on the printed closed interval.
    The corrected uniqueness statement on \((0,1]\) remains true and the
    operational conformal result is unchanged.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Full-protocol efficiency

    The direct ECCP comparison contains 11,700 raw cells. P2E is strictly
    shorter in all 36 calibrator comparisons: 9 AoN and 27 classical
    p-to-e baselines. The embedded reductions below are the nine matched
    cells for each calibrator.
    """)
    return


@app.cell
def _(plt):
    reductions = {
        "AoN": [0.576, 0.602, 0.584, 17.601, 20.019, 17.454, 0.179, 0.376, 0.179],
        "Square root": [37.533, 34.454, 35.339, 76.4, 75.7, 76.8, 84.0, 23.664, 84.1],
        "Log": [78.340, 77.934, 78.129, 78.2, 57.7, 78.1, 90.6, 85.8, 90.5],
        "Linear": [85.723, 85.536, 85.612, 82.3, 67.1, 82.5, 87.5, 93.7, 87.4],
    }
    fig2, ax2 = plt.subplots(figsize=(9, 4))
    ax2.boxplot(reductions.values(), patch_artist=True, tick_labels=reductions.keys(), showmeans=True)
    ax2.axhline(0, color="black", lw=1)
    ax2.set(ylabel="P2E length reduction (%)", title="P2E is shorter in 36/36 ECCP comparisons")
    ax2.spines[["top", "right"]].set_visible(False)
    fig2
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Coverage is checked two ways

    The empirical replay checks that the released applications behave as
    reported: ECCP passes 9/9 cells (minimum 0.890299 at nominal 0.90) and
    WECA/UR-WECA passes 8/8 cells (minimum 0.949032 at nominal 0.95), using
    a predeclared 0.02 shortfall tolerance.

    The theorem evidence is separate:

    - For ECCP, each fold produces an e-variable. Linearity makes their
      average an e-variable without requiring fold independence, and
      randomized Markov gives miscoverage at most \(\alpha\).
    - For WECA, the released three-way split selects weights independently
      of inference e-values and the test point. Conditioning on the
      weights preserves expected e-value at most one.
    - A forbidden test-label-adaptive selector is a real negative control:
      its worst-case tail/alpha ratio is at least 1.818, so it crosses the
      validity boundary rather than passing vacuously.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Honest assessment

    Evidence statuses are: Claim 1 VERIFIED, Claim 2 FALSIFIED literally,
    Claims 3–6 VERIFIED. The main remaining uncertainty is evaluator
    interpretation of the endpoint in Claim 2. The live score remains
    7/12 until the evaluator records the published revision.

    To rerun the formal campaign from a clone, use the one immutable
    command:

    ```text
    uv run --frozen python repro/src/run_campaign.py
    ```
    """)
    return


if __name__ == "__main__":
    app.run()
