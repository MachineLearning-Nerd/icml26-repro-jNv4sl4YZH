# EVAL

Verdict: **VERIFIED**

- Analytic theorem-domain cases: 18/18 passed.
- Exact expectations: all absolute errors below `1e-11`.
- Smoothness/strict monotonicity, inverse, and positivity: 18/18 passed.
- Direct full-scale P2E vs AoN: strictly shorter in 9/9 comparisons.
- Minimum observed relative reduction vs AoN: `0.0017866878` (0.179%).
- Full protocol: 11,700 raw rows, 3 datasets, 3 models, 100 seeds.
- Negative controls: all rejected for intended reasons.
- Independent checker: PASS.

The strict 9/9 result is empirical. The theorem-level prediction-set result is
the non-strict inclusion `C_P2E subseteq C_AoN`.
