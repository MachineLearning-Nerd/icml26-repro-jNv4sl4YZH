# Claim 4 source audit

- Source: `https://export.arxiv.org/e-print/2606.03600v1`
- Retrieved 2026-07-25 with explicit User-Agent.
- Archive SHA-256:
  `f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db`
- `main.tex` SHA-256:
  `49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857`
- ECCP construction: lines 646–674, equations `ECCP`, `Ex_ECCP`,
  `Ex_ECCP_U`.
- Proposition: lines 676–683, label `prop:ECCP`.
- Standard CCP comparison: equation `eq:ccpbound` and the related-work
  statement that named variants have a `1-2alpha` guarantee.

The base ECCP proposition assumes the test point is exchangeable with the
data. The two prefix variants additionally assume exchangeability of the
fold-wise e-values. The word “exact” is interpreted as the stated
finite-sample `>=1-alpha` guarantee, not equality.
