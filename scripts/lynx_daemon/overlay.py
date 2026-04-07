"""Whisper Flow-style voice overlay with smooth waveform lines."""
from __future__ import annotations

import math
import os
import queue
import random
import threading
import time

try:
    import tkinter as tk
except ImportError:
    tk = None  # type: ignore[assignment]

from .config import cfg


class VoiceOverlay:
    """Floating overlay with animated waveform lines, inspired by Whisper Flow."""

    WIDTH = 340
    HEIGHT = 80
    NUM_POINTS = 48          # number of waveform sample points
    WAVE_LINES = 3           # layered waveform lines for depth

    # Color palette
    BG = "#0D0D0D"
    BORDER = "#1A1A2E"
    WAVE_COLORS_LISTEN = ["#00D4AA", "#00B894", "#00796B"]
    WAVE_COLORS_PROCESS = ["#F5A623", "#E8913A", "#D4782F"]
    WAVE_COLOR_DONE = "#4ADE80"
    WAVE_COLOR_ERROR = "#F87171"
    LABEL_COLORS = {
        "listening": "#00D4AA",
        "processing": "#F5A623",
        "done": "#4ADE80",
        "error": "#F87171",
    }

    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled and tk is not None and bool(
            os.getenv("DISPLAY") or os.getenv("WAYLAND_DISPLAY")
        )
        self._events: queue.SimpleQueue[tuple[str, object]] = queue.SimpleQueue()
        self._thread: threading.Thread | None = None
        self._levels: list[float] = [0.0] * self.NUM_POINTS
        self._state = "idle"
        self._processing_start: float = 0.0
        self._done_start: float = 0.0

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
        if pos == "bottom-center":
            return (screen_w - self.WIDTH) // 2, screen_h - self.HEIGHT - 60
        if pos == "bottom-right":
            return screen_w - self.WIDTH - margin, screen_h - self.HEIGHT - 60
        # default: top-right
        return screen_w - self.WIDTH - margin, margin

    def _run(self) -> None:
        root = tk.Tk()
        root.withdraw()
        try:
            root.overrideredirect(True)
            root.attributes("-topmost", True)
        except tk.TclError:
            pass
        try:
            root.attributes("-alpha", 0.92)
        except tk.TclError:
            pass
        try:
            root.attributes("-type", "dock")
        except tk.TclError:
            pass

        w, h = self.WIDTH, self.HEIGHT
        x, y = self._compute_position(root.winfo_screenwidth(), root.winfo_screenheight())
        root.geometry(f"{w}x{h}+{x}+{y}")

        # Canvas fills the window
        canvas = tk.Canvas(root, width=w, height=h, bg=self.BG, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        # Draw rounded-rectangle background with subtle border
        self._draw_rounded_bg(canvas, w, h)

        # Status dot and label
        dot_id = canvas.create_oval(14, 14, 22, 22, fill="#333333", outline="", tags="dot")
        label_id = canvas.create_text(
            28, 18, text="", anchor="w",
            font=("Inter", 9, "bold"), fill="#555555", tags="label",
        )

        auto_hide_id: list[int | None] = [None]

        # Smoothed levels for fluid animation
        smooth_levels: list[float] = [0.0] * self.NUM_POINTS

        def draw_waveform() -> None:
            canvas.delete("wave")

            wave_left = 16
            wave_right = w - 16
            wave_cy = h * 0.55        # center line Y
            max_amp = h * 0.32        # max amplitude

            num = self.NUM_POINTS
            dx = (wave_right - wave_left) / (num - 1)

            # Smooth the raw levels toward targets
            for i in range(num):
                target = self._levels[i] if i < len(self._levels) else 0.0
                smooth_levels[i] += (target - smooth_levels[i]) * 0.25

            t = time.monotonic()

            if self._state == "listening":
                colors = self.WAVE_COLORS_LISTEN
                for layer in range(self.WAVE_LINES):
                    opacity_factor = 1.0 - layer * 0.3
                    phase_offset = layer * 0.7
                    amp_scale = 1.0 - layer * 0.25
                    points: list[float] = []
                    for i in range(num):
                        px = wave_left + i * dx
                        # Combine mic level with a gentle organic wave
                        lv = smooth_levels[i] * amp_scale
                        organic = 0.08 * math.sin(i * 0.4 + t * 2.5 + phase_offset)
                        amp = (lv + organic) * max_amp
                        py = wave_cy + amp * math.sin(i * 0.3 + t * 3.0 + phase_offset)
                        points.extend([px, py])
                    if len(points) >= 4:
                        color = colors[layer % len(colors)]
                        canvas.create_line(
                            *points, fill=color, width=2.5 - layer * 0.5,
                            smooth=True, tags="wave",
                        )

            elif self._state == "processing":
                dt = t - self._processing_start
                colors = self.WAVE_COLORS_PROCESS
                for layer in range(self.WAVE_LINES):
                    phase_offset = layer * 1.2
                    points = []
                    for i in range(num):
                        px = wave_left + i * dx
                        # Flowing sine waves that pulse
                        amp = max_amp * (0.15 + 0.2 * (0.5 + 0.5 * math.sin(dt * 2.0 + layer)))
                        py = wave_cy + amp * math.sin(i * 0.25 + dt * 3.5 + phase_offset)
                        points.extend([px, py])
                    if len(points) >= 4:
                        color = colors[layer % len(colors)]
                        canvas.create_line(
                            *points, fill=color, width=2.5 - layer * 0.5,
                            smooth=True, tags="wave",
                        )

            elif self._state == "done":
                dt = t - self._done_start
                # Flatline animation: wave shrinks to center
                decay = max(0.0, 1.0 - dt * 1.5)
                points = []
                for i in range(num):
                    px = wave_left + i * dx
                    amp = max_amp * 0.15 * decay
                    py = wave_cy + amp * math.sin(i * 0.35 + t * 2.0)
                    points.extend([px, py])
                if len(points) >= 4:
                    canvas.create_line(
                        *points, fill=self.WAVE_COLOR_DONE, width=2.5,
                        smooth=True, tags="wave",
                    )

            elif self._state == "error":
                # Jagged short burst
                points = []
                for i in range(num):
                    px = wave_left + i * dx
                    jag = random.uniform(-0.1, 0.1) * max_amp
                    py = wave_cy + jag
                    points.extend([px, py])
                if len(points) >= 4:
                    canvas.create_line(
                        *points, fill=self.WAVE_COLOR_ERROR, width=2,
                        smooth=False, tags="wave",
                    )
            else:
                # Idle: flat subtle breathing line
                points = []
                for i in range(num):
                    px = wave_left + i * dx
                    py = wave_cy + 2.0 * math.sin(i * 0.2 + t * 1.5)
                    points.extend([px, py])
                if len(points) >= 4:
                    canvas.create_line(
                        *points, fill="#222222", width=1.5,
                        smooth=True, tags="wave",
                    )

        def update_indicators() -> None:
            """Update the status dot and label text/color."""
            state = self._state
            color = self.LABEL_COLORS.get(state, "#555555")
            canvas.itemconfig(dot_id, fill=color)

            labels = {
                "listening": "Listening…",
                "processing": "Processing…",
                "done": "✓ Done",
                "error": "✗ Error",
            }
            canvas.itemconfig(label_id, text=labels.get(state, ""), fill=color)

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
                    self._levels[:] = [0.0] * self.NUM_POINTS
                    smooth_levels[:] = [0.0] * self.NUM_POINTS
                    update_indicators()
                elif kind == "level" and isinstance(payload, float):
                    self._levels.pop(0)
                    self._levels.append(payload)
                elif kind == "state":
                    state, text = payload  # type: ignore[misc]
                    self._state = state
                    if auto_hide_id[0] is not None:
                        root.after_cancel(auto_hide_id[0])
                        auto_hide_id[0] = None
                    if state == "done":
                        self._done_start = time.monotonic()
                        auto_hide_id[0] = root.after(2000, lambda: root.withdraw())
                    elif state == "error":
                        auto_hide_id[0] = root.after(2000, lambda: root.withdraw())
                    elif state == "processing":
                        self._processing_start = time.monotonic()
                    update_indicators()
                elif kind == "stop":
                    root.destroy()
                    return

            draw_waveform()
            root.after(33, tick)  # ~30 FPS

        tick()
        root.mainloop()

    @staticmethod
    def _draw_rounded_bg(canvas: "tk.Canvas", w: int, h: int, r: int = 12) -> None:
        """Draw a rounded rectangle background with a subtle border."""
        # Background fill
        canvas.create_rectangle(r, 0, w - r, h, fill="#0D0D0D", outline="", tags="bg")
        canvas.create_rectangle(0, r, w, h - r, fill="#0D0D0D", outline="", tags="bg")
        canvas.create_oval(0, 0, 2 * r, 2 * r, fill="#0D0D0D", outline="", tags="bg")
        canvas.create_oval(w - 2 * r, 0, w, 2 * r, fill="#0D0D0D", outline="", tags="bg")
        canvas.create_oval(0, h - 2 * r, 2 * r, h, fill="#0D0D0D", outline="", tags="bg")
        canvas.create_oval(w - 2 * r, h - 2 * r, w, h, fill="#0D0D0D", outline="", tags="bg")

        # Subtle border
        border_color = "#1F2937"
        canvas.create_line(r, 0, w - r, 0, fill=border_color, tags="bg")
        canvas.create_line(r, h, w - r, h, fill=border_color, tags="bg")
        canvas.create_line(0, r, 0, h - r, fill=border_color, tags="bg")
        canvas.create_line(w, r, w, h - r, fill=border_color, tags="bg")
        canvas.create_arc(0, 0, 2 * r, 2 * r, start=90, extent=90,
                          style="arc", outline=border_color, tags="bg")
        canvas.create_arc(w - 2 * r, 0, w, 2 * r, start=0, extent=90,
                          style="arc", outline=border_color, tags="bg")
        canvas.create_arc(0, h - 2 * r, 2 * r, h, start=180, extent=90,
                          style="arc", outline=border_color, tags="bg")
        canvas.create_arc(w - 2 * r, h - 2 * r, w, h, start=270, extent=90,
                          style="arc", outline=border_color, tags="bg")
