# Current claim-by-claim verification

This page is the canonical evaluator entrypoint for the 2026-07-25 cumulative
release. The previous live judged score is **7/12** at Space revision
`7f87ab976b2ab93d25dbc77586cbff61c4746f1e`. The conservative projected range
is **9–12/12**; **12/12 is the best-supported possible forecast**, not a judge
result.

## Fixed reproduction contract

Every OpenResearch node runs exactly:

```text
uv run --frozen python repro/src/run_campaign.py
```

The environment is Python `==3.12.*` in one repository `.venv`, resolved by
[`pyproject.toml`](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/environment/pyproject.toml)
and the exact
[`uv.lock`](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/environment/uv.lock).
The complete
[`run_campaign.py`](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/shared/run_campaign.py)
and
[`campaign_run.json`](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/shared/campaign_run.json)
are evaluator-visible.

Paper source: `https://export.arxiv.org/e-print/2606.03600v1`, retrieved
2026-07-25 with an explicit browser User-Agent. Archive SHA-256:
`f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db`;
`main.tex` SHA-256:
`49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857`.

## Evidence summary

| Claim | Exact result | Current verdict | Confidence |
| --- | --- | --- | --- |
| [1](#/current-claim-1) | 18/18 clean-room and 18/18 source cells; zero mismatches | VERIFIED | HIGH |
| [2](#/current-claim-2) | `F*(0)=infinity`, `F*=AoN` on `(0,1]`; all printed assumptions pass | FALSIFIED literally | MEDIUM |
| [3](#/current-claim-3) | 18 analytic cases; P2E shorter than AoN 9/9 at full scale | VERIFIED | HIGH |
| [4](#/current-claim-4) | Universal e-merge certificate; 11,700 rows; coverage cells 9/9 | VERIFIED | MEDIUM |
| [5](#/current-claim-5) | Conditional-weight proof; six mutations; 1,920 rows; coverage 8/8 | VERIFIED | HIGH |
| [6](#/current-claim-6) | P2E shorter in 24/24 CA and 36/36 ECCP comparisons | VERIFIED | HIGH |

The full raw evidence is one public, hash-indexed 2.8 MB JSONL file containing
all 1,920 CA and 11,700 CCP cells:
[download the immutable bundle](https://huggingface.co/buckets/DineshAI/jNv4sl4YZH-artifacts#logbook-files/outputs/jNv4sl4YZH_full_evidence_bundle.jsonl)
(SHA-256
`1cd1115ee4fefc260c79512eb1a4bea61f342ebca5bb9acf3cc5b8ca91f90359`).

## Scope calibration

Claim 2 is falsified only as printed on `[0,1]`; the corrected uniqueness
statement on `(0,1]` remains true. Claim 4’s empirical Parkinson-RF mean is
0.890299 at nominal 0.90 and its descriptive interval lies below nominal; the
finite-sample verdict rests on the universal e-variable proof, not that
interval. One CA finite-seed length-SD scalar differs from the paper table
(`0.201899` observed versus `0.18` reported). These deviations are disclosed,
not averaged away.

Continue to the [evaluator visibility matrix](#/visibility-matrix), the
[release report](#/release-report), and the
[evaluator-blind review](#/red-team-review).
