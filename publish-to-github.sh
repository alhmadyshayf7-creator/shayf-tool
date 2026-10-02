#!/usr/bin/env bash
set -euo pipefail
: "${GITHUB_REPO:?Set GITHUB_REPO like USER/lingokey-kali}"
command -v git >/dev/null || { echo 'git is required'; exit 1; }
command -v gh >/dev/null || { echo 'GitHub CLI (gh) is required. Run: sudo apt install gh'; exit 1; }
if ! gh auth status >/dev/null 2>&1; then
  echo 'Run: gh auth login'
  exit 1
fi
cd "$(dirname "$0")"
git init
git add .
git commit -m 'Initial LingoKey Kali release' || true
gh repo create "$GITHUB_REPO" --public --source=. --remote=origin --push
printf '\nGitHub repository created: https://github.com/%s\n' "$GITHUB_REPO"
