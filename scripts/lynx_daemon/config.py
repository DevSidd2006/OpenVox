"""Daemon configuration loaded from environment / .env file."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

try:
    from pynput import keyboard
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: pynput. Run `pip install -r requirements-hotkey.txt`."
    ) from exc

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def _bool_env(key: str, default: str = "true") -> bool:
    return os.getenv(key, default).strip().lower() == "true"


@dataclass(frozen=True)
class DaemonConfig:
    api_url: str
    hotkey: str
    style: str
    context: str
    language: str
    auto_paste: bool
    insert_mode: str
    overlay_enabled: bool
    # Phase 1
    audio_feedback: bool
    overlay_position: str
    vad_enabled: bool
    vad_silence_timeout: float
    vad_aggressiveness: int


cfg = DaemonConfig(
    api_url=os.getenv("WILLOW_CLONE_URL", "http://127.0.0.1:18080"),
    hotkey=os.getenv("WILLOW_HOTKEY", "ctrl+space"),
    style=os.getenv("WILLOW_STYLE", "professional"),
    context=os.getenv("WILLOW_CONTEXT", "email"),
    language=os.getenv("WILLOW_LANGUAGE", "en"),
    auto_paste=_bool_env("WILLOW_AUTO_PASTE"),
    insert_mode=os.getenv("WILLOW_INSERT_MODE", "paste").lower(),
    overlay_enabled=_bool_env("WILLOW_OVERLAY"),
    audio_feedback=_bool_env("WILLOW_AUDIO_FEEDBACK"),
    overlay_position=os.getenv("WILLOW_OVERLAY_POSITION", "top-right").lower(),
    vad_enabled=_bool_env("WILLOW_VAD_ENABLED"),
    vad_silence_timeout=float(os.getenv("WILLOW_VAD_SILENCE_TIMEOUT", "3")),
    vad_aggressiveness=int(os.getenv("WILLOW_VAD_AGGRESSIVENESS", "2")),
)


# ---------------------------------------------------------------------------
# Hotkey helpers
# ---------------------------------------------------------------------------

_ALIASES = {
    "control": "ctrl",
    "option": "alt",
    "return": "enter",
    "esc": "escape",
}


def normalize_hotkey(raw: str) -> set[str]:
    """Parse a hotkey string like ``ctrl+space`` into a set of tokens."""
    keys: set[str] = set()
    for part in raw.lower().replace("<", "").replace(">", "").split("+"):
        token = part.strip()
        if not token:
            continue
        keys.add(_ALIASES.get(token, token))
    return keys


def token_from_key(key: keyboard.Key | keyboard.KeyCode) -> str | None:
    """Extract a normalised string token from a pynput key event."""
    if isinstance(key, keyboard.KeyCode):
        return key.char.lower() if key.char else None

    name = str(key).replace("Key.", "")
    if name.startswith("ctrl"):
        return "ctrl"
    if name.startswith("alt"):
        return "alt"
    if name.startswith("cmd"):
        return "cmd"
    mapping = {"space": "space", "enter": "enter", "esc": "escape"}
    return mapping.get(name, name)
