#!/usr/bin/env python3
import os
import struct
import sys

AREA = 0x4000
PUBLIC_CODE = 0x980F
CFG_TOOL_SIZE = 383


def crc16(data, begin=0, length=None):
    if length is None:
        length = len(data) - begin
    val = 0
    for b in data[begin : begin + length]:
        val ^= b << 8
        for _ in range(8):
            val = ((val << 1) ^ (0x1021 if (val & 0x8000) else 0)) & 0xFFFF
    return val


def cipher_inplace(buf, begin, length, state):
    for pos in range(begin, begin + length):
        buf[pos] ^= state & 0xFF
        state = ((state << 1) ^ (0x1021 if (state & 0x8000) else 0)) & 0xFFFF


def is_ac791n_fwsc(fw_data):
    if len(fw_data) < 1044:
        return False
    ufw_head = bytearray(64)
    ufw_head[:47] = fw_data[:47]
    ufw_head[47:64] = fw_data[48:65]
    cipher_inplace(ufw_head, 0, 64, 65535)
    return ufw_head[16:22] == b"AC791N"


def patch_ac791n_fwsc(fw_data, rom_data, offset):
    markers = [fw_data[i * 48 + 47] for i in range(20)]
    ufw = bytearray(len(fw_data) - 20)
    for i in range(20):
        ufw[i * 47 : i * 47 + 47] = fw_data[i * 48 : i * 48 + 47]
    ufw[940:] = fw_data[960:]

    head = bytearray(ufw[:64])
    cipher_inplace(head, 0, 64, 65535)
    count = struct.unpack_from("<H", head, 8)[0]

    rec0 = bytearray(ufw[64:144])
    cipher_inplace(rec0, 0, 80, 65535)
    _rtype, _rid, _rcrc, _pad, roff, rsize, _rstored = struct.unpack_from("<HHHHIII", rec0, 0)
    flash = bytearray(ufw[roff : roff + rsize])

    rec_app = bytearray(flash[AREA + 32 : AREA + 64])
    cipher_inplace(rec_app, 0, 32, PUBLIC_CODE ^ (32 >> 2))
    app_addr, app_size = struct.unpack_from("<II", rec_app, 4)
    payload_size = app_addr + app_size + CFG_TOOL_SIZE

    for p in range(0, payload_size + 64, 32):
        chunk = min(32, payload_size + 64 - p)
        cipher_inplace(flash, AREA + p, chunk, PUBLIC_CODE ^ (p >> 2))

    if offset + len(rom_data) > len(flash):
        raise ValueError(f"Patch range 0x{offset:X}+0x{len(rom_data):X} exceeds flash image ({len(flash)} B)")
    flash[offset : offset + len(rom_data)] = rom_data

    app_crc = crc16(flash, AREA + app_addr, app_size)
    struct.pack_into("<H", flash, AREA + 32 + 2, app_crc)
    struct.pack_into("<H", flash, AREA + 32, crc16(flash, AREA + 32 + 2, 30))

    for p in range(0, payload_size + 64, 32):
        chunk = min(32, payload_size + 64 - p)
        cipher_inplace(flash, AREA + p, chunk, PUBLIC_CODE ^ (p >> 2))

    ufw[roff : roff + rsize] = flash
    struct.pack_into("<H", rec0, 4, crc16(flash))
    cipher_inplace(rec0, 0, 80, 65535)
    ufw[64:144] = rec0

    struct.pack_into("<H", head, 2, crc16(ufw, 64, count * 80))
    struct.pack_into("<H", head, 0, crc16(head, 2, 62))
    cipher_inplace(head, 0, 64, 65535)
    ufw[:64] = head

    out = bytearray(len(ufw) + 20)
    dst = 0
    for src in range(len(ufw)):
        out[dst] = ufw[src]
        dst += 1
        if src < 940 and (src + 1) % 47 == 0:
            out[dst] = markers[src // 47]
            dst += 1
    return out


def patch_firmware(firmware_path, rom_path, hex_offset, output_path):
    try:
        offset = int(hex_offset, 16)
    except ValueError:
        print("Error: Target offset must be a valid hex string (e.g., 0x4120).")
        sys.exit(1)

    if not os.path.exists(firmware_path):
        print(f"Error: Firmware file '{firmware_path}' not found.")
        sys.exit(1)

    if not os.path.exists(rom_path):
        print(f"Error: ROM file '{rom_path}' not found.")
        sys.exit(1)

    with open(firmware_path, "rb") as f:
        fw_data = bytearray(f.read())

    with open(rom_path, "rb") as f:
        rom_data = f.read()

    if is_ac791n_fwsc(fw_data):
        out_data = patch_ac791n_fwsc(fw_data, rom_data, offset)
    else:
        if offset + len(rom_data) > len(fw_data):
            fw_data.extend(b"\xff" * ((offset + len(rom_data)) - len(fw_data)))
        fw_data[offset : offset + len(rom_data)] = rom_data
        out_data = fw_data

    with open(output_path, "wb") as f:
        f.write(out_data)

    print(f"Success! Injected {len(rom_data)} bytes from '{rom_path}' into the firmware.")
    print(f"Saved playable build to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Arcade Rat ROM Injector")
        print("Usage: python rom_patcher.py <input.fwsc> <game_rom.bin> <hex_offset> <output.fwsc>")
        sys.exit(1)

    patch_firmware(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
