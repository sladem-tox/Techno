"""Display the waveform stored in a WAV file."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from matplotlib.figure import Figure


DEFAULT_FILENAME = Path("python_techno.wav")


def parse_args(argv: Sequence[str] | None = None) -> Path:
    """Parse command-line arguments and return the input filename."""
    parser = argparse.ArgumentParser(
        description="Display the waveform stored in a WAV file."
    )
    parser.add_argument(
        "filename",
        nargs="?",
        type=Path,
        default=DEFAULT_FILENAME,
        help=f"WAV file to display (default: {DEFAULT_FILENAME})",
    )
    return parser.parse_args(argv).filename


def plot_waveform(
    samples: np.ndarray,
    sample_rate: int,
    filename: Path,
) -> Figure:
    """Create a waveform figure for mono or multi-channel audio."""
    if samples.ndim not in (1, 2):
        raise ValueError(
            f"Expected one- or two-dimensional audio data, got {samples.ndim} dimensions"
        )

    time = np.arange(len(samples)) / sample_rate

    if samples.ndim == 1:
        fig, ax = plt.subplots(figsize=(12, 4), constrained_layout=True)
        ax.plot(time, samples, linewidth=0.5)
        ax.set_ylabel("Amplitude")
    else:
        fig, axes = plt.subplots(
            samples.shape[1],
            1,
            figsize=(12, 3 * samples.shape[1]),
            sharex=True,
            squeeze=False,
            constrained_layout=True,
        )
        for channel, ax in enumerate(axes[:, 0]):
            ax.plot(time, samples[:, channel], linewidth=0.5)
            ax.set_ylabel(f"Channel {channel + 1}")

    fig.suptitle(filename.name)
    fig.supxlabel("Time (seconds)")
    return fig


def main(argv: Sequence[str] | None = None) -> int:
    filename = parse_args(argv)

    try:
        samples, sample_rate = sf.read(filename)
    except (OSError, RuntimeError) as exc:
        print(f"Unable to read {filename}: {exc}", file=sys.stderr)
        return 1

    plot_waveform(samples, sample_rate, filename)
    plt.show()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
