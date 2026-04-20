#!/bin/bash
# One-time setup: connect local archive to a GitHub repo and push initial content.
#
# Usage:
#   bash scripts/setup.sh <github_user> <repo_name> <personal_access_token> [user_email]
#
# Example:
#   bash scripts/setup.sh hyunmyung briefing-archive ghp_xxxxxxxx ate0339@gmail.com
#
# After success:
#   1. Go to https://github.com/<user>/<repo>/settings/pages
#   2. Source: "Deploy from a branch" → Branch: main / (root) → Save
#   3. Wait ~1 min, then visit https://<user>.github.io/<repo>/

set -euo pipefail

if [ "$#" -lt 3 ] || [ "$#" -gt 4 ]; then
  echo "Usage: $0 <github_user> <repo_name> <pat> [user_email]"
  exit 2
fi

GH_USER="$1"
GH_REPO="$2"
GH_PAT="$3"
GH_EMAIL="${4:-ate0339@gmail.com}"

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "▶ Initializing git repo at $REPO_ROOT"
if [ ! -d .git ]; then
  git init -b main
fi

# Local-only git config (does not affect other repos)
git config user.email "$GH_EMAIL"
git config user.name  "$GH_USER"

# Remove any existing origin and replace with PAT-embedded URL.
# Note: PAT is stored only in .git/config, which is NOT committed.
if git remote | grep -q '^origin$'; then
  git remote remove origin
fi
git remote add origin "https://${GH_USER}:${GH_PAT}@github.com/${GH_USER}/${GH_REPO}.git"

# Generate initial index
python3 "$REPO_ROOT/scripts/generate_index.py"

git add .
if ! git diff --cached --quiet; then
  git commit -m "initial: briefing archive bootstrap"
fi

echo "▶ Pushing to origin/main"
git push -u origin main

echo ""
echo "✓ Setup complete."
echo ""
echo "Next steps (manual, 2 clicks):"
echo "  1. Open: https://github.com/${GH_USER}/${GH_REPO}/settings/pages"
echo "  2. Source = 'Deploy from a branch', Branch = 'main' / '(root)', Save"
echo ""
echo "After ~1 minute, your archive will be live at:"
echo "  https://${GH_USER}.github.io/${GH_REPO}/"
