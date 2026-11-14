# Arcade Rat v1.0 — User Manual

## Flashing Precompiled Firmware (`arcade_rat_fm1.fwsc`)

1. Download `arcade_rat_fm1.fwsc` (`FM-1_8000014`, 479,796 bytes) and optionally verify its SHA-256 against `firmware/SHA256SUMS.txt`.
2. Connect your M-VAVE FM-1 via USB-C and open `web/configurator.html` in a WebMIDI-capable browser (or use the M-UPGRADE web flasher / `m-flasher`).
3. Put the unit into bootloader/update mode as needed by your flasher (dual-verified across both Old Rev 1 Puya `0x856014` and New Rev 2 UCUN `0xB36014` flash hardware) and flash `arcade_rat_fm1.fwsc`.

## Mode Switching on FM-1 Hardware

* **`REC + MUTE` Combo (`0x09`)**: Hold **REC** and press **MUTE** simultaneously to toggle between **Arcade / 5-Chip Synth Mode** and the stock **FM-1 Groovebox Mode**.
* **MASTER Knob**: Adjusts master output volume across both modes.

## Arcade & Synth Controls (Software Simulator & Hardware Mapping)

* **Engine Selection**: Cycle through Z80 Arcade Cores (Pac-Man, Ms. Pac-Man, Galaga, Donkey Kong), 5-Chip Synth Models (`YM2612`, `SID 6581`, `NES 2A03`, `SN76489`, `WSG`, etc.), 16-Step Multi-Chip Tracker, and Arcade SFX Board.
* **Synth Keys & Octave Controls**: Play chromatic notes across octaves, trigger factory synth/tracker presets, and adjust DSP filter/delay parameters in real time.

## 16-Step Multi-Chip Tracker

When the Tracker Engine is active:
* **Step Buttons (1–16)**: Toggle sequencer steps for the active track on/off.
* **Track Select & Transport**: Switch between tracks and start/stop step playback.
* **Factory Patterns**: Load built-in multi-chip patterns directly from the pattern bank.
