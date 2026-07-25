# Exact command and environment

Every experiment node inherits the unchanged OpenResearch command:

```bash
uv run --frozen python repro/src/run_campaign.py
```

Environment:

- Python: exactly 3.12.x (`pyproject.toml`)
- Resolver and runner: `uv`, frozen by repository-level `uv.lock`
- Compute: Hugging Face `cpu-upgrade`, image
  `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`
- Estimated useful cores: 8 for the cumulative suite; the endpoint verifier
  itself is single-process and deterministic
- Seeds: none

The authoritative run SHA, actual CPU allocation, and runtime are emitted as
`CAMPAIGN_PROVENANCE` and `CAMPAIGN_RESULT` in the OpenResearch log.
