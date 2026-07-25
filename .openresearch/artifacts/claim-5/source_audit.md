# Claim 5 source audit

- Paper source: `https://export.arxiv.org/e-print/2606.03600v1`
- Retrieved 2026-07-25 with explicit User-Agent.
- Archive SHA-256:
  `f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db`
- `main.tex` SHA-256:
  `49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857`
- WECA construction and split: lines 704–745, Equation `WECA`.
- Coverage proposition: lines 735–741.
- Proof: Appendix subsection “Theoretical Validity of WECA”.

Released implementation:

- `Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974`
- Function `Evalue_aggregation_weighted`, lines 388–509.
- Function-block SHA-256:
  `541a30601a5346d0adbcf50bb9dcfd2e5e8317f7403fb4540516680a52751bfb`.

The weights are genuinely data-dependent: they are optimized from a tuning
split. The validity condition is not “fixed weights”; it is conditional
independence from the inference e-values and test point.
