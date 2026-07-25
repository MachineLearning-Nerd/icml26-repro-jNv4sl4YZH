# Method

Define, for arbitrary fixed `alpha in (0,1)`,

```text
F*(0) = infinity
F*(p) = 1/alpha  for 0 < p <= alpha
F*(p) = 0        for alpha < p <= 1.
```

This is decreasing and left-continuous: every nonzero point has the required
left limit, including the jump at `alpha`; the left condition at the minimum
domain endpoint is vacuous. Its integral is exactly one because a single
endpoint has zero Lebesgue measure, so the cited necessary-and-sufficient
calibrator condition holds. Every conformal p-value has the form
`(1 + count)/(n+1) > 0`; consequently `F*` and AoN agree on the entire
conformal support for every `n` and every score, proving set preservation.
But `F*(0)=infinity != 1/alpha=F_AoN(0)`, contradicting literal uniqueness.

The executable verifier checks exact rational instances over seven alpha
levels and every conformal rank for `n=1,...,500` (880,250 support points).
Those checks are regression evidence only. The proof is the symbolic
measure-zero endpoint construction, so its query budget and grid are not
selected from a target formula.

An independent output checker fails closed. Three controls each break a
different premise: inflate a positive-measure interval (integral budget
failure), lower the endpoint (monotonicity failure), and shift the jump
(set-preservation failure).
