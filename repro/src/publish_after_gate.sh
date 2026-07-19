#!/usr/bin/env bash
# Publish only after the complete local gate, then verify both public remotes.

set -euo pipefail

cd "$(dirname "$0")/../.."
source .venv/bin/activate

hf_space="DineshAI/jNv4sl4YZH"
gh_repo="MachineLearning-Nerd/icml26-repro-jNv4sl4YZH"
bundle="outputs/jNv4sl4YZH_full_evidence_bundle.jsonl"

preflight() {
  hf auth whoami | rg -q 'user=DineshAI'
  gh auth status --hostname github.com >/dev/null
  jq -e '
    .openreview_id == "jNv4sl4YZH" and
    .arxiv_id == "2606.03600" and
    .paper.openreview_id == "jNv4sl4YZH" and
    .paper.arxiv_id == "2606.03600" and
    (.tags | index("icml2026-repro")) and
    (.tags | index("paper-jNv4sl4YZH"))
  ' .trackio/metadata.json >/dev/null
  rg -Fxq '.trackio/metadata.json' .gitignore
  rg -Fxq 'outputs/*_evidence_bundle.jsonl' .gitignore
  rg -Fxq 'outputs/raw/' .gitignore
  # `upstream/` is a separate Git checkout.  Ignoring the whole directory
  # prevents `git add -A` from publishing a broken embedded-repository gitlink;
  # fresh clones obtain the exact source with the pinned commands in README.md.
  rg -Fxq 'upstream/' .gitignore
  printf '%s\n' 'Publication preflight passed (no external writes).'
}

if [[ "${1:-}" == "--preflight" ]]; then
  preflight
  exit 0
fi

preflight

python - <<'PY'
import json
from pathlib import Path

from repro.src.prepublish_gate import (
    hygiene_gate,
    validate_artifact_bundle,
    validate_required_local_artifact,
)

gate = json.loads(Path("outputs/prepublish_gate.json").read_text(encoding="utf-8"))
assert gate["paper"] == "jNv4sl4YZH"
assert gate["claims"] == 6
assert gate["claims_source_url"] == (
    "https://huggingface.co/spaces/ICML-2026-agent-repro/challenge/"
    "resolve/main/claims_anchored.json"
)
assert gate["claims_source_urls"] == {
    "anchored": (
        "https://huggingface.co/spaces/ICML-2026-agent-repro/challenge/"
        "resolve/main/claims_anchored.json"
    ),
    "fallback": (
        "https://huggingface.co/spaces/ICML-2026-agent-repro/challenge/"
        "resolve/main/claims.json"
    ),
}
assert gate["live_claims_verified"] == 6
assert gate["maximum_points"] == 12
assert gate["tests_passed"] is True
assert gate["publication_gate_passed"] is True
assert Path(gate["trackio_artifact_bundle"]).is_file()
assert len(gate["artifact_paths"]) == 21
assert set(gate["artifact_paths"]) == set(gate["artifact_sha256"])
assert validate_artifact_bundle(
    gate["trackio_artifact_bundle"], tuple(gate["artifact_paths"])
) == gate["trackio_artifact_bundle_sha256"]
assert "FULL_GATE_READY: jNv4sl4YZH" in Path(
    ".trackio/logbook/pages/conclusion/page.md"
).read_text(encoding="utf-8")
hygiene = hygiene_gate()
metadata = json.loads(Path(".trackio/metadata.json").read_text(encoding="utf-8"))
validate_required_local_artifact(
    metadata, "outputs/jNv4sl4YZH_full_evidence_bundle.jsonl"
)
assert hygiene["local_path_artifact_count"] >= 1
print(
    "Verified fresh fail-closed gate, all 21 bundle records, registered bundle, "
    "conclusion marker, and hygiene"
)
PY

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git init -b main
fi
git branch -M main
git config user.name "MachineLearning-Nerd"
git config user.email "MachineLearning-Nerd@users.noreply.github.com"
git add -A
git diff --cached --check
local_home_prefix="/home/${USER}/"
if git grep --cached -n -F "$local_home_prefix" -- .; then
  printf '%s\n' 'Refusing GitHub push: staged files contain a local absolute path.' >&2
  exit 1
fi
if ! git diff --cached --quiet; then
  git commit -m "Reproduce jNv4sl4YZH at full released scale"
fi

remote_url="https://github.com/${gh_repo}.git"
if gh repo view "$gh_repo" --json url >/dev/null 2>&1; then
  if git remote get-url origin >/dev/null 2>&1; then
    git remote set-url origin "$remote_url"
  else
    git remote add origin "$remote_url"
  fi
  git push -u origin main
else
  gh repo create "$gh_repo" --public --source=. --remote=origin --push
fi

# Hand the gate-complete paper to the single shared HF publisher only after the
# first GitHub push is complete.  Trackio publication rewrites artifact links in
# local logbook pages, so this ordering prevents the shared drain from racing
# the initial git staging/commit.  The enqueue helper revalidates the fail-closed
# gate and marker, writes atomically, and is idempotent.
python ../../icml-2026-reproduction-challenge/scripts/enqueue_backlog.py \
  --orid jNv4sl4YZH \
  --slug icml26-repro-jNv4sl4YZH-p2e-calibration \
  --paper-dir . \
  --gate outputs/prepublish_gate.json \
  --marker-file .trackio/logbook/pages/conclusion/page.md

# The shared drain is the only HF publisher, which preserves queue order and
# avoids two sessions consuming or racing for the same Space-creation slot.
printf 'Queued for the shared HF publisher; waiting for %s ...\n' "$hf_space"
until hf spaces info "$hf_space" --format json >/dev/null 2>&1; do
  sleep 60
done

space_info="$(hf spaces info "$hf_space" --format json)"
jq -e --arg expected "$hf_space" '
  .id == $expected and
  .private == false and
  (.sha | type == "string" and length > 0) and
  (.tags | index("icml2026-repro")) and
  (.tags | index("paper-jNv4sl4YZH"))
' <<<"$space_info" >/dev/null

artifact_bucket="$(jq -er '.artifacts_bucket | select(type == "string" and length > 0)' .trackio/metadata.json)"
bundle_size="$(stat -c '%s' "$bundle")"
bucket_info="$(hf buckets list "$artifact_bucket" --recursive --format json)"
jq -e \
  --arg path "logbook-files/$bundle" \
  --argjson size "$bundle_size" \
  'any(.[]; .type == "file" and .path == $path and .size == $size)' \
  <<<"$bucket_info" >/dev/null

publish_check_dir="$(mktemp -d)"
trap 'case "$publish_check_dir" in /tmp/*) rm -rf -- "$publish_check_dir" ;; esac' EXIT
hf download "$hf_space" \
  --type space \
  --include 'pages/conclusion/page.md' \
  --local-dir "$publish_check_dir" \
  --quiet >/dev/null
rg -Fq 'FULL_GATE_READY: jNv4sl4YZH' \
  "$publish_check_dir/pages/conclusion/page.md"

# Trackio rewrites local artifact placeholders to public bucket links during
# publication. Commit those public-safe pages, but never its local metadata.
git add -A
git diff --cached --check
if git grep --cached -n -F "$local_home_prefix" -- .; then
  printf '%s\n' 'Refusing final GitHub push: staged files contain a local absolute path.' >&2
  exit 1
fi
if ! git diff --cached --quiet; then
  git commit -m "Record verified Hugging Face publication links"
fi
git push -u origin main

printf 'GitHub: https://github.com/%s @ %s\n' "$gh_repo" "$(git rev-parse HEAD)"
printf 'Space: https://huggingface.co/spaces/%s @ %s\n' "$hf_space" "$(jq -r '.sha' <<<"$space_info")"
printf 'Artifacts: https://huggingface.co/buckets/%s (%s bytes verified)\n' "$artifact_bucket" "$bundle_size"
