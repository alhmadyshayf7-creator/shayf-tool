#!/usr/bin/env bash
set -euo pipefail
PREFIX="/opt/lingokey-kali"
BINPREFIX="/usr/local/bin"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ $EUID -ne 0 ]]; then echo "Run: sudo bash install.sh"; exit 1; fi
command -v python3 >/dev/null || { echo "python3 is required"; exit 1; }
install -d "$PREFIX/lib" "$PREFIX/bin" "$PREFIX/config" "$PREFIX/data"
cp -a "$SOURCE_DIR/lib/." "$PREFIX/lib/"
cp -a "$SOURCE_DIR/bin/." "$PREFIX/bin/"
cp -a "$SOURCE_DIR/config/." "$PREFIX/config/" 2>/dev/null || true
cp -a "$SOURCE_DIR/data/." "$PREFIX/data/" 2>/dev/null || true
ln -sf "$PREFIX/bin/lingokey" "$BINPREFIX/lingokey"
ln -sf "$PREFIX/bin/lingokey-term" "$BINPREFIX/lingokey-term"
install -d /etc/profile.d
cat > /etc/profile.d/lingokey-kali.sh <<'EOF'
# LingoKey commands: lingokey / lingokey-term
EOF
printf '\nInstalled LingoKey to %s\n' "$PREFIX"
printf 'Commands: lingokey status | lingokey on | lingokey-term\n'
