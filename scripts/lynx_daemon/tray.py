"""System tray icon (pystray + AppIndicator) and daemon orchestration."""
from __future__ import annotations

import enum
import os
import shutil
import subprocess
import webbrowser

from .config import cfg
from .notifier import notify
from .overlay import VoiceOverlay

try:
    from pynput import keyboard
except ImportError:
    keyboard = None  # type: ignore[assignment]

try:
    import pystray
    from PIL import Image, ImageDraw

    _HAS_TRAY = True
except ImportError:
    _HAS_TRAY = False


class DaemonState(enum.Enum):
    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"


# ---------------------------------------------------------------------------
# Icon generation
# ---------------------------------------------------------------------------

_ICON_COLORS = {
    DaemonState.IDLE: "#808080",
    DaemonState.RECORDING: "#E53E3E",
    DaemonState.PROCESSING: "#ED8936",
}


def _make_icon(state: DaemonState, size: int = 22) -> "Image.Image":
    """Generate a small coloured circle icon for the given state."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = 2
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=_ICON_COLORS[state],
        outline="#333333",
    )
    return img


# ---------------------------------------------------------------------------
# System tray icon
# ---------------------------------------------------------------------------

class SystemTrayIcon:
    """Manages the pystray icon in the system tray."""

    def __init__(self) -> None:
        self._state = DaemonState.IDLE
        self._icon: pystray.Icon | None = None
        self.on_quit: callable = lambda: None  # type: ignore[assignment]

    @property
    def state(self) -> DaemonState:
        return self._state

    def set_state(self, state: str | DaemonState) -> None:
        if isinstance(state, str):
            state = DaemonState(state)
        self._state = state
        if self._icon is not None:
            self._icon.icon = _make_icon(state)
            self._icon.title = f"Lynx - {state.value.capitalize()}"
            self._icon.update_menu()

    def _build_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem(
                lambda _: f"Status: {self._state.value.capitalize()}",
                None,
                enabled=False,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Open Web UI", self._on_open_web),
            pystray.MenuItem(
                "Audio Feedback",
                self._on_toggle_audio,
                checked=lambda _: cfg.audio_feedback,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._on_quit),
        )

    def _on_open_web(self, icon: object, item: object) -> None:
        webbrowser.open(cfg.api_url)

    def _on_toggle_audio(self, icon: object, item: object) -> None:
        # Toggle audio feedback at runtime (cfg is frozen, so we mutate the object directly)
        object.__setattr__(cfg, "audio_feedback", not cfg.audio_feedback)
        if self._icon is not None:
            self._icon.update_menu()

    def _on_quit(self, icon: object, item: object) -> None:
        self.on_quit()
        if self._icon is not None:
            self._icon.stop()

    def run(self) -> None:
        """Block the calling thread running the tray icon event loop."""
        self._icon = pystray.Icon(
            name="lynx-daemon",
            icon=_make_icon(DaemonState.IDLE),
            title="Lynx - Idle",
            menu=self._build_menu(),
        )
        self._icon.run()


# ---------------------------------------------------------------------------
# Daemon entry point
# ---------------------------------------------------------------------------

def _warn_wayland_hotkey(exc: Exception) -> None:
    session = os.getenv("XDG_SESSION_TYPE", "unknown")
    print(f"[Lynx] Hotkey listener failed: {exc}", flush=True)
    if session == "wayland" or os.getenv("WAYLAND_DISPLAY"):
        print("[Lynx] Wayland detected. To enable global hotkeys, add your user to the input group:", flush=True)
        print("[Lynx]   sudo usermod -aG input $USER   (then log out and back in)", flush=True)
        print("[Lynx] Or ensure XWayland is running and DISPLAY is set.", flush=True)
    else:
        print("[Lynx] Check that a display server (X11/Wayland) is available.", flush=True)


def run_daemon() -> None:
    """Start the full daemon: tray icon, pynput listener, and overlay."""
    if not shutil.which("arecord"):
        raise SystemExit("arecord not found. Install alsa-utils.")

    # Lazy import to avoid circular dependency
    from .recorder import PushToTalk

    overlay = VoiceOverlay(enabled=cfg.overlay_enabled)

    if _HAS_TRAY and keyboard is not None:
        # Full mode: tray icon on main thread, pynput in daemon thread
        tray = SystemTrayIcon()
        ptt = PushToTalk(overlay=overlay, tray=tray)

        listener = keyboard.Listener(on_press=ptt.on_press, on_release=ptt.on_release)
        listener.daemon = True
        try:
            listener.start()
        except Exception as exc:
            _warn_wayland_hotkey(exc)
            overlay.stop()
            return

        notify(f"Lynx push-to-talk active on [{cfg.hotkey}]")

        def on_quit() -> None:
            listener.stop()
            overlay.stop()

        tray.on_quit = on_quit
        try:
            tray.run()  # blocks until quit
        except Exception as exc:
            print(f"[Lynx] System tray failed: {exc}", flush=True)
            print("[Lynx] On GNOME Wayland, install: sudo apt install gir1.2-ayatanaappindicator3-0.1", flush=True)
            # Fall back to tray-less mode — keep listener running
            notify(f"Lynx running without tray (hotkey: [{cfg.hotkey}])")
            try:
                listener.join()
            finally:
                overlay.stop()

    elif keyboard is not None:
        # Fallback: no tray, pynput on main thread (original behaviour)
        ptt = PushToTalk(overlay=overlay, tray=None)
        notify(f"Push-to-talk active on [{cfg.hotkey}] (no tray icon)")

        try:
            with keyboard.Listener(
                on_press=ptt.on_press, on_release=ptt.on_release
            ) as listener:
                listener.join()
        except Exception as exc:
            _warn_wayland_hotkey(exc)
        finally:
            overlay.stop()
    else:
        raise SystemExit(
            "Missing dependency: pynput. Run `pip install -r requirements-hotkey.txt`."
        )
