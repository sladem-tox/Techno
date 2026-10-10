"""Composition discovery and selection."""

import importlib
from pathlib import Path
from typing import Protocol, cast

import numpy as np


class Arrangement(Protocol):
    """Interface implemented by every composition arrangement."""

    def __call__(
        self,
        track: np.ndarray,
        *,
        bpm: float,
        n_bars: int,
        rng: np.random.Generator,
    ) -> None:
        ...


COMPOSITIONS_DIR = Path(__file__).parent / "compositions"


def available_compositions() -> list[str]:
    """Return the names of available composition modules."""
    return sorted(
        path.stem
        for path in COMPOSITIONS_DIR.glob("composition*.py")
        if path.stem != "__init__"
    )


def load_arrangement(name: str) -> Arrangement:
    """Load an arrangement function by composition module name."""
    if name not in available_compositions():
        choices = ", ".join(available_compositions())
        raise ValueError(f"Unknown composition {name!r}. Available: {choices}")

    module = importlib.import_module(f".compositions.{name}", package="techno")
    arrangement = getattr(module, "arrange", None)
    if not callable(arrangement):
        raise ValueError(f"{name!r} does not define a callable arrange()")

    return cast(Arrangement, arrangement)
