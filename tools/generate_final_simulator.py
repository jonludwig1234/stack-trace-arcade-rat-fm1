#!/usr/bin/env python3
"""
Generate the fully working, battle-tested M-VAVE FM-1 Web Simulator.
Embeds Molly Howell's Z80 CPU, authentic Pac-Man ROMs, Namco WSG audio,
authentic 27-key arcade SFX synthesizer, 4 full multi-engine demo songs,
on-screen D-Pad, quick-play engine, and interactive groovebox effects.
"""
import base64
import json
import os

def main():
    # 1. Read Arcade ROMs
    rom_files = {
        "r6e": "roms/pacman.6e",
        "r6f": "roms/pacman.6f",
        "r6h": "roms/pacman.6h",
        "r6j": "roms/pacman.6j",
        "color": "roms/82s123.7f",
        "pal": "roms/82s126.4a",
        "tile": "roms/pacman.5e",
        "sprite": "roms/pacman.5f",
        "sound": "roms/82s126.1m",
    }
    roms_b64 = {}
    for k, p in rom_files.items():
        with open(p, "rb") as f:
            roms_b64[k] = base64.b64encode(f.read()).decode("ascii")

    # 2. Read Z80.js (pure JS instruction interpreter)
    z80_path = "tools/z80_source.js" if os.path.exists("tools/z80_source.js") else "/tmp/js-pacman/src/client/Z80.js"
    with open(z80_path, "r") as f:
        z80_source = f.read()

    # Adapt Z80 for browser script inclusion
    z80_source = z80_source.replace("export default function Z80", "function Z80")

    # 3. Read Demo Songs JSON
    with open("tools/demo_songs.json", "r") as f:
        demo_songs_json = f.read()

    # 4. Read Stack Trace Avatar Base64
    with open("web/images/stack_trace_avatar_b64.txt", "r") as f:
        avatar_b64 = f.read().strip()

    # 5. Read Stack Trace Chiptunes Album Cover Base64
    with open("web/images/stack_trace_chiptunes_album_b64.txt", "r") as f:
        album_b64 = f.read().strip()

    # 5. Build the full simulator HTML
    template_path = "tools/simulator_template.html"
    with open(template_path, "r") as tf:
        template = tf.read()

    html = template.replace("__Z80_SOURCE__", z80_source)
    html = html.replace("__ROMS_PAYLOAD__", json.dumps(roms_b64))
    html = html.replace("__DEMO_SONGS__", demo_songs_json)
    html = html.replace("__STACK_TRACE_AVATAR_B64__", avatar_b64)
    html = html.replace("__STACK_TRACE_ALBUM_B64__", album_b64)

    out_path = "web/fm1_pacman_preview.html"
    with open(out_path, "w") as out:
        out.write(html)

    print(f"Successfully generated {out_path} ({os.path.getsize(out_path)} bytes)!")

if __name__ == "__main__":
    main()
