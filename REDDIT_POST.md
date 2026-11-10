# Reddit Post: r/MVaveFM1

**URL:** https://www.reddit.com/r/MVaveFM1/submit

---

### Post Title:
[Custom Firmware Release] ARCADE RAT v1.0 — 8 Classic Arcade Cores, 5-Chip Synth Studio, 16-Step Tracker & Vintage Speech ROMs for M-VAVE FM-1

---

### Post Body / Content:

Hey everyone on r/MVaveFM1!

I've just released **ARCADE RAT (v1.0)**, an open-source bare-metal custom firmware and retro sound workstation for the M-VAVE FM-1 pocket FM synth.

* **GitHub Repository:** https://github.com/jonludwig1234/stack-trace-arcade-rat-fm1
* **Release v1.0.0:** https://github.com/jonludwig1234/stack-trace-arcade-rat-fm1/releases/tag/v1.0.0
* **Demo Video & Master Audio:** Available directly on the release page.

---

### 🛡️ Dual-Hardware Compatibility (Old & New FM-1 Units):
* **Verified on Old Units (Rev 1 / Batch 1):** Puya P25Q80H (`0x856014`, 1 MiB).
* **Verified on New Units (Rev 2 / Autumn 2026 Batch with logo):** UCUN UC25HQ80 (`0xB36014`, 1 MiB).
* **Fixes the Dreaded Save Bug:** If you've tried other custom firmwares on a newer FM-1 and ran into failed saves or wiped patches, it was due to locked status register bits (BP0..BP4) and hardcoded chip IDs. Arcade Rat includes dynamic JEDEC probing and auto-unprotect routines so NVRAM high-scores and presets persist 100% reliably across power cycles on both revisions!

---

### What's Inside:

1. **8 Playable Classic Arcade Engines (Bare-Metal Z80 / Sound Hardware Emulation):**
   - **Pac-Man (1980 Namco):** Z80 CPU + Namco 3-voice custom wavetable WSG.
   - **Crazy Climber (1980 Nichibutsu):** Dual AY-3-8910 PSG sound generator.
   - **Galaga (1981 Namco):** Dual Z80 + 3-voice WSG + discrete explosion noise.
   - **Donkey Kong (1981 Nintendo):** Intel 8035 microcontroller + 7-bit DAC.
   - **Frogger (1981 Konami):** Dual AY-3-8910 PSG + 10-channel polyphony.
   - **Asteroids (1979 Atari):** Vector state engine + discrete POKEY thrust & explosions.
   - **Tempest (1981 Atari):** Color vector engine + dual POKEY frequency sweeps.
   - **Gyruss (1983 Konami):** 5x AY-3-8910 stereo PSG baroque counterpoint engine.

2. **5-Engine Hardware Synth Studio:**
   - **Namco 3-Voice WSG:** 32-step 4-bit PROM wavetable synthesis with sub-oscillator.
   - **GI AY-3-8910 PSG:** Detuned dual-square waveforms with 60Hz chiptune chord arpeggios.
   - **Atari POKEY:** Polynomial noise & FM distortion counter leads.
   - **Nintendo 2A03 APU / DAC:** Sub-octave triangle & 7-bit pulse leads.
   - **M-VAVE 6-Operator FM:** 32-algorithm DX7-compatible FM synthesis with shimmer chorus.
   - **Real-Time DSP Rack:** 24dB/oct resonant ladder low-pass filter, 340ms tape delay, and harmonic feedback control via the 4 top rotary encoders.

3. **16-Step Multi-Chip Tracker:**
   - 4-channel pattern sequencer running across all sound chips simultaneously.
   - 8 factory patterns including *Arcade Rat Theme*, *Pac-Mania Dub*, *Gyruss Speed Run*, *Cyber Labyrinth*, and Bach's *Toccata in D Minor*.

4. **108-Key Arcade SFX Soundboard:**
   - 4 master banks with 27 silicone keys each (Golden Age, Nintendo 8-Bit, Atari Vector/Williams, Konami/Sega FM).

5. **Vintage Arcade Speech ROM Shelf:**
   - 8 authentic voice synthesis ROMs emulated (TSI S14001A, Votrax SC-01, Harris HC-55516 CVSD, and 8-bit Linear PCM).
   - Features iconic voices from *Berzerk*, *Q\*bert*, *Sinistar*, *Wizard of Wor*, *Gorf*, and *Dragon's Lair*.

6. **Web Workbench & Simulator:**
   - Test everything directly in your browser with Web Audio & HTML5 Canvas emulation via `web/fm1_pacman_preview.html`.

---

### How to Flash:
Compatible with **M-Flasher** (cross-platform) and the official `M-UPGRADE` tool:
1. Hold the first rotary encoder while plugging in USB-C to enter download mode.
2. Run `m-flasher flash arcade_rat_fm1.fwsc` or upload via the M-VAVE web tool.

Feedback, feature suggestions, and bug reports are welcome on GitHub!
