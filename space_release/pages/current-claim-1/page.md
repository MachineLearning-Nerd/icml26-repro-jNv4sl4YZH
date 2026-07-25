# Claim 1 — current verification

**Verdict: VERIFIED · Confidence: HIGH**

**Exact source claim.** Definition 2.2 calls a calibrator set-preserving when,
for every conformal rank-grid p-value in the stated domain,
`p > alpha` iff `F(p) < 1/alpha`. Theorem 2.6 assumes
`alpha(n+1) > 1` and non-integrality.

**Assumptions audited.** Eighteen `(n, alpha)` cells up to `n=200` satisfy both
domain conditions. Five low-level or exact-boundary controls are rejected.

**Direct result.** Clean-room cells: 18/18; author-source cells: 18/18;
membership mismatches: 0; threshold errors: 0; maximum expectation error:
`4.44e-16`. Log, square-root, and linear controls inflate the set in all 18
cells.

**Run provenance.** Cumulative HF `cpu-upgrade` run `{{FINAL_RUN_ID}}`,
Git SHA `{{FINAL_SHA}}`; estimated useful cores 8, actual allocation 64,
campaign runtime `{{FINAL_RUNTIME}}` seconds. Fixed command:
`uv run --frozen python repro/src/run_campaign.py`; one repository `.venv`,
Python `==3.12.*`, exact `uv.lock`. Seeds are deterministic and enumerated in
the raw records.

- [Exact claim contract](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-1/claim_contract.json)
- [Executable verifier](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-1/verifier.py)
- [Independent checker](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-1/checker.py)
- [Raw clean-room JSON](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-1/raw_cleanroom_output.json)
- [Raw author cross-check JSON](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-1/raw_source_crosscheck.json)
- [Checker output](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-1/independent_checker_output.json)
- [Negative-control output](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-1/negative_control_output.json)
- [Source audit](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-1/source_audit.md)
- [Limitations and deviations](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-1/limitations_and_deviations.md)

The verifier and checker both exit nonzero on a mismatch. This page supersedes
the historical Claim 1 page while retaining its full-credit evidence.
