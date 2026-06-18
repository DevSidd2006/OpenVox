"""Pure-Python RMS calculation, replacing the deprecated audioop module."""
from __future__ import annotations

import struct


def rms_level(chunk: bytes, sample_width: int = 2) -> int:
    """Compute RMS amplitude of 16-bit LE PCM audio.

    Drop-in replacement for ``audioop.rms(chunk, 2)``.
    """
    count = len(chunk) // sample_width
    if count == 0:
        return 0
    samples = struct.unpack(f"<{count}h", chunk)
    return int((sum(s * s for s in samples) / count) ** 0.5)
