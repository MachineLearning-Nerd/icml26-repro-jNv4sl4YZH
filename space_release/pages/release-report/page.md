# Release report

- Previous live judged score: `7/12`
- Conservative projected score range after the proposed change: `9–12/12`
- Best-supported possible new score: `12/12` **forecast; not a judge result**

| Claim | Current points | Possible points | Confidence | Evidence status | Basis and remaining risk |
| --- | ---: | ---: | --- | --- | --- |
| 1 | 2 | 2 | HIGH | VERIFIED | Existing full credit retained; clean-room and source rerun both exact. |
| 2 | 0 | 2 | MEDIUM | FALSIFIED | Literal endpoint witness is proof-level; risk is reviewer silently reading equality only on `(0,1]`. |
| 3 | 1 | 2 | HIGH | VERIFIED | Every analytic component plus 9/9 full-scale AoN comparisons. |
| 4 | 1 | 2 | MEDIUM | VERIFIED | Universal e-variable proof is direct; empirical Parkinson-RF interval remains below nominal. |
| 5 | 1 | 2 | HIGH | VERIFIED | Conditional proof, source independence audit, full protocol, and failing adaptive control. |
| 6 | 2 | 2 | HIGH | VERIFIED | Existing full credit retained and strengthened with direct 36/36 ECCP comparison. |

Current total score: **7/12**, unchanged until the live judge records a new
verdict. Claims 2–5 changed scientifically since the judged revision. No claim
is BLOCKED.

Exact publication action: upload the SHA-256 allowlisted text files in this
candidate to the existing Space `DineshAI/jNv4sl4YZH`; do not create another
Space. Then download the exact published revision, verify every hash, repeat
the canonical traversal, mark the paper awaiting judge, and fast-forward the
public GitHub `main` branch to the identical release content.

## Compute and provenance

All formal work used Hugging Face `cpu-upgrade`, never GPU. The cumulative
science release run is `1811c6e7-901f-4cb1-9a24-0ea0891b8717` at Git SHA
`23c37c41627a5d2e4f55553726a8af2a8f1b97ba`, estimate 8 useful CPU cores,
actual allocation 64 CPUs, campaign runtime `76.700822` seconds.
The exact command was `uv run --frozen python repro/src/run_campaign.py`.

The judged Space revision and its historical 23-file tree were downloaded
before modification. The old path set remains a subset of the new tree; the
old claim pages and static assets remain unchanged. Only README/navigation
metadata is superseded, with exact originals copied under
`evidence/historical/judged-7f87ab976b2ab93d25dbc77586cbff61c4746f1e/`.
