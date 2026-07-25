# Method

The clean-room verifier constructs the finite rank distribution and sigmoid
without importing the author helper. It tests 18 `(n, alpha)` cells up to
`n=200`, verifies exact membership and threshold identities, expectation one,
and positivity. A second route invokes the hash-pinned author source over the
same cells. The independent release checker consumes both outputs and fails
closed on missing cells, any membership mismatch, expectation failure, missing
controls, or domain drift.
