"""Push-to-talk recording, transcription, and text insertion logic."""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import threading
import urllib.error
import urllib.request
import wave
from pathlib import Path

from .audio_feedback import play
from .clipboard import copy_to_clipboard, paste_into_active_window
from .config import cfg, normalize_hotkey, token_from_key
from .notifier import notify
from .overlay import VoiceOverlay
from .rms import rms_level
from .vad import create_vad

try:
    from pynput import keyboard
except ImportError:
    keyboard = None  # type: ignore[assignment]


class PushToTalk:
    """Records audio while the hotkey is held, sends to API, and pastes result."""

    def __init__(self, overlay: VoiceOverlay, tray: object | None = None) -> None:
        self.required = normalize_hotkey(cfg.hotkey)
        self.pressed: set[str] = set()
        self.recording = False
        self.current_wav: Path | None = None
        self.overlay = overlay
        self.tray = tray  # SystemTrayIcon or None

        self._record_thread: threading.Thread | None = None
        self._record_stop = threading.Event()
        self._captured_bytes = 0
        self._auto_stopped = False

        self._vad = create_vad(cfg.vad_aggressiveness) if cfg.vad_enabled else None
        self._auto_stop_timer: threading.Timer | None = None
        self._toggle_lock = threading.Lock()

    # -- tray state helper --

    def _set_tray_state(self, state: str) -> None:
        if self.tray is not None and hasattr(self.tray, "set_state"):
            self.tray.set_state(state)

    # -- recording worker thread --

    def _record_worker(self, target_path: Path) -> None:
        process = subprocess.Popen(
            ["arecord", "-q", "-f", "S16_LE", "-r", "16000", "-c", "1", "-t", "raw"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )

        self._captured_bytes = 0
        chunk_size = 3200  # 100ms at 16kHz 16-bit mono

        with wave.open(str(target_path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)

            while not self._record_stop.is_set():
                chunk = process.stdout.read(chunk_size) if process.stdout else b""
                if not chunk:
                    break
                wav.writeframes(chunk)
                self._captured_bytes += len(chunk)

                rms = rms_level(chunk)
                level = min(1.0, float(rms) / 9000.0)
                self.overlay.level(level)

                # VAD: auto-stop after sustained silence
                if self._vad is not None:
                    silence = self._vad.silence_duration(chunk)
                    if silence >= cfg.vad_silence_timeout:
                        self._auto_stopped = True
                        # Schedule stop_recording on a separate thread so it
                        # doesn't deadlock with the worker join().
                        self._auto_stop_timer = threading.Timer(0, self.stop_recording)
                        self._auto_stop_timer.start()
                        break

        process.terminate()
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            process.kill()

    # -- recording lifecycle --

    def start_recording(self) -> None:
        if self.recording:
            return

        fd, path = tempfile.mkstemp(prefix="lynx_ptt_", suffix=".wav")
        os.close(fd)
        self.current_wav = Path(path)

        self._record_stop.clear()
        self._auto_stopped = False
        if self._vad is not None:
            self._vad.reset()

        self._record_thread = threading.Thread(
            target=self._record_worker, args=(self.current_wav,), daemon=True,
        )
        self._record_thread.start()

        self.recording = True
        self.overlay.show()
        self.overlay.set_state("listening")
        self._set_tray_state("recording")
        play("record_start")
        notify("Recording started")

    def stop_recording(self) -> None:
        if not self.recording:
            return

        self._record_stop.set()
        if self._record_thread is not None:
            self._record_thread.join(timeout=2.5)

        self.recording = False
        self.overlay.set_state("processing")
        self._set_tray_state("processing")
        play("record_stop")
        notify("Recording stopped, processing...")

        try:
            self.process_audio()
        finally:
            if self.current_wav and self.current_wav.exists():
                self.current_wav.unlink(missing_ok=True)
            self.current_wav = None
            self._record_thread = None
            self._record_stop.clear()
            self._set_tray_state("idle")

    def toggle_recording(self) -> None:
        """Toggle recording state (used for signals, menu, and one-shot triggers)."""
        if not self._toggle_lock.acquire(blocking=False):
            return  # Another toggle is already in progress
        try:
            if self.recording:
                self.stop_recording()
            else:
                self.start_recording()
        finally:
            self._toggle_lock.release()

    # -- API call and text insertion --

    def process_audio(self) -> None:
        if not self.current_wav or not self.current_wav.exists() or self._captured_bytes < 2000:
            notify("No audio captured")
            self.overlay.set_state("error")
            play("error")
            return

        # Fetch current profile to get default language/style
        try:
            profile_req = urllib.request.Request(f"{cfg.api_url}/api/profile")
            with urllib.request.urlopen(profile_req, timeout=5) as resp:
                profile = json.loads(resp.read().decode())
                lang = profile.get("default_language", cfg.language)
                tone = profile.get("preferred_tone", cfg.style)
        except Exception:
            # Fallback to config
            lang = cfg.language
            tone = cfg.style

        with self.current_wav.open("rb") as fp:
            data = {
                "style": tone,
                "context": cfg.context,
                "language": lang,
                "auto_rewrite": "true",
            }
            boundary = "----LynxBoundary7d9a1f"
            body = bytearray()
            for key, value in data.items():
                body.extend(f"--{boundary}\r\n".encode())
                body.extend(
                    f'Content-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode()
                )
            body.extend(f"--{boundary}\r\n".encode())
            body.extend(
                f'Content-Disposition: form-data; name="audio"; filename="{self.current_wav.name}"\r\n'.encode()
            )
            body.extend(b"Content-Type: audio/wav\r\n\r\n")
            body.extend(fp.read())
            body.extend(b"\r\n")
            body.extend(f"--{boundary}--\r\n".encode())

        request = urllib.request.Request(
            f"{cfg.api_url}/api/transcribe",
            data=bytes(body),
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )

        try:
            response = urllib.request.urlopen(request, timeout=60)
        except urllib.error.URLError:
            notify("Failed to reach local API. Is server running?")
            self.overlay.set_state("error")
            play("error")
            return
        except Exception:
            notify("Transcription request failed")
            self.overlay.set_state("error")
            play("error")
            return

        status_code = getattr(response, "status", 200)
        if status_code >= 400:
            notify(f"Transcription failed: HTTP {status_code}")
            self.overlay.set_state("error")
            play("error")
            return

        payload = json.loads(response.read().decode("utf-8", errors="ignore") or "{}")
        text = (payload.get("rewritten_text") or payload.get("transcript") or "").strip()
        if not text:
            notify("No text returned")
            self.overlay.set_state("error")
            play("error")
            return

        # Success path
        self.overlay.set_state("done", text)
        play("done")

        copied = copy_to_clipboard(text)
        if copied:
            pasted = paste_into_active_window(text)
            notify("Done: inserted at active cursor" if pasted else "Done: text copied to clipboard")
            return

        if cfg.insert_mode == "type" and paste_into_active_window(text):
            notify("Done: typed at active cursor")
            return

        notify("Done: install wl-copy or xclip for clipboard")

    # -- pynput key handlers --

    def on_press(self, key: object) -> None:
        token = token_from_key(key)
        if token:
            self.pressed.add(token)
        if self.required.issubset(self.pressed) and not self.recording:
            self.start_recording()

    def on_release(self, key: object) -> None:
        token = token_from_key(key)
        if token and token in self.pressed:
            self.pressed.remove(token)
        if self.recording and not self.required.issubset(self.pressed):
            if not self._auto_stopped:
                self.stop_recording()
