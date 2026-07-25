# Evaluator visibility matrix

The reviewer verdict column records artifact readiness, not the live judge’s
future decision.

| Claim | Canonical page | Code visible | Data inline | Raw link | Checker | Control | Exact claim tested | Reviewer verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [Current Claim 1](#/current-claim-1) | verifier + checker linked | 18/18, error, mismatch counts | two JSONs + bundle | PASS output linked | domain + classic inflation | Definition 2.2 equivalence on theorem domain | READY |
| 2 | [Current Claim 2](#/current-claim-2) | symbolic verifier + checker linked | witness and all assumptions | exact rational JSON | PASS output linked | three distinct invalid witnesses | Proposition 2.3 on printed `[0,1]` | READY |
| 3 | [Current Claim 3](#/current-claim-3) | analytic verifier + checker linked | errors and 9/9 AoN | summary + 11,700 rows | PASS output linked | tamper/domain controls | every Theorem 2.6 component | READY |
| 4 | [Current Claim 4](#/current-claim-4) | ECCP verifier + checker linked | universal certificate + 9/9 | summary + 11,700 rows | PASS output linked | invalid dependence/scaling | Proposition 4.1 guarantee and application | READY |
| 5 | [Current Claim 5](#/current-claim-5) | WECA verifier + checker linked | proof, 6 mutations, 8/8 | summary + 1,920 rows | PASS output linked | label-adaptive violations | Proposition 4.2 data-dependent weights | READY |
| 6 | [Current Claim 6](#/current-claim-6) | joint verifier + checker linked | all 60 comparisons and 17 coverage cells | summary + 13,620 rows | PASS output linked | reverse/missing-cell controls | Section 5 released protocols | READY |

All pages include assumptions, deviations, fixed command, locked environment,
seeds, Git SHA, CPU allocation, and runtime. The exact raw bundle SHA-256 is
`1cd1115ee4fefc260c79512eb1a4bea61f342ebca5bb9acf3cc5b8ca91f90359`.
