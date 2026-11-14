#!/usr/bin/env python3
"""Build, verify, and package precompiled M-VAVE FM-1 Arcade Rat firmware (.fwsc).

Uses the JieLi PI32v2 r3 toolchain under Wine and implements the exact
AC791N flash image and encrypted .fwsc container specification from
fm1_open/sdk/Build.ps1 and fm1_open/sdk/Package.cs.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FM1_OPEN = REPO_ROOT / "fm1_open"
SDK_DIR = FM1_OPEN / "sdk"
BUILD_DIR = FM1_OPEN / "build" / "dx7"
OBJ_DIR = BUILD_DIR / "obj"
GEN_DIR = BUILD_DIR / "generated"
TOOLCHAIN_BIN = Path(os.environ.get("FM1_PI32_TOOLCHAIN", "/home/jon/.gemini/antigravity/scratch/jieli_pi32")) / "bin"

PACK_RESOURCES = SDK_DIR / "tools" / "pack"
OUT_ROOT_FWSC = REPO_ROOT / "arcade_rat_fm1.fwsc"
OUT_FW_DIR = REPO_ROOT / "firmware"
OUT_FW_FWSC = OUT_FW_DIR / "arcade_rat_fm1.fwsc"
OUT_SHA256 = OUT_FW_DIR / "SHA256SUMS.txt"
OUT_REPORT = OUT_FW_DIR / "build_report.json"

# FM1 / AC791N flash layout constants (from fm1_open/sdk/Package.cs)
AREA = 0x4000
ENTRY_POINT = 0x02000120
APP_DATA = 0x120
FLASH_LIMIT = 0xFF000
USER_SIZE = 536576
BT_SIZE = 4096
MINIMUM_VM = 32768
PUBLIC_CODE = 0x980F
CFG_TOOL_SIZE = 383
EXT_RESERVED_SIZE = 64

MAX_VM_END = FLASH_LIMIT - USER_SIZE - BT_SIZE  # 503,808
MAX_IMAGE_SIZE = MAX_VM_END - MINIMUM_VM        # 471,040
MAX_APP_BIN = MAX_IMAGE_SIZE - AREA - APP_DATA - CFG_TOOL_SIZE - EXT_RESERVED_SIZE  # 453,921

AC791N_BOOT_HEADER = bytes([
    0x00, 0x00, 0x20, 0x02, 0x2F, 0x10, 0x4C, 0xC9,
    0x00, 0xF0, 0x0F, 0x00, 0x10, 0x10, 0xA4, 0xFF,
    0x4E, 0x5D, 0x0B, 0x41, 0xE0, 0xCD, 0x78, 0x1D,
    0xC8, 0x56, 0x41, 0x7F, 0xB3, 0x67, 0xCF, 0x9F,
])

ARCADE_SOURCES = [
    "src/fm1_flash_hw.c",
    "src/fm1_pac_bridge.c",
    "src/pac_core.c",
    "src/pac_synth.c",
    "src/pac_video.c",
    "src/pac_wsg.c",
    "src/z80.c",
]


def make_crc16_table() -> list[int]:
    table = []
    for i in range(256):
        value = i << 8
        for _ in range(8):
            value = ((value << 1) ^ (0x1021 if (value & 0x8000) else 0)) & 0xFFFF
        table.append(value)
    return table


CRC_TABLE = make_crc16_table()


def crc16(data: bytes | bytearray, begin: int = 0, length: int | None = None) -> int:
    if length is None:
        length = len(data) - begin
    value = 0
    for b in data[begin : begin + length]:
        value = ((value << 8) ^ CRC_TABLE[(value >> 8) ^ b]) & 0xFFFF
    return value


def cipher_inplace(buf: bytearray, begin: int, length: int, state: int) -> None:
    for pos in range(begin, begin + length):
        buf[pos] ^= state & 0xFF
        state = ((state << 1) ^ (0x1021 if (state & 0x8000) else 0)) & 0xFFFF


def round_up(size: int, alignment: int) -> int:
    return (size + alignment - 1) & -alignment


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run_wine(exe_name: str, args: list[str], cwd: Path, capture: bool = False) -> str:
    cmd = ["wine", str(TOOLCHAIN_BIN / exe_name)] + args
    env = os.environ.copy()
    env["WINEDEBUG"] = "-all"
    res = subprocess.run(
        cmd,
        cwd=str(cwd),
        env=env,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
    )
    if res.returncode != 0:
        out = res.stdout or ""
        raise RuntimeError(f"Command failed ({res.returncode}): {' '.join(cmd)}\n{out}")
    return res.stdout or ""


def collect_app_sources() -> list[Path]:
    synth_dir = (FM1_OPEN / "app" / "synth").resolve()
    app_dir = (FM1_OPEN / "app").resolve()
    srcs: list[Path] = []
    for p in app_dir.rglob("*"):
        if not p.is_file() or p.suffix not in (".c", ".S"):
            continue
        rp = p.resolve()
        if rp == synth_dir or synth_dir in rp.parents:
            continue
        srcs.append(rp)
    srcs.sort(key=lambda p: p.relative_to(FM1_OPEN).as_posix())
    return srcs


def check_version_h() -> tuple[str, str]:
    vh = (FM1_OPEN / "app" / "version.h").read_text(encoding="utf-8")
    vm = re.search(r'^#define\s+FM1_RELEASE_VERSION\s+"(V(?:0[1-9]|[1-9][0-9]{1,2}))"', vh, re.M)
    pm = re.search(r'^#define\s+FM1_UPDATE_PRODUCT\s+"(FM-1_8[0-9]{6})"', vh, re.M)
    if not vm or not pm:
        raise RuntimeError("Missing FM1_RELEASE_VERSION or FM1_UPDATE_PRODUCT in fm1_open/app/version.h")
    return vm.group(1), pm.group(1)


def compile_all() -> tuple[list[str], str, str, str]:
    release_version, firmware_product = check_version_h()

    for d in (OBJ_DIR, GEN_DIR):
        d.mkdir(parents=True, exist_ok=True)
    for f in OBJ_DIR.iterdir():
        if f.is_file():
            f.unlink()

    base_flags = [
        "-target", "pi32v2",
        "-integrated-as",
        "-mcpu=r3",
        "-mfprev1",
        "-Wuninitialized",
        "-Wno-invalid-noreturn",
        "-fno-common",
        "-flto",
        "-fallow-pointer-null",
        "-fprefer-gnu-section",
        "-femulated-tls",
        "-Wno-shift-negative-value",
        "-Wframe-larger-than=2560",
        "-fms-extensions",
        "-fno-unwind-tables",
        "-ffunction-sections",
        "-fdata-sections",
        "-fmessage-length=0",
        "-cl-single-precision-constant",
        "-mllvm", "-pi32v2-large-program=true",
        "-D__GCC_PI32V2__",
        "-O2",
    ]
    includes = [
        "-I" + os.path.relpath(FM1_OPEN / "sdk" / "include", BUILD_DIR).replace("\\", "/"),
        "-I" + os.path.relpath(FM1_OPEN / "sdk" / "include" / "libc", BUILD_DIR).replace("\\", "/"),
        "-I" + os.path.relpath(FM1_OPEN / "app" / "synth", BUILD_DIR).replace("\\", "/"),
        "-I" + os.path.relpath(FM1_OPEN / "sdk" / "config", BUILD_DIR).replace("\\", "/"),
        "-I" + os.path.relpath(FM1_OPEN / "app", BUILD_DIR).replace("\\", "/"),
        "-I" + os.path.relpath(FM1_OPEN / "app" / "board", BUILD_DIR).replace("\\", "/"),
        "-I" + os.path.relpath(REPO_ROOT / "src", BUILD_DIR).replace("\\", "/"),
    ]
    base_flags += includes

    app_sources = collect_app_sources()
    all_units: list[tuple[str, Path, bool]] = []
    for p in app_sources:
        rel = p.relative_to(FM1_OPEN).as_posix()
        all_units.append((rel, p, False))
    for s in ARCADE_SOURCES:
        all_units.append((s, (REPO_ROOT / s).resolve(), True))

    no_lto_app = {"app/screen.c", "app/transfer.c", "app/midi_router.c"}
    oz_app = {
        "app/project.c", "app/transfer.c", "app/samples.c", "app/screen.c",
        "app/presets.c", "app/midi_router.c", "app/fm_factory.c", "app/fm_library.c",
    }

    objects: list[str] = []
    for idx, (label, path, is_arcade) in enumerate(all_units):
        safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", label)
        out_obj = f"obj/{idx}_{safe_name}.obj"
        opts = list(base_flags)
        if is_arcade or label in no_lto_app:
            opts.append("-fno-lto")
        if label == "app/board/panel.c":
            opts.extend(["-fno-lto", "-fno-pic"])
        opts.extend(["-fwrapv", "-fno-fast-math", "-ffp-contract=off"])
        if is_arcade or label in oz_app:
            opts.append("-Oz")
        if label == "app/screen.c":
            opts.append("-fno-inline-functions")
        rel_input = os.path.relpath(path, BUILD_DIR).replace("\\", "/")
        args = opts + ["-MMD", "-MF", out_obj + ".d", "-c", rel_input, "-o", out_obj]
        print(f"  Compile {label}")
        run_wine("clang.exe", args, cwd=BUILD_DIR)
        objects.append(out_obj)

    # Generate build_identity.c
    id_inputs = ["ArcadeRat", sha256_file(SDK_DIR / "manifest.json")]
    for root_name, base_dir in (("app", FM1_OPEN / "app"), ("src", REPO_ROOT / "src")):
        files = sorted([f for f in base_dir.rglob("*") if f.is_file()], key=lambda x: x.as_posix())
        for f in files:
            rel = f"{root_name}/{f.relative_to(base_dir).as_posix()}"
            id_inputs.append(f"{rel}:{sha256_file(f)}")
    build_identity = hashlib.sha256("\n".join(id_inputs).encode("utf-8")).hexdigest()
    id_bytes = ", ".join("0x" + build_identity[i : i + 2] for i in range(0, 64, 2))
    identity_c = (
        '#include "layout.h"\n'
        f'const struct fm1_firmware_layout fm1_layout = {{{USER_SIZE}U, 7U}};\n'
        f'const unsigned char fm1_build_id[32] = {{{id_bytes}}};\n'
        f'const unsigned char fm1_update_identity[27] = "{firmware_product}";\n'
    )
    (GEN_DIR / "build_identity.c").write_text(identity_c, encoding="utf-8")
    run_wine(
        "clang.exe",
        base_flags + ["-c", "generated/build_identity.c", "-o", "obj/build_identity.obj"],
        cwd=BUILD_DIR,
    )
    objects.append("obj/build_identity.obj")

    # Linker script
    ld_in = (SDK_DIR / "config" / "linker.ld.in").read_text(encoding="utf-8")
    ld_text = (
        ld_in.replace("@SBC_DECODER@", "sbc_decoder\n")
        .replace("@ACL_TX_EXTRA@", " + 1024")
        .replace("@ACL_RX_EXTRA@", " + 4096")
    )
    (GEN_DIR / "linker").write_text(ld_text, encoding="utf-8")

    # Link sdk.elf
    gold_plugin = str(TOOLCHAIN_BIN / "LLVMgold.dll")
    link_args = [
        "--plugin", gold_plugin,
        "-o", "sdk.elf",
    ] + objects + [
        "-flto",
        "--plugin-opt=-pi32v2-always-use-itblock=false",
        "--plugin-opt=-enable-ipra=true",
        "--plugin-opt=-pi32v2-merge-max-offset=4096",
        "--plugin-opt=-pi32v2-enable-simd=true",
        "--plugin-opt=mcpu=r3",
        "--plugin-opt=-global-merge-on-const",
        "--plugin-opt=-inline-threshold=5",
        "--plugin-opt=-inline-max-allocated-size=32",
        "--plugin-opt=-inline-normal-into-special-section=true",
        "--plugin-opt=-dont-used-symbol-list=malloc,free,sprintf,printf,puts,putchar",
        "--plugin-opt=-pi32v2-enable-rep-memop",
        "--plugin-opt=-emulated-tls",
        "--sort-common",
        "--plugin-opt=-pi32v2-large-program=true",
        "--plugin-opt=-pi32v2-csync-before-rti=true",
        "--start-group",
        "--whole-archive", "../../sdk/lib/libfm1_engine.a", "--no-whole-archive",
        "../../sdk/lib/libc.a", "../../sdk/lib/libcompiler_rt.a",
        "--end-group",
        "--gc-sections",
        "-Tgenerated/linker",
        "-M=sdk.map",
        "--undefined=connectivity_wl82_bluetooth_start",
        "--undefined=audio_app_bluetooth_open",
        "--undefined=bt_get_local_name",
        "--undefined=bt_get_mac_addr",
    ]
    print("  Linking sdk.elf...")
    run_wine("pi32v2-ld.exe", link_args, cwd=BUILD_DIR)
    return objects, release_version, firmware_product, build_identity


def verify_elf_and_sram() -> dict:
    elf_path = BUILD_DIR / "sdk.elf"
    map_path = BUILD_DIR / "sdk.map"
    nm_out = run_wine("llvm-nm.exe", ["-S", "sdk.elf"], cwd=BUILD_DIR, capture=True)

    symbols: dict[str, tuple[int, int, str]] = {}
    for line in nm_out.splitlines():
        parts = line.split()
        if len(parts) == 4:
            addr_s, size_s, kind, name = parts
            addr = int(addr_s, 16)
            size = int(size_s, 16)
        elif len(parts) == 3:
            addr_s, kind, name = parts
            addr = int(addr_s, 16)
            size = 0
        else:
            continue
        if name not in symbols or size > symbols[name][1]:
            symbols[name] = (addr, size, kind)

    for sym in ("_start", "_text_rodata_begin"):
        if sym not in symbols or symbols[sym][0] != ENTRY_POINT:
            raise RuntimeError(f"Invalid entry symbol {sym}: {symbols.get(sym)}")

    map_text = map_path.read_text(encoding="utf-8", errors="ignore")
    m_heap = re.search(r"0x([0-9a-fA-F]+)\s+_MALLOC_SIZE\s*=", map_text)
    if not m_heap:
        raise RuntimeError("Could not find _MALLOC_SIZE in sdk.map")
    heap_bytes = int(m_heap.group(1), 16)
    if heap_bytes < 49152:
        raise RuntimeError(f"Runtime heap _MALLOC_SIZE={heap_bytes} < 49152 bytes minimum!")

    synth_cfg = json.loads((SDK_DIR / "synth.json").read_text(encoding="utf-8"))
    sram_callbacks = [
        "fm1_r_e7d3da61dac2", "fm1_r_1993f9b103e3", "fm1_r_05431712fb7b",
        "fm1_r_ffe3f82683f6", "fm1_audio_irq", "fm1_flash_worker_prepare",
        "fm1_r_7e12ed19990d", "fm1_r_74310ca1fed9",
        "fm1_engine_render", "fm1_engine_output_level", "fm1_audio_copy",
        "fm1_output_mix", "fm1_usb_audio_read", "fm1_bluetooth_audio_read",
        "fm1_usb_audio_write", "connectivity_audio_get_speaker_volume",
        "connectivity_audio_get_mic_volume",
        "cpu_enter_sfc_critical", "cpu_exit_sfc_critical",
        "enter_spi_code", "exit_spi_code", "fm1_r_da3931a5b7a8", "sfc_drop_cache",
        "fm1_input_tick", "fm1_panel_irq", "fm1_scan_decode",
        "fm1_key_pin", "fm1_encoder_pin", "fm1_quadrature",
        "fm1_pacman_active", "fm1_pacman_audio_mix", "pac_core_audio", "wsg_render_stereo",
    ] + synth_cfg["sram_required"]

    for name in sram_callbacks:
        if name not in symbols:
            raise RuntimeError(f"Required SRAM callback absent: {name}")
        addr = symbols[name][0]
        if not (0x01C00000 <= addr < 0x01C80000):
            raise RuntimeError(f"SRAM callback outside internal RAM: {name} @ 0x{addr:08x}")

    elf_bytes = elf_path.read_bytes()
    if elf_bytes[:6] != b"\x7fELF\x01\x01":
        raise RuntimeError("Invalid ELF32 little-endian header")
    e_entry = struct.unpack_from("<I", elf_bytes, 24)[0]
    if e_entry != ENTRY_POINT:
        raise RuntimeError(f"ELF entry point 0x{e_entry:08x} != 0x{ENTRY_POINT:08x}")

    e_shoff = struct.unpack_from("<I", elf_bytes, 32)[0]
    e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<HHH", elf_bytes, 46)
    shstr_off, shstr_sz = struct.unpack_from("<II", elf_bytes, e_shoff + e_shstrndx * e_shentsize + 16)
    shstr = elf_bytes[shstr_off : shstr_off + shstr_sz]

    sections = []
    for i in range(e_shnum):
        sh_name, sh_type, sh_flags, sh_addr, sh_off, sh_size = struct.unpack_from(
            "<IIIIII", elf_bytes, e_shoff + i * e_shentsize
        )
        if not (sh_flags & 2) or sh_size == 0:
            continue
        end_z = shstr.index(b"\x00", sh_name)
        name = shstr[sh_name:end_z].decode("ascii")
        sections.append({"name": name, "addr": sh_addr, "bytes": sh_size, "nobits": sh_type == 8})

    return {
        "elf_sha256": sha256_file(elf_path),
        "runtime_heap_bytes": heap_bytes,
        "minimum_runtime_heap_bytes": 49152,
        "sections": sections,
        "arcade_sram_addrs": {
            n: f"0x{symbols[n][0]:08x}"
            for n in ("fm1_pacman_active", "fm1_pacman_audio_mix", "pac_core_audio", "wsg_render_stereo")
        },
    }


def extract_app_bin() -> tuple[bytes, dict[str, int]]:
    secs = ("text", "data", "ram0_data", "cache_ram_data")
    parts = []
    sizes: dict[str, int] = {}
    for sec in secs:
        out_bin = GEN_DIR / f"{sec}.bin"
        run_wine("llvm-objcopy.exe", ["-O", "binary", "-j", f".{sec}", "../sdk.elf", f"{sec}.bin"], cwd=GEN_DIR)
        raw = out_bin.read_bytes()
        out_bin.unlink(missing_ok=True)
        parts.append(raw)
        sizes[sec] = len(raw)
    app_bin = b"".join(parts)
    return app_bin, sizes


def write_record(
    buf: bytearray,
    offset: int,
    name: str,
    crc_val: int,
    address: int,
    size: int,
    attributes: int,
    last: int,
    extra: int | None,
) -> None:
    buf[offset : offset + 32] = b"\x00" * 32
    struct.pack_into("<HIIHH", buf, offset + 2, crc_val, address, size, attributes, last)
    for n in range(16, 32):
        buf[offset + n] = 0xFF
    name_bytes = name.encode("ascii")
    buf[offset + 16 : offset + 16 + len(name_bytes)] = name_bytes
    buf[offset + 16 + len(name_bytes)] = 0
    if extra is not None:
        struct.pack_into("<I", buf, offset + 28, extra)
    struct.pack_into("<H", buf, offset, crc16(buf, offset + 2, 30))


def encode_boot(plain: bytes) -> bytes:
    result = bytearray(plain)
    banks = struct.unpack_from("<H", plain, 0)[0]
    if banks < 1 or banks > len(plain) // 16:
        raise RuntimeError("Invalid uboot directory")
    prev_end = banks * 16
    for i in range(banks):
        hdr = i * 16
        length = struct.unpack_from("<H", plain, hdr + 2)[0]
        start = struct.unpack_from("<i", plain, hdr + 8)[0]
        expected_hdr_crc = struct.unpack_from("<H", plain, hdr + 14)[0]
        expected_blk_crc = struct.unpack_from("<H", plain, hdr + 12)[0]
        if (
            length == 0
            or start < prev_end
            or start > len(plain) - length
            or crc16(plain, hdr, 14) != expected_hdr_crc
            or crc16(plain, start, length) != expected_blk_crc
        ):
            raise RuntimeError(f"Invalid uboot bank {i}")
        cipher_inplace(result, hdr, 16, 65535)
        cipher_inplace(result, start, length, 65535)
        prev_end = start + length
    return bytes(result)


def package_fwsc(app_bin: bytes, product: str, output_path: Path) -> dict:
    if not re.match(r"^FM-1_8[0-9]{6}$", product):
        raise RuntimeError(f"Invalid FM1 product identity: {product}")
    if len(app_bin) == 0 or len(app_bin) > MAX_APP_BIN:
        raise RuntimeError(
            f"app.bin is {len(app_bin)} bytes, exceeds FM1 flash ceiling of {MAX_APP_BIN} bytes "
            f"(overflow: {len(app_bin) - MAX_APP_BIN} bytes)"
        )

    boot = (PACK_RESOURCES / "uboot.boot").read_bytes()
    config = (PACK_RESOURCES / "boot-config.bin").read_bytes()
    tool = (PACK_RESOURCES / "cfg_tool.bin").read_bytes()
    loader = (PACK_RESOURCES / "ota.bin").read_bytes()

    if len(boot) != 14488 or len(config) != 721 or len(tool) != CFG_TOOL_SIZE:
        raise RuntimeError("Unexpected FM1 pack resource size")
    if len(loader) < 1 or len(loader) >= 32768:
        raise RuntimeError("Invalid FM1 update loader ota.bin")

    image_size = round_up(AREA + APP_DATA + len(app_bin) + len(tool) + EXT_RESERVED_SIZE, 4096)
    vm_end = MAX_VM_END
    if image_size > vm_end - MINIMUM_VM:
        raise RuntimeError(f"imageSize {image_size} > vmEnd - MinimumVm ({vm_end - MINIMUM_VM})")

    settings = bytearray(34 + len(config))
    for bit in range(16):
        settings[bit] = 16
        settings[16 + bit] = 16 ^ (255 if ((PUBLIC_CODE >> bit) & 1) == 0 else 0)
    struct.pack_into("<H", settings, 32, crc16(settings, 0, 32))
    settings[34:] = config

    flash = bytearray([0xFF] * image_size)
    flash[0 : len(AC791N_BOOT_HEADER)] = AC791N_BOOT_HEADER
    struct.pack_into("<H", flash, 0, crc16(flash, 2, 30))

    config_at = 160 + len(boot)
    write_record(flash, 32, "uboot.boot", crc16(boot), 160, len(boot), 0, 0, None)
    write_record(flash, 64, "isd_config.ini", crc16(settings), config_at, len(settings), 0x8002, 0, None)
    write_record(flash, 96, "app_dir_head", 65535, AREA, 0xFFFFFFFF, 0xFF81, 0, None)
    write_record(flash, 128, "key_mac", 65535, FLASH_LIMIT, 4096, 0x0112, 65535, None)
    for p in range(0, 160, 32):
        cipher_inplace(flash, p, 32, 65535)

    flash[160 : 160 + len(boot)] = encode_boot(boot)
    flash[config_at : config_at + len(settings)] = settings

    payload_size = APP_DATA + len(app_bin) + len(tool)
    app_at = AREA + APP_DATA
    flash[app_at : app_at + len(app_bin)] = app_bin
    flash[app_at + len(app_bin) : app_at + len(app_bin) + len(tool)] = tool

    write_record(flash, AREA + 32, "app.bin", crc16(app_bin), APP_DATA, len(app_bin), 0xFF82, 0, None)
    write_record(
        flash,
        AREA + 64,
        "cfg_tool.bin",
        crc16(tool),
        APP_DATA + len(app_bin),
        len(tool),
        0xFF82,
        0,
        None,
    )
    write_record(flash, AREA + 96, "VM", 65535, image_size, vm_end - image_size, 0x8112, 0, MINIMUM_VM)
    write_record(flash, AREA + 128, "PRCT", 65535, 0, image_size, 0x8292, 0, 0x45444F43)
    write_record(flash, AREA + 160, "BTIF", 65535, vm_end, BT_SIZE, 0x8192, 1, 0x4F545541)
    write_record(
        flash,
        AREA,
        "app_area_head",
        crc16(flash, AREA + 32, payload_size - 32),
        ENTRY_POINT,
        payload_size,
        0xFF83,
        0,
        None,
    )

    reserved = AREA + payload_size
    write_record(
        flash,
        reserved + 32,
        "USER",
        65535,
        FLASH_LIMIT - USER_SIZE,
        USER_SIZE,
        0x8192,
        1,
        0x4F545541,
    )
    write_record(
        flash,
        reserved,
        "EXT_RESERVED",
        crc16(flash, reserved + 32, 32),
        32,
        64,
        0xFF93,
        1,
        None,
    )
    for p in range(0, payload_size + 64, 32):
        chunk = min(32, payload_size + 64 - p)
        cipher_inplace(flash, AREA + p, chunk, PUBLIC_CODE ^ (p >> 2))

    # Wrap flash.bin + ota.bin into AC791N encrypted .fwsc container
    loader_at = 1024 + round_up(len(flash), 32)
    total = loader_at + round_up(len(loader), 32)
    ufw = bytearray([0xFF] * total)
    ufw[:224] = b"\x00" * 224

    for idx, (data, name) in enumerate(((flash, "flash.bin"), (loader, "ota.bin"))):
        rec = 64 + idx * 80
        struct.pack_into("<HHH", ufw, rec, 0 if idx == 0 else 100, idx, crc16(data))
        struct.pack_into(
            "<III",
            ufw,
            rec + 8,
            1024 if idx == 0 else loader_at,
            len(data),
            round_up(len(data), 32),
        )
        nb = name.encode("ascii")
        ufw[rec + 64 : rec + 64 + len(nb)] = nb
        cipher_inplace(ufw, rec, 80, 65535)

    struct.pack_into("<IHHI", ufw, 4, total, 2, 4, 512)
    ufw[16:22] = b"AC791N"
    struct.pack_into("<H", ufw, 2, crc16(ufw, 64, 160))
    struct.pack_into("<H", ufw, 0, crc16(ufw, 2, 62))
    cipher_inplace(ufw, 0, 64, 65535)

    ufw[1024 : 1024 + len(flash)] = flash
    ufw[loader_at : loader_at + len(loader)] = loader

    product_bytes = product.encode("ascii")
    out = bytearray(total + 20)
    dst = 0
    for src in range(total):
        out[dst] = ufw[src]
        dst += 1
        if src < 940 and (src + 1) % 47 == 0:
            index = src // 47
            out[dst] = (product_bytes[index] + index + 1) & 0xFF if index < len(product_bytes) else 125
            dst += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(out)
    return {
        "fits": True,
        "packager": "Package.cs-equivalent",
        "product": product,
        "app_bin_bytes": len(app_bin),
        "max_app_bin_bytes": MAX_APP_BIN,
        "FLASH_BIN_SIZE": image_size,
        "MAX_IMAGE_SIZE": MAX_IMAGE_SIZE,
        "VM_START_ADDR": image_size,
        "VM_END_ADDR": vm_end,
        "VM_REAL_SIZE": vm_end - image_size,
        "vm_extra_gap_bytes": vm_end - image_size - MINIMUM_VM,
        "btif_bytes": BT_SIZE,
        "user_bytes": USER_SIZE,
        "fwsc_bytes": len(out),
    }


def validate_with_webupdate(fwsc_path: Path, expected_product: str) -> None:
    webupdate_js = (SDK_DIR / "WebUpdate.js").read_text(encoding="utf-8")
    # Run the exact WebUpdate.js inspectPackage implementation inside Node VM
    node_script = """
const fs = require('fs');
const vm = require('vm');
const webCode = fs.readFileSync(process.argv[1], 'utf8');
const fwsc = new Uint8Array(fs.readFileSync(process.argv[2]));

// Expose inspectPackage from WebUpdate.js IIFE for verification
const instrumented = webCode.replace(
  'return {product,image,loader:loader[0].data,...(factory?{factory}: {})};\\n  }',
  'return {product,image,loader:loader[0].data,...(factory?{factory}: {})};\\n  }\\n  globalThis.__inspectPackage = inspectPackage;'
);
const sandbox = {
  Uint8Array, Uint16Array, WeakMap, Promise, Error, Object, Array, String, Number, Math,
  setTimeout, clearTimeout,
  globalThis: {},
  window: {},
};
sandbox.globalThis = sandbox;
sandbox.crypto = { subtle: { digest: async () => new ArrayBuffer(32) } };
vm.runInNewContext(instrumented, sandbox);
const info = sandbox.__inspectPackage(fwsc, false);
if (info.product !== process.argv[3]) {
  throw new Error('Product mismatch: ' + info.product);
}
if (!sandbox.__openIdentity) {
  // Check regex from WebUpdate.js line 58 explicitly too
  if (!/^(FM1_OFFICIAL_OPEN|FM1_COMMUNITY_\\d+|FM-1_8\\d{6})$/.test(info.product)) {
    throw new Error('openIdentity check failed for ' + info.product);
  }
}
console.log(JSON.stringify({
  verified: true,
  product: info.product,
  flash_image_bytes: info.image.length,
  loader_bytes: info.loader.length,
  fwsc_bytes: fwsc.length,
}));
"""
    res = subprocess.run(
        ["node", "-e", node_script, str(SDK_DIR / "WebUpdate.js"), str(fwsc_path), expected_product],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if res.returncode != 0:
        raise RuntimeError(f"WebUpdate.js inspectPackage validation failed:\n{res.stdout}")
    print(f"  WebUpdate.js inspectPackage() verified: {res.stdout.strip()}")


def main() -> int:
    print("=========================================================================")
    print("  M-VAVE FM-1 ARCADE RAT FIRMWARE BUILD & .FWSC PACKAGER (PI32v2 + WINE)")
    print("=========================================================================")
    objects, release_version, firmware_product, build_identity = compile_all()
    elf_report = verify_elf_and_sram()
    app_bin, sec_sizes = extract_app_bin()
    print(
        f"  Sections: .text={sec_sizes['text']}, .data={sec_sizes['data']}, "
        f".ram0_data={sec_sizes['ram0_data']}, .cache_ram_data={sec_sizes['cache_ram_data']}"
    )
    print(
        f"  app.bin={len(app_bin)} / {MAX_APP_BIN} B "
        f"(headroom={MAX_APP_BIN - len(app_bin)} B), "
        f"_MALLOC_SIZE={elf_report['runtime_heap_bytes']} B"
    )

    OUT_FW_DIR.mkdir(parents=True, exist_ok=True)
    layout = package_fwsc(app_bin, firmware_product, OUT_FW_FWSC)
    shutil.copy2(OUT_FW_FWSC, OUT_ROOT_FWSC)

    validate_with_webupdate(OUT_ROOT_FWSC, firmware_product)

    fw_sha = sha256_file(OUT_ROOT_FWSC)
    OUT_SHA256.write_text(f"{fw_sha}  arcade_rat_fm1.fwsc\n", encoding="utf-8")

    full_report = {
        "release_version": release_version,
        "build_identity": build_identity,
        "firmware_sha256": fw_sha,
        "section_bytes": sec_sizes,
        "elf": elf_report,
        "package": layout,
    }
    OUT_REPORT.write_text(json.dumps(full_report, indent=2) + "\n", encoding="utf-8")

    print("=========================================================================")
    print(f"  SUCCESS: {OUT_ROOT_FWSC.name} ({layout['fwsc_bytes']} bytes)")
    print(f"  SHA-256: {fw_sha}")
    print(f"  Flash image: {layout['FLASH_BIN_SIZE']} B (VM free: {layout['VM_REAL_SIZE']} B)")
    print(f"  Heap _MALLOC_SIZE: {elf_report['runtime_heap_bytes']} B")
    print("=========================================================================")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        sys.exit(1)
