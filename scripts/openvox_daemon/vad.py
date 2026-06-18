"""Voice Activity Detection wrapper around webrtcvad."""
from __future__ import annotations

import time

try:
    import webrtcvad
except ImportError:
    webrtcvad = None  # type: ignore[assignment]


class VoiceActivityDetector:
    """Lightweight VAD that tracks silence duration for auto-stop."""

    def __init__(
        self,
        sample_rate: int = 16000,
        aggressiveness: int = 2,
        frame_duration_ms: int = 20,
    ) -> None:
        if webrtcvad is None:
            raise RuntimeError("webrtcvad not installed")
        self._vad = webrtcvad.Vad(aggressiveness)
        self._sample_rate = sample_rate
        # Frame size in bytes: (samples_per_frame) * 2 bytes per sample
        self._frame_size = (sample_rate * frame_duration_ms // 1000) * 2
        self._silence_start: float | None = None

    def is_speech(self, chunk: bytes) -> bool:
        """Return ``True`` if any sub-frame in *chunk* contains speech."""
        fs = self._frame_size
        for offset in range(0, len(chunk) - fs + 1, fs):
            frame = chunk[offset : offset + fs]
            if self._vad.is_speech(frame, self._sample_rate):
                return True
        return False

    def silence_duration(self, chunk: bytes) -> float:
        """Return how many seconds of continuous silence have elapsed."""
        if self.is_speech(chunk):
            self._silence_start = None
            return 0.0
        if self._silence_start is None:
            self._silence_start = time.monotonic()
        return time.monotonic() - self._silence_start

    def reset(self) -> None:
        self._silence_start = None


def create_vad(aggressiveness: int = 2) -> VoiceActivityDetector | None:
    """Create a VAD instance, or return ``None`` if webrtcvad is unavailable."""
    if webrtcvad is None:
        return None
    try:
        return VoiceActivityDetector(aggressiveness=aggressiveness)
    except Exception:
        return None
