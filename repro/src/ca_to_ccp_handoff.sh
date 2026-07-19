#!/usr/bin/env bash
# Start the full CCP sweep only after every strict Claim 2 gate passes.

set -euo pipefail

cd "$(dirname "$0")/../.."

source .venv/bin/activate

# Serialize the entire CA verification -> CCP transition. Worker-specific locks
# below close the narrower check/start race; this owner lock also prevents two
# watcher copies from writing the same independent-verifier/Trackio evidence.
exec 9>/tmp/jNv4sl4YZH-ca-to-ccp-owner.lock
if ! flock -n 9; then
  printf '%s another CA-to-CCP handoff owner is already active; exiting\n' \
    "$(date --iso-8601=seconds)"
  exit 0
fi

ca_is_active() {
  pgrep -f '[r]un_author_ca.py' >/dev/null \
    || pgrep -f '[t]rackio logbook run --page Claim 2 --title Full released conformal-aggregation protocol' >/dev/null
}

all_ca_outputs_exist() {
  [[ -f outputs/raw/author_ca/dataset_361237.json \
    && -f outputs/raw/author_ca/dataset_361235.json \
    && -f outputs/raw/author_ca/dataset_361244.json \
    && -f outputs/raw/author_ca/dataset_361234.json ]]
}

# The currently active legacy process cannot checkpoint inside its last
# dataset, so do not disturb it. If it ever exits without promoting all four
# final artifacts, relaunch the current per-seed-checkpointed wrapper. Existing
# complete artifacts are revalidated and retained, making recovery idempotent.
while true; do
  while ca_is_active; do
    sleep 30
  done
  if all_ca_outputs_exist; then
    break
  fi
  printf '%s missing CA output after worker exit; starting resumable recovery\n' \
    "$(date --iso-8601=seconds)"
  if ! flock -n /tmp/jNv4sl4YZH-ca-worker.lock trackio logbook run \
      --page "Claim 2" \
      --title "Full released conformal-aggregation protocol" \
      -- python repro/src/run_author_ca.py \
      --source upstream \
      --output-dir outputs/raw/author_ca; then
    printf '%s resumable CA recovery exited nonzero; retrying in 60 seconds\n' \
      "$(date --iso-8601=seconds)" >&2
    sleep 60
  fi
done

trackio logbook run \
  --page "Claim 2" \
  --title "Independent full CA raw verification" \
  -- python repro/src/verify_ca_results.py \
  --raw-dir outputs/raw/author_ca \
  --output outputs/claim2_independent.json

python - <<'PY'
import json
from pathlib import Path

from repro.src.prepublish_gate import assert_exact_ca_protocol

result = json.loads(Path("outputs/claim2_independent.json").read_text())
summary = result["summary"]

assert_exact_ca_protocol(result["protocol"])
assert summary["all_four_tasks_present"]
assert summary["all_full_seed_method_cells_present"]
assert all(summary["dataset_integrity"].values())
assert summary["exact_cell_set"]
assert result["rows_seen"] == 1_920
assert summary["expected_rows"] == 1_920
assert summary["observed_unique_cells"] == 1_920
assert summary["duplicate_cell_count"] == 0
assert summary["unexpected_row_count"] == 0
assert summary["nonfinite_row_count"] == 0

assert summary["comparison_count"] == 24
assert summary["p2e_shorter_count"] == 24
assert summary["substantial_efficiency_gain_count"] == 24
assert summary["all_substantial_efficiency_gains"]
assert summary["minimum_substantial_relative_reduction"] == 0.10
assert summary["minimum_observed_relative_reduction"] >= 0.10

assert summary["p2e_empirical_coverage_cell_count"] == 8
assert summary["p2e_empirical_coverage_pass_count"] == 8
assert summary["all_p2e_empirical_coverage_within_tolerance"]
assert summary["empirical_coverage_shortfall_tolerance"] == 0.02

print("Claim 2 strict structural, efficiency, and coverage gates passed")
PY

ccp_is_active() {
  pgrep -f '[r]un_author_ccp.py' >/dev/null \
    || pgrep -f '[t]rackio logbook run --page Claim 3 --title Full released cross-conformal protocol' >/dev/null
}

all_ccp_outputs_exist() {
  [[ -f outputs/raw/author_ccp/boston.json \
    && -f outputs/raw/author_ccp/abalone.json \
    && -f outputs/raw/author_ccp/parkinson.json ]]
}

# The CCP runner promotes one complete seed checkpoint at a time and revalidates
# every retained seed/output on resume. Keep a single worker alive until all
# three paper-scale artifacts exist; never start a competing sweep.
while true; do
  while ccp_is_active; do
    sleep 30
  done
  if all_ccp_outputs_exist; then
    break
  fi
  printf '%s starting/resuming checkpointed full CCP worker\n' \
    "$(date --iso-8601=seconds)"
  if ! flock -n /tmp/jNv4sl4YZH-ccp-worker.lock trackio logbook run \
      --page "Claim 3" \
      --title "Full released cross-conformal protocol" \
      -- python repro/src/run_author_ccp.py \
      --source upstream \
      --output-dir outputs/raw/author_ccp; then
    printf '%s checkpointed CCP worker exited nonzero; retrying in 60 seconds\n' \
      "$(date --iso-8601=seconds)" >&2
    sleep 60
  fi
done
