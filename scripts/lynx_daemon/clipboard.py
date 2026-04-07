"""Clipboard copy and text-insertion helpers (Wayland + X11)."""
from __future__ import annotations

import os
import shutil
import subprocess
import time

from .config import cfg


def _is_wayland() -> bool:
    return (
        os.getenv("XDG_SESSION_TYPE", "").lower() == "wayland"
        or bool(os.getenv("WAYLAND_DISPLAY"))
    )


def copy_to_clipboard(text: str) -> bool:
    """Copy *text* to the system clipboard. Returns ``True`` on success."""
    if _is_wayland():
        if shutil.which("wl-copy"):
            subprocess.run(["wl-copy"], input=text.encode(), check=False)
            return True
        # Fall through to xclip via XWayland if wl-copy not available
    if shutil.which("xclip"):
        subprocess.run(
            ["xclip", "-selection", "clipboard"], input=text.encode(), check=False
        )
        return True
    if shutil.which("xsel"):
        subprocess.run(
            ["xsel", "--clipboard", "--input"], input=text.encode(), check=False
        )
        return True
    # Last resort on Wayland: try wl-copy even if not detected above
    if shutil.which("wl-copy"):
        subprocess.run(["wl-copy"], input=text.encode(), check=False)
        return True
    return False


def paste_into_active_window(text: str) -> bool:
    """Type *text* directly into the currently focused window.

    On Wayland the priority is:
    1. ydotool — works with *all* windows (native Wayland and XWayland)
    2. wtype  — only works with native Wayland windows
    3. clipboard paste via wl-copy + wtype Ctrl+V — universal fallback
    4. xdotool — only works with XWayland windows (needs DISPLAY)
    """
    if not cfg.auto_paste:
        return False

    # Brief pause to let window focus settle — important when triggered
    # via SIGUSR1 / custom system shortcut rather than held hotkey.
    time.sleep(0.15)

    if _is_wayland():
        # ydotool works at the kernel /dev/uinput level, so it types into
        # ANY focused window regardless of Wayland vs XWayland.
        if shutil.which("ydotool"):
            return (
                subprocess.run(
                    ["ydotool", "type", "--", text], check=False
                ).returncode == 0
            )
        # wtype only works with native Wayland windows.
        if shutil.which("wtype"):
            return subprocess.run(["wtype", text], check=False).returncode == 0
        # Fallback: copy, then emulate Ctrl+V via wtype.
        if copy_to_clipboard(text) and shutil.which("wtype"):
            time.sleep(0.05)
            return (
                subprocess.run(
                    ["wtype", "-M", "ctrl", "v", "-m", "ctrl"], check=False
                ).returncode == 0
            )
        # Last resort: xdotool via XWayland (only for XWayland apps).
        if shutil.which("xdotool"):
            return (
                subprocess.run(
                    ["xdotool", "type", "--clearmodifiers", text], check=False
                ).returncode == 0
            )
        return False

    # X11 path
    if shutil.which("xdotool"):
        return (
            subprocess.run(
                ["xdotool", "type", "--clearmodifiers", text], check=False
            ).returncode == 0
        )

    return False
