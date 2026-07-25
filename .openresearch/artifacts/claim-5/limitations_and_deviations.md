# Limitations and deviations

- Six implementation mutations are not treated as proof of a universal
  theorem; the conditional derivation carries that burden.
- The proof requires the learned weights to be independent of inference
  e-values and the test point. Test-adaptive optimization is invalid.
- The full immutable author results are independently re-aggregated rather
  than retrained.
- Coverage uncertainty is reported descriptively because seeds reuse fixed
  datasets and are not independent draws from a new-data population.
