"""Improved voice-activity overlay with state labels and configurable position."""
from __future__ import annotations

import math
import os
import queue
import threading
import time

try:
    import tkinter as tk
except ImportError:
    tk = None  # type: ignore[assignment]

from .config import cfg


class VoiceOverlay:
    """Floating overlay that shows recording bars, state labels, and text previews."""

    WIDTH = 280
    HEIGHT = 56

    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled and tk is not None and bool(
            os.getenv("DISPLAY") or os.getenv("WAYLAND_DISPLAY")
        )
        self._events: queue.SimpleQueue[tuple[str, object]] = queue.SimpleQueue()
        self._thread: threading.Thread | None = None
        self._levels: list[float] = [0.05] * 20
        self._state = "idle"
        self._processing_start: float = 0.0

        if self.enabled:
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    # -- public API (thread-safe, fire-and-forget) --

    def show(self) -> None:
        if self.enabled:
            self._events.put(("show", None))

    def hide(self) -> None:
        if self.enabled:
            self._events.put(("hide", None))

    def level(self, value: float) -> None:
        if self.enabled:
            self._events.put(("level", max(0.0, min(1.0, value))))

    def set_state(self, state: str, text: str = "") -> None:
        """Set overlay state: 'listening', 'processing', 'done', 'error'."""
        if self.enabled:
            self._events.put(("state", (state, text)))

    def stop(self) -> None:
        if self.enabled:
            self._events.put(("stop", None))

    # -- internal tkinter loop --

    def _compute_position(self, screen_w: int, screen_h: int) -> tuple[int, int]:
        pos = cfg.overlay_position
        margin = 24
        if pos == "top-center":
            return (screen_w - self.WIDTH) // 2, margin
        if pos == "bottom-right":
            return screen_w - self.WIDTH - margin, screen_h - self.HEIGHT - 60
        # default: top-right
        return screen_w - self.WIDTH - margin, margin

    def _run(self) -> None:
        root = tk.Tk()
        root.withdraw()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        try:
            root.attributes("-alpha", 0.95)
        except tk.TclError:
            pass
        # Remove from taskbar (X11 only; silently ignored on Wayland)
        try:
            root.attributes("-type", "dock")
        except tk.TclError:
            pass

        w, h = self.WIDTH, self.HEIGHT
        x, y = self._compute_position(root.winfo_screenwidth(), root.winfo_screenheight())
        root.geometry(f"{w}x{h}+{x}+{y}")

        canvas = tk.Canvas(
            root, width=w, height=h, bg="#0B1020",
            highlightthickness=1, highlightbackground="#2D3B64",
        )
        canvas.pack(fill="both", expand=True)

        bar_area_h = h - 20  # reserve 20px for label
        label_text = tk.StringVar(value="")
        label = tk.Label(
            root, textvariable=label_text, bg="#0B1020", fg="#8899BB",
            font=("Inter", 8), anchor="w",
        )
        label.place(x=8, y=h - 18, width=w - 16, height=16)

        auto_hide_id: list[int | None] = [None]

        def draw_bars() -> None:
            canvas.delete("bar")
            bar_w, gap = 8, 2
            base = bar_area_h - 4

            if self._state == "processing":
                # Pulsing animation: sine wave across bars
                t = time.monotonic() - self._processing_start
                for i in range(len(self._levels)):
                    phase = i * 0.3 + t * 4.0
                    lv = 0.15 + 0.25 * (0.5 + 0.5 * math.sin(phase))
                    bh = 6 + int(lv * (base - 6))
                    x0 = 8 + i * (bar_w + gap)
                    canvas.create_rectangle(
                        x0, base - bh, x0 + bar_w, base,
                        fill="#F6AD55", width=0, tags="bar",
                    )
            else:
                for i, lv in enumerate(self._levels):
                    bh = 6 + int(lv * (base - 6))
                    x0 = 8 + i * (bar_w + gap)
                    color = "#4FD1C5" if lv < 0.75 else "#F6AD55"
                    canvas.create_rectangle(
                        x0, base - bh, x0 + bar_w, base,
                        fill=color, width=0, tags="bar",
                    )

        def tick() -> None:
            while True:
                try:
                    kind, payload = self._events.get_nowait()
                except queue.Empty:
                    break

                if kind == "show":
                    root.deiconify()
                elif kind == "hide":
                    root.withdraw()
                    self._state = "idle"
                    self._levels[:] = [0.05] * 20
                    label_text.set("")
                elif kind == "level" and isinstance(payload, float):
                    self._levels.pop(0)
                    self._levels.append(payload)
                elif kind == "state":
                    state, text = payload  # type: ignore[misc]
                    self._state = state
                    if auto_hide_id[0] is not None:
                        root.after_cancel(auto_hide_id[0])
                        auto_hide_id[0] = None
                    if state == "listening":
                        label_text.set("Listening...")
                        label.configure(fg="#4FD1C5")
                    elif state == "processing":
                        self._processing_start = time.monotonic()
                        label_text.set("Processing...")
                        label.configure(fg="#F6AD55")
                    elif state == "done":
                        label_text.set("Done!")
                        label.configure(fg="#68D391")
                        auto_hide_id[0] = root.after(1500, lambda: root.withdraw())
                    elif state == "error":
                        label_text.set("Error")
                        label.configure(fg="#FC8181")
                        auto_hide_id[0] = root.after(1500, lambda: root.withdraw())
                elif kind == "stop":
                    root.destroy()
                    return

            draw_bars()
            root.after(40, tick)

        tick()
        root.mainloop()
