# Claim 2 source audit

Retrieved on 2026-07-25 with an explicit `OpenResearch-Reproduction/1.0`
browser User-Agent.

- Paper source: `https://export.arxiv.org/e-print/2606.03600v1`
- Source archive SHA-256:
  `f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db`
- `main.tex` SHA-256:
  `49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857`
- Definition anchor: Section `sec:ptoe_cp`, `main.tex` lines 342–362.
- Proposition anchor: `prop:only_aon_set_preserving`, lines 372–375.
- Integral characterization: `prop:ptoe_carac`, lines 1165–1173.
- Proof anchor: “Proof of Proposition
  `prop:only_aon_set_preserving`”, lines 1182–1226.

The printed domain is `[0,1]`, the codomain includes infinity, and the
proposition quantifies over all left-continuous p-to-e calibrators. The proof
derives equality with AoN only on `(0,alpha]` and `(alpha,1]`; it does not
constrain the value at zero before concluding whole-domain equality.

Primary reference cross-check:

- Vladimir Vovk and Ruodu Wang, “E-values: Calibration, combination, and
  applications”, DOI `10.1214/20-AOS2020`.
- Accepted manuscript:
  `https://pure.royalholloway.ac.uk/ws/portalfiles/portal/39179068/Accepted_Manuscript.pdf`
- Retrieved 2026-07-25; SHA-256
  `59a4d93c7465d0acaee06a0d30b5b7d9a95bf999579685502245c69632244a9e`.
- Proposition 2.1, PDF pages 3–4, characterizes decreasing
  `f:[0,1]->[0,infinity]` as a calibrator iff its integral is at most one.
  It explicitly permits—and for admissibility requires—`f(0)=infinity`, and
  says upper semicontinuity is equivalent to left-continuity in this class.

These anchors make the endpoint a stated part of the domain, not an
out-of-assumption construction.
