"""Desktop notification helper (notify-send)."""
from __future__ import annotations

import shutil
import subprocess


def notify(message: str) -> None:
    """Send a desktop notification and print to stdout."""
    print(message, flush=True)
    if shutil.which("notify-send"):
        subprocess.run(["notify-send", "OpenVox", message], check=False)
