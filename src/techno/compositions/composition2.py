"""The original generative techno arrangement."""

import numpy as np

from ..audio import add, add_exclusive
from ..drums import clap, hihat, kick
from ..effects import noise_sweep
from ..samples import load_sample
from ..synths import acid_note, chord_stab

BASS_PATTERN = [
    (0, 36),
    (2, 36),
    (3, 39),
    (4, 36),
    (6, 43),
    (7, 39),
    (8, 36),
    (10, 36),
    (11, 46),
    (12, 43),
    (14, 39),
    (15, 36),
]


def arrange(
    track: np.ndarray,
    *,
    bpm: float,
    n_bars: int,
    rng: np.random.Generator,
) -> None:
    """Arrange composition onto a stereo track."""
    beat = 60.0 / bpm
    bar = 4 * beat

    for bar_number in range(n_bars):
        bar_time = bar_number * bar

        if bar_number != 19:
            for beat_number in range(4):
                add(track, kick(), bar_time + beat_number * beat, gain=0.90)

        if bar_number >= 2:
            for eighth in range(8):
                if eighth % 2 == 1:
                    add(
                        track,
                        hihat(),
                        bar_time + eighth * beat / 2,
                        gain=rng.uniform(0.75, 1.0),
                        pan_pos=rng.uniform(-0.2, 0.2),
                    )

        if bar_number >= 16:
            for step in range(16):
                if rng.random() < 0.33:
                    add(
                        track,
                        hihat(duration=0.04),
                        bar_time + step * beat / 4,
                        gain=rng.uniform(0.2, 0.5),
                        pan_pos=rng.uniform(-0.6, 0.6),
                    )

        if bar_number >= 4:
            for beat_number in [1, 3]:
                add(track, clap(), bar_time + beat_number * beat, gain=0.8)

        if bar_number >= 8:
            for beat_number in range(4):
                if rng.random() < 0.6:
                    add(
                        track,
                        hihat(open_hat=True),
                        bar_time + (beat_number + 0.5) * beat,
                        gain=0.65,
                        pan_pos=rng.choice([-0.3, 0.3]),
                    )

        if bar_number >= 8 and bar_number != 19:
            if 16 <= bar_number <= 19:
                cutoff = 500 + (bar_number - 16) * 700
            elif bar_number >= 20:
                cutoff = 1800
            else:
                cutoff = 750

            for step, note in BASS_PATTERN:
                add(
                    track,
                    acid_note(
                        note,
                        duration=beat * 0.24,
                        cutoff=cutoff,
                        resonance_character=1.2,
                    ),
                    bar_time + step * beat / 4,
                    gain=rng.uniform(0.75, 1.0),
                )

        if bar_number >= 12 and bar_number != 19:
            for position in [0.75, 2.75]:
                add(
                    track,
                    chord_stab(
                        (60, 63, 67, 70),
                        cutoff=1300 if bar_number < 20 else 2400,
                    ),
                    bar_time + position * beat,
                    gain=0.75,
                    pan_pos=rng.uniform(-0.25, 0.25),
                )

        if bar_number in [18, 19]:
            division = 8 if bar_number == 18 else 16
            for step in range(division):
                add(
                    track,
                    clap(duration=0.12),
                    bar_time + step * bar / division,
                    gain=0.20 + 0.65 * step / division,
                    pan_pos=rng.uniform(-0.2, 0.2),
                )
    warning = load_sample("voice/warning.wav")
    add_exclusive(
        track,
        warning,
        time_seconds=24 * bar,
        gain=0.75,
        pan_pos=0.0,
    )


    add(track, noise_sweep(rng=rng), 20 * bar)
