"""Experimental sound-design generators for the sound laboratory."""

import numpy as np

from .audio import SR, highpass, lowpass, soft_clip
from .synths import midi_to_hz


def ring_mod_drone(
    *,
    duration: float = 4.0,
    carrier: float = 220.0,
    modulator: float = 37.0,
    cutoff: float = 5000.0,
) -> np.ndarray:
    """Generate a sustained ring-modulated drone."""
    if duration <= 0 or carrier <= 0 or modulator <= 0:
        raise ValueError("duration and frequencies must be positive")
    n = int(duration * SR)
    t = np.arange(n) / SR
    carrier_wave = np.sin(2 * np.pi * carrier * t)
    modulator_wave = np.sin(2 * np.pi * modulator * t)
    envelope = np.minimum(1.0, t * 8) * np.exp(-t / (duration * 1.5))
    return lowpass(carrier_wave * modulator_wave * envelope, cutoff) * 0.35


def alien_drone(
    *,
    duration: float = 5.0,
    note: float = 38.0,
    wobble: float = 0.35,
    cutoff: float = 1800.0,
) -> np.ndarray:
    """Generate a slowly unstable, layered dissonant drone."""
    if duration <= 0:
        raise ValueError("duration must be positive")
    n = int(duration * SR)
    t = np.arange(n) / SR
    frequency = midi_to_hz(note)
    tone = np.sin(2 * np.pi * frequency * t)
    tone += 0.6 * np.sin(2 * np.pi * frequency * 1.01 * t)
    tone += 0.35 * np.sin(2 * np.pi * frequency * 1.48 * t)
    modulation = 1 + wobble * np.sin(2 * np.pi * 0.23 * t)
    envelope = np.minimum(1.0, t * 3) * np.minimum(1.0, (duration - t) * 2)
    return lowpass(soft_clip(tone * modulation, 1.4) * envelope, cutoff) * 0.28


def materialisation(
    *,
    duration: float = 3.0,
    start_hz: float = 80.0,
    end_hz: float = 2400.0,
    noise_amount: float = 0.5,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Generate a rising materialisation-like sweep from tone and noise."""
    if duration <= 0 or start_hz <= 0 or end_hz <= 0:
        raise ValueError("duration and frequencies must be positive")
    if not 0 <= noise_amount <= 1:
        raise ValueError("noise_amount must be between 0 and 1")
    generator = rng if rng is not None else np.random.default_rng(42)
    n = int(duration * SR)
    t = np.arange(n) / SR
    frequency = np.geomspace(start_hz, end_hz, n)
    phase = 2 * np.pi * np.cumsum(frequency) / SR
    tone = np.sin(phase)
    noise = highpass(generator.normal(0, 1, n), 500) * noise_amount
    envelope = np.minimum(1.0, t * 4) * np.minimum(1.0, (duration - t) * 3)
    return lowpass((tone * (1 - noise_amount) + noise) * envelope, 7000) * 0.3


def tape_wobble(
    *,
    duration: float = 4.0,
    frequency: float = 220.0,
    wobble: float = 0.015,
) -> np.ndarray:
    """Generate a tone with slow tape-speed instability."""
    if duration <= 0 or frequency <= 0:
        raise ValueError("duration and frequency must be positive")
    n = int(duration * SR)
    t = np.arange(n) / SR
    speed = 1 + wobble * np.sin(2 * np.pi * 0.7 * t)
    phase = 2 * np.pi * np.cumsum(frequency * speed) / SR
    envelope = np.minimum(1.0, t * 8) * np.minimum(1.0, (duration - t) * 3)
    return np.sin(phase) * envelope * 0.3


def metallic_signal(
    *,
    duration: float = 2.5,
    frequency: float = 330.0,
    modulator: float = 91.0,
) -> np.ndarray:
    """Generate a short metallic ring-modulated signal."""
    if duration <= 0 or frequency <= 0 or modulator <= 0:
        raise ValueError("duration and frequencies must be positive")
    n = int(duration * SR)
    t = np.arange(n) / SR
    carrier = np.sin(2 * np.pi * frequency * t)
    mod = np.sin(2 * np.pi * modulator * t)
    envelope = np.exp(-t * 1.8)
    return highpass(carrier * mod * envelope, 100) * 0.35


def tardis_materialisation(
    *,
    duration: float = 4.0,
    base_hz: float = 110.0,
    wobble: float = 18.0,
) -> np.ndarray:
    """Generate an original, layered sci-fi materialisation effect."""
    if duration <= 0 or base_hz <= 0 or wobble < 0:
        raise ValueError("duration and base frequency must be positive")
    n = int(duration * SR)
    t = np.arange(n) / SR
    sweep = np.geomspace(base_hz * 0.5, base_hz * 8, n)
    phase = 2 * np.pi * np.cumsum(sweep) / SR
    tone = np.sin(phase)
    tone += 0.45 * np.sin(phase * 1.5 + 0.7 * np.sin(2 * np.pi * 0.8 * t))
    tone += 0.25 * np.sin(2 * np.pi * (base_hz * 2 + wobble * np.sin(2 * np.pi * 2 * t)) * t)
    envelope = np.minimum(1.0, t * 3) * np.minimum(1.0, (duration - t) * 2)
    return soft_clip(lowpass(tone * envelope, 4200), 1.3) * 0.26


def radar_ping(
    *,
    duration: float = 1.2,
    frequency: float = 1200.0,
    echo_delay: float = 0.35,
) -> np.ndarray:
    """Generate a short radar ping with a quiet electronic echo."""
    if duration <= 0 or frequency <= 0 or echo_delay < 0:
        raise ValueError("duration and frequency must be positive")
    n = int(duration * SR)
    t = np.arange(n) / SR
    ping = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 28)
    echo_start = int(echo_delay * SR)
    if echo_start < n:
        echo = np.zeros(n)
        echo[echo_start:] = ping[: n - echo_start] * 0.32
        ping += echo
    return ping * 0.3


def robot_transmission(
    *,
    duration: float = 2.5,
    carrier: float = 180.0,
    modulator: float = 42.0,
    tremolo: float = 9.0,
) -> np.ndarray:
    """Generate a synthetic robotic radio-transmission texture."""
    if duration <= 0 or carrier <= 0 or modulator <= 0 or tremolo < 0:
        raise ValueError("duration and frequencies must be positive")
    n = int(duration * SR)
    t = np.arange(n) / SR
    voice = np.sin(2 * np.pi * carrier * t)
    voice *= np.sin(2 * np.pi * modulator * t)
    voice *= 0.65 + 0.35 * np.sin(2 * np.pi * tremolo * t)
    envelope = np.minimum(1.0, t * 10) * np.minimum(1.0, (duration - t) * 4)
    return highpass(lowpass(voice * envelope, 2800), 180) * 0.3


def teleportation_beam(
    *,
    duration: float = 2.0,
    start_hz: float = 180.0,
    end_hz: float = 3200.0,
    pulse_rate: float = 14.0,
) -> np.ndarray:
    """Generate a pulsing upward teleportation-beam effect."""
    if duration <= 0 or start_hz <= 0 or end_hz <= 0 or pulse_rate <= 0:
        raise ValueError("duration and frequencies must be positive")
    n = int(duration * SR)
    t = np.arange(n) / SR
    frequency = np.geomspace(start_hz, end_hz, n)
    phase = 2 * np.pi * np.cumsum(frequency) / SR
    pulse = 0.55 + 0.45 * np.maximum(0, np.sin(2 * np.pi * pulse_rate * t))
    envelope = np.minimum(1.0, t * 5) * np.minimum(1.0, (duration - t) * 3)
    return highpass(np.sin(phase) * pulse * envelope, 100) * 0.25


def deep_space_drone(
    *,
    duration: float = 8.0,
    note: float = 28.0,
    detune: float = 0.8,
    movement: float = 0.3,
) -> np.ndarray:
    """Generate a slow, deep, evolving space drone."""
    if duration <= 0 or detune < 0 or movement < 0:
        raise ValueError("duration must be positive and modulation non-negative")
    n = int(duration * SR)
    t = np.arange(n) / SR
    frequency = midi_to_hz(note)
    drift = movement * np.sin(2 * np.pi * 0.09 * t)
    drone = np.sin(2 * np.pi * frequency * t)
    drone += 0.65 * np.sin(2 * np.pi * (frequency + detune + drift) * t)
    drone += 0.3 * np.sin(2 * np.pi * frequency * 1.5 * t)
    amplitude = 0.72 + 0.28 * np.sin(2 * np.pi * 0.13 * t)
    envelope = np.minimum(1.0, t * 1.5) * np.minimum(1.0, (duration - t) * 1.5)
    return lowpass(soft_clip(drone * amplitude, 1.2) * envelope, 900) * 0.32
