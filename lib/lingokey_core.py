#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

APP_DIR = Path(os.environ.get("LINGOKEY_HOME", Path.home() / ".local" / "share" / "lingokey-kali"))
STATE_FILE = APP_DIR / "state.json"
DICT_FILE = APP_DIR / "dictionary.json"
CONFIG_FILE = APP_DIR / "config.json"

ARABIC_RE = re.compile(r"[\u0600-\u06FF]")
LATIN_RE = re.compile(r"[A-Za-z]")
ANSI_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

# Standard Arabic 101 keyboard layout mapping.
AR_TO_EN: Dict[str, str] = {
    "ض":"q","ص":"w","ث":"e","ق":"r","ف":"t","غ":"y","ع":"u","ه":"i","خ":"o","ح":"p","ج":"[","د":"]",
    "ش":"a","س":"s","ي":"d","ب":"f","ل":"g","ا":"h","ت":"j","ن":"k","م":"l","ك":";","ط":"'",
    "ئ":"z","ء":"x","ؤ":"c","ر":"v","لا":"b","ى":"n","ة":"m","و":",","ز":".","ظ":"/",
}
EN_TO_AR = {v:k for k,v in AR_TO_EN.items() if len(k) == 1}

DEFAULT_DICT = {
    "مرحبا": "Hello",
    "السلام عليكم": "Peace be upon you",
    "شكرا": "Thank you",
    "كيف حالك": "How are you?",
    "جامعة": "University",
    "شبكة": "Network",
    "خطأ": "Error",
    "تحذير": "Warning",
    "تم": "Done",
    "المضيف يعمل": "Host is up",
}

@dataclass
class Suggestion:
    command: str
    what: str
    why: str
    impact: str
    risk: str


def ensure_home() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    if not DICT_FILE.exists():
        DICT_FILE.write_text(json.dumps(DEFAULT_DICT, ensure_ascii=False, indent=2), encoding="utf-8")
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(json.dumps({"show_original": True, "auto_translate_terminal": True}, indent=2), encoding="utf-8")
    if not STATE_FILE.exists():
        STATE_FILE.write_text(json.dumps({"enabled": False}, indent=2), encoding="utf-8")


def set_enabled(value: bool) -> None:
    ensure_home()
    STATE_FILE.write_text(json.dumps({"enabled": bool(value)}, indent=2), encoding="utf-8")


def is_enabled() -> bool:
    ensure_home()
    try:
        return bool(json.loads(STATE_FILE.read_text(encoding="utf-8")).get("enabled", False))
    except Exception:
        return False


def load_dictionary() -> Dict[str, str]:
    ensure_home()
    try:
        data = json.loads(DICT_FILE.read_text(encoding="utf-8"))
        return {str(k): str(v) for k, v in data.items()}
    except Exception:
        return dict(DEFAULT_DICT)


def add_dictionary(source: str, target: str) -> None:
    d = load_dictionary()
    d[source] = target
    DICT_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def detect_language(text: str) -> str:
    ar = len(ARABIC_RE.findall(text))
    en = len(LATIN_RE.findall(text))
    if ar and en:
        return "mixed"
    if ar:
        return "ar"
    if en:
        return "en"
    return "unknown"


def keyboard_fix(text: str, direction: str = "auto") -> str:
    # Preserve spaces/punctuation and only remap keyboard characters.
    if direction == "auto":
        lang = detect_language(text)
        if lang == "ar":
            direction = "ar2en"
        elif lang == "en":
            direction = "en2ar"
        else:
            return text
    table = AR_TO_EN if direction == "ar2en" else EN_TO_AR
    return "".join(table.get(ch, ch) for ch in text)


def _regex_sub_dictionary(text: str, mapping: Dict[str, str]) -> str:
    result = text
    for src in sorted(mapping, key=len, reverse=True):
        result = re.sub(re.escape(src), mapping[src], result, flags=re.IGNORECASE if src.isascii() else 0)
    return result


def translate(text: str, target: Optional[str] = None) -> str:
    lang = detect_language(text)
    if target is None:
        target = "en" if lang == "ar" else "ar" if lang == "en" else "en"

    # Optional real local backend via Argos Translate, if installed and a model is available.
    try:
        import argostranslate.translate as argos_translate  # type: ignore
        result = argos_translate.translate(text, "ar" if lang == "ar" else "en", target)
        if result and result != text:
            return result
    except Exception:
        pass

    d = load_dictionary()
    if target == "en":
        return _regex_sub_dictionary(text, d)
    reverse = {v: k for k, v in d.items()}
    return _regex_sub_dictionary(text, reverse)


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def protect_tokens(text: str) -> str:
    # Mark shell/code-like tokens so translation never modifies them.
    return text


def suggest(output: str) -> List[Suggestion]:
    t = strip_ansi(output).lower()
    suggestions: List[Suggestion] = []
    if "command not found" in t:
        m = re.search(r"([\w.-]+): command not found", t)
        cmd = m.group(1) if m else "<command>"
        suggestions.append(Suggestion(
            "command -v " + cmd,
            "Checks whether the command exists in your PATH.",
            "The shell reported that the command could not be found.",
            "Only reads the current PATH; it does not change the system.",
            "Low risk.",
        ))
    if "permission denied" in t:
        suggestions.append(Suggestion(
            "ls -l <path>",
            "Shows the file permissions and owner for the affected path.",
            "A permission error usually needs inspection before changing anything.",
            "Read-only inspection.",
            "Low risk. Replace <path> with the actual path.",
        ))
    if "could not get lock" in t or "unable to acquire the dpkg frontend lock" in t:
        suggestions.append(Suggestion(
            "ps aux | grep -E 'apt|dpkg'",
            "Lists running apt/dpkg processes so you can identify the process holding the package manager lock.",
            "Another package-manager process appears to be using the lock.",
            "Read-only process inspection.",
            "Low risk.",
        ))
    if "no module named" in t:
        m = re.search(r"no module named ['\"]?([a-zA-Z0-9_.-]+)", t)
        mod = m.group(1) if m else "<module>"
        suggestions.append(Suggestion(
            f"python3 -m pip install {mod}",
            f"Installs the Python package named {mod} for the current Python environment.",
            "Python reported that the requested module is missing.",
            "Downloads and installs a Python package.",
            "Medium risk: review the package name and environment before installing it.",
        ))
    if "temporary failure resolving" in t or "could not resolve" in t:
        suggestions.append(Suggestion(
            "getent hosts deb.debian.org",
            "Checks whether DNS can resolve a Debian mirror hostname.",
            "The output indicates a DNS/name-resolution problem.",
            "Read-only DNS check.",
            "Low risk.",
        ))
    if "syntax error" in t and "bash" in t:
        suggestions.append(Suggestion(
            "bash -n <script.sh>",
            "Checks a Bash script for syntax errors without executing it.",
            "Bash reported a syntax error.",
            "Reads and parses the script without running it.",
            "Low risk, but replace <script.sh> with the intended file.",
        ))
    return suggestions


def ai_suggest(output: str) -> List[Suggestion]:
    """Optional local Ollama integration. Falls back to deterministic rules."""
    ollama = shutil.which("ollama")
    if not ollama:
        return suggest(output)
    prompt = (
        "You are a Linux terminal helper. Analyze the following output and propose only safe, "
        "diagnostic commands. Never suggest destructive commands automatically. Return JSON array "
        "with fields command, what, why, impact, risk. Output:\n" + strip_ansi(output)[-6000:]
    )
    try:
        p = subprocess.run([ollama, "run", "llama3.2:3b", prompt], capture_output=True, text=True, timeout=30)
        data = json.loads(p.stdout.strip())
        out: List[Suggestion] = []
        for item in data if isinstance(data, list) else []:
            out.append(Suggestion(
                str(item.get("command", "")), str(item.get("what", "")), str(item.get("why", "")),
                str(item.get("impact", "")), str(item.get("risk", "")),
            ))
        return out or suggest(output)
    except Exception:
        return suggest(output)
