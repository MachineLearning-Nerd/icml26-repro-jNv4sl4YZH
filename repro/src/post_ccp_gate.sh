#!/usr/bin/env bash
# Wait for the full released CCP source run, then execute its independent gates.

set -euo pipefail

cd "$(dirname "$0")/../.."

# Only one process may append final Trackio verdicts or own publication. This
# also makes accidental duplicate watcher launches harmless.
exec 9>/tmp/jNv4sl4YZH-post-ccp-owner.lock
if ! flock -n 9; then
  printf '%s another post-CCP gate owner is already active; exiting\n' \
    "$(date --iso-8601=seconds)"
  exit 0
fi

while true; do
  if [[ -f outputs/raw/author_ccp/boston.json \
     && -f outputs/raw/author_ccp/abalone.json \
     && -f outputs/raw/author_ccp/parkinson.json ]] \
     && ! pgrep -f '[r]un_author_ccp.py' >/dev/null \
     && ! pgrep -f '[t]rackio logbook run --page Claim 3 --title Full released cross-conformal protocol' >/dev/null; then
    break
  fi
  sleep 30
done

source .venv/bin/activate

trackio logbook run \
  --page "Claim 3" \
  --title "Independent full CCP raw verification" \
  -- python repro/src/verify_ccp_results.py \
  --raw-dir outputs/raw/author_ccp \
  --output outputs/claim3_independent.json

python - <<'PY'
import json
from pathlib import Path

from repro.src.prepublish_gate import assert_exact_ccp_protocol

result = json.loads(Path("outputs/claim3_independent.json").read_text())
summary = result["summary"]
assert_exact_ccp_protocol(result["protocol"])
assert summary["all_full_seed_cells_present"]
assert result["rows_seen"] == 11_700
assert summary["expected_rows"] == 11_700
assert all(summary["dataset_integrity"].values())
assert summary["exact_cell_set"]
assert summary["observed_unique_cells"] == 11_700
assert summary["duplicate_cell_count"] == 0
assert summary["unexpected_row_count"] == 0
assert summary["nonfinite_row_count"] == 0
print("Claim 3 raw-cell completeness gate passed")
PY

trackio logbook run \
  --page "Methods & source audit" \
  --title "Primary TeX table fixture audit" \
  -- python repro/src/verify_paper_table_fixture.py \
  --output outputs/paper_table_fixture_audit.json

trackio logbook run \
  --page "Methods & source audit" \
  --title "Paper headline comparison" \
  -- python repro/src/compare_paper_headlines.py \
  --ca outputs/claim2_independent.json \
  --ccp outputs/claim3_independent.json \
  --output outputs/paper_headline_comparison.json

python - <<'PY'
import json
from pathlib import Path

result = json.loads(Path("outputs/paper_headline_comparison.json").read_text())
summary = result["summary"]
assert summary["comparison_count"] == 98
assert summary["all_within_tolerance"]
assert summary["within_tolerance_count"] == 98
assert summary["scalar_comparison_count"] == 392
assert summary["within_tolerance_scalar_count"] == 392
print("All 392 reported scalars in 98 paper-table cells are within tolerance")
PY

trackio logbook run \
  --page "Claim 3" \
  --title "Arbitrary-dependence coupling LP" \
  -- python repro/src/verify_e_merge_coverage.py \
  --output outputs/claim3_independent_e_merge.json

trackio logbook run \
  --page "Conclusion" \
  --title "Build evidence-derived final summary" \
  -- python repro/src/render_final_logbook.py \
  --output outputs/final_logbook_cells.json

trackio logbook cell markdown \
  --page "Claim 2" \
  --title "Claim 2 verdict" \
  "$(jq -r '.claim_2' outputs/final_logbook_cells.json)"

trackio logbook cell markdown \
  --page "Claim 3" \
  --title "Claim 3 verdict" \
  "$(jq -r '.claim_3' outputs/final_logbook_cells.json)"

trackio logbook cell markdown \
  --page "Negative controls" \
  --title "Final negative-control audit" \
  "$(jq -r '.negative_controls' outputs/final_logbook_cells.json)"

trackio logbook cell markdown \
  --page "Conclusion" \
  --title "Final outcome" \
  "$(jq -r '.conclusion' outputs/final_logbook_cells.json)"

trackio logbook pin --page "Conclusion" --unpin cell_eb2f15259b0e
trackio logbook pin --page "Conclusion"

trackio logbook run \
  --page "Conclusion" \
  --title "Fail-closed full publication gate" \
  -- python repro/src/prepublish_gate.py \
  --output outputs/prepublish_gate.json

until bash repro/src/publish_after_gate.sh; do
  printf '%s verified publisher exited nonzero; retrying in 60 seconds\n' \
    "$(date --iso-8601=seconds)" >&2
  sleep 60
done
