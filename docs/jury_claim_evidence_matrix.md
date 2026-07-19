# Jury claim evidence matrix

This matrix uses the exact three claim texts retrieved from the challenge's
official `claims.json` for OpenReview `jNv4sl4YZH` on 2026-07-19. The machine-
readable snapshot is `repro/configs/jury_claims.json`; the publication gate
requires all three entries and the six-point total exactly.

| Jury claim | Direct reproduction evidence | Independent evidence and falsifiers | Fail-closed acceptance rule |
| --- | --- | --- | --- |
| **C1.** P2E calibrator converts conformal p-values to e-values without altering the induced prediction set | `outputs/claim1_source_crosscheck.json` invokes the pinned author implementation over all 18 finite-rank `(n, alpha)` cells. | `outputs/claim1_independent.json` independently enumerates the finite ranks, verifies identical p/e threshold membership and exact e-value expectations, and shows classic calibrators inflate every eligible set. | 18/18 source and clean-room membership identities; every exact expectation passes; all positive and inflation controls pass; documented source underflow cannot change membership. |
| **C2.** Yields substantial efficiency gains over existing p-to-e methods in conformal inference | Four released OpenML tasks, 20 fixed seeds, 24 methods, `M=512`, and `B=500`, producing exactly 1,920 raw cells under `outputs/raw/author_ca/`. | `outputs/claim2_independent.json` reconstructs coverage/length directly from raw cells and compares P2E with log, square-root, and linear calibrators in matched WECA and UR-WECA families. `outputs/paper_headline_comparison.json` checks the eight reported CA P2E cells. | Exact expected cell set; no missing, duplicate, unexpected, or non-finite rows; P2E must reduce length by at least the pre-final-dataset 10% materiality threshold in all 24/24 matched comparisons; all reported CA mean/SD scalars inside the predeclared tolerances. |
| **C3.** Enables exact 1-α coverage in cross-conformal prediction and conformal aggregation | Released CCP protocol on Boston, Abalone, and Parkinson data: 100 seeds, three models, 13 methods, and the paper's `K=15/15/20`, producing exactly 11,700 raw cells. The complete CA evidence from C2 covers the second named application. | `outputs/claim3_independent.json` recomputes CCP coverage/length from every raw cell. `outputs/claim3_independent_e_merge.json` exactly enumerates rank tuples and solves a sparse LP over every joint coupling with the required uniform rank marginals in two equal-weight ECCP and six nonuniform WECA cases; invalid scaling and forbidden outcome-adaptive weighting are falsifiers. | Exact 11,700-cell set; all nine reported ECCP mean/SD cells inside tolerance; every valid fixed-weight coupling has worst-case failure probability at most `alpha`; adaptive weighting must violate the bound in 8/8 cases. |

The empirical coverage estimates check the released applications and headline
numbers; the exact rank enumeration and adversarial-coupling LP check the
finite-sample guarantee. Neither is presented as a substitute for the other.
