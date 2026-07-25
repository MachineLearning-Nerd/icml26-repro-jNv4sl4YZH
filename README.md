# Reproduction: Set-Preserving Calibration from Conformal P-Values to E-Values

[![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/MachineLearning-Nerd/icml26-repro-jNv4sl4YZH/blob/main/notebooks/p2e_claims.py)

**Paper:** ICML 2026 / OpenReview `jNv4sl4YZH` /
[arXiv `2606.03600`](https://arxiv.org/abs/2606.03600) · **Live judged
baseline:** 7/12 · **Compute:** Hugging Face `cpu-upgrade`, CPU only

The paper claims that its sigmoid p-to-e calibration preserves conformal sets,
retains finite-sample validity under ECCP and data-dependent WECA merging, and
improves prediction-set efficiency. We audited all six evaluator claims.
Observed evidence is: Claim 1 VERIFIED; literal Claim 2 FALSIFIED by an
assumption-satisfying endpoint witness; Claims 3–6 VERIFIED. On the complete
released protocols, P2E was shorter in 36/36 ECCP calibrator comparisons and
24/24 WECA/UR-WECA classical-calibrator comparisons. All 9 ECCP and 8 WECA
P2E coverage means met the predeclared 0.02 shortfall tolerance.

This campaign does not downscale the paper’s reported CA/CCP grids: it
revalidates 1,920 and 11,700 immutable raw cells, respectively. The cumulative
campaign reaggregates those hash-pinned cells rather than retraining every
author estimator. Coverage intervals are descriptive; Claims 4 and 5 use
separate proof-level mechanism certificates. A best-supported 12/12 is only a
forecast until the live judge evaluates the new Space revision.

- [Illustrated technical report](reports/set-preserving-p2e-reproduction-2026-07-25/report.md)
- [Self-contained marimo tutorial](notebooks/p2e_claims.py)
- [Claim contracts and fail-closed evidence](.openresearch/artifacts)

## Experiment log

The exact run command is identical on every formal node:
`uv run --frozen python repro/src/run_campaign.py`.

| Branch / experiment | Purpose or change | Exact run command | Assessment / outcome | Compute |
| --- | --- | --- | --- | --- |
| `main` | Public landing page, report, notebook, and published release mirror | Not run as an experiment (publication surface) | Presentation-only | None |
| [`orx/baseline-metadata-reconstruction`](https://github.com/MachineLearning-Nerd/icml26-repro-jNv4sl4YZH/tree/orx/baseline-metadata-reconstruction) | Passing cumulative baseline after deterministic packaging repairs | `uv run --frozen python repro/src/run_campaign.py` | 14/14 commands; 35/35 tests | HF `cpu-upgrade`, 64 vCPU allocation, 1m29s wall |
| [`orx/claim-2-literal-endpoint-counterexample`](https://github.com/MachineLearning-Nerd/icml26-repro-jNv4sl4YZH/tree/orx/claim-2-literal-endpoint-counterexample) | Test Proposition 2.3 on its printed `[0,1]` domain | `uv run --frozen python repro/src/run_campaign.py` | Literal statement FALSIFIED; positive-domain correction verified | HF `cpu-upgrade`, 64 vCPU allocation, 1m45s wall |
| [`orx/claim-3-analytic-and-full-scale-aon-verification`](https://github.com/MachineLearning-Nerd/icml26-repro-jNv4sl4YZH/tree/orx/claim-3-analytic-and-full-scale-aon-verification) | Smoothness, inverse, positivity, exactness, and direct AoN comparison | `uv run --frozen python repro/src/run_campaign.py` | VERIFIED; P2E shorter than AoN 9/9 | HF `cpu-upgrade`, 64 vCPU allocation, 1m51s wall |
| [`orx/claim-4-eccp-universal-mechanism-and-full-protoc`](https://github.com/MachineLearning-Nerd/icml26-repro-jNv4sl4YZH/tree/orx/claim-4-eccp-universal-mechanism-and-full-protoc) | Universal ECCP mechanism plus the 11,700-row protocol | `uv run --frozen python repro/src/run_campaign.py` | VERIFIED; 9/9 coverage cells | HF `cpu-upgrade`, 64 vCPU allocation, 1m45s wall |
| [`orx/claim-5-data-dependent-weca-full-protocol`](https://github.com/MachineLearning-Nerd/icml26-repro-jNv4sl4YZH/tree/orx/claim-5-data-dependent-weca-full-protocol) | Source-level data-dependence audit plus the 1,920-row protocol | `uv run --frozen python repro/src/run_campaign.py` | VERIFIED; 8/8 coverage cells; adaptive control rejected | HF `cpu-upgrade`, 64 vCPU allocation, 1m45s wall |

## Scope

This reproduction evaluates all six anchored challenge claims at the released paper
protocol, rather than treating a small synthetic example as a substitute:

1. Definition 2.2 set preservation across the exact finite-rank domain.
2. Proposition 2.3 uniqueness of the left-continuous AoN calibrator and the
   resulting sigmoid motivation.
3. Theorem 2.6 exactness, smoothness, invertibility, positivity, and AoN
   dominance of the proposed P2E sigmoid.
4. Proposition 4.1 exact `1-alpha` ECCP validity versus the weaker standard
   CCP guarantee.
5. Proposition 4.2 tuning-independent data-dependent WECA validity.
6. Section 5 paper-scale ECCP efficiency with valid empirical coverage.

The mechanism audit includes exact rank-tuple enumeration and sparse linear
programs over every joint coupling with the prescribed rank marginals, for
both deterministic and the paper's independent-uniform randomized thresholds,
plus an orbit LP for the exchangeable prefix-maximum ECCP variants, so the
coverage check is not restricted to independent folds. See
[`docs/arbitrary_dependence_coverage.md`](docs/arbitrary_dependence_coverage.md).
The exact current jury wording and the evidence/gate for each claim are mapped
in [`docs/jury_claim_evidence_matrix.md`](docs/jury_claim_evidence_matrix.md).

The source implementation is checked out locally under `upstream/` at
`Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974`.
`repro/` contains independent checks and a full-protocol runner. Generated
summaries belong in `outputs/`.

## Reproduce from a fresh clone

The local official-source checkout is intentionally not committed as an
embedded Git repository. Fetch and verify the exact source revision before
running the evidence pipeline:

```bash
git clone https://github.com/Nabil-Ala/P2E_calibration.git upstream
git -C upstream checkout 66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974
test "$(git -C upstream rev-parse HEAD)" = \
  66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974

uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -r repro/requirements.lock.txt
```

Run the deterministic Claim 1 checks and the complete released Claim 2 and
Claim 3 protocols. The runners write one atomic final file per dataset and can
reuse a previously completed dataset safely:

```bash
python repro/src/verify_p2e_identity.py \
  --output outputs/claim1_independent.json
python repro/src/crosscheck_source_p2e.py \
  --source upstream --output outputs/claim1_source_crosscheck.json
python repro/src/verify_anchored_claims.py \
  --output outputs/anchored_claims_mechanism.json
python repro/src/verify_source_manifest.py \
  --source upstream --output outputs/source_manifest_audit.json
python repro/src/verify_ca_inputs.py \
  --source upstream --output outputs/ca_input_audit.json
python repro/src/verify_ca_p2e_domains.py \
  --source upstream --output outputs/ca_p2e_domain_audit.json

python repro/src/run_author_ca.py \
  --source upstream --output-dir outputs/raw/author_ca
python repro/src/verify_ca_results.py \
  --raw-dir outputs/raw/author_ca --output outputs/claim2_independent.json

python repro/src/run_author_ccp.py \
  --source upstream --output-dir outputs/raw/author_ccp
python repro/src/verify_ccp_results.py \
  --raw-dir outputs/raw/author_ccp --output outputs/claim3_independent.json

python repro/src/verify_e_merge_coverage.py \
  --output outputs/claim3_independent_e_merge.json
python repro/src/verify_weca_independence.py \
  --source upstream --output outputs/weca_independence_audit.json
python repro/src/compare_paper_headlines.py \
  --ca outputs/claim2_independent.json \
  --ccp outputs/claim3_independent.json \
  --output outputs/paper_headline_comparison.json

# Independently re-download the hash-pinned arXiv v1 source and verify that
# all 122 fixture cells / 488 scalars were transcribed exactly from its TeX.
python repro/src/verify_paper_table_fixture.py \
  --output outputs/paper_table_fixture_audit.json
python repro/src/verify_ccp_calibrator_contract.py \
  --source upstream --output outputs/ccp_calibrator_contract_audit.json
python -m unittest discover -s repro/tests -v
```

The CA run evaluates 1,920 raw method/seed cells (four OpenML tasks, 20
seeds). The CCP run evaluates 11,700 raw model/method/seed cells (three bundled
datasets, 100 seeds). CCP uses the fail-closed
`vectorized-exact-postprocessing-v1` adapter: all source estimator, grid,
foldwise p-value, and RNG outputs are preserved, while deterministic p/e
aggregation is vectorized. Literal-source parity is tested across OLS, RF, and
Lasso for all 13 methods. These are long CPU runs, not smoke tests. After they
finish, build the evidence-derived logbook cells and execute the final gate:

```bash
python repro/src/render_final_logbook.py \
  --output outputs/final_logbook_cells.json
python repro/src/prepublish_gate.py \
  --output outputs/prepublish_gate.json
```

After the full source runs finish, `python repro/src/prepublish_gate.py` reruns
all independent checks and tests, validates every raw cell, verifies the
Trackio evidence and source pin, compares all 488 reported mean/SD scalars in
the 122 tabulated paper cells, requires all 376 unaffected scalars to pass,
requires the exact one-scalar CA finite-seed dispersion mismatch to be
explicitly disclosed, and requires all 108 scalars in the
paper/released-code F1/F2/F3 inconsistency to be source-hash-bound and
explicitly classified. The reversible released log/square-root column swap is
additionally replayed against the paper table, and all 72 available scalars
must pass the same fixed tolerances. It also requires all 24 CA material-efficiency comparisons
and all 36 CCP calibrator comparisons (including nine AoN cells), scans for
secrets/local paths, and emits a SHA-256 manifest only if the complete
publication gate passes. It also creates
a hash-indexed JSONL bundle containing fourteen summary/report artifacts and all
seven full raw dataset files; Trackio recognizes this format and promotes
it to the Hugging Face artifact bucket on publication.

`repro/src/publish_after_gate.sh` is the final idempotent publication step. It
accepts only a passing six-claim/12-point gate, pushes the public GitHub repository,
atomically joins the single shared Hugging Face publication queue, and reads
both services back after the shared drain publishes the Trackio Space. Success requires
the public challenge tags, a nonempty Space commit SHA, the final Conclusion
marker, and an artifact-bucket copy of the evidence bundle with the exact
local byte size. Trackio's local-only metadata is deliberately gitignored so
its artifact source path cannot leak into GitHub.

## Current status

The reproduction is complete and publicly submitted for verdict. The full
four-dataset CA run contains 1,920/1,920 cells, the full three-dataset CCP run
contains 11,700/11,700 cells, and the six-claim theorem/mechanism audit passes.
All 35 tests and the final publication gate pass. The public GitHub repository
is `MachineLearning-Nerd/icml26-repro-jNv4sl4YZH`; canonical backlog entry 43
was drained to `DineshAI/jNv4sl4YZH`, whose challenge tags, nonempty commit SHA,
Conclusion marker, and 2,781,144-byte Trackio evidence bundle were read back.
A hash-bound audit verifies that the paper defines the three alternative CCP
columns as log/square-root/linear while the released table driver fills those
positions with square-root/log/power; formula-faithful results remain honestly
labeled.
The environment pins `pandas==2.3.3` because the unmodified released Parkinson
loader relies on a Pandas-2-compatible in-place numeric assignment; the reason
and exact wrapper boundary are documented in `docs/source_audit.md`.
