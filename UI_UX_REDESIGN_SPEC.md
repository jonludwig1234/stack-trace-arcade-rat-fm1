# ARCADE RAT · M-VAVE FM-1 Hardware UI/UX Redesign Specification

> **Status:** Phase 1 Audit & Design Spec (Awaiting Approval Before Phase 2 C Implementation)  
> **Target:** Bare-Metal M-VAVE FM-1 Firmware (`src/`, `240×240` RGB565 ST7789 LCD, JieLi AC791N PI32v2)

---

## 1. Hardware Constraints & Memory Budget

### Display & Rendering Pipeline
- **Panel:** `240×240` RGB565 ST7789 IPS LCD (`FM1_SCREEN_SIZE = 240`, [src/pac_video.h](file:///home/jon/.gemini/antigravity/scratch/fm1-pacman/src/pac_video.h#L13)).
- **Device Blit Architecture:** Banded 16-row streaming (`16 × 240` `uint16_t` = `7,680` B static SRAM buffer `s_synth_band` / `s_band_out`) pushed via `pac_band_blit_fn` (`fm1_screen_blit`) at capped ~60 FPS (`16 ms` frame pacing in [src/fm1_pac_bridge.c](file:///home/jon/.gemini/antigravity/scratch/fm1-pacman/src/fm1_pac_bridge.c#L165)).
- **Font / Graphics Budget:** Currently **zero bitmap font** exists in `src/pac_synth.c` — only solid rectangles and 1px/2px waveform dots. Adding a compact bit-packed `5×7` uppercase/digit/symbol font (`~48` glyphs × `5` bytes = **`240` bytes** in `.rodata` flash) enables crisp, zero-RAM-overhead text labels.

### Physical Inputs (`struct fm1_controls` in [src/fm1_pac_bridge.c](file:///home/jon/.gemini/antigravity/scratch/fm1-pacman/src/fm1_pac_bridge.c#L19-L25))
- **27 Silicone Performance Keys (`keys` bitmask, `0..26`):** `C3 (48)` to `D5 (74)`.
- **14 Function Buttons (`buttons` bitmask):** Currently only `Btn 0` (`REC`), `Btn 1` (`PLAY`), `Btn 2` (`STOP`), `Btn 3` (`MUTE`), and `0x09` (`REC + MUTE` combo) are wired.
- **7 Rotary Encoders (`encoders[0..6]` deltas) + `knob` (`uint16_t`) + `battery` (`uint16_t`):** Currently only `encoders[1]` is mapped (Waveform `0..7`); `encoders[2..6]`, `knob`, and `battery` are completely unused.

### Flash & SRAM Constraints ([firmware/build_report.json](file:///home/jon/.gemini/antigravity/scratch/fm1-pacman/firmware/build_report.json))
- `.text`: `360,672` B · `.ram0_data`: `80,744` B · `.ram0_bss`: `246,048` B · `runtime_heap_bytes`: `196,748` B (minimum `49,152` B)
- `app_bin_bytes`: **`441,448` / `453,921` B max** (**`12,473` B Flash headroom**!)
- **Hard Rule:** Zero dynamic allocation (`malloc`/`calloc`), reuse the existing `16×240` static band buffer (`s_synth_band`), keep all font/icon tables `const` in flash, and keep new UI code under **`~4 KB`** `.text` so ample flash headroom remains.

---

## 2. Current UI/UX Pain Points (Codebase Audit)

1. **Zero On-Screen Status in Arcade Mode ([src/pac_core.c](file:///home/jon/.gemini/antigravity/scratch/fm1-pacman/src/pac_core.c#L160-L183)):**
   - Pressing `STOP` (`Btn 2`, God Mode) or `REC` (`Btn 0`, Coin) gives **no visual confirmation** if Pac-Man's attract screen hasn't updated yet or if God Mode is toggled mid-game.
2. **No Text, Parameter Values, or Envelope Preview in Synth Mode ([src/pac_synth.c](file:///home/jon/.gemini/antigravity/scratch/fm1-pacman/src/pac_synth.c#L105-L195)):**
   - Synth Mode draws only a grid, a waveform curve, an 8-segment top bar, and 3 bottom voice bars. There is **no** waveform name/number text, **no** `VOL` / `ATK` / `DEC` values, **no** battery/mode badge, and **no** visual feedback when turning encoders or adjusting ADSR.
3. **Underutilized Hardware Controls ([src/fm1_pac_bridge.c](file:///home/jon/.gemini/antigravity/scratch/fm1-pacman/src/fm1_pac_bridge.c#L123-L132)):**
   - `encoders[2]` and `encoders[3]` (Decay, Attack/Master Vol) are unmapped; `pac_synth_t` has `attack_rate`, `decay_rate`, and `master_volume` fields that **cannot be edited from hardware**.
4. **No Safe Defaults / Confirmation for Destructive Actions:**
   - `fm1_nvram_erase()` exists in [src/fm1_flash_hw.c](file:///home/jon/.gemini/antigravity/scratch/fm1-pacman/src/fm1_flash_hw.c#L337) with no hardware UI trigger or confirmation prompt.
5. **No Universal "Home / Back" Gesture:**
   - Pressing `MUTE` (`Btn 3`) toggles `ARCADE ↔ SYNTH`, while `REC + MUTE` (`0x09`) toggles Groovebox fallback, with no on-screen toast or consistent "Back to Home" behavior if an Edit page is open.

---

## 3. New Information Architecture & Unified Input Grammar

### Shallow 2-Level Hierarchy
- **Level 1 — Performance Home (Zero-Diving):**
  - **`UI_SCREEN_ARCADE`**: Full `240×240` Z80 Pac-Man display + non-blocking `1.2 s` top-bar toast overlay on state changes (`COIN +1`, `GOD MODE ON/OFF`, `ARCADE MODE`).
  - **`UI_SCREEN_SYNTH_HOME`**: 1-screen Synth Performance view (Header + WSG Waveform + ADSR Envelope Curve + 3 Voice Bars + Live Param Strip).
- **Level 2 — Streamlined Edit / Utility Pages (`1/2`, `2/2`) & Confirm Modal:**
  - **`UI_SCREEN_SYNTH_EDIT` (`1/2`)**: Sound Parameters (`WAVE`, `VOL`, `ATK`, `DEC`) with proportional level bars and inverted active pill.
  - **`UI_SCREEN_SYSTEM` (`2/2`)**: Hardware/NVRAM Status (`REV 1/2 JEDEC`, `NVRAM CRC OK`, `[PLAY] SAVE`, `[STOP] CLEAR NVRAM`).
  - **`UI_SCREEN_CONFIRM`**: Modal prompt for destructive actions (`CLEAR NVRAM? [PLAY=YES] [STOP=NO]`).

### Unified Input Grammar Table

| Control | Arcade Home | Synth Home | Edit Page (`1/2` · `2/2`) | Confirm Modal |
| :--- | :--- | :--- | :--- | :--- |
| **Keys 12/14/16/17** (`C4/D4/E4/F4`) | D-Pad (`L/U/D/R`) | Play Notes (`C4..F4`) | Play Notes (`C4..F4`) | Ignored |
| **All 27 Keys** (`0..26`) | Ignored (no WSG hijack) | Play Polyphonic WSG | Play Polyphonic WSG | Ignored |
| **`REC` (`Btn 0`)** | Insert Coin (`+1` toast) | Cycle Page (`Home → 1/2 → 2/2`) | Next Page / Back to Home | Cancel (`No`) |
| **`PLAY` (`Btn 1`)** | Start 1P | Trigger Test Chord / Save (`2/2`) | Save NVRAM (`2/2`) | **Confirm (`Yes`)** |
| **`STOP` (`Btn 2`)** | Toggle God Mode (toast) | **Home / Back** (no-op on Home) | **Back to Synth Home** | **Cancel (`No`)** |
| **`MUTE` (`Btn 3`)** | Switch → Synth Home | Switch → Arcade Home | Switch → Arcade Home | Cancel (`No`) |
| **`REC + MUTE` (`0x09`)** | Toggle Groovebox Fallback | Toggle Groovebox Fallback | Toggle Groovebox Fallback | Toggle Groovebox |
| **`Encoder 1`** | Volume / Pass-through | Select Waveform (`0..7`) | Select Waveform (`0..7`) | Ignored |
| **`Encoder 2`** | — | Adjust `DECAY` (live) | Adjust Selected Param | Ignored |
| **`Encoder 3`** | — | Adjust `MASTER VOL` (`0..15`) | Move Param Cursor (`0..3`) | Ignored |

---

## 4. `240×240` Pixel-Grid ASCII Wireframes

### Screen 1: Synth Performance Home (`UI_SCREEN_SYNTH_HOME`, `240×240`)
```text
+----------------------------------------------------------+ y=0
| ARCADE RAT   WSG:3 SAW   3V   [SYNTH]          BAT 92%  | 20px Header (#0D1318)
+----------------------------------------------------------+ y=20
| [0][1][2][■3■][4][5][6][7]                              | 14px WSG Selector Strip
|                                                          |
|       /\        /\          |    ADSR ENVELOPE           |
|      /  \      /  \         |     /\                     | 132px Split Canvas:
| ----/----\----/----\----    |    /  \________            | Left: 32-step WSG Wave
|           \  /              |   /            \           | Right: Live ADSR Curve
|            \/               |  /              \          |
+----------------------------------------------------------+ y=166
| V1 [████████░░]  V2 [░░░░░░░░░░]  V3 [████░░░░░░]       | 28px 3-Voice Bars
+----------------------------------------------------------+ y=194
| VOL:15 [██████]  DEC:1500 [███░░]  ATK:12K   [REC:EDIT] | 24px Live Param Footer
| * TOAST OVERLAY (1.2s when triggered): "WSG 3: SAW"    * | 22px Bottom Safe Margin
+----------------------------------------------------------+ y=240
```

### Screen 2: Edit Page `1/2` (`UI_SCREEN_SYNTH_EDIT`, `240×240`)
```text
+----------------------------------------------------------+ y=0
| SYNTH EDIT                        PAGE 1/2   [STOP:HOME] | 20px Header
+----------------------------------------------------------+ y=20
| > WAVEFORM   [ 3: SAWTOOTH       ]  < E1 / E2 >          | Inverted Pill (#00E5FF)
|   MASTER VOL [████████████░░░] 15                        |
|   DECAY RATE [████░░░░░░░░░░░] 1500                      | 180px Param Rows
|   ATTACK     [███████████░░░░] 12000                     | (24px row height, 6px pad)
|                                                          |
+----------------------------------------------------------+ y=200
| [REC] PAGE 2/2 (SYSTEM)   [PLAY] SAVE NVRAM  [STOP] HOME | 40px Soft-Key Bar
+----------------------------------------------------------+ y=240
```

### Screen 3: Arcade Performance + Non-Blocking Toast (`UI_SCREEN_ARCADE`, `240×240`)
```text
+----------------------------------------------------------+ y=0
| 8px|           [224px Centered Pac-Man CRT]         |8px |
| B  |  +------------------------------------------+  | B  |
| E  |  | * NON-BLOCKING TOAST (1.2s): GOD MODE ON |  | E  | (Translucent bar y=4..22)
| Z  |  +------------------------------------------+  | Z  |
| E  |                                                | E  |
| L  |             (Full 60Hz Z80 Maze)               | L  |
+----------------------------------------------------------+ y=240
```

### Screen 4: Destructive Action Confirmation (`UI_SCREEN_CONFIRM`, `240×240`)
```text
+----------------------------------------------------------+ y=0
| SYSTEM / NVRAM                    PAGE 2/2   [STOP:HOME] | 20px Header
+----------------------------------------------------------+ y=20
|                                                          |
|      +--------------------------------------------+      |
|      |  ERASE ALL NVRAM SCORES & SETTINGS?        |      | Centered Modal
|      |  This clears Slot A & Slot B permanently.  |      | (#141A22, #FF4757 border)
|      |                                            |      |
|      |     [ PLAY: YES ]        [ STOP: NO ]      |      |
|      +--------------------------------------------+      |
|                                                          |
+----------------------------------------------------------+ y=240
```

---

## 5. Phased Implementation Checklist (Phase 2 & Phase 3)

### Phase 2: Modular UI Implementation
- [ ] **UI Primitives (`src/pac_ui.h` / `src/pac_ui.c`):**
  - Compact `const` `5×7` bitmap font in Flash (`~240` B), `ui_draw_text_band()`, `ui_draw_rect_band()`, `ui_draw_bar_band()`, `ui_draw_header_band()`, and `ui_draw_toast_band()`.
  - Zero dynamic allocation; operates directly on `16×240` band buffers (`s_synth_band`).
- [ ] **UI State Machine & Input Router (`src/fm1_pac_bridge.c` / `src/pac_synth.c`):**
  - Add `ui_screen_t` (`UI_SCREEN_ARCADE`, `UI_SCREEN_SYNTH_HOME`, `UI_SCREEN_SYNTH_EDIT`, `UI_SCREEN_SYSTEM`, `UI_SCREEN_CONFIRM`), `toast_frames` countdown (`72` frames @ 60Hz = `1.2 s`), and `edit_cursor` (`0..3`).
  - Wire `encoders[2]` (`decay_rate`), `encoders[3]` (`master_volume`), `Btn 0/1/2/3` per the Unified Input Grammar Table, with strict min/max clamping.
- [ ] **Decoupled Band Rendering:**
  - Render all new Synth Home, Edit `1/2`, System `2/2`, Confirm Modal, and Arcade Toast overlays cleanly in both host (`pac_synth_draw_ui`) and device band (`pac_synth_draw_ui_bands`) paths with **100% pixel-for-pixel parity**.

### Phase 3: Build, Visual & Functional Verification
- [ ] **Compile & Sanitizer Check:** `make test` + `gcc -fsanitize=address,undefined -Wall -Wextra` with zero warnings and zero errors.
- [ ] **Host Framebuffer PNG Previews (`./ui_previews/`):** Export 4× nearest-neighbor upscaled PNGs of Synth Home, Edit `1/2`, System `2/2`, Confirm Modal, and Arcade Toast, and inspect them visually to confirm zero clipping or overlap.
- [ ] **Regression Assertions:** Verify parameter clamping (`VOL 0..15`, `DEC 200..8000`, `WAVE 0..7`), `REC`/`PLAY`/`STOP`/`MUTE` transitions, destructive NVRAM clear confirmation (`STOP` cancels without erasing; `PLAY` erases), and host-vs-band pixel parity.
