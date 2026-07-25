# Claim 3 source audit

Primary source retrieved 2026-07-25 with an explicit browser User-Agent:

- `https://export.arxiv.org/e-print/2606.03600v1`
- Archive SHA-256:
  `f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db`
- `main.tex` SHA-256:
  `49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857`
- Theorem `main_theorem`, Equation `final_evalue`: lines 479–495.
- Aggregation inclusion `equation:FAon_larger`: lines 504–514.
- Analytic proof: appendix subsection “Proof of Theorem
  `main_theorem`”.

The exact assumptions are `alpha(n+1)>1`, non-integral `alpha(n+1)`, and
`alpha < s < ceil(alpha(n+1))/(n+1)`. The theorem states pointwise
`F_{n,alpha} >= F_AoN`; summation yields a non-strict prediction-set subset.
The paper’s prose “always more efficient” must therefore be calibrated:
strict pointwise dominance holds except at `p=alpha`, but a universally strict
set-size reduction does not follow. Strict set reduction is separately tested
against AoN in the full released experiment.
