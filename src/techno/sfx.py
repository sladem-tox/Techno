"""Procedurally generated retro video-game sound effects."""

import numpy as np

from .audio import SR, highpass, lowpass, soft_clip
from .synths import midi_to_hz


def _envelope(t: np.ndarray, attack: float, decay: float) -> np.ndarray:
    """Return a short attack followed by an exponential decay."""
    return (1 - np.exp(-t / attack)) * np.exp(-t / decay)


def _square(freq: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Generate a band-unlimited square wave for short retro-style sounds."""
    return np.where(np.sin(2 * np.pi * np.cumsum(freq) / SR) >= 0, 1.0, -1.0)


def coin(duration: float = 0.25) -> np.ndarray:
    """Generate a bright, upward two-note pickup or coin sound."""
    n = int(duration * SR)
    t = np.arange(n) / SR
    midpoint = duration * 0.42
    first = np.full(n, midi_to_hz(84))
    second = np.full(n, midi_to_hz(91))
    frequency = np.where(t < midpoint, first, second)
    tone = np.sin(2 * np.pi * np.cumsum(frequency) / SR)
    envelope = np.exp(-t * 12)
    return tone * envelope * 0.28


def laser(duration: float = 0.35, *, rising: bool = False) -> np.ndarray:
    """Generate a short falling or rising square-wave laser effect."""
    n = int(duration * SR)
    t = np.arange(n) / SR
    start = midi_to_hz(96 if rising else 108)
    end = midi_to_hz(120 if rising else 48)
    frequency = np.geomspace(start, end, n)
    tone = _square(frequency, t)
    envelope = np.exp(-t * 7)
    return lowpass(tone * envelope, 9000) * 0.18


def explosion(
    duration: float = 0.8,
    *,
    rng: np.random.Generator,
) -> np.ndarray:
    """Generate a low boom layered with filtered noise."""
    n = int(duration * SR)
    t = np.arange(n) / SR
    frequency = 55 + 35 * np.exp(-t * 8)
    phase = 2 * np.pi * np.cumsum(frequency) / SR
    boom = np.sin(phase) * np.exp(-t * 4.5)
    noise = lowpass(rng.normal(0, 1, n), 1800) * np.exp(-t * 6)
    return soft_clip(boom * 0.75 + noise * 0.55, 1.4) * 0.3


def hit(duration: float = 0.18) -> np.ndarray:
    """Generate a short impact sound with a tonal transient and noise."""
    n = int(duration * SR)
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * 150 * t) * np.exp(-t * 28)
    noise = highpass(np.random.default_rng(42).normal(0, 1, n), 1200)
    noise *= np.exp(-t * 38)
    return (tone * 0.65 + noise * 0.35) * 0.32


def power_up(duration: float = 0.85) -> np.ndarray:
    """Generate an upward arpeggio suitable for a power-up event."""
    n = int(duration * SR)
    t = np.arange(n) / SR
    notes = np.array([72, 76, 79, 84])
    step = duration / len(notes)
    note_index = np.minimum((t / step).astype(int), len(notes) - 1)
    frequency = midi_to_hz(notes[note_index])
    tone = np.sin(2 * np.pi * np.cumsum(frequency) / SR)
    envelope = _envelope(t, 0.004, duration * 0.8)
    return tone * envelope * 0.25


def death(duration: float = 1.0) -> np.ndarray:
    """Generate a three-note descending game-over or player-death sound."""
    if duration <= 0:
        raise ValueError("duration must be positive")

    note_duration = duration / 3
    sounds = []
    for note in (72, 67, 60):
        n = int(note_duration * SR)
        t = np.arange(n) / SR
        tone = np.sin(2 * np.pi * midi_to_hz(note) * t)
        envelope = (1 - np.exp(-t * 180)) * np.exp(-t * 7)
        sounds.append(tone * envelope)

    return np.concatenate(sounds) * 0.26


def spaceship(duration: float = 1.2) -> np.ndarray:
    """Generate an alternating up/down spaceship fly-by sound."""
    if duration <= 0:
        raise ValueError("duration must be positive")

    n = int(duration * SR)
    t = np.arange(n) / SR
    cycle = duration / 4
    phase = (t % cycle) / cycle
    segment = np.minimum((t / cycle).astype(int), 3)
    rising = segment % 2 == 0
    low = midi_to_hz(48)
    high = midi_to_hz(84)
    sweep = np.where(
        rising,
        low + (high - low) * phase,
        high - (high - low) * phase,
    )
    tone = np.sin(2 * np.pi * np.cumsum(sweep) / SR)
    wobble = 1 + 0.25 * np.sin(2 * np.pi * 7 * t)
    envelope = _envelope(t, 0.015, duration * 0.7)
    return tone * wobble * envelope * 0.2


def menu_select(duration: float = 0.22) -> np.ndarray:
    """Generate a short, clean menu-confirmation tone."""
    n = int(duration * SR)
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * midi_to_hz(84) * t)
    return tone * _envelope(t, 0.002, 0.045) * 0.25


def jump(duration: float = 0.4) -> np.ndarray:
    """Generate a rising square-wave jump effect."""
    n = int(duration * SR)
    t = np.arange(n) / SR
    frequency = np.geomspace(midi_to_hz(60), midi_to_hz(84), n)
    tone = _square(frequency, t)
    return tone * _envelope(t, 0.003, duration * 0.75) * 0.2
