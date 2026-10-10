"""Shared audio and mixing helpers."""

import numpy as np
from scipy.signal import butter, sosfilt


SR = 44100


def soft_clip(x: np.ndarray, drive: float = 1.0) -> np.ndarray:
    """Apply simple tanh saturation."""
    return np.tanh(x * drive) / np.tanh(drive)


def lowpass(x: np.ndarray, cutoff: float, order: int = 4) -> np.ndarray:
    """Apply a Butterworth low-pass filter."""
    cutoff = np.clip(cutoff, 20, SR * 0.45)
    sos = butter(order, cutoff, btype="low", fs=SR, output="sos")
    return np.asarray(sosfilt(sos, x))


def highpass(x: np.ndarray, cutoff: float, order: int = 4) -> np.ndarray:
    """Apply a Butterworth high-pass filter."""
    cutoff = np.clip(cutoff, 20, SR * 0.45)
    sos = butter(order, cutoff, btype="high", fs=SR, output="sos")
    return np.asarray(sosfilt(sos, x))


def pan(x: np.ndarray, position: float = 0.0) -> np.ndarray:
    """Convert mono audio to stereo using constant-power panning."""
    position = np.clip(position, -1, 1)
    angle = (position + 1) * np.pi / 4
    return np.column_stack((np.cos(angle) * x, np.sin(angle) * x))


def add(
    track: np.ndarray,
    sound: np.ndarray,
    time_seconds: float,
    *,
    gain: float = 1.0,
    pan_pos: float = 0.0,
) -> None:
    """Add a mono or stereo sound to a stereo track."""
    start = int(time_seconds * SR)
    if sound.ndim == 1:
        sound = pan(sound, pan_pos)

    end = min(start + len(sound), len(track))
    if end <= start:
        return

    track[start:end] += gain * sound[: end - start]


def add_exclusive(
    track: np.ndarray,
    sound: np.ndarray,
    time_seconds: float,
    *,
    gain: float = 1.0,
    pan_pos: float = 0.0,
) -> None:
    """Clear a sound's time range before adding it to the stereo track.

    Use this for vocal or transition samples that need a gap in the existing
    arrangement. The cleared range is exactly the sample's duration.
    """
    start = int(time_seconds * SR)
    if sound.ndim == 1:
        sound = pan(sound, pan_pos)

    end = min(start + len(sound), len(track))
    if end <= start:
        return

    track[start:end] = 0
    track[start:end] += gain * sound[: end - start]
