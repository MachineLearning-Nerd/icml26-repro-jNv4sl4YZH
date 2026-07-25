# Exact command and environment

Fixed command on every experiment node:

```text
uv run --frozen python repro/src/run_campaign.py
```

Environment: repository-level `.venv`, Python `==3.12.*`, exact `uv.lock`.
Backend: Hugging Face `cpu-upgrade`; estimate 8 useful CPU cores for the
cumulative campaign. The run log records actual allocation, Git SHA, and exact
runtime.
