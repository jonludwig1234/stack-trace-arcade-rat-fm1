# ARCADE RAT · M-VAVE FM-1 Bare-Metal Custom Firmware & Arcade Synthesizer

**ARCADE RAT (v1.0)** is a high-performance custom firmware and retro audio-visual workstation for the **M-VAVE FM-1** pocket FM synthesizer (JieLi AC791N / Dual-Core RISC-V DSP architecture).

It transforms the pocket FM-1 synth into a full-fledged 80s arcade sound chip laboratory, tracker workstation, and playable retro arcade engine.

---

## 🌟 Key Features

1. **8 Playable Classic Arcade Engines (Bare-Metal Z80 & Sound Hardware Emulation):**
   - **Pac-Man (1980 Namco):** Z80 CPU + Namco 3-voice custom wavetable WSG.
   - **Crazy Climber (1980 Nichibutsu):** Dual AY-3-8910 PSG sound generator.
   - **Galaga (1981 Namco):** Dual Z80 + 3-voice WSG + discrete explosion noise.
   - **Donkey Kong (1981 Nintendo):** Intel 8035 microcontroller + 7-bit DAC.
   - **Frogger (1981 Konami):** Dual AY-3-8910 PSG + 10-channel polyphony.
   - **Asteroids (1979 Atari):** Vector state engine + discrete POKEY thrust & explosions.
   - **Tempest (1981 Atari):** Color vector engine + dual POKEY frequency sweeps.
   - **Gyruss (1983 Konami):** 5x AY-3-8910 stereo PSG baroque counterpoint engine.

2. **5-Engine Hardware Synthesizer Studio:**
   - **Namco 3-Voice WSG:** 32-step 4-bit PROM wavetable synthesis with sub-oscillator.
   - **GI AY-3-8910 PSG:** Detuned dual-square waveforms with 60Hz chiptune chord arpeggios.
   - **Atari POKEY:** Polynomial noise & FM distortion counter leads.
   - **Nintendo 2A03 APU / DAC:** Sub-octave triangle & 7-bit pulse leads.
   - **M-VAVE 6-Operator FM:** 32-algorithm DX7-compatible FM synthesis with shimmer chorus.
   - **Real-Time DSP Rack:** 24dB/oct resonant ladder low-pass filter, 340ms tape delay, and harmonic feedback control via 4 top rotary encoders.

3. **16-Step Multi-Chip Tracker:**
   - 4-channel pattern sequencer running across all sound chips simultaneously.
   - 8 factory patterns including *Arcade Rat Theme*, *Pac-Mania Dub*, *Gyruss Speed Run*, *Cyber Labyrinth*, and Bach's *Toccata in D Minor*.

4. **108-Key Arcade SFX Soundboard:**
   - 4 master banks with 27 silicone keys each (Golden Age, Nintendo 8-Bit, Atari Vector/Williams, Konami/Sega FM).

5. **Vintage Arcade Speech ROM Shelf:**
   - 8 authentic voice synthesis ROMs emulated (TSI S14001A, Votrax SC-01, Harris HC-55516 CVSD, and 8-bit Linear PCM).
   - Features iconic voices from *Berzerk*, *Q*bert*, *Sinistar*, *Wizard of Wor*, *Gorf*, and *Dragon's Lair*.

6. **Tactical Hardware Deck & Visualizer:**
   - Real-time 30fps/60fps CRT monitor emulation on the 240×240 IPS panel.
   - X-Y Lissajous stereo phase vector oscilloscope.
   - Z80 RAM state rewind engine & circuit-bending glitch generator.
   - NVRAM persistent Hall of Fame high-score leaderboard.

---

## 🚀 Installation & Flashing on M-VAVE FM-1

### Community Repositories & Hubs
This firmware is compatible with community flashing utilities and repositories:
- **Central Community Directory:** Listed in [aroum/fm1-custom-fw](https://github.com/aroum/fm1-custom-fw)
- **Flashing Utility:** Use [M-Flasher](https://github.com/jvitkauskas/M-Flasher) or the official `M-UPGRADE` tool.

### Flashing Steps
1. Put the M-VAVE FM-1 into bootloader/download mode (hold the first rotary encoder / boot pin while connecting USB-C).
2. Run `m-flasher` or `upgrade.py`:
   ```bash
   m-flasher flash arcade_rat_fm1.fwsc
   ```
3. Reboot device.

---

## 🛠️ Web Workbench & Simulator
You can test the entire firmware, tracker, synthesizer, and arcade vault directly in the browser via Web Audio & Canvas:
- Open `web/fm1_pacman_preview.html` in any modern web browser or run:
  ```bash
  python3 -m http.server 8085 --directory web
  ```

---

## 📜 License & Credits
- Firmware architecture by **Stack Trace** (`stack_trace`).
- Built upon the [m-vave/fm1_open](https://github.com/m-vave/fm1_open) open-source SDK initiative.
- Emulation cores: Z80 (Lin Ke-Fong), AY-3-8910, Namco WSG, Atari POKEY.
