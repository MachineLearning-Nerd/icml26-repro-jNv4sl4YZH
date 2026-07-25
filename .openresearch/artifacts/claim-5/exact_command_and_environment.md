# Exact command and environment

```bash
uv run --frozen python repro/src/run_campaign.py
```

- Python exactly 3.12.x
- Dependencies frozen by repository-level `uv.lock`
- Hugging Face `cpu-upgrade`
- Image `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`
- Estimated useful cumulative cores: 8
- Dedicated verifier: one process
- Full empirical seeds: 20; implementation mutation seeds: 6

Authoritative Git SHA, allocation, and runtimes are printed in the run log.
