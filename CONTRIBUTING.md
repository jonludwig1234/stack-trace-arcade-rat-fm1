# Contributing to Arcade Rat

We welcome community additions, especially new retro engines, synth models, and hardware refinements for the M-VAVE FM-1!

## Architecture Overview

The firmware core lives in `src/`:
- `src/pac_core.c` — Master multi-engine dispatch (`pac_core_init`, `pac_core_tick`, `pac_core_audio`) across Z80 arcade cores, 5-chip synthesizer, tracker, and SFX modes.
- `src/pac_synth.c` — Polyphonic 5-chip synth & tracker engine (`FM / YM2612`, `SID`, `NES`, `PSG`, `TIA`, `OPL2`, `POKEY`, `SN76489`, `WSG`, plus Arcade SFX soundboard).
- `src/z80.c` / `src/pac_video.c` / `src/pac_wsg.c` — Z80 CPU, arcade video renderer, and Namco WSG 3-voice wavetable audio core.
- `src/fm1_pac_bridge.c` — M-VAVE FM-1 hardware integration layer (`fm1_pacman_tick_controls`, `fm1_pacman_poll_toggle`, `fm1_pacman_audio_mix`).
- `src/fm1_flash_hw.c` — Dual-hardware SPI Flash abstraction supporting both Old Rev 1 (Puya `0x856014`) and New Rev 2 (UCUN `0xB36014`) FM-1 flash chips.

## Building & Testing Locally

Run host unit tests and container validation via Make:
```bash
make clean
make all
```

To run the full 25-battery firmware & browser verification suite:
```bash
python3 tools/master_firmware_qa.py
```

If you have the JieLi PI32v2 toolchain + `fm1_open` SDK installed under Wine, regenerate and verify `arcade_rat_fm1.fwsc` (`FM-1_8000014`) with:
```bash
python3 tools/build_firmware_package.py
```

## Hooking a New Engine or Mode into Arcade Rat

1. Add or register the engine mode in `src/pac_core.c` and expose any synthesizer/audio helpers via `src/pac_synth.c` or a new `src/` module.
2. Route FM-1 controls (`BTN_*`, rotary encoders, and 128×64 OLED scanline bands) in `src/fm1_pac_bridge.c` and keep audio-path code marked with `FM1_AUDIO_CODE` / `FM1_AUDIO_DATA` when targeting AC791N SRAM.
3. Add host regression tests in `tools/test_native_c_firmware.c` and re-run `make all` and `python3 tools/master_firmware_qa.py`.
