# Claim 4 — current verification

**Verdict: VERIFIED · Confidence: MEDIUM**

**Exact source claim.** Proposition 4.1 gives ECCP finite-sample coverage at
least `1-alpha`; the named standard CCP variants have only the approximate
`1-2alpha` lower bound plus their finite-sample correction.

**Assumptions audited.** Test/calibration exchangeability makes every fold P2E
output an e-variable. Linearity makes their average an e-variable without fold
independence. Randomized Markov then bounds miscoverage by `alpha`.

**Direct result.** The universal derivation does not depend on finite
enumeration. Exact arbitrary-dependence checks cover eight cases and
exchangeable-prefix checks five cases. Maximum valid tail/alpha ratio is
`0.952381` (randomized: `1.0`). Invalid scaling and invalid-dependence controls
are detected. The full author protocol has 11,700 rows and all 9 ECCP
dataset–model coverage means pass the predeclared 0.02 shortfall tolerance;
minimum mean `0.890299` at nominal `0.90`.

**Run provenance.** Cumulative HF `cpu-upgrade` run `1811c6e7-901f-4cb1-9a24-0ea0891b8717`,
Git SHA `23c37c41627a5d2e4f55553726a8af2a8f1b97ba`; estimated useful cores 8, actual allocation 64,
campaign runtime `76.700822` seconds. Fixed command:
`uv run --frozen python repro/src/run_campaign.py`; one repository `.venv`,
Python `==3.12.*`, exact `uv.lock`; 100 seeds per cell.

- [Exact claim contract](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-4/claim_contract.json)
- [Executable verifier](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-4/verifier.py)
- [Independent checker](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-4/checker.py)
- [Raw full-protocol summary](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-4/raw_eccp_full_protocol.json)
- [Full 11,700-row raw bundle](https://huggingface.co/buckets/DineshAI/jNv4sl4YZH-artifacts#logbook-files/outputs/jNv4sl4YZH_full_evidence_bundle.jsonl)
- [Checker output](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-4/independent_checker_output.json)
- [Negative controls](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-4/negative_control_output.json)
- [Limitations](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-4/limitations_and_deviations.md)

The Parkinson-RF descriptive 95% interval lies below 0.90. It is disclosed;
the finite-sample verdict rests on the proof certificate, not the sample mean.
