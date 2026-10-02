# LingoKey Kali

LingoKey Kali is a Linux/Kali-focused Arabic-English input and terminal assistant.

## What it does

- Arabic/English language detection.
- Arabic <-> English keyboard-layout correction.
- Offline-first dictionary translation, with optional Argos Translate backend.
- Clipboard-friendly CLI commands.
- `lingokey-term`: interactive shell wrapper that keeps the original terminal output and can show Arabic translations for English lines.
- Terminal error analysis and safe command suggestions with an explanation of purpose, reason, impact and risk.
- Single toggle state: `lingokey on|off|toggle|status`.
- Optional X11 global hotkey: `Ctrl+Alt+Space` via xbindkeys.

## Install on Kali

From a cloned/downloaded repo:

```bash
cd LingoKey-Kali
sudo bash install.sh
lingokey doctor
lingokey on
```

Then start the translated terminal:

```bash
lingokey-term
```

## GitHub one-command install

After this repository is published as `<USER>/<REPO>` on GitHub, the intended install command is:

```bash
curl -fsSL https://raw.githubusercontent.com/<USER>/<REPO>/main/install.sh -o /tmp/lingokey-install.sh && sudo bash /tmp/lingokey-install.sh
```

Do not pipe an installer from a repository you do not trust directly into `bash`.

## Optional real offline translation

Install Argos Translate in a separate Python environment and install the `ar<->en` model. LingoKey automatically uses Argos when available and falls back to its local glossary otherwise.

## Optional local AI

If Ollama is installed and a compatible local model is available, the Terminal Assistant can use it. If not, deterministic safety-focused rules are used.

## X11 hotkey

```bash
./shell/enable-x11-hotkey.sh
```

On Wayland, use the desktop environment's global-shortcut facility to run `lingokey toggle`.

## Safety

The assistant never executes suggested commands automatically. It only prints a proposal and explains what it does.
"# shayf-tool"  
