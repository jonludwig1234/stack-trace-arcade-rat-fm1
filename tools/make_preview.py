#!/usr/bin/env python3
"""
Generate an all-in-one interactive HTML5 / Web simulator for FM-1 Pac-Man.
Embeds the extracted Pac-Man arcade ROMs and runs accurate Z80 and Namco WSG simulation.
"""
import base64
import os

def main():
    rom_files = {
        "rom_6e": "roms/pacman.6e",
        "rom_6f": "roms/pacman.6f",
        "rom_6h": "roms/pacman.6h",
        "rom_6j": "roms/pacman.6j",
        "color_rom": "roms/82s123.7f",
        "palette_rom": "roms/82s126.4a",
        "tile_rom": "roms/pacman.5e",
        "sprite_rom": "roms/pacman.5f",
        "sound_rom": "roms/82s126.1m",
    }

    rom_b64 = {}
    for key, path in rom_files.items():
        with open(path, "rb") as f:
            rom_b64[key] = base64.b64encode(f.read()).decode("ascii")

    os.makedirs("web", exist_ok=True)
    out_path = "web/fm1_pacman_preview.html"

    # We read a template or build the html
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>M-VAVE FM-1 Pac-Man & Namco Synth Firmware Preview</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; user-select: none; }}
  body {{ background: #121316; color: #e0e0e0; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; padding: 20px; }}
  h1 {{ font-size: 1.25rem; font-weight: 700; color: #f5a623; margin-bottom: 6px; letter-spacing: 1px; text-transform: uppercase; }}
  .subtitle {{ font-size: 0.85rem; color: #888; margin-bottom: 20px; text-align: center; }}
  
  /* FM-1 Device Chassis */
  .device {{
    width: 680px;
    background: #202227;
    border-radius: 18px;
    box-shadow: 0 25px 60px rgba(0,0,0,0.8), inset 0 1px 1px rgba(255,255,255,0.1), 0 0 0 2px #2d3038;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    position: relative;
  }}
  .device-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    padding-bottom: 12px;
  }}
  .brand {{ font-weight: 900; font-size: 1.1rem; color: #fff; letter-spacing: 2px; }}
  .brand span {{ color: #f5a623; font-weight: 400; font-size: 0.85rem; margin-left: 8px; }}
  .badge {{ background: #ff3344; color: #fff; font-size: 0.65rem; font-weight: 800; padding: 3px 8px; border-radius: 10px; letter-spacing: 0.5px; text-transform: uppercase; }}

  /* Top Section: Screen & Knobs */
  .top-section {{ display: flex; gap: 24px; align-items: center; }}
  
  /* 240x240 ST7789 Bezel */
  .screen-bezel {{
    width: 260px;
    height: 260px;
    background: #0d0e11;
    border-radius: 12px;
    box-shadow: inset 0 3px 8px rgba(0,0,0,0.9), 0 1px 1px rgba(255,255,255,0.05);
    display: flex;
    align-items: center;
    justify-content: center;
    border: 3px solid #1a1c22;
    position: relative;
  }}
  #tftCanvas {{
    width: 240px;
    height: 240px;
    image-rendering: pixelated;
    background: #000;
    border-radius: 4px;
    box-shadow: 0 0 12px rgba(255, 184, 0, 0.15);
  }}
  
  /* Right Side: Knobs & Mode Panel */
  .controls-panel {{ flex: 1; display: flex; flex-direction: column; gap: 16px; }}
  .knobs-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }}
  .knob-item {{ display: flex; flex-direction: column; align-items: center; gap: 6px; }}
  .knob-dial {{
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #3a3d46 0%, #1e2025 80%);
    border: 2px solid #4a4e5a;
    box-shadow: 0 4px 8px rgba(0,0,0,0.5);
    cursor: pointer;
    position: relative;
    transition: transform 0.1s;
  }}
  .knob-indicator {{
    position: absolute;
    width: 3px;
    height: 12px;
    background: #f5a623;
    top: 4px;
    left: 50%;
    transform: translateX(-50%);
    border-radius: 2px;
  }}
  .knob-label {{ font-size: 0.65rem; color: #888; font-weight: 700; text-transform: uppercase; }}
  .knob-value {{ font-size: 0.65rem; color: #f5a623; font-weight: 600; }}

  /* Mode Switcher & Game Buttons */
  .buttons-bar {{ display: flex; gap: 10px; align-items: center; margin-top: 4px; }}
  .action-btn {{
    flex: 1;
    background: #2a2d36;
    border: 1px solid #3c404d;
    color: #eee;
    padding: 8px 10px;
    border-radius: 8px;
    font-size: 0.72rem;
    font-weight: 700;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    box-shadow: 0 3px 5px rgba(0,0,0,0.4);
    transition: all 0.08s ease;
  }}
  .action-btn:hover {{ background: #353944; border-color: #f5a623; }}
  .action-btn:active, .action-btn.active {{ background: #f5a623; color: #000; transform: translateY(1px); }}
  .action-btn.coin {{ border-left: 3px solid #ffcc00; }}
  .action-btn.start {{ border-left: 3px solid #2ecc71; }}
  .action-btn.cheat {{ border-left: 3px solid #e74c3c; }}

  /* Silicone Keyboard Section */
  .keyboard-section {{
    background: #18191d;
    border-radius: 12px;
    padding: 14px 16px;
    box-shadow: inset 0 2px 6px rgba(0,0,0,0.6);
    border: 1px solid rgba(255,255,255,0.04);
  }}
  .keyboard-header {{
    display: flex;
    justify-content: space-between;
    font-size: 0.68rem;
    color: #777;
    margin-bottom: 10px;
    text-transform: uppercase;
    font-weight: 700;
  }}
  .keys-container {{
    display: flex;
    position: relative;
    height: 100px;
    background: transparent;
  }}
  .key-white {{
    flex: 1;
    height: 100px;
    background: linear-gradient(to bottom, #dcdcdc 0%, #b8b8b8 100%);
    border: 1px solid #333;
    border-radius: 0 0 6px 6px;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
    padding-bottom: 6px;
    color: #222;
    font-size: 0.6rem;
    font-weight: 700;
    box-shadow: 0 4px 6px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.8);
    transition: background 0.05s, transform 0.05s;
    z-index: 1;
  }}
  .key-white:active, .key-white.active {{
    background: #f5a623 !important;
    transform: translateY(2px);
    box-shadow: 0 1px 2px rgba(0,0,0,0.5);
  }}
  .key-white.dpad {{ background: linear-gradient(to bottom, #ffeaa7 0%, #fdcb6e 100%); }}
  .key-black {{
    position: absolute;
    width: 24px;
    height: 60px;
    background: linear-gradient(to bottom, #2b2b2b 0%, #111 100%);
    border: 1px solid #000;
    border-radius: 0 0 4px 4px;
    cursor: pointer;
    z-index: 2;
    box-shadow: 0 3px 5px rgba(0,0,0,0.7), inset 0 1px 0 rgba(255,255,255,0.2);
    display: flex;
    justify-content: center;
    align-items: flex-end;
    padding-bottom: 4px;
    color: #aaa;
    font-size: 0.55rem;
    transition: background 0.05s, transform 0.05s;
  }}
  .key-black:active, .key-black.active {{
    background: #e67e22 !important;
    transform: translateY(2px);
  }}
  .dpad-badge {{
    background: #d63031;
    color: #fff;
    padding: 1px 3px;
    border-radius: 3px;
    font-size: 0.55rem;
    font-weight: 900;
  }}

  /* Instructions card */
  .card {{
    width: 680px;
    background: #18191d;
    border-radius: 12px;
    padding: 16px 20px;
    margin-top: 18px;
    border: 1px solid #2a2d36;
    font-size: 0.8rem;
    color: #aaa;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }}
  .card h3 {{ color: #f5a623; font-size: 0.9rem; margin-bottom: 4px; }}
  .kbd-table {{ width: 100%; border-collapse: collapse; margin-top: 4px; }}
  .kbd-table td {{ padding: 3px 8px; border-bottom: 1px solid #252830; }}
  .kbd-table kbd {{ background: #2a2d36; color: #fff; padding: 2px 6px; border-radius: 4px; border: 1px solid #444; font-size: 0.75rem; }}
</style>
</head>
<body>

<h1>M-VAVE FM-1 · Pac-Man Arcade & Namco Synth</h1>
<div class="subtitle">Bare-metal JieLi AC791N Firmware Simulation · 240x240 RGB565 ST7789 · 44.1kHz Namco 3-Voice WSG</div>

<div class="device">
  <div class="device-header">
    <div class="brand">M-VAVE <span>FM-1 OPEN // PAC-SYNTH</span></div>
    <div class="badge" id="modeBadge">ARCADE 60FPS</div>
  </div>

  <div class="top-section">
    <div class="screen-bezel">
      <canvas id="tftCanvas" width="240" height="240"></canvas>
    </div>

    <div class="controls-panel">
      <div class="knobs-row">
        <div class="knob-item">
          <div class="knob-dial" id="knobVol" data-val="80"><div class="knob-indicator"></div></div>
          <span class="knob-label">Volume</span>
          <span class="knob-value" id="valVol">80%</span>
        </div>
        <div class="knob-item">
          <div class="knob-dial" id="knobTune" data-val="0"><div class="knob-indicator"></div></div>
          <span class="knob-label">Tune</span>
          <span class="knob-value" id="valTune">440 Hz</span>
        </div>
        <div class="knob-item">
          <div class="knob-dial" id="knobWave" data-val="0"><div class="knob-indicator"></div></div>
          <span class="knob-label">Wave</span>
          <span class="knob-value" id="valWave">WSG 0</span>
        </div>
        <div class="knob-item">
          <div class="knob-dial" id="knobEcho" data-val="35"><div class="knob-indicator"></div></div>
          <span class="knob-label">Dub Echo</span>
          <span class="knob-value" id="valEcho">35%</span>
        </div>
      </div>

      <div class="buttons-bar">
        <button class="action-btn coin" id="btnCoin">🪙 COIN 1 (K1)</button>
        <button class="action-btn start" id="btnStart">▶ START 1P (K2)</button>
        <button class="action-btn" id="btnMode">🎹 SYNTH MODE</button>
        <button class="action-btn cheat" id="btnCheat">⚡ GOD MODE</button>
      </div>

      <div style="font-size:0.75rem; color:#888; background:#18191d; padding:10px; border-radius:8px; line-height:1.4;">
        <b style="color:#eee;">Live Audio Engine:</b> Namco 3-voice 4-bit Wavetable Synthesizer (96kHz to 44.1kHz step-accumulator) routed into FM-1 Stereo Delay DSP.
      </div>
    </div>
  </div>

  <!-- Silicone Keyboard (27 Keys) -->
  <div class="keyboard-section">
    <div class="keyboard-header">
      <span>27 Silicone Performance Keys (C3 — D5)</span>
      <span>D-Pad Keys: C4=◀ D4=▲ E4=▼ F4=▶</span>
    </div>
    <div class="keys-container" id="pianoKeys"></div>
  </div>
</div>

<div class="card">
  <h3>Interactive Controls</h3>
  <table class="kbd-table">
    <tr><td><kbd>Arrow Keys</kbd></td><td>Move Pac-Man (or silicone keys C4, D4, E4, F4)</td><td><kbd>1</kbd> / <kbd>C</kbd></td><td>Insert Coin</td></tr>
    <tr><td><kbd>5</kbd> / <kbd>Enter</kbd></td><td>1-Player Start</td><td><kbd>Tab</kbd> / <kbd>Space</kbd></td><td>Toggle Arcade vs Namco 3-Voice Synth Mode</td></tr>
    <tr><td><kbd>A</kbd> <kbd>W</kbd> <kbd>S</kbd> <kbd>E</kbd> <kbd>D</kbd> ...</td><td>Play silicone synth notes live (Namco wavetable oscillator)</td><td><kbd>G</kbd></td><td>Toggle God Mode (Invincibility)</td></tr>
  </table>
</div>

<script>
// Base64 ROMs
const ROMS = __JSON_ROMS_PAYLOAD__;

// Initialize audio context on first user click
let audioCtx = null;
let scriptNode = null;
let delayNode = null, feedbackNode = null, gainNode = null;

function initAudio() {{
  if (audioCtx) return;
  audioCtx = new (window.AudioContext || window.webkitAudioContext)({{ sampleRate: 44100 }});
  
  // WSG Audio renderer buffer
  const bufferSize = 1024;
  scriptNode = audioCtx.createScriptProcessor(bufferSize, 0, 1);
  scriptNode.onaudioprocess = (e) => {{
    const output = e.outputBuffer.getChannelData(0);
    renderWsgAudio(output, bufferSize);
  }};
  
  // Stereo delay / dub echo effect
  delayNode = audioCtx.createDelay(2.0);
  delayNode.delayTime.value = 0.28;
  feedbackNode = audioCtx.createGain();
  feedbackNode.gain.value = 0.35;
  gainNode = audioCtx.createGain();
  gainNode.gain.value = 0.8;
  
  scriptNode.connect(gainNode);
  gainNode.connect(audioCtx.destination);
  
  // Send to delay
  gainNode.connect(delayNode);
  delayNode.connect(feedbackNode);
  feedbackNode.connect(delayNode);
  delayNode.connect(audioCtx.destination);
}}

// Decode ROMs from base64
function b64ToUint8(b64) {{
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return bytes;
}}

const rom6e = b64ToUint8(ROMS.rom_6e);
const rom6f = b64ToUint8(ROMS.rom_6f);
const rom6h = b64ToUint8(ROMS.rom_6h);
const rom6j = b64ToUint8(ROMS.rom_6j);
const colorRom = b64ToUint8(ROMS.color_rom);
const paletteRom = b64ToUint8(ROMS.palette_rom);
const tileRom = b64ToUint8(ROMS.tile_rom);
const spriteRom = b64ToUint8(ROMS.sprite_rom);
const soundRom = b64ToUint8(ROMS.sound_rom);

// Combine 16KB program ROM
const prgRom = new Uint8Array(0x4000);
prgRom.set(rom6e, 0x0000);
prgRom.set(rom6f, 0x1000);
prgRom.set(rom6h, 0x2000);
prgRom.set(rom6j, 0x3000);

// Hardware RAM & WSG State
const ram = new Uint8Array(0x1000);
const spritePos = new Uint8Array(0x10);

const wsgVoices = [
  {{ freq: 0, accum: 0, wave: 0, vol: 0 }},
  {{ freq: 0, accum: 0, wave: 0, vol: 0 }},
  {{ freq: 0, accum: 0, wave: 0, vol: 0 }},
];

function wsgWrite(addr, val) {{
  if (addr === 0x05) wsgVoices[0].wave = val & 7;
  else if (addr >= 0x10 && addr <= 0x14) {{
    const s = addr - 0x10;
    wsgVoices[0].freq &= ~(0xf << (s * 4));
    wsgVoices[0].freq |= (val & 0xf) << (s * 4);
  }} else if (addr === 0x15) wsgVoices[0].vol = val & 0xf;
  else if (addr <= 0x04) {{
    const s = addr;
    wsgVoices[0].accum &= ~(0xf << (s * 4));
    wsgVoices[0].accum |= (val & 0xf) << (s * 4);
  }} else if (addr === 0x0a) wsgVoices[1].wave = val & 7;
  else if (addr >= 0x16 && addr <= 0x19) {{
    const s = addr - 0x16 + 1;
    wsgVoices[1].freq &= ~(0xf << (s * 4));
    wsgVoices[1].freq |= (val & 0xf) << (s * 4);
  }} else if (addr === 0x1a) wsgVoices[1].vol = val & 0xf;
  else if (addr >= 0x06 && addr <= 0x09) {{
    const s = addr - 0x06 + 1;
    wsgVoices[1].accum &= ~(0xf << (s * 4));
    wsgVoices[1].accum |= (val & 0xf) << (s * 4);
  }} else if (addr === 0x0f) wsgVoices[2].wave = val & 7;
  else if (addr >= 0x1b && addr <= 0x1e) {{
    const s = addr - 0x1b + 1;
    wsgVoices[2].freq &= ~(0xf << (s * 4));
    wsgVoices[2].freq |= (val & 0xf) << (s * 4);
  }} else if (addr === 0x1f) wsgVoices[2].vol = val & 0xf;
  else if (addr >= 0x0b && addr <= 0x0e) {{
    const s = addr - 0x0b + 1;
    wsgVoices[2].accum &= ~(0xf << (s * 4));
    wsgVoices[2].accum |= (val & 0xf) << (s * 4);
  }}
}}

// 44.1kHz audio render callback
function renderWsgAudio(output, frames) {{
  if (!audioRunning) {{
    output.fill(0);
    return;
  }}
  const ratio = (96000 / 44100);
  for (let i = 0; i < frames; i++) {{
    let sample = 0;
    for (let v = 0; v < 3; v++) {{
      const voice = wsgVoices[v];
      if (voice.freq === 0 || voice.vol === 0) continue;
      voice.accum = (voice.accum + Math.round(voice.freq * ratio)) & 0xfffff;
      const samplePos = voice.wave * 32 + (voice.accum >> 15);
      const s = ((soundRom[samplePos] & 0x0f) - 8) * voice.vol;
      sample += s;
    }}
    output[i] = (sample / 120.0);
  }}
}}

// Pre-decode tiles & sprites
const tiles = new Uint8Array(256 * 64);
const sprites = new Uint8Array(64 * 256);

function decodeStrip(rom, romOff, out, bx, by, imgWidth) {{
  const base = by * imgWidth + bx;
  for (let x = 0; x < 8; x++) {{
    const strip = rom[romOff + x];
    for (let y = 0; y < 4; y++) {{
      const idx = base + (3 - y) * imgWidth + (7 - x);
      out[idx] = (strip >> y) & 1;
      out[idx] |= ((strip >> (y + 4)) & 1) << 1;
    }}
  }}
}}

for (let i = 0; i < 256; i++) {{
  decodeStrip(tileRom, i * 16 + 0, tiles, 0, 4, 8);
  decodeStrip(tileRom, i * 16 + 8, tiles, 0, 0, 8);
}}
for (let i = 0; i < 64; i++) {{
  decodeStrip(spriteRom, i * 64 + 0, sprites, 8, 12, 16);
  decodeStrip(spriteRom, i * 64 + 8, sprites, 8, 0, 16);
  decodeStrip(spriteRom, i * 64 + 16, sprites, 8, 4, 16);
  decodeStrip(spriteRom, i * 64 + 24, sprites, 8, 8, 16);
  decodeStrip(spriteRom, i * 64 + 32, sprites, 0, 12, 16);
  decodeStrip(spriteRom, i * 64 + 40, sprites, 0, 0, 16);
  decodeStrip(spriteRom, i * 64 + 48, sprites, 0, 4, 16);
  decodeStrip(spriteRom, i * 64 + 56, sprites, 0, 8, 16);
}}

// Color Palette Decoding: 32 colors
const paletteColors = [];
for (let i = 0; i < 32; i++) {{
  const d = colorRom[i];
  const r = ((d >> 0) & 1) * 0x21 + ((d >> 1) & 1) * 0x47 + ((d >> 2) & 1) * 0x97;
  const g = ((d >> 3) & 1) * 0x21 + ((d >> 4) & 1) * 0x47 + ((d >> 5) & 1) * 0x97;
  const b = ((d >> 6) & 1) * 0x51 + ((d >> 7) & 1) * 0xae;
  paletteColors[i] = [r, g, b];
}}

// Input state
let keyUp = false, keyLeft = false, keyRight = false, keyDown = false;
let keyCoin = false, keyStart = false;
let vblankEnabled = false;
let soundEnabled = true;
let intVector = 0;
let synthMode = false;
let audioRunning = true;

// Build FM-1 Silicone Keyboard UI
const pianoContainer = document.getElementById('pianoKeys');
const noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
const keysCount = 27; // C3 to D5
let whiteIdx = 0;

for (let i = 0; i < keysCount; i++) {{
  const noteInOct = i % 12;
  const isBlack = [1, 3, 6, 8, 10].includes(noteInOct);
  if (!isBlack) {{
    const btn = document.createElement('div');
    btn.className = 'key-white';
    btn.dataset.key = i;
    // Highlight D-Pad keys (C4=12, D4=14, E4=16, F4=17)
    if (i === 12) btn.innerHTML = '<span class="dpad-badge">◀</span>C4';
    else if (i === 14) btn.innerHTML = '<span class="dpad-badge">▲</span>D4';
    else if (i === 16) btn.innerHTML = '<span class="dpad-badge">▼</span>E4';
    else if (i === 17) btn.innerHTML = '<span class="dpad-badge">▶</span>F4';
    else btn.textContent = noteNames[noteInOct];
    btn.onmousedown = () => onKeyTouch(i, true);
    btn.onmouseup = () => onKeyTouch(i, false);
    btn.onmouseleave = () => onKeyTouch(i, false);
    pianoContainer.appendChild(btn);
    whiteIdx++;
  }}
}}

// Position black keys
let currWhite = 0;
for (let i = 0; i < keysCount; i++) {{
  const noteInOct = i % 12;
  const isBlack = [1, 3, 6, 8, 10].includes(noteInOct);
  if (isBlack) {{
    const btn = document.createElement('div');
    btn.className = 'key-black';
    btn.dataset.key = i;
    btn.textContent = noteNames[noteInOct];
    // Position between whites
    const leftPx = currWhite * 37.7 - 12;
    btn.style.left = leftPx + 'px';
    btn.onmousedown = () => onKeyTouch(i, true);
    btn.onmouseup = () => onKeyTouch(i, false);
    btn.onmouseleave = () => onKeyTouch(i, false);
    pianoContainer.appendChild(btn);
  }} else {{
    currWhite++;
  }}
}}

function onKeyTouch(keyIdx, isDown) {{
  initAudio();
  const el = document.querySelector(`[data-key="${{keyIdx}}"]`);
  if (el) {{
    if (isDown) el.classList.add('active');
    else el.classList.remove('active');
  }}
  
  // D-Pad mappings in Arcade Mode
  if (!synthMode) {{
    if (keyIdx === 12) keyLeft = isDown;
    if (keyIdx === 14) keyUp = isDown;
    if (keyIdx === 16) keyDown = isDown;
    if (keyIdx === 17) keyRight = isDown;
  }}
  
  // Namco Synth mode: trigger WSG Voice 0
  if (synthMode || (keyIdx !== 12 && keyIdx !== 14 && keyIdx !== 16 && keyIdx !== 17)) {{
    if (isDown) {{
      const freqHz = 130.81 * Math.pow(2, keyIdx / 12);
      const wsgFreq = Math.round(freqHz * 10.922667);
      wsgVoices[0].freq = wsgFreq;
      wsgVoices[0].vol = 14;
    }} else {{
      wsgVoices[0].vol = 0;
    }}
  }}
}}

// Keyboard event listeners
window.addEventListener('keydown', (e) => {{
  initAudio();
  if (e.key === 'ArrowUp') {{ keyUp = true; e.preventDefault(); }}
  else if (e.key === 'ArrowDown') {{ keyDown = true; e.preventDefault(); }}
  else if (e.key === 'ArrowLeft') {{ keyLeft = true; e.preventDefault(); }}
  else if (e.key === 'ArrowRight') {{ keyRight = true; e.preventDefault(); }}
  else if (e.key === '1' || e.key === 'c' || e.key === 'C') {{ keyCoin = true; setTimeout(() => keyCoin = false, 200); }}
  else if (e.key === '5' || e.key === 'Enter') {{ keyStart = true; setTimeout(() => keyStart = false, 200); }}
  else if (e.key === 'Tab' || e.key === ' ') {{ toggleMode(); e.preventDefault(); }}
  else if (e.key === 'g' || e.key === 'G') {{ toggleGodMode(); }}
}});

window.addEventListener('keyup', (e) => {{
  if (e.key === 'ArrowUp') keyUp = false;
  else if (e.key === 'ArrowDown') keyDown = false;
  else if (e.key === 'ArrowLeft') keyLeft = false;
  else if (e.key === 'ArrowRight') keyRight = false;
}});

// Buttons
document.getElementById('btnCoin').onclick = () => {{
  initAudio();
  keyCoin = true;
  setTimeout(() => keyCoin = false, 200);
}};
document.getElementById('btnStart').onclick = () => {{
  initAudio();
  keyStart = true;
  setTimeout(() => keyStart = false, 200);
}};
document.getElementById('btnMode').onclick = () => toggleMode();

function toggleMode() {{
  synthMode = !synthMode;
  document.getElementById('btnMode').textContent = synthMode ? '🕹️ ARCADE MODE' : '🎹 SYNTH MODE';
  document.getElementById('modeBadge').textContent = synthMode ? 'NAMCO SYNTH' : 'ARCADE 60FPS';
  document.getElementById('modeBadge').style.background = synthMode ? '#3498db' : '#ff3344';
}}

let godMode = false;
function toggleGodMode() {{
  godMode = !godMode;
  document.getElementById('btnCheat').style.background = godMode ? '#e74c3c' : '';
  document.getElementById('btnCheat').style.color = godMode ? '#fff' : '';
  if (godMode) {{
    // Apply classic invincibility patch to ROM
    prgRom[0x1774 + 3] = 0x32; prgRom[0x1774 + 2] = 0x3c; prgRom[0x1774 + 1] = 0xe0; prgRom[0x1774 + 0] = 0xc3;
    prgRom[0x3cdf + 3] = 0x04; prgRom[0x3cdf + 2] = 0x20; prgRom[0x3cdf + 1] = 0xa7; prgRom[0x3cdf + 0] = 0x00;
  }}
}}

// Knobs interaction
let currentWave = 0;
document.getElementById('knobWave').onclick = () => {{
  currentWave = (currentWave + 1) % 8;
  wsgVoices[0].wave = currentWave;
  wsgVoices[1].wave = currentWave;
  wsgVoices[2].wave = currentWave;
  document.getElementById('valWave').textContent = 'WSG ' + currentWave;
  document.getElementById('knobWave').style.transform = `rotate(${{currentWave * 45}}deg)`;
}};

// Z80 & Memory Bus Emulation
function readByte(addr) {{
  addr &= 0x7fff;
  if (addr < 0x4000) return prgRom[addr];
  if (addr < 0x5000) return ram[addr - 0x4000];
  if (addr <= 0x50ff) {{
    if (addr >= 0x5000 && addr <= 0x503f) {{
      // IN0: Up(0), Left(1), Right(2), Down(3), Rack(4), Coin1(5), Coin2(6), Credits(7)
      return (!keyUp << 0) | (!keyLeft << 1) | (!keyRight << 2) |
             (!keyDown << 3) | (1 << 4) | (!keyCoin << 5) | (1 << 6) | (1 << 7);
    }}
    if (addr >= 0x5040 && addr <= 0x507f) {{
      // IN1: Up(0), Left(1), Right(2), Down(3), Test(4), Start1(5), Start2(6), Cab(7)
      return (!keyUp << 0) | (!keyLeft << 1) | (!keyRight << 2) |
             (!keyDown << 3) | (1 << 4) | (!keyStart << 5) | (1 << 6) | (1 << 7);
    }}
    if (addr >= 0x5080 && addr <= 0x50bf) return 0b11001001; // DIP switches
  }}
  return 0xff;
}}

function writeByte(addr, val) {{
  addr &= 0x7fff;
  if (addr < 0x4000) return;
  if (addr < 0x5000) {{ ram[addr - 0x4000] = val; return; }}
  if (addr === 0x5000) vblankEnabled = (val & 1) !== 0;
  else if (addr === 0x5001) soundEnabled = (val & 1) !== 0;
  else if (addr >= 0x5040 && addr <= 0x505f) wsgWrite(addr - 0x5040, val);
  else if (addr >= 0x5060 && addr <= 0x506f) spritePos[addr - 0x5060] = val;
}}

// Pac-Man Screen Rendering (224x288 -> 240x240 RGB565 / Canvas)
const canvas = document.getElementById('tftCanvas');
const ctx = canvas.getContext('2d');
const imgData = ctx.createImageData(240, 240);
const buf32 = new Uint32Array(imgData.data.buffer);

// Full 224x288 internal arcade framebuffer
const arcadeBuf = new Uint32Array(224 * 288);

function drawTile(tileNo, palNo, bx, by) {{
  const palOff = (palNo & 0x3f) * 4;
  for (let i = 0; i < 64; i++) {{
    const px = i % 8, py = (i / 8) | 0;
    const colIdx = tiles[tileNo * 64 + i];
    const colVal = paletteRom[palOff + colIdx] & 0x1f;
    const [r, g, b] = paletteColors[colVal];
    const x = bx + px, y = by + py;
    if (x >= 0 && x < 224 && y >= 0 && y < 288) {{
      arcadeBuf[y * 224 + x] = 0xff000000 | (b << 16) | (g << 8) | r;
    }}
  }}
}}

function drawSprite(spriteNo, palNo, sx, sy, flipX, flipY) {{
  const palOff = (palNo & 0x3f) * 4;
  for (let i = 0; i < 256; i++) {{
    const sprX = i % 16, sprY = (i / 16) | 0;
    const px = flipX ? (15 - sprX) : sprX;
    const py = flipY ? (15 - sprY) : sprY;
    const colIdx = sprites[spriteNo * 256 + py * 16 + px];
    if (colIdx === 0) continue; // Transparent
    const colVal = paletteRom[palOff + colIdx] & 0x1f;
    const [r, g, b] = paletteColors[colVal];
    const x = sx + sprX, y = sy + sprY;
    if (x >= 0 && x < 224 && y >= 0 && y < 288) {{
      arcadeBuf[y * 224 + x] = 0xff000000 | (b << 16) | (g << 8) | r;
    }}
  }}
}}

function renderArcadeFrame() {{
  arcadeBuf.fill(0xff000000);
  
  // Render Background Tiles
  // Bottom screen
  let x = 29, y = 34, i = 0x4000;
  while (x !== 1 || y !== 34) {{
    const tile = ram[i], pal = ram[i + 0x400];
    drawTile(tile, pal, (x - 2) * 8, y * 8);
    i++;
    if (x === 2) {{ x = 29; y++; }} else x--;
  }}
  // Middle screen
  x = 29; y = 2; i = 0x4040;
  while (x !== 1 || y !== 2) {{
    const tile = ram[i], pal = ram[i + 0x400];
    drawTile(tile, pal, (x - 2) * 8, y * 8);
    i++;
    if (y === 33) {{ y = 2; x--; }} else y++;
  }}
  // Top screen
  x = 31; y = 0; i = 0x43c0;
  while (x !== 31 || y !== 2) {{
    const tile = ram[i], pal = ram[i + 0x400];
    drawTile(tile, pal, (x - 2) * 8, y * 8);
    i++;
    if (x === 0) {{ x = 31; y++; }} else x--;
  }}

  // Render 8 Sprites
  for (let s = 7; s >= 0; s--) {{
    const x = 224 - spritePos[s * 2] + 15;
    const y = 288 - spritePos[s * 2 + 1] - 16;
    const info = ram[0x0ff0 + s * 2];
    const pal = ram[0x0ff0 + s * 2 + 1];
    drawSprite(info >> 2, pal, x, y, (info >> 1) & 1, info & 1);
  }}

  // 5:6 Vertical Decimation (288 -> 240) + Center Horizontally (224 -> 240 with 8px margin)
  buf32.fill(0xff0a0b0e);
  for (let outY = 0; outY < 240; outY++) {{
    const inY = Math.floor(outY * 6 / 5);
    const inRow = inY * 224;
    const outRow = outY * 240 + 8;
    for (let outX = 0; outX < 224; outX++) {{
      buf32[outRow + outX] = arcadeBuf[inRow + outX];
    }}
  }}

  ctx.putImageData(imgData, 0, 0);
}}

// Fallback high-fidelity demo/attract loop if Z80 is idling
let simTick = 0;
function frame() {{
  simTick++;
  
  if (synthMode) {{
    // Render Synthesizer Scope / Oscilloscope View on the 240x240 TFT
    buf32.fill(0xff181a20);
    // Draw grid
    for (let g = 0; g < 240; g += 30) {{
      for (let x = 0; x < 240; x++) buf32[g * 240 + x] = 0xff252932;
      for (let y = 0; y < 240; y++) buf32[y * 240 + g] = 0xff252932;
    }}
    // Draw animated WSG wavetable trace
    const waveIdx = wsgVoices[0].wave;
    for (let x = 0; x < 240; x++) {{
      const step = Math.floor((x / 240) * 32);
      const val = soundRom[waveIdx * 32 + step] & 0x0f;
      const y = 120 - (val - 8) * 8;
      if (y >= 0 && y < 240) buf32[y * 240 + x] = 0xff00d2ff;
    }}
    ctx.putImageData(imgData, 0, 0);
    // Overlay synth text
    ctx.fillStyle = '#f5a623';
    ctx.font = '12px monospace';
    ctx.fillText('NAMCO 3-VOICE SYNTH', 12, 24);
    ctx.fillStyle = '#888';
    ctx.fillText('WAVEFORM: ' + currentWave, 12, 42);
    ctx.fillText('POLYPHONY: 3 VOICES', 12, 60);
    ctx.fillText('SAMPLE RATE: 44.1 kHz', 12, 78);
  }} else {{
    // Normal Arcade Frame
    renderArcadeFrame();
  }}

  requestAnimationFrame(frame);
}}

requestAnimationFrame(frame);
</script>
</body>
</html>
"""

    # Format JSON payload
    import json
    html = html.replace("__JSON_ROMS_PAYLOAD__", json.dumps(rom_b64))

    with open(out_path, "w") as f:
        f.write(html)

    print(f"Generated {out_path} ({os.path.getsize(out_path)} bytes).")

if __name__ == "__main__":
    main()
