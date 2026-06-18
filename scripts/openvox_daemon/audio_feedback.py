"""Non-blocking audio feedback using system sounds via paplay / pw-play."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .config import cfg

_SOUND_MAP = {
    "record_start": "/usr/share/sounds/freedesktop/stereo/device-added.oga",
    "record_stop": "/usr/share/sounds/freedesktop/stereo/device-removed.oga",
    "done": "/usr/share/sounds/freedesktop/stereo/complete.oga",
    "error": "/usr/share/sounds/freedesktop/stereo/dialog-error.oga",
}


def _find_player() -> str | None:
    for cmd in ("paplay", "pw-play", "aplay"):
        if shutil.which(cmd):
            return cmd
    return None


_player: str | None = _find_player()


def play(event: str) -> None:
    """Play a feedback sound for *event*. Non-blocking, fire-and-forget."""
    # Audio feedback disabled
    return
