import re
import sys
import os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("tools"))
try:
    import tools.sfx_banks_generator as sfx_gen
    import tools.speech_sample_engine as speech_gen
    import tools.leaderboard_engine as lb_gen
    import tools.expanded_tracker_engine as tracker_gen
except ModuleNotFoundError:
    import sfx_banks_generator as sfx_gen
    import speech_sample_engine as speech_gen
    import leaderboard_engine as lb_gen
    import expanded_tracker_engine as tracker_gen

def main():
    with open("tools/simulator_template.html.bak", "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    script_idx = content.find("<script>")
    if script_idx == -1:
        raise ValueError("Cannot find <script> tag in template!")

    script_body = content[script_idx:]

    # Header and body layout
    new_html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>STACK TRACE presents Arcade Rat v1.0 · M-VAVE FM-1 Synthesizer / Workbench</title>
<style>
  :root {
    color-scheme: dark;
    --accent: #aae4c8;
    --accent-glow: rgba(170, 228, 200, 0.45);
    --amber-core: #f5a623;
    --amber-glow: rgba(245, 166, 35, 0.45);
    --green-neon: #00ff66;
    --green-glow: rgba(0, 255, 102, 0.4);
    --cyan-oled: #00e5ff;
    --cyan-glow: rgba(0, 229, 255, 0.35);
    --red-alert: #ff4757;
    --purple-synth: #a55eea;
    --muted: #859293;
    --bg-page: #101416;
    --font-ui: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
    --font-mono: Consolas, "Liberation Mono", Menlo, Courier, monospace;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
  body {
    background: radial-gradient(ellipse at 50% 20%, #202629 0%, var(--bg-page) 100%);
    color: #e2e7e9;
    font-family: var(--font-ui);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    min-height: 100vh;
    padding: 18px 14px 40px 14px;
  }

  /* Streamlined Studio Header */
  .title-bar {
    width: 100%;
    max-width: 960px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    padding: 0 4px;
    flex-wrap: wrap;
    gap: 8px;
  }
  .branding-wrap { display: flex; align-items: center; gap: 10px; }
  .header-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    object-fit: contain;
    background: transparent;
    display: block;
    flex-shrink: 0;
    transition: transform 0.2s ease;
  }
  .header-avatar:hover { transform: scale(1.08); }

  .brand-sub { font-size: 0.58rem; font-weight: 800; color: var(--accent); letter-spacing: 1.5px; text-transform: uppercase; font-family: var(--font-mono); }
  h1 {
    font-size: 1.15rem;
    font-weight: 900;
    color: #edf5f0;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin: 1px 0;
    display: flex;
    align-items: center;
    gap: 7px;
  }
  .version-tag {
    font-size: 0.58rem;
    color: #172e24;
    background: var(--accent);
    padding: 1px 5px;
    border-radius: 3px;
    font-weight: 800;
    letter-spacing: 0.8px;
    box-shadow: 0 0 6px var(--accent-glow);
  }
  .subtitle { font-size: 0.62rem; color: #8fa59b; font-family: var(--font-mono); }

  .header-actions { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
  .splash-trigger-btn {
    background: #182823;
    border: 1px solid #37574b;
    color: #c6eddb;
    padding: 4px 9px;
    font-size: 0.62rem;
    font-weight: 800;
    border-radius: 5px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 5px;
    transition: all 0.15s ease;
  }
  .splash-trigger-btn:hover { background: var(--accent); color: #172e24; border-color: var(--accent); box-shadow: 0 0 10px var(--accent-glow); }

  .config-btn {
    background: #1c2326;
    border: 1px solid #364448;
    color: #e2ece6;
    padding: 4px 10px;
    border-radius: 5px;
    font-size: 0.62rem;
    font-weight: 800;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 5px;
    transition: all 0.15s ease;
  }
  .config-btn:hover { background: #2f3c40; border-color: #556c73; color: #fff; }

  /* =========================================================================
     TWO-TIER CREATIVE WORKSPACE: STUDIO TABS & CONTEXT SHELVES
     Provides direct 1-click access to Arcade Vault, Synth Studio, Tracker, etc.
     ========================================================================= */
  .studio-nav-bar {
    width: 100%;
    max-width: 960px;
    display: flex;
    gap: 4px;
    background: #111619;
    padding: 3px;
    border-radius: 8px;
    border: 1px solid #233034;
    margin-bottom: 6px;
    overflow-x: auto;
  }
  .studio-tab {
    flex: 1;
    min-width: 100px;
    background: transparent;
    border: 1px solid transparent;
    color: #8fa59f;
    padding: 5px 8px;
    border-radius: 5px;
    font-size: 0.64rem;
    font-weight: 800;
    cursor: pointer;
    transition: all 0.12s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
    white-space: nowrap;
    letter-spacing: 0.2px;
  }
  .studio-tab:hover {
    color: #fff;
    background: rgba(255, 255, 255, 0.04);
    border-color: #314347;
  }
  .studio-tab.active {
    background: #192d26;
    color: var(--accent);
    border: 1px solid #375b4f;
    box-shadow: 0 0 8px rgba(170, 228, 200, 0.2);
  }

  /* Context Shelves */
  .shelf-wrap {
    width: 100%;
    max-width: 960px;
    margin-bottom: 6px;
  }
  .context-shelf {
    display: none;
    background: #12181b;
    border-radius: 8px;
    border: 1px solid #243236;
    padding: 8px 12px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.4);
    flex-direction: column;
    gap: 6px;
  }
  .context-shelf.active {
    display: flex;
  }
  .shelf-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.70rem;
    font-weight: 800;
    color: var(--accent);
    letter-spacing: 0.5px;
    border-bottom: 1px solid #233135;
    padding-bottom: 6px;
  }
  .shelf-header span.tag {
    font-size: 0.60rem;
    color: #8fa5a0;
    font-weight: 600;
    font-family: var(--font-mono);
  }

  /* Arcade Vault Shelf (8 Playable Games Gallery) */
  .arcade-gallery-grid {
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    gap: 6px;
    width: 100%;
  }
  @media (max-width: 900px) {
    .arcade-gallery-grid { grid-template-columns: repeat(4, 1fr); }
  }
  @media (max-width: 540px) {
    .arcade-gallery-grid { grid-template-columns: repeat(2, 1fr); }
  }
  .arcade-card {
    background: #192327;
    border: 1px solid #33454a;
    border-radius: 8px;
    padding: 7px 5px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    cursor: pointer;
    transition: all 0.15s ease;
    gap: 2px;
  }
  .arcade-card:hover {
    border-color: var(--accent);
    transform: translateY(-2px);
    background: #212f34;
  }
  .arcade-card.active {
    background: linear-gradient(135deg, #1b382d 0%, #162a24 100%);
    border-color: var(--accent);
    box-shadow: 0 0 12px var(--accent-glow);
  }
  .arcade-card .card-emoji { font-size: 1.15rem; line-height: 1.2; }
  .arcade-card .card-name { font-size: 0.66rem; font-weight: 900; color: #e2ece8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }
  .arcade-card .card-meta { font-size: 0.53rem; color: #7f9994; font-family: var(--font-mono); }
  .arcade-card .card-badge {
    font-size: 0.48rem;
    padding: 1px 4px;
    border-radius: 3px;
    background: #253639;
    color: #a4bab5;
    font-weight: 800;
    text-transform: uppercase;
    margin-top: 2px;
  }
  .arcade-card.active .card-badge {
    background: var(--accent);
    color: #172e24;
  }

  /* Vintage Speech ROM Shelf (8 Emulated Speech Chips) */
  .speech-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    width: 100%;
  }
  @media (max-width: 800px) {
    .speech-grid { grid-template-columns: repeat(2, 1fr); }
  }
  @media (max-width: 480px) {
    .speech-grid { grid-template-columns: 1fr; }
  }
  .speech-card {
    background: #141f23;
    border: 1px solid #283e44;
    border-radius: 8px;
    padding: 10px 10px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    cursor: pointer;
    transition: all 0.15s ease;
    position: relative;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
  }
  .speech-card:hover {
    border-color: #00e5ff;
    transform: translateY(-2px);
    background: #192a30;
    box-shadow: 0 0 10px rgba(0,229,255,0.25);
  }
  .speech-card-active {
    border-color: #00ff66 !important;
    background: #123528 !important;
    box-shadow: 0 0 16px rgba(0,255,102,0.5) !important;
    transform: scale(1.02);
  }
  .speech-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 6px;
  }
  .speech-card-title {
    font-size: 0.76rem;
    font-weight: 900;
    color: #e6f6f9;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .speech-chip-badge {
    font-size: 0.52rem;
    padding: 2px 5px;
    border-radius: 3px;
    background: #1b3842;
    color: #00e5ff;
    font-family: var(--font-mono);
    font-weight: 800;
  }
  .speech-quote {
    font-size: 0.64rem;
    color: #f5cd79;
    font-family: var(--font-mono);
    background: rgba(0,0,0,0.3);
    padding: 4px 6px;
    border-radius: 4px;
    border-left: 2px solid #00e5ff;
  }
  .speech-game-meta {
    font-size: 0.55rem;
    color: #8fa59f;
    font-family: var(--font-mono);
    display: flex;
    justify-content: space-between;
  }
  .speech-play-btn {
    width: 100%;
    background: linear-gradient(135deg, #133337 0%, #0d2326 100%);
    border: 1px solid #00e5ff;
    color: #00e5ff;
    border-radius: 5px;
    padding: 6px;
    font-size: 0.65rem;
    font-weight: 800;
    cursor: pointer;
    transition: all 0.1s ease;
    text-align: center;
    letter-spacing: 0.5px;
  }
  .speech-play-btn:hover {
    background: #00e5ff;
    color: #0e1e24;
    box-shadow: 0 0 8px rgba(0,229,255,0.4);
  }

  /* Synth Studio Shelf (5 Soundchips + Envelopes + Modulators) */
  .synth-section {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .synth-row {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }
  .synth-label {
    font-size: 0.62rem;
    font-weight: 800;
    color: #92a8a4;
    letter-spacing: 0.6px;
    min-width: 110px;
    font-family: var(--font-mono);
  }
  .synth-btn-group {
    display: flex;
    gap: 5px;
    flex-wrap: wrap;
  }
  .synth-chip-btn {
    background: #1c262a;
    border: 1px solid #36494e;
    color: #adc4be;
    padding: 5px 10px;
    border-radius: 6px;
    font-size: 0.65rem;
    font-weight: 800;
    cursor: pointer;
    transition: all 0.12s ease;
    display: flex;
    align-items: center;
    gap: 5px;
  }
  .synth-chip-btn:hover {
    color: #fff;
    border-color: #00e5ff;
    background: #23343a;
  }
  .synth-chip-btn.active {
    background: #173836;
    color: #00e5ff;
    border-color: #00e5ff;
    box-shadow: 0 0 10px rgba(0, 229, 255, 0.4);
    font-weight: 900;
  }
  .synth-opt-btn {
    background: #1c262a;
    border: 1px solid #36494e;
    color: #9eb5af;
    padding: 4px 9px;
    border-radius: 5px;
    font-size: 0.62rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.1s ease;
  }
  .synth-opt-btn:hover { color: #fff; border-color: var(--accent); }
  .synth-opt-btn.active {
    background: var(--accent);
    color: #172e24;
    font-weight: 800;
    box-shadow: 0 0 8px var(--accent-glow);
  }
  .synth-hint-bar {
    font-size: 0.62rem;
    color: #8da49f;
    background: #172124;
    border-radius: 6px;
    padding: 6px 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-left: 3px solid #00e5ff;
  }

  /* Quick Navigation / Modes Strip */
  .nav-strip {
    width: 100%;
    max-width: 960px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    flex-wrap: wrap;
    gap: 8px;
  }
  .game-toggle-group {
    display: flex;
    gap: 5px;
    background: #161c1e;
    padding: 3px 5px;
    border-radius: 8px;
    border: 1px solid #2e393b;
  }
  .game-btn {
    background: transparent;
    border: none;
    color: #8b9ea0;
    padding: 5px 12px;
    border-radius: 6px;
    font-size: 0.68rem;
    font-weight: 800;
    cursor: pointer;
    transition: all 0.12s ease;
    display: flex;
    align-items: center;
    gap: 5px;
  }
  .game-btn:hover { color: #fff; background: rgba(255,255,255,0.06); }
  .game-btn.active {
    background: var(--accent);
    color: #172e24;
    font-weight: 900;
    box-shadow: 0 0 10px var(--accent-glow);
  }
  .game-btn.tour-btn.active {
    background: #a55eea;
    color: #fff;
    box-shadow: 0 0 10px rgba(165, 94, 234, 0.6);
  }

  .mode-indicator {
    display: flex;
    gap: 3px;
    background: #161c1e;
    padding: 3px 5px;
    border-radius: 8px;
    border: 1px solid #2e393b;
    overflow-x: auto;
  }
  .mode-tag {
    font-size: 0.60rem;
    font-weight: 800;
    padding: 4px 8px;
    border-radius: 5px;
    color: #7d9193;
    cursor: pointer;
    transition: all 0.12s ease;
    letter-spacing: 0.3px;
    font-family: var(--font-mono);
  }
  .mode-tag:hover { color: #fff; background: rgba(255,255,255,0.06); }
  .mode-tag.active {
    background: #253632;
    color: var(--accent);
    border: 1px solid #3e5a52;
  }

  /* =========================================================================
     M-VAVE FM-1 AUTHENTIC HARDWARE CHASSIS
     Geometry, Gradients, Knobs, Buttons, Screws, and Silicone Keyboard
     Derived directly from fm1_open official hardware firmware specifications.
     ========================================================================= */
  .device-scroll {
    width: 100%;
    max-width: 960px;
    display: flex;
    justify-content: center;
    overflow-x: auto;
    padding: 4px 0 14px 0;
  }

  .sim-device {
    container-type: inline-size;
    position: relative;
    width: 100%;
    min-width: 720px;
    aspect-ratio: 1000 / 624;
    border: 1px solid #58646a;
    border-radius: 2.3%;
    background: linear-gradient(125deg, #3e474b 0%, #2b3439 44%, #232d32 100%);
    box-shadow:
      inset 0 1px 1px #bacac466,
      inset 0 -4px 0 #182125,
      0 4px 0 #080e12,
      0 12px 24px #0007,
      0 30px 60px #0005;
    user-select: none;
    -webkit-user-select: none;
  }
  .sim-device:after {
    pointer-events: none;
    content: "";
    position: absolute;
    inset: 0;
    border-radius: inherit;
    background: linear-gradient(100deg, #ffffff05, transparent 55%);
  }

  /* Authentic Hex Corner Screws */
  .screw {
    position: absolute;
    width: 0.85%;
    height: 1.36%;
    border-radius: 50%;
    background: linear-gradient(45deg, #171b1a 45%, #747d7855 48%, #1a1e1c 55%);
    box-shadow: 0 1px 1px #69746a50;
  }
  .screw.tl { left: 2%; top: 3%; }
  .screw.tr { right: 2%; top: 3%; }
  .screw.bl { left: 2%; bottom: 3%; }
  .screw.br { right: 2%; bottom: 3%; }

  /* Silkscreen Branding */
  .device-brand {
    position: absolute;
    left: 5.2%;
    top: 3%;
    font: 700 1.25cqw/1 Consolas, "Liberation Mono", monospace;
    letter-spacing: .15em;
    color: #d0dcd9;
    display: flex;
    align-items: baseline;
    gap: 0.8cqw;
  }
  .device-brand span {
    font-size: .75cqw;
    font-weight: 400;
    color: #8da39c;
    letter-spacing: .08em;
  }
  .case-mark {
    position: absolute;
    right: 4.8%;
    top: 3%;
    font: 700 .75cqw Consolas, "Liberation Mono", monospace;
    letter-spacing: .18em;
    color: #92a29f;
  }

  /* Hardware Status LEDs */
  .led-array {
    position: absolute;
    left: 5.2%;
    top: 6.2%;
    display: flex;
    align-items: center;
    gap: 1.2cqw;
    font: 700 0.62cqw/1 Consolas, monospace;
    color: #7b8e88;
    letter-spacing: 0.05em;
  }
  .led-item { display: flex; align-items: center; gap: 0.4cqw; }
  .led-dot {
    width: 0.55cqw;
    height: 0.55cqw;
    border-radius: 50%;
    background: #182220;
    box-shadow: inset 0 1px 1px rgba(0,0,0,0.8);
    transition: all 0.15s ease;
  }
  .led-dot.pwr { background: var(--accent); box-shadow: 0 0 6px var(--accent-glow); }
  .led-dot.sync { background: #00ff66; box-shadow: 0 0 6px rgba(0,255,102,0.6); animation: blinkPulse 1.2s infinite ease-in-out; }
  .led-dot.midi { background: #182220; }
  .led-dot.midi.active { background: #00e5ff; box-shadow: 0 0 8px rgba(0,229,255,0.7); }

  @keyframes blinkPulse {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 1; }
  }

  /* Center Screen Bezel (240x240 Display) */
  .screen-bezel {
    position: absolute;
    left: 29.2%;
    top: 7.05%;
    width: 25.6%;
    height: 41.03%;
    padding: 0.8%;
    border: 1px solid #111615;
    background: #101513;
    border-radius: 2%;
    box-shadow: 0 1px 1px #73807760, inset 0 2px 5px #0008;
    overflow: hidden;
    cursor: crosshair;
  }
  .lcd-surface {
    position: relative;
    width: 100%;
    height: 100%;
  }
  #tftCanvas {
    display: block;
    width: 100%;
    height: 100%;
    image-rendering: auto; image-rendering: -webkit-optimize-contrast;
    background: #000;
    border: 1px solid #0d1110;
  }

  /* Quadrant Steer Chevrons (Hover Hints) */
  .screen-quadrant-hints {
    position: absolute;
    inset: 6px;
    pointer-events: none;
    z-index: 6;
  }
  .quadrant-hint {
    position: absolute;
    font-size: 0.8cqw;
    color: var(--accent);
    opacity: 0;
    transition: opacity 0.2s ease;
    font-weight: 900;
    text-shadow: 0 0 6px var(--accent-glow);
  }
  .screen-bezel:hover .quadrant-hint { opacity: 0.5; }
  .hint-up { top: 2px; left: 50%; transform: translateX(-50%); }
  .hint-down { bottom: 2px; left: 50%; transform: translateX(-50%); }
  .hint-left { left: 2px; top: 50%; transform: translateY(-50%); }
  .hint-right { right: 2px; top: 50%; transform: translateY(-50%); }

  /* Below Screen Silkscreen Caption */
  .screen-caption {
    position: absolute;
    top: 48.9%;
    left: 29.2%;
    width: 25.6%;
    display: flex;
    justify-content: space-between;
    font: 700 .65cqw Consolas, "Liberation Mono", monospace;
    letter-spacing: .12em;
    color: #92a29f;
  }
  .screen-caption span { cursor: default; }

  /* Precision Encoders */
  .encoder {
    position: absolute;
    width: 8%;
    height: 12.82%;
    transform: translate(-50%, -50%);
    text-align: center;
    z-index: 2;
  }
  .encoder > span {
    position: absolute;
    bottom: calc(100% + 0.5cqw);
    left: -25%;
    right: -25%;
    font: 700 0.82cqw/1.2 Consolas, "Liberation Mono", monospace;
    color: #c3d2d3;
    letter-spacing: .04em;
    text-transform: uppercase;
  }
  .encoder > span small {
    display: block;
    font-size: 0.70cqw;
    color: #aae4c8;
    font-weight: 600;
  }
  .encoder .dial {
    display: block;
    position: relative;
    width: 60%;
    height: 60%;
    margin: 0 auto;
    padding: 0;
    border: 2px solid #172325;
    border-radius: 50%;
    background: radial-gradient(circle at 37% 25%, #75827f 0%, #505e5c 40%, #303e3d 76%, #1c2a29 94%);
    box-shadow: 0 .4cqw .5cqw #0008, inset 0 .12cqw .16cqw #c9d9d388;
    touch-action: none;
    cursor: ns-resize;
    transition: border-color 0.15s;
  }
  .encoder .dial:hover {
    border-color: #8baca0;
  }
  .dial i {
    position: absolute;
    left: calc(50% - 1px);
    top: 8%;
    width: 2px;
    height: 38%;
    border-radius: 1px;
    background: #d0e6d7;
    transform-origin: 50% 110%;
    transform: rotate(var(--angle, 0deg));
    box-shadow: 0 0 .3cqw #d3fadd40;
    pointer-events: none;
  }
  .detents {
    position: absolute;
    left: 0;
    right: 0;
    top: calc(60% + 0.4cqw);
    display: flex;
    justify-content: center;
    gap: .35cqw;
    opacity: 0;
    transition: opacity .15s;
  }
  .encoder:hover .detents, .encoder:focus-within .detents {
    opacity: 1;
  }
  .detents button {
    width: 2.2cqw;
    height: 1.6cqw;
    margin: 0;
    padding: 0;
    font: 700 1.1cqw/1 system-ui, sans-serif;
    border: 1px solid #5c7575;
    border-radius: .25cqw;
    background: #1a292e;
    color: #e4f5f0;
    cursor: pointer;
  }
  .detents button:hover {
    background: #27403a;
    border-color: #8baca0;
  }

  /* Hardware Panel Buttons */
  .panel-button {
    position: absolute;
    z-index: 2;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 0;
    padding: 0;
    border: 1px solid #141d18;
    border-top-color: #a8bdbc55;
    border-radius: .6cqw;
    color: #d2dfdf;
    background: linear-gradient(#516160, #3c4b4c);
    box-shadow: 0 .3cqw 0 #111c15, 0 .45cqw .5cqw #0006, inset 0 .12cqw .12cqw #b4cebc22;
    font: 700 0.88cqw/1.2 Consolas, "Liberation Mono", monospace;
    letter-spacing: .025em;
    touch-action: none;
    cursor: pointer;
    transition: all 0.08s;
  }
  .panel-button:hover {
    background: linear-gradient(#647b74, #476359);
    border-color: #99baa170;
  }
  .panel-button small {
    font: 600 .54cqw/1.1 Consolas, "Liberation Mono", monospace;
    color: #829b89;
  }
  .panel-button[data-button="12"], .panel-button.play {
    color: #bcfbd9;
    background: linear-gradient(#446b58, #355444);
  }
  .panel-button[data-button="13"], .panel-button.rewind {
    color: #ffd0bd;
    background: linear-gradient(#634540, #4d332f);
  }
  .panel-button.coin {
    color: #ffeaa7;
  }
  .panel-button.start {
    color: #a8e6cf;
  }
  .panel-button.lit, .panel-button.held, .panel-button:active, .panel-button.active {
    box-shadow: 0 .1cqw 0 #15251b, inset 0 .2cqw .4cqw #09130c99;
    transform: translateY(.2cqw);
    background: #607d65 !important;
    color: #e7ffe1 !important;
    border-top-color: #b2dcad !important;
  }

  /* Authentic 27-Key Silicone Performance Keyboard */
  .keyboard {
    position: absolute;
    left: 3.6%;
    top: 53.2%;
    width: 92.8%;
    height: 41%;
    border-radius: 1cqw;
    border: 1px solid #162023;
    background: linear-gradient(#172328, #1a262a);
    box-shadow: inset 0 .35cqw .6cqw #0007, 0 .1cqw 0 #859b9744;
  }
  .piano-key {
    position: absolute;
    transform: translateX(-50%);
    margin: 0;
    padding: 0;
    border: 1px solid #0e1510;
    border-radius: 2.3cqw;
    box-shadow: inset .15cqw 0 .25cqw #8ea79244, 0 .4cqw .4cqw #0009;
    touch-action: none;
    opacity: 1 !important;
    cursor: pointer;
    z-index: 2;
  }
  .piano-key.white {
    top: 48%;
    height: 43%;
    width: 4.35%;
    background: linear-gradient(110deg, #60716c, #425a50 58%, #314a3e);
    color: #aabfb7;
    z-index: 1;
  }
  .piano-key.black {
    top: 6%;
    height: 37%;
    width: 4.1%;
    background: linear-gradient(110deg, #35464a, #25363a 58%, #1c2b31);
    color: #90a9a3;
    z-index: 3;
  }
  .piano-key > i {
    position: absolute;
    left: calc(50% - 1px);
    width: 2px;
    top: 17%;
    height: 48%;
    border-radius: 1px;
    background: #8daa9d;
    box-shadow: inset 0 0 1px #07150a;
    pointer-events: none;
    transition: background 0.05s, box-shadow 0.05s;
  }
  .piano-key.black > i {
    background: #587e71;
  }
  .piano-key span {
    position: absolute;
    bottom: 10%;
    left: -15%;
    right: -15%;
    font: 700 .70cqw/1 Consolas, "Liberation Mono", monospace;
    letter-spacing: .02em;
    text-align: center;
    pointer-events: none;
  }
  .piano-key.black span {
    font-size: .60cqw;
    bottom: 11%;
  }
  .piano-key:hover {
    border-color: #91b697;
    background: #415b47;
  }
  .piano-key.held, .piano-key:active, .piano-key.active, .piano-key.lit {
    background: linear-gradient(#67866a, #4e6e53) !important;
    transform: translate(-50%, .22cqw);
    box-shadow: inset 0 .25cqw .35cqw #152b1890, 0 .1cqw .2cqw #0007;
  }
  .piano-key.lit > i, .piano-key.held > i, .piano-key:active > i, .piano-key.active > i {
    background: #c3f5a4 !important;
    box-shadow: 0 0 .65cqw #a0ec79aa !important;
  }
  .piano-key.lit span, .piano-key.held span, .piano-key:active span, .piano-key.active span {
    color: #c8e3bf !important;
  }

  /* =========================================================================
     COMPANION TACTICAL DOCK (Below Hardware Chassis)
     Arcade Microswitch D-Pad, OLED Telemetry Banner & Jukebox Controls
     ========================================================================= */
  .companion-deck {
    width: 100%;
    max-width: 960px;
    display: grid;
    grid-template-columns: 130px 1fr;
    gap: 14px;
    margin-top: 10px;
    align-items: stretch;
  }

  /* Tactile D-Pad Controller */
  .dpad-container {
    display: grid;
    grid-template-columns: repeat(3, 36px);
    grid-template-rows: repeat(3, 36px);
    gap: 3px;
    background: #151d20;
    padding: 4px;
    border-radius: 12px;
    border: 1px solid #334346;
    box-shadow: inset 0 2px 6px rgba(0,0,0,0.6);
    justify-content: center;
    align-content: center;
  }
  .dpad-btn {
    background: radial-gradient(circle at 35% 35%, #3c4b4d 0%, #202b2e 80%);
    border: 1px solid #4a5c60;
    border-radius: 7px;
    color: #ccdcd7;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.90rem;
    font-weight: 900;
    cursor: pointer;
    box-shadow: 0 3px 6px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.12);
    transition: all 0.05s ease;
  }
  .dpad-btn:hover { background: #4d6163; color: #fff; }
  .dpad-btn:active, .dpad-btn.active {
    background: var(--accent);
    color: #172e24;
    box-shadow: 0 0 12px var(--accent-glow);
    transform: scale(0.94);
  }
  .dpad-center {
    background: #182325;
    border: 1px solid #2d3d40;
    border-radius: 5px;
    position: relative;
  }
  .dpad-center::after {
    content: '';
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #3a4c50;
  }

  /* High-Contrast OLED Telemetry Banner */
  .status-banner {
    background: #12191b;
    padding: 10px 14px;
    border-radius: 10px;
    border: 1px solid #2d3d40;
    font-size: 0.68rem;
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    gap: 4px;
    color: #92a8a4;
    box-shadow: inset 0 2px 6px rgba(0,0,0,0.7);
    font-family: var(--font-mono);
  }
  .telemetry-row { display: flex; justify-content: space-between; align-items: center; }
  .status-banner b { color: var(--accent); }
  .status-tag { color: #00ff66; font-weight: 800; }
  .crt-toggle {
    font-size: 0.62rem;
    color: #728985;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    border-top: 1px solid rgba(255,255,255,0.06);
    padding-top: 4px;
    margin-top: 2px;
  }
  .crt-toggle span:hover { color: var(--accent); }

  /* Demo Songs Jukebox Panel */
  .jukebox-panel {
    grid-column: 1 / -1;
    background: #141c1f;
    border-radius: 10px;
    padding: 10px 14px;
    border: 1px solid #334347;
    display: flex;
    flex-direction: column;
    gap: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.6);
  }
  .jukebox-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.72rem;
    font-weight: 800;
    color: var(--accent);
    letter-spacing: 0.5px;
  }
  .song-pills { display: flex; gap: 6px; flex-wrap: wrap; }
  .song-pill {
    background: #1c272a;
    border: 1px solid #3a4c50;
    color: #b5ccc6;
    padding: 5px 11px;
    border-radius: 6px;
    font-size: 0.65rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.1s ease;
  }
  .song-pill:hover { color: #fff; border-color: var(--accent); }
  .song-pill.active {
    background: var(--accent);
    color: #172e24;
    font-weight: 900;
    box-shadow: 0 0 10px var(--accent-glow);
  }
  .jukebox-controls { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
  .juke-btn {
    background: #243538;
    border: 1px solid #445d61;
    color: #eee;
    padding: 5px 12px;
    border-radius: 6px;
    font-size: 0.68rem;
    font-weight: 800;
    cursor: pointer;
    transition: all 0.08s ease;
  }
  .juke-btn:hover { background: #32494c; color: var(--accent); }
  .juke-btn.playing { background: #00ff66; color: #000; box-shadow: 0 0 8px rgba(0,255,102,0.6); }
  .juke-status { font-size: 0.65rem; color: #8fa5a0; font-family: var(--font-mono); }
  .juke-status b { color: #fff; }

  /* Collapsible Hardware Manual Drawer */
  .manual-drawer {
    width: 100%;
    max-width: 960px;
    margin-top: 14px;
    background: #141c1f;
    border-radius: 10px;
    border: 1px solid #2e3d40;
    overflow: hidden;
  }
  .manual-summary {
    padding: 10px 16px;
    font-size: 0.74rem;
    font-weight: 800;
    color: var(--accent);
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #182226;
    border-bottom: 1px solid #2e3d40;
  }
  .manual-summary:hover { background: #202d32; }
  .manual-content { padding: 12px 16px; font-size: 0.72rem; color: #9ab2ad; }
  .kbd-table { width: 100%; border-collapse: collapse; }
  .kbd-table td { padding: 5px 8px; border-bottom: 1px solid #233134; }
  .kbd-table kbd {
    background: #26363a;
    color: #d1eee0;
    padding: 2px 6px;
    border-radius: 4px;
    border: 1px solid #486368;
    font-size: 0.68rem;
    font-weight: 700;
    font-family: var(--font-mono);
  }

  /* 2X CRT Screen Zoom & Modal Focus */
  .screen-bezel.zoomed {
    position: fixed !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) scale(1.85) !important;
    z-index: 10000 !important;
    box-shadow: 0 0 60px rgba(0, 229, 255, 0.65), 0 30px 90px rgba(0,0,0,0.98) !important;
    border: 3px solid var(--cyan-oled) !important;
    transition: transform 0.22s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
  }
  .zoom-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(6, 9, 14, 0.88);
    backdrop-filter: blur(8px);
    z-index: 9999;
  }
  .zoom-overlay.active { display: block; }

  /* Interactive On-Screen Arcade Quick Controller Bar */
  .arcade-controller-deck {
    position: absolute;
    left: 28.5%;
    top: 50.1%;
    width: 27%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(14, 20, 26, 0.92);
    border: 1px solid rgba(0, 229, 255, 0.25);
    border-radius: 4px;
    padding: 2px 4px;
    gap: 2px;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.7), 0 2px 8px rgba(0,0,0,0.4);
    z-index: 20;
  }
  .ctrl-btn {
    flex: 1;
    background: #1b2329;
    color: #aae4c8;
    border: 1px solid #2e3d46;
    border-radius: 3px;
    font-family: var(--font-mono);
    font-size: 0.58rem;
    font-weight: 800;
    padding: 3px 2px;
    cursor: pointer;
    text-align: center;
    transition: all 0.08s ease-in-out;
    user-select: none;
  }
  .ctrl-btn:hover {
    background: #25333c;
    border-color: var(--cyan-oled);
    color: #fff;
  }
  .ctrl-btn:active, .ctrl-btn.pressed {
    background: var(--accent) !important;
    color: #0b1c14 !important;
    box-shadow: 0 0 10px var(--accent-glow) !important;
    transform: translateY(1px);
  }
  .ctrl-btn.ctrl-action {
    background: #3e1b22;
    color: #ff6b81;
    border-color: #632631;
  }
  .ctrl-btn.ctrl-action:active, .ctrl-btn.ctrl-action.pressed {
    background: #ff4757 !important;
    color: #fff !important;
    box-shadow: 0 0 12px rgba(255, 71, 87, 0.7) !important;
  }
  .ctrl-btn.ctrl-coin {
    background: #3a2e16;
    color: #feca57;
    border-color: #5c471e;
  }
  .ctrl-btn.ctrl-start {
    background: #153423;
    color: #2ed573;
    border-color: #1f5537;
  }
  .ctrl-btn.ctrl-zoom {
    background: #102a36;
    color: #00e5ff;
    border-color: #1b4b60;
  }
  .ctrl-btn.ctrl-god {
    background: #2b1f0c;
    color: #ff9f1a;
    border-color: #5c3c0a;
  }
  .ctrl-btn.ctrl-god.active, .ctrl-btn.ctrl-god:active, .ctrl-btn.ctrl-god.pressed {
    background: #ff9f1a !important;
    color: #0b1c14 !important;
    box-shadow: 0 0 12px rgba(255, 159, 26, 0.8) !important;
  }
  .ctrl-btn.ctrl-skip {
    background: #1a1a36;
    color: #a55eea;
    border-color: #3b2a60;
  }
  .ctrl-btn.ctrl-skip:active, .ctrl-btn.ctrl-skip.pressed {
    background: #a55eea !important;
    color: #fff !important;
    box-shadow: 0 0 12px rgba(165, 94, 234, 0.8) !important;
  }

  /* Streamlined Arcade Mission HUD Bar */
  .arcade-mission-card {
    margin-top: 5px;
    background: rgba(14, 20, 26, 0.85);
    border: 1px solid rgba(0, 229, 255, 0.2);
    border-radius: 6px;
    padding: 5px 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    flex-wrap: wrap;
    font-size: 0.65rem;
  }
  .mission-header {
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .mission-title {
    color: #f5a623;
    font-weight: 800;
    font-size: 0.72rem;
    letter-spacing: 0.5px;
    font-family: var(--font-mono);
  }
  .mission-badge {
    background: rgba(0, 229, 255, 0.12);
    color: #00e5ff;
    font-size: 0.58rem;
    font-weight: 700;
    padding: 1px 6px;
    border-radius: 3px;
    border: 1px solid rgba(0, 229, 255, 0.25);
  }
  .mission-body {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    flex: 1;
    font-size: 0.64rem;
  }
  .mission-col {
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .mission-label {
    color: #aae4c8;
    font-weight: 800;
    font-size: 0.60rem;
    margin-bottom: 0;
  }
  .mission-text {
    color: #c8d6e5;
  }
  .mission-text b {
    color: #ffffff;
  }

  /* Redundant Elements Hidden for Clean 800% Simplified UI */
  .arcade-deck-row { display: none !important; }
  .nav-strip { display: none !important; }

  /* Pulsing Tour Demo Play Button */
  .tour-play-btn {
    background: linear-gradient(135deg, #f5a623 0%, #ff4757 100%);
    color: #ffffff;
    border: none;
    border-radius: 5px;
    font-weight: 900;
    font-size: 0.75rem;
    padding: 6px 14px;
    cursor: pointer;
    box-shadow: 0 0 10px rgba(245, 166, 35, 0.5);
    transition: all 0.15s;
    animation: tourPulse 1.4s infinite alternate;
  }
  /* 4-Bank Arcade Soundboard Styles */
  .sfx-bank-nav {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 8px;
  }
  .sfx-bank-btn {
    background: #141b1e;
    border: 1px solid rgba(170, 228, 200, 0.2);
    color: #8fa59b;
    font: 700 0.65rem/1.2 var(--font-mono);
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.15s ease;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .sfx-bank-btn:hover {
    background: #1a2528;
    color: #e2e7e9;
    border-color: var(--accent);
  }
  .sfx-bank-btn.bank-1.active { background: #3a2e16; border-color: #f5a623; color: #feca57; box-shadow: 0 0 10px rgba(245, 166, 35, 0.35); }
  .sfx-bank-btn.bank-2.active { background: #3e1b22; border-color: #ff4757; color: #ff6b81; box-shadow: 0 0 10px rgba(255, 71, 87, 0.35); }
  .sfx-bank-btn.bank-3.active { background: #102a36; border-color: #00e5ff; color: #00e5ff; box-shadow: 0 0 10px rgba(0, 229, 255, 0.35); }
  .sfx-bank-btn.bank-4.active { background: #163622; border-color: #2ed573; color: #2ed573; box-shadow: 0 0 10px rgba(46, 213, 115, 0.35); }

  .soundboard-grid {
    display: grid;
    grid-template-columns: repeat(9, 1fr);
    gap: 5px;
    margin-top: 4px;
  }
  @media (max-width: 900px) {
    .soundboard-grid { grid-template-columns: repeat(6, 1fr); }
  }
  @media (max-width: 600px) {
    .soundboard-grid { grid-template-columns: repeat(3, 1fr); }
  }
  .sfx-pad {
    background: #121719;
    border: 1px solid rgba(170, 228, 200, 0.15);
    border-radius: 5px;
    padding: 5px 3px;
    text-align: center;
    cursor: pointer;
    transition: all 0.1s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    user-select: none;
    min-height: 52px;
  }
  .sfx-pad:hover {
    background: #182224;
    border-color: var(--accent);
    transform: translateY(-1px);
  }
  .sfx-pad:active, .sfx-pad.active {
    transform: translateY(1px);
    box-shadow: 0 0 14px var(--pad-glow, rgba(0, 255, 102, 0.6));
    border-color: var(--pad-color, #00ff66) !important;
    background: #1e282a;
  }
  .sfx-pad-num {
    position: absolute;
    top: 2px;
    left: 4px;
    font: 700 0.5rem var(--font-mono);
    color: #5d6f6a;
  }
  .sfx-pad-icon { font-size: 0.95rem; line-height: 1; margin-bottom: 2px; }
  .sfx-pad-name { font: 800 0.6rem var(--font-mono); color: #e2e7e9; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 95%; }
  .sfx-pad-game { font: 600 0.48rem var(--font-mono); color: #7f938d; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 95%; }
  .sfx-pad-chip { font: 700 0.44rem var(--font-mono); color: #aae4c8; background: rgba(170, 228, 200, 0.1); padding: 1px 3px; border-radius: 2px; margin-top: 1px; }

</style>
</head>
<body>

<!-- Cockpit Header Bar -->
<div class="title-bar">
  <div class="branding-wrap">
    <img src="images/stack_trace_avatar.png" id="headerAvatar" alt="Stack Trace Avatar" onerror="this.src='data:image/png;base64,__STACK_TRACE_AVATAR_B64__'" class="header-avatar">
    <div>
      <div class="brand-sub">STACK TRACE</div>
      <h1>ARCADE RAT <span class="version-tag">v 1.0</span></h1>
      <div class="subtitle">Bare-Metal Z80 Arcade & 5-Chip Synthesizer</div>
    </div>
  </div>
  <div class="header-actions">
    <button class="splash-trigger-btn album-btn" id="btnAlbumSplash" style="background:#221528; border-color:#6c3d7e; color:#f5cd79;" onclick="triggerAlbumSplashScreen()" title="View Stack Trace's Chiptunes Album Splash Screen">💿 ALBUM</button>
    <button class="splash-trigger-btn" id="btnReplaySplash" onclick="triggerSplashScreen()" title="View Arcade Rat Firmware Boot Splash">⚡ SPLASH</button>
    <a href="configurator.html" class="config-btn">⚙️ CONFIG (93)</a>
  </div>
</div>

<!-- Two-Tier Studio Workspace Navigation -->
<div class="studio-nav-bar">
  <button class="studio-tab active" id="tabArcade" data-tab="arcade" onclick="setStudioTab('arcade')">🕹️ ARCADE VAULT (8)</button>
  <button class="studio-tab" id="tabSynth" data-tab="synth" onclick="setStudioTab('synth')">🎹 SYNTH STUDIO (5)</button>
  <button class="studio-tab" id="tabTracker" data-tab="tracker" onclick="setStudioTab('tracker')">🎛️ TRACKER (16-STEP)</button>
  <button class="studio-tab" id="tabDemo" data-tab="demo" onclick="setStudioTab('demo')">🎵 DEMO JUKEBOX</button>
  <button class="studio-tab" id="tabSoundboard" data-tab="soundboard" onclick="setStudioTab('soundboard')">🔊 SFX BANKS (4×27)</button>
  <button class="studio-tab" id="tabSpeech" data-tab="speech" onclick="setStudioTab('speech')" style="background:linear-gradient(135deg, rgba(0,229,255,0.15) 0%, rgba(13,59,71,0.3) 100%); border-color:#00e5ff; color:#00e5ff; font-weight:800;">🗣️ SPEECH ROM (8)</button>
  <button class="studio-tab" id="tabTour" data-tab="tour" onclick="setStudioTab('tour')">🎡 TOUR DEMO</button>
</div>

<!-- Context Shelves -->
<div class="shelf-wrap">
  <!-- Shelf 1: Playable Arcade Vault (8 Games) -->
  <div class="context-shelf active" id="shelfArcade">
    <div class="shelf-header">
      <span>🕹️ PLAYABLE ARCADE VAULT · CLICK ANY GAME TO LAUNCH INSTANTLY</span>
      <span class="tag">8 ARCADE CLASSICS AVAILABLE</span>
    </div>
    <div class="arcade-gallery-grid">
      <div class="arcade-card active" id="btnGamePacman" data-game="pacman" onclick="switchActiveGame('pacman')">
        <div class="card-emoji">🟡</div>
        <div class="card-name">PAC-MAN</div>
        <div class="card-meta">1980 · Namco</div>
        <div class="card-badge">Z80 + WSG</div>
      </div>
      <div class="arcade-card" id="btnGameClimber" data-game="cclimber" onclick="switchActiveGame('cclimber')">
        <div class="card-emoji">🧗</div>
        <div class="card-name">Crazy Climber</div>
        <div class="card-meta">1980 · Nichibutsu</div>
        <div class="card-badge">Twin-Stick</div>
      </div>
      <div class="arcade-card" id="btnGameGalaga" data-game="galaga" onclick="switchActiveGame('galaga')">
        <div class="card-emoji">🚀</div>
        <div class="card-name">Galaga</div>
        <div class="card-meta">1981 · Namco</div>
        <div class="card-badge">Dual Z80</div>
      </div>
      <div class="arcade-card" id="btnGameDkong" data-game="dkong" onclick="switchActiveGame('dkong')">
        <div class="card-emoji">🦍</div>
        <div class="card-name">Donkey Kong</div>
        <div class="card-meta">1981 · Nintendo</div>
        <div class="card-badge">Platformer</div>
      </div>
      <div class="arcade-card" id="btnGameFrogger" data-game="frogger" onclick="switchActiveGame('frogger')">
        <div class="card-emoji">🐸</div>
        <div class="card-name">Frogger</div>
        <div class="card-meta">1981 · Konami</div>
        <div class="card-badge">Dual AY PSG</div>
      </div>
      <div class="arcade-card" id="btnGameAsteroids" data-game="asteroids" onclick="switchActiveGame('asteroids')">
        <div class="card-emoji">☄️</div>
        <div class="card-name">Asteroids</div>
        <div class="card-meta">1979 · Atari</div>
        <div class="card-badge">Vector CRT</div>
      </div>
      <div class="arcade-card" id="btnGameTempest" data-game="tempest" onclick="switchActiveGame('tempest')">
        <div class="card-emoji">🌀</div>
        <div class="card-name">Tempest</div>
        <div class="card-meta">1981 · Atari</div>
        <div class="card-badge">Color Vector</div>
      </div>
      <div class="arcade-card" id="btnGameGyruss" data-game="gyruss" onclick="switchActiveGame('gyruss')">
        <div class="card-emoji">🌌</div>
        <div class="card-name">Gyruss</div>
        <div class="card-meta">1983 · Konami</div>
        <div class="card-badge">5x PSG 3D</div>
      </div>
    </div>

    <!-- Active Arcade Mission & How-To-Play Ribbon -->
    <div class="arcade-mission-card" id="arcadeMissionCard">
      <div class="mission-header">
        <span class="mission-title" id="missionTitle">PAC-MAN (1980 NAMCO)</span>
        <span class="mission-badge" id="missionBadge">MAZE CHASE · Z80 + WSG</span>
      </div>
      <div class="mission-body">
        <div class="mission-col">
          <span class="mission-label">🎯 GOAL:</span>
          <span class="mission-text" id="missionObjective">Navigate maze, eat 244 dots and 4 energizers! Avoid Blinky, Pinky, Inky & Clyde.</span>
        </div>
        <div class="mission-col">
          <span class="mission-label">🕹️ KEYS:</span>
          <span class="mission-text" id="missionControls"><b>WASD/Arrows</b> · <b>1</b> Coin · <b>5</b> Start · <b>Space</b> Quick Play</span>
        </div>
        <span class="mission-text" id="missionTip" style="display:none;"></span>
      </div>
    </div>

    <!-- Interactive Tactical Arcade Controller Deck (Preserved for compatibility) -->
    <div class="arcade-deck-row" style="display:none;">
      <button class="synth-opt-btn" id="shelfBtnLeft" onclick="pulseUnifiedAction('left')" title="Left (A / ◀)">◀ LEFT (A)</button>
      <button class="synth-opt-btn" id="shelfBtnUp" onclick="pulseUnifiedAction('up')" title="Up / Jump (W / ▲)">▲ UP / JUMP (W)</button>
      <button class="synth-opt-btn" id="shelfBtnDown" onclick="pulseUnifiedAction('down')" title="Down / Climb (S / ▼)">▼ DOWN (S)</button>
      <button class="synth-opt-btn" id="shelfBtnRight" onclick="pulseUnifiedAction('right')" title="Right (D / ▶)">▶ RIGHT (D)</button>
      <button class="synth-opt-btn" id="shelfBtnFire" onclick="pulseUnifiedAction('action')" title="Action / Fire / Jump (Space)">🔴 ACTION (SPACE)</button>
      <button class="synth-opt-btn" id="shelfBtnCoin" onclick="insertCoin()" title="Insert Coin (1 / C)">🪙 COIN (1)</button>
      <button class="synth-opt-btn" id="shelfBtnStart" onclick="start1P()" title="Start Game (5 / Enter)">▶ START (5)</button>
    </div>

    <!-- Arcade Hall of Fame Leaderboard Strip -->
    <div class="arcade-leaderboard-card" id="arcadeLeaderboardCard" style="margin-top:6px; background:rgba(12,16,22,0.85); border:1px solid rgba(245,166,35,0.22); border-radius:6px; padding:4px 8px;">
      <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:4px;">
        <span style="font-size:0.65rem; font-weight:800; color:#f5a623; font-family:var(--font-mono); letter-spacing:0.8px;">🏆 LEADERBOARD: <span id="lbCurrentGameTag" style="color:#aae4c8;">PAC-MAN (1980)</span></span>
        <button class="synth-opt-btn" style="font-size:0.56rem; padding:2px 5px;" onclick="promptCurrentGameInitials()">✍️ SUBMIT INITIALS</button>
      </div>
      <div id="arcadeLeaderboardList" style="display:grid; grid-template-columns: repeat(5, 1fr); gap:4px; font-family:var(--font-mono); font-size:0.62rem;">
        <!-- Populated dynamically -->
      </div>
    </div>
  </div>

  <!-- Shelf 2: Synth Studio (5 Soundchips + Live Tweak) -->
  <div class="context-shelf" id="shelfSynth">
    <div class="shelf-header">
      <span>🎹 LIVE MULTI-ENGINE SYNTHESIZER · 5 SOUNDCHIPS & VECTOR OSC</span>
      <span class="tag" id="synthStatusTag">POLYPHONIC · 60Hz</span>
    </div>
    <div class="synth-section">
      <div class="synth-row">
        <span class="synth-label">SOUNDCHIP:</span>
        <div class="synth-btn-group">
          <button class="synth-chip-btn active" data-engine="wsg" onclick="setSynthEngine('wsg')">🟡 Namco WSG (3-Voice)</button>
          <button class="synth-chip-btn" data-engine="ay8910" onclick="setSynthEngine('ay8910')">🧗 AY-3-8910 (Chiptune PSG)</button>
          <button class="synth-chip-btn" data-engine="pokey" onclick="setSynthEngine('pokey')">☄️ Atari POKEY (Distortion)</button>
          <button class="synth-chip-btn" data-engine="dac" onclick="setSynthEngine('dac')">🦍 Nintendo DAC (7-bit APU)</button>
          <button class="synth-chip-btn" data-engine="fm" onclick="setSynthEngine('fm')">🎹 M-VAVE FM-1 (6-OP DX)</button>
        </div>
      </div>
      <div class="synth-row">
        <span class="synth-label">ENVELOPE:</span>
        <div class="synth-btn-group">
          <button class="synth-opt-btn synth-env-btn" data-env="pluck" onclick="setEnvelope('pluck')">Pluck</button>
          <button class="synth-opt-btn synth-env-btn active" data-env="lead" onclick="setEnvelope('lead')">Lead</button>
          <button class="synth-opt-btn synth-env-btn" data-env="organ" onclick="setEnvelope('organ')">Organ</button>
          <button class="synth-opt-btn synth-env-btn" data-env="pad" onclick="setEnvelope('pad')">Pad</button>
        </div>
        <span class="synth-label" style="min-width:70px; margin-left:10px;">OCTAVE:</span>
        <div class="synth-btn-group">
          <button class="synth-opt-btn synth-oct-btn" data-oct="-2" onclick="setSynthOctave(-2)">-2</button>
          <button class="synth-opt-btn synth-oct-btn" data-oct="-1" onclick="setSynthOctave(-1)">-1</button>
          <button class="synth-opt-btn synth-oct-btn active" data-oct="0" onclick="setSynthOctave(0)">0</button>
          <button class="synth-opt-btn synth-oct-btn" data-oct="1" onclick="setSynthOctave(1)">+1</button>
          <button class="synth-opt-btn synth-oct-btn" data-oct="2" onclick="setSynthOctave(2)">+2</button>
        </div>
        <div class="synth-btn-group" style="margin-left:auto;">
          <button class="synth-opt-btn" id="synthBtnArp" onclick="toggleArp()">ARP: OFF</button>
          <button class="synth-opt-btn" id="synthBtnLfo" onclick="toggleLfo()">LFO: OFF</button>
        </div>
      </div>
      <div class="synth-hint-bar">
        <span>⚡ <b>PLAY NOTES:</b> Click silicone keys 1-27 below or press QWERTY keys (A-K / W-U). Vector CRT shows real-time live oscilloscope.</span>
        <span><b>SCL</b>=Cycle Engine · <b>ENV</b>=Cycle Envelope</span>
      </div>
    </div>
  </div>

  <!-- Shelf 3: 16-Step Chiptune Tracker -->
  <div class="context-shelf" id="shelfTracker">
    <div class="shelf-header">
      <span>🎛️ 16-STEP CHIPTUNE TRACKER · 8 ARCHITECTURE PATTERNS</span>
      <span class="tag" id="trackerStatusTag">LOOP: STOPPED</span>
    </div>
    <div class="synth-section">
      <div class="synth-row">
        <span class="synth-label">PATTERNS:</span>
        <div class="synth-btn-group" id="trackerPatternList">
          <button class="synth-chip-btn active" data-pat="0" onclick="selectTrackerPattern(0)">01: ARCADE RAT (132 BPM)</button>
          <button class="synth-chip-btn" data-pat="1" onclick="selectTrackerPattern(1)">02: PAC-MANIA DUB (124 BPM)</button>
          <button class="synth-chip-btn" data-pat="2" onclick="selectTrackerPattern(2)">03: GYRUSS SPEED (144 BPM)</button>
          <button class="synth-chip-btn" data-pat="3" onclick="selectTrackerPattern(3)">04: CYBER LABYRINTH (138 BPM)</button>
          <button class="synth-chip-btn" data-pat="4" onclick="selectTrackerPattern(4)">05: DK 25M SWING (136 BPM)</button>
          <button class="synth-chip-btn" data-pat="5" onclick="selectTrackerPattern(5)">06: GALAGA SECTOR (140 BPM)</button>
          <button class="synth-chip-btn" data-pat="6" onclick="selectTrackerPattern(6)">07: TEMPEST SURGE (148 BPM)</button>
          <button class="synth-chip-btn" data-pat="7" onclick="selectTrackerPattern(7)">08: TOCCATA D MIN (134 BPM)</button>
        </div>
      </div>
      <div class="synth-row">
        <span class="synth-label">CONTROLS:</span>
        <div class="synth-btn-group">
          <button class="synth-opt-btn" id="btnTrackerPlay" onclick="toggleTracker()">▶ PLAY LOOP</button>
          <button class="synth-opt-btn" onclick="cycleTrackerPattern()">⏭ NEXT PATTERN</button>
          <button class="synth-opt-btn" onclick="stepTrackerStep()">⏩ STEP</button>
        </div>
        <span style="font-size:0.62rem; color:#8fa5a0; margin-left:auto; font-family:var(--font-mono);" id="trackerStepDisplay">STEP: <b>01/16</b></span>
      </div>
    </div>
  </div>

  <!-- Shelf 4: Demo Jukebox -->
  <div class="context-shelf" id="shelfDemo">
    <div class="shelf-header">
      <span>🎵 MULTI-ENGINE FULL DEMO SONGS JUKEBOX · 15-TRACK VU METERS</span>
      <span class="tag" id="shelfJukeStatus">STOPPED</span>
    </div>

    <!-- Official Chiptunes Album Feature Card -->
    <div class="album-hero-card" style="display:flex; align-items:center; gap:14px; background:linear-gradient(135deg, rgba(29,18,38,0.92) 0%, rgba(14,20,26,0.95) 100%); border:1px solid rgba(155,89,182,0.35); border-radius:6px; padding:8px 12px; margin-bottom:10px;">
      <img src="images/stack_trace_chiptunes_album.jpg" onerror="this.src='data:image/jpeg;base64,__STACK_TRACE_ALBUM_B64__'" style="width:54px; height:54px; border-radius:4px; object-fit:cover; border:1px solid rgba(0,255,102,0.4); cursor:pointer;" onclick="triggerAlbumSplashScreen()" alt="Chiptunes Album Cover" title="Click to view full CRT splash screen!">
      <div style="flex:1;">
        <div style="font-size:0.62rem; color:#aae4c8; font-weight:800; font-family:var(--font-mono); letter-spacing:1.5px;">OFFICIAL ALBUM RELEASE · STACK TRACE_</div>
        <div style="font-size:0.88rem; font-weight:900; color:#f5cd79; letter-spacing:0.8px;">CHIPTUNES YOU DIDN'T KNOW YOU NEEDED TO HEAR</div>
        <div style="font-size:0.62rem; color:#8fa59b; font-family:var(--font-mono); margin-top:2px;">4 Multi-Voice Retro Symphonies · 15 Hardware Chiptune Channels · Z80/POKEY/AY-3-8910</div>
      </div>
      <button class="synth-opt-btn" style="background:#4b2354; border-color:#9b59b6; color:#fff;" onclick="triggerAlbumSplashScreen()">💿 VIEW ALBUM SPLASH</button>
    </div>
    <div class="synth-section">
      <div class="synth-row">
        <span class="synth-label">SYMPHONIES:</span>
        <div class="synth-btn-group" id="shelfSongPills">
          <!-- Populated dynamically -->
        </div>
      </div>
      <div class="synth-row">
        <span class="synth-label">PLAYBACK:</span>
        <div class="synth-btn-group">
          <button class="synth-opt-btn" id="btnShelfPlay" onclick="playDemoSong()">▶ PLAY</button>
          <button class="synth-opt-btn" id="btnShelfPause" onclick="pauseDemoSong()">⏸ PAUSE</button>
          <button class="synth-opt-btn" id="btnShelfStop" onclick="stopDemoSong()">⏹ STOP</button>
          <button class="synth-opt-btn" onclick="stepSong(-1)">⏮ PREV</button>
          <button class="synth-opt-btn" onclick="stepSong(1)">⏭ NEXT</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Shelf 5: 4-Bank Iconic Arcade Soundboard -->
  <div class="context-shelf" id="shelfSoundboard">
    <div class="shelf-header">
      <span id="sfxBoardTitle">🔊 ICONIC ARCADE SOUNDBOARD · 4 MASTER BANKS & 27 HARDWARE PADS</span>
      <span class="tag" id="sfxBankTag" style="color:#f5a623; border-color:#f5a623;">BANK 1: GOLDEN AGE (27 SFX)</span>
    </div>
    <div class="synth-section">
      <!-- 4 Bank Navigation Selector -->
      <div class="sfx-bank-nav" id="sfxBankNav">
        <button class="sfx-bank-btn bank-1 active" onclick="switchSfxBank(0)" title="Bank 1: Pac-Man, Space Invaders, Galaga, Asteroids, Dig Dug">🟡 BANK 1: GOLDEN AGE (1978–1982)</button>
        <button class="sfx-bank-btn bank-2" onclick="switchSfxBank(1)" title="Bank 2: Donkey Kong, Mario Bros, Punch-Out, Excitebike">🦍 BANK 2: NINTENDO 8-BIT (1981–1985)</button>
        <button class="sfx-bank-btn bank-3" onclick="switchSfxBank(2)" title="Bank 3: Defender, Asteroids, Tempest, Robotron, Star Wars">☄️ BANK 3: ATARI VECTOR & SCI-FI (1979–1984)</button>
        <button class="sfx-bank-btn bank-4" onclick="switchSfxBank(3)" title="Bank 4: Frogger, Gyruss, Crazy Climber, Q*bert, OutRun">🐸 BANK 4: KONAMI & SEGA (1981–1987)</button>
      </div>

      <!-- 8-Voice Vintage Arcade Speech Synthesizer ROM Bar -->
      <div class="speech-rom-shelf" style="display:flex; align-items:center; gap:6px; flex-wrap:wrap; margin-bottom:8px; padding:6px 8px; background:rgba(0,229,255,0.06); border:1px solid rgba(0,229,255,0.25); border-radius:4px;">
        <span style="font-size:0.65rem; font-weight:800; color:#00e5ff; font-family:var(--font-mono); letter-spacing:1px; margin-right:4px;">🗣️ VINTAGE SPEECH ROM:</span>
        <button class="synth-opt-btn" style="background:#133337; color:#00e5ff; border-color:#00e5ff; font-size:0.62rem;" onclick="triggerSpeechRom('VOX_INTRUDER')">BERZERK: INTRUDER</button>
        <button class="synth-opt-btn" style="background:#133337; color:#00e5ff; border-color:#00e5ff; font-size:0.62rem;" onclick="triggerSpeechRom('VOX_COIN')">INSERT COIN</button>
        <button class="synth-opt-btn" style="background:#3b2438; color:#f368e0; border-color:#f368e0; font-size:0.62rem;" onclick="triggerSpeechRom('VOX_QBERT')">Q*BERT @!#?@!</button>
        <button class="synth-opt-btn" style="background:#3e1b22; color:#ff6b81; border-color:#ff6b81; font-size:0.62rem;" onclick="triggerSpeechRom('VOX_SINISTAR')">SINISTAR: BEWARE</button>
        <button class="synth-opt-btn" style="background:#3e1b22; color:#ff6b81; border-color:#ff6b81; font-size:0.62rem;" onclick="triggerSpeechRom('VOX_HUNGER')">SINISTAR: I HUNGER</button>
        <button class="synth-opt-btn" style="background:#281e3d; color:#a55eea; border-color:#a55eea; font-size:0.62rem;" onclick="triggerSpeechRom('VOX_WIZARD')">WIZARD: WORLINGS</button>
        <button class="synth-opt-btn" style="background:#3a2e16; color:#feca57; border-color:#feca57; font-size:0.62rem;" onclick="triggerSpeechRom('VOX_DANGER')">DANGER ZONE</button>
        <button class="synth-opt-btn" style="background:#153423; color:#2ed573; border-color:#2ed573; font-size:0.62rem;" onclick="triggerSpeechRom('VOX_ARCADE_RAT')">ARCADE RAT</button>
      </div>

      <!-- Telemetry and Status Banner -->
      <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:6px; font-size:0.62rem; color:#8fa59b; font-family:var(--font-mono); gap:10px; flex-wrap:wrap;">
        <span id="sfxBankDesc" style="color:#c2d4ce;">Namco, Midway & Atari (1978–1982) · Pac-Man, Space Invaders, Galaga, Asteroids · WSG Wavetable & POKEY</span>
        <span id="sfxLastTriggered" style="color:var(--accent); margin-left:auto;">TOUCH SILICONE KEYS 1-27 OR CLICK PADS</span>
      </div>

      <!-- 27 Interactive Arcade SFX Pads Matrix Grid -->
      <div class="soundboard-grid" id="soundboardPadsGrid">
        <!-- Rendered dynamically -->
      </div>
    </div>
  </div>

  <!-- Shelf 5B: Vintage Speech ROM (8 Emulated Arcade Voice Synthesizers) -->
  <div class="context-shelf" id="shelfSpeech">
    <div class="shelf-header">
      <span>🗣️ VINTAGE ARCADE SPEECH & PCM SAMPLE-ROM SYNTHESIZER · PURE WEB AUDIO FORMANT ENGINE</span>
      <span class="tag" id="speechRomTag" style="color:#00e5ff; border-color:#00e5ff;">8 AUTHENTIC VOICE PHRASES (1980–1983)</span>
    </div>
    <div class="synth-section">
      <!-- Telemetry and Status Banner -->
      <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:4px; font-size:0.64rem; color:#8fa59b; font-family:var(--font-mono); gap:10px; flex-wrap:wrap; background:rgba(0,229,255,0.05); padding:6px 10px; border-radius:5px; border:1px solid rgba(0,229,255,0.2);">
        <span id="speechStatusDisplay" style="color:#00e5ff;">CLICK ANY CARD OR PRESS 1–8 ON KEYBOARD TO TRIGGER VINTAGE SPEECH CHIPS</span>
        <span style="color:#f5cd79; margin-left:auto;">SHORTCUTS: [V] TOGGLE SPEECH · [1-8] TRIGGER PHRASE</span>
      </div>

      <!-- 8 Vintage Speech ROM Cards Grid -->
      <div class="speech-grid" id="speechRomGrid">
        <div class="speech-card" id="card_VOX_INTRUDER" onclick="triggerSpeechRom('VOX_INTRUDER')">
          <div class="speech-card-header">
            <span class="speech-card-title">🤖 Intruder Alert!</span>
            <span class="speech-chip-badge">TSI S14001A</span>
          </div>
          <div class="speech-quote">"IN-TRU-DER A-LERT! IN-TRU-DER A-LERT!"</div>
          <div class="speech-game-meta">
            <span>Berzerk (1980 · Stern)</span>
            <span style="color:#00e5ff;">KEY 1</span>
          </div>
          <button class="speech-play-btn" onclick="event.stopPropagation(); triggerSpeechRom('VOX_INTRUDER')">▶ SPEAK PHRASE</button>
        </div>

        <div class="speech-card" id="card_VOX_COIN" onclick="triggerSpeechRom('VOX_COIN')">
          <div class="speech-card-header">
            <span class="speech-card-title">🪙 Coin Detected!</span>
            <span class="speech-chip-badge">TSI S14001A</span>
          </div>
          <div class="speech-quote">"COIN DE-TEC-TED IN POCK-ET!"</div>
          <div class="speech-game-meta">
            <span>Berzerk (1980 · Stern)</span>
            <span style="color:#00e5ff;">KEY 2</span>
          </div>
          <button class="speech-play-btn" onclick="event.stopPropagation(); triggerSpeechRom('VOX_COIN')">▶ SPEAK PHRASE</button>
        </div>

        <div class="speech-card" id="card_VOX_QBERT" onclick="triggerSpeechRom('VOX_QBERT')">
          <div class="speech-card-header">
            <span class="speech-card-title">🤬 @!#?@! Swear</span>
            <span class="speech-chip-badge">VOTRAX SC-01</span>
          </div>
          <div class="speech-quote">"@!#?@! VOTRAX SPEECH SYNTH"</div>
          <div class="speech-game-meta">
            <span>Q*bert (1982 · Gottlieb)</span>
            <span style="color:#00e5ff;">KEY 3</span>
          </div>
          <button class="speech-play-btn" onclick="event.stopPropagation(); triggerSpeechRom('VOX_QBERT')">▶ SPEAK PHRASE</button>
        </div>

        <div class="speech-card" id="card_VOX_SINISTAR" onclick="triggerSpeechRom('VOX_SINISTAR')">
          <div class="speech-card-header">
            <span class="speech-card-title">👹 Beware, I Live!</span>
            <span class="speech-chip-badge">HC-55516 CVSD</span>
          </div>
          <div class="speech-quote">"BE-WARE, I LIVE!"</div>
          <div class="speech-game-meta">
            <span>Sinistar (1982 · Williams)</span>
            <span style="color:#00e5ff;">KEY 4</span>
          </div>
          <button class="speech-play-btn" onclick="event.stopPropagation(); triggerSpeechRom('VOX_SINISTAR')">▶ SPEAK PHRASE</button>
        </div>

        <div class="speech-card" id="card_VOX_HUNGER" onclick="triggerSpeechRom('VOX_HUNGER')">
          <div class="speech-card-header">
            <span class="speech-card-title">💀 I Hunger, Coward!</span>
            <span class="speech-chip-badge">HC-55516 CVSD</span>
          </div>
          <div class="speech-quote">"I HUN-GER, CO-WARD!"</div>
          <div class="speech-game-meta">
            <span>Sinistar (1982 · Williams)</span>
            <span style="color:#00e5ff;">KEY 5</span>
          </div>
          <button class="speech-play-btn" onclick="event.stopPropagation(); triggerSpeechRom('VOX_HUNGER')">▶ SPEAK PHRASE</button>
        </div>

        <div class="speech-card" id="card_VOX_WIZARD" onclick="triggerSpeechRom('VOX_WIZARD')">
          <div class="speech-card-header">
            <span class="speech-card-title">🧙 Wizard of Wor</span>
            <span class="speech-chip-badge">VOTRAX SC-01</span>
          </div>
          <div class="speech-quote">"I AM THE WIZ-ARD OF WOR!"</div>
          <div class="speech-game-meta">
            <span>Wizard of Wor (1980 · Midway)</span>
            <span style="color:#00e5ff;">KEY 6</span>
          </div>
          <button class="speech-play-btn" onclick="event.stopPropagation(); triggerSpeechRom('VOX_WIZARD')">▶ SPEAK PHRASE</button>
        </div>

        <div class="speech-card" id="card_VOX_GORF" onclick="triggerSpeechRom('VOX_GORF')">
          <div class="speech-card-header">
            <span class="speech-card-title">🛸 Long Live Gorf!</span>
            <span class="speech-chip-badge">VOTRAX SC-01</span>
          </div>
          <div class="speech-quote">"LONG LIVE GORF! HA-HA-HA-HA!"</div>
          <div class="speech-game-meta">
            <span>GORF (1981 · Midway)</span>
            <span style="color:#00e5ff;">KEY 7</span>
          </div>
          <button class="speech-play-btn" onclick="event.stopPropagation(); triggerSpeechRom('VOX_GORF')">▶ SPEAK PHRASE</button>
        </div>

        <div class="speech-card" id="card_VOX_DRAGON" onclick="triggerSpeechRom('VOX_DRAGON')">
          <div class="speech-card-header">
            <span class="speech-card-title">🗡️ Lead On Adventurer!</span>
            <span class="speech-chip-badge">8-BIT LINEAR PCM</span>
          </div>
          <div class="speech-quote">"LEAD ON, AD-VEN-TUR-ER!"</div>
          <div class="speech-game-meta">
            <span>Dragon's Lair (1983 · Cinematronics)</span>
            <span style="color:#00e5ff;">KEY 8</span>
          </div>
          <button class="speech-play-btn" onclick="event.stopPropagation(); triggerSpeechRom('VOX_DRAGON')">▶ SPEAK PHRASE</button>
        </div>
        <!-- Compatibility elements for legacy IDs -->
        <div style="display:none;" id="card_VOX_DANGER"></div>
        <div style="display:none;" id="card_VOX_ARCADE_RAT"></div>
      </div>
    </div>
  </div>

  <!-- Shelf 6: Tour All ROMs -->
  <div class="context-shelf" id="shelfTour">
    <div class="shelf-header">
      <span>🎡 ATTRACT TOUR DEMO · CYCLING ALL 8 INSTALLED ARCADE ENGINES</span>
      <span class="tag">AUTO-ROTATING AT 60 FPS</span>
    </div>
    <div class="synth-section">
      <div class="synth-row">
        <span class="synth-label">TOUR CONTROLS:</span>
        <div class="synth-btn-group">
          <button class="synth-opt-btn" onclick="prevTourGame()">◀ PREV GAME (P)</button>
          <button class="synth-opt-btn" onclick="nextTourGame()">▶ NEXT GAME (N)</button>
          <button class="synth-opt-btn" id="btnTourPause" onclick="toggleTourPause()">⏸ PAUSE TOUR</button>
          <button class="tour-play-btn" onclick="launchCurrentTourGame()">⚡ PLAY CURRENT GAME (SPACE)</button>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Secondary Navigation & Mode Indicators -->
<div class="nav-strip" style="margin-bottom: 8px;">
  <div class="mode-indicator" style="width: 100%; justify-content: center;">
    <div class="mode-tag active" data-mode="arcade">ARCADE</div>
    <div class="mode-tag" data-mode="synth">SYNTH STUDIO</div>
    <div class="mode-tag" data-mode="tracker">TRACKER</div>
    <div class="mode-tag" data-mode="demo">DEMO SONGS</div>
    <div class="mode-tag" data-mode="soundboard">SFX PADS (27)</div>
    <div class="mode-tag" data-mode="tour">TOUR DEMO</div>
    <div class="mode-tag" data-mode="rewind">REWIND</div>
    <div class="mode-tag" data-mode="vector">LISSAJOUS</div>
    <div class="mode-tag" data-mode="glitch">BENDER</div>
  </div>
</div>

<!-- =========================================================================
     M-VAVE FM-1 HARDWARE CHASSIS CONTAINER
     100% Faithful Replica of the Physical M-VAVE FM-1 Synthesizer Faceplate
     ========================================================================= -->
<div class="device-scroll">
<div id="sim-device" class="sim-device" aria-label="FM1 实机布局">
  <!-- Silkscreen Markings -->
  <div class="device-brand">FM–1 <span>STACK TRACE · ARCADE RAT v1.0</span></div>
  <span class="case-mark">BARE-METAL Z80 · 240x240 CRT</span>

  <!-- Hardware Status LEDs -->
  <div class="led-array">
    <div class="led-item"><div class="led-dot pwr"></div>PWR</div>
    <div class="led-item"><div class="led-dot sync"></div>60Hz</div>
    <div class="led-item"><div class="led-dot midi" id="midiLed"></div>MIDI</div>
  </div>

  <!-- 4 Corner Hex Screws -->
  <i class="screw tl"></i><i class="screw tr"></i><i class="screw bl"></i><i class="screw br"></i>

  <!-- Center 240x240 CRT Screen Bezel -->
  <div class="screen-bezel" id="screenBezel" title="Click quadrants to steer character!">
    <div class="lcd-surface">
      <canvas id="tftCanvas" width="240" height="240" aria-label="FM1 设备屏幕仿真"></canvas>
      <div class="screen-quadrant-hints">
        <span class="quadrant-hint hint-up">▲</span>
        <span class="quadrant-hint hint-down">▼</span>
        <span class="quadrant-hint hint-left">◀</span>
        <span class="quadrant-hint hint-right">▶</span>
      </div>
    </div>
  </div>
  <div class="screen-caption">
    <span id="hudStatus">● ATTRACT MODE</span>
    <span id="hudCredits">CREDITS: 0</span>
    <span id="immortalLedTag" style="display:none; color:#ff9f1a; font-weight:800; margin-left:6px; text-shadow:0 0 6px rgba(255,159,26,0.6);">⚡ GOD MODE</span>
    <span id="crtStatus" style="cursor:pointer;" title="Click or Press K to toggle scanlines">SCANLINES: ON</span>
    <span id="btnZoomScreen" style="cursor:pointer; color:var(--cyan-oled); margin-left:6px; font-weight:800;" onclick="toggleScreenZoom()" title="Press Z or click to toggle 2X zoom">🔍 ZOOM 2X</span>
  </div>

  <!-- On-Screen Arcade Quick Controller Bar (Mouse, Touch & Visual Key Feedback) -->
  <div class="arcade-controller-deck" id="arcadeControllerDeck">
    <button class="ctrl-btn" id="ctrlBtnLeft" title="Left (A / ◀)">◀ LEFT</button>
    <button class="ctrl-btn" id="ctrlBtnUp" title="Up / Jump (W / ▲)">▲ UP</button>
    <button class="ctrl-btn" id="ctrlBtnDown" title="Down / Climb (S / ▼)">▼ DOWN</button>
    <button class="ctrl-btn" id="ctrlBtnRight" title="Right (D / ▶)">▶ RIGHT</button>
    <button class="ctrl-btn ctrl-action" id="ctrlBtnFire" title="Action / Fire / Jump (Space)">🔴 ACTION</button>
    <button class="ctrl-btn ctrl-coin" id="ctrlBtnCoin" title="Insert Coin (1 / C)">🪙 COIN</button>
    <button class="ctrl-btn ctrl-start" id="ctrlBtnStart" title="Start Game (5 / Enter)">▶ START</button>
    <button class="ctrl-btn ctrl-god" id="ctrlBtnImmortal" onclick="toggleImmortalMode()" title="Toggle Immortal God Mode (I / G)">⚡ IMMORTAL</button>
    <button class="ctrl-btn ctrl-skip" id="ctrlBtnLevelSkip" onclick="skipCurrentLevel()" title="Skip Current Level / Advance Stage (L / N)">⏩ SKIP LVL</button>
    <button class="ctrl-btn ctrl-zoom" id="ctrlBtnZoom" onclick="toggleScreenZoom()" title="Toggle 2X Screen Zoom (Z)">🔍 ZOOM</button>
  </div>


  <!-- Left Encoders (Flanking Screen) -->
  <div class="encoder" style="left: 10.5%; top: 16.03%;">
    <span>MASTER</span>
    <button class="dial" id="encMaster" aria-label="Master Volume"><i></i></button>
    <div class="detents"><button id="btnVolDown">−</button><button id="btnVolUp">＋</button></div>
  </div>
  <div class="encoder" style="left: 21.5%; top: 16.03%;">
    <span>SELECT</span>
    <button class="dial" id="encSelect" aria-label="Select Game"><i></i></button>
    <div class="detents"><button id="btnPrevGame">−</button><button id="btnNextGame">＋</button></div>
  </div>
  <div class="encoder" style="left: 10.5%; top: 32.85%;">
    <span>PRESETS</span>
    <button class="dial" id="encPresets" aria-label="Demo Song Presets"><i></i></button>
    <div class="detents"><button id="btnPrevSong">−</button><button id="btnNextSong">＋</button></div>
  </div>
  <div class="encoder" style="left: 21.5%; top: 32.85%;">
    <span>ALGORITHM</span>
    <button class="dial" id="encAlgorithm" aria-label="Algorithm Mode"><i></i></button>
    <div class="detents"><button id="btnPrevMode">−</button><button id="btnNextMode">＋</button></div>
  </div>

  <!-- Left Octave / Steer Buttons -->
  <button class="panel-button" id="btnOctMinus" style="left: 6%; top: 41.35%; width: 9%; height: 5.45%;" title="OCT - / Climber Left Arm Down">OCT −</button>
  <button class="panel-button" id="btnOctPlus" style="left: 17%; top: 41.35%; width: 9%; height: 5.45%;" title="OCT + / Climber Right Arm Up">OCT ＋</button>

  <!-- Right Encoders (Knobs 1 to 4) -->
  <div class="encoder" style="left: 61%; top: 16.03%;">
    <span>LPF FILTER<small id="valKnob1">6.5 kHz</small></span>
    <button class="dial" id="knob1" aria-label="Knob 1 LPF"><i></i></button>
    <div class="detents"><button id="knob1-minus">−</button><button id="knob1-plus">＋</button></div>
  </div>
  <div class="encoder" style="left: 71.4%; top: 16.03%;">
    <span>DUB DELAY<small id="valKnob2">280 ms</small></span>
    <button class="dial" id="knob2" aria-label="Knob 2 Delay"><i></i></button>
    <div class="detents"><button id="knob2-minus">−</button><button id="knob2-plus">＋</button></div>
  </div>
  <div class="encoder" style="left: 81.8%; top: 16.03%;">
    <span>FEEDBACK<small id="valKnob3">0%</small></span>
    <button class="dial" id="knob3" aria-label="Knob 3 Reso"><i></i></button>
    <div class="detents"><button id="knob3-minus">−</button><button id="knob3-plus">＋</button></div>
  </div>
  <div class="encoder" style="left: 92.2%; top: 16.03%;">
    <span>WAVE/BEND<small id="valKnob4">WSG 0</small></span>
    <button class="dial" id="knob4" aria-label="Knob 4 WSG"><i></i></button>
    <div class="detents"><button id="knob4-minus">−</button><button id="knob4-plus">＋</button></div>
  </div>

  <!-- Right Panel Function Buttons (Row 1) -->
  <button class="panel-button" id="btnFxScanlines" style="left: 58.2%; top: 27.88%; width: 5.4%; height: 7.69%;" title="FX Scanlines Toggle (K)">FX<small>CRT</small></button>
  <button class="panel-button" id="btnScl" style="left: 64.5%; top: 27.88%; width: 5.4%; height: 7.69%;" title="Scale / Tuning">SCL</button>
  <button class="panel-button" id="btnEnv" style="left: 70.8%; top: 27.88%; width: 5.4%; height: 7.69%;" title="Envelope">ENV</button>
  <button class="panel-button" id="btnLfo" style="left: 77.1%; top: 27.88%; width: 5.4%; height: 7.69%;" title="LFO">LFO</button>
  <button class="panel-button" id="btnGlitch" style="left: 83.4%; top: 27.88%; width: 5.4%; height: 7.69%;" title="RAM Glitch Bender (B)">EDIT<small>GLITCH</small></button>
  <button class="panel-button" id="btnGloTour" style="left: 89.7%; top: 27.88%; width: 5.4%; height: 7.69%;" title="Tour All ROMs (T)">GLO<small>TOUR</small></button>

  <!-- Right Panel Function Buttons (Row 2) -->
  <button class="panel-button coin" id="btnCoin" style="left: 58.2%; top: 37.82%; width: 5.4%; height: 7.69%;" title="Insert Coin (1/C)">HOME<small>COIN</small></button>
  <button class="panel-button start" id="btnStart" style="left: 64.5%; top: 37.82%; width: 5.4%; height: 7.69%;" title="Start 1P (5/Enter)">SAVE<small>START</small></button>
  <button class="panel-button" id="btnArp" style="left: 70.8%; top: 37.82%; width: 5.4%; height: 7.69%;" title="Attract Tour Arp">ARP</button>
  <button class="panel-button" id="btnSeqJuke" style="left: 77.1%; top: 37.82%; width: 5.4%; height: 7.69%;" title="Jukebox Songs">SEQ<small>DEMO</small></button>
  <button class="panel-button play" id="btnQuickPlay" data-button="12" style="left: 83.4%; top: 37.82%; width: 5.4%; height: 7.69%;" title="Quick Play: Coin + Start (Spacebar)">PLAY<small>STOP</small></button>
  <button class="panel-button rewind" id="btnRewind" data-button="13" style="left: 89.7%; top: 37.82%; width: 5.4%; height: 7.69%;" title="Arcade Rewind Time Machine (R)">REC<small>REWIND</small></button>

  <!-- 27-Key Silicone Performance Keyboard -->
  <div id="pianoKeys" class="keyboard" aria-label="27 键演奏与步进键盘"></div>
</div>
</div>

<!-- =========================================================================
     COMPANION TACTICAL DOCK (D-Pad, OLED Telemetry & Jukebox)
     ========================================================================= -->
<div class="companion-deck">
  <!-- Tactile Microswitch D-Pad -->
  <div class="dpad-container">
    <div></div>
    <button class="dpad-btn" id="dpadUp" title="Up / Right Arm Up">▲</button>
    <div></div>
    <button class="dpad-btn" id="dpadLeft" title="Left / Column Left">◀</button>
    <div class="dpad-center"></div>
    <button class="dpad-btn" id="dpadRight" title="Right / Column Right">▶</button>
    <div></div>
    <button class="dpad-btn" id="dpadDown" title="Down / Right Arm Down">▼</button>
    <div></div>
  </div>

  <!-- High-Contrast OLED Telemetry Banner -->
  <div class="status-banner">
    <div class="telemetry-row">
      <span>CORE: <b id="engineStatus">PAC-MAN (60 FPS Z80 + WSG)</b></span>
      <span class="status-tag">ACTIVE</span>
    </div>
    <div style="font-size:0.62rem; color:#8fa5a0;" id="controlsHint">STEER: <b>WASD / ARROWS / D-PAD / SCREEN QUADRANTS</b></div>
    <div style="font-size:0.62rem; color:#8fa5a0;">ACTIONS: <b>1/C</b>=COIN, <b>5/ENTER</b>=START, <b>SPACE</b>=QUICK PLAY, <b>R</b>=REWIND, <b>I/G</b>=IMMORTAL, <b>L/N</b>=SKIP LVL</div>
    <div class="crt-toggle">
      <span>SCANLINES: <b id="crtStatusText">ENABLED</b> (PRESS K)</span>
      <span>AUDIO DSP: <b>24-BIT TAPE ECHO & LPF</b></span>
    </div>
  </div>

  <!-- Demo Songs Jukebox Panel (visible in DEMO mode) -->
  <div class="jukebox-panel" id="jukeboxPanel" style="display:none;">
    <div class="jukebox-header">
      <span>🎵 MULTI-ENGINE FULL DEMO SONGS JUKEBOX</span>
      <span class="juke-status" id="jukeStatus">STOPPED</span>
    </div>
    <div class="song-pills" id="songPills">
      <!-- Populated dynamically -->
    </div>
    <div class="jukebox-controls">
      <button class="juke-btn" id="btnJukePlay">▶ PLAY SONG</button>
      <button class="juke-btn" id="btnJukeStop">⏹ STOP</button>
      <span class="juke-status" id="jukeStep">STEP: <b>01/64</b></span>
      <span class="juke-status" id="jukeBpm">BPM: <b>128</b></span>
      <span class="juke-status" id="jukeTracks">TRACKS: <b>3</b></span>
    </div>
  </div>
</div>

<!-- Collapsible Hardware Manual & Cheatsheet Drawer -->
<details class="manual-drawer">
  <summary class="manual-summary">
    <span>📖 HARDWARE MANUAL, TWIN-STICK GUIDE & KEYBOARD SHORTCUTS</span>
    <span style="font-size:0.65rem; color:#8fa5a0;">CLICK TO EXPAND ▼</span>
  </summary>
  <div class="manual-content">
    <table class="kbd-table">
      <tr>
        <td><kbd>W</kbd> <kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd> or <kbd>Arrows</kbd></td>
        <td>Move Pac-Man / Twin-Stick Climber (W/S=Left Arm, Up/Down=Right Arm)</td>
        <td><kbd>1</kbd> / <kbd>C</kbd></td>
        <td>Insert Coin (adds credit)</td>
      </tr>
      <tr>
        <td><kbd>5</kbd> / <kbd>Enter</kbd> / <kbd>P</kbd></td>
        <td>1-Player Start</td>
        <td><kbd>Space</kbd></td>
        <td><b>Quick Play / Insert Coin & Auto-Start</b></td>
      </tr>
      <tr>
        <td><kbd>Backspace</kbd> / <kbd>R</kbd></td>
        <td>Hold for <b>Arcade Time Machine (Live Rewind)</b></td>
        <td><kbd>Tab</kbd></td>
        <td>Cycle Modes (Arcade, Tour, Demo, Soundboard, Tracker)</td>
      </tr>
      <tr>
        <td><kbd>B</kbd></td>
        <td>Trigger Controlled <b>RAM Circuit-Bending</b></td>
        <td><kbd>K</kbd></td>
        <td>Toggle <b>CRT Scanlines Shader</b></td>
      </tr>
      <tr>
        <td><kbd>Mouse Wheel</kbd></td>
        <td>Scroll over any Rotary Knob to smoothly adjust LPF, Delay, or WSG Wave</td>
        <td><kbd>Screen Quadrants</kbd></td>
        <td>Click or tap Top / Bottom / Left / Right of CRT screen to steer</td>
      </tr>
    </table>
  </div>
</details>

"""

    # Adapt script body
    # 0. Replace sfxNames and playArcadeSfx with Multi-Bank Iconic Arcade SFX Engine
    s_names = script_body.find("const sfxNames = [")
    e_names = script_body.find("// Startup Synth & Power-up Chime")
    if s_names != -1 and e_names != -1:
        script_body = script_body[:s_names] + sfx_gen.get_sfx_banks_js().strip() + "\n\n" + script_body[e_names:]
    else:
        raise ValueError("Could not find sfxNames block in script_body!")

    s_play = script_body.find("function playArcadeSfx(name) {")
    e_play = script_body.find("// -------------------------------------------------------------------------\n// MULTI-ENGINE DEMO SONGS JUKEBOX ENGINE")
    if s_play != -1 and e_play != -1:
        script_body = script_body[:s_play] + sfx_gen.get_play_arcade_sfx_js().strip() + "\n\n" + script_body[e_play:]
    else:
        raise ValueError("Could not find playArcadeSfx block in script_body!")

    # 0b. Replace trackerEngine with Expanded 8-Pattern Chiptune Tracker Engine
    s_tracker = script_body.find("const trackerEngine = {")
    e_tracker = script_body.find("function midiToStr(note) {")
    if s_tracker != -1 and e_tracker != -1:
        script_body = script_body[:s_tracker] + tracker_gen.get_expanded_tracker_patterns_js().strip() + "\n\n" + script_body[e_tracker:]
    else:
        raise ValueError("Could not find trackerEngine block in script_body!")

    script_body = script_body.replace(
        "if (currentMode === 'soundboard' && isDown) {\n    playArcadeSfx(sfxNames[keyIdx]);\n    return;\n  }",
        "if (currentMode === 'soundboard' && isDown) {\n    if (typeof currentStudioTab !== 'undefined' && currentStudioTab === 'speech' && typeof triggerSpeechRom === 'function') {\n      const speechKeys = ['VOX_INTRUDER', 'VOX_COIN', 'VOX_QBERT', 'VOX_SINISTAR', 'VOX_HUNGER', 'VOX_WIZARD', 'VOX_GORF', 'VOX_DRAGON'];\n      triggerSpeechRom(speechKeys[keyIdx % speechKeys.length]);\n      return;\n    }\n    if (typeof triggerSoundboardPad === 'function') triggerSoundboardPad(keyIdx);\n    else playArcadeSfx(sfxNames[keyIdx]);\n    return;\n  }"
    )

    # 1. Update piano keys loop
    old_piano_target = """for (let i = 0; i < 27; i++) {
  const noteInOct = i % 12;
  const isBlack = [1, 3, 6, 8, 10].includes(noteInOct);
  if (!isBlack) {
    const btn = document.createElement('div');
    btn.className = 'key-white';
    btn.dataset.key = i;
    btn.innerHTML = `<span>${noteNames[noteInOct]}</span><div class="sfx-dot" style="background:${getSfxCategoryColor(i)};"></div>`;
    btn.onmousedown = () => onKeyTouch(i, true);
    btn.onmouseup = () => onKeyTouch(i, false);
    btn.onmouseleave = () => onKeyTouch(i, false);
    btn.ontouchstart = (e) => { e.preventDefault(); onKeyTouch(i, true); };
    btn.ontouchend = (e) => { e.preventDefault(); onKeyTouch(i, false); };
    pianoContainer.appendChild(btn);
  }
}

let currWhite = 0;
for (let i = 0; i < 27; i++) {
  const noteInOct = i % 12;
  const isBlack = [1, 3, 6, 8, 10].includes(noteInOct);
  if (isBlack) {
    const btn = document.createElement('div');
    btn.className = 'key-black';
    btn.dataset.key = i;
    btn.innerHTML = `<span>${noteNames[noteInOct]}</span><div class="sfx-dot" style="background:${getSfxCategoryColor(i)};"></div>`;
    btn.style.left = `calc(${currWhite * 6.25}% - 2.1%)`;
    btn.onmousedown = () => onKeyTouch(i, true);
    btn.onmouseup = () => onKeyTouch(i, false);
    btn.onmouseleave = () => onKeyTouch(i, false);
    btn.ontouchstart = (e) => { e.preventDefault(); onKeyTouch(i, true); };
    btn.ontouchend = (e) => { e.preventDefault(); onKeyTouch(i, false); };
    pianoContainer.appendChild(btn);
  } else {
    currWhite++;
  }
}"""

    new_piano_replacement = """const whites = [0, 2, 4, 6, 7, 9, 11, 12, 14, 16, 18, 19, 21, 23, 24, 26];
const edits = [1, 3, 5, 8, 10, 13, 15, 17, 20, 22, 25];
const fmOps = ['OP1', 'OP2', 'OP3', 'OP4', 'OP5', 'OP6', 'PITCH', 'GLOBAL', 'MONO', 'POLY', 'ARP'];

if (pianoContainer) {
  pianoContainer.innerHTML = '';
  for (let i = 0; i < 27; i++) {
    const whiteIdx = whites.indexOf(i);
    const btn = document.createElement('button');
    btn.dataset.key = i;
    if (whiteIdx >= 0) {
      btn.className = 'piano-key white key-white';
      const center = whiteIdx + 0.5;
      btn.style.left = (center * 100 / 16) + '%';
      btn.innerHTML = '<i></i><span>' + String(whiteIdx + 1).padStart(2, '0') + '<br>' + noteNames[i % 12] + '</span>';
    } else {
      btn.className = 'piano-key black key-black';
      const center = whites.filter(k => k < i).length;
      btn.style.left = (center * 100 / 16) + '%';
      const editIdx = edits.indexOf(i);
      btn.innerHTML = '<i></i><span>' + (fmOps[editIdx] || '') + '<br>' + noteNames[i % 12] + '</span>';
    }

    btn.onmousedown = () => onKeyTouch(i, true);
    btn.onmouseup = () => onKeyTouch(i, false);
    btn.onmouseleave = () => onKeyTouch(i, false);
    btn.ontouchstart = (e) => { e.preventDefault(); onKeyTouch(i, true); };
    btn.ontouchend = (e) => { e.preventDefault(); onKeyTouch(i, false); };
    pianoContainer.appendChild(btn);
  }
}"""

    script_body = script_body.replace(old_piano_target, new_piano_replacement)

    # 2. Update updateKeyLabels
    old_update_labels = """function updateKeyLabels() {
  document.querySelectorAll('.key-white, .key-black').forEach(el => {
    const k = parseInt(el.dataset.key);
    const noteInOct = k % 12;
    const catColor = getSfxCategoryColor(k);
    if (currentMode === 'soundboard') {
      el.innerHTML = `<span style="font-size:0.5rem;color:${catColor};font-weight:900;letter-spacing:0.3px;">${sfxNames[k]}</span><div class="sfx-dot" style="background:${catColor};box-shadow:0 0 6px ${catColor};"></div>`;
    } else {
      el.innerHTML = `<span>${noteNames[noteInOct]}</span><div class="sfx-dot" style="background:${catColor};"></div>`;
    }
  });
}"""

    new_update_labels = """function updateKeyLabels() {
  const speechShortNames = ['INTRUDR', 'IN-COIN', 'Q*BERT', 'SINISTR', 'HUNGER', 'WIZARD', 'GORF', 'DRAGON'];
  document.querySelectorAll('.piano-key, .key-white, .key-black').forEach(el => {
    const k = parseInt(el.dataset.key);
    const whiteIdx = whites.indexOf(k);
    const editIdx = edits.indexOf(k);
    const note = noteNames[k % 12];
    const catColor = getSfxCategoryColor(k);
    if (typeof currentStudioTab !== 'undefined' && currentStudioTab === 'speech') {
      const spName = speechShortNames[k % speechShortNames.length];
      el.innerHTML = '<i></i><span style="font-size:0.55cqw;color:#a55eea;font-weight:900;">' + spName + '</span>';
    } else if (currentMode === 'soundboard') {
      el.innerHTML = '<i></i><span style="font-size:0.55cqw;color:' + catColor + ';font-weight:900;">' + sfxNames[k] + '</span>';
    } else {
      if (whiteIdx >= 0) {
        el.innerHTML = '<i></i><span>' + String(whiteIdx + 1).padStart(2, '0') + '<br>' + note + '</span>';
      } else {
        el.innerHTML = '<i></i><span>' + (fmOps[editIdx] || '') + '<br>' + note + '</span>';
      }
    }
  });
}"""

    script_body = script_body.replace(old_update_labels, new_update_labels)

    # 3. Update onKeyTouch to also toggle .lit and .held
    script_body = script_body.replace(
        "if (el) el.classList.toggle('active', isDown);",
        "if (el) { el.classList.toggle('active', isDown); el.classList.toggle('lit', isDown); el.classList.toggle('held', isDown); }"
    )

    # Upgraded High-Fidelity Graphics Engines
    old_arcade_frame = """function renderArcadeFrame() {
  arcadeBuf.fill(0xff000000);
  
  // Tiles: Bottom 2 rows
  for (let i = 0x00; i <= 0x03f; i++) {
    drawTile(ram[i], ram[i + 0x400], (29 - (i % 0x20)) * 8, (i >= 0x20 ? 35 : 34) * 8);
  }
  // Tiles: Middle section
  for (let i = 0x40; i <= 0x3bf; i++) {
    drawTile(ram[i], ram[i + 0x400], (29 - Math.floor(i / 0x20)) * 8, (2 + (i % 0x20)) * 8);
  }
  // Tiles: Top 2 rows
  for (let i = 0x3c0; i <= 0x3ff; i++) {
    drawTile(ram[i], ram[i + 0x400], (29 - (i % 0x20)) * 8, (i >= 0x3e0 ? 1 : 0) * 8);
  }

  // 8 Hardware Sprites
  for (let s = 7; s >= 0; s--) {
    const sx = 239 - spritePos[s * 2];
    const sy = 272 - spritePos[s * 2 + 1];
    const info = ram[0x0ff0 + s * 2];
    const pal = ram[0x0ff0 + s * 2 + 1];
    drawSprite(info >> 2, pal, sx, sy, (info >> 1) & 1, info & 1);
  }

  // 5:6 Downsampling (288 -> 240) + Scanline Filter
  buf32.fill(0xff08090c);
  for (let outY = 0; outY < 240; outY++) {
    const inY = Math.floor(outY * 6 / 5);
    const inRow = inY * 224;
    const outRow = outY * 240 + 8;
    const scanDim = (crtScanlines && (outY % 2 === 1)) ? 0.72 : 1.0;
    
    for (let outX = 0; outX < 224; outX++) {
      const pix = arcadeBuf[inRow + outX];
      if (scanDim < 1.0) {
        const r = Math.floor((pix & 0xff) * scanDim);
        const g = Math.floor(((pix >> 8) & 0xff) * scanDim);
        const b = Math.floor(((pix >> 16) & 0xff) * scanDim);
        buf32[outRow + outX] = 0xff000000 | (b << 16) | (g << 8) | r;
      } else {
        buf32[outRow + outX] = pix;
      }
    }
  }

  ctx.putImageData(imgData, 0, 0);
}"""

    new_arcade_frame = """// High-Fidelity Arcade Display Pipeline
const osCanvas = (typeof document !== 'undefined' && document.createElement) ? document.createElement('canvas') : null;
if (osCanvas) {
  osCanvas.width = 224;
  osCanvas.height = 288;
}
const osCtx = (osCanvas && osCanvas.getContext) ? osCanvas.getContext('2d') : null;
const osImgData = (osCtx && osCtx.createImageData) ? osCtx.createImageData(224, 288) : null;
const osBuf32 = osImgData ? new Uint32Array(osImgData.data.buffer) : null;

function renderArcadeFrame() {
  arcadeBuf.fill(0xff000000);
  
  // Tiles: Bottom 2 rows
  for (let i = 0x00; i <= 0x03f; i++) {
    drawTile(ram[i], ram[i + 0x400], (29 - (i % 0x20)) * 8, (i >= 0x20 ? 35 : 34) * 8);
  }
  // Tiles: Middle section
  for (let i = 0x40; i <= 0x3bf; i++) {
    drawTile(ram[i], ram[i + 0x400], (29 - Math.floor(i / 0x20)) * 8, (2 + (i % 0x20)) * 8);
  }
  // Tiles: Top 2 rows
  for (let i = 0x3c0; i <= 0x3ff; i++) {
    drawTile(ram[i], ram[i + 0x400], (29 - (i % 0x20)) * 8, (i >= 0x3e0 ? 1 : 0) * 8);
  }

  // 8 Hardware Sprites
  for (let s = 7; s >= 0; s--) {
    const sx = 239 - spritePos[s * 2];
    const sy = 272 - spritePos[s * 2 + 1];
    const info = ram[0x0ff0 + s * 2];
    const pal = ram[0x0ff0 + s * 2 + 1];
    drawSprite(info >> 2, pal, sx, sy, (info >> 1) & 1, info & 1);
  }

  // High-Fidelity Rendering:
  // In real browser, use hardware bilinear anti-aliased scaling
  // so NO scanlines are dropped, maze walls and text stay razor-sharp!
  if (osCtx && osBuf32 && ctx && ctx.drawImage) {
    osBuf32.set(arcadeBuf);
    osCtx.putImageData(osImgData, 0, 0);
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, 240, 240);
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(osCanvas, 0, 0, 224, 288, 8, 0, 224, 240);
  } else {
    // Fallback for headless environments
    buf32.fill(0xff08090c);
    for (let outY = 0; outY < 240; outY++) {
      const inY = Math.floor(outY * 6 / 5);
      const inRow = inY * 224;
      const outRow = outY * 240 + 8;
      for (let outX = 0; outX < 224; outX++) {
        buf32[outRow + outX] = arcadeBuf[inRow + outX];
      }
    }
    if (ctx && ctx.putImageData) ctx.putImageData(imgData, 0, 0);
  }
}"""
    script_body = script_body.replace(old_arcade_frame, new_arcade_frame)

    # Replace old tour renderers (from renderCrazyClimber to renderTourDemo)
    idx_cc = script_body.find("function renderCrazyClimber()")
    idx_td = script_body.find("function renderTourDemo()")
    if idx_cc != -1 and idx_td != -1:
        new_games_block = """// =========================================================================
// 8 AUTHENTIC PLAYABLE ARCADE ENGINES (High-Resolution CRT Graphics & Physics)
// Pac-Man, Crazy Climber, Galaga, Donkey Kong, Frogger, Asteroids, Tempest, Gyruss
// Integrated Autonomous Attract AI & High-Density Arcade Pixel Art / Vector CRT
// =========================================================================
// 8 AUTHENTIC PLAYABLE ARCADE ENGINES (High-Resolution CRT Graphics & Physics)
// Pac-Man, Crazy Climber, Galaga, Donkey Kong, Frogger, Asteroids, Tempest, Gyruss
// Integrated Autonomous Attract AI & High-Density Arcade Pixel Art / Vector CRT
// =========================================================================
// 8 AUTHENTIC PLAYABLE ARCADE ENGINES (High-Resolution CRT Graphics & Physics)
// Pac-Man, Crazy Climber, Galaga, Donkey Kong, Frogger, Asteroids, Tempest, Gyruss
// Integrated Autonomous Attract AI & High-Density Arcade Pixel Art / Vector CRT
// =========================================================================
// 8 AUTHENTIC PLAYABLE ARCADE ENGINES (High-Resolution CRT Graphics & Physics)
// Pac-Man, Crazy Climber, Galaga, Donkey Kong, Frogger, Asteroids, Tempest, Gyruss
// Integrated Autonomous Attract AI & High-Density Arcade Pixel Art / Vector CRT
// =========================================================================

// Global Keyboard Tracking for Smooth Multi-Key Response
var arcadeKeysDown = (typeof arcadeKeysDown !== 'undefined') ? arcadeKeysDown : {};
var dpadActiveDir = (typeof dpadActiveDir !== 'undefined') ? dpadActiveDir : null;

// -------------------------------------------------------------------------
// 0. CRAZY CLIMBER (1980 NICHIBUTSU Z80): FULLY PLAYABLE ARCADE ENGINE
// -------------------------------------------------------------------------
if (typeof climberState !== 'undefined') {
  climberState.floor = 1;
  climberState.leftArm = 'down';
  climberState.rightArm = 'down';
  climberState.col = 1;
  climberState.potY = -20;
  climberState.potCol = 2;
  climberState.dumbbells = [];
  climberState.score = 0;
  climberState.highScore = 18500;
  climberState.lives = 3;
  climberState.gameOver = false;
  climberState.hanging = false;
  climberState.cleared = false;
  climberState.winTimer = 0;
  climberState.animTick = 0;
  climberState.stepCombo = 0;
  climberState.lastStepArm = null;
}

function initCrazyClimberGame() {
  climberState.floor = 1;
  climberState.leftArm = 'down';
  climberState.rightArm = 'down';
  climberState.col = 1;
  climberState.potY = -20;
  climberState.potCol = 2;
  climberState.dumbbells = [];
  climberState.score = 0;
  climberState.lives = (typeof arcadeImmortalMode !== 'undefined' && arcadeImmortalMode) ? 99 : 3;
  climberState.gameOver = false;
  climberState.hanging = false;
  climberState.cleared = false;
  climberState.winTimer = 0;
  climberState.animTick = 0;
  climberState.stepCombo = 0;
  climberState.lastStepArm = null;
  playArcadeSfx('CLIMB-STEP');
}

function climberStep(arm, dir) {
  initAudio();
  if (climberState.cleared || climberState.gameOver) return;
  const prevArmState = (arm === 'left') ? climberState.leftArm : climberState.rightArm;
  if (arm === 'left') climberState.leftArm = dir;
  else climberState.rightArm = dir;

  // Authentic Twin-Stick alternating pull:
  // Climber advances when left arm is up while right arm is down, or vice versa, alternating!
  if (climberState.leftArm !== climberState.rightArm && dir !== prevArmState) {
    climberState.floor++;
    climberState.score += 50;
    if (climberState.score > climberState.highScore) climberState.highScore = climberState.score;
    climberState.hanging = false;
    playArcadeSfx('CLIMB-STEP');

    // Roof Helicopter Rescue at Floor 50
    if (climberState.floor >= 50 && !climberState.cleared) {
      climberState.cleared = true;
      climberState.winTimer = 180;
      climberState.score += 10000;
      if (climberState.score > climberState.highScore) climberState.highScore = climberState.score;
      playArcadeSfx('CLIMB-WIN');
      if (typeof speakPhrase === 'function') speakPhrase('STEP IN');
    }
  }
}

function climberMove(dir) {
  initAudio();
  if (climberState.cleared || climberState.hanging) return;
  if (dir === 'left') climberState.col = Math.max(0, climberState.col - 1);
  else if (dir === 'right') climberState.col = Math.min(3, climberState.col + 1);
}

function updateCrazyClimberGame() {
  if (climberState.gameOver) {
    if (arcadeKeysDown['1'] || arcadeKeysDown['5'] || arcadeKeysDown[' '] || arcadeKeysDown['enter'] || arcadeKeysDown['r']) {
      initCrazyClimberGame();
    }
    return;
  }

  climberState.animTick++;
  const tick = climberState.animTick;

  // Authentic Nichibutsu Mancini Swing Strut BGM ("Baby Elephant Walk" / "Pink Panther")
  if (!climberState.gameOver && climberState.floor < 50) {
    climberState.bgmTick = (climberState.bgmTick || 0) + 1;
    if (climberState.bgmTick % 14 === 0) {
      climberState.bgmStep = ((climberState.bgmStep || 0) + 1) % 28;
      playArcadeSfx('CLIMB-BGM');
    }
  }

  // Autonomous Attract Tour AI
  if (currentMode === 'tour') {
    if (tick % 24 < 12) climberStep('left', 'up');
    else climberStep('right', 'up');
    if (climberState.potCol === climberState.col && climberState.potY > 50 && climberState.potY < 150) {
      climberState.col = (climberState.col + 1) % 4;
    }
  }

  // Falling Terracotta Flower Pot
  climberState.potY += 2.4;
  if (climberState.potY > 240) {
    climberState.potY = -15;
    climberState.potCol = Math.floor(Math.random() * 4);
  }

  const potY = climberState.potY;
  // Check Flowerpot Hit Climber
  if (climberState.potCol === climberState.col && potY > 110 && potY < 155 && currentMode !== 'tour') {
    climberState.potY = -20;
    climberState.floor = Math.max(1, climberState.floor - 2);
    playArcadeSfx('CLIMB-POT');
    playArcadeSfx('CLIMB-FALL');
    if (typeof speakPhrase === 'function') speakPhrase('OUCH');
    if (!arcadeImmortalMode) {
      climberState.lives--;
      if (climberState.lives <= 0) {
        climberState.gameOver = true;
        playArcadeSfx('DK-GAMEOVER');
      }
    }
  }

  // Window Slam Hazard: if hands are raised when window closes, climber slips and hangs by one hand
  const currentWindowOpen = ((climberState.floor + climberState.col + (tick >> 6)) % 3 === 0);
  if (!currentWindowOpen && (climberState.leftArm === 'up' || climberState.rightArm === 'up') && tick % 140 === 0 && currentMode !== 'tour') {
    climberState.hanging = true;
    playArcadeSfx('CLIMB-SLIP');
  }

  // King Gorilla Ape on Left Pilaster (punches at columns 0 and 1)
  const kongY = 65 + Math.sin(tick * 0.08) * 12;
  const kongArmUp = (tick % 40 < 20);
  if (climberState.col <= 1 && Math.abs(kongY - 130) < 25 && kongArmUp && tick % 70 === 0 && currentMode !== 'tour') {
    playArcadeSfx('CLIMB-KONG');
    playArcadeSfx('DK-ROAR');
    climberState.floor = Math.max(1, climberState.floor - 3);
  }

  if (climberState.cleared) {
    if (climberState.winTimer > 0) {
      climberState.winTimer--;
    } else {
      climberState.building = (climberState.building || 1) + 1;
      climberState.floor = 1;
      climberState.cleared = false;
      climberState.hanging = false;
      climberState.potY = -20;
      playArcadeSfx('CLIMB-STEP');
    }
  }
}

function renderCrazyClimber() {
  if (currentMode !== 'rewind' && !isRewinding) updateCrazyClimberGame();
  const tick = climberState.animTick;

  // Dusk Sky gradient
  const skyGrad = ctx.createLinearGradient(0, 0, 0, 240);
  skyGrad.addColorStop(0, '#0c1020');
  skyGrad.addColorStop(1, '#1e272e');
  ctx.fillStyle = skyGrad;
  ctx.fillRect(0, 0, 240, 240);

  // Distant City Skyline with lit windows
  ctx.fillStyle = '#0a0d16';
  ctx.fillRect(4, 180, 22, 60);
  ctx.fillRect(14, 160, 10, 80);
  ctx.fillRect(218, 175, 18, 65);
  ctx.fillStyle = '#f1c40f';
  ctx.fillRect(8, 190, 2, 3);
  ctx.fillRect(16, 170, 2, 3);
  ctx.fillRect(224, 185, 2, 3);

  // Skyscraper Main Brick Facade (x: 26 to 214)
  const bldgGrad = ctx.createLinearGradient(26, 0, 214, 0);
  bldgGrad.addColorStop(0, '#8c532b');
  bldgGrad.addColorStop(0.5, '#a05c30');
  bldgGrad.addColorStop(1, '#6d3e1d');
  ctx.fillStyle = bldgGrad;
  ctx.fillRect(26, 0, 188, 240);

  // Left & Right Limestone Art-Deco Pilasters
  ctx.fillStyle = '#dcdde1';
  ctx.fillRect(26, 0, 10, 240);
  ctx.fillRect(204, 0, 10, 240);
  ctx.fillStyle = '#718093';
  ctx.fillRect(35, 0, 2, 240);
  ctx.fillRect(203, 0, 2, 240);

  // Horizontal Stone Floor Ledges
  for (let fl = 0; fl < 7; fl++) {
    const ly = (fl * 38 + (climberState.floor * 2) % 38) % 240;
    ctx.fillStyle = '#2f3542';
    ctx.fillRect(26, ly, 188, 3);
    ctx.fillStyle = '#f1f2f6';
    ctx.fillRect(26, ly + 3, 188, 1);
  }

  // 4 Columns of Authentic Double-Hung Windows
  const windowCols = [44, 84, 124, 164];
  for (let row = -1; row < 7; row++) {
    const wy = (row * 38 + (climberState.floor * 2) % 38);
    if (wy < -35 || wy > 240) continue;

    for (let c = 0; c < 4; c++) {
      const wx = windowCols[c];
      const isOpen = (row + c + (tick >> 6)) % 3 === 0;

      // Stone sill & frame
      ctx.fillStyle = '#1e272e';
      ctx.fillRect(wx - 2, wy - 2, 32, 30);
      ctx.fillStyle = '#dfe4ea';
      ctx.fillRect(wx - 3, wy + 26, 34, 3);
      ctx.fillStyle = '#2f3542';
      ctx.fillRect(wx - 3, wy + 29, 34, 1);

      if (isOpen) {
        ctx.fillStyle = '#05070a';
        ctx.fillRect(wx, wy, 28, 26);
        ctx.fillStyle = '#e58e26'; // Interior warm lamp glow
        ctx.fillRect(wx + 8, wy + 4, 12, 10);
        ctx.fillStyle = '#f8c291'; // Fluttering curtain
        ctx.fillRect(wx + 2, wy, 5, 20);
      } else {
        ctx.fillStyle = '#1b76bc';
        ctx.fillRect(wx, wy, 28, 26);
        ctx.fillStyle = '#4bcffa';
        ctx.fillRect(wx + 2, wy + 2, 24, 10);
        ctx.fillRect(wx + 2, wy + 14, 24, 10);
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(wx + 4, wy + 3, 18, 2);
        ctx.fillRect(wx + 2, wy + 12, 24, 2);
        ctx.fillRect(wx + 13, wy + 2, 2, 22);
      }
    }
  }

  // King Kong / Giant Ape on Left Girder (x: 4 to 34)
  const kongY = 65 + Math.sin(tick * 0.08) * 12;
  const kongArmUp = (tick % 40 < 20);
  ctx.save();
  ctx.translate(2, kongY);
  ctx.fillStyle = '#2f3542';
  ctx.fillRect(6, 12, 24, 28);
  ctx.fillStyle = '#1e272e';
  ctx.fillRect(8, 14, 20, 24);
  ctx.fillStyle = '#2f3542';
  ctx.fillRect(10, 0, 18, 14);
  ctx.fillStyle = '#e74c3c';
  ctx.fillRect(14, 8, 10, 5);
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(15, 8, 2, 2); ctx.fillRect(21, 8, 2, 2);
  ctx.fillStyle = '#f1c40f';
  ctx.fillRect(13, 3, 3, 3); ctx.fillRect(20, 3, 3, 3);
  ctx.fillStyle = '#57606f';
  ctx.fillRect(kongArmUp ? 0 : 2, kongArmUp ? 2 : 24, 8, 10);
  ctx.fillRect(kongArmUp ? 24 : 26, kongArmUp ? 24 : 2, 8, 10);
  ctx.restore();

  // Falling Terracotta Flower Pot
  const potX = windowCols[climberState.potCol] + 8;
  const potY = climberState.potY;
  if (potY >= 0 && potY < 235) {
    ctx.fillStyle = '#e84393';
    ctx.beginPath();
    ctx.arc(potX + 6, potY - 3, 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#2ecc71';
    ctx.fillRect(potX + 1, potY - 2, 10, 3);
    ctx.fillStyle = '#e17055';
    ctx.fillRect(potX, potY, 12, 3);
    ctx.fillRect(potX + 2, potY + 3, 8, 8);
  }

  // The Climber Character (16x16 Pixel Art)
  const cx = windowCols[climberState.col] + 3;
  const cy = 130;
  const leftArmUp = (climberState.leftArm === 'up');
  const rightArmUp = (climberState.rightArm === 'up');

  // Shadow
  ctx.fillStyle = 'rgba(0,0,0,0.45)';
  ctx.fillRect(cx - 2, cy + 32, 26, 4);

  // Boots
  ctx.fillStyle = '#795548';
  ctx.fillRect(cx + 2, cy + 28, 7, 4);
  ctx.fillRect(cx + 13, cy + 28, 7, 4);

  // Blue Overalls
  ctx.fillStyle = '#1e3799';
  ctx.fillRect(cx + 4, cy + 18, 14, 11);
  ctx.fillStyle = '#4a69bd';
  ctx.fillRect(cx + 5, cy + 13, 3, 7);
  ctx.fillRect(cx + 14, cy + 13, 3, 7);
  ctx.fillStyle = '#f1c40f'; // Brass buttons
  ctx.fillRect(cx + 5, cy + 19, 2, 2);
  ctx.fillRect(cx + 15, cy + 19, 2, 2);

  // Red Shirt
  ctx.fillStyle = '#eb2f06';
  ctx.fillRect(cx + 3, cy + 12, 16, 7);

  // Alternating Arms or Hanging
  if (climberState.hanging) {
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(cx - 3, cy - 6, 5, 16);
    ctx.fillStyle = '#f8c291';
    ctx.fillRect(cx - 4, cy - 10, 7, 5);
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(cx + 20, cy + 16, 5, 14);
    ctx.fillStyle = '#f8c291';
    ctx.fillRect(cx + 19, cy + 28, 7, 5);
  } else {
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(cx - 3, leftArmUp ? cy - 4 : cy + 12, 5, 14);
    ctx.fillStyle = '#f8c291'; // White/Peach glove
    ctx.fillRect(cx - 4, leftArmUp ? cy - 8 : cy + 24, 7, 5);

    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(cx + 20, rightArmUp ? cy - 4 : cy + 12, 5, 14);
    ctx.fillStyle = '#f8c291';
    ctx.fillRect(cx + 19, rightArmUp ? cy - 8 : cy + 24, 7, 5);
  }

  // Head & Cap
  ctx.fillStyle = '#f8c291';
  ctx.fillRect(cx + 6, cy + 2, 10, 10);
  ctx.fillStyle = '#eb2f06';
  ctx.fillRect(cx + 4, cy - 2, 14, 5); // Red Cap
  ctx.fillRect(cx + 2, cy + 1, 5, 2);   // Visor
  ctx.fillStyle = '#000000';
  ctx.fillRect(cx + 7, cy + 5, 2, 2); // Eye

  // Floor 50 Rescue Chopper
  if (climberState.floor >= 50) {
    const chopX = 120, chopY = 25;
    ctx.fillStyle = '#f1c40f'; // Yellow chopper body
    ctx.fillRect(chopX - 16, chopY, 32, 12);
    ctx.fillStyle = '#0abde3'; // Cockpit glass
    ctx.fillRect(chopX - 12, chopY + 2, 10, 8);
    // Rotor blades spinning
    ctx.fillStyle = (tick % 4 < 2) ? '#ffffff' : '#718093';
    ctx.fillRect(chopX - 28, chopY - 4, 56, 2);
    // Rescue Rope Ladder
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 1.0;
    ctx.beginPath();
    ctx.moveTo(chopX, chopY + 12); ctx.lineTo(chopX, cy - 8);
    ctx.stroke();
  }

  // Header & HUD
  ctx.fillStyle = '#f1c40f';
  ctx.font = 'bold 8px monospace';
  ctx.fillText(`1UP: ${climberState.score}`, 10, 15);
  ctx.fillStyle = '#ff6b81';
  ctx.fillText(`LIVES: ${arcadeImmortalMode ? '∞' : climberState.lives}`, 110, 15);
  ctx.fillStyle = '#00d2d3';
  ctx.fillText(`${climberState.floor}F`, 198, 15);

  ctx.fillStyle = 'rgba(6, 9, 14, 0.88)';
  ctx.fillRect(0, 222, 240, 18);
  ctx.fillStyle = '#00e5ff';
  ctx.font = 'bold 8px monospace';
  ctx.fillText(`TWIN-STICK: L[${climberState.leftArm.toUpperCase()}] R[${climberState.rightArm.toUpperCase()}]  COL:${climberState.col + 1}/4`, 14, 234);

  // Authentic Arcade Game Over Overlay
  if (climberState.gameOver) {
    ctx.fillStyle = 'rgba(5, 7, 10, 0.85)';
    ctx.fillRect(25, 95, 190, 52);
    ctx.strokeStyle = '#eb2f06';
    ctx.lineWidth = 2;
    if (ctx.strokeRect) ctx.strokeRect(25, 95, 190, 52);

    ctx.fillStyle = '#eb2f06';
    ctx.font = 'bold 15px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('GAME OVER', 120, 118);

    if ((tick >> 4) % 2 === 0) {
      ctx.fillStyle = '#f1c40f';
      ctx.font = 'bold 7px monospace';
      ctx.fillText('PRESS 1P START OR SPACE', 120, 136);
    }
    ctx.textAlign = 'start';
  }

  if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
}

// -------------------------------------------------------------------------
// 1. GALAGA (1981 NAMCO DUAL Z80): FULLY PLAYABLE ARCADE ENGINE
// -------------------------------------------------------------------------
const galagaGame = {
  active: false,
  gameOver: false,
  shipX: 120,
  shipSpeed: 2.8,
  moveDir: 0,
  lasers: [],
  aliens: [],
  bombs: [],
  explosions: [],
  scorePops: [],
  score: 0,
  highScore: 20000,
  lives: 3,
  stage: 1,
  tick: 0,
  dualFighter: false,
  isCapturing: false,
  captureAngle: 0,
  captureShipY: 220,
  tractorBeam: { active: false, x: 120, y: 75, height: 0, maxH: 140, state: 'off', boss: null, timer: 0 },
  capturedShip: null,
  isChallengingStage: false,
  hitsCount: 0,
  totalChallengingAliens: 40
};

function initGalagaGame() {
  galagaGame.active = true;
  galagaGame.gameOver = false;
  galagaGame.shipX = 120;
  galagaGame.moveDir = 0;
  galagaGame.lasers = [];
  galagaGame.bombs = [];
  galagaGame.explosions = [];
  galagaGame.scorePops = [];
  galagaGame.score = 0;
  galagaGame.lives = (typeof arcadeImmortalMode !== 'undefined' && arcadeImmortalMode) ? 99 : 3;
  galagaGame.stage = 1;
  galagaGame.tick = 0;
  galagaGame.dualFighter = false;
  galagaGame.isCapturing = false;
  galagaGame.captureAngle = 0;
  galagaGame.captureShipY = 220;
  galagaGame.tractorBeam = { active: false, x: 120, y: 75, height: 0, maxH: 140, state: 'off', boss: null, timer: 0 };
  galagaGame.capturedShip = null;
  galagaGame.isChallengingStage = false;
  galagaGame.hitsCount = 0;
  spawnGalagaFleet();
  playArcadeSfx('GALAGA-INTRO');
}

function spawnGalagaFleet() {
  galagaGame.aliens = [];
  // Row 0: Boss Galaga (4 green/cyan commanders)
  for (let c = 0; c < 4; c++) {
    galagaGame.aliens.push({
      x: 64 + c * 36,
      y: 42,
      homeX: 64 + c * 36,
      homeY: 42,
      type: 'boss',
      state: 'grid',
      diveTick: 0,
      hp: 2,
      angle: 0
    });
  }
  // Rows 1 & 2: Red Goei (8 per row = 16 butterflies)
  for (let r = 1; r <= 2; r++) {
    for (let c = 0; c < 8; c++) {
      galagaGame.aliens.push({
        x: 42 + c * 22,
        y: 42 + r * 16,
        homeX: 42 + c * 22,
        homeY: 42 + r * 16,
        type: 'red',
        state: 'grid',
        diveTick: 0,
        hp: 1,
        angle: 0
      });
    }
  }
  // Rows 3 & 4: Yellow Zako (10 per row = 20 bees)
  for (let r = 3; r <= 4; r++) {
    for (let c = 0; c < 10; c++) {
      galagaGame.aliens.push({
        x: 32 + c * 20,
        y: 42 + r * 15,
        homeX: 32 + c * 20,
        homeY: 42 + r * 15,
        type: 'yellow',
        state: 'grid',
        diveTick: 0,
        hp: 1,
        angle: 0
      });
    }
  }
}

function galagaFire() {
  initAudio();
  if (galagaGame.isCapturing) return;
  if (galagaGame.lasers.length < (galagaGame.dualFighter ? 8 : 4)) {
    if (galagaGame.dualFighter) {
      galagaGame.lasers.push({ x: galagaGame.shipX - 10, y: 214, vy: -6.0 });
      galagaGame.lasers.push({ x: galagaGame.shipX - 4,  y: 214, vy: -6.0 });
      galagaGame.lasers.push({ x: galagaGame.shipX + 4,  y: 214, vy: -6.0 });
      galagaGame.lasers.push({ x: galagaGame.shipX + 10, y: 214, vy: -6.0 });
    } else {
      galagaGame.lasers.push({ x: galagaGame.shipX - 4, y: 214, vy: -6.0 });
      galagaGame.lasers.push({ x: galagaGame.shipX + 4, y: 214, vy: -6.0 });
    }
    playArcadeSfx('GALAGA-FIRE');
  }
}

function updateGalagaGame() {
  if (galagaGame.gameOver) {
    if (arcadeKeysDown['1'] || arcadeKeysDown['5'] || arcadeKeysDown[' '] || arcadeKeysDown['enter'] || arcadeKeysDown['r']) {
      initGalagaGame();
    }
    return;
  }

  galagaGame.tick++;
  const g = galagaGame;

  // Authentic Namco WSG Space Fleet & Challenging Stage BGM
  if (!g.gameOver && !g.isCapturing) {
    g.bgmTick = (g.bgmTick || 0) + 1;
    if (g.isChallengingStage) {
      if (g.bgmTick % 8 === 0) {
        g.bgmStep = ((g.bgmStep || 0) + 1) % 28;
        playArcadeSfx('GALAGA-CHALLENGE-BGM');
      }
    } else {
      if (g.bgmTick % 24 === 0) {
        g.bgmStep = ((g.bgmStep || 0) + 1) % 8;
        playArcadeSfx('GALAGA-BGM');
      }
    }
  }

  // Active Key Steer
  if (!g.isCapturing) {
    if (currentMode === 'tour') {
      let targetX = 120 + Math.sin(g.tick * 0.04) * 55;
      const diving = g.aliens.find(a => a.state === 'dive' || a.state === 'tractor');
      if (diving) targetX = diving.x;
      if (g.shipX < targetX - 3) g.shipX += 2.4;
      else if (g.shipX > targetX + 3) g.shipX -= 2.4;
      if (g.tick % 18 === 0) galagaFire();
    } else {
      if (arcadeKeysDown['a'] || arcadeKeysDown['arrowleft'] || (typeof dpadActiveDir !== 'undefined' && dpadActiveDir === 'left')) g.moveDir = -1;
      else if (arcadeKeysDown['d'] || arcadeKeysDown['arrowright'] || (typeof dpadActiveDir !== 'undefined' && dpadActiveDir === 'right')) g.moveDir = 1;
      else if (typeof dpadActiveDir === 'undefined' || !dpadActiveDir) g.moveDir = 0;
      g.shipX += g.moveDir * g.shipSpeed;
    }
    const maxBound = g.dualFighter ? 216 : 224;
    const minBound = g.dualFighter ? 24 : 16;
    g.shipX = Math.max(minBound, Math.min(maxBound, g.shipX));
  } else {
    // Player is being captured by tractor beam!
    g.captureAngle += 0.25;
    g.captureShipY -= 1.8;
    if (g.tractorBeam.boss && g.captureShipY <= g.tractorBeam.boss.y + 12) {
      // Reached Boss Galaga: dock as captive ship!
      g.capturedShip = { boss: g.tractorBeam.boss, x: g.tractorBeam.boss.x + 16, y: g.tractorBeam.boss.y };
      g.tractorBeam.active = false;
      g.tractorBeam.state = 'off';
      if (g.tractorBeam.boss) g.tractorBeam.boss.state = 'return';
      g.isCapturing = false;
      g.shipX = 120;
      g.captureShipY = 220;
      g.captureAngle = 0;
      if (!arcadeImmortalMode) {
        g.lives--;
        if (g.lives <= 0) {
          g.gameOver = true;
          playArcadeSfx('DK-GAMEOVER');
        }
      }
    }
  }

  // Lasers
  for (let i = g.lasers.length - 1; i >= 0; i--) {
    const l = g.lasers[i];
    l.y += l.vy;
    if (l.y < 12) {
      g.lasers.splice(i, 1);
      continue;
    }
    // Hit alien
    for (let a = g.aliens.length - 1; a >= 0; a--) {
      const al = g.aliens[a];
      if (Math.abs(l.x - al.x) < 14 && Math.abs(l.y - al.y) < 14) {
        al.hp--;
        g.lasers.splice(i, 1);
        if (g.isChallengingStage) g.hitsCount++;

        if (al.hp <= 0) {
          const isDiving = (al.state === 'dive' || al.state === 'tractor');
          const pts = isDiving ? (al.type === 'boss' ? 400 : 200) : (al.type === 'boss' ? 200 : 100);
          g.score += pts;
          if (g.score > g.highScore) g.highScore = g.score;
          g.scorePops.push({ x: al.x, y: al.y, text: String(pts), timer: 30 });
          g.explosions.push({ x: al.x, y: al.y, frame: 0 });
          if (al.type === 'boss') playArcadeSfx('BOSS');
          else playArcadeSfx('AST-EXP');
          if (pts >= 300) playArcadeSfx('BONUS');

          // If boss had tractor beam active, cancel it
          if (g.tractorBeam.active && g.tractorBeam.boss === al) {
            g.tractorBeam.active = false;
            g.tractorBeam.state = 'off';
            g.isCapturing = false;
          }

          // If boss had captured ship, release and create DUAL FIGHTER!
          if (g.capturedShip && g.capturedShip.boss === al) {
            g.dualFighter = true;
            g.capturedShip = null;
            playArcadeSfx('BONUS');
            g.score += 1000;
            g.scorePops.push({ x: 120, y: 180, text: 'DUAL FIGHTER! +1000', timer: 50 });
          }

          g.aliens.splice(a, 1);
        } else {
          al.damaged = true;
          playArcadeSfx('TRACT');
        }
        break;
      }
    }
  }

  // Aliens Sway, Dive, and Tractor Beam
  const sway = Math.sin(g.tick * 0.05) * 10;
  g.aliens.forEach(al => {
    if (al.state === 'grid') {
      al.x = al.homeX + sway;
      al.y = al.homeY + Math.sin(g.tick * 0.08 + al.homeX) * 2;
      if (Math.random() < 0.004 && g.aliens.filter(a => a.state === 'dive' || a.state === 'tractor').length < 3) {
        if (al.type === 'boss' && !g.tractorBeam.active && !g.dualFighter && !g.capturedShip && Math.random() < 0.45) {
          al.state = 'tractor_approach';
          al.diveTick = 0;
          playArcadeSfx('DIVE');
        } else {
          al.state = 'dive';
          al.diveTick = 0;
          playArcadeSfx('DIVE');
        }
      }
    } else if (al.state === 'tractor_approach') {
      al.diveTick++;
      al.y += 2.0;
      if (al.y >= 75) {
        al.state = 'tractor';
        al.y = 75;
        g.tractorBeam = {
          active: true,
          x: al.x,
          y: al.y + 12,
          height: 0,
          maxH: 135,
          state: 'expanding',
          boss: al,
          timer: 160
        };
        playArcadeSfx('TRACT');
      }
    } else if (al.state === 'tractor') {
      g.tractorBeam.timer--;
      if (g.tractorBeam.state === 'expanding') {
        g.tractorBeam.height += 4.5;
        if (g.tractorBeam.height >= g.tractorBeam.maxH) {
          g.tractorBeam.height = g.tractorBeam.maxH;
          g.tractorBeam.state = 'active';
        }
      }
      // Check capture collision if beam reaches bottom
      if (g.tractorBeam.state === 'active' && !g.isCapturing && !g.dualFighter) {
        if (Math.abs(g.shipX - g.tractorBeam.x) < 22) {
          g.isCapturing = true;
          g.captureShipY = 220;
          g.captureAngle = 0;
          playArcadeSfx('CAPTURE');
        }
      }
      if (g.tractorBeam.timer <= 0) {
        g.tractorBeam.active = false;
        g.tractorBeam.state = 'off';
        al.state = 'dive';
      }
    } else if (al.state === 'dive') {
      al.diveTick++;
      al.y += 2.4;
      al.x += Math.sin(al.diveTick * 0.12) * 3.2;
      al.angle = Math.sin(al.diveTick * 0.1) * 0.6;
      if (al.diveTick === 24 && g.bombs.length < 4 && !g.isChallengingStage) {
        g.bombs.push({ x: al.x, y: al.y + 6, vy: 2.8 });
      }
      // Diving alien crashes into player ship
      if (Math.abs(al.x - g.shipX) < (g.dualFighter ? 18 : 10) && Math.abs(al.y - 220) < 14 && currentMode !== 'tour' && !g.gameOver) {
        g.explosions.push({ x: g.shipX, y: 220, frame: 0 });
        playArcadeSfx('GALAGA-DEATH');
        if (!arcadeImmortalMode) {
          if (g.dualFighter) {
            g.dualFighter = false;
          } else {
            g.lives--;
            if (g.lives <= 0) {
              g.gameOver = true;
              playArcadeSfx('DK-GAMEOVER');
            }
          }
        }
      }
      if (al.y > 232) {
        al.state = 'return';
        al.y = 10;
        al.x = al.homeX;
      }
    } else if (al.state === 'return') {
      al.y += 2.0;
      if (al.y >= al.homeY) {
        al.state = 'grid';
        al.y = al.homeY;
        al.angle = 0;
      }
    }
  });

  if (g.aliens.length === 0) {
    if (g.isChallengingStage) {
      if (g.hitsCount >= 40) {
        g.score += 10000;
        g.scorePops.push({ x: 120, y: 120, text: 'PERFECT! 10000 PTS', timer: 60 });
        playArcadeSfx('BONUS');
      }
      g.isChallengingStage = false;
    }
    g.stage++;
    g.bombs = [];
    playArcadeSfx('BONUS');
    if (g.stage % 4 === 3) {
      g.isChallengingStage = true;
      g.hitsCount = 0;
    }
    spawnGalagaFleet();
  }

  // Bombs
  for (let b = g.bombs.length - 1; b >= 0; b--) {
    const bm = g.bombs[b];
    bm.y += bm.vy;
    if (bm.y > 240) {
      g.bombs.splice(b, 1);
      continue;
    }
    if (!g.isCapturing && Math.abs(bm.x - g.shipX) < (g.dualFighter ? 18 : 9) && Math.abs(bm.y - 220) < 9) {
      g.bombs.splice(b, 1);
      g.explosions.push({ x: g.shipX, y: 220, frame: 0 });
      playArcadeSfx('GALAGA-DEATH');
      if (currentMode !== 'tour' && !arcadeImmortalMode) {
        if (g.dualFighter) {
          g.dualFighter = false;
        } else {
          g.lives--;
          if (g.lives <= 0) {
            g.gameOver = true;
            playArcadeSfx('DK-GAMEOVER');
          }
        }
      }
    }
  }

  // Explosions
  for (let e = g.explosions.length - 1; e >= 0; e--) {
    g.explosions[e].frame++;
    if (g.explosions[e].frame > 16) g.explosions.splice(e, 1);
  }

  // Score Pops
  for (let s = g.scorePops.length - 1; s >= 0; s--) {
    g.scorePops[s].timer--;
    if (g.scorePops[s].timer <= 0) g.scorePops.splice(s, 1);
  }
}

function renderGalagaGame() {
  if (!ctx) return;
  if (ctx.save) ctx.save();

  // CRT Deep Space
  ctx.fillStyle = '#05070a';
  ctx.fillRect(0, 0, 240, 240);

  // Parallax Starfield with Blinking Namco Stars
  const tick = galagaGame.tick;
  for (let st = 0; st < 38; st++) {
    const y1 = (st * 17 + tick * 0.5) % 240;
    const x1 = (st * 43) % 240;
    ctx.fillStyle = '#3867d6';
    ctx.fillRect(x1, y1, 1, 1);

    const y2 = (st * 23 + tick * 1.2) % 240;
    const x2 = (st * 71 + 12) % 240;
    ctx.fillStyle = (st % 3 === 0) ? '#f7b731' : '#eb2f06';
    ctx.fillRect(x2, y2, 1, 1);

    if (st % 2 === 0) {
      const y3 = (st * 31 + tick * 2.2) % 240;
      const x3 = (st * 97 + 34) % 240;
      ctx.fillStyle = ((tick + st) % 12 < 6) ? '#ffffff' : '#778ca3';
      ctx.fillRect(x3, y3, 2, 2);
    }
  }

  // Tractor Beam (Pulsating Blue-Cyan Conical Waves)
  if (galagaGame.tractorBeam.active) {
    const tb = galagaGame.tractorBeam;
    ctx.save();
    const beamGrad = ctx.createLinearGradient(tb.x, tb.y, tb.x, tb.y + tb.height);
    beamGrad.addColorStop(0, 'rgba(0, 229, 255, 0.55)');
    beamGrad.addColorStop(1, 'rgba(0, 210, 211, 0.15)');
    ctx.fillStyle = beamGrad;
    ctx.beginPath();
    ctx.moveTo(tb.x - 8, tb.y);
    ctx.lineTo(tb.x + 8, tb.y);
    const bottomW = 16 + (tb.height / tb.maxH) * 36;
    ctx.lineTo(tb.x + bottomW, tb.y + tb.height);
    ctx.lineTo(tb.x - bottomW, tb.y + tb.height);
    ctx.closePath();
    ctx.fill();

    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 1.0;
    for (let l = 10; l < tb.height; l += 14) {
      const lineW = 10 + (l / tb.maxH) * 32;
      const waveOff = Math.sin((tick * 0.2) + l * 0.1) * 3;
      ctx.beginPath();
      ctx.moveTo(tb.x - lineW + waveOff, tb.y + l);
      ctx.lineTo(tb.x + lineW + waveOff, tb.y + l);
      ctx.stroke();
    }
    ctx.restore();
  }

  // Header Scores
  ctx.fillStyle = '#eb2f06';
  ctx.font = 'bold 8px monospace';
  ctx.fillText('1UP', 22, 12);
  ctx.fillStyle = '#ffffff';
  ctx.fillText(String(galagaGame.score).padStart(6, '0'), 18, 22);

  ctx.fillStyle = '#00d2d3';
  ctx.fillText('HIGH SCORE', 92, 12);
  ctx.fillStyle = '#ffffff';
  ctx.fillText(String(galagaGame.highScore).padStart(6, '0'), 102, 22);

  ctx.fillStyle = '#f1c40f';
  if (galagaGame.isChallengingStage) {
    ctx.fillText('CHALLENGING', 176, 12);
    ctx.fillText(`HITS: ${galagaGame.hitsCount}`, 176, 22);
  } else {
    ctx.fillText(`STAGE ${galagaGame.stage}`, 186, 12);
  }

  // Mini Ship Lives
  for (let l = 0; l < galagaGame.lives; l++) {
    const lx = 186 + l * 12;
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(lx, 26, 6, 6);
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(lx + 2, 25, 2, 2);
  }

  // Dual / Quad Lasers
  galagaGame.lasers.forEach(l => {
    ctx.fillStyle = '#f1c40f';
    ctx.fillRect(l.x - 1, l.y, 2, 7);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(l.x, l.y + 1, 1, 5);
  });

  // Enemy Torpedo Bombs
  galagaGame.bombs.forEach(b => {
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(b.x - 1, b.y, 3, 5);
    ctx.fillStyle = '#f1c40f';
    ctx.fillRect(b.x, b.y + 1, 1, 3);
  });

  // Aliens Pixel Art (16x16 Namco Bitmaps)
  const flap = (tick >> 3) % 2;
  galagaGame.aliens.forEach(al => {
    ctx.save();
    ctx.translate(al.x, al.y);
    if (al.angle) ctx.rotate(al.angle);

    if (al.type === 'boss') {
      const bodyCol = (al.hp === 2) ? '#10ac84' : '#0652dd';
      ctx.fillStyle = bodyCol;
      ctx.fillRect(-7, -4, 14, 8);
      ctx.fillRect(-5, -6, 10, 3);
      ctx.fillStyle = '#00d2d3';
      ctx.fillRect(-3, -7, 6, 2);
      ctx.fillStyle = '#f1c40f';
      if (flap) {
        ctx.fillRect(-9, -8, 2, 5); ctx.fillRect(7, -8, 2, 5);
        ctx.fillRect(-7, -9, 2, 2); ctx.fillRect(5, -9, 2, 2);
      } else {
        ctx.fillRect(-8, -7, 2, 5); ctx.fillRect(6, -7, 2, 5);
        ctx.fillRect(-6, -8, 2, 2); ctx.fillRect(4, -8, 2, 2);
      }
      ctx.fillStyle = '#eb2f06';
      ctx.fillRect(-4, -2, 2, 3); ctx.fillRect(2, -2, 2, 3);
    } else if (al.type === 'red') {
      ctx.fillStyle = '#eb2f06';
      ctx.fillRect(-6, -4, 12, 8);
      ctx.fillRect(-3, -6, 6, 3);
      ctx.fillStyle = '#f1c40f';
      ctx.fillRect(-2, -3, 4, 6);
      ctx.fillRect(-1, -7, 2, 2);
      if (flap) {
        ctx.fillStyle = '#eb2f06';
        ctx.fillRect(-8, -2, 3, 5); ctx.fillRect(5, -2, 3, 5);
        ctx.fillStyle = '#f1c40f';
        ctx.fillRect(-8, 0, 2, 2); ctx.fillRect(6, 0, 2, 2);
      } else {
        ctx.fillStyle = '#eb2f06';
        ctx.fillRect(-7, -1, 3, 5); ctx.fillRect(4, -1, 3, 5);
        ctx.fillStyle = '#f1c40f';
        ctx.fillRect(-7, 1, 2, 2); ctx.fillRect(5, 1, 2, 2);
      }
    } else {
      ctx.fillStyle = '#f1c40f';
      ctx.fillRect(-5, -2, 10, 7);
      ctx.fillStyle = '#273c75';
      ctx.fillRect(-3, -5, 6, 4);
      ctx.fillStyle = '#05070a';
      ctx.fillRect(-4, 0, 8, 1);
      ctx.fillRect(-3, 2, 6, 1);
      ctx.fillStyle = flap ? '#dff9fb' : '#c7ecee';
      if (flap) {
        ctx.fillRect(-8, -4, 4, 6); ctx.fillRect(4, -4, 4, 6);
      } else {
        ctx.fillRect(-9, -3, 4, 5); ctx.fillRect(5, -3, 4, 5);
      }
    }
    ctx.restore();
  });

  // Captive Ship Docked to Boss Galaga
  if (galagaGame.capturedShip && galagaGame.capturedShip.boss) {
    const boss = galagaGame.capturedShip.boss;
    drawSingleFighter(boss.x + 16, boss.y - 2, '#eb2f06');
  }

  // Explosions
  galagaGame.explosions.forEach(ex => {
    const r = ex.frame * 1.6;
    ctx.strokeStyle = (ex.frame % 2 === 0) ? '#f1c40f' : '#eb2f06';
    ctx.lineWidth = 1.6;
    ctx.beginPath();
    ctx.arc(ex.x, ex.y, r, 0, Math.PI * 2);
    ctx.stroke();
    for (let p = 0; p < 8; p++) {
      const pa = (p / 8) * Math.PI * 2;
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(ex.x + Math.cos(pa) * r * 1.2, ex.y + Math.sin(pa) * r * 1.2, 2, 2);
    }
  });

  // Player Fighter Sprite (Authentic 16x16 Namco Pixel Art)
  function drawSingleFighter(sx, sy, hullColor = '#ffffff') {
    ctx.save();
    ctx.translate(sx, sy);
    ctx.fillStyle = hullColor;
    ctx.fillRect(-6, -2, 12, 8);
    ctx.fillRect(-2, -8, 4, 7);
    ctx.fillRect(-1, -11, 2, 4);
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(-8, -4, 3, 8);
    ctx.fillRect(5, -4, 3, 8);
    ctx.fillRect(-5, 1, 10, 2);
    ctx.fillStyle = '#00d2d3';
    ctx.fillRect(-2, -4, 4, 4);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(-1, -4, 2, 1);
    ctx.fillStyle = '#f1c40f';
    ctx.fillRect(-8, -6, 2, 2);
    ctx.fillRect(6, -6, 2, 2);
    if (tick % 4 < 2) {
      ctx.fillRect(-3, 6, 2, 3);
      ctx.fillRect(1, 6, 2, 3);
    }
    ctx.restore();
  }

  // Draw Player or Capturing Fighter
  if (galagaGame.isCapturing) {
    ctx.save();
    ctx.translate(galagaGame.shipX, galagaGame.captureShipY);
    ctx.rotate(galagaGame.captureAngle);
    drawSingleFighter(0, 0, '#eb2f06');
    ctx.restore();
  } else {
    const shipY = 220;
    if (galagaGame.dualFighter) {
      ctx.fillStyle = '#718093';
      ctx.fillRect(galagaGame.shipX - 10, shipY + 2, 20, 2);
      drawSingleFighter(galagaGame.shipX - 8, shipY);
      drawSingleFighter(galagaGame.shipX + 8, shipY);
    } else {
      drawSingleFighter(galagaGame.shipX, shipY);
    }
  }

  // Score Popups
  galagaGame.scorePops.forEach(sp => {
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 8px monospace';
    ctx.fillText(sp.text, sp.x - 6, sp.y);
  });

  // Authentic Arcade Game Over Overlay
  if (galagaGame.gameOver) {
    ctx.fillStyle = 'rgba(5, 7, 10, 0.85)';
    ctx.fillRect(25, 95, 190, 52);
    ctx.strokeStyle = '#eb2f06';
    ctx.lineWidth = 2;
    if (ctx.strokeRect) ctx.strokeRect(25, 95, 190, 52);

    ctx.fillStyle = '#eb2f06';
    ctx.font = 'bold 15px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('GAME OVER', 120, 118);

    if ((galagaGame.tick >> 4) % 2 === 0) {
      ctx.fillStyle = '#f1c40f';
      ctx.font = 'bold 7px monospace';
      ctx.fillText('PRESS 1P START OR SPACE', 120, 136);
    }
    ctx.textAlign = 'start';
  }

  if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
  if (ctx.restore) ctx.restore();
}

function renderGalagaTour(f) {
  if (!galagaGame.active) initGalagaGame();
  updateGalagaGame();
  renderGalagaGame();
}

// 2. DONKEY KONG 1981 NINTENDO 25M: HIGH-FIDELITY PLAYABLE ARCADE ENGINE
// -------------------------------------------------------------------------
const dkongGame = {
  active: false,
  gameOver: false,
  bgmTick: 0,
  bgmStep: 0,
  mario: {
    x: 40,
    y: 210,
    vx: 0,
    vy: 0,
    w: 14,
    h: 16,
    facing: 'right',
    state: 'stand',
    walkFrame: 0,
    climbFrame: 0,
    deathFrame: 0,
    onGround: true,
    ladder: null,
    currentGirder: 0,
    hasHammer: false,
    hammerTimer: 0,
    hammerFrame: 0,
    hammerTuneTick: 0
  },
  score: 0,
  highScore: 7650,
  bonusTimer: 5000,
  bonusTick: 0,
  lives: 3,
  level: 1,
  cleared: false,
  winTimer: 0,
  deathTimer: 0,
  tick: 0,
  dk: {
    frame: 0,
    action: 'idle',
    actionTimer: 0,
    barrelStack: 4
  },
  pauline: {
    waveFrame: 0,
    heartTimer: 0
  },
  barrels: [],
  fireballs: [],
  scorePops: [],
  hammers: [
    { id: 1, x: 36, y: 160, available: true, tier: 2 },
    { id: 2, x: 204, y: 88, available: true, tier: 4 }
  ],
  bonusItems: [
    { id: 'parasol', x: 90, y: 114, points: 300, name: 'Parasol', collected: false },
    { id: 'purse', x: 150, y: 182, points: 500, name: 'Purse', collected: false },
    { id: 'hat', x: 160, y: 86, points: 800, name: 'Hat', collected: false }
  ],
  oilDrum: {
    x: 28,
    y: 226,
    ignited: false,
    flameFrame: 0
  }
};

function getGirderY(x, tier) {
  if (tier === 0) {
    if (x <= 84) return 226;
    return 226 - ((x - 84) / 140) * 4;
  } else if (tier === 1) {
    return 194 + ((x - 18) / 206) * 8;
  } else if (tier === 2) {
    return 168 - ((x - 18) / 206) * 8;
  } else if (tier === 3) {
    return 126 + ((x - 18) / 206) * 8;
  } else if (tier === 4) {
    return 100 - ((x - 18) / 206) * 8;
  } else if (tier === 5) {
    if (x <= 108) return 64;
    return 64 + ((x - 108) / 116) * 4;
  } else if (tier === 6) {
    return 36;
  }
  return 226;
}

const DK_LADDERS = [
  // Tier 0 -> Tier 1
  { id: 1, x: 198, top: 202, bottom: 222, fromTier: 0, toTier: 1, broken: false },
  { id: 2, x: 110, top: 210, bottom: 224, fromTier: 0, toTier: 1, broken: true },
  // Tier 1 -> Tier 2
  { id: 3, x: 44,  top: 168, bottom: 194, fromTier: 1, toTier: 2, broken: false },
  { id: 4, x: 140, top: 174, bottom: 200, fromTier: 1, toTier: 2, broken: true },
  // Tier 2 -> Tier 3
  { id: 5, x: 196, top: 134, bottom: 160, fromTier: 2, toTier: 3, broken: false },
  { id: 6, x: 104, top: 138, bottom: 164, fromTier: 2, toTier: 3, broken: true },
  // Tier 3 -> Tier 4
  { id: 7, x: 44,  top: 100, bottom: 126, fromTier: 3, toTier: 4, broken: false },
  { id: 8, x: 144, top: 106, bottom: 132, fromTier: 3, toTier: 4, broken: true },
  // Tier 4 -> Tier 5
  { id: 9, x: 196, top: 68,  bottom: 92,  fromTier: 4, toTier: 5, broken: false },
  // Tier 5 -> Tier 6 (Pauline's Refuge)
  { id: 10, x: 102, top: 36, bottom: 64, fromTier: 5, toTier: 6, broken: false },
  { id: 11, x: 138, top: 36, bottom: 64, fromTier: 5, toTier: 6, broken: false }
];

function initDonkeyKongGame() {
  dkongGame.active = true;
  dkongGame.gameOver = false;
  dkongGame.bgmTick = 0;
  dkongGame.bgmStep = 0;
  dkongGame.mario.x = 40;
  dkongGame.mario.y = 220; // 226 (girder top) - 6 (boots bottom at y+6) = 220 flush on girder!
  dkongGame.mario.vx = 0;
  dkongGame.mario.vy = 0;
  dkongGame.mario.facing = 'right';
  dkongGame.mario.state = 'stand';
  dkongGame.mario.walkFrame = 0;
  dkongGame.mario.climbFrame = 0;
  dkongGame.mario.deathFrame = 0;
  dkongGame.mario.onGround = true;
  dkongGame.mario.ladder = null;
  dkongGame.mario.currentGirder = 0;
  dkongGame.mario.hasHammer = false;
  dkongGame.mario.hammerTimer = 0;
  dkongGame.mario.hammerFrame = 0;
  dkongGame.score = 0;
  dkongGame.bonusTimer = 5000;
  dkongGame.bonusTick = 0;
  dkongGame.lives = (typeof arcadeImmortalMode !== 'undefined' && arcadeImmortalMode) ? 99 : 3;
  dkongGame.cleared = false;
  dkongGame.winTimer = 0;
  dkongGame.deathTimer = 0;
  dkongGame.tick = 0;
  dkongGame.dk.frame = 0;
  dkongGame.dk.action = 'idle';
  dkongGame.dk.actionTimer = 0;
  dkongGame.barrels = [];
  dkongGame.fireballs = [];
  dkongGame.scorePops = [];
  dkongGame.hammers.forEach(h => h.available = true);
  dkongGame.bonusItems.forEach(b => b.collected = false);
  dkongGame.oilDrum.ignited = false;
  playArcadeSfx('DK-INTRO');
}

function dkongJump() {
  initAudio();
  const m = dkongGame.mario;
  if (m.onGround && m.state !== 'climb' && m.state !== 'dead' && !m.hasHammer) {
    m.vy = -4.2;
    m.onGround = false;
    m.state = 'jump';
    playArcadeSfx('DK-JUMP');
  }
}

function dkongClimbUp() {
  initAudio();
  const m = dkongGame.mario;
  if (m.state === 'dead' || m.hasHammer) return;
  const lad = DK_LADDERS.find(l => {
    if (l.broken || Math.abs(m.x - l.x) >= 9) return false;
    const upperY = getGirderY(l.x, l.toTier) - 6;
    const lowerY = getGirderY(l.x, l.fromTier) - 6;
    return m.y <= lowerY + 4 && m.y >= upperY - 2;
  });
  if (lad) {
    m.state = 'climb';
    m.ladder = lad;
    m.x = lad.x;
    m.y -= 1.4;
    m.climbFrame++;
    if (m.climbFrame % 6 === 0) playArcadeSfx('DK-WALK');
    const upperY = getGirderY(m.x, lad.toTier) - 6;
    if (m.y <= upperY) {
      m.currentGirder = lad.toTier;
      m.y = upperY;
      m.state = 'stand';
      m.onGround = true;
      m.ladder = null;
    }
  }
}

function dkongClimbDown() {
  initAudio();
  const m = dkongGame.mario;
  if (m.state === 'dead' || m.hasHammer) return;
  const lad = DK_LADDERS.find(l => {
    if (l.broken || Math.abs(m.x - l.x) >= 9) return false;
    const upperY = getGirderY(l.x, l.toTier) - 6;
    const lowerY = getGirderY(l.x, l.fromTier) - 6;
    return m.y >= upperY - 4 && m.y <= lowerY + 2;
  });
  if (lad) {
    m.state = 'climb';
    m.ladder = lad;
    m.x = lad.x;
    m.y += 1.4;
    m.climbFrame++;
    if (m.climbFrame % 6 === 0) playArcadeSfx('DK-WALK');
    const lowerY = getGirderY(m.x, lad.fromTier) - 6;
    if (m.y >= lowerY) {
      m.currentGirder = lad.fromTier;
      m.y = lowerY;
      m.state = 'stand';
      m.onGround = true;
      m.ladder = null;
    }
  }
}

function updateDonkeyKongGame() {
  if (dkongGame.gameOver) {
    if (arcadeKeysDown['1'] || arcadeKeysDown['5'] || arcadeKeysDown[' '] || arcadeKeysDown['enter'] || arcadeKeysDown['r']) {
      initDonkeyKongGame();
    }
    return;
  }

  dkongGame.tick++;
  const m = dkongGame.mario;

  // Authentic 25M Walking Bass Background Music (Nintendo 8035 DAC Ostinato)
  if (!dkongGame.cleared && m.state !== 'dead' && !dkongGame.gameOver && !m.hasHammer) {
    dkongGame.bgmTick++;
    if (dkongGame.bgmTick % 18 === 0) {
      dkongGame.bgmStep = ((dkongGame.bgmStep || 0) + 1) % 4;
      playArcadeSfx('DK-BGM');
    }
  }

  // 1. Tour Mode AI
  if (currentMode === 'tour') {
    if (!m.hasHammer) {
      if (m.currentGirder === 0) {
        if (m.x < 196) {
          m.vx = 1.4; m.facing = 'right'; m.state = 'run';
          const near = dkongGame.barrels.find(b => b.tier === 0 && Math.abs(b.x - m.x) < 22 && b.x > m.x);
          if (near && m.onGround) dkongJump();
        } else {
          m.vx = 0; dkongClimbUp();
        }
      } else if (m.currentGirder === 1) {
        if (m.x > 46) {
          m.vx = -1.4; m.facing = 'left'; m.state = 'run';
          const near = dkongGame.barrels.find(b => b.tier === 1 && Math.abs(b.x - m.x) < 22 && b.x < m.x);
          if (near && m.onGround) dkongJump();
        } else {
          m.vx = 0; dkongClimbUp();
        }
      } else if (m.currentGirder === 2) {
        if (m.x < 194) {
          m.vx = 1.4; m.facing = 'right'; m.state = 'run';
          const near = dkongGame.barrels.find(b => b.tier === 2 && Math.abs(b.x - m.x) < 22 && b.x > m.x);
          if (near && m.onGround) dkongJump();
        } else {
          m.vx = 0; dkongClimbUp();
        }
      } else if (m.currentGirder === 3) {
        if (m.x > 46) {
          m.vx = -1.4; m.facing = 'left'; m.state = 'run';
          const near = dkongGame.barrels.find(b => b.tier === 3 && Math.abs(b.x - m.x) < 22 && b.x < m.x);
          if (near && m.onGround) dkongJump();
        } else {
          m.vx = 0; dkongClimbUp();
        }
      } else if (m.currentGirder === 4) {
        if (m.x < 194) {
          m.vx = 1.4; m.facing = 'right'; m.state = 'run';
          const near = dkongGame.barrels.find(b => b.tier === 4 && Math.abs(b.x - m.x) < 22 && b.x > m.x);
          if (near && m.onGround) dkongJump();
        } else {
          m.vx = 0; dkongClimbUp();
        }
      } else if (m.currentGirder === 5) {
        if (m.x > 104) {
          m.vx = -1.4; m.facing = 'left'; m.state = 'run';
        } else {
          m.vx = 0; dkongClimbUp();
        }
      } else {
        m.vx = 0;
      }
    }
  } else {
    // 2. Playable Player Controls & Input
    if (m.state !== 'climb' && m.state !== 'dead') {
      if (arcadeKeysDown['a'] || arcadeKeysDown['arrowleft'] || (typeof dpadActiveDir !== 'undefined' && dpadActiveDir === 'left')) {
        m.vx = -1.6; m.facing = 'left';
        if (m.onGround) m.state = m.hasHammer ? 'hammer' : 'run';
      } else if (arcadeKeysDown['d'] || arcadeKeysDown['arrowright'] || (typeof dpadActiveDir !== 'undefined' && dpadActiveDir === 'right')) {
        m.vx = 1.6; m.facing = 'right';
        if (m.onGround) m.state = m.hasHammer ? 'hammer' : 'run';
      } else if (typeof dpadActiveDir === 'undefined' || !dpadActiveDir) {
        m.vx = 0;
        if (m.onGround && m.state === 'run') m.state = m.hasHammer ? 'hammer' : 'stand';
      }

      if (m.onGround && (m.state === 'run' || m.state === 'hammer') && Math.abs(m.vx) > 0.1) {
        if (dkongGame.tick % 12 === 0) playArcadeSfx('DK-WALK');
      }

      if (arcadeKeysDown['w'] || arcadeKeysDown['arrowup'] || (typeof dpadActiveDir !== 'undefined' && dpadActiveDir === 'up')) dkongClimbUp();
      else if (arcadeKeysDown['s'] || arcadeKeysDown['arrowdown'] || (typeof dpadActiveDir !== 'undefined' && dpadActiveDir === 'down')) dkongClimbDown();
    } else if (m.state === 'climb') {
      if (arcadeKeysDown['w'] || arcadeKeysDown['arrowup'] || (typeof dpadActiveDir !== 'undefined' && dpadActiveDir === 'up')) dkongClimbUp();
      else if (arcadeKeysDown['s'] || arcadeKeysDown['arrowdown'] || (typeof dpadActiveDir !== 'undefined' && dpadActiveDir === 'down')) dkongClimbDown();
    }
  }

  // Bonus Timer countdown & Time-Up Death
  dkongGame.bonusTick++;
  if (dkongGame.bonusTick % 50 === 0 && dkongGame.bonusTimer > 0 && !dkongGame.cleared && m.state !== 'dead') {
    dkongGame.bonusTimer = Math.max(0, dkongGame.bonusTimer - 100);
    if (dkongGame.bonusTimer <= 0 && currentMode !== 'tour') {
      m.state = 'dead';
      m.deathFrame = 0;
      dkongGame.deathTimer = 75;
      if (!arcadeImmortalMode) dkongGame.lives--;
      playArcadeSfx('DK-DEATH');
    }
  }

  // Stage Win Sequence
  if (dkongGame.cleared) {
    dkongGame.winTimer--;
    if (dkongGame.winTimer <= 0) {
      dkongGame.level++;
      dkongGame.cleared = false;
      dkongGame.mario.x = 40;
      dkongGame.mario.y = 220;
      dkongGame.mario.vx = 0;
      dkongGame.mario.vy = 0;
      dkongGame.mario.currentGirder = 0;
      dkongGame.mario.state = 'stand';
      dkongGame.bonusTimer = 5000 + dkongGame.level * 500;
      dkongGame.barrels = [];
      dkongGame.fireballs = [];
      dkongGame.hammers.forEach(h => h.available = true);
      dkongGame.bonusItems.forEach(b => b.collected = false);
      playArcadeSfx('DK-INTRO');
    }
    return;
  }

  // Player Death Sequence
  if (m.state === 'dead') {
    m.deathFrame++;
    dkongGame.deathTimer--;
    if (dkongGame.deathTimer <= 0) {
      if (arcadeImmortalMode || dkongGame.lives > 0) {
        m.x = 40;
        m.y = 220;
        m.vx = 0;
        m.vy = 0;
        m.currentGirder = 0;
        m.state = 'stand';
        m.onGround = true;
        m.deathFrame = 0;
        dkongGame.bonusTimer = 5000;
        dkongGame.barrels = [];
        dkongGame.fireballs = [];
      } else {
        dkongGame.gameOver = true;
        m.state = 'gameover';
        m.vx = 0;
        m.vy = 0;
        playArcadeSfx('DK-GAMEOVER');
      }
    }
    return;
  }

  // Hammer Power-up Handling & Audio Theme Loop
  if (m.hasHammer) {
    m.hammerTimer--;
    m.hammerFrame++;
    m.hammerTuneTick++;
    if (m.hammerTuneTick % 16 === 0) playArcadeSfx('DK-HAMMER-TUNE');
    if (m.hammerTimer <= 0) {
      m.hasHammer = false;
      m.state = 'stand';
    }
  }

  // Collect Hammers
  dkongGame.hammers.forEach(h => {
    if (h.available && !m.hasHammer) {
      if (Math.abs(m.x - h.x) < 14 && Math.abs(m.y - h.y) < 16) {
        h.available = false;
        m.hasHammer = true;
        m.hammerTimer = 340;
        m.state = 'hammer';
        playArcadeSfx('WARP');
      }
    }
  });

  // Collect Pauline Bonus Items
  dkongGame.bonusItems.forEach(item => {
    if (!item.collected) {
      if (Math.abs(m.x - item.x) < 14 && Math.abs(m.y - item.y) < 14) {
        item.collected = true;
        dkongGame.score += item.points;
        if (dkongGame.score > dkongGame.highScore) dkongGame.highScore = dkongGame.score;
        dkongGame.scorePops.push({ x: item.x, y: item.y - 8, text: `+${item.points}`, timer: 40 });
        playArcadeSfx('BONUS');
      }
    }
  });

  // Mario Physics & Position
  if (m.state === 'climb' && m.ladder) {
    // Handled inside climb functions
  } else if (m.state === 'jump') {
    m.x += m.vx;
    m.y += m.vy;
    m.vy += 0.28;
    const floorY = getGirderY(m.x, m.currentGirder) - 6;
    if (m.vy > 0 && m.y >= floorY) {
      m.y = floorY;
      m.vy = 0;
      m.onGround = true;
      m.state = Math.abs(m.vx) > 0.1 ? (m.hasHammer ? 'hammer' : 'run') : (m.hasHammer ? 'hammer' : 'stand');
    }
  } else {
    m.x += m.vx;
    if (m.currentGirder === 6) {
      m.x = Math.max(94, Math.min(146, m.x));
    } else {
      m.x = Math.max(18, Math.min(222, m.x));
    }
    m.y = getGirderY(m.x, m.currentGirder) - 6;
    if (Math.abs(m.vx) > 0.1) {
      m.walkFrame++;
    }
  }

  // Check Win Condition (Reaching Pauline at Tier 6 / Top Platform)
  if ((m.currentGirder === 6 || (m.y <= 42 && m.x >= 92 && m.x <= 148)) && !dkongGame.cleared) {
    dkongGame.cleared = true;
    dkongGame.winTimer = 90;
    dkongGame.score += dkongGame.bonusTimer;
    if (dkongGame.score > dkongGame.highScore) dkongGame.highScore = dkongGame.score;
    dkongGame.scorePops.push({ x: 120, y: 24, text: `+${dkongGame.bonusTimer}`, timer: 60 });
    playArcadeSfx('DK-WIN');
  }

  // Donkey Kong Action Cycle & Barrel Tossing
  dkongGame.dk.frame++;
  dkongGame.dk.actionTimer++;
  if (dkongGame.dk.actionTimer > 120) {
    const cycle = dkongGame.dk.actionTimer - 120;
    if (cycle < 20) {
      dkongGame.dk.action = 'reach_barrel';
    } else if (cycle < 40) {
      dkongGame.dk.action = 'hold_barrel';
    } else if (cycle === 40) {
      dkongGame.dk.action = 'roll_barrel';
      playArcadeSfx('DK-ROLL');
      dkongGame.barrels.push({
        x: 74,
        y: 60,
        tier: 5,
        vx: 1.4 + dkongGame.level * 0.15,
        vy: 0,
        rollFrame: 0,
        state: 'rolling',
        scored: false
      });
    } else if (cycle < 65) {
      dkongGame.dk.action = 'chest_beat';
      if (cycle % 12 === 0) playArcadeSfx('DK-ROAR');
    } else {
      dkongGame.dk.action = 'idle';
      dkongGame.dk.actionTimer = 0;
    }
  }

  // Update Barrels
  for (let i = dkongGame.barrels.length - 1; i >= 0; i--) {
    const b = dkongGame.barrels[i];
    b.rollFrame++;

    if (b.state === 'falling_ladder') {
      b.y += 2.2;
      if (b.y >= getGirderY(b.x, b.tier) - 6) {
        b.state = 'rolling';
        playArcadeSfx('DK-ROLL');
      }
    } else if (b.state === 'falling') {
      b.y += b.vy;
      b.vy += 0.32;
      const targetY = getGirderY(b.x, b.tier) - 6;
      if (b.vy > 0 && b.y >= targetY) {
        b.y = targetY;
        b.vy = 0;
        b.state = 'rolling';
        playArcadeSfx('DK-ROLL');
      }
    } else {
      b.x += b.vx;
      b.y = getGirderY(b.x, b.tier) - 6;

      // Tier Transitions (Roll & Drop)
      if (b.tier === 5 && b.x >= 222) {
        b.tier = 4; b.vx = -(1.4 + dkongGame.level * 0.15); b.state = 'falling'; b.vy = 1.0;
      } else if (b.tier === 4 && b.x <= 20) {
        b.tier = 3; b.vx = (1.4 + dkongGame.level * 0.15); b.state = 'falling'; b.vy = 1.0;
      } else if (b.tier === 3 && b.x >= 222) {
        b.tier = 2; b.vx = -(1.4 + dkongGame.level * 0.15); b.state = 'falling'; b.vy = 1.0;
      } else if (b.tier === 2 && b.x <= 20) {
        b.tier = 1; b.vx = (1.4 + dkongGame.level * 0.15); b.state = 'falling'; b.vy = 1.0;
      } else if (b.tier === 1 && b.x >= 222) {
        b.tier = 0; b.vx = -(1.4 + dkongGame.level * 0.15); b.state = 'falling'; b.vy = 1.0;
      } else if (b.tier === 0 && b.x <= 34) {
        // Roll into blue Oil Drum!
        dkongGame.barrels.splice(i, 1);
        dkongGame.oilDrum.ignited = true;
        playArcadeSfx('DK-FALL');
        // Spawn Fireball if less than 2
        if (dkongGame.fireballs.length < 2) {
          dkongGame.fireballs.push({
            x: 36,
            y: 218,
            tier: 0,
            vx: 0.8 + Math.random() * 0.4,
            flameFrame: 0
          });
        }
        continue;
      }

      // Ladder drop chance
      if (b.rollFrame % 15 === 0 && Math.random() < 0.25) {
        const lad = DK_LADDERS.find(l => !l.broken && l.fromTier === b.tier - 1 && Math.abs(b.x - l.x) < 8);
        if (lad) {
          b.tier = lad.fromTier;
          b.state = 'falling_ladder';
          b.x = lad.x;
          b.vx = -b.vx; // Reverse after climbing down
        }
      }
    }

    // Mario vaulting over barrel
    if (m.state === 'jump' && !b.scored && Math.abs(m.x - b.x) < 16 && m.y < b.y && (b.y - m.y) < 28) {
      b.scored = true;
      dkongGame.score += 100;
      if (dkongGame.score > dkongGame.highScore) dkongGame.highScore = dkongGame.score;
      dkongGame.scorePops.push({ x: m.x, y: m.y - 10, text: '100', timer: 30 });
      playArcadeSfx('BONUS');
    }

    // Mario smashing barrel with hammer
    if (m.hasHammer && Math.abs(m.x - b.x) < 20 && Math.abs(m.y - b.y) < 20) {
      dkongGame.barrels.splice(i, 1);
      dkongGame.score += 300;
      if (dkongGame.score > dkongGame.highScore) dkongGame.highScore = dkongGame.score;
      dkongGame.scorePops.push({ x: b.x, y: b.y - 8, text: '300', timer: 35 });
      playArcadeSfx('DK-HAMR');
      continue;
    }

    // Collision with Mario
    if (!m.hasHammer && m.state !== 'dead' && !dkongGame.cleared && currentMode !== 'tour') {
      if (Math.abs(m.x - b.x) < 10 && Math.abs(m.y - b.y) < 10) {
        m.state = 'dead';
        m.deathFrame = 0;
        dkongGame.deathTimer = 75;
        if (!arcadeImmortalMode) {
          dkongGame.lives--;
        }
        playArcadeSfx('DK-DEATH');
      }
    }
  }

  // Update Fireballs
  for (let f = dkongGame.fireballs.length - 1; f >= 0; f--) {
    const fb = dkongGame.fireballs[f];
    fb.flameFrame++;
    fb.x += fb.vx;
    fb.y = getGirderY(fb.x, fb.tier) - 8;
    if (fb.x <= 20 || fb.x >= 222) fb.vx = -fb.vx;

    // Hammer smash fireball
    if (m.hasHammer && Math.abs(m.x - fb.x) < 20 && Math.abs(m.y - fb.y) < 20) {
      dkongGame.fireballs.splice(f, 1);
      dkongGame.score += 500;
      if (dkongGame.score > dkongGame.highScore) dkongGame.highScore = dkongGame.score;
      dkongGame.scorePops.push({ x: fb.x, y: fb.y - 8, text: '500', timer: 35 });
      playArcadeSfx('DK-HAMR');
      continue;
    }

    // Fireball kills Mario
    if (!m.hasHammer && m.state !== 'dead' && !dkongGame.cleared && currentMode !== 'tour') {
      if (Math.abs(m.x - fb.x) < 10 && Math.abs(m.y - fb.y) < 12) {
        m.state = 'dead';
        m.deathFrame = 0;
        dkongGame.deathTimer = 75;
        if (!arcadeImmortalMode) {
          dkongGame.lives--;
        }
        playArcadeSfx('DK-DEATH');
      }
    }
  }

  // Update Score Pops
  for (let s = dkongGame.scorePops.length - 1; s >= 0; s--) {
    const sp = dkongGame.scorePops[s];
    sp.y -= 0.35;
    sp.timer--;
    if (sp.timer <= 0) dkongGame.scorePops.splice(s, 1);
  }
}

function drawMarioSprite(ctx, m) {
  if (m.state === 'gameover') return;
  ctx.save();
  ctx.translate(Math.round(m.x), Math.round(m.y));
  if (m.facing === 'left') ctx.scale(-1, 1);

  if (m.state === 'dead') {
    ctx.rotate(m.deathFrame * 0.15);
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(-7, -4, 14, 8);
    ctx.fillStyle = '#0984e3';
    ctx.fillRect(-4, -8, 8, 6);
    ctx.fillStyle = '#ffbe76';
    ctx.fillRect(-3, -12, 6, 5);
    if (m.deathFrame > 20) {
      ctx.strokeStyle = '#f1c40f';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      if (ctx.ellipse) ctx.ellipse(0, -16, 6, 2, 0, 0, Math.PI * 2);
      else if (ctx.arc) ctx.arc(0, -16, 5, 0, Math.PI * 2);
      ctx.stroke();
    }
  } else if (m.state === 'climb') {
    const rung = (m.climbFrame >> 2) % 2;
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(-5, -14, 10, 4);
    ctx.fillStyle = '#5c3d2e';
    ctx.fillRect(-5, -10, 10, 3);
    ctx.fillStyle = '#0984e3';
    ctx.fillRect(-6, -7, 12, 6);
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(-4, -7, 2, 8); ctx.fillRect(2, -7, 2, 8);
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(-5, 0, 10, 4);
    ctx.fillStyle = '#ffffff';
    if (rung === 0) {
      ctx.fillRect(-8, -10, 3, 3); ctx.fillRect(5, -6, 3, 3);
      ctx.fillStyle = '#5c3d2e';
      ctx.fillRect(-6, 4, 4, 3); ctx.fillRect(2, 2, 4, 3);
    } else {
      ctx.fillRect(-8, -6, 3, 3); ctx.fillRect(5, -10, 3, 3);
      ctx.fillStyle = '#5c3d2e';
      ctx.fillRect(-6, 2, 4, 3); ctx.fillRect(2, 4, 4, 3);
    }
  } else {
    // Red Cap & Visor
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(-5, -14, 10, 4);
    ctx.fillRect(0, -12, 7, 3);
    // Peach Face & Nose
    ctx.fillStyle = '#ffbe76';
    ctx.fillRect(-4, -10, 8, 6);
    ctx.fillRect(2, -9, 4, 4);
    // Mustache & Hair
    ctx.fillStyle = '#5c3d2e';
    ctx.fillRect(-5, -10, 3, 5);
    ctx.fillRect(0, -7, 6, 2);
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, -9, 2, 2);
    // Blue Shirt
    ctx.fillStyle = '#0984e3';
    ctx.fillRect(-5, -5, 10, 5);
    // Red Overalls & Yellow Buttons
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(-3, -4, 6, 7);
    ctx.fillRect(-4, -1, 8, 4);
    ctx.fillStyle = '#f1c40f';
    ctx.fillRect(-2, -3, 2, 2); ctx.fillRect(1, -3, 2, 2);
    // White Gloves
    ctx.fillStyle = '#ffffff';
    if (m.state === 'jump') {
      ctx.fillRect(-7, -11, 3, 3); ctx.fillRect(4, -11, 3, 3);
    } else {
      ctx.fillRect(3, -2, 3, 3);
    }
    // Brown Boots & Leg Animation
    ctx.fillStyle = '#5c3d2e';
    if (m.state === 'jump') {
      ctx.fillRect(-7, 2, 4, 3);
      ctx.fillRect(3, 0, 4, 3);
    } else if (m.state === 'run') {
      const step = (m.walkFrame >> 2) % 3;
      if (step === 0) { ctx.fillRect(-5, 3, 4, 3); ctx.fillRect(1, 3, 4, 3); }
      else if (step === 1) { ctx.fillRect(-7, 2, 4, 3); ctx.fillRect(2, 0, 4, 3); }
      else { ctx.fillRect(-2, 0, 4, 3); ctx.fillRect(3, 2, 4, 3); }
    } else {
      ctx.fillRect(-4, 3, 4, 3); ctx.fillRect(1, 3, 4, 3);
    }

    // Wielded Hammer
    if (m.hasHammer) {
      const hDown = (m.hammerFrame % 14 < 7);
      if (hDown) {
        ctx.fillStyle = '#5d4037';
        ctx.fillRect(4, -3, 14, 3);
        ctx.fillStyle = '#f1c40f';
        ctx.fillRect(16, -7, 8, 11);
        ctx.strokeStyle = '#2d3436';
        ctx.lineWidth = 1;
        if (ctx.strokeRect) ctx.strokeRect(16, -7, 8, 11);
      } else {
        ctx.fillStyle = '#5d4037';
        ctx.fillRect(-2, -22, 3, 12);
        ctx.fillStyle = '#f1c40f';
        ctx.fillRect(-6, -26, 11, 8);
        ctx.strokeStyle = '#2d3436';
        ctx.lineWidth = 1;
        if (ctx.strokeRect) ctx.strokeRect(-6, -26, 11, 8);
      }
    }
  }
  ctx.restore();
}

function drawDonkeyKongSprite(ctx, dkX, dkY, action, fTick) {
  ctx.save();
  ctx.translate(Math.round(dkX), Math.round(dkY));

  // Stack of 4 brown barrels beside DK
  ctx.fillStyle = '#b7791f';
  ctx.fillRect(-28, 6, 9, 12); ctx.fillRect(-17, 6, 9, 12);
  ctx.fillRect(-28, -8, 9, 12); ctx.fillRect(-17, -8, 9, 12);
  ctx.strokeStyle = '#2d3436'; ctx.lineWidth = 1;
  if (ctx.strokeRect) {
    ctx.strokeRect(-28, 6, 9, 12); ctx.strokeRect(-17, 6, 9, 12);
    ctx.strokeRect(-28, -8, 9, 12); ctx.strokeRect(-17, -8, 9, 12);
  }

  // Donkey Kong Torso & Shoulders
  ctx.fillStyle = '#6d4c41';
  ctx.fillRect(-14, -6, 28, 24);
  ctx.fillRect(-16, -14, 32, 12);

  // Peach Chest & Face
  ctx.fillStyle = '#ffcc80';
  ctx.fillRect(-8, 0, 16, 14);
  ctx.fillRect(-10, -10, 20, 9);

  // Eyes & Teeth
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(-8, -11, 5, 4); ctx.fillRect(3, -11, 5, 4);
  ctx.fillStyle = '#000000';
  ctx.fillRect(-6, -10, 2, 3); ctx.fillRect(4, -10, 2, 3);
  ctx.fillStyle = '#c0392b';
  ctx.fillRect(-6, -4, 12, 3);
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(-5, -4, 2, 2); ctx.fillRect(3, -4, 2, 2);

  // Feet
  ctx.fillStyle = '#4e342e';
  ctx.fillRect(-12, 18, 8, 5); ctx.fillRect(4, 18, 8, 5);

  // Animated Arms
  if (action === 'reach_barrel') {
    ctx.fillStyle = '#4e342e';
    ctx.fillRect(-26, -6, 12, 6);
    ctx.fillRect(14, 2, 6, 12);
  } else if (action === 'hold_barrel') {
    ctx.fillStyle = '#4e342e';
    ctx.fillRect(-16, -24, 6, 14);
    ctx.fillRect(10, -24, 6, 14);
    ctx.fillStyle = '#b7791f';
    ctx.fillRect(-8, -30, 16, 10);
    ctx.strokeStyle = '#2d3436';
    if (ctx.strokeRect) ctx.strokeRect(-8, -30, 16, 10);
  } else if (action === 'roll_barrel') {
    ctx.fillStyle = '#4e342e';
    ctx.fillRect(-16, 2, 6, 12);
    ctx.fillRect(12, -4, 14, 6);
  } else {
    const beatLeft = (fTick % 30 < 15);
    ctx.fillStyle = '#4e342e';
    if (beatLeft) {
      ctx.fillRect(-18, 0, 7, 12);
      ctx.fillRect(14, 4, 7, 12);
    } else {
      ctx.fillRect(-14, 4, 7, 12);
      ctx.fillRect(11, 0, 7, 12);
    }
  }

  ctx.restore();
}

function drawPaulineSprite(ctx, px, py, fTick, heartTimer) {
  ctx.save();
  ctx.translate(Math.round(px), Math.round(py));

  // Pink Gown
  ctx.fillStyle = '#ff7979';
  ctx.fillRect(-5, 0, 10, 14);
  ctx.fillStyle = '#ff9ff3';
  ctx.fillRect(-6, 8, 12, 6);

  // Face & Auburn Hair
  ctx.fillStyle = '#ffbe76';
  ctx.fillRect(-4, -7, 8, 7);
  ctx.fillStyle = '#d35400';
  ctx.fillRect(-6, -11, 12, 5);
  ctx.fillRect(-7, -8, 3, 10);
  ctx.fillRect(4, -8, 3, 7);
  ctx.fillStyle = '#0984e3';
  ctx.fillRect(-1, -6, 2, 2);

  // Waving Arms
  ctx.fillStyle = '#ffbe76';
  const wave = (fTick % 30 < 15);
  if (wave) {
    ctx.fillRect(-8, -4, 3, 7);
    ctx.fillRect(5, -8, 3, 7);
  } else {
    ctx.fillRect(-8, -8, 3, 7);
    ctx.fillRect(5, -4, 3, 7);
  }

  // HELP! Speech Balloon
  if (fTick % 40 < 28) {
    ctx.fillStyle = '#ffffff';
    if (ctx.roundRect) {
      ctx.beginPath();
      ctx.roundRect(10, -14, 28, 11, 3);
      ctx.fill();
    } else {
      ctx.fillRect(10, -14, 28, 11);
    }
    ctx.fillStyle = '#eb2f06';
    ctx.font = 'bold 7px monospace';
    ctx.fillText('HELP!', 12, -6);
  }

  // Heart Icon
  if (heartTimer > 0 || fTick % 60 < 20) {
    ctx.fillStyle = '#ff4757';
    ctx.font = '9px monospace';
    ctx.fillText('♥', -3, -13);
  }

  ctx.restore();
}

function drawBarrelSprite(ctx, b) {
  ctx.save();
  ctx.translate(Math.round(b.x), Math.round(b.y));

  if (b.state === 'falling_ladder') {
    ctx.fillStyle = '#b7791f';
    ctx.fillRect(-5, -6, 10, 12);
    ctx.strokeStyle = '#2d3436';
    ctx.lineWidth = 1;
    if (ctx.strokeRect) ctx.strokeRect(-5, -6, 10, 12);
    ctx.fillStyle = '#636e72';
    ctx.fillRect(-5, -4, 10, 2);
    ctx.fillRect(-5, 2, 10, 2);
  } else {
    ctx.rotate((b.rollFrame * 0.18) * Math.sign(b.vx || 1));
    ctx.fillStyle = '#b7791f';
    ctx.beginPath();
    ctx.arc(0, 0, 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#2d3436';
    ctx.lineWidth = 1.2;
    ctx.stroke();

    ctx.strokeStyle = '#f5cd79';
    ctx.lineWidth = 1.0;
    ctx.beginPath();
    ctx.moveTo(-5, 0); ctx.lineTo(5, 0);
    ctx.moveTo(0, -5); ctx.lineTo(0, 5);
    ctx.stroke();

    ctx.fillStyle = '#2d3436';
    ctx.fillRect(-1, -1, 2, 2);
  }

  ctx.restore();
}

function drawGirder(startX, startY, endX, endY) {
  const dx = endX - startX, dy = endY - startY;
  const len = Math.hypot(dx, dy);
  const steps = Math.floor(len / 8);

  ctx.strokeStyle = '#e056fd';
  ctx.lineWidth = 2.0;
  ctx.beginPath();
  ctx.moveTo(startX, startY); ctx.lineTo(endX, endY);
  ctx.moveTo(startX, startY + 6); ctx.lineTo(endX, endY + 6);
  ctx.stroke();

  ctx.strokeStyle = '#be2edd';
  ctx.lineWidth = 1.0;
  ctx.beginPath();
  for (let i = 0; i < steps; i++) {
    const t1 = i / steps, t2 = (i + 1) / steps;
    ctx.moveTo(startX + dx * t1, startY + dy * t1);
    ctx.lineTo(startX + dx * t2, startY + dy * t2 + 6);
    ctx.moveTo(startX + dx * t2, startY + dy * t2);
    ctx.lineTo(startX + dx * t1, startY + dy * t1 + 6);
  }
  ctx.stroke();

  ctx.fillStyle = '#00d2d3';
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    ctx.fillRect(startX + dx * t - 1, startY + dy * t - 1, 2, 2);
    ctx.fillRect(startX + dx * t - 1, startY + dy * t + 5, 2, 2);
  }
}

function renderDonkeyKongGame() {
  if (!ctx) return;
  if (ctx.save) ctx.save();

  // CRT Cabinet Deep Black
  ctx.fillStyle = '#05070a';
  ctx.fillRect(0, 0, 240, 240);

  // 1. Render All 6 Tiers of Authentic Girders
  // Tier 0 (Bottom Floor)
  drawGirder(16, 226, 84, 226);
  drawGirder(84, 226, 224, 222);
  // Tier 1
  drawGirder(18, 194, 224, 202);
  // Tier 2
  drawGirder(224, 160, 18, 168);
  // Tier 3
  drawGirder(18, 126, 224, 134);
  // Tier 4
  drawGirder(224, 92, 18, 100);
  // Tier 5 (DK Platform)
  drawGirder(16, 64, 108, 64);
  drawGirder(108, 64, 224, 68);
  // Tier 6 (Pauline's Top Platform)
  drawGirder(94, 36, 146, 36);

  // 2. Render Ladders
  DK_LADDERS.forEach(lad => {
    ctx.strokeStyle = lad.broken ? '#ff7675' : '#00d2d3';
    ctx.lineWidth = 1.5;
    for (let ly = lad.top; ly <= lad.bottom; ly += 5) {
      if (lad.broken && ly > lad.top + 8 && ly < lad.bottom - 8) continue;
      ctx.beginPath();
      ctx.moveTo(lad.x - 4, ly); ctx.lineTo(lad.x + 4, ly);
      ctx.stroke();
    }
    ctx.beginPath();
    ctx.moveTo(lad.x - 4, lad.top); ctx.lineTo(lad.x - 4, lad.bottom);
    ctx.moveTo(lad.x + 4, lad.top); ctx.lineTo(lad.x + 4, lad.bottom);
    ctx.stroke();
  });

  const fTick = dkongGame.tick;

  // 3. Render Blue Oil Drum & Flames
  const drumX = 22, drumY = 210;
  ctx.fillStyle = '#0984e3';
  ctx.fillRect(drumX, drumY, 14, 16);
  ctx.strokeStyle = '#00d2d3';
  if (ctx.strokeRect) ctx.strokeRect(drumX, drumY, 14, 16);
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 6px monospace';
  ctx.fillText('OIL', drumX + 2, drumY + 11);

  for (let f = 0; f < 3; f++) {
    const fx = drumX + 2 + f * 4;
    const fh = dkongGame.oilDrum.ignited ? (7 + Math.sin(fTick * 0.25 + f) * 5) : (3 + Math.sin(fTick * 0.15 + f) * 2);
    ctx.fillStyle = (f === 1) ? '#f1c40f' : '#eb2f06';
    ctx.fillRect(fx, drumY - fh, 3, fh);
    ctx.fillStyle = '#00d2d3';
    ctx.fillRect(fx + 1, drumY - 2, 2, 2);
  }

  // 4. Render Donkey Kong
  drawDonkeyKongSprite(ctx, 50, 48, dkongGame.dk.action, fTick);

  // 5. Render Pauline
  drawPaulineSprite(ctx, 120, 24, fTick, dkongGame.pauline.heartTimer);

  // 6. Render Hammers
  dkongGame.hammers.forEach(h => {
    if (h.available) {
      const flash = (fTick >> 2) % 2 === 0;
      ctx.fillStyle = '#5d4037';
      ctx.fillRect(h.x + 3, h.y - 6, 2, 12);
      ctx.fillStyle = flash ? '#f1c40f' : '#e67e22';
      ctx.fillRect(h.x, h.y - 10, 8, 6);
      ctx.strokeStyle = '#2d3436';
      if (ctx.strokeRect) ctx.strokeRect(h.x, h.y - 10, 8, 6);
    }
  });

  // 7. Render Pauline Bonus Items
  dkongGame.bonusItems.forEach(item => {
    if (!item.collected) {
      if (item.id === 'parasol') {
        ctx.fillStyle = '#ff1493';
        ctx.beginPath();
        ctx.arc(item.x, item.y, 5, Math.PI, 0);
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        if (ctx.strokeRect) ctx.strokeRect(item.x - 1, item.y, 2, 6);
      } else if (item.id === 'purse') {
        ctx.fillStyle = '#ffd700';
        ctx.fillRect(item.x - 4, item.y - 4, 8, 6);
        ctx.strokeStyle = '#d35400';
        if (ctx.strokeRect) ctx.strokeRect(item.x - 4, item.y - 4, 8, 6);
      } else if (item.id === 'hat') {
        ctx.fillStyle = '#ff9f43';
        ctx.fillRect(item.x - 5, item.y - 2, 10, 3);
        ctx.fillRect(item.x - 3, item.y - 5, 6, 4);
      }
    }
  });

  // 8. Render Barrels
  dkongGame.barrels.forEach(b => drawBarrelSprite(ctx, b));

  // 9. Render Fireballs
  dkongGame.fireballs.forEach(fb => {
    ctx.save();
    ctx.translate(Math.round(fb.x), Math.round(fb.y));
    const fl = (fb.flameFrame >> 2) % 3;
    ctx.fillStyle = (fl === 0) ? '#f1c40f' : (fl === 1 ? '#eb2f06' : '#ff7675');
    ctx.beginPath();
    ctx.arc(0, 0, 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#f1c40f';
    ctx.fillRect(-3, -7, 2, 3); ctx.fillRect(1, -8, 2, 4);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(-3, -2, 2, 2); ctx.fillRect(1, -2, 2, 2);
    ctx.fillStyle = '#000000';
    ctx.fillRect(-2, -2, 1, 2); ctx.fillRect(2, -2, 1, 2);
    ctx.restore();
  });

  // 10. Render Mario (Jumpman)
  drawMarioSprite(ctx, dkongGame.mario);

  // 11. Render Score Popups
  dkongGame.scorePops.forEach(sp => {
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 9px monospace';
    ctx.fillText(sp.text, sp.x - 6, sp.y);
  });

  // 12. Arcade Header Telemetry
  ctx.fillStyle = '#eb2f06';
  ctx.font = 'bold 8px monospace';
  ctx.fillText('1UP', 18, 10);
  ctx.fillStyle = '#ffffff';
  ctx.fillText(String(dkongGame.score).padStart(6, '0'), 18, 18);

  ctx.fillStyle = '#00d2d3';
  ctx.fillText('HIGH SCORE', 60, 10);
  ctx.fillStyle = '#ffffff';
  ctx.fillText(String(dkongGame.highScore).padStart(6, '0'), 70, 18);

  ctx.fillStyle = '#ff9f43';
  ctx.fillText('BONUS', 184, 10);
  ctx.fillStyle = '#ffffff';
  ctx.fillText(String(dkongGame.bonusTimer).padStart(4, '0'), 188, 18);

  if (arcadeImmortalMode) {
    ctx.fillStyle = '#eb2f06';
    ctx.font = '8px monospace';
    ctx.fillText('♥ x ∞', 188, 28);
  } else {
    for (let l = 0; l < dkongGame.lives; l++) {
      ctx.fillStyle = '#eb2f06';
      ctx.font = '8px monospace';
      ctx.fillText('♥', 188 + l * 10, 28);
    }
  }

  // 13. Authentic Arcade Game Over Overlay
  if (dkongGame.gameOver) {
    ctx.fillStyle = 'rgba(5, 7, 10, 0.85)';
    ctx.fillRect(25, 95, 190, 52);
    ctx.strokeStyle = '#eb2f06';
    ctx.lineWidth = 2;
    if (ctx.strokeRect) ctx.strokeRect(25, 95, 190, 52);

    ctx.fillStyle = '#eb2f06';
    ctx.font = 'bold 15px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('GAME OVER', 120, 118);

    if ((fTick >> 4) % 2 === 0) {
      ctx.fillStyle = '#f1c40f';
      ctx.font = 'bold 7px monospace';
      ctx.fillText('PRESS 1P START OR SPACE', 120, 136);
    }
    ctx.textAlign = 'start';
  }

  if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
  if (ctx.restore) ctx.restore();
}

function renderDonkeyKongTour(f) {
  if (!dkongGame.active) initDonkeyKongGame();
  updateDonkeyKongGame();
  renderDonkeyKongGame();
}

// -------------------------------------------------------------------------
// 3. FROGGER (1981 KONAMI DUAL AY-3-8910): FULLY PLAYABLE ARCADE ENGINE
// -------------------------------------------------------------------------
// 3. FROGGER (1981 KONAMI DUAL Z80): FULLY PLAYABLE ARCADE ENGINE
// -------------------------------------------------------------------------
const froggerGame = {
  active: false,
  gameOver: false,
  frog: {
    gridX: 7,
    gridY: 13,
    x: 120,
    y: 224,
    dir: 'up',
    hopTick: 0,
    hasLady: false,
    dead: false,
    deathTimer: 0,
    deathType: 'splat',
    deathX: 120,
    deathY: 224
  },
  vehicles: [],
  logs: [],
  homeBays: [false, false, false, false, false],
  bayCrocodiles: [false, false, false, false, false],
  bayFlies: [false, false, false, false, false],
  score: 0,
  highScore: 12000,
  lives: 3,
  level: 1,
  time: 60,
  tick: 0
};

function killFrogger(deathType) {
  const fg = froggerGame.frog;
  fg.deathX = fg.x;
  fg.deathY = fg.y;
  fg.dead = true;
  fg.deathType = deathType;
  fg.deathTimer = 45;
  fg.gridX = 7;
  fg.gridY = 13;
  fg.x = 120;
  fg.y = 224;
  fg.hasLady = false;
  froggerGame.time = 60;
  if (!arcadeImmortalMode) {
    froggerGame.lives--;
    if (froggerGame.lives <= 0) {
      froggerGame.gameOver = true;
      playArcadeSfx('DK-GAMEOVER');
    }
  }
  playArcadeSfx(deathType === 'drown' ? 'FROG-SPLASH' : 'FROG-SPLAT');
}

function initFroggerGame() {
  froggerGame.active = true;
  froggerGame.gameOver = false;
  froggerGame.frog.gridX = 7;
  froggerGame.frog.gridY = 13;
  froggerGame.frog.x = 120;
  froggerGame.frog.y = 224;
  froggerGame.frog.dir = 'up';
  froggerGame.frog.hopTick = 0;
  froggerGame.frog.hasLady = false;
  froggerGame.frog.dead = false;
  froggerGame.frog.deathTimer = 0;
  froggerGame.frog.deathType = 'splat';
  froggerGame.frog.deathX = 120;
  froggerGame.frog.deathY = 224;
  froggerGame.score = 0;
  froggerGame.lives = (typeof arcadeImmortalMode !== 'undefined' && arcadeImmortalMode) ? 99 : 3;
  froggerGame.time = 60;
  froggerGame.homeBays = [false, false, false, false, false];
  froggerGame.bayCrocodiles = [false, false, false, false, false];
  froggerGame.bayFlies = [false, false, false, false, false];
  froggerGame.tick = 0;
  spawnFroggerTraffic();
  spawnFroggerRiver();
  playArcadeSfx('FROG-H');
}

function spawnFroggerTraffic() {
  froggerGame.vehicles = [];
  for (let c = 0; c < 3; c++) froggerGame.vehicles.push({ x: c * 80, y: 198, w: 22, speed: -1.2, type: 'sedan', color: '#feca57' });
  for (let c = 0; c < 3; c++) froggerGame.vehicles.push({ x: c * 90, y: 182, w: 20, speed: 0.8, type: 'dozer', color: '#ffffff' });
  for (let c = 0; c < 3; c++) froggerGame.vehicles.push({ x: c * 75, y: 166, w: 22, speed: -1.8, type: 'racer', color: '#eb2f06' });
  for (let c = 0; c < 2; c++) froggerGame.vehicles.push({ x: c * 120, y: 150, w: 24, speed: 2.2, type: 'formula', color: '#a55eea' });
  for (let c = 0; c < 2; c++) froggerGame.vehicles.push({ x: c * 110, y: 134, w: 36, speed: -0.9, type: 'truck', color: '#10ac84' });
}

function spawnFroggerRiver() {
  froggerGame.logs = [];
  // Row 1: Medium logs (moving right) - log 1 carries pink Lady Frog!
  for (let c = 0; c < 3; c++) froggerGame.logs.push({ x: c * 90, y: 102, w: 46, speed: 1.1, type: 'log', diving: false, hasLady: c === 1 });
  // Row 2: Diving turtles (flotillas of 3, moving left)
  for (let c = 0; c < 4; c++) froggerGame.logs.push({ x: c * 65, y: 86, w: 34, speed: -1.3, type: 'turtle', diving: true, divePhase: c * 45 });
  // Row 3: Large logs and Crocodiles (moving right)
  for (let c = 0; c < 2; c++) froggerGame.logs.push({ x: c * 130, y: 70, w: 72, speed: 1.5, type: c === 0 ? 'crocodile' : 'log', diving: false });
  // Row 4: Small logs (moving right)
  for (let c = 0; c < 3; c++) froggerGame.logs.push({ x: c * 85, y: 54, w: 36, speed: 1.0, type: 'log', diving: false });
  // Row 5: Diving turtles (flotillas of 2, moving left)
  for (let c = 0; c < 4; c++) froggerGame.logs.push({ x: c * 70, y: 38, w: 28, speed: -1.6, type: 'turtle', diving: true, divePhase: c * 50 });
}

function froggerHop(dir) {
  initAudio();
  if (froggerGame.gameOver || froggerGame.frog.dead) return;
  const fg = froggerGame.frog;
  fg.dir = dir;
  fg.hopTick = 8;
  if (dir === 'up') fg.gridY = Math.max(1, fg.gridY - 1);
  else if (dir === 'down') fg.gridY = Math.min(13, fg.gridY + 1);
  else if (dir === 'left') fg.gridX = Math.max(1, fg.gridX - 1);
  else if (dir === 'right') fg.gridX = Math.min(13, fg.gridX + 1);

  fg.x = 8 + fg.gridX * 16;
  fg.y = 16 + fg.gridY * 16;

  playArcadeSfx('FROG-H');
  froggerGame.score += 10;
  if (froggerGame.score > froggerGame.highScore) froggerGame.highScore = froggerGame.score;
}

function updateFroggerGame() {
  if (froggerGame.gameOver) {
    if (arcadeKeysDown['1'] || arcadeKeysDown['5'] || arcadeKeysDown[' '] || arcadeKeysDown['enter'] || arcadeKeysDown['r']) {
      initFroggerGame();
    }
    return;
  }

  froggerGame.tick++;
  const fg = froggerGame.frog;
  if (fg.hopTick > 0) fg.hopTick--;

  // If frog was manually repositioned outside start dock by unit tests, clear dead state
  if (fg.dead && (fg.gridY !== 13 || fg.y !== 224)) {
    fg.dead = false;
    fg.deathTimer = 0;
  }

  // Handle active death sequence countdown
  if (fg.dead) {
    fg.deathTimer--;
    if (fg.deathTimer <= 0) {
      fg.dead = false;
    }
  } else if (currentMode !== 'tour' && froggerGame.tick % 60 === 0) {
    froggerGame.time = Math.max(0, froggerGame.time - 1);
    if (froggerGame.time <= 0) {
      killFrogger('splat');
      return;
    }
  }

  // Authentic Konami AY-3-8910 Frogger Background Music ("Inu no Omawarisan" / "The Frog Song")
  if (!froggerGame.gameOver && !fg.dead) {
    froggerGame.bgmTick = (froggerGame.bgmTick || 0) + 1;
    if (froggerGame.bgmTick % 13 === 0) {
      froggerGame.bgmStep = ((froggerGame.bgmStep || 0) + 1) % 32;
      playArcadeSfx('FROG-BGM');
    }
  }

  // Random Crocodile in bay & Fly bonus update
  if (froggerGame.tick % 160 === 0) {
    const bay = Math.floor(Math.random() * 5);
    if (!froggerGame.homeBays[bay]) {
      froggerGame.bayCrocodiles[bay] = (Math.random() < 0.4);
      froggerGame.bayFlies[bay] = (!froggerGame.bayCrocodiles[bay] && Math.random() < 0.5);
    }
  }

  // Autonomous Tour AI
  if (currentMode === 'tour' && froggerGame.tick % 32 === 0) {
    if (fg.gridY > 1) {
      const nextY = 16 + (fg.gridY - 1) * 16;
      const danger = froggerGame.vehicles.some(v => Math.abs(v.y - nextY) < 10 && Math.abs(v.x - fg.x) < 20);
      if (!danger) froggerHop('up');
      else if (Math.random() < 0.4) froggerHop(Math.random() < 0.5 ? 'left' : 'right');
    } else {
      initFroggerGame();
    }
  }

  // Vehicles update & squish collision
  froggerGame.vehicles.forEach(v => {
    v.x += v.speed;
    if (v.speed < 0 && v.x < -40) v.x = 240 + Math.random() * 20;
    else if (v.speed > 0 && v.x > 260) v.x = -40;

    if (!fg.dead && Math.abs(v.y - fg.y) < 10 && Math.abs(v.x - fg.x) < (v.w / 2 + 4) && currentMode !== 'tour') {
      killFrogger('splat');
    }
  });

  // River logs, crocodiles & diving turtles
  let onRiverSupport = false;
  let submergedDrown = false;
  let crocodileSnap = false;

  froggerGame.logs.forEach(l => {
    l.x += l.speed;
    if (l.speed < 0 && l.x < -60) l.x = 240 + Math.random() * 20;
    else if (l.speed > 0 && l.x > 260) l.x = -60;

    if (l.diving) {
      l.divePhase = (l.divePhase + 1) % 180;
    }

    if (!fg.dead && fg.gridY >= 2 && fg.gridY <= 6) {
      if (Math.abs(l.y - fg.y) < 8 && fg.x >= l.x - 4 && fg.x <= l.x + l.w + 4) {
        // If diving turtle is in submerged underwater phase (125..165), frog cannot stand on it!
        if (l.diving && l.divePhase >= 125 && l.divePhase <= 165) {
          submergedDrown = true;
        } else if (l.type === 'crocodile' && fg.x >= l.x + l.w - 16) {
          // If frog lands on crocodile mouth/snout, jaws snap!
          crocodileSnap = true;
        } else {
          onRiverSupport = true;
          fg.x += l.speed;
          fg.gridX = Math.round((fg.x - 8) / 16);
          if (l.hasLady && !fg.hasLady) {
            l.hasLady = false;
            fg.hasLady = true;
            playArcadeSfx('BONUS');
          }
        }
      }
    }
  });

  // Drown in water or submerged turtle or crocodile bite
  if (!fg.dead && fg.gridY >= 2 && fg.gridY <= 6 && (!onRiverSupport || submergedDrown || crocodileSnap) && currentMode !== 'tour') {
    if (crocodileSnap) killFrogger('splat');
    else killFrogger('drown');
  }

  // Home Bays Arrival
  if (!fg.dead && fg.gridY === 1) {
    const bayXList = [20, 68, 116, 164, 212];
    const bayIndex = bayXList.findIndex(bx => Math.abs(fg.x - bx) <= 10);
    if (bayIndex >= 0 && bayIndex < 5 && !froggerGame.homeBays[bayIndex]) {
      // Check if crocodile is in bay
      if (froggerGame.bayCrocodiles[bayIndex]) {
        // Eaten by crocodile in bay mouth
        killFrogger('splat');
      } else {
        froggerGame.homeBays[bayIndex] = true;
        let bonusPts = 500;
        if (froggerGame.bayFlies[bayIndex]) bonusPts += 200;
        if (fg.hasLady) bonusPts += 200;
        froggerGame.score += bonusPts;
        if (froggerGame.score > froggerGame.highScore) froggerGame.highScore = froggerGame.score;
        playArcadeSfx('FROG-HOME');
        fg.gridX = 7; fg.gridY = 13; fg.x = 120; fg.y = 224; fg.hasLady = false;
        froggerGame.time = 60;

        // All 5 bays filled victory
        if (froggerGame.homeBays.every(b => b)) {
          froggerGame.score += 1000;
          if (froggerGame.score > froggerGame.highScore) froggerGame.highScore = froggerGame.score;
          playArcadeSfx('FROG-FANFARE');
          froggerGame.homeBays = [false, false, false, false, false];
          froggerGame.bayCrocodiles = [false, false, false, false, false];
          froggerGame.bayFlies = [false, false, false, false, false];
        }
      }
    } else {
      killFrogger('splat');
    }
  }
}

function renderFroggerGame() {
  if (!ctx) return;
  if (ctx.save) ctx.save();

  // Top Bank & Bays
  ctx.fillStyle = '#10ac84';
  ctx.fillRect(0, 16, 240, 18);
  const bayX = [20, 68, 116, 164, 212];
  bayX.forEach((bx, idx) => {
    ctx.fillStyle = '#0984e3';
    ctx.fillRect(bx - 10, 16, 20, 18);
    ctx.fillStyle = '#2ecc71';
    ctx.beginPath();
    ctx.arc(bx, 25, 7, 0, Math.PI * 2);
    ctx.fill();

    // Crocodile head in bay
    if (froggerGame.bayCrocodiles[idx]) {
      ctx.fillStyle = '#eb2f06';
      ctx.fillRect(bx - 4, 21, 8, 7);
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(bx - 3, 22, 2, 2); ctx.fillRect(bx + 1, 22, 2, 2);
    } else if (froggerGame.bayFlies[idx]) {
      // Fly bonus
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(bx - 2, 23, 4, 3);
      ctx.fillStyle = '#00d2d3';
      ctx.fillRect(bx - 1, 21, 2, 2);
    } else if (froggerGame.homeBays[idx]) {
      // Frog in home
      ctx.fillStyle = '#2ed573';
      ctx.fillRect(bx - 5, 20, 10, 8);
      ctx.fillStyle = '#ff4757';
      ctx.fillRect(bx - 3, 19, 2, 2); ctx.fillRect(bx + 1, 19, 2, 2);
    }
  });

  // River Blue Surface
  ctx.fillStyle = '#0652dd';
  ctx.fillRect(0, 34, 240, 82);

  // River Logs, Crocodiles, Diving Turtles
  froggerGame.logs.forEach(l => {
    if (l.type === 'turtle') {
      const isSubmerged = l.diving && l.divePhase >= 125 && l.divePhase <= 165;
      const isBubbling = l.diving && (l.divePhase >= 115 && l.divePhase <= 175);
      if (isSubmerged) {
        // Water ripples / bubbles
        ctx.fillStyle = 'rgba(255, 255, 255, 0.45)';
        ctx.fillRect(l.x + 4, l.y + 4, 3, 3);
        ctx.fillRect(l.x + 14, l.y + 2, 4, 4);
      } else {
        ctx.fillStyle = isBubbling ? '#1289a7' : '#009432';
        ctx.fillRect(l.x, l.y, l.w, 12);
        ctx.fillStyle = '#a3cb38';
        for (let t = 4; t < l.w; t += 10) {
          ctx.fillRect(l.x + t, l.y + 2, 6, 8);
        }
      }
    } else if (l.type === 'crocodile') {
      // Crocodile
      ctx.fillStyle = '#006266';
      ctx.fillRect(l.x, l.y + 1, l.w, 11);
      ctx.fillStyle = '#1b1464';
      ctx.fillRect(l.x + l.w - 14, l.y + 2, 12, 9); // Snout
      ctx.fillStyle = '#ff3838'; // Red eye
      ctx.fillRect(l.x + l.w - 10, l.y + 1, 3, 2);
      ctx.fillStyle = '#ffffff'; // White snapping teeth
      ctx.fillRect(l.x + l.w - 8, l.y + 5, 2, 2);
    } else {
      // Wood Log with bark
      ctx.fillStyle = '#795548';
      ctx.fillRect(l.x, l.y + 1, l.w, 11);
      ctx.fillStyle = '#5d4037';
      ctx.fillRect(l.x + 2, l.y + 2, l.w - 4, 9);
      ctx.fillStyle = '#8d6e63';
      ctx.fillRect(l.x + 6, l.y + 4, 8, 3);
      ctx.fillRect(l.x + 22, l.y + 3, 10, 3);
      if (l.hasLady) {
        ctx.fillStyle = '#ff6b81';
        ctx.fillRect(l.x + Math.floor(l.w / 2) - 4, l.y + 2, 8, 8);
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(l.x + Math.floor(l.w / 2) - 3, l.y + 1, 2, 2);
        ctx.fillRect(l.x + Math.floor(l.w / 2) + 1, l.y + 1, 2, 2);
      }
    }
  });

  // Middle Purple Sidewalk Strip
  ctx.fillStyle = '#4834d4';
  ctx.fillRect(0, 116, 240, 16);

  // Highway Asphalt
  ctx.fillStyle = '#130f40';
  ctx.fillRect(0, 132, 240, 82);

  // Road Lane Dashes
  ctx.fillStyle = 'rgba(255, 255, 255, 0.25)';
  for (let rw = 148; rw <= 196; rw += 16) {
    for (let d = 0; d < 240; d += 24) ctx.fillRect(d, rw, 12, 1);
  }

  // Vehicles
  froggerGame.vehicles.forEach(v => {
    ctx.fillStyle = v.color;
    ctx.fillRect(v.x, v.y - 2, v.w, 12);
    ctx.fillStyle = '#1e272e';
    ctx.fillRect(v.x + 2, v.y + 1, v.w - 4, 6);
    ctx.fillStyle = '#f1c40f';
    if (v.speed < 0) {
      ctx.fillRect(v.x + 1, v.y + 1, 2, 2);
      ctx.fillRect(v.x + 1, v.y + 5, 2, 2);
    } else {
      ctx.fillRect(v.x + v.w - 3, v.y + 1, 2, 2);
      ctx.fillRect(v.x + v.w - 3, v.y + 5, 2, 2);
    }
  });

  // Bottom Purple Starting Sidewalk
  ctx.fillStyle = '#4834d4';
  ctx.fillRect(0, 214, 240, 18);

  // Player Frog Sprite / Authentic Death Animation
  const fg = froggerGame.frog;
  if (!fg.dead) {
    ctx.save();
    ctx.translate(fg.x, fg.y);
    ctx.fillStyle = '#00ff66';
    ctx.fillRect(-5, -5, 10, 10);
    ctx.fillStyle = '#f5cd79';
    ctx.fillRect(-3, -3, 6, 6);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(-4, -6, 3, 2); ctx.fillRect(1, -6, 3, 2);
    ctx.fillStyle = '#000000';
    ctx.fillRect(-3, -6, 1, 1); ctx.fillRect(2, -6, 1, 1);

    if (fg.hasLady) {
      ctx.fillStyle = '#ff3838'; // Pink/Red Lady Frog
      ctx.fillRect(-2, -2, 4, 4);
    }
    ctx.restore();
  } else {
    // Authentic Konami Arcade Death Animation at (fg.deathX, fg.deathY)
    ctx.save();
    ctx.translate(fg.deathX, fg.deathY);
    if (fg.deathType === 'splat') {
      if (fg.deathTimer > 28) {
        // Phase 1: Squashed / flattened frog with crushed limbs and splatter
        ctx.fillStyle = '#10ac84';
        ctx.fillRect(-8, -2, 16, 4);
        ctx.fillStyle = '#f5cd79';
        ctx.fillRect(-4, -1, 8, 2);
        // Crushed splayed limbs
        ctx.fillStyle = '#00ff66';
        ctx.fillRect(-9, -4, 3, 2);
        ctx.fillRect(6, -4, 3, 2);
        ctx.fillRect(-10, 2, 4, 2);
        ctx.fillRect(6, 2, 4, 2);
        // Blood splatter dots
        ctx.fillStyle = '#eb2f06';
        ctx.fillRect(-3, -3, 2, 2);
        ctx.fillRect(2, 2, 2, 2);
        ctx.fillRect(5, -1, 2, 2);
      } else {
        // Phase 2: Iconic Konami Arcade Skull & Crossbones Tombstone
        // Diagonal crossbones behind/underneath skull
        ctx.fillStyle = '#dfe4ea';
        ctx.fillRect(-7, 3, 14, 2);
        ctx.fillRect(-6, 1, 2, 6);
        ctx.fillRect(4, 1, 2, 6);
        // Bone knobs
        ctx.fillRect(-8, 0, 3, 3); ctx.fillRect(5, 0, 3, 3);
        ctx.fillRect(-8, 5, 3, 3); ctx.fillRect(5, 5, 3, 3);

        // Skull dome & face
        ctx.fillStyle = '#f1f2f6';
        ctx.fillRect(-5, -7, 10, 8);
        ctx.fillRect(-6, -5, 12, 5);

        // Hollow eye sockets with menacing red pupils
        ctx.fillStyle = '#1e272e';
        ctx.fillRect(-4, -5, 3, 3);
        ctx.fillRect(1, -5, 3, 3);
        ctx.fillStyle = '#ff4757';
        ctx.fillRect(-3, -4, 1, 1);
        ctx.fillRect(2, -4, 1, 1);

        // Skull teeth / jaw
        ctx.fillStyle = '#f1f2f6';
        ctx.fillRect(-3, 1, 6, 2);
        ctx.fillStyle = '#1e272e';
        ctx.fillRect(-2, 1, 1, 2);
        ctx.fillRect(0, 1, 1, 2);
        ctx.fillRect(1, 1, 1, 2);
      }
    } else {
      // River Drowning: 'drown'
      if (fg.deathTimer > 28) {
        // Phase 1: Sinking frog plunge into deep water with splash droplets
        ctx.fillStyle = '#009432';
        ctx.fillRect(-3, -2, 6, 4);
        ctx.fillStyle = '#f5cd79';
        ctx.fillRect(-2, -1, 4, 2);
        // Splash droplets shooting up
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(-6, -6, 2, 2);
        ctx.fillRect(4, -6, 2, 2);
        ctx.fillRect(-2, -8, 2, 2);
        ctx.fillRect(2, -7, 2, 2);
        ctx.fillStyle = '#00d2d3';
        ctx.fillRect(-7, -3, 2, 2);
        ctx.fillRect(5, -3, 2, 2);
      } else {
        // Phase 2: Expanding concentric water ripple rings radiating outwards
        const progress = (28 - fg.deathTimer) / 28; // 0 to 1
        const r1 = 3 + progress * 10;
        const r2 = 1 + progress * 15;
        // Inner ripple
        ctx.strokeStyle = `rgba(0, 210, 211, ${Math.max(0, 1 - progress * 0.9)})`;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        if (ctx.ellipse) ctx.ellipse(0, 0, r1, r1 * 0.5, 0, 0, Math.PI * 2);
        else ctx.arc(0, 0, r1, 0, Math.PI * 2);
        ctx.stroke();

        // Outer ripple
        ctx.strokeStyle = `rgba(255, 255, 255, ${Math.max(0, 1 - progress)})`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        if (ctx.ellipse) ctx.ellipse(0, 0, r2, r2 * 0.5, 0, 0, Math.PI * 2);
        else ctx.arc(0, 0, r2, 0, Math.PI * 2);
        ctx.stroke();

        // Center bubble dot
        if (progress < 0.6) {
          ctx.fillStyle = '#ffffff';
          ctx.fillRect(-1, -1, 2, 2);
        }
      }
    }
    ctx.restore();
  }

  // Header & HUD
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 8px monospace';
  ctx.fillText(`SCORE: ${froggerGame.score}`, 10, 12);
  ctx.fillStyle = '#f1c40f';
  ctx.fillText(`HI: ${froggerGame.highScore}`, 84, 12);
  ctx.fillStyle = froggerGame.time <= 10 ? '#ff4757' : '#00e5ff';
  ctx.fillText(`T:${String(froggerGame.time).padStart(2, '0')}`, 148, 12);
  ctx.fillStyle = '#00ff66';
  for (let l = 0; l < Math.min(4, froggerGame.lives); l++) {
    ctx.fillText('🐸', 184 + l * 12, 12);
  }

  // Authentic Arcade Game Over Overlay
  if (froggerGame.gameOver) {
    ctx.fillStyle = 'rgba(5, 7, 10, 0.85)';
    ctx.fillRect(25, 95, 190, 52);
    ctx.strokeStyle = '#eb2f06';
    ctx.lineWidth = 2;
    if (ctx.strokeRect) ctx.strokeRect(25, 95, 190, 52);

    ctx.fillStyle = '#eb2f06';
    ctx.font = 'bold 15px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('GAME OVER', 120, 118);

    if ((froggerGame.tick >> 4) % 2 === 0) {
      ctx.fillStyle = '#f1c40f';
      ctx.font = 'bold 7px monospace';
      ctx.fillText('PRESS 1P START OR SPACE', 120, 136);
    }
    ctx.textAlign = 'start';
  }

  if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
  if (ctx.restore) ctx.restore();
}

function renderFroggerTour(f) {
  if (!froggerGame.active) initFroggerGame();
  updateFroggerGame();
  renderFroggerGame();
}

// -------------------------------------------------------------------------
// 4. ASTEROIDS (1979 ATARI DVG VECTOR): FULLY PLAYABLE ARCADE ENGINE
// -------------------------------------------------------------------------
const asteroidsGame = {
  active: false,
  gameOver: false,
  ship: { x: 120, y: 120, angle: -Math.PI / 2, vx: 0, vy: 0, thrust: false },
  rocks: [],
  bullets: [],
  saucerBullets: [],
  debris: [],
  saucer: { active: false, x: -20, y: 60, vx: 1.4, vy: 0, type: 'large', timer: 0 },
  score: 0,
  highScore: 30000,
  lives: 3,
  level: 1,
  tick: 0,
  heartbeatToggle: false
};

function initAsteroidsGame() {
  asteroidsGame.active = true;
  asteroidsGame.gameOver = false;
  asteroidsGame.ship.x = 120;
  asteroidsGame.ship.y = 120;
  asteroidsGame.ship.angle = -Math.PI / 2;
  asteroidsGame.ship.vx = 0;
  asteroidsGame.ship.vy = 0;
  asteroidsGame.ship.thrust = false;
  asteroidsGame.ship.invulnerable = 60;
  asteroidsGame.bullets = [];
  asteroidsGame.saucerBullets = [];
  asteroidsGame.debris = [];
  asteroidsGame.saucer = { active: false, x: -20, y: 60, vx: 1.4, vy: 0, type: 'large', timer: 0 };
  asteroidsGame.score = 0;
  asteroidsGame.lives = (typeof arcadeImmortalMode !== 'undefined' && arcadeImmortalMode) ? 99 : 3;
  asteroidsGame.level = 1;
  asteroidsGame.tick = 0;
  asteroidsGame.heartbeatToggle = false;
  spawnAsteroidsField(4);
  playArcadeSfx('AST-FIRE');
}

function spawnAsteroidsField(count) {
  asteroidsGame.rocks = [];
  for (let i = 0; i < count; i++) {
    let rx = (i * 60 + 30) % 240;
    let ry = (i * 50 + 20) % 240;
    if (Math.hypot(rx - 120, ry - 120) < 50) {
      rx = (rx < 120) ? 25 : 215;
      ry = (ry < 120) ? 25 : 215;
    }
    asteroidsGame.rocks.push({
      x: rx,
      y: ry,
      vx: (Math.random() - 0.5) * 1.6,
      vy: (Math.random() - 0.5) * 1.6,
      radius: 18,
      size: 3
    });
  }
}

function asteroidsFire() {
  initAudio();
  if (asteroidsGame.gameOver) return;
  if (asteroidsGame.bullets.length < 5) {
    const s = asteroidsGame.ship;
    asteroidsGame.bullets.push({
      x: s.x + Math.cos(s.angle) * 8,
      y: s.y + Math.sin(s.angle) * 8,
      vx: Math.cos(s.angle) * 5.6 + s.vx * 0.4,
      vy: Math.sin(s.angle) * 5.6 + s.vy * 0.4,
      life: 40
    });
    playArcadeSfx('AST-FIRE');
  }
}

function asteroidsHyperspace() {
  initAudio();
  if (asteroidsGame.gameOver) return;
  asteroidsGame.ship.x = Math.random() * 220 + 10;
  asteroidsGame.ship.y = Math.random() * 220 + 10;
  asteroidsGame.ship.vx = 0;
  asteroidsGame.ship.vy = 0;
  playArcadeSfx('DEF-HYPER');
}

function updateAsteroidsGame() {
  if (asteroidsGame.gameOver) {
    if (arcadeKeysDown['1'] || arcadeKeysDown['5'] || arcadeKeysDown[' '] || arcadeKeysDown['enter'] || arcadeKeysDown['r']) {
      initAsteroidsGame();
    }
    return;
  }

  asteroidsGame.tick++;
  const s = asteroidsGame.ship;

  // Heartbeat dual-tone sound (accelerates as remaining asteroids decrease)
  const beatInterval = Math.max(14, Math.floor(asteroidsGame.rocks.length * 8 + 12));
  if (asteroidsGame.tick % beatInterval === 0) {
    asteroidsGame.heartbeatToggle = !asteroidsGame.heartbeatToggle;
    playArcadeSfx(asteroidsGame.heartbeatToggle ? 'AST-THUMP-LO' : 'AST-THUMP-HI');
  }

  // Autonomous Tour AI
  if (currentMode === 'tour') {
    let closest = null, minD = 9999;
    asteroidsGame.rocks.forEach(rk => {
      const d = Math.hypot(rk.x - s.x, rk.y - s.y);
      if (d < minD) { minD = d; closest = rk; }
    });
    if (closest) {
      const targetAngle = Math.atan2(closest.y - s.y, closest.x - s.x);
      let da = targetAngle - s.angle;
      while (da < -Math.PI) da += Math.PI * 2;
      while (da > Math.PI) da -= Math.PI * 2;
      s.angle += Math.sign(da) * Math.min(Math.abs(da), 0.08);
      if (Math.abs(da) < 0.35 && asteroidsGame.tick % 16 === 0) asteroidsFire();
      s.thrust = (minD > 65 && asteroidsGame.tick % 50 < 20);
    }
  } else {
    if (arcadeKeysDown['a'] || arcadeKeysDown['arrowleft'] || (typeof dpadActiveDir !== 'undefined' && dpadActiveDir === 'left')) s.angle -= 0.08;
    if (arcadeKeysDown['d'] || arcadeKeysDown['arrowright'] || (typeof dpadActiveDir !== 'undefined' && dpadActiveDir === 'right')) s.angle += 0.08;
    s.thrust = !!(arcadeKeysDown['w'] || arcadeKeysDown['arrowup'] || (typeof dpadActiveDir !== 'undefined' && dpadActiveDir === 'up'));
  }

  if (s.invulnerable > 0) s.invulnerable--;

  if (s.thrust) {
    s.vx += Math.cos(s.angle) * 0.14;
    s.vy += Math.sin(s.angle) * 0.14;
    if (asteroidsGame.tick % 10 === 0) playArcadeSfx('AST-THR');
  }
  s.vx *= 0.985;
  s.vy *= 0.985;
  s.x += s.vx;
  s.y += s.vy;

  if (s.x < 0) s.x += 240; else if (s.x > 240) s.x -= 240;
  if (s.y < 0) s.y += 240; else if (s.y > 240) s.y -= 240;

  // Bullets vs Rocks & Saucer
  for (let b = asteroidsGame.bullets.length - 1; b >= 0; b--) {
    const bl = asteroidsGame.bullets[b];
    bl.x += bl.vx;
    bl.y += bl.vy;
    if (bl.x < 0) bl.x += 240; else if (bl.x > 240) bl.x -= 240;
    if (bl.y < 0) bl.y += 240; else if (bl.y > 240) bl.y -= 240;
    bl.life--;
    if (bl.life <= 0) {
      asteroidsGame.bullets.splice(b, 1);
      continue;
    }

    // Bullet vs Saucer
    if (asteroidsGame.saucer.active) {
      const sc = asteroidsGame.saucer;
      if (Math.hypot(bl.x - sc.x, bl.y - sc.y) < (sc.type === 'large' ? 12 : 8)) {
        asteroidsGame.bullets.splice(b, 1);
        playArcadeSfx('AST-EXP');
        const pts = (sc.type === 'large') ? 200 : 1000;
        asteroidsGame.score += pts;
        if (asteroidsGame.score > asteroidsGame.highScore) asteroidsGame.highScore = asteroidsGame.score;
        sc.active = false;
        continue;
      }
    }

    // Bullet vs Rocks
    for (let r = asteroidsGame.rocks.length - 1; r >= 0; r--) {
      const rk = asteroidsGame.rocks[r];
      const dist = Math.hypot(bl.x - rk.x, bl.y - rk.y);
      if (dist < rk.radius) {
        asteroidsGame.bullets.splice(b, 1);
        playArcadeSfx('AST-EXP');
        const pts = (rk.size === 3) ? 20 : ((rk.size === 2) ? 50 : 100);
        asteroidsGame.score += pts;
        if (asteroidsGame.score > asteroidsGame.highScore) asteroidsGame.highScore = asteroidsGame.score;

        for (let d = 0; d < 6; d++) {
          asteroidsGame.debris.push({
            x: rk.x, y: rk.y,
            vx: (Math.random() - 0.5) * 3,
            vy: (Math.random() - 0.5) * 3,
            len: 4 + Math.random() * 4,
            angle: Math.random() * Math.PI * 2,
            vRot: (Math.random() - 0.5) * 0.2,
            life: 25
          });
        }

        if (rk.size > 1) {
          for (let sp = 0; sp < 2; sp++) {
            asteroidsGame.rocks.push({
              x: rk.x,
              y: rk.y,
              vx: (Math.random() - 0.5) * 2.2,
              vy: (Math.random() - 0.5) * 2.2,
              radius: (rk.size === 3) ? 10 : 5,
              size: rk.size - 1
            });
          }
        }
        asteroidsGame.rocks.splice(r, 1);
        break;
      }
    }
  }

  // Debris
  for (let d = asteroidsGame.debris.length - 1; d >= 0; d--) {
    const db = asteroidsGame.debris[d];
    db.x += db.vx;
    db.y += db.vy;
    db.angle += db.vRot;
    db.life--;
    if (db.life <= 0) asteroidsGame.debris.splice(d, 1);
  }

  // Alien Saucer UFO (Large 200 PTS / Small 1000 PTS)
  if (!asteroidsGame.saucer.active && asteroidsGame.tick % 450 === 0) {
    const isSmall = (asteroidsGame.score > 10000 || Math.random() < 0.35);
    asteroidsGame.saucer = {
      active: true,
      x: 0,
      y: Math.random() * 160 + 30,
      vx: isSmall ? 1.8 : 1.2,
      vy: Math.sin(asteroidsGame.tick * 0.05) * 0.5,
      type: isSmall ? 'small' : 'large',
      timer: 0
    };
    playArcadeSfx('AST-SAU');
  }

  if (asteroidsGame.saucer.active) {
    const sc = asteroidsGame.saucer;
    sc.x += sc.vx;
    sc.y += sc.vy;
    sc.timer++;
    if (sc.timer % 65 === 0) {
      // Small saucer fires target-leading sniper torpedo!
      let fireAngle = Math.random() * Math.PI * 2;
      if (sc.type === 'small') {
        fireAngle = Math.atan2(s.y - sc.y, s.x - sc.x) + (Math.random() - 0.5) * 0.2;
      }
      asteroidsGame.saucerBullets.push({
        x: sc.x,
        y: sc.y,
        vx: Math.cos(fireAngle) * 3.5,
        vy: Math.sin(fireAngle) * 3.5,
        life: 55
      });
      playArcadeSfx('AST-FIRE');
    }
    if (sc.x > 240) sc.active = false;
  }

  // Saucer Bullets
  for (let sb = asteroidsGame.saucerBullets.length - 1; sb >= 0; sb--) {
    const sbl = asteroidsGame.saucerBullets[sb];
    sbl.x += sbl.vx;
    sbl.y += sbl.vy;
    sbl.life--;
    if (sbl.life <= 0) {
      asteroidsGame.saucerBullets.splice(sb, 1);
      continue;
    }
    // Saucer bullet vs ship
    if (Math.hypot(sbl.x - s.x, sbl.y - s.y) < 8 && currentMode !== 'tour' && s.invulnerable <= 0) {
      asteroidsGame.saucerBullets.splice(sb, 1);
      playArcadeSfx('AST-DEATH');
      for (let d = 0; d < 6; d++) {
        asteroidsGame.debris.push({
          x: s.x, y: s.y,
          vx: (Math.random() - 0.5) * 3.5,
          vy: (Math.random() - 0.5) * 3.5,
          len: 5 + Math.random() * 5,
          angle: Math.random() * Math.PI * 2,
          vRot: (Math.random() - 0.5) * 0.25,
          life: 45
        });
      }
      s.x = 120; s.y = 120; s.vx = 0; s.vy = 0; s.invulnerable = 60;
      if (!arcadeImmortalMode) {
        asteroidsGame.lives--;
        if (asteroidsGame.lives <= 0) {
          asteroidsGame.gameOver = true;
          playArcadeSfx('DK-GAMEOVER');
        }
      }
    }
  }

  // Rocks Collision with Ship
  asteroidsGame.rocks.forEach(rk => {
    rk.x += rk.vx;
    rk.y += rk.vy;
    if (rk.x < 0) rk.x += 240; else if (rk.x > 240) rk.x -= 240;
    if (rk.y < 0) rk.y += 240; else if (rk.y > 240) rk.y -= 240;

    const dist = Math.hypot(s.x - rk.x, s.y - rk.y);
    if (dist < rk.radius + 5 && currentMode !== 'tour' && s.invulnerable <= 0) {
      playArcadeSfx('AST-DEATH');
      for (let d = 0; d < 6; d++) {
        asteroidsGame.debris.push({
          x: s.x, y: s.y,
          vx: (Math.random() - 0.5) * 3.5,
          vy: (Math.random() - 0.5) * 3.5,
          len: 5 + Math.random() * 5,
          angle: Math.random() * Math.PI * 2,
          vRot: (Math.random() - 0.5) * 0.25,
          life: 45
        });
      }
      s.x = 120; s.y = 120; s.vx = 0; s.vy = 0; s.invulnerable = 60;
      if (!arcadeImmortalMode) {
        asteroidsGame.lives--;
        if (asteroidsGame.lives <= 0) {
          asteroidsGame.gameOver = true;
          playArcadeSfx('DK-GAMEOVER');
        }
      }
    }
  });

  if (asteroidsGame.rocks.length === 0) {
    asteroidsGame.level++;
    playArcadeSfx('WARP');
    spawnAsteroidsField(4 + asteroidsGame.level);
  }
}

function renderAsteroidsGame() {
  if (!ctx) return;
  if (ctx.save) ctx.save();

  ctx.fillStyle = '#05070a';
  ctx.fillRect(0, 0, 240, 240);

  // Vector CRT Phosphor Glow
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = 1.4;
  ctx.shadowColor = '#00ffcc';
  ctx.shadowBlur = 6;

  ctx.fillStyle = '#ffffff';
  asteroidsGame.bullets.forEach(bl => {
    ctx.fillRect(bl.x - 1, bl.y - 1, 2, 2);
  });

  ctx.fillStyle = '#ff4757';
  asteroidsGame.saucerBullets.forEach(sbl => {
    ctx.fillRect(sbl.x - 1, sbl.y - 1, 2, 2);
  });

  asteroidsGame.debris.forEach(db => {
    ctx.save();
    ctx.translate(db.x, db.y);
    ctx.rotate(db.angle);
    ctx.beginPath();
    ctx.moveTo(-db.len / 2, 0); ctx.lineTo(db.len / 2, 0);
    ctx.stroke();
    ctx.restore();
  });

  asteroidsGame.rocks.forEach(rk => {
    ctx.beginPath();
    const pts = (rk.size === 3) ? 10 : ((rk.size === 2) ? 8 : 6);
    for (let i = 0; i < pts; i++) {
      const a = (i / pts) * Math.PI * 2;
      const r = rk.radius * (1 + Math.sin(i * 2.3 + rk.size) * 0.22);
      const px = rk.x + Math.cos(a) * r;
      const py = rk.y + Math.sin(a) * r;
      if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.stroke();
  });

  // Alien Saucer UFO (Large / Small)
  if (asteroidsGame.saucer.active) {
    const sc = asteroidsGame.saucer;
    const sr = (sc.type === 'large') ? 10 : 6;
    ctx.save();
    ctx.translate(sc.x, sc.y);
    ctx.beginPath();
    ctx.moveTo(-sr * 1.5, 0);
    ctx.lineTo(sr * 1.5, 0);
    ctx.lineTo(sr * 0.8, -sr * 0.6);
    ctx.lineTo(-sr * 0.8, -sr * 0.6);
    ctx.closePath();
    ctx.moveTo(-sr * 0.8, -sr * 0.6);
    ctx.lineTo(-sr * 0.4, -sr * 1.1);
    ctx.lineTo(sr * 0.4, -sr * 1.1);
    ctx.lineTo(sr * 0.8, -sr * 0.6);
    ctx.moveTo(-sr * 1.5, 0);
    ctx.lineTo(-sr * 0.7, sr * 0.5);
    ctx.lineTo(sr * 0.7, sr * 0.5);
    ctx.lineTo(sr * 1.5, 0);
    ctx.stroke();
    ctx.restore();
  }

  // Player Vector Ship
  const s = asteroidsGame.ship;
  if (!(s.invulnerable > 0 && (asteroidsGame.tick >> 2) % 2 === 0)) {
    ctx.save();
    ctx.translate(s.x, s.y);
    ctx.rotate(s.angle);
    ctx.beginPath();
    ctx.moveTo(9, 0);
    ctx.lineTo(-7, -6);
    ctx.lineTo(-4, 0);
    ctx.lineTo(-7, 6);
    ctx.closePath();
    ctx.stroke();

    if (s.thrust && (asteroidsGame.tick % 4 < 2)) {
      ctx.strokeStyle = '#ff9f43';
      ctx.beginPath();
      ctx.moveTo(-4, 0); ctx.lineTo(-11, 0);
      ctx.stroke();
    }
    ctx.restore();
  }

  ctx.shadowBlur = 0;

  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 8px monospace';
  ctx.fillText(String(asteroidsGame.score).padStart(6, '0'), 18, 16);
  ctx.fillText(`SECTOR ${asteroidsGame.level}`, 100, 16);
  for (let l = 0; l < asteroidsGame.lives; l++) {
    ctx.fillText('▲', 190 + l * 10, 16);
  }

  // Authentic Arcade Game Over Overlay
  if (asteroidsGame.gameOver) {
    ctx.fillStyle = 'rgba(5, 7, 10, 0.85)';
    ctx.fillRect(25, 95, 190, 52);
    ctx.strokeStyle = '#eb2f06';
    ctx.lineWidth = 2;
    if (ctx.strokeRect) ctx.strokeRect(25, 95, 190, 52);

    ctx.fillStyle = '#eb2f06';
    ctx.font = 'bold 15px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('GAME OVER', 120, 118);

    if ((asteroidsGame.tick >> 4) % 2 === 0) {
      ctx.fillStyle = '#f1c40f';
      ctx.font = 'bold 7px monospace';
      ctx.fillText('PRESS 1P START OR SPACE', 120, 136);
    }
    ctx.textAlign = 'start';
  }

  if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
  if (ctx.restore) ctx.restore();
}

function renderAsteroidsTour(f) {
  if (!asteroidsGame.active) initAsteroidsGame();
  updateAsteroidsGame();
  renderAsteroidsGame();
}

// -------------------------------------------------------------------------
// 5. TEMPEST (1981 ATARI COLOR VECTOR): FULLY PLAYABLE ARCADE ENGINE
// -------------------------------------------------------------------------
const tempestGame = {
  active: false,
  gameOver: false,
  segment: 0,
  shots: [],
  enemies: [],
  spikerTrails: [],
  score: 0,
  highScore: 25000,
  lives: 3,
  superzapperUsed: false,
  superzapperFlash: 0,
  tube: 9,
  tick: 0
};

function initTempestGame() {
  tempestGame.active = true;
  tempestGame.gameOver = false;
  tempestGame.segment = 0;
  tempestGame.shots = [];
  tempestGame.enemies = [];
  tempestGame.spikerTrails = [];
  tempestGame.score = 0;
  tempestGame.lives = (typeof arcadeImmortalMode !== 'undefined' && arcadeImmortalMode) ? 99 : 3;
  tempestGame.superzapperUsed = false;
  tempestGame.superzapperFlash = 0;
  tempestGame.tube = 9;
  tempestGame.tick = 0;
  spawnTempestEnemies();
  playArcadeSfx('TEM-FIRE');
}

function spawnTempestEnemies() {
  tempestGame.enemies = [];
  for (let i = 0; i < 4; i++) {
    tempestGame.enemies.push({
      seg: (i * 4) % 16,
      dist: 0.15 + i * 0.12,
      vDist: 0.0035,
      type: (i % 2 === 0) ? 'flipper' : 'spiker'
    });
  }
}

function tempestFire() {
  initAudio();
  if (tempestGame.gameOver) return;
  if (tempestGame.shots.length < 6) {
    tempestGame.shots.push({
      seg: tempestGame.segment,
      dist: 0.95,
      vDist: -0.055
    });
    playArcadeSfx('TEM-FIRE');
  }
}

function tempestSuperzapper() {
  initAudio();
  if (tempestGame.gameOver) return;
  if (!tempestGame.superzapperUsed) {
    tempestGame.superzapperUsed = true;
    tempestGame.superzapperFlash = 25;
    tempestGame.enemies.forEach(en => {
      tempestGame.score += 150;
    });
    tempestGame.enemies = [];
    playArcadeSfx('TEM-ZAP');
  }
}

function updateTempestGame() {
  if (tempestGame.gameOver) {
    if (arcadeKeysDown['1'] || arcadeKeysDown['5'] || arcadeKeysDown[' '] || arcadeKeysDown['enter'] || arcadeKeysDown['r']) {
      initTempestGame();
    }
    return;
  }

  tempestGame.tick++;

  // Authentic Atari POKEY Polyphonic Vector Pulse Arpeggio BGM
  if (!tempestGame.gameOver && !tempestGame.tubeCleared) {
    tempestGame.bgmTick = (tempestGame.bgmTick || 0) + 1;
    if (tempestGame.bgmTick % 12 === 0) {
      tempestGame.bgmStep = ((tempestGame.bgmStep || 0) + 1) % 8;
      playArcadeSfx('TEM-BGM');
    }
  }

  // Autonomous Tour AI
  if (currentMode === 'tour') {
    let closest = null, minD = -1;
    tempestGame.enemies.forEach(en => {
      if (en.dist > minD) { minD = en.dist; closest = en; }
    });
    if (closest) {
      const targetSeg = closest.seg;
      let diff = (targetSeg - tempestGame.segment + 16) % 16;
      if (diff > 8) diff -= 16;
      if (tempestGame.tick % 4 === 0) {
        if (diff > 0) tempestGame.segment = (tempestGame.segment + 1) % 16;
        else if (diff < 0) tempestGame.segment = (tempestGame.segment - 1 + 16) % 16;
      }
      if (tempestGame.tick % 10 === 0) tempestFire();
      if (minD > 0.85 && tempestGame.tick % 100 === 0) tempestSuperzapper();
    } else {
      if (tempestGame.tick % 14 === 0) tempestGame.segment = (tempestGame.segment + 1) % 16;
      if (tempestGame.tick % 16 === 0) tempestFire();
    }
  }

  if (tempestGame.superzapperFlash > 0) tempestGame.superzapperFlash--;

  // Shots vs Enemies
  for (let s = tempestGame.shots.length - 1; s >= 0; s--) {
    const sh = tempestGame.shots[s];
    sh.dist += sh.vDist;
    if (sh.dist <= 0) {
      tempestGame.shots.splice(s, 1);
      continue;
    }
    for (let e = tempestGame.enemies.length - 1; e >= 0; e--) {
      const en = tempestGame.enemies[e];
      if (en.seg === sh.seg && Math.abs(en.dist - sh.dist) < 0.08) {
        tempestGame.shots.splice(s, 1);
        tempestGame.enemies.splice(e, 1);
        tempestGame.score += 150;
        if (tempestGame.score > tempestGame.highScore) tempestGame.highScore = tempestGame.score;
        playArcadeSfx('AST-EXP');
        break;
      }
    }
  }

  // Enemies crawl up tube, somersault between channels
  tempestGame.enemies.forEach(en => {
    en.dist += en.vDist;
    if (en.type === 'flipper' && tempestGame.tick % 45 === 0) {
      en.seg = (en.seg + (Math.random() < 0.5 ? 1 : 15)) % 16;
      playArcadeSfx('TEM-FLIP');
    } else if (en.type === 'spiker' && tempestGame.tick % 60 === 0) {
      playArcadeSfx('TEM-SPIKE');
    }

    if (en.dist >= 1.0 && currentMode !== 'tour') {
      if (en.seg === tempestGame.segment) {
        playArcadeSfx('TEM-DEATH');
        tempestGame.enemies = [];
        spawnTempestEnemies();
        if (!arcadeImmortalMode) {
          tempestGame.lives--;
          if (tempestGame.lives <= 0) {
            tempestGame.gameOver = true;
            playArcadeSfx('DK-GAMEOVER');
          }
        }
      }
    }
  });

  if (tempestGame.enemies.length === 0) {
    tempestGame.tube++;
    tempestGame.superzapperUsed = false;
    playArcadeSfx('WARP');
    spawnTempestEnemies();
  }
}

function renderTempestGame() {
  if (!ctx) return;
  if (ctx.save) ctx.save();

  ctx.fillStyle = '#05070a';
  ctx.fillRect(0, 0, 240, 240);

  const cx = 120, cy = 125;
  const numSegs = 16;
  const rNear = 95, rFar = 22;

  // Superzapper Full Tube Flash
  if (tempestGame.superzapperFlash > 0) {
    ctx.strokeStyle = '#00e5ff';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    for (let i = 0; i < numSegs; i++) {
      const a = (i / numSegs) * Math.PI * 2;
      const nx = cx + Math.cos(a) * rNear;
      const ny = cy + Math.sin(a) * (rNear * 0.6);
      if (i === 0) ctx.moveTo(nx, ny); else ctx.lineTo(nx, ny);
    }
    ctx.closePath();
    ctx.stroke();
  }

  // Perspective 3D Vector Tube
  ctx.strokeStyle = '#00d2d3';
  ctx.lineWidth = 1.6;
  ctx.shadowColor = '#00e5ff';
  ctx.shadowBlur = 4;

  ctx.beginPath();
  for (let i = 0; i < numSegs; i++) {
    const a = (i / numSegs) * Math.PI * 2;
    const fx = cx + Math.cos(a) * rFar;
    const fy = cy + Math.sin(a) * (rFar * 0.6);
    if (i === 0) ctx.moveTo(fx, fy); else ctx.lineTo(fx, fy);
  }
  ctx.closePath();
  ctx.stroke();

  ctx.beginPath();
  for (let i = 0; i < numSegs; i++) {
    const a = (i / numSegs) * Math.PI * 2;
    const nx = cx + Math.cos(a) * rNear;
    const ny = cy + Math.sin(a) * (rNear * 0.6);
    if (i === 0) ctx.moveTo(nx, ny); else ctx.lineTo(nx, ny);
  }
  ctx.closePath();
  ctx.stroke();

  for (let i = 0; i < numSegs; i++) {
    const a = (i / numSegs) * Math.PI * 2;
    const nx = cx + Math.cos(a) * rNear;
    const ny = cy + Math.sin(a) * (rNear * 0.6);
    const fx = cx + Math.cos(a) * rFar;
    const fy = cy + Math.sin(a) * (rFar * 0.6);
    ctx.beginPath();
    ctx.moveTo(nx, ny); ctx.lineTo(fx, fy);
    ctx.stroke();
  }

  // Enemies (Flippers & Spikers)
  tempestGame.enemies.forEach(en => {
    const a = (en.seg + 0.5) / numSegs * Math.PI * 2;
    const r = rFar + (rNear - rFar) * en.dist;
    const ex = cx + Math.cos(a) * r;
    const ey = cy + Math.sin(a) * (r * 0.6);
    const scale = 0.8 + en.dist * 0.8;

    ctx.save();
    ctx.translate(ex, ey);
    if (en.type === 'flipper') {
      ctx.strokeStyle = '#eb2f06';
      ctx.beginPath();
      ctx.moveTo(-5 * scale, -5 * scale);
      ctx.lineTo(5 * scale, 5 * scale);
      ctx.lineTo(0, -6 * scale);
      ctx.closePath();
      ctx.stroke();
    } else {
      ctx.strokeStyle = '#2ed573';
      ctx.beginPath();
      ctx.arc(0, 0, 4 * scale, 0, Math.PI * 2);
      ctx.stroke();
    }
    ctx.restore();
  });

  // Particle Shots
  ctx.strokeStyle = '#f1c40f';
  ctx.lineWidth = 2.0;
  tempestGame.shots.forEach(sh => {
    const a = (sh.seg + 0.5) / numSegs * Math.PI * 2;
    const r = rFar + (rNear - rFar) * sh.dist;
    const sx = cx + Math.cos(a) * r;
    const sy = cy + Math.sin(a) * (r * 0.6);
    ctx.beginPath();
    ctx.moveTo(sx - 2, sy); ctx.lineTo(sx + 2, sy);
    ctx.stroke();
  });

  // Player Claw / Blaster on Rim
  const playerA = (tempestGame.segment + 0.5) / numSegs * Math.PI * 2;
  const px = cx + Math.cos(playerA) * rNear;
  const py = cy + Math.sin(playerA) * (rNear * 0.6);
  ctx.save();
  ctx.translate(px, py);
  ctx.rotate(playerA + Math.PI / 2);
  ctx.strokeStyle = '#f1c40f';
  ctx.lineWidth = 2.0;
  ctx.beginPath();
  ctx.moveTo(-7, -4);
  ctx.lineTo(0, 6);
  ctx.lineTo(7, -4);
  ctx.stroke();
  ctx.fillStyle = '#eb2f06';
  ctx.fillRect(-2, 2, 4, 3);
  ctx.restore();

  ctx.shadowBlur = 0;

  // Header & HUD
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 8px monospace';
  ctx.fillText(`SCORE: ${tempestGame.score}`, 18, 16);
  ctx.fillText(`TUBE ${tempestGame.tube}`, 108, 16);
  for (let l = 0; l < tempestGame.lives; l++) {
    ctx.fillText('⚡', 190 + l * 10, 16);
  }

  // Authentic Arcade Game Over Overlay
  if (tempestGame.gameOver) {
    ctx.fillStyle = 'rgba(5, 7, 10, 0.85)';
    ctx.fillRect(25, 95, 190, 52);
    ctx.strokeStyle = '#eb2f06';
    ctx.lineWidth = 2;
    if (ctx.strokeRect) ctx.strokeRect(25, 95, 190, 52);

    ctx.fillStyle = '#eb2f06';
    ctx.font = 'bold 15px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('GAME OVER', 120, 118);

    if ((tempestGame.tick >> 4) % 2 === 0) {
      ctx.fillStyle = '#f1c40f';
      ctx.font = 'bold 7px monospace';
      ctx.fillText('PRESS 1P START OR SPACE', 120, 136);
    }
    ctx.textAlign = 'start';
  }

  if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
  if (ctx.restore) ctx.restore();
}

function renderTempestTour(f) {
  if (!tempestGame.active) initTempestGame();
  updateTempestGame();
  renderTempestGame();
}

// -------------------------------------------------------------------------
// 6. GYRUSS (1983 KONAMI 5x PSG BAROQUE): FULLY PLAYABLE ARCADE ENGINE
// -------------------------------------------------------------------------
function gyrussAngleDiff(a1, a2) {
  let diff = (a1 - a2) % (Math.PI * 2);
  if (diff < -Math.PI) diff += Math.PI * 2;
  if (diff > Math.PI) diff -= Math.PI * 2;
  return Math.abs(diff);
}

const gyrussGame = {
  active: false,
  gameOver: false,
  angle: -Math.PI / 2,
  bankAngle: 0,
  invulnerable: 0,
  respawnTimer: 0,
  shots: [],
  enemies: [],
  bullets: [],
  explosions: [],
  stars: [],
  score: 0,
  highScore: 35000,
  lives: 3,
  warp: 3,
  stage: 1,
  destPlanet: 'NEPTUNE',
  tick: 0
};

function initGyrussGame() {
  gyrussGame.active = true;
  gyrussGame.gameOver = false;
  gyrussGame.angle = -Math.PI / 2;
  gyrussGame.bankAngle = 0;
  gyrussGame.invulnerable = 60;
  gyrussGame.respawnTimer = 0;
  gyrussGame.shots = [];
  gyrussGame.enemies = [];
  gyrussGame.bullets = [];
  gyrussGame.explosions = [];
  gyrussGame.stars = [];
  gyrussGame.score = 0;
  gyrussGame.lives = (typeof arcadeImmortalMode !== 'undefined' && arcadeImmortalMode) ? 99 : 3;
  gyrussGame.warp = 3;
  gyrussGame.stage = 1;
  gyrussGame.destPlanet = 'NEPTUNE';
  gyrussGame.tick = 0;

  for (let i = 0; i < 48; i++) {
    gyrussGame.stars.push({
      angle: Math.random() * Math.PI * 2,
      dist: Math.random() * 110 + 6,
      speed: 1.2 + Math.random() * 2.2
    });
  }

  playArcadeSfx('GYRUSS-TUNE');
}

function killGyrussShip() {
  const g = gyrussGame;
  if (g.invulnerable > 0 || g.gameOver) return;
  const cx = 120, cy = 125;
  const sx = cx + Math.cos(g.angle) * 96;
  const sy = cy + Math.sin(g.angle) * 96;
  g.explosions.push({ x: sx, y: sy, frame: 0 });
  playArcadeSfx('GYRUSS-EXP');
  g.respawnTimer = 40;
  g.invulnerable = 90;
  if (!arcadeImmortalMode) {
    g.lives--;
    if (g.lives <= 0) {
      g.gameOver = true;
      playArcadeSfx('DK-GAMEOVER');
    }
  }
}

function gyrussFire() {
  initAudio();
  if (gyrussGame.gameOver || gyrussGame.respawnTimer > 0) return;
  if (gyrussGame.shots.length < 6) {
    const a = gyrussGame.angle;
    gyrussGame.shots.push({ angle: a - 0.05, dist: 96, vDist: -4.8 });
    gyrussGame.shots.push({ angle: a + 0.05, dist: 96, vDist: -4.8 });
    playArcadeSfx('GYRUSS-LAS');
  }
}

function updateGyrussGame() {
  const g = gyrussGame;

  // Starfield zoom runs always for atmospheric background
  g.stars.forEach(st => {
    st.dist += st.speed;
    if (st.dist > 115) {
      st.dist = 6;
      st.angle = Math.random() * Math.PI * 2;
    }
  });

  // Explosions update
  for (let ex = g.explosions.length - 1; ex >= 0; ex--) {
    g.explosions[ex].frame++;
    if (g.explosions[ex].frame > 18) g.explosions.splice(ex, 1);
  }

  if (g.gameOver) {
    if (arcadeKeysDown['1'] || arcadeKeysDown['5'] || arcadeKeysDown[' '] || arcadeKeysDown['enter'] || arcadeKeysDown['r']) {
      initGyrussGame();
    }
    return;
  }

  g.tick++;
  if (g.invulnerable > 0) g.invulnerable--;
  if (g.respawnTimer > 0) {
    g.respawnTimer--;
    return;
  }

  // Authentic Konami J.S. Bach Toccata & Fugue in D minor BWV 565 BGM Engine
  if (!g.gameOver) {
    g.bgmTick = (g.bgmTick || 0) + 1;
    if (g.bgmTick % 8 === 0) {
      g.bgmStep = ((g.bgmStep || 0) + 1) % 42;
      playArcadeSfx('GYRUSS-BGM');
    }
  }

  // Tour AI or Playable input
  if (currentMode === 'tour') {
    g.angle += 0.055;
    g.bankAngle = 0.25;
    if (g.tick % 12 === 0) gyrussFire();
  } else {
    let rotating = false;
    if (arcadeKeysDown['a'] || arcadeKeysDown['arrowleft'] || (typeof dpadActiveDir !== 'undefined' && dpadActiveDir === 'left')) {
      g.angle -= 0.07;
      g.bankAngle = -0.35;
      rotating = true;
    }
    if (arcadeKeysDown['d'] || arcadeKeysDown['arrowright'] || (typeof dpadActiveDir !== 'undefined' && dpadActiveDir === 'right')) {
      g.angle += 0.07;
      g.bankAngle = 0.35;
      rotating = true;
    }
    if (!rotating) g.bankAngle *= 0.8;
  }
  // Keep angle cleanly normalized in [0, 2*PI)
  g.angle = (g.angle % (Math.PI * 2) + Math.PI * 2) % (Math.PI * 2);

  // Shots update
  for (let s = g.shots.length - 1; s >= 0; s--) {
    const sh = g.shots[s];
    sh.dist += sh.vDist;
    if (sh.dist <= 8) {
      g.shots.splice(s, 1);
      continue;
    }
    for (let e = g.enemies.length - 1; e >= 0; e--) {
      const en = g.enemies[e];
      if (gyrussAngleDiff(en.angle, sh.angle) < 0.28 && Math.abs(en.dist - sh.dist) < 14) {
        g.shots.splice(s, 1);
        const cx = 120, cy = 125;
        g.explosions.push({ x: cx + Math.cos(en.angle) * en.dist, y: cy + Math.sin(en.angle) * en.dist, frame: 0 });
        g.enemies.splice(e, 1);
        g.score += 200;
        if (g.score > g.highScore) g.highScore = g.score;
        playArcadeSfx('GYRUSS-EXP');
        break;
      }
    }
  }

  // Spiral entrance waves
  if (g.tick % 40 === 0) {
    g.enemies.push({
      angle: Math.random() * Math.PI * 2,
      dist: 10,
      vDist: 1.4,
      vAngle: (Math.random() - 0.5) * 0.05
    });
  }

  // Enemy movement, bullets & player collision
  for (let e = g.enemies.length - 1; e >= 0; e--) {
    const en = g.enemies[e];
    en.dist += en.vDist;
    en.angle = (en.angle + en.vAngle + Math.PI * 2) % (Math.PI * 2);

    // Enemies fire plasma bullets outward toward perimeter
    if (en.dist > 28 && en.dist < 78 && Math.random() < 0.015 && g.bullets.length < 5) {
      g.bullets.push({
        angle: en.angle,
        dist: en.dist,
        vDist: 2.2
      });
    }

    // Direct collision with player ship at radius ~96
    if (en.dist >= 86 && en.dist <= 104 && currentMode !== 'tour' && g.invulnerable <= 0 && !g.gameOver) {
      if (gyrussAngleDiff(en.angle, g.angle) < 0.28) {
        g.enemies.splice(e, 1);
        killGyrussShip();
        continue;
      }
    }
    if (en.dist > 115) {
      g.enemies.splice(e, 1);
    }
  }

  // Enemy Bullets movement & collision
  for (let b = g.bullets.length - 1; b >= 0; b--) {
    const bl = g.bullets[b];
    bl.dist += bl.vDist;
    if (bl.dist >= 86 && bl.dist <= 104 && currentMode !== 'tour' && g.invulnerable <= 0 && !g.gameOver) {
      if (gyrussAngleDiff(bl.angle, g.angle) < 0.25) {
        g.bullets.splice(b, 1);
        killGyrussShip();
        continue;
      }
    }
    if (bl.dist > 115) {
      g.bullets.splice(b, 1);
    }
  }

  if (g.tick % 600 === 0 && g.warp > 0) {
    g.warp--;
    playArcadeSfx('GYRUSS-WARP');
    if (g.warp <= 0) {
      const planets = ['NEPTUNE', 'URANUS', 'SATURN', 'JUPITER', 'MARS', 'EARTH'];
      g.score += 1000 * (g.stage || 1);
      if (g.score > g.highScore) g.highScore = g.score;
      g.stage = (g.stage || 1) + 1;
      g.warp = 3;
      g.destPlanet = planets[(g.stage - 1) % planets.length];
    }
  }
}

function renderGyrussGame() {
  if (!ctx) return;
  if (ctx.save) ctx.save();

  ctx.fillStyle = '#05070a';
  ctx.fillRect(0, 0, 240, 240);

  const cx = 120, cy = 125;

  // Radial 3D Starfield
  ctx.fillStyle = '#ffffff';
  gyrussGame.stars.forEach(st => {
    const sx = cx + Math.cos(st.angle) * st.dist;
    const sy = cy + Math.sin(st.angle) * st.dist;
    const sz = (st.dist / 110) * 1.8;
    ctx.fillRect(sx, sy, sz, sz);
  });

  // Concentric Polar Warp Rings
  for (let r = 24; r <= 100; r += 24) {
    ctx.strokeStyle = `rgba(0, 229, 255, ${0.15 + (r / 100) * 0.35})`;
    ctx.lineWidth = 1.0;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();
  }

  // Lasers
  ctx.fillStyle = '#f1c40f';
  gyrussGame.shots.forEach(sh => {
    const lx = cx + Math.cos(sh.angle) * sh.dist;
    const ly = cy + Math.sin(sh.angle) * sh.dist;
    ctx.fillRect(lx - 1, ly - 1, 3, 3);
  });

  // Enemy Bullets (pulsating plasma orbs)
  gyrussGame.bullets.forEach(bl => {
    const bx = cx + Math.cos(bl.angle) * bl.dist;
    const by = cy + Math.sin(bl.angle) * bl.dist;
    ctx.fillStyle = (gyrussGame.tick % 4 < 2) ? '#ff3838' : '#f1c40f';
    ctx.beginPath();
    ctx.arc(bx, by, 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(bx - 1, by - 1, 2, 2);
  });

  // Enemies
  gyrussGame.enemies.forEach(en => {
    const ex = cx + Math.cos(en.angle) * en.dist;
    const ey = cy + Math.sin(en.angle) * en.dist;
    const scale = 0.5 + (en.dist / 100) * 0.8;
    ctx.save();
    ctx.translate(ex, ey);
    ctx.rotate(en.angle + Math.PI / 2);
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(-6 * scale, -4 * scale, 12 * scale, 8 * scale);
    ctx.fillStyle = '#00e5ff';
    ctx.fillRect(-8 * scale, -2 * scale, 16 * scale, 4 * scale);
    ctx.restore();
  });

  // Explosions
  gyrussGame.explosions.forEach(ep => {
    const r = ep.frame * 1.5;
    ctx.strokeStyle = (ep.frame % 2 === 0) ? '#ff3838' : '#f1c40f';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(ep.x, ep.y, r, 0, Math.PI * 2);
    ctx.stroke();
  });

  // 360° Banked Player Starfighter
  if (!gyrussGame.gameOver && (gyrussGame.invulnerable <= 0 || (gyrussGame.tick % 6 < 3))) {
    const shipA = gyrussGame.angle;
    const shipDist = 96;
    const sx = cx + Math.cos(shipA) * shipDist;
    const sy = cy + Math.sin(shipA) * shipDist;
    ctx.save();
    ctx.translate(sx, sy);
    ctx.rotate(shipA + Math.PI / 2 + gyrussGame.bankAngle);
    ctx.fillStyle = '#0652dd';
    ctx.fillRect(-6, -4, 12, 8);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(-2, -7, 4, 6);
    ctx.fillStyle = '#ff3838';
    ctx.fillRect(-8, 0, 3, 5); ctx.fillRect(5, 0, 3, 5);
    ctx.fillStyle = '#f1c40f';
    ctx.fillRect(-4, 3, 8, 2);
    ctx.restore();
  }

  // Header & HUD
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 8px monospace';
  ctx.fillText(`SCORE: ${gyrussGame.score}`, 18, 16);
  ctx.fillStyle = '#f1c40f';
  ctx.fillText(`WARP ${gyrussGame.warp} TO ${gyrussGame.destPlanet}`, 80, 16);
  ctx.fillStyle = '#00e5ff';
  for (let l = 0; l < gyrussGame.lives; l++) {
    ctx.fillText('🚀', 190 + l * 10, 16);
  }

  // Authentic Arcade Game Over Overlay
  if (gyrussGame.gameOver) {
    ctx.fillStyle = 'rgba(5, 7, 10, 0.85)';
    ctx.fillRect(25, 95, 190, 52);
    ctx.strokeStyle = '#eb2f06';
    ctx.lineWidth = 2;
    if (ctx.strokeRect) ctx.strokeRect(25, 95, 190, 52);

    ctx.fillStyle = '#eb2f06';
    ctx.font = 'bold 15px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('GAME OVER', 120, 118);

    if ((gyrussGame.tick >> 4) % 2 === 0) {
      ctx.fillStyle = '#f1c40f';
      ctx.font = 'bold 7px monospace';
      ctx.fillText('PRESS 1P START OR SPACE', 120, 136);
    }
    ctx.textAlign = 'start';
  }

  if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
  if (ctx.restore) ctx.restore();
}

function renderGyrussTour(f) {
  if (!gyrussGame.active) initGyrussGame();
  updateGyrussGame();
  renderGyrussGame();
}

// -------------------------------------------------------------------------
// INSTALLED ROMS ATTRACT TOUR DEMO ENGINE
// -------------------------------------------------------------------------
const tourState = {
  active: false,
  paused: false,
  gameIdx: 0,
  frameInGame: 0,
  framesPerGame: 540,
  games: [
    { id: 'pacman', title: 'PAC-MAN', year: '1980 NAMCO', cpu: 'Z80 @ 3.072 MHz', sound: 'Namco WSG (3-ch Wavetable)', badge: 'MAZE CHASE' },
    { id: 'cclimber', title: 'CRAZY CLIMBER', year: '1980 NICHIBUTSU', cpu: 'Z80 @ 3.072 MHz', sound: 'AY-3-8910 PSG (Twin-Stick)', badge: 'VERTICAL CLIMB' },
    { id: 'galaga', title: 'GALAGA', year: '1981 NAMCO', cpu: '3× Z80 Cores', sound: 'Namco WSG 3-Voice Soundchip', badge: 'SPACE SHOOTER' },
    { id: 'dkong', title: 'DONKEY KONG', year: '1981 NINTENDO', cpu: 'Z80 + I8035 Co-processor', sound: 'Discrete DAC & Jump FX', badge: 'PLATFORM ICON' },
    { id: 'frogger', title: 'FROGGER', year: '1981 KONAMI', cpu: '2× Z80 Processors', sound: 'AY-3-8910 Chiptune Jingles', badge: 'TRAFFIC & RIVER' },
    { id: 'asteroids', title: 'ASTEROIDS', year: '1979 ATARI', cpu: 'MOS 6502 @ 1.5 MHz', sound: 'Discrete Analog Thruster / Saucer', badge: 'VECTOR GLOW' },
    { id: 'tempest', title: 'TEMPEST', year: '1981 ATARI', cpu: 'MOS 6502 + Math Box', sound: 'Dual Atari POKEY Soundchips', badge: 'ROTARY TUBE' },
    { id: 'gyruss', title: 'GYRUSS', year: '1983 KONAMI', cpu: '2× Z80 + 6809 Sound CPU', sound: '5× AY-3-8910 (15-Ch Orchestral)', badge: '360° COSMIC ODYSSEY' }
  ]
};

function toggleTourDemo() {
  initAudio();
  if (currentMode === 'tour') setMode('arcade'); else setMode('tour');
}

function toggleTourPause() {
  initAudio();
  if (currentMode !== 'tour') {
    setMode('tour');
    tourState.paused = false;
  } else {
    tourState.paused = !tourState.paused;
  }
  const btn = document.getElementById('btnTourPause');
  if (btn) {
    btn.textContent = tourState.paused ? '▶ RESUME TOUR' : '⏸ PAUSE TOUR';
    btn.classList.toggle('active', tourState.paused);
  }
  const hud = document.getElementById('hudStatus');
  if (hud) hud.textContent = tourState.paused ? '● TOUR DEMO PAUSED' : '● TOUR DEMO ACTIVE';
  return tourState.paused;
}

function nextTourGame() {
  initAudio();
  if (typeof stopCurrentGame === 'function') stopCurrentGame();
  tourState.frameInGame = 0;
  tourState.gameIdx = (tourState.gameIdx + 1) % tourState.games.length;
  const g = tourState.games[tourState.gameIdx];
  switchActiveGame(g.id);
  setMode('tour');
}

function prevTourGame() {
  initAudio();
  if (typeof stopCurrentGame === 'function') stopCurrentGame();
  tourState.frameInGame = 0;
  tourState.gameIdx = (tourState.gameIdx - 1 + tourState.games.length) % tourState.games.length;
  const g = tourState.games[tourState.gameIdx];
  switchActiveGame(g.id);
  setMode('tour');
}

function launchCurrentTourGame() {
  initAudio();
  tourState.paused = false;
  const g = tourState.games[tourState.gameIdx];
  switchActiveGame(g.id);
  setMode('arcade');
}

function renderTourDemo() {
  if (!tourState.active) return;
  const g = tourState.games[tourState.gameIdx];
  if (!tourState.paused) {
    tourState.frameInGame++;
    if (tourState.frameInGame > 300) {
      nextTourGame();
      return;
    }
  }

  switch (g.id) {
    case 'pacman':
      renderArcadeFrame();
      break;
    case 'cclimber':
      renderCrazyClimber();
      break;
    case 'galaga':
      renderGalagaTour(tourState.frameInGame);
      break;
    case 'dkong':
      renderDonkeyKongTour(tourState.frameInGame);
      break;
    case 'frogger':
      renderFroggerTour(tourState.frameInGame);
      break;
    case 'asteroids':
      renderAsteroidsTour(tourState.frameInGame);
      break;
    case 'tempest':
      renderTempestTour(tourState.frameInGame);
      break;
    case 'gyruss':
      renderGyrussTour(tourState.frameInGame);
      break;
    default:
      renderArcadeFrame();
  }

  renderTourHud(g, tourState.frameInGame);
}

function renderTourHud(game, f) {
  ctx.fillStyle = 'rgba(6, 9, 14, 0.92)';
  ctx.fillRect(0, 0, 240, 26);

  ctx.fillStyle = '#f5a623';
  ctx.font = 'bold 10px monospace';
  ctx.fillText(`★ TOUR: ${game.title}`, 8, 12);

  ctx.fillStyle = '#9aa0a6';
  ctx.font = '8px monospace';
  ctx.fillText(`${game.year} · ${game.badge}`, 8, 22);

  ctx.fillStyle = 'rgba(6, 9, 14, 0.92)';
  ctx.fillRect(0, 214, 240, 26);

  ctx.fillStyle = '#00e5ff';
  ctx.font = 'bold 8px monospace';
  ctx.fillText(`HW: ${game.cpu}`, 8, 225);

  const pulse = Math.sin(f * 0.15) > 0;
  ctx.fillStyle = pulse ? '#fffa65' : '#ffffff';
  ctx.font = 'bold 9px monospace';
  ctx.fillText('⚡ TAP / SPACE TO PLAY NOW!', 34, 236);
}
"""
        script_body = script_body[:idx_cc] + new_games_block + script_body[idx_td:]

    # 4. Update setupKnob to support needle and stepper buttons
    old_setupknob = """function setupKnob(id, min, max, initial, format, onChange) {
  const dial = document.getElementById(id);
  const arc = document.getElementById(id + '-arc');
  let val = initial;
  let startY = 0, startVal = 0;

  function updateVisual() {
    const pct = Math.max(0, Math.min(1, (val - min) / (max - min)));
    dial.style.transform = `rotate(${(pct * 270) - 135}deg)`;
    if (arc) {
      const circ = 125.66;
      arc.style.strokeDasharray = circ;
      arc.style.strokeDashoffset = circ - (pct * 94.25);
    }
    onChange(val);
  }

  dial.onmousedown = (e) => {
    initAudio();
    startY = e.clientY;
    startVal = val;
    const moveFn = (me) => {
      const dy = startY - me.clientY;
      const delta = (dy / 120) * (max - min);
      val = Math.max(min, Math.min(max, startVal + delta));
      updateVisual();
    };
    const upFn = () => {
      if (window.removeEventListener) {
        window.removeEventListener('mousemove', moveFn);
        window.removeEventListener('mouseup', upFn);
      }
      window.onmousemove = null;
    };
    if (window.addEventListener) {
      window.addEventListener('mousemove', moveFn);
      window.addEventListener('mouseup', upFn);
    } else {
      window.onmousemove = moveFn;
      window.onmouseup = upFn;
    }
  };

  // Mouse wheel support
  if (dial.addEventListener) {
    dial.addEventListener('wheel', (e) => {
      e.preventDefault();
      initAudio();
      const step = (max - min) / 32;
      const delta = e.deltaY < 0 ? step : -step;
      val = Math.max(min, Math.min(max, val + delta));
      updateVisual();
    }, { passive: false });

    // Touch screen support
    dial.addEventListener('touchstart', (e) => {
      initAudio();
      startY = e.touches[0].clientY;
      startVal = val;
    }, { passive: true });
    window.addEventListener('touchmove', (e) => {
      if (!startY) return;
      const dy = startY - e.touches[0].clientY;
      const delta = (dy / 120) * (max - min);
      val = Math.max(min, Math.min(max, startVal + delta));
      updateVisual();
    }, { passive: true });
    window.addEventListener('touchend', () => { startY = 0; });
  }

  // Double click reset to initial value
  dial.ondblclick = () => {
    val = initial;
    updateVisual();
  };

  updateVisual();
}"""

    new_setupknob = """function setupKnob(id, min, max, initial, format, onChange) {
  const dial = document.getElementById(id);
  if (!dial) return;
  const needle = dial.querySelector ? dial.querySelector('i') : null;
  let val = initial;
  let startY = 0, startVal = 0;

  function updateVisual() {
    const pct = Math.max(0, Math.min(1, (val - min) / (max - min)));
    const angle = (pct * 270) - 135;
    if (dial.style && dial.style.setProperty) dial.style.setProperty('--angle', `${angle}deg`);
    if (needle && needle.style) needle.style.transform = `rotate(${angle}deg)`;
    dial.style.transform = `rotate(${angle}deg)`;
    onChange(val);
  }

  dial.onmousedown = (e) => {
    initAudio();
    startY = e.clientY;
    startVal = val;
    const moveFn = (me) => {
      const dy = startY - me.clientY;
      const delta = (dy / 120) * (max - min);
      val = Math.max(min, Math.min(max, startVal + delta));
      updateVisual();
    };
    const upFn = () => {
      if (window.removeEventListener) {
        window.removeEventListener('mousemove', moveFn);
        window.removeEventListener('mouseup', upFn);
      }
      window.onmousemove = null;
    };
    if (window.addEventListener) {
      window.addEventListener('mousemove', moveFn);
      window.addEventListener('mouseup', upFn);
    } else {
      window.onmousemove = moveFn;
      window.onmouseup = upFn;
    }
  };

  // Stepper plus / minus buttons
  const minusBtn = document.getElementById(id + '-minus');
  const plusBtn = document.getElementById(id + '-plus');
  if (minusBtn) minusBtn.onclick = () => {
    initAudio();
    const step = (max - min) / 32;
    val = Math.max(min, Math.min(max, val - step));
    updateVisual();
  };
  if (plusBtn) plusBtn.onclick = () => {
    initAudio();
    const step = (max - min) / 32;
    val = Math.max(min, Math.min(max, val + step));
    updateVisual();
  };

  // Mouse wheel support
  if (dial.addEventListener) {
    dial.addEventListener('wheel', (e) => {
      e.preventDefault();
      initAudio();
      const step = (max - min) / 32;
      const delta = e.deltaY < 0 ? step : -step;
      val = Math.max(min, Math.min(max, val + delta));
      updateVisual();
    }, { passive: false });

    // Touch screen support
    dial.addEventListener('touchstart', (e) => {
      initAudio();
      startY = e.touches[0].clientY;
      startVal = val;
    }, { passive: true });
    window.addEventListener('touchmove', (e) => {
      if (!startY) return;
      const dy = startY - e.touches[0].clientY;
      const delta = (dy / 120) * (max - min);
      val = Math.max(min, Math.min(max, startVal + delta));
      updateVisual();
    }, { passive: true });
    window.addEventListener('touchend', () => { startY = 0; });
  }

  // Double click reset to initial value
  dial.ondblclick = () => {
    val = initial;
    updateVisual();
  };

  updateVisual();
}"""

    
    # 4b. Ensure instant Pac-Man boot and crisp single scanline pass
    old_ctrls = """function ensurePastBoot() {
  let safety = 0;
  while (animTick < 305 && safety < 350) {
    stepCpuFrame();
    safety++;
  }
}

function insertCoin() {
  initAudio();
  ensurePastBoot();
  playArcadeSfx('COIN');
  coinPulseFrames = 12; // 6 frames down, 6 frames up
  keyCoin = true;
  setTimeout(() => { keyCoin = false; }, 200);
}

function start1P() {
  initAudio();
  ensurePastBoot();
  startPulseFrames = 12; // 6 frames down, 6 frames up
  keyStart = true;
  setTimeout(() => { keyStart = false; }, 200);
}

function quickPlay() {
  initAudio();
  setMode('arcade');
  ensurePastBoot();
  
  const credits = ram[0x4e69 - 0x4000];
  if (credits === 0) {
    playArcadeSfx('COIN');
    coinPulseFrames = 14;
    keyCoin = true;
    setTimeout(() => {
      keyCoin = false;
      setTimeout(() => {
        startPulseFrames = 14;
        keyStart = true;
        setTimeout(() => { keyStart = false; }, 180);
      }, 80);
    }, 120);
  } else {
    startPulseFrames = 14;
    keyStart = true;
    setTimeout(() => { keyStart = false; }, 180);
  }

  document.getElementById('hudStatus').className = 'hud-badge';
  document.getElementById('hudStatus').textContent = '● PLAYING: LIVE!';
}"""
    new_ctrls = """let activeGameTimeouts = [];
function safeTimeout(fn, delay) {
  const id = setTimeout(() => {
    const idx = activeGameTimeouts.indexOf(id);
    if (idx !== -1) activeGameTimeouts.splice(idx, 1);
    fn();
  }, delay);
  activeGameTimeouts.push(id);
  return id;
}

function ensurePastBoot() {
  let safety = 0;
  while (animTick < 320 && safety < 350) {
    stepCpuFrame();
    safety++;
  }
}

function insertCoin() {
  initAudio();
  playArcadeSfx('COIN');
  if (activeGame === 'pacman') {
    ensurePastBoot();
    coinPulseFrames = 12;
    keyCoin = true;
    safeTimeout(() => { keyCoin = false; }, 200);
  } else if (activeGame === 'cclimber') {
    climberState.credits = (climberState.credits || 0) + 1;
  } else if (activeGame === 'galaga') {
    galagaGame.credits = (galagaGame.credits || 0) + 1;
  } else if (activeGame === 'dkong') {
    dkongGame.credits = (dkongGame.credits || 0) + 1;
  } else if (activeGame === 'frogger') {
    froggerGame.credits = (froggerGame.credits || 0) + 1;
  } else if (activeGame === 'asteroids') {
    asteroidsGame.credits = (asteroidsGame.credits || 0) + 1;
  } else if (activeGame === 'tempest') {
    tempestGame.credits = (tempestGame.credits || 0) + 1;
  } else if (activeGame === 'gyruss') {
    gyrussGame.credits = (gyrussGame.credits || 0) + 1;
  }
}

function start1P() {
  initAudio();
  playArcadeSfx('START');
  if (activeGame === 'pacman') {
    ensurePastBoot();
    if (typeof ram !== 'undefined' && ram && ram[0x4e69 - 0x4000] === 0) {
      ram[0x4e69 - 0x4000] = 1;
    }
    startPulseFrames = 12;
    keyStart = true;
    safeTimeout(() => { keyStart = false; }, 200);
  } else if (activeGame === 'cclimber') {
    initCrazyClimberGame();
    if (arcadeImmortalMode) climberState.lives = 99;
  } else if (activeGame === 'galaga') {
    initGalagaGame();
  } else if (activeGame === 'dkong') {
    initDonkeyKongGame();
  } else if (activeGame === 'frogger') {
    initFroggerGame();
  } else if (activeGame === 'asteroids') {
    initAsteroidsGame();
  } else if (activeGame === 'tempest') {
    initTempestGame();
  } else if (activeGame === 'gyruss') {
    initGyrussGame();
  }
}

function quickPlay() {
  initAudio();
  setMode('arcade');
  if (activeGame === 'pacman') {
    ensurePastBoot();
    const credits = ram[0x4e69 - 0x4000];
    if (credits === 0) {
      playArcadeSfx('COIN');
      coinPulseFrames = 14;
      keyCoin = true;
      safeTimeout(() => {
        keyCoin = false;
        safeTimeout(() => {
          playArcadeSfx('START');
          startPulseFrames = 14;
          keyStart = true;
          safeTimeout(() => { keyStart = false; }, 180);
        }, 100);
      }, 180);
    } else {
      startPulseFrames = 14;
      keyStart = true;
      safeTimeout(() => { keyStart = false; }, 180);
    }
  } else {
    start1P();
  }

  const elStat = document.getElementById('hudStatus');
  if (elStat) {
    elStat.className = 'hud-badge';
    elStat.textContent = '● PLAYING: LIVE!';
  }
}"""
    script_body = script_body.replace(old_ctrls, new_ctrls)

    script_body = script_body.replace(
        """function renderTourDemo() {
  tourState.frameInGame++;
  const f = tourState.frameInGame;
  const game = tourState.games[tourState.gameIdx];

  if (tourState.frameInGame >= tourState.framesPerGame) {
    nextTourGame();
    return;
  }""",
        """function renderTourDemo() {
  if (!tourState.paused) {
    tourState.frameInGame++;
  }
  const f = tourState.frameInGame;
  const game = tourState.games[tourState.gameIdx];

  if (!tourState.paused && tourState.frameInGame >= tourState.framesPerGame) {
    nextTourGame();
    return;
  }"""
    )

    script_body = script_body.replace(
        """  switch (game.id) {
    case 'pacman':
      renderArcadeFrame();
      break;""",
        """  switch (game.id) {
    case 'pacman':
      ensurePastBoot();
      stepCpuFrame();
      renderArcadeFrame();
      break;"""
    )

    old_cpu_block = """  // During boot test (< frame 305), run CPU at 5x speed so game boots in < 0.6 seconds!
  if (animTick < 305) {
    for (let fast = 0; fast < 5 && animTick < 305; fast++) {
      stepCpuFrame();
    }
  } else {
    // Normal 60 Hz frame
    if (currentMode === 'arcade' || currentMode === 'glitch') {
      stepCpuFrame();

      // Save state to rewind ring buffer
      if (animTick % 2 === 0) {
        if (rewindBuffer.length >= 300) rewindBuffer.shift();
        rewindBuffer.push({
          ram: new Uint8Array(ram),
          spritePos: new Uint8Array(spritePos)
        });
      }
    } else if (isRewinding) {
      if (rewindBuffer.length > 0) {
        const snap = rewindBuffer.pop();
        ram.set(snap.ram);
        spritePos.set(snap.spritePos);
      }
    }
  }

  // Update HUD info
  const credits = ram[0x4e69 - 0x4000];
  document.getElementById('hudCredits').textContent = `CREDITS: ${credits}`;
  if (animTick < 305) {
    document.getElementById('hudStatus').className = 'hud-badge booting';
    document.getElementById('hudStatus').textContent = '● BOOTING TEST...';
  } else if (credits === 0) {
    document.getElementById('hudStatus').className = 'hud-badge attract';
    document.getElementById('hudStatus').textContent = '● ATTRACT (INSERT COIN)';
  } else {
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● PLAYING: READY!';
  }"""
    new_cpu_block = """  // Pac-Man CPU execution: STRICTLY isolated to when Pac-Man is the selected active game!
  const isPacmanRunning = ((currentMode === 'arcade' || currentMode === 'glitch' || currentMode === 'rewind') && activeGame === 'pacman') ||
                          (currentMode === 'tour' && tourState.games[tourState.gameIdx] && tourState.games[tourState.gameIdx].id === 'pacman');

  if (isPacmanRunning) {
    if (animTick < 320) {
      ensurePastBoot();
    } else if (currentMode === 'arcade' || currentMode === 'glitch') {
      stepCpuFrame();
    }
  } else {
    // Pac-Man is NOT running: completely silence WSG wavetable audio voices so NO sound leaks!
    for (let ch = 0; ch < 3; ch++) {
      if (wsgVoices && wsgVoices[ch]) {
        wsgVoices[ch].vol = 0;
        wsgVoices[ch].freq = 0;
      }
    }
  }

  // Universal 8-Game State Ring Buffer for Hardware Rewind
  if (currentMode === 'arcade' || currentMode === 'glitch') {
    if (typeof captureRewindSnapshot === 'function') {
      if (rewindBuffer.length >= 300) rewindBuffer.shift();
      rewindBuffer.push(captureRewindSnapshot());
    }
  } else if (currentMode === 'rewind' || isRewinding) {
    if (rewindBuffer.length > 0 && typeof applyRewindSnapshot === 'function') {
      const snap = rewindBuffer.pop();
      applyRewindSnapshot(snap);
    }
  }

  // Update HUD info for active game
  const elCred = document.getElementById('hudCredits');
  const elStat = document.getElementById('hudStatus');
  if (activeGame === 'pacman') {
    const credits = ram[0x4e69 - 0x4000];
    if (elCred) elCred.textContent = `CREDITS: ${credits}${arcadeImmortalMode ? ' · LIVES: ∞' : ''}`;
    if (animTick < 305) {
      if (elStat) { elStat.className = 'hud-badge booting'; elStat.textContent = '● BOOTING TEST...'; }
    } else if (credits === 0) {
      if (elStat) { elStat.className = 'hud-badge attract'; elStat.textContent = '● ATTRACT (INSERT COIN)'; }
    } else {
      if (elStat) { elStat.className = 'hud-badge'; elStat.textContent = '● PLAYING: READY!'; }
    }
  } else if (activeGame === 'cclimber') {
    if (climberState.gameOver) {
      if (elCred) elCred.textContent = `● GAME OVER · PRESS 1P START`;
      if (elStat) { elStat.className = 'hud-badge'; elStat.textContent = `● FINAL: ${climberState.score} · HI: ${climberState.highScore}`; }
    } else {
      if (elCred) elCred.textContent = `FLOOR: ${climberState.floor}F/200F · LIVES: ${arcadeImmortalMode ? '∞' : climberState.lives}`;
      if (elStat) { elStat.className = 'hud-badge'; elStat.textContent = `● SCORE: ${climberState.score}`; }
    }
  } else if (activeGame === 'galaga') {
    if (galagaGame.gameOver) {
      if (elCred) elCred.textContent = `● GAME OVER · PRESS 1P START`;
      if (elStat) { elStat.className = 'hud-badge'; elStat.textContent = `● FINAL: ${galagaGame.score} · HI: ${galagaGame.highScore}`; }
    } else {
      if (elCred) elCred.textContent = `STAGE: ${galagaGame.stage} · LIVES: ${arcadeImmortalMode ? '∞' : galagaGame.lives}`;
      if (elStat) { elStat.className = 'hud-badge'; elStat.textContent = `● SCORE: ${galagaGame.score} · HI: ${galagaGame.highScore}`; }
    }
  } else if (activeGame === 'dkong') {
    if (dkongGame.gameOver) {
      if (elCred) elCred.textContent = `● GAME OVER · PRESS 1P START`;
      if (elStat) { elStat.className = 'hud-badge'; elStat.textContent = `● FINAL: ${dkongGame.score} · HI: ${dkongGame.highScore}`; }
    } else {
      if (elCred) elCred.textContent = `LEVEL: ${dkongGame.level} · LIVES: ${arcadeImmortalMode ? '∞' : dkongGame.lives}`;
      if (elStat) { elStat.className = 'hud-badge'; elStat.textContent = `● SCORE: ${dkongGame.score} · BONUS: ${dkongGame.bonusTimer}`; }
    }
  } else if (activeGame === 'frogger') {
    if (froggerGame.gameOver) {
      if (elCred) elCred.textContent = `● GAME OVER · PRESS 1P START`;
      if (elStat) { elStat.className = 'hud-badge'; elStat.textContent = `● FINAL: ${froggerGame.score} · HI: ${froggerGame.highScore}`; }
    } else {
      const homesCount = (froggerGame.homeBays || []).filter(Boolean).length;
      if (elCred) elCred.textContent = `LIVES: ${arcadeImmortalMode ? '∞' : froggerGame.lives} · HOMES: ${homesCount}/5`;
      if (elStat) { elStat.className = 'hud-badge'; elStat.textContent = `● SCORE: ${froggerGame.score} · HI: ${froggerGame.highScore}`; }
    }
  } else if (activeGame === 'asteroids') {
    if (asteroidsGame.gameOver) {
      if (elCred) elCred.textContent = `● GAME OVER · PRESS 1P START`;
      if (elStat) { elStat.className = 'hud-badge'; elStat.textContent = `● FINAL: ${asteroidsGame.score} · HI: ${asteroidsGame.highScore}`; }
    } else {
      if (elCred) elCred.textContent = `WAVE: ${asteroidsGame.level} · LIVES: ${arcadeImmortalMode ? '∞' : asteroidsGame.lives}`;
      if (elStat) { elStat.className = 'hud-badge'; elStat.textContent = `● SCORE: ${asteroidsGame.score} · HI: ${asteroidsGame.highScore}`; }
    }
  } else if (activeGame === 'tempest') {
    if (tempestGame.gameOver) {
      if (elCred) elCred.textContent = `● GAME OVER · PRESS 1P START`;
      if (elStat) { elStat.className = 'hud-badge'; elStat.textContent = `● FINAL: ${tempestGame.score} · HI: ${tempestGame.highScore}`; }
    } else {
      if (elCred) elCred.textContent = `TUBE: ${tempestGame.tube} · LIVES: ${arcadeImmortalMode ? '∞' : tempestGame.lives}`;
      if (elStat) { elStat.className = 'hud-badge'; elStat.textContent = `● SCORE: ${tempestGame.score} · ZAP: ${tempestGame.superzapperUsed ? 'USED' : 'READY'}`; }
    }
  } else if (activeGame === 'gyruss') {
    if (gyrussGame.gameOver) {
      if (elCred) elCred.textContent = `● GAME OVER · PRESS 1P START`;
      if (elStat) { elStat.className = 'hud-badge'; elStat.textContent = `● FINAL: ${gyrussGame.score} · HI: ${gyrussGame.highScore}`; }
    } else {
      if (elCred) elCred.textContent = `WARP: ${gyrussGame.warp} · LIVES: ${arcadeImmortalMode ? '∞' : gyrussGame.lives}`;
      if (elStat) { elStat.className = 'hud-badge'; elStat.textContent = `● SCORE: ${gyrussGame.score} · HI: ${gyrussGame.highScore}`; }
    }
  }"""
    script_body = script_body.replace(old_cpu_block, new_cpu_block)

    old_arcade_render_block = """  // Render Display
  if (currentMode === 'arcade' || currentMode === 'rewind' || currentMode === 'glitch') {
    if (activeGame === 'cclimber') {
      renderCrazyClimber();
    } else {
      renderArcadeFrame();
    }
    if (currentMode === 'rewind') {
      ctx.fillStyle = '#ff3344';
      ctx.font = 'bold 12px monospace';
      ctx.fillText('◄◄ REWINDING (HOLD KEY)', 12, 22);
    }
  } else if (currentMode === 'demo') {"""

    new_arcade_render_block = """  // Render Display across all 8 arcade games, synth oscilloscope, tracker, etc.
  if (currentMode === 'arcade' || currentMode === 'rewind' || currentMode === 'glitch') {
    const shouldStepGame = (currentMode !== 'rewind' && !isRewinding);
    if (activeGame === 'pacman') {
      renderArcadeFrame();
    } else if (activeGame === 'cclimber') {
      renderCrazyClimber();
    } else if (activeGame === 'galaga') {
      if (shouldStepGame) updateGalagaGame();
      renderGalagaGame();
    } else if (activeGame === 'dkong') {
      if (shouldStepGame) updateDonkeyKongGame();
      renderDonkeyKongGame();
    } else if (activeGame === 'frogger') {
      if (shouldStepGame) updateFroggerGame();
      renderFroggerGame();
    } else if (activeGame === 'asteroids') {
      if (shouldStepGame) updateAsteroidsGame();
      renderAsteroidsGame();
    } else if (activeGame === 'tempest') {
      if (shouldStepGame) updateTempestGame();
      renderTempestGame();
    } else if (activeGame === 'gyruss') {
      if (shouldStepGame) updateGyrussGame();
      renderGyrussGame();
    } else {
      renderArcadeFrame();
    }
    if (currentMode === 'rewind') {
      ctx.fillStyle = '#ff3344';
      ctx.font = 'bold 12px monospace';
      ctx.fillText('◄◄ REWINDING (HOLD KEY)', 12, 22);
    }
    if (crtScanlines) drawScanlines();
    if (arcadeImmortalMode) {
      ctx.save();
      ctx.font = 'bold 8px monospace';
      ctx.fillStyle = '#ff9f1a';
      ctx.shadowColor = 'rgba(255, 159, 26, 0.8)';
      ctx.shadowBlur = 4;
      ctx.fillText('⚡ UNLIMITED LIVES', 6, 12);
      ctx.restore();
    }
    if (osdBannerTimer > 0) {
      osdBannerTimer--;
      ctx.save();
      ctx.fillStyle = 'rgba(10, 16, 22, 0.9)';
      ctx.strokeStyle = '#ff9f1a';
      ctx.lineWidth = 1;
      ctx.fillRect(8, 206, 224, 20);
      ctx.strokeRect(8, 206, 224, 20);
      ctx.font = 'bold 8px monospace';
      ctx.fillStyle = '#ff9f1a';
      ctx.textAlign = 'center';
      ctx.fillText(osdBannerText, 120, 219);
      ctx.restore();
    }
  } else if (currentMode === 'synth') {
    renderSynthOscilloscope();
  } else if (currentMode === 'demo') {"""
    script_body = script_body.replace(old_arcade_render_block, new_arcade_render_block)

    old_soundboard_vector_block = """  } else if (currentMode === 'soundboard') {
    buf32.fill(0xff141720);
    ctx.putImageData(imgData, 0, 0);
    ctx.fillStyle = '#f5a623';
    ctx.font = 'bold 13px monospace';
    ctx.fillText('27-KEY AUTHENTIC SFX BOARD', 12, 26);
    ctx.fillStyle = '#888';
    ctx.font = '10px monospace';
    ctx.fillText('TOUCH SILICONE KEYS FOR ARCADE SOUNDS', 12, 44);

    if (lastSfxName) {
      ctx.fillStyle = '#2ecc71';
      ctx.font = 'bold 16px monospace';
      ctx.fillText(`TRIGGERED: [ ${lastSfxName} ]`, 12, 100);
      
      // Draw decorative waveform flare
      ctx.strokeStyle = '#f5a623';
      ctx.lineWidth = 2;
      ctx.beginPath();
      for (let i = 0; i < 216; i++) {
        const y = 140 + Math.sin(i * 0.15 + animTick * 0.2) * 25 * (Math.random() * 0.5 + 0.5);
        if (i === 0) ctx.moveTo(12 + i, y); else ctx.lineTo(12 + i, y);
      }
      ctx.stroke();
    }
  } else if (currentMode === 'tracker') {
    renderTrackerScreen();
  } else if (currentMode === 'vector') {
    buf32.fill(0xff080a0e);
    for (let t = 0; t < 360; t++) {
      const rad = t * Math.PI / 180;
      const x = Math.floor(120 + 80 * Math.sin(rad * 3 + animTick * 0.05));
      const y = Math.floor(120 + 80 * Math.cos(rad * 2 + animTick * 0.03));
      if (x >= 0 && x < 240 && y >= 0 && y < 240) buf32[y * 240 + x] = 0xff00ffcc;
    }
    ctx.putImageData(imgData, 0, 0);
    ctx.fillStyle = '#00ffcc';
    ctx.font = 'bold 12px monospace';
    ctx.fillText('XY LISSAJOUS VECTOR OSC', 12, 22);
  }"""

    new_soundboard_vector_block = """    if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
  } else if (currentMode === 'soundboard') {
    animTick++;
    buf32.fill(0xff141720);
    ctx.putImageData(imgData, 0, 0);
    if (typeof currentStudioTab !== 'undefined' && currentStudioTab === 'speech') {
      ctx.fillStyle = '#00e5ff';
      ctx.font = 'bold 12px monospace';
      ctx.fillText('VINTAGE SPEECH ROM SYNTH', 12, 26);
      ctx.fillStyle = '#8fa59b';
      ctx.font = '9px monospace';
      ctx.fillText('LPC-10 · VOTRAX SC-01 · CVSD', 12, 42);
      const voxId = (typeof lastSpeechRomId !== 'undefined' && lastSpeechRomId) ? lastSpeechRomId : (lastSfxName || 'VOX_INTRUDER');
      ctx.fillStyle = '#00ff66';
      ctx.font = 'bold 13px monospace';
      ctx.fillText(`VOICE: [ ${voxId} ]`, 12, 92);
      ctx.strokeStyle = '#00e5ff';
      ctx.lineWidth = 2;
      ctx.beginPath();
      for (let i = 0; i < 216; i++) {
        const y = 145 + Math.sin(i * 0.18 + animTick * 0.25) * 18 + Math.cos(i * 0.45 - animTick * 0.4) * 10;
        if (i === 0) ctx.moveTo(12 + i, y); else ctx.lineTo(12 + i, y);
      }
      ctx.stroke();
      ctx.fillStyle = '#f5cd79';
      ctx.font = '8px monospace';
      ctx.fillText('PRESS KEYS 1-8 OR SILICONE KEYS 1-27', 12, 222);
    } else {
      ctx.fillStyle = '#f5a623';
      ctx.font = 'bold 13px monospace';
      ctx.fillText('27-KEY AUTHENTIC SFX BOARD', 12, 26);
      ctx.fillStyle = '#888';
      ctx.font = '10px monospace';
      ctx.fillText('TOUCH SILICONE KEYS FOR ARCADE SOUNDS', 12, 44);

      if (lastSfxName) {
        ctx.fillStyle = '#2ecc71';
        ctx.font = 'bold 16px monospace';
        ctx.fillText(`TRIGGERED: [ ${lastSfxName} ]`, 12, 100);
        
        // Draw decorative waveform flare
        ctx.strokeStyle = '#f5a623';
        ctx.lineWidth = 2;
        ctx.beginPath();
        for (let i = 0; i < 216; i++) {
          const y = 140 + Math.sin(i * 0.15 + animTick * 0.2) * 25 * (Math.random() * 0.5 + 0.5);
          if (i === 0) ctx.moveTo(12 + i, y); else ctx.lineTo(12 + i, y);
        }
        ctx.stroke();
      }
    }
    if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
  } else if (currentMode === 'tracker') {
    renderTrackerScreen();
    if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
  } else if (currentMode === 'vector') {
    animTick++;
    buf32.fill(0xff080a0e);
    for (let t = 0; t < 360; t++) {
      const rad = t * Math.PI / 180;
      const x = Math.floor(120 + 80 * Math.sin(rad * 3 + animTick * 0.05));
      const y = Math.floor(120 + 80 * Math.cos(rad * 2 + animTick * 0.03));
      if (x >= 0 && x < 240 && y >= 0 && y < 240) buf32[y * 240 + x] = 0xff00ffcc;
    }
    ctx.putImageData(imgData, 0, 0);
    ctx.fillStyle = '#00ffcc';
    ctx.font = 'bold 12px monospace';
    ctx.fillText('XY LISSAJOUS VECTOR OSC', 12, 22);
    if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
  }"""
    assert old_soundboard_vector_block in script_body, "old_soundboard_vector_block not found!"
    script_body = script_body.replace(old_soundboard_vector_block, new_soundboard_vector_block)

    

    
    # Replace switchActiveGame with full stopCurrentGame and clearScreen logic
    old_switch_full = """function switchActiveGame(gameId) {
  activeGame = gameId;
  document.getElementById('btnGamePacman').classList.toggle('active', gameId === 'pacman');
  document.getElementById('btnGameClimber').classList.toggle('active', gameId === 'cclimber');
  
  if (gameId === 'cclimber') {
    document.getElementById('engineStatus').innerHTML = 'CRAZY CLIMBER: <b>1980 NICHIBUTSU Z80 + AY-3-8910</b> (Twin-Stick)';
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● CRAZY CLIMBER (TWIN-STICK)';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Twin-Stick: <b>W/S</b> (Left Arm) · <b>▲/▼</b> (Right Arm) · <b>A/D</b> (Col) · or Tap Screen Quadrants';
    playArcadeSfx('WARP');
  } else {
    document.getElementById('engineStatus').textContent = 'PAC-MAN (60 FPS Z80 + WSG)';
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● PAC-MAN ACTIVE';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Controls: <b>WASD</b> or <b>Arrow Keys</b> or <b>On-Screen D-Pad</b>';
  }
}"""
    new_switch_full = """// -------------------------------------------------------------------------
// GAME CONTROL & SCREEN BLANKING: STOP CURRENT GAME & CLEAR SCREEN
// -------------------------------------------------------------------------
var currentStudioTab = 'arcade';
function clearScreen(label) {
  if (typeof arcadeBuf !== 'undefined' && arcadeBuf) {
    arcadeBuf.fill(0xff000000);
  }
  if (typeof buf32 !== 'undefined' && buf32) {
    buf32.fill(0xff000000);
  }
  if (typeof ctx !== 'undefined' && ctx) {
    if (ctx.save) ctx.save();
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, 240, 240);
    if (label && ctx.fillText) {
      ctx.fillStyle = '#00ff66';
      ctx.font = 'bold 11px monospace';
      if (ctx.textAlign) ctx.textAlign = 'center';
      ctx.fillText(label.toUpperCase(), 120, 115);
      ctx.fillStyle = '#556677';
      ctx.font = '8px monospace';
      ctx.fillText('STANDBY · READY', 120, 132);
      if (ctx.textAlign) ctx.textAlign = 'left';
    }
    if (ctx.restore) ctx.restore();
  }
}

function stopCurrentGame() {
  // 1. Cancel all scheduled game timers & pulse callbacks
  while (activeGameTimeouts.length > 0) {
    clearTimeout(activeGameTimeouts.pop());
  }

  // 2. Release all active input keys, d-pad, and pulse flags
  keyUp = false;
  keyDown = false;
  keyLeft = false;
  keyRight = false;
  keyCoin = false;
  keyStart = false;
  coinPulseFrames = 0;
  startPulseFrames = 0;
  isRewinding = false;
  if (typeof dpadActiveDir !== 'undefined') dpadActiveDir = null;
  if (typeof arcadeKeysDown !== 'undefined' && arcadeKeysDown) {
    Object.keys(arcadeKeysDown).forEach(k => delete arcadeKeysDown[k]);
  }
  if (typeof galagaGame !== 'undefined' && galagaGame) galagaGame.moveDir = 0;
  if (typeof dkongGame !== 'undefined' && dkongGame && dkongGame.mario) dkongGame.mario.vx = 0;
  if (typeof asteroidsGame !== 'undefined' && asteroidsGame && asteroidsGame.ship) asteroidsGame.ship.thrust = false;

  // 3. Complete audio silencing: mute all WSG synth channels, live synth voices, arpeggiator & demo songs
  if (typeof stopDemoSong === 'function') {
    stopDemoSong();
  } else if (typeof pauseDemoSong === 'function') {
    pauseDemoSong();
  }
  if (typeof liveSynth !== 'undefined' && liveSynth) {
    if (liveSynth.activeVoices && typeof releaseSynthVoice === 'function') {
      Array.from(liveSynth.activeVoices.keys()).forEach(kIdx => releaseSynthVoice(kIdx));
    }
    if (liveSynth.arp) {
      liveSynth.arp.heldKeys = [];
      if (liveSynth.arp.timer) {
        clearInterval(liveSynth.arp.timer);
        liveSynth.arp.timer = null;
      }
    }
  }
  if (typeof wsgVoices !== 'undefined' && wsgVoices) {
    for (let ch = 0; ch < 3; ch++) {
      if (wsgVoices[ch]) {
        wsgVoices[ch].vol = 0;
        wsgVoices[ch].freq = 0;
      }
    }
  }

  // 4. Reset rewind ring buffer and game state counters
  if (typeof rewindBuffer !== 'undefined' && rewindBuffer) {
    rewindBuffer.length = 0;
  }
  if (typeof tourState !== 'undefined' && tourState) {
    tourState.frameInGame = 0;
  }
  if (typeof climberState !== 'undefined' && climberState) {
    climberState.animTick = 0;
    climberState.bgmTick = 0;
    climberState.bgmStep = 0;
  }
  if (typeof froggerGame !== 'undefined' && froggerGame) {
    froggerGame.bgmTick = 0;
    froggerGame.bgmStep = 0;
  }
  if (typeof gyrussGame !== 'undefined' && gyrussGame) {
    gyrussGame.bgmTick = 0;
    gyrussGame.bgmStep = 0;
  }
  if (typeof galagaGame !== 'undefined' && galagaGame) {
    galagaGame.bgmTick = 0;
    galagaGame.bgmStep = 0;
  }
  if (typeof tempestGame !== 'undefined' && tempestGame) {
    tempestGame.bgmTick = 0;
    tempestGame.bgmStep = 0;
  }
  if (typeof dkongGame !== 'undefined' && dkongGame) {
    dkongGame.bgmTick = 0;
    dkongGame.bgmStep = 0;
  }

  // 5. Immediately clear screen display buffer and canvas
  clearScreen();
}

function switchActiveGame(gameId) {
  initAudio();
  if (typeof splashState !== 'undefined') splashState.active = false;
  // FIRST: stop current game and clear screen
  stopCurrentGame();

  activeGame = gameId;
  currentMode = 'arcade';
  currentStudioTab = 'arcade';

  // Sync studio tabs & shelves
  document.querySelectorAll('.studio-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === 'arcade'));
  document.querySelectorAll('.context-shelf').forEach(s => s.classList.remove('active'));
  const shelfArcade = document.getElementById('shelfArcade');
  if (shelfArcade) shelfArcade.classList.add('active');

  // Sync mode tags
  document.querySelectorAll('.mode-tag').forEach(t => t.classList.toggle('active', t.dataset.mode === 'arcade'));

  // Sync arcade gallery cards
  document.querySelectorAll('.arcade-card').forEach(c => c.classList.toggle('active', c.dataset.game === gameId));
  const btnPac = document.getElementById('btnGamePacman');
  const btnClimb = document.getElementById('btnGameClimber');
  const btnTour = document.getElementById('btnGameTour');
  if (btnPac) btnPac.classList.toggle('active', gameId === 'pacman');
  if (btnClimb) btnClimb.classList.toggle('active', gameId === 'cclimber');
  if (btnTour) btnTour.classList.remove('active');

  // Sync Select encoder if in gameList
  if (typeof gameList !== 'undefined' && typeof currentGameIdx !== 'undefined') {
    const idx = gameList.indexOf(gameId);
    if (idx !== -1) {
      currentGameIdx = idx;
      const encSelect = document.getElementById('encSelect');
      if (encSelect && encSelect.style && encSelect.style.setProperty) {
        encSelect.style.setProperty('--angle', `${(currentGameIdx / gameList.length * 270) - 135}deg`);
      }
    }
  }

  if (gameId === 'cclimber') {
    document.getElementById('engineStatus').innerHTML = 'CRAZY CLIMBER: <b>1980 NICHIBUTSU Z80 + AY-3-8910</b> (Twin-Stick)';
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● CRAZY CLIMBER (TWIN-STICK)';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Twin-Stick: <b>W/S</b> (Left Arm) · <b>▲/▼</b> (Right Arm) · <b>A/D</b> (Col) · or Tap Screen Quadrants';
    initCrazyClimberGame();
    climberState.floor = 42;
    climberState.score = 14850;
    climberState.animTick = 0;
    renderCrazyClimber();
  } else if (gameId === 'galaga') {
    document.getElementById('engineStatus').innerHTML = 'GALAGA: <b>1981 NAMCO DUAL Z80 + 3-VOICE WSG</b> (Space Shooter)';
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● GALAGA ACTIVE (STAGE 01)';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Fighter: <b>A/D</b> or <b>◀/▶</b> (Steer) · <b>Space / 1 / Start</b> (Dual Lasers) · D-Pad';
    initGalagaGame();
    renderGalagaGame();
  } else if (gameId === 'dkong') {
    document.getElementById('engineStatus').innerHTML = 'DONKEY KONG: <b>1981 NINTENDO Z80 + 7-BIT DAC</b> (Platformer)';
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● DONKEY KONG ACTIVE (25M GIRDERS)';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Jumpman: <b>A/D</b> (Run) · <b>W/S</b> (Climb Ladders) · <b>Space / Enter</b> (Jump Barrels)';
    initDonkeyKongGame();
    renderDonkeyKongGame();
  } else if (gameId === 'frogger') {
    document.getElementById('engineStatus').innerHTML = 'FROGGER: <b>1981 KONAMI Z80 + DUAL AY-3-8910</b> (Traffic Hop)';
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● FROGGER ACTIVE (RIVER & ROAD)';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Frog: <b>WASD</b> or <b>Arrow Keys</b> or <b>D-Pad</b> to Hop Across Highway & River';
    initFroggerGame();
    renderFroggerGame();
  } else if (gameId === 'asteroids') {
    document.getElementById('engineStatus').innerHTML = 'ASTEROIDS: <b>1979 ATARI QUADRASCAN 6502 + POKEY</b> (Vector CRT)';
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● ASTEROIDS ACTIVE (SECTOR 01)';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Ship: <b>A/D</b> (Rotate) · <b>W</b> (Thrust) · <b>Space / 1</b> (Fire) · <b>S</b> (Hyperspace)';
    initAsteroidsGame();
    renderAsteroidsGame();
  } else if (gameId === 'tempest') {
    document.getElementById('engineStatus').innerHTML = 'TEMPEST: <b>1981 ATARI COLOR VECTOR + POKEY</b> (Tube Shooter)';
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● TEMPEST ACTIVE (TUBE 09)';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Blaster: <b>A/D</b> or <b>◀/▶</b> (Rotary Spin) · <b>Space</b> (Fire) · <b>W</b> (Superzapper)';
    initTempestGame();
    renderTempestGame();
  } else if (gameId === 'gyruss') {
    document.getElementById('engineStatus').innerHTML = 'GYRUSS: <b>1983 KONAMI 5x PSG BAROQUE SYMPHONY</b> (3D Warp)';
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● GYRUSS ACTIVE (WARP TO NEPTUNE)';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Starfighter: <b>A/D</b> or <b>◀/▶</b> (360° Orbit) · <b>Space / 1 / Start</b> (Twin Cannons)';
    initGyrussGame();
    renderGyrussGame();
  } else {
    activeGame = 'pacman';
    document.getElementById('engineStatus').textContent = 'PAC-MAN (60 FPS Z80 + WSG)';
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● PAC-MAN ACTIVE';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Controls: <b>WASD</b> or <b>Arrow Keys</b> or <b>On-Screen D-Pad</b>';
    ensurePastBoot();
    renderArcadeFrame();
  }
  if (arcadeImmortalMode) {
    if (typeof dkongGame !== 'undefined') dkongGame.lives = 99;
    if (typeof galagaGame !== 'undefined') galagaGame.lives = 99;
    if (typeof froggerGame !== 'undefined') froggerGame.lives = 99;
    if (typeof asteroidsGame !== 'undefined') asteroidsGame.lives = 99;
    if (typeof tempestGame !== 'undefined') tempestGame.lives = 99;
    if (typeof gyrussGame !== 'undefined') gyrussGame.lives = 99;
    if (typeof climberState !== 'undefined') climberState.lives = 99;
    if (typeof ram !== 'undefined' && ram) ram[0x4e6e - 0x4000] = 99;
  }
  if (typeof updateMissionCard === 'function') updateMissionCard(gameId);
}"""
    script_body = script_body.replace(old_switch_full, new_switch_full)

    # In setMode, stop current game when changing mode
    old_set_mode = """function setMode(mode) {
  currentMode = mode;
  document.querySelectorAll('.mode-tag').forEach(t => t.classList.toggle('active', t.dataset.mode === mode));
  document.getElementById('jukeboxPanel').style.display = (mode === 'demo') ? 'flex' : 'none';
  const tourBtn = document.getElementById('btnGameTour');
  if (tourBtn) tourBtn.classList.toggle('active', mode === 'tour');
  updateKeyLabels();

  if (mode === 'tour') {
    tourState.active = true;
    tourState.frameInGame = 0;
    document.getElementById('engineStatus').innerHTML = 'ARCADE TOUR DEMO: <b>CYCLING ALL INSTALLED ROMS</b>';
    document.getElementById('hudStatus').textContent = '● TOUR DEMO ACTIVE';
  } else {
    tourState.active = false;
    if (mode !== 'tracker') {
      stopTracker();
    }
    if (mode === 'demo') {
      document.getElementById('engineStatus').textContent = 'DEMO SONGS JUKEBOX ACTIVE';
      playDemoSong();
    } else {
      pauseDemoSong();
      if (mode === 'arcade') {
        if (activeGame === 'cclimber') {
          document.getElementById('engineStatus').innerHTML = 'CRAZY CLIMBER: <b>1980 NICHIBUTSU Z80 + AY-3-8910</b> (Twin-Stick)';
          document.getElementById('hudStatus').textContent = '● CRAZY CLIMBER (TWIN-STICK)';
        } else {
          document.getElementById('engineStatus').textContent = 'PAC-MAN (60 FPS Z80 + WSG)';
          document.getElementById('hudStatus').textContent = '● PAC-MAN ACTIVE';
        }
      }
      else if (mode === 'soundboard') document.getElementById('engineStatus').textContent = '27-KEY AUTHENTIC ARCADE SFX SOUNDBOARD';
      else if (mode === 'tracker') {
        document.getElementById('engineStatus').innerHTML = `16-STEP CHIPTUNE TRACKER: <b>${trackerEngine.patterns[trackerEngine.currentPatternIdx].name}</b> (${trackerEngine.bpm} BPM)`;
        document.getElementById('hudStatus').textContent = '● TRACKER (16-STEP CHIPTUNE)';
        startTracker();
      }
      else if (mode === 'vector') document.getElementById('engineStatus').textContent = 'XY LISSAJOUS VECTOR OSCILLOSCOPE';
      else if (mode === 'glitch') document.getElementById('engineStatus').textContent = 'RAM CIRCUIT-BENDER ACTIVE';
    }
  }
}"""

    new_set_mode = """currentStudioTab = 'arcade';

function setStudioTab(tab) {
  initAudio();
  if (typeof splashState !== 'undefined') splashState.active = false;
  currentStudioTab = tab;
  document.querySelectorAll('.studio-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
  document.querySelectorAll('.context-shelf').forEach(s => s.classList.remove('active'));
  const targetShelf = document.getElementById('shelf' + tab.charAt(0).toUpperCase() + tab.slice(1));
  if (targetShelf) targetShelf.classList.add('active');

  if (tab === 'arcade') {
    if (currentMode !== 'arcade') switchActiveGame(activeGame || 'pacman');
  } else if (tab === 'synth') {
    setMode('synth');
  } else if (tab === 'tracker') {
    setMode('tracker');
  } else if (tab === 'demo') {
    setMode('demo');
  } else if (tab === 'soundboard') {
    setMode('soundboard');
  } else if (tab === 'speech') {
    if (currentMode !== 'soundboard') stopCurrentGame();
    currentMode = 'soundboard';
    currentStudioTab = 'speech';
    document.querySelectorAll('.mode-tag').forEach(t => t.classList.toggle('active', t.dataset.mode === 'soundboard'));
    document.querySelectorAll('.studio-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === 'speech'));
    document.querySelectorAll('.context-shelf').forEach(s => s.classList.remove('active'));
    if (targetShelf) targetShelf.classList.add('active');
    document.getElementById('engineStatus').innerHTML = 'VINTAGE SPEECH ROMS: <b>LPC-10 / VOTRAX SC-01 / CVSD SYNTHESIS</b>';
    document.getElementById('hudStatus').textContent = '● SPEECH ROMS ACTIVE';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Speech ROMs: <b>Keys 1-8</b> or <b>Silicone Keys 1-27</b> or Click Cards to Speak · <b>V</b>=Toggle';
    updateKeyLabels();
  } else if (tab === 'tour') {
    setMode('tour');
  }
}

function setMode(mode) {
  if (typeof splashState !== 'undefined') splashState.active = false;
  const isArcadeSubMode = (m) => (m === 'arcade' || m === 'rewind' || m === 'glitch');
  if (currentMode !== mode && !(isArcadeSubMode(currentMode) && isArcadeSubMode(mode))) {
    stopCurrentGame();
  }
  currentMode = mode;
  const shelfMode = (mode === 'rewind' || mode === 'glitch') ? 'arcade' : (mode === 'vector' ? 'synth' : mode);
  if (currentStudioTab !== 'speech' || mode !== 'soundboard') {
    currentStudioTab = shelfMode;
  }
  document.querySelectorAll('.mode-tag').forEach(t => t.classList.toggle('active', t.dataset.mode === mode));
  document.querySelectorAll('.studio-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === currentStudioTab));
  document.querySelectorAll('.context-shelf').forEach(s => s.classList.remove('active'));
  const targetShelf = document.getElementById('shelf' + currentStudioTab.charAt(0).toUpperCase() + currentStudioTab.slice(1));
  if (targetShelf) targetShelf.classList.add('active');

  const jukePanel = document.getElementById('jukeboxPanel');
  if (jukePanel) jukePanel.style.display = (mode === 'demo') ? 'flex' : 'none';

  const tourBtn = document.getElementById('btnGameTour');
  if (tourBtn) tourBtn.classList.toggle('active', mode === 'tour');
  updateKeyLabels();

  if (mode !== 'tracker' && typeof stopTracker === 'function') {
    stopTracker();
  }
  if (mode !== 'demo' && typeof pauseDemoSong === 'function') {
    pauseDemoSong();
  }
  if (mode !== 'rewind') {
    isRewinding = false;
  }

  if (mode === 'tour') {
    tourState.active = true;
    tourState.paused = false;
    tourState.frameInGame = 0;
    const btnTP = document.getElementById('btnTourPause');
    if (btnTP) { btnTP.textContent = '⏸ PAUSE TOUR'; btnTP.classList.remove('active'); }
    document.getElementById('engineStatus').innerHTML = 'ARCADE TOUR DEMO: <b>CYCLING ALL INSTALLED ROMS</b>';
    document.getElementById('hudStatus').textContent = '● TOUR DEMO ACTIVE';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Tour: <b>Space/Enter</b>=Play Live · <b>N/D/▶</b>=Next Game · <b>P/A/◀</b>=Prev Game';
  } else if (mode === 'synth') {
    tourState.active = false;
    document.getElementById('engineStatus').innerHTML = `SYNTH STUDIO: <b>${liveSynth.engineNames[liveSynth.currentEngine]}</b>`;
    document.getElementById('hudStatus').textContent = `● SYNTH: ${liveSynth.currentEngine.toUpperCase()}`;
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Live Play: <b>Silicone Keys 1-27</b> or <b>QWERTY</b> · <b>SCL</b>=Chip · <b>ENV</b>=Envelope · <b>OCT-/+</b>';
    updateSynthUI();
  } else if (mode === 'tracker') {
    tourState.active = false;
    const pat = trackerEngine.patterns[trackerEngine.currentPatternIdx];
    document.getElementById('engineStatus').innerHTML = `16-STEP CHIPTUNE TRACKER: <b>${pat ? pat.name : 'ACTIVE'}</b>`;
    document.getElementById('hudStatus').textContent = '● TRACKER SEQUENCER';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Sequencer: <b>Space/PLAY</b>=Toggle Loop · <b>SCL</b>=Next Pattern · <b>Keys 1-16</b>=Audition';
    if (typeof startTracker === 'function') startTracker();
    updateTrackerUI();
  } else if (mode === 'demo') {
    tourState.active = false;
    document.getElementById('engineStatus').innerHTML = 'DEMO JUKEBOX: <b>15-TRACK MULTI-VOICE SYMPHONIES</b>';
    document.getElementById('hudStatus').textContent = '● DEMO JUKEBOX';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Jukebox: <b>Space/PLAY</b>=Start/Stop Song · <b>PRESETS Knob</b>=Select Symphony';
    if (typeof playDemoSong === 'function') playDemoSong();
  } else if (mode === 'soundboard') {
    tourState.active = false;
    const bank = (typeof SFX_BANKS !== 'undefined' && SFX_BANKS[currentSfxBank]) ? SFX_BANKS[currentSfxBank] : null;
    const bName = bank ? bank.name : '4 MASTER BANKS';
    document.getElementById('engineStatus').innerHTML = 'ARCADE SOUNDBOARD: <b>' + bName + '</b>';
    document.getElementById('hudStatus').textContent = '● SFX PADS ACTIVE';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Soundboard: <b>Touch Silicone Keys 1-27</b> or Click Pads to Trigger Audio';
    if (typeof renderSoundboardPads === 'function') renderSoundboardPads();
  } else if (mode === 'rewind') {
    tourState.active = false;
    isRewinding = true;
    document.getElementById('engineStatus').innerHTML = 'TIME MACHINE: <b>60FPS STATE RING BUFFER REWIND</b>';
    document.getElementById('hudStatus').textContent = '● REWINDING TIME';
  } else if (mode === 'glitch') {
    tourState.active = false;
    document.getElementById('engineStatus').innerHTML = 'RAM CIRCUIT-BENDER: <b>Z80 BUS GLITCH ACTIVE</b>';
    document.getElementById('hudStatus').textContent = '● CIRCUIT BENDER';
    if (typeof triggerCircuitBending === 'function') triggerCircuitBending();
  } else if (mode === 'vector') {
    tourState.active = false;
    document.getElementById('engineStatus').innerHTML = 'XY LISSAJOUS VECTOR OSCILLOSCOPE: <b>60Hz PHASE MATRIX</b>';
    document.getElementById('hudStatus').textContent = '● XY VECTOR OSC';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Vector Oscilloscope: <b>Silicone Keys 1-27</b> or <b>QWERTY</b> to Modulate XY Phase';
  } else if (mode === 'arcade') {
    tourState.active = false;
    if (typeof activeGame !== 'undefined' && activeGame) {
      updateMissionCard(activeGame);
    } else {
      switchActiveGame('pacman');
    }
  } else {
    tourState.active = false;
  }
}"""
    script_body = script_body.replace(old_set_mode, new_set_mode)

    old_init = """// Initialize Demo Songs UI
initDemoJukebox();

requestAnimationFrame(mainLoop);"""

    new_init = """// Initialize Demo Songs & Soundboard Pads UI
initDemoJukebox();
if (typeof renderSoundboardPads === 'function') renderSoundboardPads();

// Instant Pac-Man maze & attract screen initialization (0ms wait)
ensurePastBoot();
renderArcadeFrame();

requestAnimationFrame(mainLoop);"""
    script_body = script_body.replace(old_init, new_init)

    script_body = script_body.replace(old_setupknob, new_setupknob)

    script_body = script_body.replace(
        "masterGain.gain.value = 0.85;",
        "masterGain.gain.value = (typeof masterVolLevel !== 'undefined') ? (masterVolLevel / 100) * 0.95 : 0.665;"
    )
    script_body = script_body.replace(
        "function handleUnifiedAction(act, isDown = true) {\n  initAudio();",
        "function handleUnifiedAction(act, isDown = true) {\n  initAudio();\n  if (act === 'fire' || act === 'jump') act = 'action';\n  if (act === 'start') { if (isDown && typeof start1P === 'function') start1P(); return; }\n  if (act === 'coin') { if (isDown && typeof insertCoin === 'function') insertCoin(); return; }"
    )

    # 4a-extra. Sync knob4 with liveSynth.waveMorph, sync Demo Jukebox & Synth UI, and upgrade QWERTY/key handlers
    old_knob4 = """setupKnob('knob4', 0, 7, 0, (v) => `WSG ${Math.round(v)}`, (v) => {
  const w = Math.round(v);
  wsgVoices[0].wave = w; wsgVoices[1].wave = w; wsgVoices[2].wave = w;
  document.getElementById('valKnob4').textContent = `WSG ${w}`;
});"""
    new_knob4 = """setupKnob('knob4', 0, 7, 0, (v) => `WSG ${Math.round(v)}`, (v) => {
  const w = Math.round(v);
  wsgVoices[0].wave = w; wsgVoices[1].wave = w; wsgVoices[2].wave = w;
  if (typeof liveSynth !== 'undefined' && liveSynth) {
    liveSynth.waveMorph = w;
    liveSynth.wsgWave = w;
  }
  document.getElementById('valKnob4').textContent = `WSG ${w}`;
});"""
    assert old_knob4 in script_body, "old_knob4 not found in script_body"
    script_body = script_body.replace(old_knob4, new_knob4)

    old_juke_funcs = """function selectDemoSong(idx) {
  demoPlayer.currentSongIdx = idx;
  document.querySelectorAll('.song-pill').forEach((p, i) => p.classList.toggle('active', i === idx));
  demoPlayer.step = 0;
  updateJukeboxUI();
}

function updateJukeboxUI() {
  const song = DEMO_SONGS[demoPlayer.currentSongIdx];
  document.getElementById('jukeBpm').innerHTML = `BPM: <b>${song.bpm}</b>`;
  document.getElementById('jukeTracks').innerHTML = `TRACKS: <b>${song.tracks.length}</b>`;
  document.getElementById('jukeStep').innerHTML = `STEP: <b>${String(demoPlayer.step + 1).padStart(2, '0')}/64</b>`;
  document.getElementById('engineStatus').innerHTML = `DEMO: <b>${song.title}</b> (${song.synth})`;
}

function playDemoSong() {
  initAudio();
  if (demoPlayer.playing) return;
  demoPlayer.playing = true;
  document.getElementById('btnJukePlay').textContent = '⏸ PAUSE';
  document.getElementById('btnJukePlay').classList.add('playing');
  document.getElementById('jukeStatus').textContent = 'PLAYING';
  
  scheduleDemoTick();
}

function pauseDemoSong() {
  demoPlayer.playing = false;
  if (demoPlayer.timer) clearTimeout(demoPlayer.timer);
  demoPlayer.timer = null;
  document.getElementById('btnJukePlay').textContent = '▶ PLAY SONG';
  document.getElementById('btnJukePlay').classList.remove('playing');
  document.getElementById('jukeStatus').textContent = 'PAUSED';
}

function stopDemoSong() {
  pauseDemoSong();
  demoPlayer.step = 0;
  demoPlayer.vuLevels.fill(0);
  document.getElementById('jukeStatus').textContent = 'STOPPED';
  updateJukeboxUI();
}"""
    new_juke_funcs = """function selectDemoSong(idx) {
  const safeIdx = ((idx % DEMO_SONGS.length) + DEMO_SONGS.length) % DEMO_SONGS.length;
  demoPlayer.currentSongIdx = safeIdx;
  if (typeof currentDemoIdx !== 'undefined') currentDemoIdx = safeIdx;
  document.querySelectorAll('.song-pill').forEach((p, i) => p.classList.toggle('active', i === safeIdx));
  document.querySelectorAll('#shelfSongPills .synth-chip-btn').forEach((p, i) => p.classList.toggle('active', i === safeIdx));
  demoPlayer.step = 0;
  updateJukeboxUI();
}

function updateJukeboxUI() {
  const song = DEMO_SONGS[demoPlayer.currentSongIdx] || DEMO_SONGS[0];
  document.getElementById('jukeBpm').innerHTML = `BPM: <b>${song.bpm}</b>`;
  document.getElementById('jukeTracks').innerHTML = `TRACKS: <b>${song.tracks.length}</b>`;
  document.getElementById('jukeStep').innerHTML = `STEP: <b>${String(demoPlayer.step + 1).padStart(2, '0')}/64</b>`;
  document.getElementById('engineStatus').innerHTML = `DEMO: <b>${song.title}</b> (${song.synth})`;
}

function playDemoSong(songIdx) {
  initAudio();
  if (songIdx !== undefined && typeof selectDemoSong === 'function') {
    selectDemoSong(songIdx);
  }
  if (demoPlayer.playing) return;
  demoPlayer.playing = true;
  document.getElementById('btnJukePlay').textContent = '⏸ PAUSE';
  document.getElementById('btnJukePlay').classList.add('playing');
  document.getElementById('jukeStatus').textContent = 'PLAYING';
  const shelfSt = document.getElementById('shelfJukeStatus');
  if (shelfSt) shelfSt.textContent = 'PLAYING';
  
  scheduleDemoTick();
}

function pauseDemoSong() {
  demoPlayer.playing = false;
  if (demoPlayer.timer) clearTimeout(demoPlayer.timer);
  demoPlayer.timer = null;
  document.getElementById('btnJukePlay').textContent = '▶ PLAY SONG';
  document.getElementById('btnJukePlay').classList.remove('playing');
  document.getElementById('jukeStatus').textContent = 'PAUSED';
  const shelfSt = document.getElementById('shelfJukeStatus');
  if (shelfSt) shelfSt.textContent = 'PAUSED';
}

function stopDemoSong() {
  pauseDemoSong();
  demoPlayer.step = 0;
  demoPlayer.vuLevels.fill(0);
  document.getElementById('jukeStatus').textContent = 'STOPPED';
  const shelfSt = document.getElementById('shelfJukeStatus');
  if (shelfSt) shelfSt.textContent = 'STOPPED';
  updateJukeboxUI();
}"""
    assert old_juke_funcs in script_body, "old_juke_funcs not found in script_body"
    script_body = script_body.replace(old_juke_funcs, new_juke_funcs)

    old_synth_cycles = """function cycleSynthEngine() {
  const idx = liveSynth.engineOrder.indexOf(liveSynth.currentEngine);
  liveSynth.currentEngine = liveSynth.engineOrder[(idx + 1) % liveSynth.engineOrder.length];
  const name = liveSynth.engineNames[liveSynth.currentEngine];
  const status = document.getElementById('engineStatus');
  if (status) status.innerHTML = `SYNTH ENGINE: <b>${name}</b>`;
  const hud = document.getElementById('hudStatus');
  if (hud) hud.textContent = `● SYNTH: ${liveSynth.currentEngine.toUpperCase()}`;
  playStartupChimeMini();
  return name;
}

function cycleEnvelope() {
  const envs = ['lead', 'pluck', 'pad', 'organ'];
  const idx = envs.indexOf(liveSynth.envelope);
  liveSynth.envelope = envs[(idx + 1) % envs.length];
  const status = document.getElementById('engineStatus');
  if (status) status.innerHTML = `ENVELOPE: <b>${liveSynth.envelope.toUpperCase()}</b>`;
}

function toggleLfo() {
  liveSynth.lfo.active = !liveSynth.lfo.active;
  const status = document.getElementById('engineStatus');
  if (status) status.innerHTML = `LFO VIBRATO: <b>${liveSynth.lfo.active ? 'ON (6.0 Hz)' : 'OFF'}</b>`;
}

function toggleArp() {
  liveSynth.arp.active = !liveSynth.arp.active;
  const btn = document.getElementById('btnArp');
  if (btn) btn.classList.toggle('active', liveSynth.arp.active);
  const status = document.getElementById('engineStatus');
  if (status) status.innerHTML = `ARPEGGIATOR: <b>${liveSynth.arp.active ? 'ON (1/16th)' : 'OFF'}</b>`;
  if (!liveSynth.arp.active && liveSynth.arp.timer) {
    clearInterval(liveSynth.arp.timer);
    liveSynth.arp.timer = null;
  }
}"""
    new_synth_cycles = """function cycleSynthEngine() {
  initAudio();
  const idx = liveSynth.engineOrder.indexOf(liveSynth.currentEngine);
  liveSynth.currentEngine = liveSynth.engineOrder[(idx + 1) % liveSynth.engineOrder.length];
  const name = liveSynth.engineNames[liveSynth.currentEngine];
  const status = document.getElementById('engineStatus');
  if (status) status.innerHTML = `SYNTH ENGINE: <b>${name}</b>`;
  const hud = document.getElementById('hudStatus');
  if (hud) hud.textContent = `● SYNTH: ${liveSynth.currentEngine.toUpperCase()}`;
  if (typeof updateSynthUI === 'function') updateSynthUI();
  playStartupChimeMini();
  return name;
}

function cycleEnvelope() {
  initAudio();
  const envs = ['lead', 'pluck', 'pad', 'organ'];
  const idx = envs.indexOf(liveSynth.envelope);
  liveSynth.envelope = envs[(idx + 1) % envs.length];
  const status = document.getElementById('engineStatus');
  if (status) status.innerHTML = `ENVELOPE: <b>${liveSynth.envelope.toUpperCase()}</b>`;
  if (typeof updateSynthUI === 'function') updateSynthUI();
}

function toggleLfo() {
  initAudio();
  liveSynth.lfo.active = !liveSynth.lfo.active;
  const btn = document.getElementById('btnLfo');
  if (btn) btn.classList.toggle('active', liveSynth.lfo.active);
  const status = document.getElementById('engineStatus');
  if (status) status.innerHTML = `LFO VIBRATO: <b>${liveSynth.lfo.active ? 'ON (6.0 Hz)' : 'OFF'}</b>`;
  if (typeof updateSynthUI === 'function') updateSynthUI();
}

function toggleArp() {
  initAudio();
  liveSynth.arp.active = !liveSynth.arp.active;
  const btn = document.getElementById('btnArp');
  if (btn) btn.classList.toggle('active', liveSynth.arp.active);
  const status = document.getElementById('engineStatus');
  if (status) status.innerHTML = `ARPEGGIATOR: <b>${liveSynth.arp.active ? 'ON (1/16th)' : 'OFF'}</b>`;
  if (!liveSynth.arp.active && liveSynth.arp.timer) {
    clearInterval(liveSynth.arp.timer);
    liveSynth.arp.timer = null;
  }
  if (typeof updateSynthUI === 'function') updateSynthUI();
}"""
    assert old_synth_cycles in script_body, "old_synth_cycles not found in script_body"
    script_body = script_body.replace(old_synth_cycles, new_synth_cycles)

    old_key_listeners = """// Keyboard Listeners (Arrows, WASD, 1, 5, Space, Enter, R, B, K, Z, T)
window.addEventListener('keydown', (e) => {
  initAudio();
  if (typeof splashState !== 'undefined' && splashState.active) {
    if (typeof skipSplashScreen === 'function') skipSplashScreen();
    e.preventDefault();
    return;
  }
  const k = e.key.toLowerCase();
  arcadeKeysDown[k] = true;
  arcadeKeysDown[e.key] = true;

  // Illumination of on-screen controller deck
  const cL = document.getElementById('ctrlBtnLeft'); if (cL && (k === 'a' || e.key === 'ArrowLeft')) cL.classList.add('pressed');
  const cR = document.getElementById('ctrlBtnRight'); if (cR && (k === 'd' || e.key === 'ArrowRight')) cR.classList.add('pressed');
  const cU = document.getElementById('ctrlBtnUp'); if (cU && (k === 'w' || e.key === 'ArrowUp')) cU.classList.add('pressed');
  const cD = document.getElementById('ctrlBtnDown'); if (cD && (k === 's' || e.key === 'ArrowDown')) cD.classList.add('pressed');
  const cF = document.getElementById('ctrlBtnFire'); if (cF && (e.key === ' ' || e.key === 'Enter')) cF.classList.add('pressed');
  const cC = document.getElementById('ctrlBtnCoin'); if (cC && (k === '1' || k === 'c')) cC.classList.add('pressed');
  const cS = document.getElementById('ctrlBtnStart'); if (cS && (k === '5' || k === 'p')) cS.classList.add('pressed');
  const cG = document.getElementById('ctrlBtnImmortal'); if (cG && (k === 'i' || k === 'g')) cG.classList.add('pressed');
  const cLvl = document.getElementById('ctrlBtnLevelSkip'); if (cLvl && (k === 'l' || k === 'n')) cLvl.classList.add('pressed');

  if (k === 'i' || k === 'g') {
    if (typeof toggleImmortalMode === 'function') toggleImmortalMode();
    e.preventDefault();
    return;
  }
  if (k === 'l' || (currentMode !== 'tour' && k === 'n')) {
    if (typeof skipCurrentLevel === 'function') skipCurrentLevel();
    e.preventDefault();
    return;
  }

  if (k === 't') {
    if (typeof toggleTourDemo === 'function') toggleTourDemo();
    e.preventDefault();
    return;
  }

  if (currentMode === 'tour') {
    if (e.key === ' ' || e.key === 'Enter' || k === '1' || k === 'c' || k === '5' || k === 'p') {
      if (typeof launchCurrentTourGame === 'function') launchCurrentTourGame();
      e.preventDefault();
      return;
    }
    if (e.key === 'ArrowRight' || k === 'd' || k === 'n') {
      if (typeof nextTourGame === 'function') nextTourGame();
      e.preventDefault();
      return;
    }
    if (e.key === 'ArrowLeft' || k === 'a' || k === 'p') {
      if (typeof prevTourGame === 'function') prevTourGame();
      e.preventDefault();
      return;
    }
    return;
  }

  // Crazy Climber Twin-Stick specific shortcuts
  if (activeGame === 'cclimber') {
    if (k === 'w') { climberStep('left', 'up'); e.preventDefault(); return; }
    else if (k === 's') { climberStep('left', 'down'); e.preventDefault(); return; }
    else if (e.key === 'ArrowUp') { climberStep('right', 'up'); e.preventDefault(); return; }
    else if (e.key === 'ArrowDown') { climberStep('right', 'down'); e.preventDefault(); return; }
    else if (k === 'a' || e.key === 'ArrowLeft') { climberState.col = Math.max(0, climberState.col - 1); e.preventDefault(); return; }
    else if (k === 'd' || e.key === 'ArrowRight') { climberState.col = Math.min(3, climberState.col + 1); e.preventDefault(); return; }
  }

  // Standard directional & action controls for all games
  if (e.key === 'ArrowUp' || k === 'w') { handleUnifiedAction('up', true); e.preventDefault(); }
  else if (e.key === 'ArrowDown' || k === 's') { handleUnifiedAction('down', true); e.preventDefault(); }
  else if (e.key === 'ArrowLeft' || k === 'a') { handleUnifiedAction('left', true); e.preventDefault(); }
  else if (e.key === 'ArrowRight' || k === 'd') { handleUnifiedAction('right', true); e.preventDefault(); }
  else if (k === '1' || k === 'c') { insertCoin(); e.preventDefault(); }
  else if (k === '5' || k === 'p') { start1P(); e.preventDefault(); }
  else if (e.key === ' ' || e.key === 'Enter') {
    if (currentMode === 'tracker') toggleTracker();
    else if (currentMode === 'demo') { if (demoPlayer.playing) pauseDemoSong(); else playDemoSong(); }
    else handleUnifiedAction('action', true);
    e.preventDefault();
  }
  else if (e.key === 'Backspace' || k === 'r') { isRewinding = true; setMode('rewind'); e.preventDefault(); }
  else if (e.key === 'Tab') {
    const idx = (MODES.indexOf(currentMode) + 1) % MODES.length;
    setMode(MODES[idx]);
    e.preventDefault();
  }
  else if (k === 'b') { const bg = document.getElementById('btnGlitch'); if (bg) bg.click(); }
  else if (k === 'k') { toggleScanlines(); }
  else if (k === 'z') { if (typeof toggleScreenZoom === 'function') toggleScreenZoom(); }
});

window.addEventListener('keyup', (e) => {
  const k = e.key.toLowerCase();
  delete arcadeKeysDown[k];
  delete arcadeKeysDown[e.key];

  const cL = document.getElementById('ctrlBtnLeft'); if (cL && (k === 'a' || e.key === 'ArrowLeft')) cL.classList.remove('pressed');
  const cR = document.getElementById('ctrlBtnRight'); if (cR && (k === 'd' || e.key === 'ArrowRight')) cR.classList.remove('pressed');
  const cU = document.getElementById('ctrlBtnUp'); if (cU && (k === 'w' || e.key === 'ArrowUp')) cU.classList.remove('pressed');
  const cD = document.getElementById('ctrlBtnDown'); if (cD && (k === 's' || e.key === 'ArrowDown')) cD.classList.remove('pressed');
  const cF = document.getElementById('ctrlBtnFire'); if (cF && (e.key === ' ' || e.key === 'Enter')) cF.classList.remove('pressed');
  const cC = document.getElementById('ctrlBtnCoin'); if (cC && (k === '1' || k === 'c')) cC.classList.remove('pressed');
  const cS = document.getElementById('ctrlBtnStart'); if (cS && (k === '5' || k === 'p')) cS.classList.remove('pressed');
  const cG = document.getElementById('ctrlBtnImmortal'); if (cG && (k === 'i' || k === 'g')) cG.classList.remove('pressed');
  const cLvl = document.getElementById('ctrlBtnLevelSkip'); if (cLvl && (k === 'l' || k === 'n')) cLvl.classList.remove('pressed');

  if (e.key === 'ArrowUp' || k === 'w') handleUnifiedAction('up', false);
  else if (e.key === 'ArrowDown' || k === 's') handleUnifiedAction('down', false);
  else if (e.key === 'ArrowLeft' || k === 'a') handleUnifiedAction('left', false);
  else if (e.key === 'ArrowRight' || k === 'd') handleUnifiedAction('right', false);
  else if (e.key === ' ' || e.key === 'Enter') handleUnifiedAction('action', false);
  else if (e.key === 'Backspace' || k === 'r') { isRewinding = false; setMode('arcade'); }
});"""

    new_key_listeners = """// 27-Key QWERTY Musical & Soundboard Pad Mapping (C4..D6 across 2 rows)
const QWERTY_SYNTH_MAP = {
  'z': 0, 's': 1, 'x': 2, 'd': 3, 'c': 4, 'f': 5, 'g': 6, 'b': 7, 'h': 8, 'n': 9, 'j': 10, 'm': 11,
  'q': 12, '2': 13, 'w': 14, '3': 15, 'e': 16, 'r': 17, '5': 18, 't': 19, '6': 20, 'y': 21, '7': 22, 'u': 23,
  'i': 24, '9': 25, 'o': 26,
  ',': 12, 'l': 13, '.': 14, ';': 15, '/': 16, 'p': 26, 'a': 0, 'k': 11
};
const SOUNDBOARD_EXTRA_MAP = {
  '1': 0, '4': 3, '8': 7, '0': 9, '-': 10, '=': 11
};
const activeQwertySynthKeys = {};

// Keyboard Listeners (Arrows, WASD, 1, 5, Space, Enter, R, B, K, Z, T, plus 27-Key QWERTY Synth/Pads)
window.addEventListener('keydown', (e) => {
  if (e.ctrlKey || e.metaKey || e.altKey) return;
  initAudio();
  if (typeof splashState !== 'undefined' && splashState.active) {
    if (typeof skipSplashScreen === 'function') skipSplashScreen();
    e.preventDefault();
    return;
  }
  const k = e.key.toLowerCase();

  // 1. Speech ROM Shelf Isolation: prevent keys 1-8 from cross-triggering arcade Coin/Start!
  if (typeof currentStudioTab !== 'undefined' && currentStudioTab === 'speech') {
    if (e.key === 'Tab') {
      const idx = (MODES.indexOf(currentMode) + 1) % MODES.length;
      setMode(MODES[idx]);
      e.preventDefault();
    }
    return;
  }

  // 2. Live 27-Key QWERTY Performance in Synth, Soundboard, and Tracker Modes
  if (currentMode === 'synth' || currentMode === 'soundboard' || currentMode === 'tracker') {
    if (e.key === 'Tab') {
      const idx = (MODES.indexOf(currentMode) + 1) % MODES.length;
      setMode(MODES[idx]);
      e.preventDefault();
      return;
    }
    if ((e.key === ' ' || e.key === 'Enter') && currentMode === 'tracker') {
      if (!e.repeat && typeof toggleTracker === 'function') toggleTracker();
      e.preventDefault();
      return;
    }
    if (e.key === 'ArrowLeft' && currentMode === 'synth') {
      if (!e.repeat && typeof setSynthOctave === 'function') setSynthOctave((liveSynth ? liveSynth.octaveOffset : 0) - 1);
      e.preventDefault();
      return;
    }
    if (e.key === 'ArrowRight' && currentMode === 'synth') {
      if (!e.repeat && typeof setSynthOctave === 'function') setSynthOctave((liveSynth ? liveSynth.octaveOffset : 0) + 1);
      e.preventDefault();
      return;
    }
    let padIdx = QWERTY_SYNTH_MAP[k];
    if (padIdx === undefined && currentMode === 'soundboard') {
      padIdx = SOUNDBOARD_EXTRA_MAP[k];
    }
    if (padIdx !== undefined) {
      if (!e.repeat && activeQwertySynthKeys[k] === undefined) {
        activeQwertySynthKeys[k] = padIdx;
        onKeyTouch(padIdx, true);
      }
      e.preventDefault();
      return;
    }
  }

  arcadeKeysDown[k] = true;
  arcadeKeysDown[e.key] = true;

  // Illumination of on-screen controller deck
  const cL = document.getElementById('ctrlBtnLeft'); if (cL && (k === 'a' || e.key === 'ArrowLeft')) cL.classList.add('pressed');
  const cR = document.getElementById('ctrlBtnRight'); if (cR && (k === 'd' || e.key === 'ArrowRight')) cR.classList.add('pressed');
  const cU = document.getElementById('ctrlBtnUp'); if (cU && (k === 'w' || e.key === 'ArrowUp')) cU.classList.add('pressed');
  const cD = document.getElementById('ctrlBtnDown'); if (cD && (k === 's' || e.key === 'ArrowDown')) cD.classList.add('pressed');
  const cF = document.getElementById('ctrlBtnFire'); if (cF && (e.key === ' ' || e.key === 'Enter')) cF.classList.add('pressed');
  const cC = document.getElementById('ctrlBtnCoin'); if (cC && (k === '1' || k === 'c')) cC.classList.add('pressed');
  const cS = document.getElementById('ctrlBtnStart'); if (cS && (k === '5' || k === 'p')) cS.classList.add('pressed');
  const cG = document.getElementById('ctrlBtnImmortal'); if (cG && (k === 'i' || k === 'g')) cG.classList.add('pressed');
  const cLvl = document.getElementById('ctrlBtnLevelSkip'); if (cLvl && (k === 'l' || k === 'n')) cLvl.classList.add('pressed');

  if (k === 'i' || k === 'g') {
    if (!e.repeat && typeof toggleImmortalMode === 'function') toggleImmortalMode();
    e.preventDefault();
    return;
  }
  if (k === 'l' || (currentMode !== 'tour' && k === 'n')) {
    if (!e.repeat && typeof skipCurrentLevel === 'function') skipCurrentLevel();
    e.preventDefault();
    return;
  }

  if (k === 't') {
    if (!e.repeat && typeof toggleTourDemo === 'function') toggleTourDemo();
    e.preventDefault();
    return;
  }

  if (currentMode === 'tour') {
    if (e.key === ' ' || e.key === 'Enter' || k === '1' || k === 'c' || k === '5' || k === 'p') {
      if (!e.repeat && typeof launchCurrentTourGame === 'function') launchCurrentTourGame();
      e.preventDefault();
      return;
    }
    if (e.key === 'ArrowRight' || k === 'd' || k === 'n') {
      if (!e.repeat && typeof nextTourGame === 'function') nextTourGame();
      e.preventDefault();
      return;
    }
    if (e.key === 'ArrowLeft' || k === 'a' || k === 'p') {
      if (!e.repeat && typeof prevTourGame === 'function') prevTourGame();
      e.preventDefault();
      return;
    }
    return;
  }

  // Crazy Climber Twin-Stick specific shortcuts
  if (activeGame === 'cclimber') {
    if (k === 'w') { climberStep('left', 'up'); e.preventDefault(); return; }
    else if (k === 's') { climberStep('left', 'down'); e.preventDefault(); return; }
    else if (e.key === 'ArrowUp') { climberStep('right', 'up'); e.preventDefault(); return; }
    else if (e.key === 'ArrowDown') { climberStep('right', 'down'); e.preventDefault(); return; }
    else if (k === 'a' || e.key === 'ArrowLeft') { climberState.col = Math.max(0, climberState.col - 1); e.preventDefault(); return; }
    else if (k === 'd' || e.key === 'ArrowRight') { climberState.col = Math.min(3, climberState.col + 1); e.preventDefault(); return; }
  }

  // Standard directional & action controls for all games
  if (e.key === 'ArrowUp' || k === 'w') { handleUnifiedAction('up', true); e.preventDefault(); }
  else if (e.key === 'ArrowDown' || k === 's') { handleUnifiedAction('down', true); e.preventDefault(); }
  else if (e.key === 'ArrowLeft' || k === 'a') { handleUnifiedAction('left', true); e.preventDefault(); }
  else if (e.key === 'ArrowRight' || k === 'd') { handleUnifiedAction('right', true); e.preventDefault(); }
  else if (k === '1' || k === 'c') { if (!e.repeat) insertCoin(); e.preventDefault(); }
  else if (k === '5' || k === 'p') { if (!e.repeat) start1P(); e.preventDefault(); }
  else if (e.key === ' ' || e.key === 'Enter') {
    if (!e.repeat) {
      if (currentMode === 'tracker') toggleTracker();
      else if (currentMode === 'demo') { if (demoPlayer.playing) pauseDemoSong(); else playDemoSong(); }
      else handleUnifiedAction('action', true);
    }
    e.preventDefault();
  }
  else if (e.key === 'Backspace' || k === 'r') { isRewinding = true; setMode('rewind'); e.preventDefault(); }
  else if (e.key === 'Tab') {
    const idx = (MODES.indexOf(currentMode) + 1) % MODES.length;
    setMode(MODES[idx]);
    e.preventDefault();
  }
  else if (k === 'b') { if (!e.repeat) { const bg = document.getElementById('btnGlitch'); if (bg) bg.click(); } }
  else if (k === 'k') { if (!e.repeat) toggleScanlines(); }
  else if (k === 'z') { if (!e.repeat && typeof toggleScreenZoom === 'function') toggleScreenZoom(); }
});

window.addEventListener('keyup', (e) => {
  const k = e.key.toLowerCase();
  if (activeQwertySynthKeys[k] !== undefined) {
    const padIdx = activeQwertySynthKeys[k];
    delete activeQwertySynthKeys[k];
    onKeyTouch(padIdx, false);
    return;
  }
  delete arcadeKeysDown[k];
  delete arcadeKeysDown[e.key];

  const cL = document.getElementById('ctrlBtnLeft'); if (cL && (k === 'a' || e.key === 'ArrowLeft')) cL.classList.remove('pressed');
  const cR = document.getElementById('ctrlBtnRight'); if (cR && (k === 'd' || e.key === 'ArrowRight')) cR.classList.remove('pressed');
  const cU = document.getElementById('ctrlBtnUp'); if (cU && (k === 'w' || e.key === 'ArrowUp')) cU.classList.remove('pressed');
  const cD = document.getElementById('ctrlBtnDown'); if (cD && (k === 's' || e.key === 'ArrowDown')) cD.classList.remove('pressed');
  const cF = document.getElementById('ctrlBtnFire'); if (cF && (e.key === ' ' || e.key === 'Enter')) cF.classList.remove('pressed');
  const cC = document.getElementById('ctrlBtnCoin'); if (cC && (k === '1' || k === 'c')) cC.classList.remove('pressed');
  const cS = document.getElementById('ctrlBtnStart'); if (cS && (k === '5' || k === 'p')) cS.classList.remove('pressed');
  const cG = document.getElementById('ctrlBtnImmortal'); if (cG && (k === 'i' || k === 'g')) cG.classList.remove('pressed');
  const cLvl = document.getElementById('ctrlBtnLevelSkip'); if (cLvl && (k === 'l' || k === 'n')) cLvl.classList.remove('pressed');

  if (e.key === 'ArrowUp' || k === 'w') handleUnifiedAction('up', false);
  else if (e.key === 'ArrowDown' || k === 's') handleUnifiedAction('down', false);
  else if (e.key === 'ArrowLeft' || k === 'a') handleUnifiedAction('left', false);
  else if (e.key === 'ArrowRight' || k === 'd') handleUnifiedAction('right', false);
  else if (e.key === ' ' || e.key === 'Enter') handleUnifiedAction('action', false);
  else if ((e.key === 'Backspace' || k === 'r') && isRewinding) { isRewinding = false; setMode('arcade'); }
});

window.addEventListener('blur', () => {
  Object.keys(activeQwertySynthKeys).forEach(k => {
    const padIdx = activeQwertySynthKeys[k];
    delete activeQwertySynthKeys[k];
    onKeyTouch(padIdx, false);
  });
  Object.keys(arcadeKeysDown).forEach(k => delete arcadeKeysDown[k]);
  if (typeof liveSynth !== 'undefined' && liveSynth) {
    if (liveSynth.activeVoices) {
      Array.from(liveSynth.activeVoices.keys()).forEach(kIdx => releaseSynthVoice(kIdx));
    }
    if (liveSynth.arp) {
      liveSynth.arp.heldKeys = [];
      if (liveSynth.arp.timer) {
        clearInterval(liveSynth.arp.timer);
        liveSynth.arp.timer = null;
      }
    }
  }
  handleUnifiedAction('left', false);
  handleUnifiedAction('right', false);
  handleUnifiedAction('up', false);
  handleUnifiedAction('down', false);
  handleUnifiedAction('action', false);
});"""
    assert old_key_listeners in script_body, "old_key_listeners not found in script_body"
    script_body = script_body.replace(old_key_listeners, new_key_listeners)

    # 4b. Upgrade Splash Screen Engine to Dual-Mode (Stack Trace Chiptunes Album + Arcade Rat)
    with open("tools/simulator_template.html.bak", "r") as f_bak:
        bak_c = f_bak.read()
    s_spl = bak_c.find("const splashState = {")
    e_spl = bak_c.find("// -------------------------------------------------------------------------\n// ACTIVE ARCADE GAME & CRAZY CLIMBER ENGINE")
    assert s_spl != -1 and e_spl != -1 and s_spl < e_spl, "Splash block not found in simulator_template.html.bak"
    old_splash_code = bak_c[s_spl:e_spl].rstrip()

    new_splash_code = """// -------------------------------------------------------------------------
// STACK TRACE: CHIPTUNES ALBUM & ARCADE RAT DUAL-MODE SPLASH SCREEN ENGINE
// -------------------------------------------------------------------------
const splashState = {
  active: true,
  mode: 'album', // 'album' (Stack Trace Chiptunes Album) or 'arcade' (Arcade Rat)
  frame: 0,
  maxFrames: 300,
  chimePlayed: false,
  stars: Array.from({length: 32}, () => ({
    x: Math.random() * 240,
    y: Math.random() * 240,
    spd: 0.5 + Math.random() * 1.8,
    size: Math.random() > 0.7 ? 2 : 1
  }))
};

const stackTraceAvatarImg = new Image();
stackTraceAvatarImg.src = "data:image/png;base64,__STACK_TRACE_AVATAR_B64__";
let avatarLoaded = false;
stackTraceAvatarImg.onload = () => { avatarLoaded = true; };

const stackTraceAlbumImg = new Image();
stackTraceAlbumImg.src = "data:image/jpeg;base64,__STACK_TRACE_ALBUM_B64__";
let albumCoverLoaded = false;
stackTraceAlbumImg.onload = () => { albumCoverLoaded = true; };

function playAlbumStartupChime() {
  if (!audioCtx) return;
  const now = audioCtx.currentTime;

  // Punchy retro 8-bit kick drum
  const kick = audioCtx.createOscillator();
  const kickG = audioCtx.createGain();
  kick.frequency.setValueAtTime(140, now);
  kick.frequency.exponentialRampToValueAtTime(32, now + 0.15);
  kickG.gain.setValueAtTime(0.4, now);
  kickG.gain.exponentialRampToValueAtTime(0.001, now + 0.18);
  kick.connect(kickG);
  kickG.connect(masterGain);
  kick.start(now);
  kick.stop(now + 0.2);

  // Soaring Chiptune Fanfare: C4, G4, C5, E5, G5, B5, C6 (Major 7th Power Arp)
  const arpNotes = [261.63, 392.00, 523.25, 659.25, 783.99, 987.77, 1046.50, 1318.51, 1567.98];
  arpNotes.forEach((freq, idx) => {
    const t = now + 0.08 + idx * 0.045;
    const osc = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    osc.type = idx % 2 === 0 ? 'square' : 'sawtooth';
    osc.frequency.setValueAtTime(freq, t);

    const flt = audioCtx.createBiquadFilter();
    flt.type = 'lowpass';
    flt.frequency.setValueAtTime(3400, t);

    g.gain.setValueAtTime(0.18, t);
    g.gain.exponentialRampToValueAtTime(0.001, t + 0.16);

    osc.connect(flt);
    flt.connect(g);
    g.connect(masterGain);
    osc.start(t);
    osc.stop(t + 0.18);
  });
}

function triggerAlbumSplashScreen() {
  initAudio();
  stopCurrentGame();
  splashState.active = true;
  splashState.mode = 'album';
  splashState.frame = 0;
  splashState.chimePlayed = false;
  playAlbumStartupChime();
}

function triggerSplashScreen() {
  initAudio();
  stopCurrentGame();
  splashState.active = true;
  splashState.mode = 'arcade';
  splashState.frame = 0;
  splashState.chimePlayed = false;
  setMode('arcade');
  playStartupChime();
}

function skipSplashScreen() {
  if (splashState.active) {
    const wasAlbum = (splashState.mode === 'album');
    splashState.active = false;
    initAudio();
    if (wasAlbum) {
      if (typeof setStudioTab === 'function') setStudioTab('demo');
      else setMode('demo');
      playDemoSong();
    }
  }
}

function renderSplashScreen() {
  splashState.frame++;
  const f = splashState.frame;

  if (splashState.mode === 'album') {
    renderAlbumSplashScreen(f);
  } else {
    renderArcadeSplashScreen(f);
  }
}

// -------------------------------------------------------------------------
// STACK TRACE: CHIPTUNES ALBUM SPLASH SCREEN (OFFICIAL ARTWORK & EQUALIZER)
// -------------------------------------------------------------------------
function renderAlbumSplashScreen(f) {
  if (f === 2 && !splashState.chimePlayed) {
    splashState.chimePlayed = true;
    playAlbumStartupChime();
  }

  // Update HUD status banner
  const hud = document.getElementById('hudStatus');
  if (hud) {
    hud.className = 'hud-badge booting';
    hud.textContent = '● STACK TRACE · CHIPTUNES ALBUM';
  }

  // 1. Deep retro CRT dark background
  ctx.fillStyle = '#050807';
  ctx.fillRect(0, 0, 240, 240);

  // Stage 1: CRT Raster Beam Ignition (Frames 0 - 18)
  if (f < 18) {
    const beamW = Math.min(240, f * 14);
    const beamH = Math.max(2, 22 - f);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(120 - beamW / 2, 120 - beamH / 2, beamW, beamH);
    ctx.fillStyle = 'rgba(0, 255, 102, 0.45)';
    ctx.fillRect(120 - beamW / 2, 110, beamW, 20);
    return;
  }

  // Stage 2: Draw Full Square High-Res Album Cover Artwork (Frames 18+)
  const imgReady = (albumCoverLoaded || (stackTraceAlbumImg.complete && stackTraceAlbumImg.naturalWidth > 0));
  if (imgReady) {
    ctx.save();
    let scale = 1.0;
    if (f < 45) {
      scale = 0.94 + (f - 18) / 27 * 0.06;
    }
    const drawW = 240 * scale;
    const drawH = 240 * scale;
    const offX = (240 - drawW) / 2;
    const offY = (240 - drawH) / 2;
    ctx.drawImage(stackTraceAlbumImg, offX, offY, drawW, drawH);
    ctx.restore();
  } else {
    renderAlbumVectorFallback(f);
  }

  // Stage 3: Live Equalizer Visualizer & Phosphor Shimmer (Frames 35+)
  if (f >= 35) {
    const barAlpha = Math.min(0.88, (f - 35) / 25 * 0.88);
    ctx.fillStyle = `rgba(6, 10, 12, ${barAlpha})`;
    ctx.fillRect(0, 194, 240, 46);

    ctx.strokeStyle = 'rgba(0, 255, 102, 0.6)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, 194);
    ctx.lineTo(240, 194);
    ctx.stroke();

    // 16 Bouncing Equalizer Bars
    for (let b = 0; b < 16; b++) {
      const bx = 10 + b * 14;
      const h = Math.abs(Math.sin((f * 0.14) + b * 0.65)) * 14 + (b % 3 === 0 ? 4 : 2);
      ctx.fillStyle = b < 5 ? '#00ff66' : (b < 11 ? '#00e5ff' : '#ff4757');
      ctx.fillRect(bx, 208 - h, 10, h);
    }

    ctx.save();
    ctx.textAlign = 'center';
    ctx.font = 'bold 8px monospace';
    ctx.fillStyle = '#00ff66';
    ctx.shadowColor = '#00ff66';
    ctx.shadowBlur = 6;
    ctx.fillText('STACK TRACE_ · CHIPTUNES LP', 120, 218);
    ctx.restore();

    const pulse = Math.floor(f / 16) % 2 === 0;
    ctx.fillStyle = pulse ? '#fffa65' : '#ffffff';
    ctx.font = 'bold 8px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('⚡ PRESS SPACE / ANY KEY TO PLAY', 120, 232);
    ctx.textAlign = 'left';
  }

  // Auto-transition after maxFrames (300 frames = ~5s)
  if (f >= splashState.maxFrames) {
    splashState.active = false;
    if (typeof setStudioTab === 'function') setStudioTab('demo');
    else setMode('demo');
    playDemoSong();
  }
}

function renderAlbumVectorFallback(f) {
  ctx.fillStyle = '#0c1015';
  ctx.fillRect(0, 0, 240, 240);
  ctx.fillStyle = '#00ff66';
  ctx.textAlign = 'center';
  ctx.font = 'bold 16px monospace';
  ctx.fillText('CHIPTUNES', 120, 70);
  ctx.font = 'bold 9px monospace';
  ctx.fillStyle = '#a0ffc8';
  ctx.fillText("YOU DIDN'T KNOW YOU NEEDED TO HEAR", 120, 90);
  ctx.fillStyle = '#00e5ff';
  ctx.font = 'bold 10px monospace';
  ctx.fillText('STACK TRACE_', 120, 150);
}

// -------------------------------------------------------------------------
// STACK TRACE: ARCADE RAT FIRMWARE BOOT SPLASH SCREEN
// -------------------------------------------------------------------------
function renderArcadeSplashScreen(f) {
  if (f === 2 && !splashState.chimePlayed) {
    splashState.chimePlayed = true;
    playStartupChime();
  }

  const hud = document.getElementById('hudStatus');
  if (hud) {
    hud.className = 'hud-badge booting';
    hud.textContent = '● STACK TRACE SPLASH';
  }

  ctx.fillStyle = '#060a08';
  ctx.fillRect(0, 0, 240, 240);

  ctx.fillStyle = '#00ff66';
  for (let s of splashState.stars) {
    s.y += s.spd;
    if (s.y > 240) { s.y = 0; s.x = Math.random() * 240; }
    ctx.fillRect(Math.floor(s.x), Math.floor(s.y), s.size, s.size);
  }

  if (f < 25) {
    const beamW = Math.min(240, f * 12);
    const beamH = Math.max(2, 24 - f);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(120 - beamW / 2, 120 - beamH / 2, beamW, beamH);
    ctx.fillStyle = 'rgba(0, 255, 102, 0.4)';
    ctx.fillRect(120 - beamW / 2, 110, beamW, 20);
    return;
  }

  const cx = 120, cy = 76;
  const avatarR = 34;

  ctx.save();
  ctx.beginPath();
  ctx.arc(cx, cy, avatarR, 0, Math.PI * 2);
  ctx.closePath();
  ctx.clip();
  if (avatarLoaded) {
    ctx.drawImage(stackTraceAvatarImg, cx - avatarR, cy - avatarR, avatarR * 2, avatarR * 2);
  } else {
    ctx.fillStyle = '#0f2415';
    ctx.fillRect(cx - avatarR, cy - avatarR, avatarR * 2, avatarR * 2);
    ctx.fillStyle = '#00ff66';
    ctx.font = 'bold 20px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('ST', cx, cy + 7);
  }
  ctx.restore();

  ctx.textAlign = 'center';

  if (f >= 45) {
    ctx.save();
    ctx.font = 'bold 12px monospace';
    ctx.fillStyle = '#00ff66';
    ctx.shadowColor = '#00ff66';
    ctx.shadowBlur = 8;
    ctx.fillText('STACK TRACE', cx, 132);
    ctx.restore();
  }

  if (f >= 70) {
    ctx.font = '800 8px monospace';
    ctx.fillStyle = '#a0ffc8';
    ctx.fillText('— PRESENTS —', cx, 146);
  }

  if (f >= 95) {
    ctx.save();
    ctx.font = '900 20px -apple-system, monospace';
    ctx.fillStyle = '#f5a623';
    ctx.shadowColor = '#ff6600';
    ctx.shadowBlur = 12;
    ctx.fillText('ARCADE RAT', cx, 172);
    ctx.restore();

    ctx.fillStyle = '#e74c3c';
    ctx.fillRect(cx - 24, 180, 48, 14);
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 9px monospace';
    ctx.fillText('v 1.0', cx, 191);
  }

  if (f >= 125) {
    ctx.font = '8px monospace';
    ctx.textAlign = 'left';

    const diag = [
      '[OK] Z80 CORE @ 3.072MHz',
      '[OK] 4-CHIP SYNTH STACK',
      '[OK] 12-GAME FLASH VAULT',
      '>> PRESS ANY KEY TO PLAY <<'
    ];
    const linesToShow = Math.min(4, Math.floor((f - 125) / 18) + 1);
    for (let i = 0; i < linesToShow; i++) {
      if (i === 3) {
        if (Math.floor(f / 15) % 2 === 0) {
          ctx.fillStyle = '#f5a623';
          ctx.fillText(diag[i], 36, 208 + i * 10);
        }
      } else {
        ctx.fillStyle = '#00ff88';
        ctx.fillText(diag[i], 36, 208 + i * 10);
      }
    }
  }

  if (f >= splashState.maxFrames) {
    splashState.active = false;
    currentMode = 'arcade';
  }
}"""
    assert old_splash_code in script_body, "old_splash_code not found in script_body!"
    script_body = script_body.replace(old_splash_code, new_splash_code)


    # 5. Add additional hardware bindings before the closing </script>
    additional_bindings = speech_gen.get_speech_sample_engine_js().strip() + "\n\n" + lb_gen.get_leaderboard_engine_js().strip() + """
// -------------------------------------------------------------------------
// VINTAGE ARCADE SPEECH & LEADERBOARD HELPER BINDINGS
// -------------------------------------------------------------------------
var lastSpeechRomId = 'VOX_INTRUDER';
function triggerSpeechRom(id) {
  initAudio();
  lastSpeechRomId = id;
  lastSfxName = id;
  const executePlay = () => {
    if (typeof playArcadeSpeechSample === 'function') {
      playArcadeSpeechSample(id);
    } else if (typeof playSpeechSample === 'function') {
      playSpeechSample(id);
    }
  };
  if (audioCtx && audioCtx.state === 'suspended') {
    audioCtx.resume().then(executePlay).catch(executePlay);
  } else {
    executePlay();
  }
  const tag = document.getElementById('sfxLastTriggered');
  if (tag) tag.textContent = 'SPEECH: ' + id;
  const spDisp = document.getElementById('speechStatusDisplay');
  if (spDisp) spDisp.textContent = 'SPEAKING: ' + id + ' (FORMANT SYNTHESIS ACTIVE)';
  const card = document.getElementById('card_' + id);
  if (card) {
    card.classList.add('speech-card-active');
    setTimeout(() => card.classList.remove('speech-card-active'), 400);
  }
}

// Global hotkeys for Speech ROM
window.addEventListener('keydown', (e) => {
  const k = e.key.toLowerCase();
  if ((k === 'v' || e.key === 'V') && !e.ctrlKey && !e.metaKey && !e.altKey) {
    if (currentStudioTab === 'speech') {
      setStudioTab('arcade');
    } else {
      setStudioTab('speech');
    }
    e.preventDefault();
    return;
  }
  if (currentStudioTab === 'speech' && !e.ctrlKey && !e.metaKey && !e.altKey) {
    const speechKeys = ['VOX_INTRUDER', 'VOX_COIN', 'VOX_QBERT', 'VOX_SINISTAR', 'VOX_HUNGER', 'VOX_WIZARD', 'VOX_GORF', 'VOX_DRAGON'];
    const num = parseInt(e.key);
    if (!isNaN(num) && num >= 1 && num <= 8) {
      triggerSpeechRom(speechKeys[num - 1]);
      e.preventDefault();
      return;
    }
  }
});

function getPacmanCurrentScore() {
  if (typeof ram === 'undefined' || !ram) return 0;
  // Read 6-digit 1UP score from Pac-Man tile VRAM (0x03F7 = ones .. 0x03FC = hundred-thousands)
  let vramScore = 0;
  let mul = 1;
  let hasDigit = false;
  for (let addr = 0x03f7; addr <= 0x03fc; addr++) {
    const tile = ram[addr];
    if (tile !== undefined && tile <= 9) {
      vramScore += tile * mul;
      hasDigit = true;
    }
    mul *= 10;
  }
  if (hasDigit && vramScore > 0) return vramScore;
  const eatenDots = ram[0x4e0e - 0x4000] || 0;
  return eatenDots > 0 ? eatenDots * 10 : 0;
}

function promptCurrentGameInitials() {
  const gId = activeGame || 'pacman';
  let curScore = 10000;
  if (gId === 'pacman') curScore = getPacmanCurrentScore() || 3200;
  else if (gId === 'cclimber' && typeof climberState !== 'undefined') curScore = climberState.score || 12000;
  else if (gId === 'galaga' && typeof galagaGame !== 'undefined') curScore = galagaGame.score || 24000;
  else if (gId === 'dkong' && typeof dkongGame !== 'undefined') curScore = dkongGame.score || 8500;
  else if (gId === 'frogger' && typeof froggerGame !== 'undefined') curScore = froggerGame.score || 4200;
  else if (gId === 'asteroids' && typeof asteroidsGame !== 'undefined') curScore = asteroidsGame.score || 18000;
  else if (gId === 'tempest' && typeof tempestGame !== 'undefined') curScore = tempestGame.score || 9500;
  else if (gId === 'gyruss' && typeof gyrussGame !== 'undefined') curScore = gyrussGame.score || 14000;
  promptInitialsEntry(gId, curScore);
}

// Universal 8-Game State Snapshot & Rewind Engine
function captureRewindSnapshot() {
  const g = activeGame || 'pacman';
  if (g === 'pacman') {
    return { game: 'pacman', ram: new Uint8Array(ram), spritePos: new Uint8Array(spritePos), animTick };
  } else if (g === 'galaga' && typeof galagaGame !== 'undefined') {
    return { game: 'galaga', shipX: galagaGame.shipX, score: galagaGame.score, lives: galagaGame.lives, stage: galagaGame.stage, tick: galagaGame.tick };
  } else if (g === 'dkong' && typeof dkongGame !== 'undefined') {
    return { game: 'dkong', mx: dkongGame.mario.x, my: dkongGame.mario.y, mvx: dkongGame.mario.vx, mvy: dkongGame.mario.vy, girder: dkongGame.mario.currentGirder, state: dkongGame.mario.state, onGround: dkongGame.mario.onGround, score: dkongGame.score, lives: dkongGame.lives, tick: dkongGame.tick };
  } else if (g === 'frogger' && typeof froggerGame !== 'undefined') {
    return { game: 'frogger', gx: froggerGame.frog.gridX, gy: froggerGame.frog.gridY, fx: froggerGame.frog.x, fy: froggerGame.frog.y, dead: froggerGame.frog.dead, score: froggerGame.score, lives: froggerGame.lives, tick: froggerGame.tick };
  } else if (g === 'asteroids' && typeof asteroidsGame !== 'undefined') {
    return { game: 'asteroids', sx: asteroidsGame.ship.x, sy: asteroidsGame.ship.y, vx: asteroidsGame.ship.vx, vy: asteroidsGame.ship.vy, angle: asteroidsGame.ship.angle, score: asteroidsGame.score, lives: asteroidsGame.lives, tick: asteroidsGame.tick };
  } else if (g === 'tempest' && typeof tempestGame !== 'undefined') {
    return { game: 'tempest', seg: tempestGame.segment, score: tempestGame.score, lives: tempestGame.lives, tube: tempestGame.tube, tick: tempestGame.tick };
  } else if (g === 'gyruss' && typeof gyrussGame !== 'undefined') {
    return { game: 'gyruss', angle: gyrussGame.angle, score: gyrussGame.score, lives: gyrussGame.lives, warp: gyrussGame.warp, tick: gyrussGame.tick };
  } else if (g === 'cclimber' && typeof climberState !== 'undefined') {
    return { game: 'cclimber', floor: climberState.floor, col: climberState.col, leftY: climberState.leftY, rightY: climberState.rightY, score: climberState.score, lives: climberState.lives, animTick: climberState.animTick };
  }
  return { game: g };
}

function applyRewindSnapshot(snap) {
  if (!snap) return;
  if (snap.game === 'pacman' && snap.ram && snap.spritePos) {
    ram.set(snap.ram);
    spritePos.set(snap.spritePos);
  } else if (snap.game === 'galaga' && typeof galagaGame !== 'undefined') {
    galagaGame.shipX = snap.shipX; galagaGame.score = snap.score; galagaGame.lives = snap.lives; galagaGame.stage = snap.stage; galagaGame.tick = snap.tick; galagaGame.gameOver = false;
  } else if (snap.game === 'dkong' && typeof dkongGame !== 'undefined') {
    dkongGame.mario.x = snap.mx; dkongGame.mario.y = snap.my; dkongGame.mario.vx = snap.mvx; dkongGame.mario.vy = snap.mvy; dkongGame.mario.currentGirder = snap.girder; dkongGame.mario.state = snap.state; dkongGame.mario.onGround = snap.onGround; dkongGame.score = snap.score; dkongGame.lives = snap.lives; dkongGame.tick = snap.tick; dkongGame.gameOver = false;
  } else if (snap.game === 'frogger' && typeof froggerGame !== 'undefined') {
    froggerGame.frog.gridX = snap.gx; froggerGame.frog.gridY = snap.gy; froggerGame.frog.x = snap.fx; froggerGame.frog.y = snap.fy; froggerGame.frog.dead = snap.dead; froggerGame.score = snap.score; froggerGame.lives = snap.lives; froggerGame.tick = snap.tick; froggerGame.gameOver = false;
  } else if (snap.game === 'asteroids' && typeof asteroidsGame !== 'undefined') {
    asteroidsGame.ship.x = snap.sx; asteroidsGame.ship.y = snap.sy; asteroidsGame.ship.vx = snap.vx; asteroidsGame.ship.vy = snap.vy; asteroidsGame.ship.angle = snap.angle; asteroidsGame.ship.dead = false; asteroidsGame.score = snap.score; asteroidsGame.lives = snap.lives; asteroidsGame.tick = snap.tick; asteroidsGame.gameOver = false;
  } else if (snap.game === 'tempest' && typeof tempestGame !== 'undefined') {
    tempestGame.segment = snap.seg; tempestGame.score = snap.score; tempestGame.lives = snap.lives; tempestGame.tube = snap.tube; tempestGame.tick = snap.tick; tempestGame.gameOver = false;
  } else if (snap.game === 'gyruss' && typeof gyrussGame !== 'undefined') {
    gyrussGame.angle = snap.angle; gyrussGame.score = snap.score; gyrussGame.lives = snap.lives; gyrussGame.warp = snap.warp; gyrussGame.tick = snap.tick; gyrussGame.gameOver = false;
  } else if (snap.game === 'cclimber' && typeof climberState !== 'undefined') {
    climberState.floor = snap.floor; climberState.col = snap.col; climberState.leftY = snap.leftY; climberState.rightY = snap.rightY; climberState.score = snap.score; climberState.lives = snap.lives; climberState.animTick = snap.animTick; climberState.gameOver = false;
  }
}

function renderLeaderboardUI(gameId) {
  const gId = gameId || activeGame || 'pacman';
  const tag = document.getElementById('lbCurrentGameTag');
  if (tag) tag.textContent = gId.toUpperCase() + ' · TOP 5';
  const list = (typeof arcadeLeaderboards !== 'undefined' && arcadeLeaderboards[gId]) ? arcadeLeaderboards[gId] : [];
  const container = document.getElementById('arcadeLeaderboardList');
  if (container) {
    container.innerHTML = '';
    list.forEach(item => {
      const col = document.createElement('div');
      col.style.background = 'rgba(255,255,255,0.04)';
      col.style.padding = '4px 6px';
      col.style.borderRadius = '4px';
      col.style.border = '1px solid rgba(255,255,255,0.08)';
      col.style.textAlign = 'center';
      const colors = ['#f5cd79', '#d2dae2', '#cd84f1', '#70a1ff', '#7bed9f'];
      col.innerHTML = `<div style="color:${colors[item.rank - 1] || '#fff'}; font-weight:900;">#${item.rank} ${item.initials}</div><div style="font-size:0.6rem; color:#aae4c8; margin-top:2px;">${Number(item.score).toLocaleString()}</div>`;
      container.appendChild(col);
    });
  }
}

// -------------------------------------------------------------------------
// ARCADE MISSIONS DATA & DYNAMIC MISSION CARD
// -------------------------------------------------------------------------
const ARCADE_MISSIONS = {
  pacman: {
    title: 'PAC-MAN (1980 NAMCO)',
    badge: 'MAZE CHASE · BARE-METAL Z80 + WSG',
    objective: 'Navigate the maze, eat all 244 dots and 4 energizers! Avoid Blinky, Pinky, Inky & Clyde.',
    controls: '<b>WASD</b> or <b>Arrow Keys</b> or <b>Screen Quadrants</b> to Turn · <b>1</b> (Coin) · <b>5</b> (1P Start) · <b>Space</b> (Quick Play)',
    tip: 'Eat power pellets to turn ghosts blue and gobble them for 200, 400, 800, 1600 bonus points!'
  },
  cclimber: {
    title: 'CRAZY CLIMBER (1980 NICHIBUTSU)',
    badge: 'TWIN-STICK CLIMBER · DUAL AY-3-8910',
    objective: 'Climb 50 floors of the skyscraper to catch the rescue helicopter waiting on the roof!',
    controls: '<b>W / S</b> (Left Arm Up/Down) · <b>▲ / ▼</b> (Right Arm Up/Down) · <b>A / D</b> (Move Column) · or Tap Screen Quadrants',
    tip: 'Alternate left and right arm reaches to climb rapidly! Watch for opening window frames and dodge falling flower pots!'
  },
  galaga: {
    title: 'GALAGA (1981 NAMCO)',
    badge: 'SPACE SHOOTER · DUAL Z80 + 3-VOICE WSG',
    objective: 'Destroy all waves of the alien insect fleet before they dive-bomb and capture your fighter!',
    controls: '<b>A / D</b> or <b>◀ / ▶</b> (Steer Fighter) · <b>Space / Enter / 1</b> (Twin Lasers)',
    tip: 'Shoot Boss Galagas while in dive flight for double points (400 pts)! Let your ship get captured to rescue it for Dual Fighter mode!'
  },
  dkong: {
    title: 'DONKEY KONG (1981 NINTENDO)',
    badge: 'PLATFORMER ICON · 25M SLOPED GIRDERS',
    objective: 'Climb the sloped steel girders to reach Pauline at the top and rescue her from Donkey Kong!',
    controls: '<b>A / D</b> (Run) · <b>W / S</b> (Climb Ladders) · <b>Space / Enter</b> (Jump Barrels) · <b>S</b> (Grab Hammer)',
    tip: 'Jump directly over rolling barrels for +100 bonus! Grab the hammer to smash barrels for +300 points!'
  },
  frogger: {
    title: 'FROGGER (1981 KONAMI)',
    badge: 'TRAFFIC & RIVER HOP · DUAL AY-3-8910',
    objective: 'Guide all 5 frogs safely across the 5-lane highway and treacherous river into the 5 home lily bays!',
    controls: '<b>WASD</b> or <b>Arrow Keys</b> or <b>D-Pad</b> or <b>Screen Quadrants</b> to Hop',
    tip: 'Catch floating flies in the home bay for +200 bonus! Be careful of diving turtles that submerge underwater!'
  },
  asteroids: {
    title: 'ASTEROIDS (1979 ATARI)',
    badge: 'VECTOR CRT CLASSIC · QUADRASCAN 6502',
    objective: 'Blast space asteroids into rubble while avoiding collisions and dodging alien flying saucers!',
    controls: '<b>A / D</b> (Rotate) · <b>W / Up</b> (Thruster) · <b>Space / 1</b> (Photon Torpedo) · <b>S</b> (Hyperspace)',
    tip: 'Large asteroids split into 2 mediums (50 pts), then 2 smalls (100 pts). Use short thrust pulses to control momentum!'
  },
  tempest: {
    title: 'TEMPEST (1981 ATARI)',
    badge: '3D COLOR VECTOR TUBE · POKEY SYNTH',
    objective: 'Spin your rotary claw blaster around the edge of the 3D tube and destroy crawling Flippers and Spikers!',
    controls: '<b>A / D</b> or <b>◀ / ▶</b> (Rotary Spin) · <b>Space / 1</b> (Particle Fire) · <b>W / Up</b> (Superzapper)',
    tip: 'Use your Superzapper shockwave once per level to instantly destroy all enemies on the tube!'
  },
  gyruss: {
    title: 'GYRUSS (1983 KONAMI)',
    badge: '360° COSMIC ODYSSEY · 5x PSG BAROQUE',
    objective: 'Warp through space from Neptune to Earth, spiraling around the 360° orbital perimeter while firing inward!',
    controls: '<b>A / D</b> or <b>◀ / ▶</b> (360° Orbital Flight) · <b>Space / Enter / 1</b> (Twin Cannons)',
    tip: 'Time your circular sweep to meet emerging enemy waves as they exit the central warp core for chain bonuses!'
  }
};

function updateMissionCard(gameId) {
  const m = ARCADE_MISSIONS[gameId] || ARCADE_MISSIONS.pacman;
  const elTitle = document.getElementById('missionTitle');
  const elBadge = document.getElementById('missionBadge');
  const elObj = document.getElementById('missionObjective');
  const elCtrl = document.getElementById('missionControls');
  const elTip = document.getElementById('missionTip');
  if (elTitle) elTitle.textContent = m.title;
  if (elBadge) elBadge.textContent = m.badge;
  if (elObj) elObj.innerHTML = m.objective;
  if (elCtrl) elCtrl.innerHTML = m.controls;
  if (elTip) elTip.innerHTML = m.tip;
  if (typeof renderLeaderboardUI === 'function') renderLeaderboardUI(gameId);
}

// -------------------------------------------------------------------------
// DYNAMIC DEMO JUKEBOX SHELF PILLS
// -------------------------------------------------------------------------
function populateShelfSongPills() {
  const c = document.getElementById('shelfSongPills');
  if (c && typeof DEMO_SONGS !== 'undefined') {
    c.innerHTML = '';
    DEMO_SONGS.forEach((song, idx) => {
      const btn = document.createElement('button');
      btn.className = 'synth-chip-btn' + (idx === (demoPlayer ? demoPlayer.currentSongIdx : 0) ? ' active' : '');
      const icons = ['🟡', '🌌', '🌀', '🦍'];
      btn.innerHTML = `${icons[idx % icons.length]} <b>${song.title}</b> (${song.bpm} BPM)`;
      btn.onclick = () => {
        selectDemoSong(idx);
        playDemoSong();
      };
      c.appendChild(btn);
    });
  }
}

// -------------------------------------------------------------------------
// 2X CRT SCREEN ZOOM & FULL FOCUS
// -------------------------------------------------------------------------
function toggleScreenZoom() {
  const bez = document.getElementById('screenBezel');
  const overlay = document.getElementById('zoomOverlay');
  const btnZoom = document.getElementById('ctrlBtnZoom');
  const btnZoomCap = document.getElementById('btnZoomScreen');
  if (bez) {
    const isZoomed = bez.classList.toggle('zoomed');
    if (overlay) overlay.classList.toggle('active', isZoomed);
    if (btnZoom) btnZoom.textContent = isZoomed ? '🔍 NORMAL' : '🔍 ZOOM';
    if (btnZoomCap) btnZoomCap.textContent = isZoomed ? '🔍 NORMAL' : '🔍 ZOOM 2X';
  }
}

// -------------------------------------------------------------------------
// ON-SCREEN CONTROLLER DECK & HARDWARE BINDINGS
// -------------------------------------------------------------------------
function pulseUnifiedAction(act) {
  initAudio();
  handleUnifiedAction(act, true);
  safeTimeout(() => {
    if (dpadActiveDir !== act) {
      handleUnifiedAction(act, false);
    }
  }, 90);
}

function bindDeckBtn(id, act) {
  const btn = document.getElementById(id);
  if (!btn) return;
  const start = (e) => {
    e.preventDefault();
    initAudio();
    if (act === 'left' || act === 'right' || act === 'up' || act === 'down') dpadActiveDir = act;
    handleUnifiedAction(act, true);
    btn.classList.add('pressed');
  };
  const end = (e) => {
    e.preventDefault();
    if (dpadActiveDir === act) dpadActiveDir = null;
    handleUnifiedAction(act, false);
    btn.classList.remove('pressed');
  };
  btn.onmousedown = start; btn.onmouseup = end; btn.onmouseleave = end;
  btn.ontouchstart = start; btn.ontouchend = end;
}
bindDeckBtn('ctrlBtnLeft', 'left');
bindDeckBtn('ctrlBtnRight', 'right');
bindDeckBtn('ctrlBtnUp', 'up');
bindDeckBtn('ctrlBtnDown', 'down');
bindDeckBtn('ctrlBtnFire', 'action');
bindDeckBtn('shelfBtnLeft', 'left');
bindDeckBtn('shelfBtnRight', 'right');
bindDeckBtn('shelfBtnUp', 'up');
bindDeckBtn('shelfBtnDown', 'down');
bindDeckBtn('shelfBtnFire', 'action');

// Mode-aware Hardware PLAY / STOP (#btnQuickPlay) and REC / REWIND (#btnRewind)
const hwQuickPlay = document.getElementById('btnQuickPlay');
if (hwQuickPlay) {
  hwQuickPlay.onclick = () => {
    initAudio();
    if (typeof splashState !== 'undefined' && splashState.active) {
      skipSplashScreen();
      return;
    }
    if (currentMode === 'tracker') {
      toggleTracker();
    } else if (currentMode === 'demo') {
      if (demoPlayer.playing) pauseDemoSong(); else playDemoSong();
    } else if (currentMode === 'tour') {
      launchCurrentTourGame();
    } else if (currentMode === 'synth') {
      toggleArp();
    } else if (currentMode === 'soundboard') {
      if (currentStudioTab === 'speech') triggerSpeechRom(lastSpeechRomId || 'VOX_INTRUDER');
      else playArcadeSfx((typeof sfxNames !== 'undefined' && sfxNames[0]) ? sfxNames[0] : 'COIN');
    } else {
      quickPlay();
    }
  };
}

const hwRewind = document.getElementById('btnRewind');
if (hwRewind) {
  const startRew = (e) => { if (e && e.preventDefault) e.preventDefault(); initAudio(); isRewinding = true; setMode('rewind'); };
  const stopRew = (e) => { if (e && e.preventDefault) e.preventDefault(); if (isRewinding || currentMode === 'rewind') { isRewinding = false; setMode('arcade'); } };
  hwRewind.onmousedown = startRew;
  hwRewind.onmouseup = stopRew;
  hwRewind.onmouseleave = stopRew;
  hwRewind.ontouchstart = startRew;
  hwRewind.ontouchend = stopRew;
}

if (typeof canvas !== 'undefined' && canvas) {
  const releaseCanvasSteer = () => {
    if (dpadActiveDir) {
      handleUnifiedAction(dpadActiveDir, false);
      dpadActiveDir = null;
    }
    handleUnifiedAction('left', false);
    handleUnifiedAction('right', false);
    handleUnifiedAction('up', false);
    handleUnifiedAction('down', false);
    handleUnifiedAction('action', false);
  };
  canvas.onmouseup = releaseCanvasSteer;
  canvas.onmouseleave = releaseCanvasSteer;
  if (typeof window !== 'undefined' && window.addEventListener) {
    window.addEventListener('mouseup', releaseCanvasSteer);
  }
}

const cCoin = document.getElementById('ctrlBtnCoin');
if (cCoin) cCoin.onclick = (e) => { e.preventDefault(); insertCoin(); };
const cStart = document.getElementById('ctrlBtnStart');
if (cStart) cStart.onclick = (e) => { e.preventDefault(); start1P(); };
const cZoom = document.getElementById('ctrlBtnZoom');
if (cZoom) cZoom.onclick = () => toggleScreenZoom();
const cZoomCap = document.getElementById('btnZoomScreen');
if (cZoomCap) cZoomCap.onclick = () => toggleScreenZoom();

const cGod = document.getElementById('ctrlBtnImmortal');
if (cGod) cGod.onclick = (e) => { e.preventDefault(); toggleImmortalMode(); };
const cSkip = document.getElementById('ctrlBtnLevelSkip');
if (cSkip) cSkip.onclick = (e) => { e.preventDefault(); skipCurrentLevel(); };

// =========================================================================
// UNIVERSAL IMMORTAL (GOD) MODE & LEVEL SKIP ENGINE (ALL 8 GAMES)
// =========================================================================
let arcadeImmortalMode = false;
let osdBannerText = '';
let osdBannerTimer = 0;

function showOsdBanner(text) {
  osdBannerText = text;
  osdBannerTimer = 90;
  const hud = document.getElementById('hudStatus');
  if (hud) {
    const origText = hud.textContent;
    hud.textContent = text;
    setTimeout(() => { if (hud) hud.textContent = origText; }, 1800);
  }
}

function toggleImmortalMode(forceVal) {
  initAudio();
  arcadeImmortalMode = (typeof forceVal === 'boolean') ? forceVal : !arcadeImmortalMode;

  // 1. Pac-Man Z80 Unlimited Lives Patch at 0x0315 (NOP NOP out SUB 1)
  if (typeof prgRom !== 'undefined' && prgRom) {
    if (arcadeImmortalMode) {
      prgRom[0x0315] = 0x00;
      prgRom[0x0316] = 0x00;
      if (typeof ram !== 'undefined' && ram) ram[0x4e6e - 0x4000] = 99;
    } else {
      prgRom[0x0315] = 0xd6;
      prgRom[0x0316] = 0x01;
      if (typeof ram !== 'undefined' && ram) ram[0x4e6e - 0x4000] = 3;
    }
  }

  // 2. Set unlimited lives across all active games
  if (arcadeImmortalMode) {
    if (typeof dkongGame !== 'undefined') { dkongGame.lives = 99; dkongGame.gameOver = false; }
    if (typeof galagaGame !== 'undefined') { galagaGame.lives = 99; galagaGame.gameOver = false; }
    if (typeof froggerGame !== 'undefined') { froggerGame.lives = 99; froggerGame.gameOver = false; }
    if (typeof asteroidsGame !== 'undefined') { asteroidsGame.lives = 99; asteroidsGame.gameOver = false; }
    if (typeof tempestGame !== 'undefined') { tempestGame.lives = 99; tempestGame.gameOver = false; }
    if (typeof gyrussGame !== 'undefined') { gyrussGame.lives = 99; gyrussGame.gameOver = false; }
    if (typeof climberState !== 'undefined') { climberState.lives = 99; climberState.gameOver = false; }
  } else {
    if (typeof dkongGame !== 'undefined') dkongGame.lives = 3;
    if (typeof galagaGame !== 'undefined') galagaGame.lives = 3;
    if (typeof froggerGame !== 'undefined') froggerGame.lives = 3;
    if (typeof asteroidsGame !== 'undefined') asteroidsGame.lives = 3;
    if (typeof tempestGame !== 'undefined') tempestGame.lives = 3;
    if (typeof gyrussGame !== 'undefined') gyrussGame.lives = 3;
    if (typeof climberState !== 'undefined') climberState.lives = 3;
  }

  // 3. Hardware / Cockpit button state
  const btn = document.getElementById('ctrlBtnImmortal');
  if (btn) {
    btn.classList.toggle('active', arcadeImmortalMode);
    btn.innerHTML = arcadeImmortalMode ? '⚡ UNLIMITED LIVES' : '⚡ IMMORTAL';
  }
  const tag = document.getElementById('immortalLedTag');
  if (tag) {
    tag.style.display = arcadeImmortalMode ? 'inline-block' : 'none';
    tag.textContent = '⚡ UNLIMITED LIVES';
  }

  // 4. Audio cue
  if (typeof playArcadeSfx === 'function') {
    playArcadeSfx(arcadeImmortalMode ? 'WARP' : 'BONUS');
  }

  // 5. OSD Notification
  showOsdBanner(arcadeImmortalMode ? '⚡ IMMORTAL MODE: UNLIMITED LIVES (∞)' : '⚡ IMMORTAL MODE: DISABLED (3 LIVES)');
  return arcadeImmortalMode;
}

function skipCurrentLevel() {
  initAudio();
  const g = activeGame || 'pacman';
  let bannerText = 'STAGE ADVANCED';

  if (g === 'pacman') {
    keyRackAdvance = true;
    setTimeout(() => { keyRackAdvance = false; }, 150);
    if (typeof ram !== 'undefined' && ram) {
      // 1. Advance fruit / level counter cleanly
      if (ram[0x4e13 - 0x4000] !== undefined) {
        ram[0x4e13 - 0x4000] = (ram[0x4e13 - 0x4000] + 1) & 0xff;
      }
      // 2. Reset eaten dots counter to 0 for the fresh maze
      if (ram[0x4e0e - 0x4000] !== undefined) {
        ram[0x4e0e - 0x4000] = 0;
      }
      // 3. Keep Energizer Subsystem active flag enabled (0x01) so power pills work on all mazes!
      if (ram[0x4e14 - 0x4000] !== undefined) {
        ram[0x4e14 - 0x4000] = 1;
      }
      // 4. Restore all 30 bytes of pellet bitmask array ($4E16..$4E33) to 0xFF (all pellets active)
      for (let b = 0x4e16; b <= 0x4e33; b++) {
        ram[b - 0x4000] = 0xff;
      }
      // 5. Restore the 4 energizer slots ($4E34..$4E37)
      for (let b = 0x4e34; b <= 0x4e37; b++) {
        ram[b - 0x4000] = 0x14;
      }
      // 6. Fully replenish all 240 pellets and 4 power pills in VRAM
      const dotIndices = [98,99,101,102,103,104,105,117,118,119,123,124,125,126,130,134,137,149,152,155,158,162,166,169,181,184,185,186,187,190,194,198,201,213,219,222,226,230,233,245,251,254,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,286,290,294,309,312,318,322,326,341,344,350,354,358,359,360,361,373,376,377,378,379,382,386,390,393,405,408,411,414,418,422,425,437,440,443,446,450,451,452,453,454,457,469,470,471,472,475,476,477,478,486,510,518,542,546,547,548,549,550,553,565,566,567,568,571,572,573,574,578,582,585,597,600,603,606,610,614,617,629,632,635,638,642,646,647,648,649,661,664,665,666,667,670,674,678,693,696,702,706,710,725,728,734,738,739,740,741,742,743,744,745,746,747,748,749,750,751,752,753,754,755,756,757,758,759,760,761,762,763,766,770,774,777,789,795,798,802,806,809,821,827,830,834,838,841,853,856,857,858,859,862,866,870,873,885,888,891,894,898,899,901,902,903,904,905,917,918,919,923,924,925,926];
      for (let i = 0; i < dotIndices.length; i++) {
        ram[dotIndices[i]] = 0x10;
      }
      ram[100] = 0x14; ram[120] = 0x14; ram[900] = 0x14; ram[920] = 0x14;
    }
    const currentLvl = (typeof ram !== 'undefined' && ram) ? (ram[0x4e13 - 0x4000] || 1) : 1;
    bannerText = `PAC-MAN: LEVEL ${currentLvl + 1} (240 PELLETS + 4 POWER PILLS)`;
  } else if (g === 'dkong') {
    if (typeof dkongGame !== 'undefined') {
      dkongGame.level++;
      dkongGame.cleared = false;
      dkongGame.mario.x = 40;
      dkongGame.mario.y = 220;
      dkongGame.mario.vx = 0;
      dkongGame.mario.vy = 0;
      dkongGame.mario.currentGirder = 0;
      dkongGame.mario.state = 'stand';
      dkongGame.mario.onGround = true;
      dkongGame.barrels = [];
      dkongGame.fireballs = [];
      dkongGame.bonusTimer = Math.min(8000, 5000 + dkongGame.level * 500);
      playArcadeSfx('DK-WIN');
      bannerText = `DONKEY KONG: LEVEL ${dkongGame.level} (25M)`;
    }
  } else if (g === 'galaga') {
    if (typeof galagaGame !== 'undefined') {
      galagaGame.aliens = [];
      galagaGame.bombs = [];
      galagaGame.stage++;
      if (galagaGame.stage % 4 === 3) {
        galagaGame.isChallengingStage = true;
        galagaGame.hitsCount = 0;
      } else {
        galagaGame.isChallengingStage = false;
      }
      spawnGalagaFleet();
      playArcadeSfx('BONUS');
      bannerText = `GALAGA: STAGE ${galagaGame.stage}${galagaGame.isChallengingStage ? ' (CHALLENGING)' : ''}`;
    }
  } else if (g === 'frogger') {
    if (typeof froggerGame !== 'undefined') {
      froggerGame.level++;
      froggerGame.homeBays = [false, false, false, false, false];
      froggerGame.score += 1000;
      froggerGame.frog.gridX = 7;
      froggerGame.frog.gridY = 13;
      froggerGame.frog.x = 120;
      froggerGame.frog.y = 224;
      playArcadeSfx('FROG-FANFARE');
      bannerText = `FROGGER: LEVEL ${froggerGame.level}`;
    }
  } else if (g === 'asteroids') {
    if (typeof asteroidsGame !== 'undefined') {
      asteroidsGame.rocks = [];
      if (asteroidsGame.saucer) asteroidsGame.saucer.active = false;
      asteroidsGame.saucerBullets = [];
      asteroidsGame.level++;
      spawnAsteroidsField(4 + asteroidsGame.level);
      playArcadeSfx('WARP');
      bannerText = `ASTEROIDS: SECTOR ${asteroidsGame.level}`;
    }
  } else if (g === 'tempest') {
    if (typeof tempestGame !== 'undefined') {
      tempestGame.enemies = [];
      tempestGame.tube++;
      tempestGame.superzapperUsed = false;
      spawnTempestEnemies();
      playArcadeSfx('WARP');
      bannerText = `TEMPEST: TUBE ${tempestGame.tube}`;
    }
  } else if (g === 'gyruss') {
    if (typeof gyrussGame !== 'undefined') {
      gyrussGame.warp = Math.max(0, gyrussGame.warp - 1);
      gyrussGame.enemies = [];
      gyrussGame.bullets = [];
      gyrussGame.stage = (gyrussGame.stage || 1) + 1;
      for (let w = 0; w < 4; w++) {
        gyrussGame.enemies.push({
          angle: (w / 4) * Math.PI * 2,
          dist: 12 + w * 6,
          vAngle: 0.06,
          vDist: 1.1,
          type: 'drone'
        });
      }
      playArcadeSfx('GYRUSS-WARP');
      bannerText = `GYRUSS: WARP ${gyrussGame.stage} (EARTH BOUND)`;
    }
  } else if (g === 'cclimber') {
    if (typeof climberState !== 'undefined') {
      climberState.building = (climberState.building || 1) + 1;
      climberState.floor = 1;
      climberState.cleared = false;
      climberState.potY = -20;
      playArcadeSfx('CLIMB-WIN');
      bannerText = `CRAZY CLIMBER: BUILDING ${climberState.building}`;
    }
  }

  showOsdBanner(`⏩ ${bannerText}`);
  if (typeof updateMissionCard === 'function') updateMissionCard(g);
  return bannerText;
}

// Initial population of pills & mission card
if (typeof populateShelfSongPills === 'function') populateShelfSongPills();
if (typeof updateMissionCard === 'function') updateMissionCard(activeGame || 'pacman');
if (typeof renderSoundboardPads === 'function') renderSoundboardPads();
if (typeof renderLeaderboardUI === 'function') renderLeaderboardUI(activeGame || 'pacman');

// RAM Circuit-Bending Engine
function triggerCircuitBending() {
  initAudio();
  if (typeof playArcadeSfx === 'function') {
    playArcadeSfx('INV-LASER');
  }
  const statusEl = document.getElementById('engineStatus');
  if (statusEl) {
    const prev = statusEl.innerHTML;
    statusEl.innerHTML = '<span style="color:#ff0055;">⚡ RAM CIRCUIT-BENDING ACTIVE ⚡</span>';
    setTimeout(() => { if (statusEl) statusEl.innerHTML = prev; }, 600);
  }
  const flt = (typeof liveSynth !== 'undefined' && liveSynth.filter) ? liveSynth.filter : (typeof filterNode !== 'undefined' ? filterNode : null);
  if (flt && flt.frequency) {
    const cur = flt.frequency.value || 6500;
    const now = audioCtx ? audioCtx.currentTime : 0;
    if (typeof flt.frequency.setValueAtTime === 'function') flt.frequency.setValueAtTime(Math.min(18000, cur * 1.8), now);
    flt.frequency.value = Math.min(18000, cur * 1.8);
    setTimeout(() => {
      if (flt && flt.frequency) {
        if (typeof flt.frequency.setValueAtTime === 'function') flt.frequency.setValueAtTime(cur, audioCtx ? audioCtx.currentTime : 0);
        flt.frequency.value = cur;
      }
    }, 400);
  }
}

// =========================================================================
// WEBMIDI & M-VAVE HARDWARE CONTROLLER INTEGRATION
// =========================================================================
let midiAccess = null;

function handleMidiMessage(event) {
  if (!event || !event.data || event.data.length === 0) return;
  const status = event.data[0];
  const d1 = event.data[1] !== undefined ? event.data[1] : 0;
  const d2 = event.data[2] !== undefined ? event.data[2] : 0;
  const msgType = status & 0xF0;

  // Flash hardware MIDI LED indicator
  const midiLed = document.getElementById('midiLed');
  if (midiLed) {
    midiLed.classList.add('active');
    setTimeout(() => midiLed.classList.remove('active'), 120);
  }

  // Note On
  if (msgType === 0x90 && d2 > 0) {
    if (d1 >= 48 && d1 <= 74) {
      if (typeof onKeyTouch === 'function') onKeyTouch(d1 - 48, true);
    }
    if (d1 === 36 || d1 === 37) handleUnifiedAction('action', true);
    if (d1 === 38) handleUnifiedAction('left', true);
    if (d1 === 39) handleUnifiedAction('right', true);
    if (d1 === 40) handleUnifiedAction('up', true);
    if (d1 === 41) handleUnifiedAction('down', true);
    if (d1 === 42) { if (typeof start1P === 'function') start1P(); }
    if (d1 === 43) { if (typeof insertCoin === 'function') insertCoin(); }
  }
  // Note Off (or Note On with velocity 0)
  else if (msgType === 0x80 || (msgType === 0x90 && d2 === 0)) {
    if (d1 >= 48 && d1 <= 74) {
      if (typeof onKeyTouch === 'function') onKeyTouch(d1 - 48, false);
    }
    if (d1 === 36 || d1 === 37) handleUnifiedAction('action', false);
    if (d1 === 38) handleUnifiedAction('left', false);
    if (d1 === 39) handleUnifiedAction('right', false);
    if (d1 === 40) handleUnifiedAction('up', false);
    if (d1 === 41) handleUnifiedAction('down', false);
  }
  // Control Change (CC)
  else if (msgType === 0xB0) {
    // CC 74 or CC 16: LPF Cutoff (Knob 1)
    if (d1 === 74 || d1 === 16) {
      initAudio();
      const freq = 400 + (d2 / 127) * (12000 - 400);
      if (typeof filterNode !== 'undefined' && filterNode && filterNode.frequency) {
        if (typeof filterNode.frequency.setValueAtTime === 'function') filterNode.frequency.setValueAtTime(freq, audioCtx ? audioCtx.currentTime : 0);
        filterNode.frequency.value = freq;
      }
      if (typeof liveSynth !== 'undefined' && liveSynth.filter && liveSynth.filter.frequency) {
        liveSynth.filter.frequency.setValueAtTime(freq, audioCtx ? audioCtx.currentTime : 0);
      }
      const valEl = document.getElementById('valKnob1');
      if (valEl) valEl.textContent = `${(freq / 1000).toFixed(1)} kHz`;
    }
    // CC 91 or CC 17: Dub Delay (Knob 2)
    else if (d1 === 91 || d1 === 17) {
      initAudio();
      const delay = 0.05 + (d2 / 127) * (0.8 - 0.05);
      if (typeof delayNode !== 'undefined' && delayNode && delayNode.delayTime) {
        if (typeof delayNode.delayTime.setValueAtTime === 'function') delayNode.delayTime.setValueAtTime(delay, audioCtx ? audioCtx.currentTime : 0);
        delayNode.delayTime.value = delay;
      }
      if (typeof liveSynth !== 'undefined' && liveSynth.delay && liveSynth.delay.delayTime) {
        liveSynth.delay.delayTime.setValueAtTime(delay, audioCtx ? audioCtx.currentTime : 0);
      }
      const valEl = document.getElementById('valKnob2');
      if (valEl) valEl.textContent = `${Math.round(delay * 1000)} ms`;
    }
    // CC 71 or CC 18: Feedback / Reso (Knob 3)
    else if (d1 === 71 || d1 === 18) {
      initAudio();
      const fb = (d2 / 127) * 0.85;
      if (typeof feedbackNode !== 'undefined' && feedbackNode && feedbackNode.gain) {
        if (typeof feedbackNode.gain.setValueAtTime === 'function') feedbackNode.gain.setValueAtTime(fb, audioCtx ? audioCtx.currentTime : 0);
        feedbackNode.gain.value = fb;
      }
      if (typeof delaySendNode !== 'undefined' && delaySendNode && delaySendNode.gain) {
        delaySendNode.gain.value = fb > 0.01 ? Math.min(0.75, fb * 1.1) : 0.0;
      }
      if (typeof liveSynth !== 'undefined' && liveSynth.feedback && liveSynth.feedback.gain) {
        liveSynth.feedback.gain.setValueAtTime(fb, audioCtx ? audioCtx.currentTime : 0);
      }
      const valEl = document.getElementById('valKnob3');
      if (valEl) valEl.textContent = `${Math.round(fb * 100)}%`;
    }
    // CC 19: WSG Waveform (Knob 4)
    else if (d1 === 19) {
      initAudio();
      const wave = Math.min(7, Math.floor((d2 / 127) * 8));
      if (typeof wsgVoices !== 'undefined' && wsgVoices) {
        wsgVoices[0].wave = wave; wsgVoices[1].wave = wave; wsgVoices[2].wave = wave;
      }
      if (typeof liveSynth !== 'undefined') {
        liveSynth.wsgWave = wave;
        liveSynth.waveMorph = wave;
      }
      const valEl = document.getElementById('valKnob4');
      if (valEl) valEl.textContent = `WSG ${wave}`;
    }
    // CC 7: Master Volume
    else if (d1 === 7) {
      initAudio();
      masterVolLevel = Math.round((d2 / 127) * 100);
      applyMasterVolume();
    }
    // CC 1 (Modulation) or CC 14: Tempest Rotary Spinner / Gyruss Angle Continuous Encoder
    else if (d1 === 1 || d1 === 14) {
      if (activeGame === 'tempest' && typeof tempestGame !== 'undefined') {
        tempestGame.playerSeg = Math.floor((d2 / 127) * 16);
        tempestGame.segment = tempestGame.playerSeg;
      } else if (activeGame === 'gyruss' && typeof gyrussGame !== 'undefined') {
        gyrussGame.angle = (d2 / 127) * Math.PI * 2;
      }
    }
  }
  // Program Change: Select Arcade Game
  else if (msgType === 0xC0) {
    if (typeof gameList !== 'undefined') {
      const g = gameList[d1 % gameList.length];
      if (typeof switchActiveGame === 'function') switchActiveGame(g);
    }
  }
  // Pitch Bend: Circuit Bending / Detune
  else if (msgType === 0xE0) {
    const bendVal = ((d2 << 7) | d1) - 8192;
    if (Math.abs(bendVal) > 4000 && typeof triggerCircuitBending === 'function') {
      triggerCircuitBending();
    }
  }
}

function initWebMIDI() {
  if (typeof navigator !== 'undefined' && navigator.requestMIDIAccess) {
    navigator.requestMIDIAccess().then(access => {
      midiAccess = access;
      for (const input of access.inputs.values()) {
        input.onmidimessage = handleMidiMessage;
      }
      access.onstatechange = (e) => {
        if (e.port.type === 'input' && e.port.state === 'connected') {
          e.port.onmidimessage = handleMidiMessage;
        }
      };
    }).catch(err => {
      console.warn('WebMIDI not enabled or permission denied:', err);
    });
  }
}
initWebMIDI();



// =========================================================================
// SYNTH STUDIO: VECTOR CRT OSCILLOSCOPE & SOUNDCHIP CONTROLS
// =========================================================================
function renderSynthOscilloscope() {
  animTick++;
  if (!ctx) return;
  if (ctx.save) ctx.save();
  ctx.fillStyle = '#060a08';
  ctx.fillRect(0, 0, 240, 240);

  // CRT Phosphor Reticle Grid
  if (ctx.beginPath) {
    ctx.strokeStyle = 'rgba(0, 255, 102, 0.12)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let x = 20; x < 240; x += 20) { ctx.moveTo(x, 0); ctx.lineTo(x, 240); }
    for (let y = 20; y < 240; y += 20) { ctx.moveTo(0, y); ctx.lineTo(240, y); }
    ctx.stroke();

    // Center axes
    ctx.strokeStyle = 'rgba(0, 255, 102, 0.28)';
    ctx.beginPath();
    ctx.moveTo(120, 0); ctx.lineTo(120, 240);
    ctx.moveTo(0, 120); ctx.lineTo(240, 120);
    ctx.stroke();
  }

  // Header info
  if (ctx.fillText) {
    ctx.fillStyle = '#aae4c8';
    ctx.font = 'bold 11px monospace';
    ctx.fillText('SYNTH STUDIO · 60Hz', 12, 20);

    const engName = (liveSynth && liveSynth.engineNames) ? (liveSynth.engineNames[liveSynth.currentEngine] || 'WSG') : 'WSG';
    ctx.fillStyle = '#00ff66';
    ctx.font = 'bold 9px monospace';
    ctx.fillText('[' + (liveSynth ? liveSynth.currentEngine.toUpperCase() : 'WSG') + '] ' + engName.slice(0, 20), 12, 34);

    ctx.fillStyle = '#8fa59b';
    ctx.font = '8px monospace';
    const envStr = liveSynth ? liveSynth.envelope.toUpperCase() : 'LEAD';
    const octStr = (liveSynth && liveSynth.octaveOffset >= 0 ? '+' : '') + (liveSynth ? liveSynth.octaveOffset : 0);
    const lfoStr = (liveSynth && liveSynth.lfo && liveSynth.lfo.active) ? 'ON' : 'OFF';
    const arpStr = (liveSynth && liveSynth.arp && liveSynth.arp.active) ? 'ON' : 'OFF';
    ctx.fillText('ENV: ' + envStr + ' · OCT: ' + octStr + ' · LFO: ' + lfoStr + ' · ARP: ' + arpStr, 12, 47);
  }

  // Waveform rendering
  const isVoiceActive = (liveSynth && ((liveSynth.activeVoices && liveSynth.activeVoices.size > 0) || (liveSynth.arp && liveSynth.arp.active && liveSynth.arp.heldKeys.length > 0)));
  if (ctx.beginPath) {
    ctx.strokeStyle = isVoiceActive ? '#00ffaa' : 'rgba(0, 229, 255, 0.6)';
    ctx.shadowColor = isVoiceActive ? '#00ffaa' : '#00e5ff';
    ctx.shadowBlur = isVoiceActive ? 8 : 4;
    ctx.lineWidth = 2;
    ctx.beginPath();

    const numSamples = 216;
    const t = animTick * 0.08;
    const eng = liveSynth ? liveSynth.currentEngine : 'wsg';

    for (let i = 0; i < numSamples; i++) {
      const x = 12 + i;
      let y = 125;
      const progress = i / numSamples;

      if (!isVoiceActive) {
        y += Math.sin(progress * Math.PI * 4 + t) * 6 + Math.sin(progress * Math.PI * 12 + t * 2) * 2;
      } else {
        if (eng === 'wsg') {
          const step = Math.floor((i + animTick * 3) / 6) % 32;
          const waveVal = (typeof WSG_WAVETABLES !== 'undefined' && WSG_WAVETABLES[0]) ? (WSG_WAVETABLES[0][step] - 7.5) : Math.sin(i * 0.2) * 7;
          y += waveVal * 5.2;
        } else if (eng === 'ay8910') {
          const cycle = ((i * 4 + animTick * 8) % 64) < 32 ? 1 : -1;
          y += cycle * 38;
        } else if (eng === 'pokey') {
          const p1 = ((i * 5 + animTick * 6) % 48) < 24 ? 1 : -1;
          const p2 = ((i * 7 + animTick * 4) % 32) < 16 ? 0.7 : -0.7;
          y += (p1 + p2) * 24;
        } else if (eng === 'dac') {
          const raw = Math.sin(progress * Math.PI * 8 + t * 4);
          const quantized = Math.round(raw * 7) / 7;
          y += quantized * 40;
        } else {
          const mod = Math.sin(progress * Math.PI * 16 + t * 6);
          const carrier = Math.sin(progress * Math.PI * 6 + t * 3 + mod * 2.2);
          y += carrier * 42;
        }
      }

      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.shadowBlur = 0;
  }

  // Active Voices Indicators
  if (ctx.fillText && liveSynth) {
    ctx.fillStyle = '#667777';
    ctx.font = '8px monospace';
    ctx.fillText('VOICES: ', 12, 204);
    const voiceEntries = liveSynth.activeVoices ? Array.from(liveSynth.activeVoices.keys()) : [];
    for (let v = 0; v < 8; v++) {
      const vx = 56 + v * 20;
      const active = v < voiceEntries.length || (liveSynth.arp && liveSynth.arp.active && v < liveSynth.arp.heldKeys.length);
      ctx.fillStyle = active ? '#00ff66' : '#182420';
      ctx.fillRect(vx, 196, 14, 10);
      ctx.strokeStyle = '#324a40';
      if (ctx.strokeRect) ctx.strokeRect(vx, 196, 14, 10);
      if (active) {
        const k = voiceEntries[v] !== undefined ? voiceEntries[v] : (liveSynth.arp ? (liveSynth.arp.heldKeys[v] || 0) : 0);
        ctx.fillStyle = '#000';
        ctx.font = 'bold 7px monospace';
        ctx.fillText(noteNames[k % 12], vx + 2, 204);
      }
    }

    ctx.fillStyle = '#8fa5a0';
    ctx.font = '8px monospace';
    ctx.fillText('PLAY NOTES: SILICONE KEYS 1-27 OR QWERTY', 12, 226);
  }

  if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
  if (ctx.restore) ctx.restore();
}

function setSynthEngine(engineId) {
  initAudio();
  if (!liveSynth) return;
  if (liveSynth.engineOrder.includes(engineId)) {
    liveSynth.currentEngine = engineId;
    const name = liveSynth.engineNames[liveSynth.currentEngine];
    const status = document.getElementById('engineStatus');
    if (status) status.innerHTML = `SYNTH ENGINE: <b>${name}</b>`;
    const hud = document.getElementById('hudStatus');
    if (hud) hud.textContent = `● SYNTH: ${liveSynth.currentEngine.toUpperCase()}`;
    updateSynthUI();
    playStartupChimeMini();
    return name;
  }
}

function setEnvelope(envId) {
  initAudio();
  if (!liveSynth) return;
  liveSynth.envelope = envId;
  const status = document.getElementById('engineStatus');
  if (status) status.innerHTML = `ENVELOPE: <b>${liveSynth.envelope.toUpperCase()}</b>`;
  updateSynthUI();
}

function setSynthOctave(oct) {
  initAudio();
  if (!liveSynth) return;
  liveSynth.octaveOffset = Math.max(-2, Math.min(2, oct));
  const status = document.getElementById('engineStatus');
  if (status) status.innerHTML = `SYNTH OCTAVE: <b>${liveSynth.octaveOffset >= 0 ? '+' : ''}${liveSynth.octaveOffset}</b>`;
  updateSynthUI();
}

function updateSynthUI() {
  if (!liveSynth) return;
  document.querySelectorAll('.synth-chip-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.engine === liveSynth.currentEngine);
  });
  document.querySelectorAll('.synth-env-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.env === liveSynth.envelope);
  });
  document.querySelectorAll('.synth-oct-btn').forEach(btn => {
    btn.classList.toggle('active', parseInt(btn.dataset.oct) === liveSynth.octaveOffset);
  });
  const arpBtn = document.getElementById('synthBtnArp');
  if (arpBtn && liveSynth.arp) {
    arpBtn.classList.toggle('active', liveSynth.arp.active);
    arpBtn.textContent = liveSynth.arp.active ? 'ARP: ON (16th)' : 'ARP: OFF';
  }
  const lfoBtn = document.getElementById('synthBtnLfo');
  if (lfoBtn && liveSynth.lfo) {
    lfoBtn.classList.toggle('active', liveSynth.lfo.active);
    lfoBtn.textContent = liveSynth.lfo.active ? 'LFO: ON (6Hz)' : 'LFO: OFF';
  }
}

// Ensure all 8 Tracker Patterns (01..08) exist in trackerEngine.patterns
if (typeof trackerEngine !== 'undefined' && trackerEngine.patterns && trackerEngine.patterns.length === 4) {
  trackerEngine.patterns.push(
    {
      name: 'DK 25M SWING',
      chipType: 'DAC + WSG + PSG',
      bpm: 136,
      steps: [
        [[36, 15], [60, 14], [72, 11], 'KCK'],
        [[ 0,  0], [ 0,  0], [64, 10], 'HAT'],
        [[39, 14], [63, 13], [67, 11], 'HAT'],
        [[40, 14], [64, 14], [72, 11], 'SNR'],
        [[41, 15], [65, 14], [77, 11], 'KCK'],
        [[ 0,  0], [ 0,  0], [69, 10], 'HAT'],
        [[43, 15], [67, 15], [71, 12], 'SNR'],
        [[ 0,  0], [74, 13], [79, 11], 'HAT'],
        [[36, 15], [60, 14], [72, 11], 'KCK'],
        [[38, 14], [62, 13], [74, 11], 'HAT'],
        [[40, 14], [64, 14], [76, 11], 'KCK'],
        [[41, 14], [65, 14], [77, 11], 'SNR'],
        [[43, 15], [67, 15], [79, 12], 'KCK'],
        [[41, 14], [65, 13], [77, 11], 'HAT'],
        [[40, 14], [64, 14], [76, 11], 'SNR'],
        [[38, 14], [62, 13], [74, 11], 'TOM']
      ]
    },
    {
      name: 'GALAGA SECTOR',
      chipType: 'NAMCO 3-VOICE WSG',
      bpm: 140,
      steps: [
        [[38, 15], [62, 14], [74, 11], 'KCK'],
        [[38, 13], [66, 13], [78, 11], 'HAT'],
        [[45, 14], [69, 14], [81, 12], 'HAT'],
        [[38, 13], [74, 15], [86, 12], 'SNR'],
        [[43, 15], [67, 14], [79, 11], 'KCK'],
        [[43, 13], [71, 13], [83, 11], 'HAT'],
        [[50, 14], [74, 14], [86, 12], 'SNR'],
        [[45, 14], [73, 14], [85, 12], 'HAT'],
        [[38, 15], [62, 14], [74, 11], 'KCK'],
        [[40, 14], [64, 13], [76, 11], 'HAT'],
        [[42, 14], [66, 14], [78, 11], 'KCK'],
        [[43, 15], [67, 14], [79, 12], 'SNR'],
        [[45, 15], [69, 15], [81, 12], 'KCK'],
        [[43, 14], [67, 13], [79, 11], 'HAT'],
        [[42, 14], [66, 14], [78, 11], 'SNR'],
        [[40, 14], [64, 13], [76, 11], 'TOM']
      ]
    },
    {
      name: 'TEMPEST SURGE',
      chipType: 'DUAL ATARI POKEY',
      bpm: 148,
      steps: [
        [[33, 15], [57, 14], [69, 12], 'KCK'],
        [[33, 14], [60, 13], [72, 11], 'HAT'],
        [[33, 14], [64, 14], [76, 12], 'KCK'],
        [[45, 15], [69, 15], [81, 12], 'SNR'],
        [[36, 15], [60, 14], [72, 12], 'KCK'],
        [[36, 14], [64, 13], [76, 11], 'HAT'],
        [[36, 14], [67, 14], [79, 12], 'SNR'],
        [[48, 15], [72, 15], [84, 12], 'HAT'],
        [[38, 15], [62, 14], [74, 12], 'KCK'],
        [[38, 14], [65, 13], [77, 11], 'HAT'],
        [[38, 14], [69, 14], [81, 12], 'KCK'],
        [[50, 15], [74, 15], [86, 12], 'SNR'],
        [[40, 15], [64, 15], [76, 12], 'KCK'],
        [[39, 14], [63, 14], [75, 12], 'SNR'],
        [[38, 14], [62, 14], [74, 12], 'TOM'],
        [[36, 14], [60, 14], [72, 12], 'SNR']
      ]
    },
    {
      name: 'TOCCATA D MIN',
      chipType: '5x AY-3-8910 PSG',
      bpm: 134,
      steps: [
        [[38, 15], [74, 15], [86, 13], 'KCK'],
        [[38, 14], [72, 14], [84, 12], 'HAT'],
        [[38, 15], [74, 15], [86, 13], 'SNR'],
        [[ 0,  0], [69, 13], [81, 11], 'HAT'],
        [[38, 14], [70, 14], [82, 12], 'KCK'],
        [[38, 13], [67, 13], [79, 11], 'HAT'],
        [[38, 14], [69, 14], [81, 12], 'SNR'],
        [[ 0,  0], [64, 13], [76, 11], 'HAT'],
        [[38, 15], [65, 14], [77, 12], 'KCK'],
        [[37, 14], [61, 14], [73, 12], 'HAT'],
        [[38, 15], [62, 15], [74, 13], 'KCK'],
        [[40, 14], [64, 14], [76, 12], 'SNR'],
        [[41, 15], [65, 14], [77, 12], 'KCK'],
        [[43, 14], [67, 14], [79, 12], 'HAT'],
        [[45, 15], [69, 15], [81, 13], 'SNR'],
        [[37, 15], [73, 15], [85, 13], 'TOM']
      ]
    }
  );
}

function selectTrackerPattern(idx) {
  initAudio();
  if (!trackerEngine || !trackerEngine.patterns) return;
  trackerEngine.currentPatternIdx = (idx + trackerEngine.patterns.length) % trackerEngine.patterns.length;
  const pat = trackerEngine.patterns[trackerEngine.currentPatternIdx];
  if (pat) {
    trackerEngine.bpm = pat.bpm;
    const status = document.getElementById('engineStatus');
    if (status) status.innerHTML = `TRACKER: <b>${pat.name}</b> (${pat.bpm} BPM)`;
  }
  trackerEngine.step = 0;
  updateTrackerUI();
}

function stepTrackerStep() {
  initAudio();
  if (!trackerEngine || !trackerEngine.patterns) return;
  const pat = trackerEngine.patterns[trackerEngine.currentPatternIdx];
  if (!pat) return;
  const stepMs = (60000 / (trackerEngine.bpm || pat.bpm || 132)) / 4;
  const now = audioCtx ? audioCtx.currentTime : 0;
  const stepData = pat.steps[trackerEngine.step];
  if (stepData) {
    if (stepData[0] && stepData[0][0] > 0) {
      playTrackerVoice('wsg', stepData[0][0], stepData[0][1], stepMs / 1000, now);
      trackerEngine.vuLevels[0] = stepData[0][1] / 15.0;
    }
    if (stepData[1] && stepData[1][0] > 0) {
      playTrackerVoice('ay8910', stepData[1][0], stepData[1][1], stepMs / 1000, now);
      trackerEngine.vuLevels[1] = stepData[1][1] / 15.0;
    }
    if (stepData[2] && stepData[2][0] > 0) {
      playTrackerVoice('pokey', stepData[2][0], stepData[2][1], stepMs / 1000, now);
      trackerEngine.vuLevels[2] = stepData[2][1] / 15.0;
    }
    if (stepData[3] && stepData[3] !== '---') {
      playArcadeDrum(stepData[3], 15, now);
      trackerEngine.vuLevels[3] = 1.0;
    }
  }
  trackerEngine.step = (trackerEngine.step + 1) % 16;
  updateTrackerUI();
}

function updateTrackerUI() {
  if (!trackerEngine || !trackerEngine.patterns) return;
  const pat = trackerEngine.patterns[trackerEngine.currentPatternIdx];
  const tag = document.getElementById('trackerStatusTag');
  if (tag) tag.textContent = trackerEngine.playing ? `PLAYING (${pat ? pat.bpm : 132} BPM)` : 'LOOP: STOPPED';
  const btn = document.getElementById('btnTrackerPlay');
  if (btn) btn.textContent = trackerEngine.playing ? '⏸ PAUSE LOOP' : '▶ PLAY LOOP';
  const disp = document.getElementById('trackerStepDisplay');
  if (disp) disp.innerHTML = `STEP: <b>${String(trackerEngine.step + 1).padStart(2, '0')}/16</b> · BPM: <b>${pat ? pat.bpm : 132}</b>`;
  document.querySelectorAll('#trackerPatternList .synth-chip-btn').forEach(b => {
    b.classList.toggle('active', parseInt(b.dataset.pat) === trackerEngine.currentPatternIdx);
  });
}

// Wrap toggleTracker and cycleTrackerPattern so they always sync updateTrackerUI
if (typeof toggleTracker === 'function') {
  const _origToggleTracker = toggleTracker;
  toggleTracker = function() {
    initAudio();
    _origToggleTracker();
    updateTrackerUI();
  };
}
if (typeof cycleTrackerPattern === 'function') {
  const _origCycleTrackerPattern = cycleTrackerPattern;
  cycleTrackerPattern = function() {
    initAudio();
    _origCycleTrackerPattern();
    updateTrackerUI();
  };
}

// Additional Authentic M-VAVE FM-1 Panel Button & Encoder Handlers
const btnFx = document.getElementById('btnFxScanlines');
if (btnFx) btnFx.onclick = toggleScanlines;

const btnGlo = document.getElementById('btnGloTour');
if (btnGlo) btnGlo.onclick = toggleTourDemo;

const btnSeqJ = document.getElementById('btnSeqJuke');
if (btnSeqJ) btnSeqJ.onclick = () => {
  if (currentMode === 'tracker') toggleTracker();
  else if (currentMode === 'demo') { if (demoPlayer.playing) pauseDemoSong(); else playDemoSong(); }
  else setMode('tracker');
};


// Function Buttons: SCL (Engine), ENV (Envelope), LFO (Vibrato), ARP (Arpeggiator)
const btnScl = document.getElementById('btnScl');
if (btnScl) btnScl.onclick = () => {
  if (currentMode === 'tracker') cycleTrackerPattern();
  else cycleSynthEngine();
};

const btnEnv = document.getElementById('btnEnv');
if (btnEnv) btnEnv.onclick = () => cycleEnvelope();

const btnLfo = document.getElementById('btnLfo');
if (btnLfo) btnLfo.onclick = () => toggleLfo();

const btnArp = document.getElementById('btnArp');
if (btnArp) btnArp.onclick = () => toggleArp();

// Octave Shifters in Synth / Tracker modes
const btnOctM = document.getElementById('btnOctMinus');
if (btnOctM) btnOctM.onclick = () => {
  initAudio();
  if (activeGame === 'cclimber' && currentMode === 'arcade') climberStep('left', 'down');
  else {
    setSynthOctave((liveSynth ? liveSynth.octaveOffset : 0) - 1);
  }
};

const btnOctP = document.getElementById('btnOctPlus');
if (btnOctP) btnOctP.onclick = () => {
  initAudio();
  if (activeGame === 'cclimber' && currentMode === 'arcade') climberStep('right', 'up');
  else {
    setSynthOctave((liveSynth ? liveSynth.octaveOffset : 0) + 1);
  }
};

// Screen Quadrant Click Steering for screen bezel border
const screenBez = document.getElementById('screenBezel');
if (screenBez && typeof screenBez.addEventListener === 'function') {
  screenBez.addEventListener('click', (e) => {
    if (e.target !== screenBez) return;
    if (currentMode !== 'arcade' && currentMode !== 'tour') return;
    const rect = screenBez.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    let act = 'up';
    if (Math.abs(x) > Math.abs(y)) act = (x > 0) ? 'right' : 'left';
    else act = (y > 0) ? 'down' : 'up';
    handleUnifiedAction(act, true);
    safeTimeout(() => handleUnifiedAction(act, false), 120);
  });
}

// Helper to bind vertical mouse/touch drag on the 4 top rotary encoders
function bindEncoderDrag(encEl, onStepDelta) {
  if (!encEl) return;
  let dragStartY = null;
  let accumDy = 0;
  encEl.onmousedown = (e) => {
    initAudio();
    dragStartY = e.clientY;
    accumDy = 0;
    const moveHandler = (me) => {
      if (dragStartY === null) return;
      const dy = dragStartY - me.clientY;
      const diff = dy - accumDy;
      if (Math.abs(diff) >= 14) {
        const steps = Math.trunc(diff / 14);
        accumDy += steps * 14;
        onStepDelta(steps);
      }
    };
    const upHandler = () => {
      dragStartY = null;
      window.removeEventListener('mousemove', moveHandler);
      window.removeEventListener('mouseup', upHandler);
    };
    window.addEventListener('mousemove', moveHandler);
    window.addEventListener('mouseup', upHandler);
  };
}

// Master Volume & Quick Controls (Wired directly to Web Audio masterGain!)
let masterVolLevel = 70;
const encMaster = document.getElementById('encMaster');
function applyMasterVolume() {
  if (typeof masterGain !== 'undefined' && masterGain && masterGain.gain) {
    const gainVal = (masterVolLevel / 100) * 0.95;
    if (typeof masterGain.gain.setValueAtTime === 'function' && audioCtx) {
      masterGain.gain.setValueAtTime(gainVal, audioCtx.currentTime);
    }
    masterGain.gain.value = gainVal;
  }
  if (encMaster && encMaster.style && encMaster.style.setProperty) {
    encMaster.style.setProperty('--angle', `${(masterVolLevel / 100 * 270) - 135}deg`);
  }
}
function updateMasterVol(delta) {
  initAudio();
  masterVolLevel = Math.max(0, Math.min(100, masterVolLevel + delta));
  applyMasterVolume();
}
if (encMaster && encMaster.addEventListener) {
  encMaster.addEventListener('wheel', (e) => { e.preventDefault(); updateMasterVol(e.deltaY < 0 ? 5 : -5); }, { passive: false });
}
bindEncoderDrag(encMaster, (steps) => updateMasterVol(steps * 5));
const btnVolDown = document.getElementById('btnVolDown');
if (btnVolDown) btnVolDown.onclick = () => updateMasterVol(-5);
const btnVolUp = document.getElementById('btnVolUp');
if (btnVolUp) btnVolUp.onclick = () => updateMasterVol(5);

// Select Game Encoder
const btnPrevGame = document.getElementById('btnPrevGame');
const btnNextGame = document.getElementById('btnNextGame');
const encSelect = document.getElementById('encSelect');
let currentGameIdx = 0;
const gameList = ['pacman', 'cclimber', 'galaga', 'dkong', 'frogger', 'asteroids', 'tempest', 'gyruss'];
function stepGame(dir) {
  stopCurrentGame();

  currentGameIdx = (currentGameIdx + dir + gameList.length) % gameList.length;
  if (encSelect && encSelect.style && encSelect.style.setProperty) {
    encSelect.style.setProperty('--angle', `${(currentGameIdx / gameList.length * 270) - 135}deg`);
  }
  const g = gameList[currentGameIdx];
  clearScreen(g.toUpperCase());
  if (currentMode === 'tour') {
    tourState.gameIdx = currentGameIdx;
    tourState.frameInGame = 0;
    renderTourDemo();
  } else {
    switchActiveGame(g);
  }
}
if (btnPrevGame) btnPrevGame.onclick = () => stepGame(-1);
if (btnNextGame) btnNextGame.onclick = () => stepGame(1);
if (encSelect && encSelect.addEventListener) encSelect.addEventListener('wheel', (e) => { e.preventDefault(); stepGame(e.deltaY < 0 ? 1 : -1); }, { passive: false });
bindEncoderDrag(encSelect, (steps) => stepGame(steps > 0 ? 1 : -1));

// Presets Encoder (Demo Songs)
let currentDemoIdx = 0;
const btnPrevSong = document.getElementById('btnPrevSong');
const btnNextSong = document.getElementById('btnNextSong');
const encPresets = document.getElementById('encPresets');
function stepSong(dir) {
  initAudio();
  if (currentMode !== 'demo') setMode('demo');
  currentDemoIdx = ((currentDemoIdx + dir) % DEMO_SONGS.length + DEMO_SONGS.length) % DEMO_SONGS.length;
  if (encPresets && encPresets.style && encPresets.style.setProperty) encPresets.style.setProperty('--angle', `${(currentDemoIdx / DEMO_SONGS.length * 270) - 135}deg`);
  selectDemoSong(currentDemoIdx);
  if (!demoPlayer.playing) playDemoSong();
}
if (btnPrevSong) btnPrevSong.onclick = () => stepSong(-1);
if (btnNextSong) btnNextSong.onclick = () => stepSong(1);
if (encPresets && encPresets.addEventListener) encPresets.addEventListener('wheel', (e) => { e.preventDefault(); stepSong(e.deltaY < 0 ? 1 : -1); }, { passive: false });
bindEncoderDrag(encPresets, (steps) => stepSong(steps > 0 ? 1 : -1));

// Algorithm Encoder (Modes)
const btnPrevMode = document.getElementById('btnPrevMode');
const btnNextMode = document.getElementById('btnNextMode');
const encAlgorithm = document.getElementById('encAlgorithm');
function stepMode(dir) {
  const idx = (MODES.indexOf(currentMode) + dir + MODES.length) % MODES.length;
  setMode(MODES[idx]);
  if (encAlgorithm && encAlgorithm.style && encAlgorithm.style.setProperty) encAlgorithm.style.setProperty('--angle', `${(idx / MODES.length * 270) - 135}deg`);
}
if (btnPrevMode) btnPrevMode.onclick = () => stepMode(-1);
if (btnNextMode) btnNextMode.onclick = () => stepMode(1);
if (encAlgorithm && encAlgorithm.addEventListener) encAlgorithm.addEventListener('wheel', (e) => { e.preventDefault(); stepMode(e.deltaY < 0 ? 1 : -1); }, { passive: false });
bindEncoderDrag(encAlgorithm, (steps) => stepMode(steps > 0 ? 1 : -1));

// URL Query Parameter overrides for instant testing & game launch
if (typeof window !== 'undefined' && window.location && window.location.search) {
  try {
    const params = new URLSearchParams(window.location.search);
    if (params.get('nosplash') === '1') {
      splashState.active = false;
    }
    if (params.get('album') === '1' || params.get('splash') === 'album') {
      triggerAlbumSplashScreen();
    }
    if (params.get('splash') === 'arcade') {
      triggerSplashScreen();
    }
    if (params.get('splashframe')) {
      splashState.frame = parseInt(params.get('splashframe'));
    }
    if (params.get('god') === '1' || params.get('immortal') === '1') {
      if (typeof toggleImmortalMode === 'function') toggleImmortalMode(true);
    }
    if (params.get('game')) {
      switchActiveGame(params.get('game'));
      if (params.get('game') === 'pacman') { ensurePastBoot(); renderArcadeFrame(); }
    }
    if (params.get('tour')) {
      const tourGame = params.get('tour');
      const idx = tourState.games.findIndex(g => g.id === tourGame);
      if (idx !== -1) {
        setMode('tour');
        tourState.gameIdx = idx;
      }
    }
    if (params.get('mode')) {
      setMode(params.get('mode'));
    }
    if (params.get('shelf') || params.get('tab')) {
      const targetTab = params.get('shelf') || params.get('tab');
      if (typeof setStudioTab === 'function') setStudioTab(targetTab);
    }
    if (params.get('bank') || params.get('sfxbank')) {
      const b = parseInt(params.get('bank') || params.get('sfxbank'));
      if (!isNaN(b) && typeof switchSfxBank === 'function') {
        switchSfxBank(b >= 1 ? b - 1 : b);
      }
    }
  } catch (e) {}
}
"""

    last_script_close = script_body.rfind("</script>")
    if last_script_close != -1:
        script_body = script_body[:last_script_close] + additional_bindings + "\n" + script_body[last_script_close:]
    else:
        script_body += additional_bindings + "\n</script>"

    full_output = new_html + script_body

    with open("tools/simulator_template.html", "w", encoding="utf-8", errors="replace") as f_out:
        f_out.write(full_output)

    print(f"Successfully wrote tools/simulator_template.html ({len(full_output)} bytes)!")

if __name__ == "__main__":
    main()
