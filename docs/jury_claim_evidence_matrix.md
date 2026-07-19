# Jury claim evidence matrix

The challenge frontend gives `claims_anchored.json` priority over the broad
fallback `claims.json`. For OpenReview `jNv4sl4YZH`, the effective live entry
has six anchored claims worth 12 points. `repro/configs/jury_claims.json` pins
their exact text; the publication gate downloads and verifies both live files
and refuses any count, wording, or merge-source drift.

| Claim | Direct reproduction evidence | Independent evidence and fail-closed rule |
| --- | --- | --- |
| **C1 — Definition 2.2 set preservation.** | `outputs/claim1_source_crosscheck.json` invokes the pinned implementation over 18 theorem-domain finite-rank cells. | `outputs/claim1_independent.json` independently constructs the sigmoid and requires exact p/e membership and threshold identities in 18/18 cells. All five excluded-domain controls must reject. |
| **C2 — AoN uniqueness and sigmoid motivation.** | `outputs/anchored_claims_mechanism.json` hash-binds Proposition 2.3, Theorem 2.6, Equation 9, and the full uniqueness proof in arXiv v1. | Four exact rational budget certificates require the forced lower plateau to consume the full p-to-e integral budget, zero remaining tail budget, and a valid conformal-grid witness for the left-continuity contradiction. |
| **C3 — Exact, smooth, invertible, positive, AoN-dominating P2E.** | The same anchored audit evaluates all 18 theorem cases used by C1 and binds the analytic derivative and inverse in the primary TeX. | Every case must have expectation error below `1e-11`, inverse round-trip error below `1e-10`, finite log-values, strictly negative derivatives, pointwise P2E ≥ AoN with strict witnesses, and the correct P2E-set-subset-of-AoN aggregation direction. The full CCP run must also be strictly shorter than AoN in 9/9 cells. |
| **C4 — ECCP `1-alpha` coverage versus standard CCP.** | `outputs/claim3_independent.json` reproduces exactly 11,700 CCP cells: three datasets, 100 seeds, three models, and 13 methods. | `outputs/claim3_independent_e_merge.json` solves arbitrary-dependence coupling LPs and exchangeable-orbit LPs for deterministic and randomized ECCP rules. The anchored audit binds Proposition 4.1 and the standard bound `1-2alpha-correction`; four numerical cases require it to remain below `1-alpha`. All 27 P2E coverage cells must pass the fixed empirical shortfall sanity rule. |
| **C5 — data-dependent WECA validity.** | `outputs/claim2_independent.json` verifies exactly 1,920 CA cells over four OpenML tasks, 20 seeds, and 24 methods. | `outputs/weca_independence_audit.json` hash-binds the released three-way split and requires selected weights to remain unchanged under final-calibration and test-data/outcome mutations in 6/6 cases; a forbidden test-adaptive control must change in 6/6. Six nonuniform weighted coupling LPs must retain deterministic and randomized validity, while outcome-adaptive weighting must fail. |
| **C6 — smaller ECCP sets with valid coverage.** | The full CCP verifier requires P2E to be strictly shorter in all 36/36 matched calibrator comparisons, including 9/9 AoN and 27/27 classical comparisons; every classical reduction must exceed the predeclared 10% materiality threshold. | `outputs/paper_headline_comparison.json` checks all 488 reported mean/SD scalars across 122 paper-table cells. The exact cell set, finite metric ranges, all efficiency rules, and all 27 P2E coverage sanity cells must pass simultaneously. |

The empirical coverage estimates reproduce the released applications; the
rank/coupling certificates establish the finite-sample mechanisms. Neither is
used as a substitute for the other. `outputs/ca_p2e_domain_audit.json` also
accounts for every one of the 1,680 internal CA calibration contexts: 1,600 are
inside Theorem 2.6 and 80 are exact-rank numerical-limit contexts. Those 80
preserve the released sets and admit exact AoN mean-one repairs, but are not
misreported as positive exact-P2E theorem instances.
