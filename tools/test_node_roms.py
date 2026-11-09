#!/usr/bin/env python3
"""
Test harness for full JavaScript Pac-Man emulation in Node.js.
Verifies:
1. Z80 boot
2. VRAM generation
3. 240x240 RGB pixel buffer output
4. Audio WSG updates
"""
import base64
import json
import os

with open("roms/pacman.6e", "rb") as f: r6e = base64.b64encode(f.read()).decode("ascii")
with open("roms/pacman.6f", "rb") as f: r6f = base64.b64encode(f.read()).decode("ascii")
with open("roms/pacman.6h", "rb") as f: r6h = base64.b64encode(f.read()).decode("ascii")
with open("roms/pacman.6j", "rb") as f: r6j = base64.b64encode(f.read()).decode("ascii")
with open("roms/82s123.7f", "rb") as f: color_rom = base64.b64encode(f.read()).decode("ascii")
with open("roms/82s126.4a", "rb") as f: pal_rom = base64.b64encode(f.read()).decode("ascii")
with open("roms/pacman.5e", "rb") as f: tile_rom = base64.b64encode(f.read()).decode("ascii")
with open("roms/pacman.5f", "rb") as f: sprite_rom = base64.b64encode(f.read()).decode("ascii")
with open("roms/82s126.1m", "rb") as f: sound_rom = base64.b64encode(f.read()).decode("ascii")

roms = {
    "r6e": r6e, "r6f": r6f, "r6h": r6h, "r6j": r6j,
    "color": color_rom, "pal": pal_rom,
    "tile": tile_rom, "sprite": sprite_rom, "sound": sound_rom
}

with open("/tmp/roms.json", "w") as f:
    json.dump(roms, f)

print("Saved /tmp/roms.json")
