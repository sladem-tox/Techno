"""Command-line interface for rendering compositions."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .composition import available_compositions, load_arrangement
from .render import render

BPM = 128
N_BARS = 32
MASTER_GAIN = 0.75
TRACKS_DIR = Path("Tracks")
def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description="Render a techno composition.")
    parser.add_argument(
        "--composition",
        default="composition1",
        choices=available_compositions(),
        help="composition to render (default: composition1)",
    )
    parser.add_argument(
        "--list-compositions",
        action="store_true",
        help="list available compositions and exit",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Render the selected composition."""
    args = parse_args(argv)
    if args.list_compositions:
        print("\n".join(available_compositions()))
        return 0

    try:
        arrangement = load_arrangement(args.composition)
        TRACKS_DIR.mkdir(parents=True, exist_ok=True)
        render(
            TRACKS_DIR / f"{args.composition}.wav",
            arrange=arrangement,
            bpm=BPM,
            n_bars=N_BARS,
            master_gain=MASTER_GAIN,
        )
    except ValueError as exc:
        print(f"Unable to render composition: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
