# Source audit

The repository is author-owned and describes itself as the ICML 2026
reproduction package. Its `e-ca/` implementation has the four exact OpenML
task IDs, 20 fixed seeds, alpha `.05`, seven base models, `M=512`, and `B=500`
used for the conformal-aggregation study. Its `e-ccp/` tree contains the
Boston, Abalone, and Parkinson/UPDRS inputs plus the 100-seed cross-conformal
driver.

The executable source and bundled CCP inputs are also pinned independently of
the Git reference in `repro/configs/source_manifest.json`. The manifest records
SHA-256, Git blob SHA-1, and byte size for all ten released files used to define
or execute the CA/CCP protocols. Its verifier parses all three CSVs, checks
10,558 data rows and their exact headers, then executes the pinned loader and
requires the Boston, Abalone, and Parkinson arrays to have shapes `(506, 14)`,
`(4177, 10)`, and `(5875, 13)` with finite values and exact loader configs. The
final publication gate reruns this check and includes its hash-indexed audit in
the public evidence bundle.

The paper specifies `K=15` for Boston/Abalone and `K=20` for Parkinson in its
reported CCP tables. The upstream driver exposes `K` as a local constant, so
the reproduction runner will pass those values explicitly rather than silently
using its default of five folds. This is a transparent protocol completion, not
a change to the P2E method.

The independent verifier will not import the upstream P2E helper: it will
construct the finite rank distribution and P2E threshold separately, recompute
the e-value expectation and p/e set equality, and reconstruct coverage and
length summaries from raw output rows.

The hash-pinned primary TeX states the main P2E theorem only when
`alpha*(n+1) > 1` and this quantity is non-integer. The Claim-1 verifier now
enforces that contract before solving for the calibrator: its 18 positive cells
all satisfy the theorem assumptions, and five deliberately low-level or
exact-rank-boundary inputs must be rejected. This corrects an earlier audit
grid that included `(n=10, alpha=.05)` as a numerical extension even though it
was outside the stated theorem domain.

The WECA guarantee additionally requires its selected nonuniform weights not
to depend on final inference e-values. The pinned source partitions calibration
indices into `i1/i2/i3`, builds candidate weights from `i1` scores and `i2`
covariates, then evaluates final p/e-values only with `i3`. A separate
source-hash-bound noninterference audit mutates all `i3` rows and, independently,
all test covariates/outcomes across six released seeds. The returned weights are
bit-identical in all 12 mutations, whereas a deliberately test-adaptive control
changes in 6/6 cases.

## Environment compatibility

The released requirements leave package versions unconstrained. Its Parkinson
loader standardizes a slice of integer-backed Pandas columns in place. That
assignment is accepted by Pandas 2 but raises a `TypeError` in Pandas 3, before
any estimator is run. The reproduction therefore pins `pandas==2.3.3`; this
restores the source's intended behavior without modifying author code. The
CCP wrapper also enters the released `e-ccp/` working directory before loading
the bundled relative-path datasets, while keeping all generated outputs outside
the vendored source tree. Because the complete CCP protocol has 11,700 cells,
the CCP wrapper atomically checkpoints after each complete 39-cell seed and the
CA wrapper does the same after each complete 24-cell seed. Both fail closed on
missing, duplicate, non-finite, or out-of-scope cells before resuming. This
changes only orchestration and failure recovery; it does not alter the released
estimators, data, folds, models, methods, or seeds. Final dataset JSON is also
written atomically and structurally revalidated before reuse. The independent
CA and CCP aggregators separately reject protocol drift, missing, duplicate,
unexpected, and non-finite raw cells.

A line-by-line audit of the CCP wrapper against `e-ccp/main.py` confirms the
released split (`default_rng(seed)`, train sample without replacement, sorted
complement test set), seeds 45–144, three model calls, 300-point grid, 13
reported methods, and per-test aggregation. It also identifies one material
source/paper drift: the paper defines its third classical calibrator as
`F3(p)=2(1-p)`, whereas `e-ccp/eccp_utils.py` names the corresponding output
`int_cc_eval_pow` and computes `5(1-p)^4`. Treating that output as the paper's
linear baseline would be incorrect. The wrapper therefore leaves every author
estimator and returned foldwise p-value untouched, replays the identical local
randomization stream, and reconstructs only the paper-specified F3 intervals
as `ECCP(linear)`. A dedicated numerical test verifies the reconstruction and
proves it differs from the released power expression. The wrapper deliberately
uses the same `numpy.nanmean` aggregation as the released driver; interval
counts are checked before aggregation and any non-finite seed summary is
rejected before checkpoint promotion. A fake-source execution test exercises
this behavior.

## Exact vectorized CCP adapter

The literal released functions perform deterministic p/e aggregation in a
Python loop over every candidate-grid/test-point pair. A measured Parkinson-
shaped microkernel (`K=20`, 300 grid points) took about `0.32 s` for ten test
points versus `0.012 s` when vectorized, a roughly `27x` local speedup. Extrapolating only
that loop (not model fitting) across 2,875 Parkinson test points, three models,
and 100 seeds gives roughly `7.7` literal CPU-hours versus `0.28` vectorized
CPU-hours. This is a calibrator-kernel projection, not an end-to-end runtime
claim; model fitting and interval extraction are excluded.

The full runner therefore uses the named
`vectorized-exact-postprocessing-v1` adapter. It reproduces the source fold
permutation, OLS/RF/Lasso fits, candidate grid, foldwise p-values, and RNG
draws, then evaluates the same deterministic aggregation formulas with NumPy
arrays. Parallel seeds were rejected because the released random forest
already uses all local cores; that route would oversubscribe the host and raise
RAM risk. The largest Parkinson p-value tensor is about 138 MB, and temporary
calibrator arrays are evaluated one at a time.

A dedicated parity test executes both literal and vectorized paths for OLS,
RF, and Lasso. It requires bit-identical grids and foldwise p-values and exact
interval equality for all 13 published method cells, including the separately
audited paper-linear F3 reconstruction. The protocol records the adapter name,
and the final publication gate rejects output missing that provenance.
