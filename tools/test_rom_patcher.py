#!/usr/bin/env python3
"""Unit and boundary tests for tools/rom_patcher.py."""

import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent
sys.path.insert(0, str(TOOLS_DIR))

import rom_patcher  # noqa: E402


class TestRomPatcher(unittest.TestCase):
    def setUp(self):
        self.fw_path = REPO_ROOT / "arcade_rat_fm1.fwsc"
        self.fw_bytes = self.fw_path.read_bytes()

    def test_valid_ac791n_detection_and_truncated_rejection(self):
        self.assertTrue(rom_patcher.is_ac791n_fwsc(self.fw_bytes))
        self.assertFalse(rom_patcher.is_ac791n_fwsc(self.fw_bytes[:512]))
        self.assertFalse(rom_patcher.is_ac791n_fwsc(b"\x00" * 2048))

    def test_negative_offset_rejected(self):
        with self.assertRaises(ValueError):
            rom_patcher.patch_ac791n_fwsc(self.fw_bytes, b"\xAA\xBB", -16)

        with tempfile.TemporaryDirectory() as tmp:
            rom = Path(tmp) / "rom.bin"
            out = Path(tmp) / "out.fwsc"
            rom.write_bytes(b"\x01\x02")
            res = subprocess.run(
                [sys.executable, str(TOOLS_DIR / "rom_patcher.py"), str(self.fw_path), str(rom), "-0x10", str(out)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(res.returncode, 0)
            self.assertFalse(out.exists())

    def test_oob_offset_rejected(self):
        with self.assertRaises(ValueError):
            rom_patcher.patch_ac791n_fwsc(self.fw_bytes, b"\xAA" * 64, len(self.fw_bytes))

    def test_corrupted_record_count_rejected(self):
        bad = bytearray(self.fw_bytes)
        ufw = bytearray(len(bad) - 20)
        for i in range(20):
            ufw[i * 47 : i * 47 + 47] = bad[i * 48 : i * 48 + 47]
        ufw[940:] = bad[960:]
        head = bytearray(ufw[:64])
        rom_patcher.cipher_inplace(head, 0, 64, 65535)
        struct.pack_into("<H", head, 8, 9999)  # impossible record count
        rom_patcher.cipher_inplace(head, 0, 64, 65535)
        bad[:47] = head[:47]
        bad[48:65] = head[47:64]
        with self.assertRaises(ValueError):
            rom_patcher.patch_ac791n_fwsc(bytes(bad), b"\x00", 0x4100)

    def test_roundtrip_patch_preserves_container_crcs(self):
        # Patch safe trailing padding area inside flash record
        patched = rom_patcher.patch_ac791n_fwsc(self.fw_bytes, b"TEST", 0x4010)
        self.assertEqual(len(patched), len(self.fw_bytes))
        self.assertTrue(rom_patcher.is_ac791n_fwsc(patched))

        # Decode header & verify CRCs match
        ufw = bytearray(len(patched) - 20)
        for i in range(20):
            ufw[i * 47 : i * 47 + 47] = patched[i * 48 : i * 48 + 47]
        ufw[940:] = patched[960:]
        head = bytearray(ufw[:64])
        rom_patcher.cipher_inplace(head, 0, 64, 65535)
        head_crc, table_crc = struct.unpack_from("<HH", head, 0)
        count = struct.unpack_from("<H", head, 8)[0]
        self.assertEqual(head_crc, rom_patcher.crc16(head, 2, 62))
        self.assertEqual(table_crc, rom_patcher.crc16(ufw, 64, count * 80))


if __name__ == "__main__":
    unittest.main()
