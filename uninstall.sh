#!/usr/bin/env bash
set -euo pipefail
if [[ $EUID -ne 0 ]]; then echo "Run: sudo bash uninstall.sh"; exit 1; fi
rm -f /usr/local/bin/lingokey /usr/local/bin/lingokey-term /etc/profile.d/lingokey-kali.sh
rm -rf /opt/lingokey-kali
echo "LingoKey removed. User data in ~/.local/share/lingokey-kali was preserved."
