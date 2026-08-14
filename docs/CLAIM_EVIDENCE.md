# Claim-to-evidence audit

The six claims below are the anchored challenge wording captured in
`repro/configs/jury_claims.json`. “Verified” means that the stated scope and
controls pass. It does not mean that every paper statement is universally true.

## C1 — Set preservation

The clean-room verifier constructs finite conformal-rank p-value distributions
and the proposed P2E e-variable, then checks both membership equality and the
`1/alpha` threshold identity. It covers 18 theorem-domain `(n, alpha)` cells,
with five deliberately excluded boundary/domain controls. The same cells are
cross-checked against the pinned author source.

- Verdict: **VERIFIED**.
- Evidence: `outputs/claim1_independent.json`,
  `outputs/claim1_source_crosscheck.json`.
- Controls: classical p-to-e calibrators inflate the set in all 18 cells;
  excluded-domain inputs are rejected.

## C2 — AoN uniqueness

The literal proposition quantifies over `[0,1]`. The endpoint verifier builds
the admissible witness:

```text
F*(0) = infinity
F*(p) = 1/alpha  for 0 < p <= alpha
F*(p) = 0        for alpha < p <= 1.
```

It checks that the witness satisfies the printed monotonicity,
left-continuity, integral-budget, and set-preservation assumptions while
differing from the stated AoN value at zero. This is a symbolic contradiction,
not a finite-grid approximation. The corrected conclusion is that a
set-preserving calibrator is forced to equal AoN on `(0,1]`; the endpoint is
not identified by the printed assumptions.

- Verdict: **FALSIFIED as literally printed**; corrected positive-domain form
  **VERIFIED**.
- Evidence: `outputs/claim2_endpoint_counterexample.json`,
  `outputs/anchored_claims_mechanism.json`.
- Controls: endpoint lowering, added positive-interval mass, and moved-jump
  controls fail in the intended directions.

## C3 — Sigmoid properties

The analytic verifier checks expectation one, strict positivity, a strictly
negative derivative, inverse round-trips, pointwise AoN dominance, and
aggregation dominance across 18 independent theorem-domain cases. The full
CCP evidence then compares the proposed calibrator with AoN and the classical
calibrators.

- Verdict: **VERIFIED**.
- Evidence: `outputs/claim3_properties_fullscale.json`,
  `outputs/anchored_claims_mechanism.json`, and
  `outputs/claim3_independent.json`.
- Scale: 36/36 CCP comparisons pass; P2E is shorter than AoN in 9/9 matched
  dataset/model cells.

## C4 — ECCP validity

The mechanism verifier computes exact e-merge expectations and sparse LP
worst-case rejection probabilities over all joint conformal-rank couplings
with the required marginals. It separately checks the exchangeable-prefix
variants and the paper’s randomized threshold. Invalid scaling and adaptive
weights are negative controls. The independent full-protocol summary covers
11,700 released CCP rows and nine ECCP empirical coverage cells.

- Verdict: **VERIFIED** at the stated e-value/exchangeability scope.
- Evidence: `outputs/claim4_eccp_full_protocol.json`,
  `outputs/claim3_independent_e_merge.json`, and
  `outputs/claim3_independent.json`.
- Limitation: the minimum empirical Parkinson RF mean is `0.890299` at nominal
  `0.90`; the exact verdict comes from the certificate, not the descriptive
  across-seed interval.

## C5 — WECA validity

The source audit follows the released `i1/i2/i3` split: tuning-derived weights
must be independent of final inference e-values and the test point. Six seeded
mutations keep the selected weights bit-identical when final-calibration or
test data change; a forbidden outcome-adaptive control changes. The complete
CA protocol contributes 1,920 rows and eight P2E coverage cells.

- Verdict: **VERIFIED** under the split-independence assumption.
- Evidence: `outputs/claim5_weca_full_protocol.json`,
  `outputs/weca_independence_audit.json`, and
  `outputs/claim2_independent.json`.
- Limitation: empirical rows reuse immutable released protocol results; the
  conditional proof certificate carries the general validity claim.

## C6 — Section 5 efficiency

The efficiency verifier recomputes coverage and length summaries from every raw
cell and rejects missing, duplicate, non-finite, or out-of-scope records. It
requires all 24 CA comparisons and all 36 CCP comparisons to pass the declared
materiality rule. The headline comparator parses 122 paper cells (488 scalars)
and classifies, rather than hides, known source drift.

- Verdict: **VERIFIED** at the released protocol scope.
- Evidence: `outputs/claim6_full_protocol.json`,
  `outputs/paper_headline_comparison.json`, and
  `outputs/ccp_calibrator_contract_audit.json`.
- Results: 24/24 CA wins, 36/36 CCP wins, 94 unaffected paper cells passing;
  one finite-seed CA length-SD discrepancy and 27 CCP source-discrepant cells
  are explicitly disclosed.

## Evidence dependency map

```text
sources/arxiv-v1 + pinned author commit
                 |
                 +--> source manifest / theorem-domain audits
                 +--> C1 finite-rank identity
                 +--> C2 endpoint witness
                 +--> C3 sigmoid certificate
                 +--> C4 e-merge / ECCP certificate
                 +--> C5 WECA noninterference certificate
                 +--> C6 raw efficiency + headline comparison
                                      |
                                      v
                         outputs/publication_gate.json
```

The output names `claim2_independent.json` and `claim3_independent.json` are
historical protocol names. Their claim role is defined by this matrix and the
configurations, not by the filename alone.
