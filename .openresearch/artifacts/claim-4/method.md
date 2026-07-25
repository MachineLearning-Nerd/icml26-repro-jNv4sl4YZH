# Method

The universal certificate reconstructs the proof:

1. Exchangeability makes each fold P2E output a valid e-variable.
2. Linearity gives `E[sum E_k/K] <= 1` under arbitrary fold dependence.
3. Randomized Markov bounds ECCP miscoverage by `alpha`.
4. The two prefix variants invoke the stated exchangeable e-merging result.

This derivation—not the finite LP cases—carries the universal quantifier.
Exact enumerations independently exercise arbitrary dependence, randomized
thresholding, and exchangeable prefixes.

The full empirical protocol independently aggregates 11,700 raw cells:
three datasets, three regressors, 13 methods, and seeds 45–144. Nine ECCP
dataset-model coverage means are reported with standard deviations and
descriptive 95% intervals.

Controls scale an e-value beyond its expectation budget and apply prefix
merging without exchangeability; each is rejected.
