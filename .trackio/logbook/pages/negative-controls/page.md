# Negative controls


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_8c12c27b75d2", "created_at": "2026-07-18T12:24:41+00:00", "title": "C1 controls"}
-->
Classic p-to-e calibrators `-log(p)`, `p^-1/2 - 1`, and `2(1-p)` inflate the conformal set in every eligible finite-rank control. The one ineligible control has no rank at or below alpha, so the original p-set is already the full rank support and cannot be enlarged. The author floating-point implementation underflows some extremely small already-excluded e-values at `n>=100`; threshold membership and the exact expectation remain correct, and the clean-room verifier records finite log-e values.
