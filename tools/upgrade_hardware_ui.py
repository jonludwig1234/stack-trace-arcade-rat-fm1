import re

# Read current simulator_template.html
with open("tools/simulator_template.html", "r") as f:
    orig = f.read()

# 1. New CSS & HTML replacement up to <script>
new_head_and_body = """<!DOCTYPE html>
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

  /* Cockpit Top Header */
  .title-bar {
    width: 100%;
    max-width: 960px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
    padding: 0 4px;
    flex-wrap: wrap;
    gap: 12px;
  }
  .branding-wrap { display: flex; align-items: center; gap: 14px; }
  .header-avatar {
    width: 58px;
    height: 58px;
    border-radius: 50%;
    border: 2px solid var(--accent);
    box-shadow: 0 0 16px var(--accent-glow), inset 0 0 8px rgba(170,228,200,0.3);
    object-fit: cover;
    background: #000;
    transition: transform 0.25s ease;
  }
  .header-avatar:hover { transform: scale(1.05) rotate(2deg); }

  .brand-sub { font-size: 0.68rem; font-weight: 800; color: var(--accent); letter-spacing: 2px; text-transform: uppercase; font-family: var(--font-mono); }
  h1 {
    font-size: 1.45rem;
    font-weight: 900;
    color: #edf5f0;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    margin: 2px 0;
    display: flex;
    align-items: center;
    gap: 9px;
  }
  .version-tag {
    font-size: 0.65rem;
    color: #172e24;
    background: var(--accent);
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 800;
    letter-spacing: 1px;
    box-shadow: 0 0 8px var(--accent-glow);
  }
  .subtitle { font-size: 0.70rem; color: #8fa59b; }

  .header-actions { display: flex; gap: 9px; align-items: center; flex-wrap: wrap; }
  .splash-trigger-btn {
    background: #203a31;
    border: 1px solid #4d7667;
    color: #c6eddb;
    padding: 7px 13px;
    font-size: 0.70rem;
    font-weight: 800;
    border-radius: 7px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s ease;
  }
  .splash-trigger-btn:hover { background: var(--accent); color: #172e24; border-color: var(--accent); box-shadow: 0 0 14px var(--accent-glow); }

  .config-btn {
    background: #242c2f;
    border: 1px solid #425257;
    color: #e2ece6;
    padding: 7px 14px;
    border-radius: 7px;
    font-size: 0.70rem;
    font-weight: 800;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s ease;
  }
  .config-btn:hover { background: #37464a; border-color: #6a8288; color: #fff; }

  /* Quick Navigation / Modes Strip */
  .nav-strip {
    width: 100%;
    max-width: 960px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
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
    image-rendering: pixelated;
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
</style>
</head>
<body>

<!-- Cockpit Header Bar -->
<div class="title-bar">
  <div class="branding-wrap">
    <img src="images/stack_trace_avatar.png" id="headerAvatar" alt="Stack Trace Avatar" onerror="this.src='data:image/png;base64,__STACK_TRACE_AVATAR_B64__'" class="header-avatar">
    <div>
      <div class="brand-sub">STACK TRACE PRESENTS</div>
      <h1>ARCADE RAT <span class="version-tag">v 1.0</span></h1>
      <div class="subtitle">Bare-Metal Z80 Arcade · 15-Track Gyruss Symphony · 27-SFX Engine · Tape Dub Rack</div>
    </div>
  </div>
  <div class="header-actions">
    <button class="splash-trigger-btn" id="btnReplaySplash" onclick="triggerSplashScreen()">⚡ SPLASH SCREEN</button>
    <a href="configurator.html" class="config-btn">⚙️ OPEN CONFIGURATOR (93 GAMES)</a>
  </div>
</div>

<!-- Quick Navigation / Game Switcher Strip -->
<div class="nav-strip">
  <div class="game-toggle-group">
    <button class="game-btn active" id="btnGamePacman" onclick="switchActiveGame('pacman')">🟡 PAC-MAN</button>
    <button class="game-btn" id="btnGameClimber" onclick="switchActiveGame('cclimber')">🧗 CRAZY CLIMBER</button>
    <button class="game-btn tour-btn" id="btnGameTour" onclick="toggleTourDemo()">🎡 TOUR ALL ROMS</button>
  </div>

  <!-- Mode Indicator Pills -->
  <div class="mode-indicator">
    <div class="mode-tag active" data-mode="arcade">ARCADE</div>
    <div class="mode-tag" data-mode="tour">TOUR DEMO</div>
    <div class="mode-tag" data-mode="demo">DEMO SONGS</div>
    <div class="mode-tag" data-mode="soundboard">SFX PADS (27)</div>
    <div class="mode-tag" data-mode="tracker">TRACKER</div>
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
    <span id="crtStatus" style="cursor:pointer;" title="Click or Press K to toggle scanlines">SCANLINES: ON</span>
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
    <span>FEEDBACK<small id="valKnob3">40%</small></span>
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
    <div style="font-size:0.62rem; color:#8fa5a0;">ACTIONS: <b>1/C</b>=COIN, <b>5/ENTER</b>=START, <b>SPACE</b>=QUICK PLAY, <b>R</b>=REWIND</div>
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

# 2. Update JavaScript in script_body
script_body_content = orig[script_idx:]

# Update the piano keyboard generation logic to use the official M-VAVE positions and styling
old_piano_code_pattern = r"// 27 Silicone Keys\s+const pianoContainer = document\.getElementById\('pianoKeys'\);[\s\S]*?function updateKeyLabels\(\) {"
new_piano_code = """// 27 Silicone Keys (Authentic M-VAVE FM-1 Geometry & Styling)
const pianoContainer = document.getElementById('pianoKeys');
const noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
const whites = [0, 2, 4, 6, 7, 9, 11, 12, 14, 16, 18, 19, 21, 23, 24, 26];
const edits = [1, 3, 5, 8, 10, 13, 15, 17, 20, 22, 25];
const fmOps = ['OP1', 'OP2', 'OP3', 'OP4', 'OP5', 'OP6', 'PITCH', 'GLOBAL', 'MONO', 'POLY', 'ARP'];

function getSfxCategoryColor(idx) {
  if (idx < 7) return '#f5a623'; // Pac-Man Gold
  if (idx < 12) return '#00e5ff'; // Galaga Cyan
  if (idx < 16) return '#ff9f1c'; // Donkey Kong Amber
  if (idx < 20) return '#ff4757'; // Mario Red
  if (idx < 23) return '#2ecc71'; // Asteroids Emerald
  return '#a55eea';               // Tempest / Konami Violet
}

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
}

function updateKeyLabels() {"

script_body_content = re.sub(old_piano_code_pattern, new_piano_code, script_body_content, count=1)

# Update updateKeyLabels implementation
old_update_labels_pattern = r"function updateKeyLabels\(\) \{[\s\S]*?\}\n\nfunction onKeyTouch"
new_update_labels = """function updateKeyLabels() {
  document.querySelectorAll('.piano-key').forEach(el => {
    const k = parseInt(el.dataset.key);
    const whiteIdx = whites.indexOf(k);
    const editIdx = edits.indexOf(k);
    const note = noteNames[k % 12];
    const catColor = getSfxCategoryColor(k);
    if (currentMode === 'soundboard') {
      el.innerHTML = '<i></i><span style="font-size:0.55cqw;color:' + catColor + ';font-weight:900;">' + sfxNames[k] + '</span>';
    } else {
      if (whiteIdx >= 0) {
        el.innerHTML = '<i></i><span>' + String(whiteIdx + 1).padStart(2, '0') + '<br>' + note + '</span>';
      } else {
        el.innerHTML = '<i></i><span>' + (fmOps[editIdx] || '') + '<br>' + note + '</span>';
      }
    }
  });
}

function onKeyTouch"""

script_body_content = re.sub(old_update_labels_pattern, new_update_labels, script_body_content, count=1)

# Update onKeyTouch to also toggle .lit and .held
old_ontouch_pattern = r"if \(el\) el\.classList\.toggle\('active', isDown\);"
new_ontouch = """if (el) {
    el.classList.toggle('active', isDown);
    el.classList.toggle('lit', isDown);
    el.classList.toggle('held', isDown);
  }"""
script_body_content = re.sub(old_ontouch_pattern, new_ontouch, script_body_content, count=1)

# Update setupKnob to support the M-VAVE encoder needle and stepper buttons
old_setupknob_pattern = r"function setupKnob\(id, min, max, initial, format, onChange\) \{[\s\S]*?updateVisual\(\);\n\}"
new_setupknob = """function setupKnob(id, min, max, initial, format, onChange) {
  const dial = document.getElementById(id);
  if (!dial) return;
  const needle = dial.querySelector('i');
  let val = initial;
  let startY = 0, startVal = 0;

  function updateVisual() {
    const pct = Math.max(0, Math.min(1, (val - min) / (max - min)));
    const angle = (pct * 270) - 135;
    dial.style.setProperty('--angle', `${angle}deg`);
    if (needle) needle.style.transform = `rotate(${angle}deg)`;
    onChange(val);
  }

  dial.onmousedown = (e) => {
    initAudio();
    startY = e.clientY;
    startVal = val;
    window.onmousemove = (me) => {
      const dy = startY - me.clientY;
      const delta = (dy / 120) * (max - min);
      val = Math.max(min, Math.min(max, startVal + delta));
      updateVisual();
    };
    window.onmouseup = () => { window.onmousemove = null; window.onmouseup = null; };
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

script_body_content = re.sub(old_setupknob_pattern, new_setupknob, script_body_content, count=1)

# Add bindings for the new hardware controls (MASTER, SELECT, PRESETS, ALGORITHM, OCT -, OCT +, FX, GLO, etc.)
additional_hardware_bindings = """
// Additional Authentic M-VAVE FM-1 Panel Button & Encoder Handlers
const btnFx = document.getElementById('btnFxScanlines');
if (btnFx) btnFx.onclick = toggleCrt;

const btnGlo = document.getElementById('btnGloTour');
if (btnGlo) btnGlo.onclick = toggleTourDemo;

const btnSeqJ = document.getElementById('btnSeqJuke');
if (btnSeqJ) btnSeqJ.onclick = () => {
  if (demoPlayer.playing) pauseDemoSong(); else playDemoSong();
};

const btnOctM = document.getElementById('btnOctMinus');
if (btnOctM) btnOctM.onclick = () => {
  initAudio();
  if (activeGame === 'cclimber') climberStep('left', 'down');
  else playArcadeSfx('DK-WALK');
};

const btnOctP = document.getElementById('btnOctPlus');
if (btnOctP) btnOctP.onclick = () => {
  initAudio();
  if (activeGame === 'cclimber') climberStep('right', 'up');
  else playArcadeSfx('DK-JUMP');
};

// Master Volume & Quick Controls
let masterVolLevel = 70;
const encMaster = document.getElementById('encMaster');
function updateMasterVol(delta) {
  initAudio();
  masterVolLevel = Math.max(0, Math.min(100, masterVolLevel + delta));
  if (encMaster) encMaster.style.setProperty('--angle', `${(masterVolLevel / 100 * 270) - 135}deg`);
  if (audioCtx && audioCtx.destination) {
    // scale audio destination gain if available
  }
}
if (encMaster) {
  encMaster.addEventListener('wheel', (e) => { e.preventDefault(); updateMasterVol(e.deltaY < 0 ? 5 : -5); }, { passive: false });
}
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
  currentGameIdx = (currentGameIdx + dir + gameList.length) % gameList.length;
  if (encSelect) encSelect.style.setProperty('--angle', `${(currentGameIdx / gameList.length * 270) - 135}deg`);
  const g = gameList[currentGameIdx];
  if (g === 'pacman' || g === 'cclimber') switchActiveGame(g);
  else {
    if (currentMode !== 'tour') toggleTourDemo();
    tourState.idx = currentGameIdx;
  }
}
if (btnPrevGame) btnPrevGame.onclick = () => stepGame(-1);
if (btnNextGame) btnNextGame.onclick = () => stepGame(1);
if (encSelect) encSelect.addEventListener('wheel', (e) => { e.preventDefault(); stepGame(e.deltaY < 0 ? 1 : -1); }, { passive: false });

// Presets Encoder (Demo Songs)
const btnPrevSong = document.getElementById('btnPrevSong');
const btnNextSong = document.getElementById('btnNextSong');
const encPresets = document.getElementById('encPresets');
function stepSong(dir) {
  setMode('demo');
  currentDemoIdx = (currentDemoIdx + dir + DEMO_SONGS.length) % DEMO_SONGS.length;
  if (encPresets) encPresets.style.setProperty('--angle', `${(currentDemoIdx / DEMO_SONGS.length * 270) - 135}deg`);
  selectDemoSong(currentDemoIdx);
}
if (btnPrevSong) btnPrevSong.onclick = () => stepSong(-1);
if (btnNextSong) btnNextSong.onclick = () => stepSong(1);
if (encPresets) encPresets.addEventListener('wheel', (e) => { e.preventDefault(); stepSong(e.deltaY < 0 ? 1 : -1); }, { passive: false });

// Algorithm Encoder (Modes)
const btnPrevMode = document.getElementById('btnPrevMode');
const btnNextMode = document.getElementById('btnNextMode');
const encAlgorithm = document.getElementById('encAlgorithm');
function stepMode(dir) {
  const idx = (MODES.indexOf(currentMode) + dir + MODES.length) % MODES.length;
  setMode(MODES[idx]);
  if (encAlgorithm) encAlgorithm.style.setProperty('--angle', `${(idx / MODES.length * 270) - 135}deg`);
}
if (btnPrevMode) btnPrevMode.onclick = () => stepMode(-1);
if (btnNextMode) btnNextMode.onclick = () => stepMode(1);
if (encAlgorithm) encAlgorithm.addEventListener('wheel', (e) => { e.preventDefault(); stepMode(e.deltaY < 0 ? 1 : -1); }, { passive: false });
"""

script_body_content += "\n" + additional_hardware_bindings + "\n"

# Put everything together
final_template = new_head_and_body + script_body_content

with open("tools/simulator_template.html", "w") as out:
    out.write(final_template)

print(f"Successfully updated tools/simulator_template.html! (Length: {len(final_template)})")
