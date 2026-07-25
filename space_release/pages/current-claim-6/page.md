# Claim 6 — current verification

**Verdict: VERIFIED · Confidence: HIGH**

**Exact source claim.** Section 5 reports that P2E aggregation produces
smaller prediction sets than baseline p-to-e conversions while retaining valid
coverage in the released ECCP and conformal-aggregation applications.

**Assumptions audited.** CA uses four OpenML tasks, 20 seeds, seven base
regressors, `M=512`, `B=500`, nominal 0.95. CCP uses three bundled datasets,
three models, 100 seeds, paper fold counts, nominal 0.90. A source-hash-bound
audit corrects the released CCP F1/F2/F3 column mismatch and uses
formula-faithful log, square-root, and linear calibrators.

**Direct result.** CA: 1,920/1,920 rows, P2E shorter in 24/24
WECA/UR-WECA comparisons, minimum relative reduction `40.302%`, coverage 8/8.
ECCP: 11,700/11,700 rows, P2E strictly shorter in 36/36 comparisons including
AoN 9/9, minimum classical reduction `23.664%`, coverage 9/9.

**Run provenance.** Cumulative HF `cpu-upgrade` run `1811c6e7-901f-4cb1-9a24-0ea0891b8717`,
Git SHA `23c37c41627a5d2e4f55553726a8af2a8f1b97ba`; estimated useful cores 8, actual allocation 64,
campaign runtime `76.700822` seconds. Fixed command:
`uv run --frozen python repro/src/run_campaign.py`; one repository `.venv`,
Python `==3.12.*`, exact `uv.lock`. CA uses 20 seeds; CCP uses 100.

- [Exact claim contract](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-6/claim_contract.json)
- [Executable verifier](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-6/verifier.py)
- [Independent checker](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-6/checker.py)
- [Raw full-protocol summary](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-6/raw_full_protocol_summary.json)
- [Full 13,620-row raw bundle](https://huggingface.co/buckets/DineshAI/jNv4sl4YZH-artifacts#logbook-files/outputs/jNv4sl4YZH_full_evidence_bundle.jsonl)
- [Checker output](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-6/independent_checker_output.json)
- [Negative controls](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-6/negative_control_output.json)
- [Limitations](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-6/limitations_and_deviations.md)

One finite-seed CA length-SD scalar is `0.201899` versus paper `0.18`; the
other three scalars in that cell and the efficiency result pass. This page
retains the old full-credit evidence and adds direct ECCP and AoN comparisons.
