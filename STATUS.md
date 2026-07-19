# Status

## Current step

`in_progress` — Claim 1 is complete locally. Claim 2's full released CA run is
active under Trackio: tasks `361237`, `361235`, and `361244` are complete, with
task `361234` still computing. The three completed tasks contain exactly 1,440
raw rows (20 seeds × 24 methods each), all finite and structurally complete;
their six P2E headline cells agree with the paper within `0.004` coverage and
`0.22%` relative length. P2E is shorter in all 18 completed
task/family/comparator cells versus log, square-root, and linear calibrators;
the minimum relative reduction is `87.82%`. Claim 3's full CCP runner remains
queued until CA finishes. The local Trackio logbook is structured and tagged
but unpublished.

## Pinned inputs

- Paper: arXiv `2606.03600`, OpenReview `jNv4sl4YZH`.
- Official source: `Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974`.
- Aggregation data: live OpenML task IDs `361234`, `361235`, `361237`, and
  `361244`, each queried successfully during the audit.
- CCP data: bundled Boston, Abalone, and Parkinson/UPDRS CSVs.

## Full-scope plan

1. **C1 — complete:** the clean-room finite-rank construction passed all 18
   `(n, alpha)` cells: zero p/e set mismatches, exact-e expectation error at
   most `4.45e-16`, and all eligible classic-calibrator controls inflate the
   set. A separate invocation of the pinned author implementation has the
   same 18/18 membership identities and exact expectations. The source emits
   IEEE underflowed zeros for extremely small, already-excluded e-values at
   `n>=100`; this is documented in `outputs/claim1_source_crosscheck.json` and
   does not alter the threshold decisions.
2. **C2:** run the released conformal-aggregation protocol: four datasets,
   20 fixed seeds, alpha `.05`, seven base regressors, `M=512`, `B=500`.
   Recompute coverage and length from raw source outputs independently.
3. **C3:** run paper-scale cross-conformal trials on bundled Boston, Abalone,
   and Parkinson datasets with 100 fixed seeds and the paper's reported fold
   counts; independently recompute all interval coverages/lengths and include
   nominal/invalid-calibrator controls. A separate eight-cell finite-rank
   e-merge enumeration already verifies the exact mean-one mechanism and all
   `1-alpha` Markov events. An exact sparse linear program additionally
   maximizes failure probability over every joint coupling with the required
   uniform conformal-rank marginals: all 8/8 fixed-weight worst cases remain at
   or below `alpha`, including two equal-weight ECCP and six nonuniform
   tuning-independent WECA cases. A 2x-invalid-e-value control is correctly
   reported as only 4/8 under the LP (it remains conservative in four cases),
   while forbidden outcome-adaptive max weighting violates the bound in 8/8.
   This directly checks both ECCP and WECA's independent-tuning requirement,
   but does not replace the queued empirical run.

## Publication gate

Do not publish until all source runs, independent verifiers, negative controls,
tests, headline-number comparison, and secret scan pass. The current Hugging
Face quota does not affect local implementation work. The fail-closed
`repro/src/prepublish_gate.py` now reruns every independent checker and all
tests, validates the 1,920 CA and 11,700 CCP cell sets, requires all 17 paper
headline cells within tolerance, verifies the source pin and Trackio evidence,
scans hygiene, and hashes every final artifact. It cannot pass until the full
source outputs and final Conclusion marker exist. On success it packages seven
summary/report artifacts plus all seven raw dataset files into one hash-indexed JSONL
artifact that Trackio will promote to the Hugging Face bucket.
The headline tolerances were fixed before the remaining results existed at
`0.01` absolute coverage and `5%` relative length; larger drift halts the gate.
The comparison now covers all four reported scalars in each headline cell:
coverage mean/SD and length mean/SD, for 68 checks across 17 cells. The added
SD tolerances (`0.01` absolute coverage SD and `10%` relative length SD) were
fixed after three CA tasks but before the final CA task and all CCP outputs.

## Fresh preflight — 2026-07-19

- Confirmed the vendored official source remains clean at
  `66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974`.
- Confirmed the checked-in protocol retains the paper-scale CA and CCP
  configurations described above.
- Initialized the local publication repository and committed the current
  implementation at `3143c6c` without pushing it. The complete `upstream/`
  checkout is now ignored, and the publisher preflight requires that rule, so
  Git cannot accidentally publish an unusable embedded-repository gitlink.
  `README.md` now gives the exact official clone/commit verification,
  environment installation, 1,920-cell CA, 11,700-cell CCP, independent
  verification, test, and final-gate commands for a fresh public clone.
- Read-only checks against the installed Hugging Face CLI and existing public
  challenge artifacts confirmed the publisher's Space JSON fields, tag/SHA
  checks, recursive bucket JSON fields, exact-size artifact lookup, and Space
  download options match the live CLI/API shapes.
- Re-read the live official challenge `claims.json`: it still lists exactly
  three claims (six possible points). Their exact text, direct evidence,
  independent evidence, falsifiers, and fail-closed acceptance rules are now
  pinned in `repro/configs/jury_claims.json` and
  `docs/jury_claim_evidence_matrix.md`; the publication gate enforces this
  snapshot. The claim-scope check remains part of the current `18/18` passing
  test suite.
- Tightened C2's qualitative word "substantial" into a fail-closed numerical
  rule before the final dataset exists: every one of the 24 matched P2E versus
  log/square-root/linear comparisons must reduce interval length by at least
  10%. The verifier now records per-comparison relative reductions and the
  minimum; the renderer and final gate require all 24 to pass. A dedicated
  negative test confirms that results can be shorter in 6/6 comparisons yet
  correctly fail when the reduction is only 5%. The 18 comparisons from the
  three completed real datasets currently exceed this threshold by a wide
  margin (minimum `87.82%`).
- Expanded the exact C3 mechanism suite from six nonuniform WECA cases to
  eight cases by adding explicit equal-weight two- and three-fold ECCP merges.
  All 8/8 valid arbitrary-dependence LP optima pass; outcome-adaptive weighting
  fails 8/8. A separate permutation enumeration independently matches the
  two-fold LP optimum, and malformed/negative/non-normalized weights are
  rejected. The refreshed result is captured in Trackio and closes the
  previously implicit ECCP mechanism scope.
- Added a pre-final-result empirical coverage sanity gate for both applications
  named by C3. All eight CA P2E and all nine CCP ECCP coverage means must be no
  more than two percentage points below nominal; the full gate checks exact
  cell counts before applying it. Dedicated undercoverage fixtures fail for CA
  and CCP. This is explicitly labeled a gross-undercoverage check rather than
  evidence of exactness; the exact rank/e-value and arbitrary-dependence LP
  certificate remains independently required.
- Audited Trackio `0.31.5` artifact capture: the wrapped final gate detects its
  newly written `.jsonl` bundle and registers a deduplicated local path artifact
  after the command exits. The publisher now refuses all external writes unless
  metadata contains exactly the required bundle path with the correct resolved
  local source, `dataset` type, and byte size. The later Hugging Face bucket
  readback still independently requires the public object at that exact size.
- The bundle is no longer trusted by size/hash alone. Its ordered 14-record
  manifest (seven summaries/reports plus seven full raw dataset files) is
  persisted in the gate result; every JSONL line is re-parsed and required to
  match its current source path, source SHA-256, and decoded payload immediately
  before publication. Unit controls reject both post-gate source mutation and
  an altered embedded payload.
- Exercised the actual end-to-end gate while evidence is intentionally
  incomplete. It revalidated C1 and the expanded C3 mechanism, then stopped at
  the strict CA verifier because `dataset_361234.json` is absent. It created
  neither a passing manifest nor an evidence bundle, proving the live gate
  cannot promote the current 1,440/1,920-row partial state.
- Pinned the headline policy independently inside the final gate: exactly eight
  CA and nine CCP cells from Table 2 / Appendix Tables 6-8, with coverage
  mean/SD absolute tolerances `0.01/0.01` and length mean/SD relative tolerances
  `5%/10%`. Editing the configuration cannot widen those values unnoticed.
  The comparator now aborts on any non-finite input or nonpositive paper length
  denominator; a NaN fixture is rejected rather than serialized.
- Audited the rendered logbook for stale status contradictions. Scaffold-time
  Claim 2, Claim 3, mechanism, and Conclusion cells are now explicitly dated
  historical notes and name the later evidence-derived verdict that supersedes
  them. The final Conclusion still becomes authoritative only when pinned and
  containing `FULL_GATE_READY: jNv4sl4YZH`. Trackio's agent reader confirms the
  hierarchy; 18 tests and a 63-file hygiene scan pass.
- Ran all eighteen local mechanism/protocol/author-launcher/raw-verifier and
  paper-headline drift-control tests successfully (including positive and
  deliberately incomplete raw fixtures), including local-only Trackio artifact
  path validation, and completed a scoped secret scan with no findings.
- Pin `pandas==2.3.3`: the unmodified author Parkinson loader needs Pandas 2
  compatibility for an in-place standardized-float assignment. The CCP wrapper
  enters `e-ccp/` before source loading so the released relative data paths
  resolve, while its raw evidence remains outside the vendored source tree.
  Both source wrappers now write atomic per-seed checkpoints and never promote
  a partial failed seed: 24 method cells per CA seed and 39 cells per CCP seed
  (3 models × 13 methods). Final dataset artifacts are also atomic and are
  revalidated before reuse; the author estimators and protocols are unchanged.
  The CA loader accepts all three existing 480-row final artifacts as exactly
  20 complete seeds each. Both independent raw verifiers fail closed on
  protocol drift, missing, duplicate, unexpected, or non-finite cells.
  CCP aggregation now matches the released driver's `numpy.nanmean` exactly;
  a fake-source test confirms NaN element handling, all 39 per-seed cells, and
  the interval-count/finite-summary guards before checkpoint promotion.
- The author CA loader fetched all four released OpenML task IDs through the
  pinned environment (1,030×8; 1,503×5; 1,066×2; and 4,177×7 retained numeric
  rows respectively). It is therefore ready for the actual 4×20-seed sweep.
- `repro/src/compare_paper_headlines.py` will compare the independently
  summarized raw results to the 8 reported CA P2E cells and 9 reported CCP
  ECCP cells transcribed from the paper, checking all 68 mean/SD scalars and
  explicitly reporting any drift.
- The serialized handoff launched Claim 2 after the unrelated shared sweep
  completed. Three of four CA tasks are now complete; do not start the CCP
  sweep until the final CA task and its independent verifier finish. A second
  durable one-shot handoff waits for all three CCP final artifacts, then runs
  the strict 11,700-cell verifier, all 68 scalar paper-headline checks, the
  arbitrary-dependence LP, evidence-derived final Trackio cells, and the
  fail-closed publication gate. After—and only after—that gate succeeds, the
  final step creates/pushes the public GitHub repository and publishes the
  Trackio Space. It then requires public Space/tag/SHA readback, the final
  Conclusion marker, and an exact-size evidence bundle in the Trackio bucket.
  Trackio's required local `abs_path` mapping is validated but its metadata
  file is gitignored, preventing that local-only path from entering GitHub.
- At `2026-07-19 12:28 IST`, the legacy (pre-checkpoint-patch) active process
  for final task `361234` remained healthy at about `97.1%` CPU, `190 MB` RSS,
  and zero swap. Its larger `4,177 x 7` retained input explains why it is much
  slower than the three completed `1,030`- to `1,503`-row tasks. The exact-PID
  continuation guard and both serialized handoffs remain alive. The required
  Python 3.12 environment was re-entered, the publication shell scripts passed
  syntax/preflight checks, and all `18/18` tests passed again.
- At `2026-07-19 13:12 IST`, the CA-to-CCP transition was made fail-closed at
  commit `9bd602d`. The durable handoff now requires the exact 1,920-cell set,
  zero structural errors, all 24/24 comparisons above the predeclared 10%
  efficiency threshold, and all 8/8 P2E coverage cells within the predeclared
  0.02 shortfall tolerance before it can start the 11,700-cell CCP sweep. The
  full 18-test suite and shell syntax check pass. The legacy CA process was not
  interrupted; only its idle old handoff was replaced by the stricter durable
  handoff (PID `3482976`).
- From `2026-07-19 15:39–16:56 IST`, repeated 50-second liveness samples
  observed the final `361234` task gain essentially one CPU-second per
  wall-second on every interval. At the final sample it had accumulated
  `20:28:03` of CPU time over `20:57:24` elapsed, RSS remained within
  `192–194 MB`, and process swap remained zero. The worker, exact-PID
  continuation guard, strict CA-to-CCP handoff, and post-CCP gate watcher all
  remain alive, with empty error logs. The complete `18/18` test suite and
  non-writing publication preflight also pass. No fourth artifact has been
  promoted yet; this is a long but demonstrably active finite source
  computation, not a stalled process.
- At `2026-07-19 18:31 IST`, the final CA task remained compute-active at
  `97.7%` CPU with `22:02:38` accumulated CPU time, `193,636 kB` RSS, and zero
  process swap. The three completed dataset artifacts remain unchanged and no
  incomplete fourth artifact has been promoted. The strict CA-to-CCP and
  post-CCP watchers remain alive.
- The gate-complete publication handoff is now durable. After the existing
  fail-closed gate and `FULL_GATE_READY: jNv4sl4YZH` marker pass, the publisher
  revalidates both proofs and atomically/idempotently appends this paper to the
  canonical shared Hugging Face backlog. It no longer races the single shared
  drain worker for a Space-creation slot; it waits for that worker and then
  performs the existing public Space/tag/SHA/artifact readback. An attempted
  enqueue against the current incomplete state is rejected without modifying
  the backlog. Paper commit: `0ff983a`; control-plane helper commit: `e63646c`.
- At `2026-07-19 18:44 IST`, the CA-to-CCP handoff was made self-healing. It
  continues to leave the healthy legacy CA process untouched, but if that
  process ever exits without all four final artifacts it now launches the
  current per-seed-checkpointed CA wrapper, which revalidates and retains the
  three completed datasets before resuming the missing one. Only after all
  four files exist does it execute the unchanged strict 1,920-cell Claim 2
  verifier and start Claim 3. Recovery failures retain any completed seed
  checkpoints and retry after 60 seconds. The replacement handoff is live at
  PID `3528025`; the complete `18/18` test suite and shell syntax check pass.
- A paper/source calibrator audit found that Appendix Tables 6–8 define the
  third classical CCP calibrator as `F3(p)=2(1-p)`, but the pinned released
  `e-ccp` source instead exposes `ECCP(pow)` computed as `5(1-p)^4`. It would
  be incorrect to relabel that source output as linear. The full CCP wrapper
  now retains every author estimator, split, foldwise p-value, seed, grid, and
  randomization stream, but reconstructs the paper-specified F3 intervals as
  `ECCP(linear)` from those returned p-values. The protocol remains exactly 13
  methods and 11,700 cells. A dedicated numerical falsifier proves the two
  formulas differ; the expanded suite passes `19/19`. Commit: `e278564`.
