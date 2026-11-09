#!/usr/bin/env python3
"""
Convert Pac-Man arcade ROMs into a C header file (pacman_roms.h).
"""
import os
import sys

def main():
    rom_dir = sys.argv[1] if len(sys.argv) > 1 else "roms"
    out_file = sys.argv[2] if len(sys.argv) > 2 else "src/pacman_roms.h"

    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    files = [
        ("pacman_rom_6e", "pacman.6e"),
        ("pacman_rom_6f", "pacman.6f"),
        ("pacman_rom_6h", "pacman.6h"),
        ("pacman_rom_6j", "pacman.6j"),
        ("pacman_color_rom", "82s123.7f"),
        ("pacman_palette_rom", "82s126.4a"),
        ("pacman_tile_rom", "pacman.5e"),
        ("pacman_sprite_rom", "pacman.5f"),
        ("pacman_sound_rom1", "82s126.1m"),
    ]

    with open(out_file, "w") as out:
        out.write("/* Auto-generated Pac-Man ROM data for M-VAVE FM-1 firmware */\n")
        out.write("#ifndef PACMAN_ROMS_H\n#define PACMAN_ROMS_H\n\n#include <stdint.h>\n\n")

        for var_name, filename in files:
            path = os.path.join(rom_dir, filename)
            data = open(path, "rb").read()
            out.write(f"/* {filename} ({len(data)} bytes) */\n")
            out.write(f"static const uint8_t {var_name}[{len(data)}] = {{\n")
            for i, byte in enumerate(data):
                if i % 16 == 0:
                    out.write("    ")
                out.write(f"0x{byte:02x}, ")
                if i % 16 == 15:
                    out.write("\n")
            if len(data) % 16 != 0:
                out.write("\n")
            out.write("};\n\n")

        out.write("#endif /* PACMAN_ROMS_H */\n")

    print(f"Generated {out_file} successfully.")

if __name__ == "__main__":
    main()
