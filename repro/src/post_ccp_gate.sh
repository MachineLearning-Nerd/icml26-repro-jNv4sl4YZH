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

# This long-running worker may have started from the pre-hardening runner whose
# progress messages rendered the resolved output path.  Trackio captures that
# stdout only after the run exits, so normalize just those output links before
# any publication hygiene check.  The command/source provenance stays intact.
paper_root="$(pwd -P)"
sed -i "s|${paper_root}/||g" \
  .trackio/logbook/pages/claim-3/page.md

source .venv/bin/activate

trackio logbook run \
  --page "Methods & source audit" \
  --title "Released OpenML CA input fingerprint audit" \
  -- python repro/src/verify_ca_inputs.py \
  --source upstream \
  --output outputs/ca_input_audit.json

trackio logbook run \
  --page "Methods & source audit" \
  --title "Released CA P2E theorem-domain audit" \
  -- python repro/src/verify_ca_p2e_domains.py \
  --source upstream \
  --output outputs/ca_p2e_domain_audit.json

trackio logbook run \
  --page "Methods & source audit" \
  --title "Released source and dataset manifest audit" \
  -- python repro/src/verify_source_manifest.py \
  --source upstream \
  --output outputs/source_manifest_audit.json

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
assert summary["invalid_metric_row_count"] == 0
print("Claim 3 raw-cell completeness gate passed")
PY

trackio logbook run \
  --page "Methods & source audit" \
  --title "WECA independent-tuning audit" \
  -- python repro/src/verify_weca_independence.py \
  --source upstream \
  --output outputs/weca_independence_audit.json

trackio logbook run \
  --page "Methods & source audit" \
  --title "Primary TeX table fixture audit" \
  -- python repro/src/verify_paper_table_fixture.py \
  --output outputs/paper_table_fixture_audit.json

trackio logbook run \
  --page "Methods & source audit" \
  --title "Paper and released-code calibrator contract audit" \
  -- python repro/src/verify_ccp_calibrator_contract.py \
  --source upstream \
  --output outputs/ccp_calibrator_contract_audit.json

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
assert summary["comparison_count"] == 122
assert summary["scalar_comparison_count"] == 488
assert summary["all_unaffected_within_tolerance"]
assert summary["all_outside_tolerance_cells_accounted_for"]
assert summary["all_source_table_replays_within_tolerance"]
assert summary["unaffected_comparison_count"] == 94
assert summary["unaffected_within_tolerance_count"] == 94
assert summary["unaffected_scalar_comparison_count"] == 376
assert summary["unaffected_within_tolerance_scalar_count"] == 376
assert summary["known_discrepancy_comparison_count"] == 27
assert summary["known_discrepancy_scalar_comparison_count"] == 108
assert summary["source_table_replay_comparison_count"] == 18
assert summary["source_table_replay_within_tolerance_count"] == 18
assert summary["source_table_replay_scalar_comparison_count"] == 72
assert summary["source_table_replay_within_tolerance_scalar_count"] == 72
assert summary["known_ca_dispersion_discrepancy_count"] == 1
assert summary["known_ca_dispersion_scalar_count"] == 4
assert summary["known_ca_dispersion_within_tolerance_scalar_count"] == 3
assert summary["known_ca_dispersion_outside_tolerance_count"] == 1
assert summary["unexpected_outside_tolerance_count"] == 0
print(
    "All 376 unaffected scalars pass; the one CA finite-seed SD discrepancy "
    "and all 27 paper/source-discrepant cells are explicitly classified; "
    "the reversible source-column swap replays all 72 available scalars"
)
PY

trackio logbook run \
  --page "Claim 4" \
  --title "Exchangeable and randomized e-merge coverage certificate" \
  -- python repro/src/verify_e_merge_coverage.py \
  --output outputs/claim3_independent_e_merge.json

trackio logbook run \
  --page "Methods & source audit" \
  --title "Six anchored-claim theorem and mechanism audit" \
  -- python repro/src/verify_anchored_claims.py \
  --output outputs/anchored_claims_mechanism.json

trackio logbook run \
  --page "Conclusion" \
  --title "Build evidence-derived final summary" \
  -- python repro/src/render_final_logbook.py \
  --output outputs/final_logbook_cells.json

for claim in 1 2 3 4 5 6; do
  trackio logbook cell markdown \
    --page "Claim $claim" \
    --title "Claim $claim verdict" \
    "$(jq -r --arg key "claim_$claim" '.[$key]' outputs/final_logbook_cells.json)"
done

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
