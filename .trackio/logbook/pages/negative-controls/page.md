# Negative controls


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_8c12c27b75d2", "created_at": "2026-07-18T12:24:41+00:00", "title": "C1 controls"}
-->
Classic p-to-e calibrators `-log(p)`, `p^-1/2 - 1`, and `2(1-p)` inflate the conformal set in every eligible finite-rank control. The one ineligible control has no rank at or below alpha, so the original p-set is already the full rank support and cannot be enlarged. The author floating-point implementation underflows some extremely small already-excluded e-values at `n>=100`; threshold membership and the exact expectation remain correct, and the clean-room verifier records finite log-e values.


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_bac175c387e5", "created_at": "2026-07-19T18:54:50+00:00", "title": "Final negative-control audit"}
-->
The controls fail in the intended direction. All 5 excluded theorem-domain boundary cases are rejected, and classical p-to-e calibrators inflate the conformal set in all 18 valid finite-rank cases. Invalid 2x e-value scaling violates the arbitrary-dependence deterministic bound in 4/8 cases and the randomized bound in 8/8 cases. It also violates the exchangeable ECCP-Exch and UR-ECCP-Exch orbit bounds in 5/5 and 5/5 cases. Inference-adaptive one-hot weights fail both weighted-merge bounds in 8/8 and 8/8 cases. All raw verifiers separately reject protocol drift, missing, duplicate, unexpected or non-finite cells, invalid metric ranges, and insufficient efficiency gains.
