# Exact command and environment

Fixed command inherited by every node:

```bash
uv run --frozen python repro/src/run_campaign.py
```

- Python exactly 3.12.x; repository-level `uv.lock`
- Hugging Face `cpu-upgrade`
- Image: `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`
- Estimated useful cores for cumulative suite: 8
- Dedicated verifier parallelism: 1 process
- Released CCP seeds: 45–144 (100 seeds)

The run log records authoritative Git SHA, actual allocation, per-command
runtime, and total runtime.
