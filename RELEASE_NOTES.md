### ARCADE RAT v1.0.0 Community Release & Dual-Hardware Update

⬇️ **Download Precompiled FM-1 Firmware (.fwsc · 479,796 bytes · `FM-1_8000014`):**
https://github.com/jonludwig1234/stack-trace-arcade-rat-fm1/releases/download/v1.0.0/arcade_rat_fm1.fwsc
- **SHA-256:** `a503dd43d03738fd4b57197233799ade7d7beae349cb2011f2ce13c256e9fa6b`
- **Verified:** PI32v2 ELF + internal SRAM audio ISR + `_MALLOC_SIZE` `196,748` B + `WebUpdate.js` `inspectPackage()` check (`app.bin` `441,448` B)

🎬 **Watch / Download 1080p Video Showcase (MP4):**
https://github.com/jonludwig1234/stack-trace-arcade-rat-fm1/releases/download/v1.0.0/fm1_firmware_showcase_demo.mp4

🎵 **Download Master Audio (24-bit WAV):**
https://github.com/jonludwig1234/stack-trace-arcade-rat-fm1/releases/download/v1.0.0/commercial_master_audio.wav

---

#### 🛡️ Verified Dual-Hardware Compatibility (Old & New FM-1 Devices)
- **Old FM-1 Units (Rev 1 / Batch 1):** Verified for Puya P25Q80H SPI NOR Flash (`0x856014`, 1 MiB).
- **New FM-1 Units (Rev 2 / Autumn 2026 Batch with Front Logo):** Verified for UCUN UC25HQ80 SPI NOR Flash (`0xB36014`, 1 MiB).
- **Fixes Community Save Bug:** Resolves the widespread issue where newer units failed to write presets or high scores due to factory block protection bits (`BP0..BP4`, `TB`, `SRP0`). Includes dynamic capacity probing and automatic status register unprotect routines (`WRSR 0x00 0x00`).

---

#### 🎮 Enhanced Multi-Game Arcade Engine Audits
- **Zero Multi-Hit Life Drain:** Single hazard collisions decrement exactly 1 life and grant clean invulnerability / respawn across all 8 arcade titles.
- **Continuous Auto-Fire Cadence:** Holding fire keys provides authentic cadence across Asteroids, Tempest, and Gyruss.
- **Keypad & Touch Restart:** Immediate Game Over restart triggers wired across both physical buttons and virtual D-Pad.

---

#### 🌟 Feature Summary
- **8 Playable Classic Arcade Engines:** Pac-Man, Crazy Climber, Galaga, Donkey Kong, Frogger, Asteroids, Tempest, Gyruss.
- **5 Hardware Synthesizer Studio Engines:** WSG, AY-3-8910, POKEY, 2A03 DAC, 6-Op FM with real-time DSP resonant ladder filter and tape delay.
- **16-Step Multi-Chip Tracker:** 4-channel pattern sequencer with 8 factory patterns.
- **108 Arcade SFX Pads:** 4 silicone banks covering Golden Age, Nintendo 8-Bit, Atari Vector, and Konami/Sega FM.
- **8 Authentic Vintage Speech ROMs:** TSI S14001A, Votrax SC-01, Harris HC-55516 CVSD, Linear PCM (Berzerk, Q*bert, Sinistar, Gorf, Wizard of Wor).
- **Production Certified:** 25/25 Master Firmware QA battery suites passing 100% green.
