# Branch audit

The repository originally exposed execution-tool branches under `orx/*`.
Those names describe how a run was launched, not what the branch contains.
The final public taxonomy uses `baseline/*`, `audit/*`, and `release/*` while
preserving each branch tip and its history.

| Original branch | Final branch | Scientific or packaging role |
| --- | --- | --- |
| `orx/judged-7-of-12-baseline` | `baseline/judged-7-of-12` | Original live-score baseline and locked environment |
| `orx/baseline-protocol-sidecar-repair` | `baseline/protocol-sidecar-repair` | Reconstruct missing protocol sidecars |
| `orx/baseline-metadata-reconstruction` | `baseline/metadata-reconstruction` | Passing cumulative baseline |
| `orx/claim-2-literal-endpoint-counterexample` | `audit/claim-2-endpoint-counterexample` | Exact endpoint counterexample and corrected theorem |
| `orx/claim-3-analytic-and-full-scale-aon-verification` | `audit/claim-3-sigmoid-aon` | Sigmoid analytic properties and AoN comparison |
| `orx/claim-4-eccp-universal-mechanism-and-full-protoc` | `audit/claim-4-eccp-coverage` | ECCP mechanism, LPs, and full protocol |
| `orx/claim-5-data-dependent-weca-full-protocol` | `audit/claim-5-weca-independence` | WECA source noninterference and CA protocol |
| `orx/judge-first-compact-evidence` | `audit/judge-first-visibility` | Evaluator prompt-truncation audit |
| `orx/evaluator-visible-cumulative-release-candidate` | `release/evaluator-visible-cumulative` | Cumulative evidence release candidate |
| `orx/fail-closed-openml-outage-fallback` | `release/openml-outage-fallback` | Fail-closed OpenML availability path |
| `orx/final-judge-first-publication` | `release/final-judge-first` | Final judge-first package |
| `orx/audited-publication-package` | `release/audited-publication-package` | Earlier audited publication package |

`main` remains the canonical landing page and publication branch. It is the
only branch used by the repository URL and is the default branch. No branch is
presented as a new scientific result merely because it is a packaging branch.

After publication, verify the final branch list and tip identities with:

```bash
npx -y gh-axi api repos/MachineLearning-Nerd/icml26-set-preserving-p2e-calibration/branches --paginate
git ls-remote --heads origin
```

The final GitHub readback is the authority for tip SHAs; this document records
the semantic mapping so branch names remain understandable if commit IDs are
rewritten to normalize attribution.
