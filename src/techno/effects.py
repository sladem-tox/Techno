"""Effects and master-bus processing."""

import numpy as np

from .audio import SR, highpass, soft_clip


def delay(
    track: np.ndarray,
    beat: float,
    delay_beats: float = 0.75,
    feedback: float = 0.35,
    wet: float = 0.25,
) -> np.ndarray:
    """Add a short stereo feedback delay."""
    output = track.copy()
    delay_samples = int(delay_beats * beat * SR)
    gain = feedback

    for index in range(5):
        shift = delay_samples * (index + 1)
        if shift >= len(track):
            break

        delayed = track[:-shift].copy()
        if index % 2 == 0:
            delayed[:, 0] *= 0.65
        else:
            delayed[:, 1] *= 0.65

        output[shift:] += delayed * gain * wet
        gain *= feedback

    return output


def noise_sweep(
    duration: float = 2.0,
    *,
    rng: np.random.Generator,
) -> np.ndarray:
    """Generate a filtered noise sweep for transitions."""
    n = int(duration * SR)
    t = np.arange(n) / SR
    noise = rng.normal(0, 1, n)
    envelope = np.exp(-t * 2.3)
    return highpass(noise, 3500) * envelope * 0.08


def master(
    track: np.ndarray,
    *,
    master_gain: float,
    fade_seconds: float,
) -> np.ndarray:
    """Apply high-pass filtering, saturation, normalisation, and fade-out."""
    track = track.copy()
    track[:, 0] = highpass(track[:, 0], 25)
    track[:, 1] = highpass(track[:, 1], 25)
    track = soft_clip(track, 1.25)

    peak = np.max(np.abs(track))
    if peak > 0:
        track /= peak
    track *= master_gain

    fade_samples = int(fade_seconds * SR)
    fade = np.linspace(1, 0, fade_samples)
    track[-fade_samples:, 0] *= fade
    track[-fade_samples:, 1] *= fade
    return track
