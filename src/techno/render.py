"""Composition rendering and WAV output."""

from pathlib import Path

import numpy as np
import soundfile as sf

from .audio import SR
from .composition import Arrangement
from .effects import delay, master


def render(
    filename: Path,
    *,
    arrange: Arrangement,
    bpm: float,
    n_bars: int,
    master_gain: float,
) -> None:
    """Render the default composition to a WAV file."""
    beat = 60.0 / bpm
    bar = 4 * beat
    duration = n_bars * bar
    track = np.zeros((int(duration * SR), 2))
    rng = np.random.default_rng(42)

    arrange(track, bpm=bpm, n_bars=n_bars, rng=rng)
    track = delay(track, beat, delay_beats=0.75, feedback=0.42, wet=0.18)
    track = master(
        track,
        master_gain=master_gain,
        fade_seconds=bar * 2,
    )
    sf.write(filename, track, SR, subtype="PCM_16")

    print()
    print("====================================")
    print("    PYTHON TECHNO MACHINE")
    print("====================================")
    print(f"BPM       : {bpm:g}")
    print(f"Bars      : {n_bars}")
    print(f"Duration  : {duration:.1f} seconds")
    print(f"Sample rate: {SR}")
    print(f"Output    : {filename}")
    print("====================================")
