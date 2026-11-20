# M-VAVE FM-1 Workspace Rules

- **Dual-HTML Synchronization:** `roms/pacman.6e` is absent from this checkout, so `tools/generate_final_simulator.py` cannot rebuild the preview bundle directly. Mirror every web UI, Canvas, audio, and game-engine edit across both `tools/simulator_template.html` and `web/fm1_pacman_preview.html`.
- **Legacy Mock-Canvas Compatibility:** Node QA batteries (`test_frogger_death_fidelity.js`, `test_quality_control_all_games.js`, `test_all_games_arcade_spec.js`, `test_donkey_kong_authentic.js`) supply minimal mock `ctx` objects. Feature-guard `ctx.roundRect`, `ctx.createRadialGradient`, `ctx.moveTo`, and `ctx.closePath` with safe fallbacks (`fillRect` / solid `fillStyle`).
- **Protected Test Invariants:** Preserve the 4 original song titles in `tools/demo_songs.json` required by `tools/verify_all.py` and keep Frogger's respawn dock coordinate (`fg.y === 224` at `gridY = 13`) expected by `tools/test_frogger_death_fidelity.js`.
- **ROM vs. Simulation Clarity:** Only Pac-Man executes a real embedded Z80 arcade binary ROM (`src/pacman_roms.h`); the other 7 included arcade titles are JavaScript Canvas simulations.
