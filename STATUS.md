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
   theorem-domain `(n, alpha)` cells: zero p/e set or threshold mismatches,
   exact-e expectation error at most `4.45e-16`, and all classic-calibrator
   controls inflate the set. The theorem domain (`alpha*(n+1) > 1` and
   non-integer) is parsed from the hash-pinned primary TeX; all five excluded
   low-level/rank-boundary controls are rejected. A separate invocation of the
   pinned author implementation has the same 18/18 membership identities and
   exact expectations. The source emits
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
   deterministic `1-alpha` Markov events. Exact sparse linear programs
   additionally maximize both deterministic-threshold rejection probability
   and the paper's independent-uniform randomized-threshold failure probability
   over every joint coupling with the required uniform conformal-rank
   marginals: all 8/8 fixed-weight worst cases remain at or below `alpha`,
   including two equal-weight ECCP and six nonuniform tuning-independent WECA
   cases. A 2x-invalid-e-value control is correctly reported as only 4/8 under
   the deterministic LP (it remains conservative in four cases) but fails 8/8
   randomized LPs, while forbidden outcome-adaptive max weighting violates
   both bounds in 8/8.
   This directly checks both ECCP and WECA's independent-tuning requirement,
   but does not replace the queued empirical run.

## Publication gate

Do not publish until all source runs, independent verifiers, negative controls,
tests, headline-number comparison, and secret scan pass. The current Hugging
Face quota does not affect local implementation work. The fail-closed
`repro/src/prepublish_gate.py` now reruns every independent checker and all
tests, validates the 1,920 CA and 11,700 CCP cell sets, requires all 122 tabulated paper
headline cells within tolerance, verifies the source pin and Trackio evidence,
scans hygiene, and hashes every final artifact. It cannot pass until the full
source outputs and final Conclusion marker exist. On success it packages twelve
summary/report artifacts plus all seven raw dataset files into one hash-indexed JSONL
artifact that Trackio will promote to the Hugging Face bucket.
The headline tolerances were fixed before the remaining results existed at
`0.01` absolute coverage and `5%` relative length; larger drift halts the gate.
The comparison now covers all four reported scalars in each headline cell:
coverage mean/SD and length mean/SD, for 488 checks across 122 cells. The added
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
  All 8/8 valid arbitrary-dependence LP optima pass for both deterministic and
  paper-exact randomized thresholds; outcome-adaptive weighting fails 8/8
  under both rules. Separate permutation enumerations independently match the
  two-fold deterministic and randomized LP optima, and malformed/negative/non-normalized weights are
  rejected. The refreshed result is captured in Trackio and closes the
  previously implicit ECCP mechanism scope.
- Added a pre-final-result empirical coverage sanity gate for both applications
  named by C3. All eight CA P2E and all 27 CCP P2E-method coverage means
  (ECCP, ECCP-Exch, and UR-ECCP-Exch) must be no
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
- The bundle is no longer trusted by size/hash alone. Its ordered 15-record
  manifest (eight summaries/reports plus seven full raw dataset files) is
  persisted in the gate result; every JSONL line is re-parsed and required to
  match its current source path, source SHA-256, and decoded payload immediately
  before publication. Unit controls reject both post-gate source mutation and
  an altered embedded payload.
- Exercised the actual end-to-end gate while evidence is intentionally
  incomplete. It revalidated C1 and the expanded C3 mechanism, then stopped at
  the strict CA verifier because `dataset_361234.json` is absent. It created
  neither a passing manifest nor an evidence bundle, proving the live gate
  cannot promote the current 1,440/1,920-row partial state.
- Pinned the headline policy independently inside the final gate: exactly 32
  CA and 90 CCP cells from Table 2, the CA alternative-calibrator table, and
  Appendix Tables 6-8, with coverage
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
  summarized raw results to all 32 reported CA P2E/comparator cells and all 90
  tabulated CCP cells transcribed from both panels of Appendix Tables 6–8,
  checking all 488 mean/SD scalars and explicitly reporting any drift.
- The serialized handoff launched Claim 2 after the unrelated shared sweep
  completed. Three of four CA tasks are now complete; do not start the CCP
  sweep until the final CA task and its independent verifier finish. A second
  durable one-shot handoff waits for all three CCP final artifacts, then runs
  the strict 11,700-cell verifier, all 488 scalar paper-table checks, the
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
  formulas differ. A second test invokes the real pinned OLS CCP primitive and
  independently replays its RNG, reproducing the source power-calibrator
  intervals exactly before checking the corrected linear construction. The
  expanded suite passes `20/20`; both audits are captured in Trackio. Commits:
  `e278564`, `935df3e`, and `c3ce549`.
- Claim 2's substantial-efficiency evidence is now gated across both paper
  applications, not CA alone. The exact 13-method CCP tuple and its mappings
  to AoN, log, square-root, and the paper-corrected linear calibrator are pinned
  in tests. The independent verifier must produce exactly 36 matched CCP
  comparisons: P2E no longer than the baseline in 36/36, strictly shorter in
  36/36 and 9/9 AoN cells, with all 27/27 classical-calibrator reductions at
  least 10%. Equality
  at the AoN boundary and a 5% classical reduction both fail the intended
  strict/materiality gates. The renderer and prepublication gate enforce these
  counts before writing the final claim verdict. The complete `20/20` suite is
  captured in Trackio. Commits: `5719dc8` and `3f4c511`.
- Before any CCP result existed, the paper-number gate was first expanded from the
  nine winning ECCP cells to every method in both tabulated panels of Appendix
  Tables 6–8: 90 CCP cells (three datasets x three models x ten methods), plus
  the eight CA P2E cells. At that stage, all 392 coverage/length mean/SD scalars
  across 98 cells became fail-closed publication requirements. An independent parser
  matched all 90 CCP configuration cells field-for-field against the primary
  arXiv TeX, preventing manual-transcription drift. The live post-CCP watcher,
  final renderer, prepublication gate, tests, documentation, and captured
  Trackio audit at that stage all required the same 98-cell/392-scalar totals (`a5505cd`,
  `010fb7c`, `8adf111`).
- A pre-CCP runtime audit compared literal source execution, seed-level
  parallelism, and exact vectorization. Parallel seeds were rejected because
  released RF already uses all cores. The selected
  `vectorized-exact-postprocessing-v1` adapter preserves the source fold split,
  estimators, grids, p-values, and RNG, while replacing only scalar p/e
  aggregation. The reproducible Parkinson-shaped microbenchmark measured
  roughly `27x` for that kernel (about `7.7` projected literal versus `0.28`
  vectorized CPU-hours over the full Parkinson protocol, excluding fitting and
  interval extraction). Literal-versus-vectorized tests require bit-identical p-values and
  exact intervals for OLS, RF, Lasso, and all 13 methods. Adapter provenance is
  part of the raw protocol and final gate.
- The post-CCP and prepublication gates now bind the raw evidence to the exact
  paper protocol rather than trusting a self-declared but internally
  consistent protocol: pinned source SHA; Boston/Abalone at 15 folds and
  Parkinson at 20; seeds 45--144; OLS/RF/Lasso; the ordered 13-method tuple;
  alpha 0.1; 300 grid points; and the parity-checked execution adapter.
  Negative controls independently remove a dataset, seed, model, or method and
  alter alpha, grid size, or adapter; every drift is rejected. All 23 tests and
  the no-write publication preflight pass.
- The original 98-cell/392-scalar paper-number fixture became independently executable,
  not a one-off transcription claim. A verifier downloads arXiv `2606.03600v1`
  in memory, requires archive SHA-256 `f5124c...` and `main.tex` SHA-256
  `49058f...`, parses Table 2 and both panels of Appendix Tables 6--8, and
  compares every field with `paper_headlines.json`. The live primary source
  yielded 98/98 cells and 392/392 exact scalar transcriptions with zero
  mismatches; the audit JSON is a required fifteenth evidence-bundle record.
- At `2026-07-19 19:39 IST`, the current commit's complete 22-test suite passed
  in `7.75s`. A fresh invocation of the real prepublication gate revalidated
  the source pin, Claim 1 identity/source parity, and all eight Claim 3
  arbitrary-dependence cases, then failed closed at the strict CA verifier
  because `dataset_361234.json` is still absent. It emitted neither a passing
  manifest nor an evidence bundle. The legacy final-task worker remained
  compute-active at `97.8%` CPU with `23:09:30` CPU time, `191,984 kB` RSS, and
  zero swap; the serialized CA-to-CCP and post-CCP handoffs remain alive.
- At `2026-07-19 20:08 IST`, the legacy final-task worker remained compute-active
  at `97.8%` CPU with `23:38:31` CPU time and about `194 MB` RSS. The three
  completed 480-row artifacts remain intact; `dataset_361234.json` has not yet
  been promoted, so the strict Claim-2 gate correctly has not started CCP.
  Both durable handoffs and the shared HF drain are alive. Primary-source
  fixture audit commit `e6295ce` leaves the repository clean and raises the
  complete suite to 23 passing tests without reducing any paper-scale work.
- The CA-to-CCP transition is now self-healing on both sides. After Claim 2's
  strict gate passes, a single-owner loop starts or resumes the checkpointed
  full CCP worker until all Boston, Abalone, and Parkinson artifacts exist.
  A failed/interrupted CCP attempt retains only structurally complete seeds,
  retries after 60 seconds, and cannot launch a competing worker while either
  the runner or its Trackio parent is active. The live CA process is not
  interrupted by this watcher hardening. Paper-specific nonblocking file locks
  close the final check/start race if duplicate watcher processes are ever
  launched accidentally, while a whole-transition owner lock prevents duplicate
  Claim-2 verification and Trackio writes.
- The post-CCP watcher now has the same singleton-owner guarantee, so duplicate
  launches cannot append competing final verdict cells or race publication.
  After all evidence and the fail-closed gate pass once, only the idempotent
  publisher is retried on a nonzero GitHub/HF/readback exit, at 60-second
  intervals. This preserves the completed evidence and canonical queue entry
  across transient external failures without rerunning the heavy CCP sweep.
- A fresh released-input audit explains the long final CA task: `361234` retains
  4,177 rows, versus 1,030, 1,503, and 1,066 for the three completed tasks. The
  author WECA loop evaluates 508 sampled/baseline weights over a calibration
  split, 512 candidate values, and calibration-score comparisons, so its
  dominant cost grows roughly quadratically with row count. Scaling the three
  observed completed-task durations by squared row-count ratios projects
  approximately 25--40 hours for `361234` (median about 29.5 hours). Its current
  ~16.7-hour final-task runtime is therefore consistent with expected finite
  work, not evidence of a hang; the active legacy process should remain intact.
- Claim 2 now has the same exact raw-protocol contract as Claim 3. Both the
  CA-to-CCP transition and final publication gate reject any drift in the pinned
  source SHA, ordered four task names/IDs, released 20-seed tuple, alpha 0.05,
  512 grid points, or 500 weight samples. Negative controls alter each field;
  an internally consistent 1,920-cell result at a different scope can no longer
  pass merely by declaring that reduced/changed scope in its own metadata.
- At `2026-07-19 20:27 IST`, a fresh read of the challenge's authoritative live
  `claims.json` still returns exactly the three locally pinned jury texts for
  `jNv4sl4YZH`; the paper remains worth six possible points. The legacy final
  CA worker remains compute-active at `97.9%` CPU and about `193 MB` RSS, with
  the three completed task artifacts intact and the fourth not yet promoted.
- The verified publisher now completes its first public GitHub push before
  atomically joining the shared Hugging Face backlog. This prevents the shared
  Trackio publisher from rewriting local artifact links concurrently with the
  initial git stage/commit, while retaining idempotent, gate-checked queueing.
  The ordering is regression-tested; all 25 tests, shell syntax, publication
  preflight, and diff hygiene pass.
- Raw CA and CCP checkpoints and independent verifiers now reject semantically
  impossible metrics as well as non-finite values: every coverage must be in
  `[0,1]` and every interval length must be nonnegative. Both transition gates
  and the final publication gate require zero out-of-domain rows. Positive and
  negative range fixtures pass across both runners and both verifiers; the
  complete 25-test suite, bytecode compilation, shell syntax, preflight, and
  diff hygiene remain green without interrupting the live legacy CA process.
- The final publication gate now refreshes the official challenge
  `claims.json` over HTTPS and requires exactly the three pinned claim texts
  before emitting its passing manifest. Count, extra-claim, missing-claim, and
  wording-drift controls fail; a real live refresh returned all three exact
  texts. The publisher additionally requires this live verification proof from
  the fresh gate. All 26 tests pass.
- Claim 3 now includes a direct audit of WECA's independent-tuning assumption,
  not only the abstract fixed-weight coupling LP. The audit is bound to the
  pinned `methods.py` and `Evalue_aggregation_weighted` hashes, verifies the
  released `i1/i2/i3` disjoint dataflow, and runs six released-seed
  noninterference cases. Arbitrarily changing every final-calibration row or
  every test covariate/outcome changes selected weights by exactly zero in all
  cases; a forbidden test-adaptive control changes in 6/6. The final gate,
  evidence-derived verdict, Trackio, and 16-record bundle now require this
  artifact. All 27 tests, compilation, shell syntax, preflight, and diff hygiene
  pass while the legacy final CA task remains uninterrupted.
- A real premature invocation of the expanded final gate refreshed the live
  claims, revalidated Claim 1, the eight coupling LP cases, and all six WECA
  noninterference cases, then stopped at the absent fourth CA artifact. It
  emitted neither `prepublish_gate.json` nor the 16-record evidence bundle, so
  the new mechanism evidence does not weaken the full-scale fail-closed rule.
- Before the final CA task or any CCP result existed, the primary-source gate
  was expanded again to cover every paper-reported CA cell used by Claim 2.
  The parser now validates Table 2's eight P2E cells plus all 24 matched
  log/square-root/linear WECA and UR-WECA comparator cells in the adjacent
  alternative-calibrator table, as well as all 90 CCP cells. The pinned arXiv
  v1 TeX matches all 122 cells and all 488 coverage/length mean/SD scalars
  exactly; method and dataset order drift is rejected. The final renderer,
  post-CCP watcher, publication gate, tests, evidence matrix, and public
  documentation all require the expanded totals. The expanded primary-source
  audit is captured in Trackio, all 28 tests and the no-write publication
  preflight pass, and a real premature final-gate invocation still fails at
  the missing fourth CA artifact while emitting neither the publication
  manifest nor evidence bundle. At `2026-07-19 20:55 IST`, the untouched
  legacy CA worker remained compute-active at `97.9%` CPU with `24:24:44` CPU
  time and about `193 MB` RSS; both serialized handoffs remained alive.
- The Claim-3 mechanism certificate now matches the released randomized
  constructions exactly. For every rank tuple it evaluates both the ordinary
  `1/alpha` failure indicator and the conditional failure cost
  `min(alpha * merged_e, 1)` induced by the independent uniform threshold used
  by ECCP and UR-WECA, then maximizes each over all couplings with uniform rank
  marginals. All 8/8 valid cases pass both adversarial LPs; the maximum
  randomized failure/alpha ratio is `1.0`. Invalid 2x scaling fails all 8/8
  randomized LPs, and inference-adaptive max weighting fails 8/8 under both
  thresholds. The updated output and source are captured in Trackio, and the
  renderer and publication gate require the new deterministic-plus-randomized
  fields. All 28 tests, compilation, shell checks, hygiene, and no-write
  publication preflight pass. A real premature gate accepts the expanded
  mechanism certificate and then still stops at the missing fourth CA artifact,
  emitting neither manifest nor bundle. At `2026-07-19 21:03 IST`, the
  untouched CA worker remained compute-active at `97.9%` CPU with `24:33:01`
  CPU time and about `193 MB` RSS; both serialized handoffs remained alive.
- Claim 3 now independently covers the two released exchangeable variants, not
  only the equal-weight ECCP merge. Five orbit LPs assign probability to
  unordered rank multisets and average uniformly over every distinct ordering,
  enforcing fold exchangeability exactly. ECCP-Exch and randomized-first
  UR-ECCP-Exch pass 5/5 worst-case LPs (maximum failure/alpha ratios `0.9524`
  and `0.9727`); invalid 2x scaling fails 5/5 for both. A separate two-rank
  closed-form oracle matches the implementation. The future full CCP gate now
  also requires the empirical shortfall check for all 27 P2E-method cells
  (ECCP, ECCP-Exch, and UR-ECCP-Exch), rather than only nine ECCP cells. The
  expanded certificate is captured in Trackio; all 29 tests and preflights
  pass, and a real premature gate still emits no manifest/bundle. At
  `2026-07-19 21:11 IST`, the untouched CA worker remained active at `97.9%`
  CPU with `24:40:49` CPU time and about `191 MB` RSS.
- The released inputs are now independently content-pinned, not merely bound
  to a clean Git commit. A machine-readable manifest verifies SHA-256, Git blob
  SHA-1, and byte size for all 10 CA/CCP code and bundled-data files. It parses
  all three CCP CSV schemas (10,558 data rows total) and executes the released
  loaders, requiring finite arrays of shapes `(506, 14)`, `(4177, 10)`, and
  `(5875, 13)` plus the exact loader configs. A corrupted-hash control fails.
  The audit is captured with a clean relative Trackio command, required by the
  final gate, and included in the future 17-record evidence bundle. All 30
  tests, compilation, shell syntax, and hygiene checks pass. A real premature
  gate accepted the new audit and then rejected the absent fourth CA artifact,
  emitting neither manifest nor bundle. At `2026-07-19 21:24 IST`, the
  untouched CA worker remained active at `97.9%` CPU with `24:53:42` CPU time
  and about `191 MB` RSS; both serialized handoffs and the shared HF drain
  remained alive. The implementation is committed at `a421cbd`; the refreshed
  post-CCP watcher owns its singleton lock as PID `3567976`.
- Claim 1 now follows the main theorem's exact stated assumptions instead of
  counting an empirical extension as theorem evidence. The primary-TeX audit
  hash-binds the theorem block and verifies its domain, strict `s` interval,
  and normalized logistic formula. The earlier `(n=10, alpha=.05)` cell is
  outside the theorem because `alpha*(n+1)=.55`; it has been replaced by the
  theorem-valid `(40,.05)` cell. All 18/18 positive cells pass source and
  independent membership, exact-threshold, exact-expectation, and positivity
  checks; all 18 classical-calibrator controls inflate; five out-of-domain
  controls reject. The updated evidence is captured in Trackio, all 31 tests
  pass, and the real premature gate accepts Claim 1 before still stopping at
  the missing fourth CA artifact with no manifest or bundle. At
  `2026-07-19 21:36 IST`, the untouched CA worker remained active at `97.9%`
  CPU with about `25:05:24` CPU time and `193 MB` RSS; both handoffs and the
  shared HF drain remained alive.
- The four live OpenML CA inputs are now content-pinned independently of their
  task IDs. The audit binds exact task/dataset IDs, names, versions, targets,
  processed array shapes, and SHA-256 values after the released numeric-column
  and missing/non-finite-row filtering. All 7,776 rows and 47,126 feature
  values are finite and hash-identical; a deliberately corrupted feature hash
  is rejected. The audit is Trackio-captured, required by the final gate, and
  included in the future 18-record evidence bundle. All 32 tests, compilation,
  shell syntax, publication preflight, and hygiene pass. A real premature gate
  accepts the new OpenML certificate before rejecting the absent fourth CA
  output and emits neither manifest nor bundle. At `2026-07-19 21:42 IST`, the
  untouched CA worker remained compute-active at `97.9%` CPU and about `193 MB`
  RSS; the handoffs and shared HF drain remained alive. The audit is committed
  at `95f579b`; refreshed post-CCP watcher PID `3571647` owns the singleton lock.
- Every internal P2E calibration size produced by the released CA split and
  subsampling code is now audited. Of 1,680 ECA/WECA contexts, 1,600 satisfy
  the paper's exact theorem domain and 80 hit an exact-rank boundary. The
  released `C=1e6` numerical limit preserves all boundary prediction sets and
  differs from exact AoN values by at most `6.43e-174`; an exact AoN repair has
  mean one and the same set in all 27 unique boundary sizes. The final logbook
  and claim matrix disclose these 80 empirical contexts rather than calling
  them positive exact-P2E theorem instances. The audit is Trackio-captured,
  required by the gate, and raises the future evidence bundle to 19 records.
  All 33 tests, compilation, shell syntax, publication preflight, and diff
  checks pass. A real premature gate accepted the new audit before rejecting
  the absent fourth CA artifact and left no manifest or bundle. At
  `2026-07-19 21:58 IST`, the untouched CA worker remained active at `97.9%`
  CPU with three complete 480-row artifacts; both serialized handoffs and the
  shared HF drain remained alive. The shared drain has published all 42 current
  backlog entries, and this paper will join it atomically only after the full
  three-claim gate and first GitHub push succeed. The audit implementation is
  committed at `9f23d62`; refreshed post-CCP watcher PID `3575557` owns its
  singleton lock and the active CA worker was not interrupted.
