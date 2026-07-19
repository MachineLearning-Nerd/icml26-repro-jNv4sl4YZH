# Reproduction: Set-Preserving Calibration from Conformal P-Values to E-Values

ICML 2026 paper / OpenReview `jNv4sl4YZH` / arXiv `2606.03600`.

## Scope

This reproduction evaluates all three challenge claims at the released paper
protocol, rather than treating a small synthetic example as a substitute:

1. The finite-sample P2E mapping preserves the original conformal prediction
   set while producing an exact e-value.
2. P2E-based conformal aggregation is more efficient than the released
   comparator calibrators on the paper's four 20-seed OpenML tasks.
3. The released cross-conformal and aggregation constructions satisfy their
   advertised `1 - alpha` guarantee; the paper-scale CCP runs cover Boston,
   Abalone, and Parkinson data with 100 seeds each.

The mechanism audit includes exact rank-tuple enumeration and a sparse linear
program over every joint coupling with the prescribed rank marginals, so the
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
python repro/src/compare_paper_headlines.py \
  --ca outputs/claim2_independent.json \
  --ccp outputs/claim3_independent.json \
  --output outputs/paper_headline_comparison.json
python -m unittest discover -s repro/tests -v
```

The CA run evaluates 1,920 raw method/seed cells (four OpenML tasks, 20
seeds). The CCP run evaluates 11,700 raw model/method/seed cells (three bundled
datasets, 100 seeds). These are long CPU runs, not smoke tests. After they
finish, build the evidence-derived logbook cells and execute the final gate:

```bash
python repro/src/render_final_logbook.py \
  --output outputs/final_logbook_cells.json
python repro/src/prepublish_gate.py \
  --output outputs/prepublish_gate.json
```

After the full source runs finish, `python repro/src/prepublish_gate.py` reruns
all independent checks and tests, validates every raw cell, verifies the
Trackio evidence and source pin, checks all 68 reported mean/SD scalars in the
17 paper headline cells, requires all 24 CA material-efficiency comparisons
and all 36 CCP calibrator comparisons (including nine AoN cells), scans for
secrets/local paths, and emits a SHA-256 manifest only if the complete
publication gate passes. It also creates
a hash-indexed JSONL bundle containing seven summary/report artifacts and all
seven full raw dataset files; Trackio recognizes this format and promotes
it to the Hugging Face artifact bucket on publication.

`repro/src/publish_after_gate.sh` is the final idempotent publication step. It
accepts only a passing three-claim gate, pushes the public GitHub repository,
publishes the Trackio Space, and reads both services back. Success requires
the public challenge tags, a nonempty Space commit SHA, the final Conclusion
marker, and an artifact-bucket copy of the evidence bundle with the exact
local byte size. Trackio's local-only metadata is deliberately gitignored so
its artifact source path cannot leak into GitHub.

## Current status

The source and environment are pinned. Claim 1 is complete. Claim 2's full
four-dataset run is active; three datasets (1,440/1,920 cells) are complete.
Claim 3's full 11,700-cell run is serialized behind the final Claim 2 dataset.
The environment pins `pandas==2.3.3` because the unmodified released Parkinson
loader relies on a Pandas-2-compatible in-place numeric assignment; the reason
and exact wrapper boundary are documented in `docs/source_audit.md`.
