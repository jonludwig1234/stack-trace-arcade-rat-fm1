import sys
import os

def patch_firmware(firmware_path, rom_path, hex_offset, output_path):
    try:
        offset = int(hex_offset, 16)
    except ValueError:
        print("Error: Target offset must be a valid hex string (e.g., 0x4000).")
        sys.exit(1)

    if not os.path.exists(firmware_path):
        print(f"Error: Firmware file '{firmware_path}' not found.")
        sys.exit(1)

    if not os.path.exists(rom_path):
        print(f"Error: ROM file '{rom_path}' not found.")
        sys.exit(1)

    with open(firmware_path, 'rb') as f:
        fw_data = bytearray(f.read())

    with open(rom_path, 'rb') as f:
        rom_data = f.read()

    # Expand firmware binary if the ROM injection goes past the current EOF
    if offset + len(rom_data) > len(fw_data):
        fw_data.extend(b'\xff' * ((offset + len(rom_data)) - len(fw_data)))

    # Inject the ROM payload
    fw_data[offset:offset+len(rom_data)] = rom_data

    with open(output_path, 'wb') as f:
        f.write(fw_data)

    print(f"Success! Injected {len(rom_data)} bytes from '{rom_path}' into the firmware.")
    print(f"Saved playable build to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Arcade Rat ROM Injector")
        print("Usage: python rom_patcher.py <input.fwsc> <game_rom.bin> <hex_offset> <output.fwsc>")
        sys.exit(1)
    
    patch_firmware(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
