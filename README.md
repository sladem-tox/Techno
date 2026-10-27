# Python Techno

A small generative techno machine written in Python. It synthesizes drums,
bass, chords, effects, and writes the result to a WAV file.

## Requirements

- Python 3.12 or newer
- [`uv`](https://docs.astral.sh/uv/)

## Setup

From the project directory, install or synchronize the environment:

```powershell
uv sync
```

## Generate a track

Run the default composition:

```powershell
uv run techno
```

The command writes the generated audio to:

```text
python_techno.wav
```

To open the WAV file using the default Windows audio player:

```powershell
Start-Process .\python_techno.wav
```

## Display the waveform

Display the waveform with Matplotlib:

```powershell
uv run python -m techno.read
```

To display a different WAV file:

```powershell
uv run python -m techno.read .\Tracks\python_techno.wav
```

## Check individual sounds

List the generated drum/effect sounds and files in `samples/`:

```powershell
uv run python -m techno.sound_chk --list
```

Play one of the listed sounds:

```powershell
uv run python -m techno.sound_chk --play drums:kick
uv run python -m techno.sound_chk --play effects:noise_sweep
uv run python -m techno.sound_chk --play sfx:coin
uv run python -m techno.sound_chk --play sfx:explosion
uv run python -m techno.sound_chk --play sfx:death
uv run python -m techno.sound_chk --play sfx:spaceship
```

The installed command is also available:

```powershell
uv run sound_chk --list
uv run sound_chk --play drums:kick
uv run sound_chk --play sfx:laser
uv run sound_chk --play sfx:death
uv run sound_chk --play sfx:spaceship
```

Generated preview sounds are written to `Tracks/sound_check/` before they are
opened with the default audio player. Sample files are opened directly.

## Experiment with sound design

Use the sound laboratory for adjustable, non-compositional experiments:

```powershell
uv run sound_lab --list
uv run sound_lab --sound ring_mod_drone --carrier 220 --modulator 37 --duration 4 --play
uv run sound_lab --sound materialisation --duration 3 --noise-amount 0.6
uv run sound_lab --sound alien_drone --note 38 --cutoff 1400
uv run sound_lab --sound radar_ping --frequency 1200 --echo-delay 0.35
uv run sound_lab --sound teleportation_beam --duration 2 --pulse-rate 14
```

Laboratory WAV files are written to `Tracks/lab/`. Generate several deterministic
variations for comparison with `--variations`, or choose a filename with
`--output`.

For an interactive Tk interface, run:

```powershell
uv run sound_lab_gui
# Or:
uv run sound_lab --gui
```

Select a patch to reveal its parameters, edit the values, then generate or
generate and play the resulting WAV.

## Project structure

```text
src/techno/
├── cli.py                  # Command-line settings and entry point
├── composition.py          # Composition discovery and selection
├── render.py               # Rendering and WAV output
├── audio.py                # Filters, panning, and mixing helpers
├── drums.py                # Drum synthesizers
├── synths.py               # Bass, chords, and oscillators
├── sfx.py                 # Retro video-game-style one-shot generators
├── sound_design.py        # Experimental sound-design generators
├── sound_lab.py           # Sound-design experimentation CLI
├── effects.py              # Delay and mastering
├── read.py                 # WAV waveform display
└── compositions/
    └── composition1.py     # Bar-by-bar arrangement
```

### Synthesizer sounds

`synths.py` provides reusable waveform and note generators:

```python
from ..synths import synth_lead, synth_pad, synth_pluck

add(track, synth_lead(72), time_seconds=8 * bar)
add(track, synth_pluck(60), time_seconds=8 * bar + beat)
add(track, synth_pad((60, 64, 67)), time_seconds=12 * bar)
```

Available waveforms are `sine`, `saw`, `square`, `triangle`, and `pulse`.
`synth_note()` exposes waveform, ADSR envelope, filter cutoff, vibrato, and
gain controls; `synth_lead()`, `synth_pluck()`, and `synth_pad()` provide
convenient instrument-style presets.

## Creating a new composition

Copy the existing arrangement:

```text
src/techno/compositions/composition1.py
→ src/techno/compositions/composition2.py
```

Edit `composition2.py`, then select it from the command line:

```powershell
uv run techno --composition composition2
```

The output filename is derived automatically from the composition:

```text
Tracks/composition1.wav
Tracks/composition2.wav
```

List available compositions with:

```powershell
uv run techno --list-compositions
```

`render.py` no longer needs to be edited when adding a composition. Each
composition module must define an `arrange()` function with the same signature
as `composition1.py`.

Keep finished WAV files in `Tracks/` so they are separate from the generated
working output.

## Adding samples to a composition

Samples in `samples/` can be loaded and positioned with `add()`. For example,
to place `samples/voice/warning.wav` at the start of bar 20:

```python
from ..audio import add_exclusive
from ..samples import load_sample


def arrange(track, *, bpm, n_bars, rng):
    beat = 60.0 / bpm
    bar = 4 * beat

    warning = load_sample("voice/warning.wav")
    add_exclusive(
        track,
        warning,
        time_seconds=20 * bar,
        gain=0.8,
        pan_pos=0.0,
    )
```

`time_seconds` is measured from the beginning of the track. You can position a
sample relative to beats or bars, for example:

```python
time_seconds = 8 * bar + 2.5 * beat
```

Use `add_exclusive()` when the sample needs space in the arrangement. It
clears the existing mix for exactly the sample's duration before adding it.
For a sample that lasts three seconds, no other previously-arranged sounds
will remain in that three-second window:

```python
sample = load_sample("voice/warning.wav")
add_exclusive(track, sample, time_seconds=20 * bar)
```

Use the normal `add()` function instead when the sample should layer over the
existing music.

Samples are automatically converted to the project sample rate (`44,100 Hz`)
and stereo samples are mixed to mono by default. Use
`load_sample("path/to/file.wav", mono=False)` to preserve stereo data.

The loader currently supports formats handled by `soundfile`, such as WAV.