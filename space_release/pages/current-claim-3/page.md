# Claim 3 — current verification

**Verdict: VERIFIED · Confidence: HIGH**

**Exact source claim.** Theorem 2.6 states that the sigmoid P2E calibrator is
exact, smooth, invertible, strictly positive, and dominates AoN in aggregation
under `alpha(n+1)>1` with non-integral `alpha(n+1)`.

**Assumptions audited.** All 18 analytic cells satisfy the theorem domain.
The pointwise comparison is calibrated honestly: theorem-level prediction-set
inclusion is non-strict; strict length reduction is a full-protocol empirical
result.

**Direct result.** Expectation error is at most `4.44e-16`; inverse round-trip
error at most `2.22e-16`; every sampled derivative is strictly negative and
every value strictly positive. Across 11,700 CCP rows, P2E is strictly shorter
than AoN in 9/9 dataset–model comparisons; minimum relative reduction
`0.178669%`.

**Run provenance.** Cumulative HF `cpu-upgrade` run `1811c6e7-901f-4cb1-9a24-0ea0891b8717`,
Git SHA `23c37c41627a5d2e4f55553726a8af2a8f1b97ba`; estimated useful cores 8, actual allocation 64,
campaign runtime `76.700822` seconds. Fixed command:
`uv run --frozen python repro/src/run_campaign.py`; one repository `.venv`,
Python `==3.12.*`, exact `uv.lock`; 100 seeds per empirical cell.

- [Exact claim contract](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-3/claim_contract.json)
- [Executable verifier](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-3/verifier.py)
- [Independent checker](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-3/checker.py)
- [Raw analytic and AoN summary](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-3/raw_properties_and_aon_output.json)
- [Full 11,700-row raw bundle](https://huggingface.co/buckets/DineshAI/jNv4sl4YZH-artifacts#logbook-files/outputs/jNv4sl4YZH_full_evidence_bundle.jsonl)
- [Checker output](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-3/independent_checker_output.json)
- [Negative controls](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-3/negative_control_output.json)
- [Limitations](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-3/limitations_and_deviations.md)

This page supersedes the historical toy-scale mechanism check.
