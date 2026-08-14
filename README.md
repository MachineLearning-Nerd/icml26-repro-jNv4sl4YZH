# ICML 2026 reproduction: Set-Preserving P2E Calibration

This repository is the clean-room audit for [*Set-Preserving Calibration from
Conformal P-Values to E-Values*](https://arxiv.org/abs/2606.03600) by Nabil
Alami, Jad Zakharia, and Souhaib Ben Taieb. The paper studies when conformal
p-values can be converted into e-values without changing prediction sets, and
whether the resulting e-values can be merged more efficiently.

Repository target name: `icml26-set-preserving-p2e-calibration`

Paper: [arXiv:2606.03600](https://arxiv.org/abs/2606.03600) ·
[OpenReview:jNv4sl4YZH](https://openreview.net/forum?id=jNv4sl4YZH)

## Current result

The evidence supports five of the six anchored challenge claims. Claim 2 is
**falsified as literally printed**: its uniqueness statement quantifies over
`[0,1]`, but the printed assumptions permit an endpoint value
`F*(0)=infinity` while leaving `F*` equal to the all-or-nothing calibrator on
`(0,1]`. The corrected positive-domain statement is verified, and the
operational conformal result is unchanged because conformal p-values are
positive.

The complete released protocols contain 1,920 conformal-aggregation rows and
11,700 cross-conformal rows. P2E is shorter than the named baselines in 24/24
aggregation comparisons and 36/36 cross-conformal comparisons, including 9/9
comparisons against AoN. All eight aggregation and 27 cross-conformal P2E
coverage sanity cells pass the predeclared 0.02 absolute shortfall tolerance.
The exact validity claims are supported by proof-level e-value and
arbitrary-dependence certificates, not by those empirical means alone.

No challenge score is claimed here. The repository records evidence verdicts,
source drift, limitations, and reproduction scope.

## What is in the repository

| Path | Purpose |
| --- | --- |
| `repro/src/` | Independent verifiers, source-audit code, protocol runners, and the local publication gate |
| `repro/tests/` | Focused regression tests for protocol, source, claim, and negative-control contracts |
| `repro/configs/` | Paper claim snapshot, source manifest, protocol, and headline-table fixtures |
| `outputs/` | Hash-bound machine-readable evidence used by the final gate |
| `docs/` | Claim/evidence, source, branch, publication, and research-log documentation |
| `sources/arxiv-v1/` | Retrieved arXiv v1 source archive, primary TeX, and PDF used for the audit |
| `reports/` | Human-readable claim-by-claim technical report |
| `space_release/` | Historical evaluator-visible evidence snapshot; it is not the local publication authority |
| `notebooks/` | Small interactive explanation of the P2E identities and claims |

The filename `claim2_independent.json` is retained for provenance: it is the
paper's CA protocol artifact and supplies evidence for challenge Claim 5. The
literal uniqueness result is stored separately as
`claim2_endpoint_counterexample.json`.

## Claim-to-evidence map

| Challenge claim | Verdict | How the result is produced | Primary evidence |
| --- | --- | --- | --- |
| C1 — Definition 2.2 set preservation | **VERIFIED** | Construct finite-rank p-values and the P2E e-variable independently; compare set membership and threshold identities over 18 theorem-domain cells; cross-check against the pinned author source and reject five domain controls. | `outputs/claim1_independent.json`, `outputs/claim1_source_crosscheck.json` |
| C2 — Proposition 2.3 uniqueness | **FALSIFIED literally**; corrected `(0,1]` form verified | Build the symbolic endpoint witness `F*(0)=infinity`, `F*(p)=1/alpha` for `0<p<=alpha`, and `F*(p)=0` otherwise; check monotonicity, left continuity, integral budget, and set preservation. | `outputs/claim2_endpoint_counterexample.json`, `outputs/anchored_claims_mechanism.json` |
| C3 — Theorem 2.6 sigmoid properties | **VERIFIED** | Evaluate exactness, positivity, derivative sign, inverse round-trips, pointwise AoN dominance, and aggregation dominance in 18 independent cases; compare full CCP results. | `outputs/claim3_properties_fullscale.json`, `outputs/claim3_independent.json` |
| C4 — ECCP validity | **VERIFIED** | Use exact e-merge expectations, sparse LPs over arbitrary fold-rank couplings, exchangeable-prefix orbit LPs, randomized Markov controls, and the complete 11,700-row CCP protocol. | `outputs/claim4_eccp_full_protocol.json`, `outputs/claim3_independent_e_merge.json` |
| C5 — WECA validity | **VERIFIED** | Audit the released split flow, mutate final-calibration/test data, require weights to remain bit-identical, reject outcome-adaptive controls, and verify the complete 1,920-row CA protocol. | `outputs/claim5_weca_full_protocol.json`, `outputs/weca_independence_audit.json`, `outputs/claim2_independent.json` |
| C6 — Section 5 efficiency | **VERIFIED** | Recompute coverage and length from all raw cells; require every P2E comparison and materiality threshold; compare 488 paper scalars while classifying the documented source mismatches. | `outputs/claim6_full_protocol.json`, `outputs/paper_headline_comparison.json`, `outputs/ccp_calibrator_contract_audit.json` |

The production path is intentionally explicit:

```text
paper/source hashes
        -> independent mechanism verifiers
        -> raw protocol runners and cell-set verifiers
        -> negative controls and source-drift audits
        -> publication_gate.py
        -> outputs/publication_gate.json
```

## Reproduce

The deterministic environment is Python 3.12 and the locked dependencies in
`uv.lock`.

```bash
uv sync --frozen

git clone https://github.com/Nabil-Ala/P2E_calibration.git upstream
git -C upstream checkout 66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974

uv run python repro/src/verify_p2e_identity.py \
  --output outputs/claim1_independent.json
uv run python repro/src/verify_claim2_endpoint.py \
  --output outputs/claim2_endpoint_counterexample.json
uv run python repro/src/verify_anchored_claims.py \
  --output outputs/anchored_claims_mechanism.json
uv run python -m unittest discover -s repro/tests -v
```

The complete released protocols are CPU-heavy. `run_campaign.py` is the
historical cumulative runner and may retrieve the immutable public evidence
bundle before rerunning the full checks. For a clean clone that already has
the checked-in evidence outputs, the scoped publication check is:

```bash
uv run python repro/src/publication_gate.py --skip-producers
```

The gate is fail-closed. It checks the paper/source identifiers, every claim
verdict, raw-cell counts, protocol summaries, headline discrepancy accounting,
negative controls, source hashes, tracked-file hygiene, and the JSON evidence
bundle. It does not publish to GitHub, Hugging Face, Trackio, or any other
service.

## Branch audit

`main` is the canonical public branch. The other branches preserve the
experiment lineage with descriptive names; the full tip mapping and status are
in [`docs/BRANCH_AUDIT.md`](docs/BRANCH_AUDIT.md).

| Branch | Role |
| --- | --- |
| `baseline/judged-7-of-12` | Original live-score baseline |
| `baseline/protocol-sidecar-repair` | Repaired missing protocol sidecars |
| `baseline/metadata-reconstruction` | Passing cumulative baseline |
| `audit/claim-2-endpoint-counterexample` | Literal uniqueness falsifier |
| `audit/claim-3-sigmoid-aon` | Analytic sigmoid and AoN audit |
| `audit/claim-4-eccp-coverage` | ECCP mechanism and full protocol |
| `audit/claim-5-weca-independence` | WECA split-independence and CA protocol |
| `audit/judge-first-visibility` | Evaluator prompt-truncation audit |
| `release/evaluator-visible-cumulative` | Cumulative evidence release candidate |
| `release/openml-outage-fallback` | Fail-closed OpenML availability path |
| `release/final-judge-first` | Final judge-first package |
| `release/audited-publication-package` | Earlier audited publication package |

The old `orx/` prefix described the execution tool, not the scientific role;
it is not retained in the final public branch names.

## Paper citation

```bibtex
@inproceedings{alami2026setpreserving,
  title     = {Set-Preserving Calibration from Conformal P-Values to E-Values},
  author    = {Alami, Nabil and Zakharia, Jad and Ben Taieb, Souhaib},
  booktitle = {Proceedings of the 43rd International Conference on Machine Learning},
  year      = {2026},
  eprint    = {2606.03600},
  archivePrefix = {arXiv},
  url       = {https://arxiv.org/abs/2606.03600}
}
```

## Thank you

Thank you to Nabil Alami, Jad Zakharia, and Souhaib Ben Taieb for making the
paper and the pinned `Nabil-Ala/P2E_calibration` implementation available. The
public source made it possible to inspect the theorem domain, reproduce the
released protocols, identify the endpoint qualification, and document the
paper/source formula drift precisely. This repository is an independent
reproduction audit and is not an official author repository.

For the evidence policy, source provenance, branch history, and publication
checks, see [`docs/CLAIM_EVIDENCE.md`](docs/CLAIM_EVIDENCE.md),
[`docs/SOURCE_AUDIT.md`](docs/SOURCE_AUDIT.md),
[`docs/PUBLICATION_GATE.md`](docs/PUBLICATION_GATE.md), and
[`STATUS.md`](STATUS.md).
