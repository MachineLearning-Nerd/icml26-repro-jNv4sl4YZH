#!/usr/bin/env bash
# Start the full CCP sweep only after every strict Claim 2 gate passes.

set -euo pipefail

cd "$(dirname "$0")/../.."

while pgrep -f '[r]un_author_ca.py' >/dev/null \
   || pgrep -f '[t]rackio logbook run --page Claim 2 --title Full released conformal-aggregation protocol' >/dev/null; do
  sleep 30
done

source .venv/bin/activate

trackio logbook run \
  --page "Claim 2" \
  --title "Independent full CA raw verification" \
  -- python repro/src/verify_ca_results.py \
  --raw-dir outputs/raw/author_ca \
  --output outputs/claim2_independent.json

python - <<'PY'
import json
from pathlib import Path

result = json.loads(Path("outputs/claim2_independent.json").read_text())
summary = result["summary"]

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

trackio logbook run \
  --page "Claim 3" \
  --title "Full released cross-conformal protocol" \
  -- python repro/src/run_author_ccp.py \
  --source upstream \
  --output-dir outputs/raw/author_ccp
