# Local publication gate

`repro/src/publication_gate.py` is the only publication gate for the canonical
repository. It is a local, read-only validation step that writes one
machine-readable result under `outputs/`. It does not authenticate to or write
to GitHub, Hugging Face, Trackio, OpenResearch, or any other external service.

## Run

```bash
uv sync --frozen
uv run python repro/src/publication_gate.py --skip-producers
```

`--skip-producers` means “validate the checked-in evidence.” It is the normal
fresh-clone check and does not silently regenerate expensive author protocols.
The full scientific commands are listed in the README and require the ignored
official source checkout under `upstream/`.

## Checks

The gate fails closed unless it can prove all of the following:

- the paper, OpenReview ID, official source commit, and claim snapshot match
  the repository configuration;
- C1, C3, C4, C5, and C6 have their required verified evidence;
- C2 is explicitly recorded as `FALSIFIED` with the endpoint witness and
  corrected positive-domain statement;
- CA and CCP evidence contain exactly 1,920 and 11,700 rows;
- raw summaries, protocol adapters, coverage cells, efficiency comparisons,
  negative controls, and source-drift accounting match fixed values;
- all 122 headline cells and 488 scalar comparisons are accounted for,
  including the one CA dispersion discrepancy and 27 source-discrepant CCP
  cells;
- the paper/source artifacts and declared configuration hashes match;
- no `.trackio` directory, environment file, token-like secret, absolute local
  path, or tracked publisher script is present;
- the evidence bundle can be regenerated and round-tripped from current JSON
  sources.

The gate’s output includes the evidence file list, SHA-256 hashes, claim
verdicts, row counts, and a `publication_gate_passed` boolean. The output is
itself committed so a reviewer can inspect the exact validation result.

## Publication boundary

“Published” means the GitHub tree contains the reviewed files and the final
branch/identity readback has passed. External experiment dashboards and old
publication queues are not dependencies of this repository. The checked-in
`space_release/` directory is an archival evaluator snapshot and is not used to
authorize a new external publication.
