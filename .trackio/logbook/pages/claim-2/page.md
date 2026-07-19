# Claim 2


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_1779c7b2f04a", "created_at": "2026-07-18T12:24:39+00:00", "title": "Full protocol queued"}
-->
**Initial execution plan (2026-07-18; historical):** the full conformal-aggregation run was configured for all four released OpenML tasks, all 20 author seeds, `alpha=.05`, seven base regressors, `M=512`, and `B=500`. Its source runner writes raw per-task records; an independent summarizer recomputes coverage and length without importing the author aggregation functions. The authoritative outcome is the later **Claim 2 verdict** cell, which the final gate derives from exactly 1,920 verified raw cells.
