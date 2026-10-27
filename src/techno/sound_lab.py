"""Command-line laboratory for experimenting with generated sounds."""

import argparse
import inspect
import os
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

import numpy as np
import soundfile as sf

from .audio import SR
from .sound_design import (
    alien_drone,
    deep_space_drone,
    materialisation,
    metallic_signal,
    radar_ping,
    ring_mod_drone,
    robot_transmission,
    tardis_materialisation,
    tape_wobble,
    teleportation_beam,
)


OUTPUT_DIR = Path("Tracks") / "lab"
SoundFactory = Callable[..., np.ndarray]
SOUNDS: dict[str, SoundFactory] = {
    "alien_drone": alien_drone,
    "deep_space_drone": deep_space_drone,
    "materialisation": materialisation,
    "metallic_signal": metallic_signal,
    "radar_ping": radar_ping,
    "ring_mod_drone": ring_mod_drone,
    "robot_transmission": robot_transmission,
    "tardis_materialisation": tardis_materialisation,
    "tape_wobble": tape_wobble,
    "teleportation_beam": teleportation_beam,
}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse sound laboratory options."""
    parser = argparse.ArgumentParser(
        description="Generate and save experimental sound-design patches."
    )
    parser.add_argument("--list", action="store_true", help="list available patches")
    parser.add_argument("--gui", action="store_true", help="open the Tk interface")
    parser.add_argument("--sound", choices=sorted(SOUNDS), help="patch to generate")
    parser.add_argument("--duration", type=float, help="duration in seconds")
    parser.add_argument("--frequency", type=float, help="base frequency in Hz")
    parser.add_argument("--base-hz", type=float, help="base frequency in Hz")
    parser.add_argument("--carrier", type=float, help="ring-mod carrier frequency")
    parser.add_argument("--modulator", type=float, help="modulator frequency")
    parser.add_argument("--tremolo", type=float, help="tremolo rate in Hz")
    parser.add_argument("--note", type=float, help="alien-drone MIDI note")
    parser.add_argument("--cutoff", type=float, help="low-pass filter cutoff in Hz")
    parser.add_argument("--wobble", type=float, help="pitch or tape wobble amount")
    parser.add_argument("--detune", type=float, help="drone detuning in Hz")
    parser.add_argument("--movement", type=float, help="drone movement amount")
    parser.add_argument("--pulse-rate", type=float, help="teleportation pulse rate")
    parser.add_argument("--noise-amount", type=float, help="materialisation noise mix")
    parser.add_argument("--echo-delay", type=float, help="radar echo delay in seconds")
    parser.add_argument("--start-hz", type=float, help="materialisation start frequency")
    parser.add_argument("--end-hz", type=float, help="materialisation end frequency")
    parser.add_argument("--output", type=Path, help="output WAV path")
    parser.add_argument("--play", action="store_true", help="open the generated WAV")
    parser.add_argument(
        "--variations",
        type=int,
        default=1,
        help="generate numbered variations with deterministic seeds",
    )
    return parser.parse_args(argv)


def _parameters(args: argparse.Namespace) -> dict[str, float]:
    """Translate shared CLI options into parameters for a selected patch."""
    values = {
        "duration": args.duration,
        "frequency": args.frequency,
        "base_hz": args.base_hz,
        "carrier": args.carrier,
        "modulator": args.modulator,
        "tremolo": args.tremolo,
        "note": args.note,
        "cutoff": args.cutoff,
        "wobble": args.wobble,
        "detune": args.detune,
        "movement": args.movement,
        "pulse_rate": args.pulse_rate,
        "noise_amount": args.noise_amount,
        "echo_delay": args.echo_delay,
        "start_hz": args.start_hz,
        "end_hz": args.end_hz,
    }
    return {key: value for key, value in values.items() if value is not None}


def _play_file(filename: Path) -> None:
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


def generate(args: argparse.Namespace) -> list[Path]:
    """Generate requested variations and return their output paths."""
    if not args.sound:
        raise ValueError("--sound is required unless --list is used")
    if args.variations < 1:
        raise ValueError("--variations must be at least 1")

    output = args.output
    if output is None:
        output = OUTPUT_DIR / f"{args.sound}.wav"
    parameters = _parameters(args)
    paths = []
    for index in range(args.variations):
        factory = SOUNDS[args.sound]
        supported = inspect.signature(factory).parameters
        selected = {
            key: value for key, value in parameters.items() if key in supported
        }
        if args.sound == "materialisation":
            selected["rng"] = np.random.default_rng(42 + index)
        sound = factory(**selected)
        filename = output
        if args.variations > 1:
            filename = output.with_name(f"{output.stem}_{index + 1}{output.suffix}")
        filename.parent.mkdir(parents=True, exist_ok=True)
        sf.write(filename, sound, SR, subtype="PCM_16")
        paths.append(filename)
    return paths


def main(argv: Sequence[str] | None = None) -> int:
    """Run the sound laboratory."""
    args = parse_args(argv)
    if args.gui:
        from .sound_lab_gui import main as run_gui

        run_gui()
        return 0
    if args.list:
        print("\n".join(sorted(SOUNDS)))
        return 0
    try:
        paths = generate(args)
        for path in paths:
            print(f"Generated {path}")
        if args.play:
            _play_file(paths[0])
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        print(f"Unable to generate sound: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
