import numpy as np

from .audio import SR, highpass, soft_clip


rng = np.random.default_rng(42)


# ============================================================
# DRUM SYNTHESIS
# ============================================================

def kick(duration=0.55):
    """
    Techno kick.

    Fundamental oscillator starts high and rapidly drops
    towards ~48 Hz.
    """

    n = int(duration * SR)
    t = np.arange(n) / SR

    # Pitch envelope
    freq = (
        48
        + 110 * np.exp(-t * 35)
        + 35 * np.exp(-t * 100)
    )

    phase = 2 * np.pi * np.cumsum(freq) / SR

    # Main body
    body = np.sin(phase)

    # Amplitude envelope
    envelope = np.exp(-t * 8)

    # Tiny transient/click
    click = rng.normal(0, 1, n) * np.exp(-t * 120)

    x = body * envelope
    x += click * 0.12

    return soft_clip(x, 1.5)


def clap(duration=0.35):
    """Noise-based synthetic clap."""

    n = int(duration * SR)
    t = np.arange(n) / SR

    noise = rng.normal(0, 1, n)

    # Several little bursts mimic multiple handclaps
    env = (
        np.exp(-t * 35)
        + 0.8 * np.exp(-np.maximum(t - 0.012, 0) * 45)
            * (t >= 0.012)
        + 0.6 * np.exp(-np.maximum(t - 0.027, 0) * 50)
            * (t >= 0.027)
    )

    x = noise * env

    # Remove bass frequencies
    x = highpass(x, 900)

    return x * 0.18


def hihat(duration=0.08, open_hat=False):
    """Synthetic hi-hat made from filtered noise."""

    if open_hat:
        duration = 0.30

    n = int(duration * SR)
    t = np.arange(n) / SR

    noise = rng.normal(0, 1, n)

    decay = 18 if open_hat else 65

    env = np.exp(-t * decay)

    x = noise * env

    # Hats live mostly in the high-frequency region
    x = highpass(x, 6000)

    return x * 0.10


def ride(duration: float = 0.8) -> np.ndarray:
    """Synthetic ride cymbal made from metallic partials and noise."""
    n = int(duration * SR)
    t = np.arange(n) / SR

    partials = (
        np.sin(2 * np.pi * 3100 * t)
        + 0.7 * np.sin(2 * np.pi * 4170 * t)
        + 0.5 * np.sin(2 * np.pi * 5350 * t)
        + 0.35 * np.sin(2 * np.pi * 6890 * t)
    )
    noise = rng.normal(0, 1, n)
    envelope = np.exp(-t * 4.5)

    x = highpass((partials * 0.35 + noise) * envelope, 2500)
    return soft_clip(x, 1.4) * 0.08


def snare(duration: float = 0.25) -> np.ndarray:
    n = int(duration * SR)
    t = np.arange(n) / SR

    noise = rng.normal(0, 1, n)
    noise_env = np.exp(-t * 22)

    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 28)

    return 0.2 * (noise * noise_env + tone)


def shaker(duration: float = 0.12) -> np.ndarray:
    n = int(duration * SR)
    t = np.arange(n) / SR

    noise = rng.normal(0, 1, n)
    envelope = np.exp(-t * 35)

    return noise * envelope * 0.08


def tom(note_hz: float = 110.0, duration: float = 0.4) -> np.ndarray:
    n = int(duration * SR)
    t = np.arange(n) / SR

    frequency = note_hz + 80 * np.exp(-t * 18)
    phase = 2 * np.pi * np.cumsum(frequency) / SR
    envelope = np.exp(-t * 8)

    return np.sin(phase) * envelope * 0.3
