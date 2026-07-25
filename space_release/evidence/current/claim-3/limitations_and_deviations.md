# Limitations and deviations

- Numerical cases regression-test the analytic proof; they are not used to
  infer universal smoothness or invertibility.
- Direct AoN comparisons cover the complete released CCP experiment but do
  not imply strict reduction for every possible dataset.
- The smallest observed AoN reduction is 0.179%, so “strict” should not be
  paraphrased as “substantial” for this baseline.
- The historical author raw data is reused exactly and independently
  re-aggregated; expensive training is not rerun because the immutable
  11,700-cell evidence is hash-bound and already complete.
