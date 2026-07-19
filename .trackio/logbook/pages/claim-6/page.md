# Claim 6


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_df9167b71a9e", "created_at": "2026-07-19T18:54:49+00:00", "title": "Claim 6 verdict"}
-->
Claim 6 is verified at the complete released empirical scale. The CCP run contains exactly 11,700 unique finite cells (three datasets, 100 seeds, three models, 13 methods) using the parity-checked `vectorized-exact-postprocessing-v1` adapter. P2E is strictly shorter in 36/36 matched baseline comparisons: 9/9 AoN cells and 27/27 formula-faithful log, square-root, and linear calibrator cells, with every classical reduction exceeding the predeclared 10% threshold. The independent CA evidence adds 24/24 material P2E wins, ranging from 40.30% to 95.96% reduction. All 376 unaffected reported scalars across 94 paper-table cells pass the fixed drift tolerances. One additional CA cell passes coverage mean/SD and length mean but reproduces length SD as `0.201898618094345` versus the paper's rounded `0.18`; this single finite-seed dispersion scalar is explicitly disclosed and does not alter any efficiency or coverage verdict. The remaining 27 cells (108 scalars) are explicitly classified by a hash-bound audit: the paper defines F1/F2/F3 as log/square-root/linear, while the released CCP table driver fills those positions with square-root/log/power. The reversible log/square-root swap is also replayed numerically: all 72 scalars in 18 source-position cells match the paper table under the released mapping. No result is relabeled to conceal either discrepancy, and all P2E coverage checks remain valid.
