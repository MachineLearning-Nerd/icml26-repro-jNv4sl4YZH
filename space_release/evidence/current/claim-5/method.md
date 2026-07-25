# Method

The proof certificate conditions on the learned tuning weights:

```text
E[sum_k omega*_k E_k | omega*]
  = sum_k omega*_k E[E_k | omega*]
  <= sum_k omega*_k
  = 1.
```

Thus the weighted sum is an e-variable even if inference e-values are mutually
dependent. Markov and randomized Markov give WECA and UR-WECA coverage.

The source-bound implementation audit runs six distinct seeds. It verifies
disjoint splits, nonuniform tuning-dependent weights, zero weight change
after inference/test mutations, and a change under a deliberately forbidden
test-adaptive rule.

The empirical arm independently re-aggregates all 1,920 released cells:
four OpenML tasks, 20 seeds, `M=512`, and `B=500`. It reports WECA(P2E) and
UR-WECA(P2E) coverage means, standard deviations, and descriptive intervals.

Exact controls show illegal adaptive weights exceed the alpha tail budget by
at least 1.818× (deterministic) and 1.943× (randomized).
