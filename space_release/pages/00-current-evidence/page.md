# Current evidence capsule — read before historical pages

`JUDGE_FIRST_EVIDENCE_V2`

This compact page is intentionally first in lexical page order. The exact
public judge implementation reads `pages/index.md`, then every other Markdown
page lexically, and truncates at 120,000 characters. Every later
`pages/claim-*` page is preserved immutable evidence from the **Historical
rejected baseline**; none is the current verifier. The executable audit
`evidence/current/release/audit_judge_prompt_visibility.py` reproduces that
ordering and cap, proves this entire capsule is present, and proves every file
from Space revision `a7496ba32db672e7aa46c42edb3b7c3c45ff6725`
remains present. Protected historical evidence remains byte-identical; only
navigation and regenerated release manifests may change.

The paper source is arXiv `2606.03600v1`, retrieved from
`https://export.arxiv.org/e-print/2606.03600v1` on `2026-07-25T06:41:06Z`.
Archive SHA-256:
`f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db`;
`main.tex` SHA-256:
`49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857`.
The author implementation is pinned to
`Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974`.

All scientific checks below were rerun together by the unchanged command:

```text
uv run --frozen python repro/src/run_campaign.py
```

The accepted cumulative run is OpenResearch run
`88a1580c-ae40-4095-a76a-893e8ffbdcf7`, Git
`e21845d8d451497c3cb34dc36587cabe69eb5cd3`, on Hugging Face
`cpu-upgrade`; estimated useful cores 8, actual allocation 64, campaign
runtime `307.135424` seconds. It used Python `==3.12.*`, the repository
`uv.lock`, one repository `.venv`, and exited zero on 27/27 commands and
49/49 tests. CA uses the 20 released deterministic seeds; CCP uses seeds
45–144. Each checker exits nonzero on any failed contract field.

**OpenML availability rule.** The current regression first re-downloads and
rehashes all four live OpenML tasks. If and only if the official API returns a
server-side 5xx, it instead revalidates the immutable prior live-OpenML
attestation restored from the SHA-256-pinned evidence bundle against the exact
task manifest, array hashes, source commit, author-loader hash, and clean
worktree. It records that fallback mode explicitly. A 4xx, changed manifest,
changed array hash, changed loader, missing attestation, or tampered
attestation exits nonzero; three dedicated controls exercise those boundaries.

## `EXACT_CLAIM_1_EVIDENCE` — set preservation

**Source contract.** Definition 2.2 and Theorem 2.6 require, for every
finite-rank conformal p-value in the theorem domain,
`p > alpha` if and only if `F(p) < 1/alpha`. The audited domain is the rank
grid `{1/(n+1),...,1}`, with `alpha(n+1)>1` and non-integral
`alpha(n+1)`.

**Direct construction and result.** The verifier independently reconstructs
the sigmoid root, enumerates every rank in 18 predeclared `(n,alpha)` cells
with `n` through 200 and `alpha` in `{0.05,0.1,0.2}`, and checks both sides of
the biconditional:

```python
for rank in range(1, n + 2):
    p = rank / (n + 1)
    assert (p > alpha) == (F(p) < 1 / alpha)
assert abs(sum(F(r/(n+1)) for r in range(1,n+2))/(n+1) - 1) < 1e-11
```

Observed independent summary:

```json
{"cleanroom_cells_checked":18,"source_cells_checked":18,
 "membership_mismatches":0,"maximum_expectation_abs_error":4.440892098500626e-16,
 "negative_controls_checked":23,"status":"PASS"}
```

Threshold-identity error was exactly zero in all cells. The separate
hash-pinned author-source cross-check also had zero mismatches in 18/18 cells.
Five excluded-domain controls were rejected. Log, square-root, and linear
calibrators inflated sets in all 18 control cells; a tampered membership record
makes the checker exit nonzero.

Executable and raw evidence:
[contract](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-1/claim_contract.json),
[verifier](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-1/verifier.py),
[checker](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-1/checker.py),
[clean-room JSON](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-1/raw_cleanroom_output.json),
[source cross-check](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-1/raw_source_crosscheck.json),
[controls](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-1/negative_control_output.json).

## `EXACT_CLAIM_2_EVIDENCE` — uniqueness, exact printed domain

**Source contract and quantifier.** Proposition 2.3 universally quantifies
over decreasing, left-continuous p-to-e calibrators
`F:[0,1] -> [0,infinity]` that are set-preserving for every `n` and
nonconformity score, and states that only AoN qualifies.

**Proof-level reconstruction on the operational domain `(0,1]`.** Set
preservation plus left continuity forces `F(alpha)=1/alpha`. Monotonicity gives
`F(p)>=1/alpha` on `(0,alpha]`; this interval already consumes the complete
calibrator budget,
`integral_0^alpha F >= alpha*(1/alpha)=1`. Nonnegativity therefore forces zero
almost everywhere on `(alpha,1]`, and monotonicity plus left continuity
upgrades that equality to pointwise equality. Repeating over `alpha` gives
AoN on every positive conformal p-value.

**Literal endpoint counterexample.** None of those steps constrains `F(0)`.
The primary calibrator reference explicitly permits extended values and
`f(0)=infinity`. Define:

```text
F*(0) = infinity
F*(p) = F_AoN(p) for every p in (0,1].
```

Then `F*` is decreasing; left continuity imposes no condition from the left at
zero; its Lebesgue integral is exactly one because a singleton has measure
zero; every conformal p-value is positive, so it is set-preserving for every
stated sample and score; yet it differs from the paper's finite-valued AoN at
zero. This satisfies the printed assumptions and contradicts literal
uniqueness on `[0,1]`, while leaving the useful corrected theorem on `(0,1]`
intact.

The exact rational verifier checked seven alphas and 880,250 positive support
points. Independent output:

```json
{"checked_alpha_rows":7,"checker_is_independent_of_verifier_implementation":true,
 "failures":[],"status":"PASS","verdict_checked":"FALSIFIED"}
```

Three assumption-sensitive controls fail for distinct intended reasons:
`F(0)=0` violates decreasingness; adding positive-interval mass gives integral
`101/100`; shifting the jump creates a membership mismatch at `p=1/10`,
`n=99`. Thus this is an assumption-satisfying counterexample to the exact
printed domain, not a numerical proxy or failed implementation.

Executable and raw evidence:
[contract](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-2/claim_contract.json),
[verifier](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-2/verifier.py),
[independent checker](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-2/checker.py),
[exact rational output](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-2/raw_counterexample_output.json),
[controls](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-2/negative_control_output.json),
[source audit](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-2/source_audit.md).

## `EXACT_CLAIM_3_EVIDENCE` — sigmoid properties and AoN comparison

**Source contract.** Theorem 2.6 and Equation `final_evalue` assert exactness,
smoothness, invertibility, strict positivity, and AoN dominance when
`alpha(n+1)>1`, non-integral `alpha(n+1)`,
`alpha<s<ceil(alpha(n+1))/(n+1)`, and the positive exactness root `C`.

**Analytic certificate.** Writing the positive numerator constant as `A`,
the verifier reconstructs:

```text
F'(p) = -C*A*exp(C(p-s)) / [alpha*(1+exp(C(p-s)))^2] < 0
F^{-1}(e) = s + log(A/(alpha*e)-1)/C
```

The logistic expression is smooth and positive on the domain. Exact discrete
expectation and `F(alpha)=1/alpha` were checked over all 18 theorem-domain
cells: maximum expectation error `4.44e-16`, maximum inverse round-trip error
`2.22e-16`, every sampled derivative strictly negative, every value positive.
Pointwise `F_P2E(p)>=F_AoN(p)`, strict except at `p=alpha`, gives non-strict
prediction-set inclusion after aggregation. This is the theorem-level scope;
universal strict set-size reduction is not claimed.

**Direct full protocol against AoN.** The released CCP experiment contains
11,700 raw rows, three datasets, three models, 100 seeds per cell. P2E sets are
strictly shorter than AoN in 9/9 dataset–model cells; minimum absolute
reduction `0.0212515`, minimum relative reduction `0.178669%`.

```json
{"analytic_cases_checked":18,"fullscale_AoN_comparisons_checked":9,
 "failures":[],"status":"PASS"}
```

Controls with `C=0`, `C<0`, and a `0.99` scaling respectively lose
invertibility/strict decrease, become increasing, and violate exactness plus
the equality at alpha.

Executable and raw evidence:
[verifier](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-3/verifier.py),
[checker](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-3/checker.py),
[analytic and AoN JSON](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-3/raw_properties_and_aon_output.json),
[controls](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-3/negative_control_output.json).

## `EXACT_CLAIM_4_EVIDENCE` — ECCP finite-sample validity

**Exact claim and assumptions.** Proposition 4.1 states that ECCP covers with
probability at least `1-alpha`; the named standard CCP variants have only the
approximate `1-2alpha` bound plus finite-sample correction. The assumptions are
test/calibration exchangeability, each fold P2E output being an e-variable,
independent uniform `U` for randomized ECCP, and fold-e-value exchangeability
only for the prefix variants. “Exact” is a finite-sample lower-bound guarantee,
not equality of empirical coverage.

**Universal derivation.** If `E_k` is the fold e-value, exchangeability gives
`E[E_k]<=1`. Hence, without any independence among folds,

```text
E[(1/K) sum_k E_k] = (1/K) sum_k E[E_k] <= 1.
P((1/K) sum_k E_k >= 1/alpha) <= alpha
```

The last line is Markov; randomized Markov handles the randomized rule. The
exchangeable prefix variants use their separately stated e-merging inequality.
The certificate is symbolic and does not infer universality from enumeration.
Exact arbitrary-dependence checks cover eight cases and exchangeable-prefix
checks five; maximum valid tail/alpha ratio is `0.952381` (randomized `1.0`).
Invalid scaling and invalid prefix-dependence controls are detected.

**Released empirical protocol.** All 11,700 rows were independently parsed.
All 9/9 dataset–model ECCP coverage means pass the predeclared absolute
shortfall tolerance `0.02`; minimum mean `0.890299` at nominal `0.90`, across
100 seeds. The Parkinson–RF descriptive across-seed 95% interval lies below
0.90 and is disclosed; it neither proves nor refutes the finite-sample theorem,
which follows from the certificate above.

```json
{"full_protocol_rows_checked":11700,"coverage_cells_checked":9,
 "failures":[],"status":"PASS"}
```

For comparison, reconstructed standard-CCP lower bounds at alpha `0.1` range
from `0.79149` to `0.79284`, below ECCP's `0.9` target.

Executable and raw evidence:
[verifier](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-4/verifier.py),
[checker](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-4/checker.py),
[full-protocol JSON](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-4/raw_eccp_full_protocol.json),
[controls](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-4/negative_control_output.json).

## `EXACT_CLAIM_5_EVIDENCE` — data-dependent WECA weights

**Exact claim and assumptions.** Proposition 4.2 permits simplex weights
`omega*=g(D_tune)` chosen from tuning data, provided those weights are
independent of the inference e-values and test point, and the test point is
exchangeable with each inference split.

**Conditional proof certificate.** Conditional on the tuning-selected weight:

```text
E[sum_k omega*_k E_k | omega*]
  <= sum_k omega*_k = 1.
```

Thus Markov or randomized Markov bounds miscoverage by alpha. No independence
among the inference e-values is needed. This derivation, not six finite
mutations, carries the universal statement.

**Implementation and empirical audits.** The pinned author source partitions
indices into disjoint tuning, weight-calibration, and final-calibration sets.
For each of six released seeds, replacing every final-calibration row or every
test covariate/outcome changes selected weights by exactly `0.0`; the source
flow contract checks 11 required dependencies. Full released protocol:
1,920 rows, four OpenML tasks, 20 seeds, seven regressors, `M=512`, `B=500`.
All 8/8 P2E WECA/UR-WECA coverage cells pass the `0.02` tolerance; minimum
coverage `0.949032` at nominal `0.95`.

```json
{"full_protocol_rows_checked":1920,"coverage_cells_checked":8,
 "mutation_cases_checked":6,"failures":[],"status":"PASS"}
```

A forbidden test-label-adaptive selector changes weights in all 6/6 source
controls and violates the e-bound: minimum tail/alpha ratios `1.818`
deterministic and `1.943` randomized. This demonstrates why the proposition's
independence condition is substantive.

Executable and raw evidence:
[verifier](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-5/verifier.py),
[checker](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-5/checker.py),
[full-protocol JSON](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-5/raw_weca_full_protocol.json),
[controls](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-5/negative_control_output.json).

## `EXACT_CLAIM_6_EVIDENCE` — full-protocol efficiency and coverage

**Exact empirical contract.** Section 5 claims smaller prediction sets than
the named p-to-e baselines while retaining valid empirical coverage in CA and
ECCP. CA uses four OpenML tasks, 20 seeds, seven regressors, `M=512`, `B=500`,
nominal `0.95`. CCP uses three bundled datasets, three models, 100 seeds,
paper fold counts, nominal `0.90`.

**Complete results.**

| Protocol | Raw rows | Direct comparisons | P2E shorter | Coverage cells |
| --- | ---: | ---: | ---: | ---: |
| WECA / UR-WECA | 1,920/1,920 | 24 | 24/24 | 8/8 |
| ECCP | 11,700/11,700 | 36 | 36/36 | 9/9 |

For CA, minimum relative length reduction is `40.302%` and minimum P2E
coverage is `0.949032` at nominal `0.95`. For ECCP, the 36 comparisons include
AoN 9/9 and log/square-root/linear 27/27; minimum classical-baseline reduction
is `23.664%`, minimum AoN reduction `0.178669%`, and minimum P2E coverage
`0.890299` at nominal `0.90`.

```json
{"ca_rows_checked":1920,"eccp_rows_checked":11700,
 "ca_comparisons_checked":24,"eccp_comparisons_checked":36,
 "failures":[],"status":"PASS"}
```

The released CCP columns F1/F2/F3 drift from formula names; the audit is bound
to the source hash and compares formula-faithful log, square-root, and linear
calibrators. One finite-seed CA length-SD scalar is `0.201899` versus paper
`0.18`; the remaining scalars in that cell and every efficiency/coverage
contract pass. Negative controls prove the tolerance cannot be vacuous, a
missing cell fails closed, and reversing the efficiency rule fails.

Executable and raw evidence:
[verifier](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-6/verifier.py),
[checker](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-6/checker.py),
[full-protocol summary](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-6/raw_full_protocol_summary.json),
[controls](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-6/negative_control_output.json),
[complete immutable 13,620-row bundle](https://huggingface.co/buckets/DineshAI/jNv4sl4YZH-artifacts#logbook-files/outputs/jNv4sl4YZH_full_evidence_bundle.jsonl).

## Scope and reviewer decision surface

The evidence supports Claim 1 and Claims 3–6 directly. For Claim 2, the
operational theorem on positive p-values is proof-verified, while the exact
printed universal statement on `[0,1]` has the explicit endpoint
counterexample above. A reviewer can therefore accept the useful corrected
theorem or independently classify the literal printed statement as falsified;
neither conclusion rests on a finite toy sweep.

The previous live score is `7/12`; no score change is asserted until the live
judge evaluates this new Space revision. The strongest scientifically
supported forecast is `12/12`, with a conservative `10–12/12` range because
Claim 2 depends on whether the endpoint convention is interpreted literally.

`END_JUDGE_FIRST_EVIDENCE_V2`
