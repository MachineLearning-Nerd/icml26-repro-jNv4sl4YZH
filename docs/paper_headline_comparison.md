# Paper headline comparison

This project preserves a machine-readable transcription of every CA P2E row,
every CA log/square-root/linear comparator row used by Claim 2, and every
tabulated CCP row needed to cross-check the full source runs against the paper.
The values are transcribed from arXiv `2606.03600v1`, Table 2, the CA
alternative-calibrator table, and Appendix Tables 6–8 into
`repro/configs/paper_headlines.json`.

`repro/src/verify_paper_table_fixture.py` independently downloads the fixed
arXiv v1 source, checks its archive and `main.tex` hashes, parses all 122 cells,
and requires exact equality for every one of the 488 configured scalars. The
paper source itself is never copied into this repository or evidence bundle.

The transcription was rechecked against the primary arXiv v1 HTML on
2026-07-19. Table 2 reports the four WECA(P2E) and four UR-WECA(P2E) CA cells;
the adjacent alternative-calibrator table reports 24 matched F1/log,
F2/square-root, and F3/linear cells; Appendix Tables 6, 7, and 8 report the
Boston, Abalone, and Parkinson
length/coverage cells for OLS, RF, and Lasso. Both panels are transcribed:
CCP/e-mod/u-mod/eu-mod/ECCP(2alpha), plus P2E ECCP/AoN/F1/F2/F3. The paper also states that ECCP
is valid under arbitrary dependence among fold-wise p-values, which is the
scope targeted by `docs/arbitrary_dependence_coverage.md`.

Primary source: <https://arxiv.org/html/2606.03600v1>

The comparison is deliberately separate from claim verification:

- raw-row completeness, coverage, length, and negative controls determine
  whether the reproduction supports a claim;
- headline deltas diagnose environment, data, or source-version drift;
- a value outside the documented tolerance is reported rather than rounded or
  normalized to make it resemble the paper.

The mean gate was predeclared before the remaining source results were
available: absolute mean-coverage drift must be at most `0.01`, and relative
mean-length drift must be at most `5%`. These limits comfortably contain the
already-complete CA cells (maximum `0.004` coverage and `0.22%` relative
length) while rejecting a materially different empirical result. On
2026-07-19, after three CA tasks but before the final CA task and every CCP
result, the audit was strengthened to include the paper's reported standard
deviations: absolute coverage-SD drift must be at most `0.01`, and relative
length-SD drift must be at most `10%`.

The CA comparison covers the paper's reported WECA and UR-WECA P2E, log,
square-root, and linear rows across all four OpenML task IDs. The CCP
comparison covers all ten methods
tabulated for OLS, RF, and Lasso on Boston, Abalone, and Parkinson at the
reported 15/15/20 fold counts. In total, the fail-closed comparison checks all
four reported scalars (coverage mean/SD and length mean/SD) in 122 cells:
488 scalar comparisons. All 32 CA cells and all 90 CCP cells were parsed back
from the primary arXiv TeX and matched field-for-field before the final CA task
or any CCP result existed.

Separately, the raw CA/CCP verifiers apply a fixed two-percentage-point
gross-undercoverage sanity threshold to all eight P2E aggregation cells and all
27 ECCP/ECCP-Exch/UR-ECCP-Exch cells. This empirical tolerance was fixed before the final CA task
and every CCP result existed. It does not establish the word "exact"; the
finite-rank enumeration and arbitrary-dependence LP provide that mechanism
certificate.
