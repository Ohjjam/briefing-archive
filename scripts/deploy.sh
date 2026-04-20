#!/bin/bash
# Daily deploy: copy today's briefing HTMLs into category folders,
# regenerate index, and push to GitHub.
#
# Called by the "daily-briefing-archive-deploy" scheduled task.
# Idempotent — re-runs on the same day are no-ops.
#
# Exit codes:
#   0  success (or nothing to deploy)
#   1  deploy error
#   2  archive repo not initialized (run setup.sh first)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE_DIR="$(cd "$REPO_ROOT/.." && pwd)"
TODAY="${TODAY_OVERRIDE:-$(date +%Y-%m-%d)}"

cd "$REPO_ROOT"

# --- Preflight ---
if [ ! -d .git ]; then
  echo "ERROR: archive is not a git repo. Run: bash scripts/setup.sh <user> <repo> <pat>" >&2
  exit 2
fi

if ! git remote | grep -q '^origin$'; then
  echo "ERROR: no 'origin' remote. Run setup.sh first." >&2
  exit 2
fi

# --- Copy today's briefings into category folders ---
# Source filename → target path
declare -A MAP=(
  ["ai-briefing-${TODAY}.html"]="ai/${TODAY}.html"
  ["energy-chem-briefing-${TODAY}.html"]="energy-chem/${TODAY}.html"
  ["briefing-${TODAY}.html"]="world/${TODAY}.html"
)

DEPLOYED=()
MISSING=()
for src in "${!MAP[@]}"; do
  src_path="$SOURCE_DIR/$src"
  dst_path="$REPO_ROOT/${MAP[$src]}"
  if [ -f "$src_path" ]; then
    cp "$src_path" "$dst_path"
    DEPLOYED+=("${MAP[$src]}")
  else
    MISSING+=("$src")
  fi
done

if [ ${#DEPLOYED[@]} -eq 0 ]; then
  echo "▪ No briefings for $TODAY to deploy (missing: ${MISSING[*]:-none})"
  exit 0
fi

echo "▶ Copied ${#DEPLOYED[@]} briefing(s) for $TODAY:"
for d in "${DEPLOYED[@]}"; do echo "    • $d"; done

# --- Regenerate index ---
echo "▶ Regenerating index.html"
python3 "$REPO_ROOT/scripts/generate_index.py"

# --- Commit & push ---
git add .
if git diff --cached --quiet; then
  echo "▪ No staged changes — nothing to commit (already deployed?)"
  exit 0
fi

COMMIT_MSG="archive: $TODAY briefings (${#DEPLOYED[@]} items)"
git commit -m "$COMMIT_MSG"

echo "▶ Pushing to origin/main"
git push origin main

# Extract user/repo from remote URL for friendly output
REMOTE_URL=$(git remote get-url origin)
SLUG=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[/:]([^/]+)/([^/.]+)(\.git)?$|\1/\2|' | head -1)
PAGE_USER=$(echo "$SLUG" | cut -d/ -f1)
PAGE_REPO=$(echo "$SLUG" | cut -d/ -f2)

echo ""
echo "✓ Deployed $TODAY — live at https://${PAGE_USER}.github.io/${PAGE_REPO}/"
