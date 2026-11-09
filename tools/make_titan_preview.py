#!/usr/bin/env python3
"""
Generate the M-VAVE FM-1 ARCADE GROOVEBOX // TITAN EDITION interactive Web Simulator.
Implements:
1. Arcade Game Engine (Pac-Man, 60FPS)
2. Live Time Machine (Rolling 10s Rewind Buffer)
3. 4-Soundchip Synth & 16-Step Chiptune Tracker (Namco WSG, AY-3-8910, POKEY)
4. 27-Pad Arcade DJ Soundboard (Instant SFX triggers)
5. Audio-Reactive XY Lissajous & 32-band FFT Spectrum Visualizer
6. Circuit-Bending / Glitch Matrix Engine
7. Dub Tape Delay & Resonant Filter DSP Rack
"""
import base64
import os
import json

def main():
    rom_files = {
        "rom_6e": "roms/pacman.6e",
        "rom_6f": "roms/pacman.6f",
        "rom_6h": "roms/pacman.6h",
        "rom_6j": "roms/pacman.6j",
        "color_rom": "roms/82s123.7f",
        "palette_rom": "roms/82s126.4a",
        "tile_rom": "roms/pacman.5e",
        "sprite_rom": "roms/pacman.5f",
        "sound_rom": "roms/82s126.1m",
    }

    rom_b64 = {}
    for key, path in rom_files.items():
        with open(path, "rb") as f:
            rom_b64[key] = base64.b64encode(f.read()).decode("ascii")

    os.makedirs("web", exist_ok=True)
    out_path = "web/fm1_pacman_preview.html"

    with open("tools/preview_template.html", "r") as tf:
        template = tf.read()

    html = template.replace("__JSON_ROMS_PAYLOAD__", json.dumps(rom_b64))

    with open(out_path, "w") as f:
        f.write(html)

    print(f"Generated {out_path} ({os.path.getsize(out_path)} bytes).")

if __name__ == "__main__":
    main()
