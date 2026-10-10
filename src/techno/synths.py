"""Melodic and tonal synthesizers."""

from typing import Literal

import numpy as np

from .audio import SR, lowpass, soft_clip

Waveform = Literal["sine", "saw", "square", "triangle", "pulse"]


def midi_to_hz(note: float) -> float:
    """Convert a MIDI note number to frequency in Hz."""
    return 440.0 * 2 ** ((note - 69) / 12)


def saw(freq: float, t: np.ndarray) -> np.ndarray:
    """Generate a simple sawtooth oscillator."""
    return 2 * ((freq * t) % 1.0) - 1.0


def sine(freq: float | np.ndarray, t: np.ndarray) -> np.ndarray:
    """Generate a sine oscillator."""
    return np.sin(2 * np.pi * np.cumsum(np.broadcast_to(freq, t.shape)) / SR)


def square(freq: float | np.ndarray, t: np.ndarray) -> np.ndarray:
    """Generate a square oscillator."""
    return np.where(sine(freq, t) >= 0, 1.0, -1.0)


def triangle(freq: float, t: np.ndarray) -> np.ndarray:
    """Generate a triangle oscillator."""
    return 2 * np.abs(2 * ((freq * t) % 1.0) - 1.0) - 1.0


def pulse(freq: float, t: np.ndarray, width: float = 0.5) -> np.ndarray:
    """Generate a variable-width pulse oscillator."""
    width = float(np.clip(width, 0.05, 0.95))
    return np.where((freq * t) % 1.0 < width, 1.0, -1.0)


def envelope(
    t: np.ndarray,
    *,
    attack: float = 0.01,
    decay: float = 0.1,
    sustain: float = 0.7,
    release: float = 0.15,
) -> np.ndarray:
    """Generate an ADSR envelope across a finite note."""
    if min(attack, decay, release) < 0:
        raise ValueError("envelope times must not be negative")
    if not 0 <= sustain <= 1:
        raise ValueError("sustain must be between 0 and 1")

    total = len(t) / SR
    attack_end = min(attack, total)
    decay_end = min(attack_end + decay, total)
    release_start = max(decay_end, total - release)
    result = np.empty_like(t, dtype=float)

    attack_mask = t < attack_end
    result[attack_mask] = (
        t[attack_mask] / attack_end if attack_end else 1.0
    )
    decay_mask = (t >= attack_end) & (t < decay_end)
    decay_length = decay_end - attack_end
    result[decay_mask] = (
        1 - (1 - sustain) * (t[decay_mask] - attack_end) / decay_length
        if decay_length
        else sustain
    )
    sustain_mask = (t >= decay_end) & (t < release_start)
    result[sustain_mask] = sustain
    release_mask = t >= release_start
    release_length = total - release_start
    result[release_mask] = (
        sustain * (1 - (t[release_mask] - release_start) / release_length)
        if release_length
        else 0
    )
    return result


def _oscillator(
    waveform: Waveform,
    frequency: float | np.ndarray,
    t: np.ndarray,
    *,
    pulse_width: float,
) -> np.ndarray:
    """Select a waveform for a note generator."""
    if waveform == "sine":
        return sine(frequency, t)
    if waveform == "saw":
        return saw(float(np.asarray(frequency).flat[0]), t)
    if waveform == "square":
        return square(frequency, t)
    if waveform == "triangle":
        return triangle(float(np.asarray(frequency).flat[0]), t)
    if waveform == "pulse":
        return pulse(float(np.asarray(frequency).flat[0]), t, pulse_width)
    raise ValueError(f"unsupported waveform: {waveform!r}")


def synth_note(
    note: float,
    duration: float = 0.5,
    *,
    waveform: Waveform = "saw",
    attack: float = 0.01,
    decay: float = 0.1,
    sustain: float = 0.7,
    release: float = 0.15,
    cutoff: float | None = 5000,
    vibrato: float = 0.0,
    pulse_width: float = 0.5,
    gain: float = 0.2,
) -> np.ndarray:
    """Generate a configurable monophonic synthesizer note."""
    if duration <= 0:
        raise ValueError("duration must be positive")
    n = int(duration * SR)
    t = np.arange(n) / SR
    frequency = midi_to_hz(note)
    if vibrato:
        frequency = frequency * (1 + 0.01 * vibrato * np.sin(2 * np.pi * 5 * t))
    tone = _oscillator(waveform, frequency, t, pulse_width=pulse_width)
    tone *= envelope(
        t,
        attack=attack,
        decay=decay,
        sustain=sustain,
        release=release,
    )
    if cutoff is not None:
        tone = lowpass(tone, cutoff)
    return soft_clip(tone, 1.2) * gain


def synth_pad(
    notes: tuple[float, ...],
    duration: float = 1.5,
    *,
    waveform: Waveform = "saw",
    cutoff: float = 1800,
    gain: float = 0.12,
) -> np.ndarray:
    """Generate a slowly evolving polyphonic pad."""
    if not notes:
        raise ValueError("pad requires at least one note")
    n = int(duration * SR)
    t = np.arange(n) / SR
    result = np.zeros(n)
    for index, note in enumerate(notes):
        detune = 0.997 + 0.003 * (index % 3)
        frequency = midi_to_hz(note) * detune
        result += _oscillator(waveform, frequency, t, pulse_width=0.5)
    result /= len(notes)
    result *= envelope(t, attack=0.15, decay=0.25, sustain=0.75, release=0.3)
    return lowpass(soft_clip(result, 1.1), cutoff) * gain


def synth_pluck(
    note: float,
    duration: float = 0.6,
    *,
    waveform: Waveform = "triangle",
    cutoff: float = 3000,
    gain: float = 0.22,
) -> np.ndarray:
    """Generate a short percussive plucked synth note."""
    return synth_note(
        note,
        duration,
        waveform=waveform,
        attack=0.002,
        decay=0.18,
        sustain=0.05,
        release=0.12,
        cutoff=cutoff,
        gain=gain,
    )


def synth_lead(
    note: float,
    duration: float = 0.4,
    *,
    waveform: Waveform = "square",
    cutoff: float = 3200,
    vibrato: float = 0.35,
    gain: float = 0.18,
) -> np.ndarray:
    """Generate a sustained lead note with optional vibrato."""
    return synth_note(
        note,
        duration,
        waveform=waveform,
        attack=0.025,
        decay=0.12,
        sustain=0.72,
        release=0.08,
        cutoff=cutoff,
        vibrato=vibrato,
        gain=gain,
    )


def acid_note(
    note: float,
    duration: float = 0.20,
    cutoff: float = 800,
    resonance_character: float = 0.0,
) -> np.ndarray:
    """Generate an acid-style bass note."""
    n = int(duration * SR)
    t = np.arange(n) / SR
    freq = midi_to_hz(note)
    x = saw(freq, t) + 0.35 * saw(freq * 1.003, t)
    env = (1 - np.exp(-t * 150)) * np.exp(-t * 5)
    x *= env
    x = lowpass(x, cutoff, order=3)
    return soft_clip(x, 1.5 + resonance_character) * 0.22


def chord_stab(
    notes: tuple[int, ...] = (60, 63, 67),
    duration: float = 0.35,
    cutoff: float = 1800,
) -> np.ndarray:
    """Generate a filtered chord stab."""
    n = int(duration * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)

    for note in notes:
        freq = midi_to_hz(note)
        x += saw(freq, t) + 0.20 * saw(freq * 1.006, t)

    x /= len(notes)
    env = (1 - np.exp(-t * 100)) * np.exp(-t * 8)
    x = lowpass(x * env, cutoff)
    return soft_clip(x, 1.8) * 0.18
