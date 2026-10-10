"""List and play individual drum, effect, and sample sounds."""

import argparse
import os
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

import numpy as np
import soundfile as sf

from .audio import SR
from .drums import clap, hihat, kick, ride, shaker, snare, tom
from .effects import noise_sweep
from .sfx import (
    coin,
    death,
    explosion,
    hit,
    jump,
    laser,
    menu_select,
    power_up,
    spaceship,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLES_DIR = PROJECT_ROOT / "samples"
OUTPUT_DIR = PROJECT_ROOT / "Tracks" / "sound_check"
SoundFactory = Callable[[], np.ndarray]


def available_sounds() -> dict[str, Path | SoundFactory]:
    """Return playable generated sounds and sample files."""
    rng = np.random.default_rng(42)
    sounds: dict[str, Path | SoundFactory] = {
        "drums:kick": kick,
        "drums:clap": clap,
        "drums:hihat": hihat,
        "drums:open_hihat": lambda: hihat(open_hat=True),
        "drums:ride": ride,
        "drums:snare": snare,
        "drums:shaker": shaker,
        "drums:tom": tom,
        "effects:noise_sweep": lambda: noise_sweep(rng=rng),
        "sfx:coin": coin,
        "sfx:death": death,
        "sfx:explosion": lambda: explosion(rng=rng),
        "sfx:hit": hit,
        "sfx:jump": jump,
        "sfx:laser": laser,
        "sfx:laser_rising": lambda: laser(rising=True),
        "sfx:menu_select": menu_select,
        "sfx:power_up": power_up,
        "sfx:spaceship": spaceship,
    }

    for sample in sorted(SAMPLES_DIR.rglob("*")):
        if sample.is_file():
            relative = sample.relative_to(SAMPLES_DIR).as_posix()
            sounds[f"sample:{relative}"] = sample

    return sounds


def play_file(filename: Path) -> None:
    """Open an audio file with the operating system's default player."""
    if sys.platform == "win32":
        startfile = getattr(os, "startfile", None)
        if startfile is None:
            raise RuntimeError("Windows audio playback is unavailable")
        startfile(str(filename))
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(filename)])
    else:
        subprocess.Popen(["xdg-open", str(filename)])


def list_sounds(sounds: dict[str, Path | SoundFactory]) -> None:
    """Print all available sound names."""
    for name, sound in sounds.items():
        kind = "sample" if isinstance(sound, Path) else "generated"
        print(f"{name} ({kind})")


def play_sound(name: str, sounds: dict[str, Path | SoundFactory]) -> None:
    """Render or locate a sound and open it in the default audio player."""
    try:
        sound = sounds[name]
    except KeyError as exc:
        available = ", ".join(sounds)
        raise ValueError(f"Unknown sound {name!r}. Available sounds: {available}") from exc

    if isinstance(sound, Path):
        filename = sound
    else:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        filename = OUTPUT_DIR / f"{name.replace(':', '_').replace('/', '_')}.wav"
        generated = sound()
        sf.write(filename, generated, SR, subtype="PCM_16")

    print(f"Opening {filename}")
    play_file(filename)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse sound-check command-line arguments."""
    parser = argparse.ArgumentParser(
        description="List or play individual techno sounds."
    )
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument(
        "--list",
        action="store_true",
        help="list available sounds",
    )
    actions.add_argument(
        "--play",
        metavar="NAME",
        help="play a sound by name, as shown by --list",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the sound-check command."""
    args = parse_args(argv)
    sounds = available_sounds()

    if args.list:
        list_sounds(sounds)
    else:
        try:
            play_sound(args.play, sounds)
        except (OSError, RuntimeError, ValueError) as exc:
            print(f"Unable to play sound: {exc}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
