#!/usr/bin/env python3
"""
M-VAVE FM-1 Arcade Firmware Showcase Video Generator
Composes a high-definition (1920x1080 @ 30fps) demo video combining:
- Authentic live gameplay and soundboard screenshots for all 8 games, 4 SFX banks, speech ROMs, and tracker
- Real-time animated audio visualizer driven by the master recorded soundtrack
- Professional cyber-retro HUD overlays, chapter headers, hardware telemetry, and feature specs
- Fully synchronized 44.1kHz stereo audio track
"""

import os
import sys
import json
import math
import wave
import struct
import subprocess
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DIR = os.path.join(PROJECT_ROOT, "web")
TIMELINE_FILE = os.path.join(WEB_DIR, "demo_timeline.json")
AUDIO_FILE = os.path.join(WEB_DIR, "demo_soundtrack.wav")
OUTPUT_VIDEO = os.path.join(WEB_DIR, "fm1_firmware_showcase_demo.mp4")
FFMPEG_BIN = "/home/jon/.local/bin/ffmpeg"

WIDTH = 1920
HEIGHT = 1080
FPS = 30

FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_MONO = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"

SCENE_ASSETS = {
    "scene_01_intro": "snap_simplified_firmware_ui.png",
    "scene_02_pacman": "snap_pacman_authentic.png",
    "scene_03_galaga": "snap_galaga_authentic.png",
    "scene_04_dkong": "snap_dkong_authentic.png",
    "scene_05_frogger": "snap_frogger_authentic.png",
    "scene_06_asteroids": "snap_asteroids_authentic.png",
    "scene_07_tempest": "snap_tempest_authentic.png",
    "scene_08_cclimber": "snap_cclimber_authentic.png",
    "scene_09_gyruss": "snap_gyruss_authentic.png",
    "scene_10_bank1": "snap_sfx_bank1.png",
    "scene_11_bank2": "snap_sfx_bank2.png",
    "scene_12_bank3": "snap_sfx_bank3.png",
    "scene_13_bank4": "snap_sfx_bank4.png",
    "scene_14_speech_berzerk": "snap_speech_rom_shelf_authentic.png",
    "scene_15_speech_sinistar": "snap_speech_soundboard.png",
    "scene_16_speech_classics": "snap_speech_soundboard.png",
    "scene_17_drum_tracker": "snap_tracker_8patterns.png",
    "scene_18_leaderboard": "snap_hall_of_fame.png",
    "scene_19_jukebox": "snap_album_splash_art.png",
    "scene_20_outro": "snap_simplified_firmware_ui.png",
}

SCENE_CHAPTERS = {
    "scene_01_intro": "OVERVIEW · HARDWARE EMULATION PLATFORM",
    "scene_02_pacman": "CHAPTER 1: ARCADE EMULATION CORE (GAME 1/8)",
    "scene_03_galaga": "CHAPTER 1: ARCADE EMULATION CORE (GAME 2/8)",
    "scene_04_dkong": "CHAPTER 1: ARCADE EMULATION CORE (GAME 3/8)",
    "scene_05_frogger": "CHAPTER 1: ARCADE EMULATION CORE (GAME 4/8)",
    "scene_06_asteroids": "CHAPTER 1: ARCADE EMULATION CORE (GAME 5/8)",
    "scene_07_tempest": "CHAPTER 1: ARCADE EMULATION CORE (GAME 6/8)",
    "scene_08_cclimber": "CHAPTER 1: ARCADE EMULATION CORE (GAME 7/8)",
    "scene_09_gyruss": "CHAPTER 1: ARCADE EMULATION CORE (GAME 8/8)",
    "scene_10_bank1": "CHAPTER 2: 108 SFX SOUNDBOARD (BANK 1/4)",
    "scene_11_bank2": "CHAPTER 2: 108 SFX SOUNDBOARD (BANK 2/4)",
    "scene_12_bank3": "CHAPTER 2: 108 SFX SOUNDBOARD (BANK 3/4)",
    "scene_13_bank4": "CHAPTER 2: 108 SFX SOUNDBOARD (BANK 4/4)",
    "scene_14_speech_berzerk": "CHAPTER 3: VINTAGE SPEECH ROMS (TSI S14001A)",
    "scene_15_speech_sinistar": "CHAPTER 3: VINTAGE SPEECH ROMS (VOTRAX & CVSD)",
    "scene_16_speech_classics": "CHAPTER 3: VINTAGE SPEECH ROMS (8-VOICE SUITE)",
    "scene_17_drum_tracker": "CHAPTER 4: FM-1 DRUM SYNTH & 16-STEP TRACKER",
    "scene_18_leaderboard": "CHAPTER 5: NVRAM LEADERBOARDS & IMMORTAL MODE",
    "scene_19_jukebox": "CHAPTER 5: LIVE JUKEBOX & CIRCUIT-BENDING REWIND",
    "scene_20_outro": "CERTIFICATION & SPECIFICATION SUMMARY",
}

def load_audio_amplitudes(wav_path, target_fps=30):
    """Calculates RMS audio energy per video frame for the visualizer."""
    with wave.open(wav_path, "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw_data = wf.readframes(n_frames)

    fmt = f"<{n_frames * n_channels}h"
    samples = struct.unpack(fmt, raw_data)
    
    samples_per_video_frame = int(framerate / target_fps)
    total_video_frames = int(n_frames / samples_per_video_frame)
    
    rms_per_frame = []
    for f in range(total_video_frames):
        start = f * samples_per_video_frame * n_channels
        end = start + samples_per_video_frame * n_channels
        chunk = samples[start:end]
        if not chunk:
            rms_per_frame.append(0.0)
            continue
        sum_sq = sum(s * s for s in chunk)
        rms = math.sqrt(sum_sq / len(chunk)) / 32768.0
        rms_per_frame.append(min(1.0, rms * 3.5))  # Boost for visual pop
        
    return rms_per_frame, total_video_frames, n_frames / framerate

def create_base_frame(sim_img, chapter_text, title_text, desc_text, frame_idx, total_frames, rms_val):
    """Renders a single 1080p frame with sleek retro-futuristic HUD."""
    im = Image.new("RGB", (WIDTH, HEIGHT), (12, 15, 22))
    draw = ImageDraw.Draw(im)

    # 1. Subtle background cyber-grid
    grid_color = (20, 26, 38)
    for x in range(0, WIDTH, 80):
        draw.line([(x, 0), (x, HEIGHT)], fill=grid_color, width=1)
    for y in range(0, HEIGHT, 80):
        draw.line([(0, y), (WIDTH, y)], fill=grid_color, width=1)

    # 2. Main Simulator Display Area
    # Scale simulator image to fit nicely within (1340, 840)
    target_w = 1260
    target_h = int(sim_img.height * (target_w / sim_img.width))
    if target_h > 820:
        target_h = 820
        target_w = int(sim_img.width * (target_h / sim_img.height))

    scaled_sim = sim_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    sim_x = (WIDTH - target_w) // 2
    sim_y = 100

    # Glow shadow behind simulator
    draw.rectangle([sim_x - 6, sim_y - 6, sim_x + target_w + 5, sim_y + target_h + 5], fill=(0, 229, 255, 30), outline=(0, 229, 255), width=2)
    im.paste(scaled_sim, (sim_x, sim_y))

    # 3. Top Header Bar
    draw.rectangle([0, 0, WIDTH, 80], fill=(8, 10, 16))
    draw.line([(0, 80), (WIDTH, 80)], fill=(0, 229, 255), width=2)

    font_brand = ImageFont.truetype(FONT_BOLD, 26)
    font_chap = ImageFont.truetype(FONT_MONO, 22)
    font_badge = ImageFont.truetype(FONT_BOLD, 18)

    # Brand Title
    draw.text((40, 24), "M-VAVE FM-1 ARCADE FIRMWARE", font=font_brand, fill=(255, 255, 255))
    
    # Pulsing Live LED
    pulse = 0.5 + 0.5 * math.sin(frame_idx * 0.2)
    led_color = (int(255 * pulse), 40, 40)
    draw.ellipse([460, 31, 478, 49], fill=led_color)
    draw.text((490, 28), "AUTHENTIC AUDIO & HARDWARE SIMULATOR", font=font_badge, fill=(180, 195, 215))

    # Chapter Badge
    chap_bbox = font_chap.getbbox(chapter_text)
    chap_w = chap_bbox[2] - chap_bbox[0]
    draw.rectangle([WIDTH - chap_w - 60, 20, WIDTH - 30, 62], fill=(24, 32, 48), outline=(255, 184, 0), width=1)
    draw.text((WIDTH - chap_w - 45, 28), chapter_text, font=font_chap, fill=(255, 184, 0))

    # 4. Bottom HUD Card
    hud_y = HEIGHT - 140
    draw.rectangle([0, hud_y, WIDTH, HEIGHT], fill=(8, 10, 16))
    draw.line([(0, hud_y), (WIDTH, hud_y)], fill=(0, 229, 255), width=2)

    font_title = ImageFont.truetype(FONT_BOLD, 30)
    font_desc = ImageFont.truetype(FONT_REGULAR, 20)

    # Feature Title
    draw.text((40, hud_y + 18), title_text, font=font_title, fill=(0, 229, 255))
    # Subtitle / Specs
    draw.text((40, hud_y + 60), desc_text, font=font_desc, fill=(210, 225, 240))

    # 5. Dynamic 32-Bar Audio Visualizer (Driven by audio amplitude)
    vis_x_start = WIDTH - 420
    vis_y_bottom = hud_y + 90
    bar_width = 8
    bar_gap = 4
    num_bars = 28

    for b in range(num_bars):
        # Generate organic frequency wave shape scaled by RMS energy
        freq_weight = math.sin((b / num_bars) * math.pi)
        jitter = 0.7 + 0.3 * math.sin(frame_idx * 0.4 + b * 0.6)
        bar_h = max(4, int(rms_val * 70 * freq_weight * jitter))
        
        # Color gradient: Cyan -> Gold -> Hot Coral
        if b < 14:
            bar_color = (0, 229, 255)
        elif b < 22:
            bar_color = (255, 184, 0)
        else:
            bar_color = (255, 60, 80)
            
        bx = vis_x_start + b * (bar_width + bar_gap)
        draw.rectangle([bx, vis_y_bottom - bar_h, bx + bar_width, vis_y_bottom], fill=bar_color)

    font_vis_lbl = ImageFont.truetype(FONT_MONO, 14)
    draw.text((vis_x_start, hud_y + 100), "MASTER DSP AUDIO SPECTRUM", font=font_vis_lbl, fill=(120, 140, 170))

    # 6. Overall Timeline Progress Bar at bottom edge
    progress = frame_idx / max(1, total_frames - 1)
    draw.rectangle([0, HEIGHT - 6, WIDTH, HEIGHT], fill=(20, 25, 35))
    draw.rectangle([0, HEIGHT - 6, int(WIDTH * progress), HEIGHT], fill=(0, 229, 255))

    return im

def main():
    print("=" * 70)
    print("  M-VAVE FM-1 ARCADE FIRMWARE: MASTER DEMO VIDEO COMPOSITOR")
    print("=" * 70)

    if not os.path.exists(TIMELINE_FILE) or not os.path.exists(AUDIO_FILE):
        print(f"Error: Missing timeline {TIMELINE_FILE} or audio {AUDIO_FILE}")
        sys.exit(1)

    with open(TIMELINE_FILE, "r") as f:
        timeline_data = json.load(f)

    cue_points = timeline_data.get("cuePoints", [])
    if not cue_points:
        print("Error: No cue points found in timeline!")
        sys.exit(1)

    print(f"Loaded {len(cue_points)} cue points from timeline.")
    
    rms_amplitudes, total_frames, audio_duration = load_audio_amplitudes(AUDIO_FILE, FPS)
    print(f"Audio duration: {audio_duration:.2f}s -> {total_frames} video frames at {FPS} FPS.")

    # Pre-load and cache screenshot images
    cached_images = {}
    for scene_id, filename in SCENE_ASSETS.items():
        # Look in workspace root, brain artifacts dir, or tools
        possible_paths = [
            os.path.join(PROJECT_ROOT, filename),
            os.path.join("/home/jon/.gemini/antigravity/brain/76628535-31d8-4f4a-baa3-a47a7f1798ab", filename),
            os.path.join(PROJECT_ROOT, "tools", filename)
        ]
        img_path = None
        for p in possible_paths:
            if os.path.exists(p):
                img_path = p
                break
        
        if img_path:
            cached_images[scene_id] = Image.open(img_path).convert("RGB")
        else:
            # Fallback to snap_simplified_firmware_ui.png
            fallback = os.path.join(PROJECT_ROOT, "snap_simplified_firmware_ui.png")
            if os.path.exists(fallback):
                cached_images[scene_id] = Image.open(fallback).convert("RGB")
            else:
                cached_images[scene_id] = Image.new("RGB", (1200, 920), (20, 24, 36))

    print(f"Pre-loaded {len(cached_images)} scene showcase assets.")

    # Launch ffmpeg process streaming raw RGB24 frames from stdin
    ffmpeg_cmd = [
        FFMPEG_BIN,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",                     # Standard input for video frames
        "-i", AUDIO_FILE,              # Master synchronized audio
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        OUTPUT_VIDEO
    ]

    print(f"Starting ffmpeg video encoder: {OUTPUT_VIDEO}...")
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    # Render each frame in sequence
    for f_idx in range(total_frames):
        current_time = f_idx / FPS
        
        # Determine active cue point
        active_cue = cue_points[0]
        for c in cue_points:
            if current_time >= c["time"]:
                active_cue = c
            else:
                break

        scene_id = active_cue.get("sceneId", "scene_01_intro")
        sim_img = cached_images.get(scene_id, cached_images["scene_01_intro"])
        chapter = SCENE_CHAPTERS.get(scene_id, "M-VAVE FM-1 ARCADE FIRMWARE")
        title = active_cue.get("name", "M-VAVE FM-1 Arcade Firmware")
        desc = active_cue.get("desc", "Authentic Arcade Audio & Hardware Emulation")
        rms = rms_amplitudes[f_idx] if f_idx < len(rms_amplitudes) else 0.0

        frame_img = create_base_frame(sim_img, chapter, title, desc, f_idx, total_frames, rms)
        proc.stdin.write(frame_img.tobytes())

        if f_idx % 90 == 0 or f_idx == total_frames - 1:
            pct = (f_idx + 1) / total_frames * 100
            sys.stdout.write(f"\rRendering video frames: {pct:.1f}% ({f_idx + 1}/{total_frames} frames) [{current_time:.1f}s / {audio_duration:.1f}s]")
            sys.stdout.flush()

    proc.stdin.close()
    print("\nFinalizing video stream and encoding audio track...")
    stderr_out = proc.stderr.read().decode("utf-8", errors="ignore")
    proc.wait()

    if proc.returncode != 0:
        print("FFmpeg error:", stderr_out)
        sys.exit(1)

    vid_size = os.path.getsize(OUTPUT_VIDEO)
    print("=" * 70)
    print(f"🎉 MASTER DEMO VIDEO CREATED SUCCESSFULLY! 🎉")
    print(f"File: {OUTPUT_VIDEO}")
    print(f"Size: {vid_size / 1024 / 1024:.2f} MB")
    print(f"Resolution: {WIDTH}x{HEIGHT} @ {FPS} FPS")
    print(f"Duration: {audio_duration:.2f}s")
    print("=" * 70)

if __name__ == "__main__":
    main()
