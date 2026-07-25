# Claim 5 — current verification

**Verdict: VERIFIED · Confidence: HIGH**

**Exact source claim.** Proposition 4.2 allows data-dependent WECA weights when
the simplex-valued weights are functions only of tuning data and are
independent of inference e-values and the test point.

**Assumptions audited.** The hash-pinned released source divides calibration
indices into disjoint tuning, weight-calibration, and final-calibration splits.
Across six released seeds, mutating final-calibration rows or all test
covariates/outcomes changes the selected weights by exactly zero.

**Direct result.** Conditional on the tuning-selected weights, the weighted
e-value expectation is at most one, without assuming independence among
inference e-values. Full protocol: 1,920 rows, four OpenML tasks, 20 seeds,
`M=512`, `B=500`; all 8 P2E WECA/UR-WECA coverage cells pass, minimum
`0.949032` at nominal 0.95. A forbidden test-label-adaptive selector changes
weights in 6/6 controls and violates coverage: minimum tail/alpha ratios
`1.818` deterministic and `1.943` randomized.

**Run provenance.** Cumulative HF `cpu-upgrade` run `1811c6e7-901f-4cb1-9a24-0ea0891b8717`,
Git SHA `23c37c41627a5d2e4f55553726a8af2a8f1b97ba`; estimated useful cores 8, actual allocation 64,
campaign runtime `76.700822` seconds. Fixed command:
`uv run --frozen python repro/src/run_campaign.py`; one repository `.venv`,
Python `==3.12.*`, exact `uv.lock`; 20 deterministic released seeds.

- [Exact claim contract](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-5/claim_contract.json)
- [Executable verifier](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-5/verifier.py)
- [Independent checker](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-5/checker.py)
- [Raw full-protocol summary](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-5/raw_weca_full_protocol.json)
- [Full 1,920-row raw bundle](https://huggingface.co/buckets/DineshAI/jNv4sl4YZH-artifacts#logbook-files/outputs/jNv4sl4YZH_full_evidence_bundle.jsonl)
- [Checker output](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-5/independent_checker_output.json)
- [Negative controls](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-5/negative_control_output.json)
- [Limitations](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-5/limitations_and_deviations.md)

Arbitrary label-dependent test-time weights are outside the proposition and
fail the intended negative control.
