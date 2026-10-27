"""Tkinter interface for the experimental sound laboratory."""

from __future__ import annotations

import inspect
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

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
from .sound_lab import OUTPUT_DIR, _play_file


SOUNDS = {
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


class SoundLabApp:
    """Interactive sound patch generator."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Techno Sound Lab")
        self.root.resizable(False, False)
        self.parameter_vars: dict[str, tk.StringVar] = {}
        self.parameter_frame = ttk.Frame(root, padding=(12, 0, 12, 8))
        self.output_var = tk.StringVar(value=str(OUTPUT_DIR / "lab_sound.wav"))
        self.variations_var = tk.StringVar(value="1")
        self.status_var = tk.StringVar(value="Choose a patch and generate a sound.")

        ttk.Label(root, text="Sound patch").grid(
            row=0, column=0, padx=12, pady=(12, 6), sticky="w"
        )
        self.sound_var = tk.StringVar(value=next(iter(SOUNDS)))
        sound_menu = ttk.Combobox(
            root,
            textvariable=self.sound_var,
            values=sorted(SOUNDS),
            state="readonly",
            width=26,
        )
        sound_menu.grid(row=0, column=1, padx=12, pady=(12, 6), sticky="ew")
        sound_menu.bind("<<ComboboxSelected>>", self._select_sound)

        self.parameter_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        self._select_sound()

        ttk.Label(root, text="Output WAV").grid(
            row=2, column=0, padx=12, pady=6, sticky="w"
        )
        ttk.Entry(root, textvariable=self.output_var, width=36).grid(
            row=2, column=1, padx=12, pady=6, sticky="ew"
        )
        ttk.Label(root, text="Variations").grid(
            row=3, column=0, padx=12, pady=6, sticky="w"
        )
        ttk.Spinbox(
            root, from_=1, to=99, textvariable=self.variations_var, width=8
        ).grid(row=3, column=1, padx=12, pady=6, sticky="w")

        actions = ttk.Frame(root, padding=12)
        actions.grid(row=4, column=0, columnspan=2, sticky="ew")
        ttk.Button(actions, text="Generate", command=self.generate).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(actions, text="Generate and Play", command=self.generate_and_play).pack(
            side="left"
        )
        ttk.Label(root, textvariable=self.status_var).grid(
            row=5, column=0, columnspan=2, padx=12, pady=(0, 12), sticky="w"
        )

    def _select_sound(self, _event: object | None = None) -> None:
        """Refresh parameter fields for the selected generator."""
        for child in self.parameter_frame.winfo_children():
            child.destroy()
        self.parameter_vars.clear()

        signature = inspect.signature(SOUNDS[self.sound_var.get()])
        row = 0
        for name, parameter in signature.parameters.items():
            if name == "rng" or parameter.default is inspect.Parameter.empty:
                continue
            value = str(parameter.default)
            self.parameter_vars[name] = tk.StringVar(value=value)
            ttk.Label(self.parameter_frame, text=name.replace("_", " ").title()).grid(
                row=row, column=0, padx=(0, 12), pady=4, sticky="w"
            )
            ttk.Entry(self.parameter_frame, textvariable=self.parameter_vars[name], width=18).grid(
                row=row, column=1, pady=4, sticky="w"
            )
            row += 1

    def _generate(self) -> list[Path]:
        """Generate the selected patch and save its WAV file(s)."""
        factory = SOUNDS[self.sound_var.get()]
        parameters: dict[str, float | np.random.Generator] = {}
        for name, variable in self.parameter_vars.items():
            parameters[name] = float(variable.get())
        if self.sound_var.get() == "materialisation":
            parameters["rng"] = np.random.default_rng(42)

        variations = int(self.variations_var.get())
        if variations < 1:
            raise ValueError("variations must be at least 1")
        output = Path(self.output_var.get())
        output.parent.mkdir(parents=True, exist_ok=True)
        paths = []
        for index in range(variations):
            if self.sound_var.get() == "materialisation":
                parameters["rng"] = np.random.default_rng(42 + index)
            sound = factory(**parameters)
            filename = output
            if variations > 1:
                filename = output.with_name(f"{output.stem}_{index + 1}{output.suffix}")
            sf.write(filename, sound, SR, subtype="PCM_16")
            paths.append(filename)
        return paths

    def generate(self) -> None:
        """Generate a sound and update the status label."""
        try:
            paths = self._generate()
            self.status_var.set(f"Generated {paths[0]}")
        except (OSError, TypeError, ValueError) as exc:
            messagebox.showerror("Unable to generate sound", str(exc))

    def generate_and_play(self) -> None:
        """Generate a sound and open the first resulting WAV."""
        try:
            paths = self._generate()
            self.status_var.set(f"Generated {paths[0]}")
            _play_file(paths[0])
        except (OSError, RuntimeError, TypeError, ValueError) as exc:
            messagebox.showerror("Unable to generate or play sound", str(exc))


def main() -> None:
    """Start the Tkinter sound laboratory."""
    root = tk.Tk()
    SoundLabApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
