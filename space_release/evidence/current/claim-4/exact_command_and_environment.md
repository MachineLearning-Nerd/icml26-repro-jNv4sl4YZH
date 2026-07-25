# Exact command and environment

```bash
uv run --frozen python repro/src/run_campaign.py
```

The command is unchanged across the experiment tree. Python is exactly
3.12.x and dependencies are frozen by the repository `uv.lock`. Runs use
Hugging Face `cpu-upgrade` with
`ghcr.io/astral-sh/uv:python3.12-bookworm-slim`. Estimated useful cores are
8 for the cumulative suite; the dedicated verifier is single-process. The
run log records actual CPU allocation, Git SHA, and runtimes.
