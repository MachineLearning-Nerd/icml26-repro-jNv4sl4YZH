# Source and provenance audit

## Primary paper

- Title: *Set-Preserving Calibration from Conformal P-Values to E-Values*.
- Authors: Nabil Alami, Jad Zakharia, and Souhaib Ben Taieb.
- arXiv: [`2606.03600`](https://arxiv.org/abs/2606.03600), v1 used for the
  paper-table audit.
- OpenReview: [`jNv4sl4YZH`](https://openreview.net/forum?id=jNv4sl4YZH).
- v1 source URL: `https://export.arxiv.org/e-print/2606.03600v1`.
- v1 PDF URL: `https://arxiv.org/pdf/2606.03600v1`.

The checked-in source artifacts are under `sources/arxiv-v1/`:

| Artifact | SHA-256 |
| --- | --- |
| `source.tar.gz` | `f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db` |
| `main.tex` | `49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857` |
| `paper.pdf` | `702dbea68adb646d41255420c67122b63f879c66b333684f904fc39d11c718e2` |

The paper-table fixture verifier independently checks the archive and TeX
hashes before parsing the 122 configured headline cells.

## Official implementation

The author repository is
[`Nabil-Ala/P2E_calibration`](https://github.com/Nabil-Ala/P2E_calibration),
pinned at commit `66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974`. It is cloned into
the ignored `upstream/` directory for source-dependent checks and is never
embedded as a gitlink in this repository.

The ten hash-bound files are declared in
`repro/configs/source_manifest.json` and cover the released CA driver,
calibrators, CCP driver, utilities, and three bundled datasets. The audit
requires the source worktree to be clean, all Git blob IDs and SHA-256 values
to match, all loader shapes to match, and 10,558 source dataset rows to be
accounted for.

The CA manifest separately binds four OpenML tasks, 7,776 retained rows, and
47,126 feature values. The CCP protocol uses the bundled Boston, Abalone, and
Parkinson/UPDRS data. A fresh run must fail closed when OpenML is unavailable or
when any content hash changes.

## Protocol boundary

The reproduction preserves author estimators, data splits, seeds, folds,
candidate grids, and foldwise p-values. The CCP runner uses the named
`vectorized-exact-postprocessing-v1` adapter only for deterministic p/e
aggregation; parity checks require the same source grids, foldwise outputs,
randomization, and 13 method cells. This is orchestration, not a replacement
model.

The released CCP table driver has a material formula/column mismatch. The paper
defines F1/F2/F3 as log/square-root/linear, while the released driver fills
those positions with square-root/log/power. The last released function computes
`5(1-p)^4`, not the paper’s `2(1-p)`. The audit binds the paper TeX and released
source by hash, records numerical witnesses, keeps formula-faithful labels, and
replays only the reversible log/square-root swap across 72 available scalars.

## Claim 2 endpoint qualification

The paper’s uniqueness proof forces the AoN form on positive intervals but does
not identify the value at zero. The endpoint verifier records the exact witness
and the corrected statement. This qualification is part of the result, not an
implementation failure.

## Environment

The checked-in `pyproject.toml` and `uv.lock` pin Python 3.12-compatible
dependencies, including `pandas==2.3.3`, which is required by the released
Parkinson loader’s in-place numeric assignment. No author source file is
modified.
