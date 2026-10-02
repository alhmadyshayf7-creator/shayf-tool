#!/usr/bin/env bash
set -e
sudo apt install -y xbindkeys
lingokey install-hotkey
xbindkeys
printf 'Ctrl+Alt+Space toggles LingoKey on X11.\n'
