# Source audit

The repository is author-owned and describes itself as the ICML 2026
reproduction package. Its `e-ca/` implementation has the four exact OpenML
task IDs, 20 fixed seeds, alpha `.05`, seven base models, `M=512`, and `B=500`
used for the conformal-aggregation study. Its `e-ccp/` tree contains the
Boston, Abalone, and Parkinson/UPDRS inputs plus the 100-seed cross-conformal
driver.

The paper specifies `K=15` for Boston/Abalone and `K=20` for Parkinson in its
reported CCP tables. The upstream driver exposes `K` as a local constant, so
the reproduction runner will pass those values explicitly rather than silently
using its default of five folds. This is a transparent protocol completion, not
a change to the P2E method.

The independent verifier will not import the upstream P2E helper: it will
construct the finite rank distribution and P2E threshold separately, recompute
the e-value expectation and p/e set equality, and reconstruct coverage and
length summaries from raw output rows.

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

A line-by-line parity audit of the CCP wrapper against `e-ccp/main.py` confirms
the released split (`default_rng(seed)`, train sample without replacement,
sorted complement test set), seeds 45–144, three model calls, 300-point grid,
13 interval keys, and per-test aggregation. The wrapper deliberately uses the
same `numpy.nanmean` aggregation as the released driver; interval counts are
checked before aggregation and any non-finite seed summary is rejected before
checkpoint promotion. A fake-source execution test exercises this behavior.
