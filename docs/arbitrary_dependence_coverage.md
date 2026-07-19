# Arbitrary-dependence coverage control

A fixed weighted mean of valid e-values remains an e-value without requiring
independence. This includes the equal-weight ECCP merge and the
tuning-independent nonuniform weights used by WECA. The paper's ECCP and
UR-WECA sets additionally use an independent `U ~ Uniform(0,1)` threshold:
conditional failure probability for a merged value `e` is
`min(alpha * e, 1)`. To test both mechanisms computationally rather than assume
an independent product distribution,
`repro/src/verify_e_merge_coverage.py` solves a finite coupling problem for
each rank configuration.

This matches the paper's Proposition 4.1 scope: ECCP is stated to retain its
finite-sample coverage guarantee under arbitrary dependence among fold-wise
p-values. Primary source: <https://arxiv.org/html/2606.03600v1>.

For every tuple of conformal ranks, the script evaluates both the deterministic
failure indicator at `1 / alpha` and the exact randomized failure cost
`min(alpha * e, 1)`. It then uses sparse linear programs to maximize each total
failure mass over **all** joint distributions whose marginal rank distribution
in every fold is uniform. Thus, the optimized results include arbitrary
positive or negative dependence between folds. A valid case passes only when
both worst-case failure probabilities are no greater than `alpha`.

| Calibration n | alpha | Fixed weights | LP variables | Valid det./rand. | Invalid 2x det./rand. | Adaptive max det./rand. |
|---:|---:|---|---:|---:|---:|---:|
| 10 | 0.1 | .50, .50 (ECCP) | 121 | .090909 / .100000 | .181818 / .194544 | .181818 / .194544 |
| 10 | 0.1 | 1/3, 1/3, 1/3 (ECCP) | 1,331 | .090909 / .100000 | .136364 / .200000 | .272727 / .291816 |
| 10 | 0.1 | .25, .75 | 121 | .090909 / .100000 | .090909 / .150454 | .181818 / .194544 |
| 10 | 0.1 | .10, .30, .60 | 1,331 | .090909 / .100000 | .090909 / .178545 | .272727 / .291816 |
| 10 | 0.1 | .05, .15, .30, .50 | 14,641 | .090909 / .100000 | .181818 / .197272 | .363636 / .389070 |
| 20 | 0.1 | .20, .80 | 441 | .095238 / .100000 | .095238 / .138286 | .190476 / .194286 |
| 20 | 0.1 | .10, .20, .70 | 9,261 | .095238 / .100000 | .095238 / .157905 | .285714 / .291429 |
| 20 | 0.2 | .15, .35, .50 | 9,261 | .190476 / .200000 | .380952 / .392466 | .571429 / .577397 |

All eight valid coupling optima—two equal-weight ECCP cases and six
nonuniform tuning-independent WECA cases—satisfy both the deterministic and
paper-exact randomized-uniform bounds. The worst randomized failure equals but
never exceeds `alpha`, as predicted by randomized Markov.
Doubling every e-value is an invalid construction, but is still accidentally
conservative for four weight configurations; it violates the bound in 4/8 LP
cases and 2/8 independent-product cases. Under the randomized rule, the same
invalid scaling violates the adversarial bound in 8/8 cases. The decisive control
instead chooses a one-hot weight on the largest e-value *after observing the
inference tuple*. That forbidden outcome-adaptive weighting violates the bound
in all 8/8 cases under both rules, with minimum worst-case tail/alpha ratios
`1.818` (deterministic) and `1.943` (randomized).
This cleanly isolates why WECA's weights must come from its independent tuning
split. The complementary source-bound audit
`repro/src/verify_weca_independence.py` pins the released `methods.py` and WECA
function hashes, confirms the three calibration partitions are disjoint, and
reruns the routine across six released seeds. Replacing every final-calibration
row or every test covariate/outcome leaves each selected weight bit-identical;
a deliberately forbidden test-outcome-adaptive rule changes in all six cases.
This is a finite mechanism audit; the separate full
Boston/Abalone/Parkinson source run remains required for the empirical claim.
