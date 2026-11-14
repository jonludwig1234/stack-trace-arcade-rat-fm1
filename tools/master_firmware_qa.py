#!/usr/bin/env python3
"""
Master Firmware & Arcade QA Battery
Performs 100% exhaustive QA validation across all 8 game ROMs, native C firmware,
soundchips, synthesis engines, hardware controls, mortality mechanics,
stage progressions, endurance stress (8,000 frames), and audio DSP.
"""

import os
import socket
import subprocess
import sys
import time

def run_step(step_num, total_steps, title, command):
    print(f"\n[{step_num}/{total_steps}] RUNNING: {title}...")
    start = time.time()
    res = subprocess.run(command, shell=True, capture_output=True, text=True)
    duration = time.time() - start
    if res.returncode != 0:
        print(f"❌ FAILED: {title} (exit code {res.returncode}) [{duration:.2f}s]")
        print("STDOUT:\n", res.stdout)
        print("STDERR:\n", res.stderr)
        return False
    else:
        print(f"✅ PASSED: {title} [{duration:.2f}s]")
        for line in res.stdout.strip().splitlines()[-5:]:
            print(f"   {line}")
        return True

def main():
    print("=" * 78)
    print("  STACK TRACE & M-VAVE FM-1 ARCADE FIRMWARE: COMPREHENSIVE QA MASTER BATTERY  ")
    print("=" * 78)

    steps = [
        ("Native C Firmware GCC Compilation & Unit Execution Rig", 
         "gcc -O2 tools/test_native_c_firmware.c src/fm1_flash_hw.c src/fm1_pac_bridge.c src/pac_core.c src/pac_synth.c src/pac_video.c src/pac_wsg.c src/pac_demo_songs.c src/z80.c -I src/ -lm -o tools/test_native_c_firmware && tools/test_native_c_firmware"),
        ("Master Arcade Specification & ROM Execution Suite", 
         "node tools/test_all_games_arcade_spec.js"),
        ("Multi-Frame Quality Control & Ground Invariant Playthrough", 
         "node tools/test_quality_control_all_games.js"),
        ("Full Mortality, Finite Lives & Game Over Across All 8 Games", 
         "node tools/test_all_games_mortal_and_gameover.js"),
        ("Stage Progression, Win Conditions & Level Clears Across All Games",
         "node tools/test_stage_progression_all_games.js"),
        ("Long-Running Endurance (8,000 Frames) & Zero-Leak Heap Stress",
         "node tools/test_endurance_stress.js"),
        ("Attract Tour Demo, Jukebox Demo Songs & Rewind Time Machine",
         "node tools/test_tour_jukebox_rewind.js"),
        ("Multi-Input Schemes (Keyboard, D-Pad, Knobs, Touch) & HUD Telemetry", 
         "node tools/test_all_games_input_dispatch.js && node tools/test_all_games_gameplay_audit.js"),
        ("Donkey Kong 1981: 25M Girder Math, Finite Lives & 8035 BGM Rig", 
         "node tools/test_donkey_kong_authentic.js"),
        ("Gyruss 1983: 360° Polar Angle Wrap, Plasma Bullets & Mortal Rig", 
         "node tools/test_gyruss_mortal_mechanics.js"),
        ("Iconic Arcade SFX Banks (108 Sounds Across 4 Chips) DSP Synthesis & Hardware Fidelity", 
         "node tools/test_verify_all_sfx_banks.js && node tools/test_sfx_fidelity_audit.js"),
        ("16-Step Chiptune Tracker & 5 Multi-Engine Synthesizers", 
         "node tools/test_tracker_and_synths.js"),
        ("FM-1 System Architecture, Configurator & ROM Catalog Verification", 
         "python3 tools/verify_all.py"),
        ("Arcade Hall of Fame Leaderboard & NVRAM Battery Persistence Rig",
         "node tools/test_nvram_leaderboard_persistence.js"),
        ("WebMIDI Hardware & Rotary Encoder Controller Integration Rig",
         "node tools/test_midi_hardware_controls.js"),
        ("Audio Context Lifecycle, Frequency Safety & Polyphony Stress Battery",
         "node tools/test_audio_lifecycle_and_polyphony.js"),
        ("Pac-Man Z80 Authentic Bus, Memory Bounds & Interrupt Rig",
         "node tools/test_pacman_z80_bus.js"),
        ("Headless Chrome E2E Browser DOM & Canvas Pixel Rendering Audit",
         "node tools/test_headless_e2e_browser.js"),
        ("Universal Immortal Mode & Level Skip Across All 8 Games",
         "node tools/test_immortal_and_level_skip.js"),
        ("Authentic Arcade Background Music (BGM) Engine Across All 8 Games",
         "node tools/test_all_games_bgm.js"),
        ("Frogger 1981: Authentic Death Animation & Dual AY-3-8910 SFX Fidelity Rig",
         "node tools/test_frogger_death_fidelity.js"),
        ("All 8 Arcade Titles: Death Sound Dispatch & DSP Hardware Fidelity Audit",
         "node tools/audit_arcade_death_sounds.js"),
        ("Vintage Arcade Speech ROM Synthesis & LPC-10/Votrax/CVSD Fidelity Rig",
         "node tools/test_speech_rom_fidelity.js"),
        ("Real-User Journeys, Negative Cross-Trigger Isolation & DSP Wiring Rig",
         "node tools/test_real_user_journeys_and_acoustics.js"),
        ("Dual-Hardware Flash Compatibility & Cross-Revision NVRAM Engine",
         "node tools/test_dual_hardware_flash_compat.js")
    ]

    httpd = None
    try:
        with socket.create_connection(("127.0.0.1", 8085), timeout=0.3):
            pass
    except OSError:
        httpd = subprocess.Popen(
            [sys.executable, "-m", "http.server", "8085", "--directory", "web"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(0.4)

    total = len(steps)
    all_passed = True
    try:
        for idx, (title, cmd) in enumerate(steps, 1):
            if not run_step(idx, total, title, cmd):
                all_passed = False
                break
    finally:
        if httpd is not None:
            httpd.terminate()
            try:
                httpd.wait(timeout=3)
            except subprocess.TimeoutExpired:
                httpd.kill()
        if os.path.exists("tools/test_native_c_firmware"):
            os.remove("tools/test_native_c_firmware")

    print("\n" + "=" * 78)
    if all_passed:
        print(f"🎉 ALL {total} / {total} MASTER FIRMWARE QA BATTERIES PASSED 100% GREEN! 🎉")
        print("FIRMWARE & ALL ARCADE ROM ENGINES ARE CERTIFIED PRODUCTION-READY FOR RELEASE.")
        print("=" * 78)
        sys.exit(0)
    else:
        print("❌ FIRMWARE QA BATTERY FAILED! DO NOT SHIP UNTIL RESOLVED.")
        print("=" * 78)
        sys.exit(1)

if __name__ == "__main__":
    main()
