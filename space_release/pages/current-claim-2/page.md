# Claim 2 — current verification

**Verdict: FALSIFIED literally · Confidence: MEDIUM**

**Exact source claim.** Proposition 2.3 states that any decreasing,
left-continuous p-to-e calibrator on `[0,1]` that is set-preserving must equal
the all-or-nothing calibrator. The paper proof constrains positive intervals
but does not constrain the value at zero.

**Assumptions audited.** The primary calibrator reference permits
`[0,infinity]` values and uses `f(0)=infinity` in its admissibility theorem.
Define `F*(0)=infinity` and `F*(p)=AoN(p)` for every `p>0`. Then `F*` is
decreasing and left-continuous, has integral one, is set-preserving for every
positive conformal p-value, and differs from AoN at zero.

**Direct result.** The symbolic witness satisfies every printed assumption and
contradicts uniqueness for every `alpha in (0,1)`. An exact rational
reconstruction checks 880,250 positive support points and seven alpha values.
Three controls fail for the intended reasons: lowering the endpoint breaks
monotonicity; adding positive-interval mass exceeds the integral budget; moving
the jump breaks set membership.

**Run provenance.** Cumulative HF `cpu-upgrade` run `{{FINAL_RUN_ID}}`,
Git SHA `{{FINAL_SHA}}`; estimated useful cores 8, actual allocation 64,
campaign runtime `{{FINAL_RUNTIME}}` seconds. Fixed command:
`uv run --frozen python repro/src/run_campaign.py`; one repository `.venv`,
Python `==3.12.*`, exact `uv.lock`. This proof is deterministic and uses no
stochastic seeds.

- [Exact claim contract](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-2/claim_contract.json)
- [Executable verifier](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-2/verifier.py)
- [Independent checker](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-2/checker.py)
- [Raw counterexample JSON](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-2/raw_counterexample_output.json)
- [Checker output](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-2/independent_checker_output.json)
- [Negative-control output](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-2/negative_control_output.json)
- [Source audit](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-2/source_audit.md)
- [Limitations](https://huggingface.co/spaces/DineshAI/jNv4sl4YZH/resolve/main/evidence/current/claim-2/limitations_and_deviations.md)

The corrected uniqueness statement on `(0,1]` remains verified. The
operational conformal result is unchanged because conformal p-values are
strictly positive. This page supersedes the historical rejected Claim 2
verifier, which tested unrelated aggregation experiments.
