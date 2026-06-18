#!/usr/bin/env python3
"""OpenVox push-to-talk hotkey daemon.

Delegates to the lynx_daemon package which provides:
- System tray icon (pystray)
- Improved voice overlay with state labels
- Audio feedback (start/stop/done chimes)
- VAD silence detection with auto-stop
- Push-to-talk recording via Groq API
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure the scripts/ directory is on sys.path so lynx_daemon is importable
_scripts_dir = str(Path(__file__).resolve().parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from openvox_daemon.tray import run_daemon


def main() -> None:
    run_daemon()


if __name__ == "__main__":
    main()
