"""Load audio samples for use in compositions."""

from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

from .audio import SR


SAMPLES_DIR = Path(__file__).resolve().parents[2] / "samples"


def sample_path(relative_path: str | Path) -> Path:
    """Resolve a path relative to the project's samples directory."""
    path = SAMPLES_DIR / relative_path
    if not path.is_file():
        raise FileNotFoundError(f"Sample not found: {path}")
    return path


def load_sample(
    relative_path: str | Path,
    *,
    mono: bool = True,
) -> np.ndarray:
    """Load a sample and convert it to the project's sample rate.

    ``relative_path`` is relative to ``samples/``. Samples are returned as
    floating-point NumPy arrays ready for ``audio.add()``.
    """
    path = sample_path(relative_path)
    data, sample_rate = sf.read(path, always_2d=False)
    sample = np.asarray(data, dtype=float)

    if sample.ndim == 2 and mono:
        sample = np.mean(sample, axis=1)

    if sample_rate != SR:
        sample = resample_poly(sample, SR, sample_rate, axis=0)

    return sample
