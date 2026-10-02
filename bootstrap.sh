#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-}"
if [[ -z "$REPO" ]]; then
  echo "Usage: curl -fsSL https://raw.githubusercontent.com/USER/REPO/main/bootstrap.sh | bash -s -- USER/REPO"
  exit 2
fi
if [[ $EUID -eq 0 ]]; then
  SUDO=""
else
  SUDO="sudo"
fi
if ! command -v git >/dev/null 2>&1; then
  $SUDO apt-get update
  $SUDO apt-get install -y git
fi
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

git clone --depth 1 "https://github.com/${REPO}.git" "$TMP/repo"
$SUDO bash "$TMP/repo/install.sh"

printf '\nLingoKey installed. Run:\n  lingokey doctor\n  lingokey on\n  lingokey-term\n'
