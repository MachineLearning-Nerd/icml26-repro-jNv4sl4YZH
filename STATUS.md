# Status

Audit date: 2026-08-14

Paper: *Set-Preserving Calibration from Conformal P-Values to E-Values*

OpenReview: `jNv4sl4YZH`
ArXiv: [`2606.03600`](https://arxiv.org/abs/2606.03600)

## Evidence verdict

| Item | Current status |
| --- | --- |
| C1 set preservation | VERIFIED — 18 theorem-domain cells and source cross-check |
| C2 AoN uniqueness | FALSIFIED literally on `[0,1]`; corrected statement on `(0,1]` verified |
| C3 sigmoid properties | VERIFIED — 18 analytic cases; full CCP AoN comparison 9/9 |
| C4 ECCP validity | VERIFIED — arbitrary-dependence and exchangeable certificates; 11,700 CCP rows |
| C5 WECA validity | VERIFIED — split noninterference and 1,920 CA rows |
| C6 efficiency | VERIFIED — 24/24 CA and 36/36 CCP comparisons |

This is an evidence report, not a challenge-score claim. The repository keeps
the failed literal claim visible rather than converting it into a pass because
the downstream conformal application remains operationally useful.

## Pinned inputs

- Official implementation: [`Nabil-Ala/P2E_calibration`](https://github.com/Nabil-Ala/P2E_calibration) at commit `66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974`.
- Paper source archive: `sources/arxiv-v1/source.tar.gz`, SHA-256 `f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db`.
- Primary TeX: `sources/arxiv-v1/main.tex`, SHA-256 `49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857`.
- Paper PDF: `sources/arxiv-v1/paper.pdf`, SHA-256 `702dbea68adb646d41255420c67122b63f879c66b333684f904fc39d11c718e2`.
- CA tasks: OpenML IDs `361234`, `361235`, `361237`, and `361244`; four tasks × 20 seeds.
- CCP data: bundled Boston, Abalone, and Parkinson/UPDRS CSVs; three datasets × 100 seeds × three models × 13 methods.

## Evidence accounting

- C1: 18 finite-rank cases, five excluded-domain controls, and maximum exact-e expectation error `4.44e-16`.
- C2: symbolic endpoint witness valid for every `alpha ∈ (0,1)`; the operational correction is equality with AoN on `(0,1]` only.
- C3: 18 exactness/positivity/smoothness/inverse/dominance cases and 36 full CCP efficiency comparisons.
- C4: eight arbitrary-dependence e-merge cases, five exchangeable-prefix cases, and 9/9 empirical ECCP coverage cells.
- C5: six source-level noninterference mutations, 8/8 empirical CA coverage cells, and 1,920 verified rows.
- C6: 24/24 CA wins, 36/36 CCP wins, 122 paper cells / 488 scalars compared, 94 unaffected cells passing, one exact CA dispersion discrepancy disclosed, and 27 source-discrepant CCP cells classified.

The released CCP implementation places the paper’s F1/F2/F3 formulas and
reported columns differently: the paper states log/square-root/linear while
the released driver supplies square-root/log/power. The audit preserves the
released output, binds both implementations by hash, and replays the
reversible log/square-root swap across 72 scalars. It never relabels the
power-calibrator result as the paper’s linear result.

## Local publication gate

Run:

```bash
uv sync --frozen
uv run python repro/src/publication_gate.py --skip-producers
```

The gate writes `outputs/publication_gate.json` only after it verifies the
checked-in evidence. It is intentionally local-only: no hidden metadata,
Trackio logbook, Hugging Face publisher, or external write is required. The
official source checkout is ignored under `upstream/` and is hash-checked when
source-dependent commands are run.

## Known limitations

The complete author protocol reuses immutable released rows for the final
aggregation checks rather than retraining every author estimator. The coverage
means and across-seed intervals are descriptive; exact validity comes from the
e-value certificates and their stated assumptions. OpenML availability can
change, so fresh runs should record the content hashes and fail closed when a
task cannot be retrieved.

## History

The original working tree used `orx/*` branches and a Trackio/Hugging Face
publication handoff. Those branches preserve experiment history, but the
canonical public collection uses descriptive `baseline/*`, `audit/*`, and
`release/*` names. The old private publication machinery is removed from the
canonical tree; `space_release/` remains only as an archived evaluator-visible
snapshot.
