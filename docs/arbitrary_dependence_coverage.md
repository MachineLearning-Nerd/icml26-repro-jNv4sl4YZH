# Arbitrary-dependence coverage control

A fixed weighted mean of valid e-values remains an e-value without requiring
independence. This includes the equal-weight ECCP merge and the
tuning-independent nonuniform weights used by WECA. To test that mechanism
computationally rather than assume an independent product distribution,
`repro/src/verify_e_merge_coverage.py` solves a finite coupling problem for
each rank configuration.

This matches the paper's Proposition 4.1 scope: ECCP is stated to retain its
finite-sample coverage guarantee under arbitrary dependence among fold-wise
p-values. Primary source: <https://arxiv.org/html/2606.03600v1>.

For every tuple of conformal ranks, the script marks whether the merged e-value
crosses `1 / alpha`. It then uses a sparse linear program to maximize the total
failure mass over **all** joint distributions whose marginal rank distribution
in every fold is uniform. Thus, the optimized result includes arbitrary positive
or negative dependence between folds. A valid case passes only when this
worst-case tail probability is no greater than `alpha`.

| Calibration n | alpha | Fixed weights | Coupling variables | Valid tail | Invalid 2x tail | Adaptive-max tail |
|---:|---:|---|---:|---:|---:|---:|
| 10 | 0.1 | .50, .50 (ECCP) | 121 | 0.090909 | 0.181818 | 0.181818 |
| 10 | 0.1 | 1/3, 1/3, 1/3 (ECCP) | 1,331 | 0.090909 | 0.181818 | 0.272727 |
| 10 | 0.1 | .25, .75 | 121 | 0.090909 | 0.090909 | 0.181818 |
| 10 | 0.1 | .10, .30, .60 | 1,331 | 0.090909 | 0.090909 | 0.272727 |
| 10 | 0.1 | .05, .15, .30, .50 | 14,641 | 0.090909 | 0.181818 | 0.363636 |
| 20 | 0.1 | .20, .80 | 441 | 0.095238 | 0.095238 | 0.190476 |
| 20 | 0.1 | .10, .20, .70 | 9,261 | 0.095238 | 0.095238 | 0.285714 |
| 20 | 0.2 | .15, .35, .50 | 9,261 | 0.190476 | 0.380952 | 0.571429 |

All eight valid coupling optima—two equal-weight ECCP cases and six
nonuniform tuning-independent WECA cases—satisfy the required tail bound.
Doubling every e-value is an invalid construction, but is still accidentally
conservative for four weight configurations; it violates the bound in 4/8 LP
cases and 2/8 independent-product cases. The decisive control
instead chooses a one-hot weight on the largest e-value *after observing the
inference tuple*. That forbidden outcome-adaptive weighting violates the bound
in all 8/8 cases, with worst-case tail/alpha ratios from `1.818` to `3.636`.
This cleanly isolates why WECA's weights must come from its independent tuning
split. The complementary source-bound audit
`repro/src/verify_weca_independence.py` pins the released `methods.py` and WECA
function hashes, confirms the three calibration partitions are disjoint, and
reruns the routine across six released seeds. Replacing every final-calibration
row or every test covariate/outcome leaves each selected weight bit-identical;
a deliberately forbidden test-outcome-adaptive rule changes in all six cases.
This is a finite mechanism audit; the separate full
Boston/Abalone/Parkinson source run remains required for the empirical claim.
