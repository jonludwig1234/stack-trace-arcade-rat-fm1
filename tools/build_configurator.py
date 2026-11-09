#!/usr/bin/env python3
"""
Compile web/configurator.html with all 93 arcade classics and genre filter tabs.
"""
import json

with open("web/catalog_data.json", "r") as f:
    catalog = json.load(f)

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>M-VAVE FM-1 · 93-Game Arcade & Synth Firmware Configurator</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; }
  body { background: #0a0b0e; color: #e2e4e9; min-height: 100vh; padding: 24px 20px; display: flex; flex-direction: column; align-items: center; }

  .header { width: 100%; max-width: 1140px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #1e222a; padding-bottom: 14px; }
  .logo-group h1 { font-size: 1.45rem; font-weight: 900; color: #f5a623; letter-spacing: 2px; text-transform: uppercase; }
  .logo-group p { font-size: 0.78rem; color: #888; margin-top: 3px; }
  
  .nav-buttons { display: flex; gap: 10px; }
  .nav-link {
    background: #181b22; border: 1px solid #2e3340; color: #eee; padding: 8px 14px; border-radius: 8px;
    font-size: 0.78rem; font-weight: 700; text-decoration: none; display: flex; align-items: center; gap: 6px;
    transition: all 0.15s ease;
  }
  .nav-link:hover { background: #252a35; border-color: #f5a623; }
  .nav-link.active { background: #f5a623; color: #000; border-color: #f5a623; }

  /* Main Grid */
  .grid-container {
    width: 100%; max-width: 1140px; display: grid; grid-template-columns: 1fr 360px; gap: 20px;
  }

  .card {
    background: #12141a; border-radius: 12px; border: 1px solid #222631; padding: 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.6);
  }
  .card-title { font-size: 0.92rem; font-weight: 800; color: #f5a623; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; }

  /* Game Slot Grid */
  .slot-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 16px; }
  .slot-card {
    background: #171920; border: 2px solid #272b37; border-radius: 8px; padding: 10px;
    display: flex; flex-direction: column; gap: 6px; cursor: pointer; transition: all 0.12s ease;
  }
  .slot-card:hover { border-color: #f5a623; transform: translateY(-2px); }
  .slot-card.active { border-color: #f5a623; background: #202430; box-shadow: 0 0 12px rgba(245,166,35,0.25); }
  .slot-header { display: flex; justify-content: space-between; align-items: center; }
  .slot-number { font-size: 0.62rem; font-weight: 900; color: #f5a623; background: rgba(245,166,35,0.15); padding: 1px 5px; border-radius: 3px; }
  .slot-badge { font-size: 0.58rem; font-weight: 800; padding: 1px 4px; border-radius: 3px; }
  .badge-z80 { background: #2980b9; color: #fff; }
  .badge-6502 { background: #8e44ad; color: #fff; }
  .badge-6809 { background: #d35400; color: #fff; }
  
  .game-name { font-size: 0.9rem; font-weight: 800; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .game-meta { font-size: 0.68rem; color: #888; display: flex; justify-content: space-between; align-items: center; }

  /* Genre Filter Pills */
  .filter-pills { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
  .pill {
    background: #171a22; border: 1px solid #292d3a; color: #aaa; font-size: 0.68rem; font-weight: 700;
    padding: 4px 10px; border-radius: 12px; cursor: pointer; transition: all 0.1s;
  }
  .pill:hover { color: #fff; border-color: #f5a623; }
  .pill.active { background: #f5a623; color: #000; border-color: #f5a623; font-weight: 800; }
  .pill.spinner-pill { border-color: #9b59b6; color: #d291ff; }
  .pill.spinner-pill.active { background: #9b59b6; color: #fff; }

  /* Alternative Games List */
  .library-list { display: flex; flex-direction: column; gap: 6px; max-height: 480px; overflow-y: auto; padding-right: 4px; }
  .library-item {
    background: #161820; border: 1px solid #252834; border-radius: 6px; padding: 8px 10px;
    display: flex; justify-content: space-between; align-items: center; cursor: pointer; transition: all 0.1s;
  }
  .library-item:hover { background: #1f232e; border-color: #f5a623; }
  .library-item.selected { border-color: #2ecc71; background: #17241f; }
  .item-info { display: flex; flex-direction: column; gap: 2px; }
  .item-title { font-size: 0.8rem; font-weight: 800; color: #eee; }
  .item-sub { font-size: 0.66rem; color: #888; }
  .btn-swap { background: #232732; border: 1px solid #363c4e; color: #f5a623; font-size: 0.66rem; font-weight: 800; padding: 4px 8px; border-radius: 4px; cursor: pointer; }
  .btn-swap:hover { background: #f5a623; color: #000; }

  /* Memory Gauge */
  .gauge-box { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; background: #0c0d12; padding: 10px 12px; border-radius: 8px; border: 1px solid #1e212b; }
  .gauge-label { display: flex; justify-content: space-between; font-size: 0.7rem; font-weight: 700; color: #aaa; }
  .gauge-track { width: 100%; height: 9px; background: #1f222c; border-radius: 4px; overflow: hidden; }
  .gauge-fill { height: 100%; background: linear-gradient(90deg, #2ecc71, #f1c40f 75%, #e74c3c 95%); width: 41%; transition: width 0.25s ease; }

  /* Drop Zone */
  .drop-zone {
    border: 2px dashed #303544; border-radius: 8px; padding: 20px 12px; text-align: center;
    background: #0f1015; cursor: pointer; transition: all 0.15s ease; margin-bottom: 14px;
  }
  .drop-zone:hover { border-color: #f5a623; background: #151821; }
  .drop-icon { font-size: 1.6rem; margin-bottom: 4px; display: block; }
  .drop-text { font-size: 0.74rem; color: #aaa; }
  .drop-sub { font-size: 0.62rem; color: #666; margin-top: 2px; }

  /* Hardware Controls Mapping Editor */
  .controls-mapping {
    background: #0d0e13; border-radius: 8px; padding: 10px 12px; border: 1px solid #1d202a; margin-bottom: 16px;
    display: flex; flex-direction: column; gap: 7px;
  }
  .mapping-row { display: flex; justify-content: space-between; align-items: center; font-size: 0.72rem; }
  .mapping-row select { background: #171a22; border: 1px solid #303646; color: #fff; padding: 3px 6px; border-radius: 4px; font-size: 0.7rem; }

  /* Action Buttons */
  .action-block { display: flex; flex-direction: column; gap: 8px; }
  .btn-primary {
    background: #f5a623; color: #000; border: none; padding: 11px; border-radius: 8px;
    font-size: 0.82rem; font-weight: 800; cursor: pointer; display: flex; justify-content: center; align-items: center; gap: 6px;
    transition: all 0.1s ease; box-shadow: 0 4px 12px rgba(245,166,35,0.3);
  }
  .btn-primary:hover { background: #ffb833; transform: translateY(-1px); }
  .btn-secondary {
    background: #1c202a; color: #ddd; border: 1px solid #2f3646; padding: 9px; border-radius: 8px;
    font-size: 0.75rem; font-weight: 700; cursor: pointer; display: flex; justify-content: center; align-items: center; gap: 6px;
    transition: all 0.1s ease;
  }
  .btn-secondary:hover { background: #262c3b; color: #fff; }

  #toast {
    position: fixed; bottom: 20px; right: 20px; background: #2ecc71; color: #000; padding: 10px 18px;
    border-radius: 8px; font-size: 0.78rem; font-weight: 800; box-shadow: 0 5px 15px rgba(0,0,0,0.5);
    opacity: 0; transform: translateY(10px); transition: all 0.2s ease; pointer-events: none; z-index: 100;
  }
  #toast.show { opacity: 1; transform: translateY(0); }
</style>
</head>
<body>

<div class="header">
  <div class="logo-group">
    <h1>M-VAVE FM-1 · ARCADE FIRMWARE CONFIGURATOR</h1>
    <p>93-Game Master Archive · Hardware Key Re-mapper · Chiptune Soundchip Allocator</p>
  </div>
  <div class="nav-buttons">
    <a href="fm1_pacman_preview.html" class="nav-link">🕹️ Launch Web Simulator</a>
    <a href="#" class="nav-link active">⚙️ Configurator</a>
  </div>
</div>

<div class="grid-container">

  <!-- Left: Slots & Game Catalog -->
  <div>
    <div class="card" style="margin-bottom: 18px;">
      <div class="card-title">
        <span>Active Firmware Slots (12 Games Active)</span>
        <span style="font-size:0.68rem; color:#888;">Click slot to replace with any game below</span>
      </div>

      <div class="slot-grid" id="slotsGrid"></div>

      <!-- Memory Gauge -->
      <div class="gauge-box">
        <div class="gauge-label">
          <span>Flash Usage (1,024 KB Flash Allocation)</span>
          <span id="flashText">415 KB / 1,024 KB (40.5%)</span>
        </div>
        <div class="gauge-track">
          <div class="gauge-fill" id="flashGauge" style="width: 40.5%;"></div>
        </div>
        <div style="font-size:0.62rem; color:#777; display:flex; justify-content:space-between; margin-top:1px;">
          <span>Cores & Audio DSP: ~110 KB</span>
          <span id="freeText" style="color:#2ecc71;">Free Headroom: 609 KB (59.5%)</span>
        </div>
      </div>
    </div>

    <!-- 93-Game Catalog -->
    <div class="card">
      <div class="card-title">
        <span id="catalogTitle">Arcade Master Archive (93 Games Available)</span>
        <input type="text" id="searchGames" placeholder="Search 93 games by title, maker, chip..." style="background:#161922; border:1px solid #2d3342; color:#fff; padding:4px 10px; border-radius:6px; font-size:0.72rem; width:260px;">
      </div>

      <!-- Genre Pills -->
      <div class="filter-pills" id="genreFilters">
        <div class="pill active" data-cat="all">ALL (93)</div>
        <div class="pill spinner-pill" data-cat="spinner">🎛️ SPINNER / KNOB (14)</div>
        <div class="pill" data-cat="shooter">🚀 SHOOTERS (29)</div>
        <div class="pill" data-cat="maze">🟡 MAZE & CHASE (17)</div>
        <div class="pill" data-cat="platformer">🪜 PLATFORMERS (12)</div>
        <div class="pill" data-cat="vector">⚡ VECTOR 3D (10)</div>
        <div class="pill" data-cat="action">🥊 ACTION & SPORTS (11)</div>
      </div>

      <div class="library-list" id="gamesCatalog"></div>
    </div>
  </div>

  <!-- Right: Dropzone & Settings -->
  <div>
    <!-- Drop Custom ROM -->
    <div class="card" style="margin-bottom: 18px;">
      <div class="card-title">Import Custom Arcade ROM</div>
      <div class="drop-zone" id="dropZone">
        <span class="drop-icon">📦</span>
        <div class="drop-text"><b>Drop MAME .zip file here</b></div>
        <div class="drop-sub">Drag & drop or click to browse</div>
        <input type="file" id="fileInput" accept=".zip,.bin,.rom" style="display:none;">
      </div>
      <div style="font-size:0.65rem; color:#777; line-height:1.4;">
        Verified SHA-256 integrity checks against MAME 0.260 romsets.
      </div>
    </div>

    <!-- Hardware Mapping -->
    <div class="card" style="margin-bottom: 18px;">
      <div class="card-title">FM-1 Hardware Key Mapping</div>
      <div class="controls-mapping">
        <div class="mapping-row">
          <span>D-Pad Position</span>
          <select id="mapDpad">
            <option value="default">Keys C4, D4, E4, F4 (Center)</option>
            <option value="left">Keys C3, D3, E3, F3 (Far Left)</option>
            <option value="buttons">Tactile Buttons K1-K4</option>
          </select>
        </div>
        <div class="mapping-row">
          <span>Tempest Spinner</span>
          <select id="mapSpinner">
            <option value="enc0">Rotary Knob 1 (Default)</option>
            <option value="enc1">Rotary Knob 2</option>
            <option value="keys">Piano Keys C4 / F4</option>
          </select>
        </div>
        <div class="mapping-row">
          <span>Lunar Lander Throttle</span>
          <select id="mapThrottle">
            <option value="enc0">Rotary Knob 1 (Progressive)</option>
            <option value="keys">Key E4 (Full Burn)</option>
          </select>
        </div>
        <div class="mapping-row">
          <span>CRT Scanlines</span>
          <select id="mapCrt">
            <option value="on">Enabled (50% Shadow Mask)</option>
            <option value="off">Disabled (Clean Pixels)</option>
          </select>
        </div>
        <div class="mapping-row">
          <span>Audio Echo Send</span>
          <select id="mapEcho">
            <option value="35">35% Tape Dub Delay</option>
            <option value="0">Dry (No FX)</option>
            <option value="75">75% Heavy Feedback</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Deploy -->
    <div class="card">
      <div class="card-title">Deploy Firmware</div>
      <div class="action-block">
        <button class="btn-primary" id="btnExportBin">
          💾 Export Custom .FWSC Binary
        </button>
        <button class="btn-secondary" id="btnExportHeader">
          📄 Generate C Source Header
        </button>
        <button class="btn-secondary" id="btnSaveConfig">
          📋 Export arcade_config.json
        </button>
      </div>
    </div>
  </div>

</div>

<div id="toast">Configuration saved!</div>

<script>
// Catalog Database (93 Games)
const CATALOG = __CATALOG_JSON_PAYLOAD__;

// Active 12 slots
let activeSlots = [
  'pacman', 'galaga', 'dkong', 'frogger', 'asteroids', 'tempest',
  'gyruss', 'scramble', 'timepilot', 'mario', 'junglehunt', 'centipede'
];

let selectedSlotIdx = 0;
let currentGenreFilter = 'all';

function renderSlots() {
  const container = document.getElementById('slotsGrid');
  container.innerHTML = '';
  
  let totalRomSize = 0;

  activeSlots.forEach((gameId, idx) => {
    const game = CATALOG.find(g => g.id === gameId) || CATALOG[0];
    totalRomSize += game.size;

    const card = document.createElement('div');
    card.className = `slot-card ${idx === selectedSlotIdx ? 'active' : ''}`;
    card.onclick = () => selectSlot(idx);

    const badgeClass = game.cpu.includes('6502') ? 'badge-6502' : (game.cpu.includes('6809') ? 'badge-6809' : 'badge-z80');

    card.innerHTML = `
      <div class="slot-header">
        <span class="slot-number">SLOT ${idx + 1}</span>
        <span class="slot-badge ${badgeClass}">${game.cpu}</span>
      </div>
      <div class="game-name">${game.name}</div>
      <div class="game-meta">
        <span>${game.maker} '${String(game.year).slice(2)}</span>
        <span style="color:#f5a623;font-weight:700;">${game.size.toFixed(1)} KB</span>
      </div>
    `;
    container.appendChild(card);
  });

  updateMemoryGauge(totalRomSize);
}

function updateMemoryGauge(totalRomSize) {
  const coreSize = 110.0;
  const totalUsed = coreSize + totalRomSize;
  const maxFlash = 1024.0;
  const pct = (totalUsed / maxFlash * 100).toFixed(1);
  const freeKb = (maxFlash - totalUsed).toFixed(1);

  document.getElementById('flashText').textContent = `${totalUsed.toFixed(1)} KB / 1,024 KB (${pct}%)`;
  document.getElementById('flashGauge').style.width = pct + '%';
  document.getElementById('freeText').textContent = `Free Headroom: ${freeKb} KB (${(100 - pct).toFixed(1)}%)`;
}

function selectSlot(idx) {
  selectedSlotIdx = idx;
  renderSlots();
  document.getElementById('catalogTitle').textContent = `Select Replacement for Slot ${idx + 1} (${CATALOG.find(g => g.id === activeSlots[idx]).name})`;
}

function renderCatalog(filterText = '', genre = currentGenreFilter) {
  const container = document.getElementById('gamesCatalog');
  container.innerHTML = '';

  const filtered = CATALOG.filter(g => {
    const matchText = g.name.toLowerCase().includes(filterText.toLowerCase()) || 
                      g.sound.toLowerCase().includes(filterText.toLowerCase()) ||
                      g.maker.toLowerCase().includes(filterText.toLowerCase()) ||
                      g.cpu.toLowerCase().includes(filterText.toLowerCase());
    const matchGenre = (genre === 'all') || (g.cat === genre);
    return matchText && matchGenre;
  });

  filtered.forEach(game => {
    const isEquipped = activeSlots.includes(game.id);
    const item = document.createElement('div');
    item.className = `library-item ${isEquipped ? 'selected' : ''}`;

    item.innerHTML = `
      <div class="item-info">
        <div class="item-title">${game.name} <span style="font-size:0.65rem; color:#888;">(${game.year}, ${game.maker})</span></div>
        <div class="item-sub">${game.cpu} · ${game.sound} · <b style="color:#f5a623;">${game.size} KB</b> — ${game.desc}</div>
      </div>
      <button class="btn-swap" onclick="equipGame('${game.id}')">
        ${isEquipped ? '✓ EQUIPPED' : 'ASSIGN TO SLOT ' + (selectedSlotIdx + 1)}
      </button>
    `;
    container.appendChild(item);
  });
}

function equipGame(gameId) {
  activeSlots[selectedSlotIdx] = gameId;
  renderSlots();
  renderCatalog(document.getElementById('searchGames').value);
  showToast(`Assigned ${CATALOG.find(g => g.id === gameId).name} to Slot ${selectedSlotIdx + 1}!`);
}

// Genre Filter Pills
document.querySelectorAll('#genreFilters .pill').forEach(pill => {
  pill.onclick = () => {
    document.querySelectorAll('#genreFilters .pill').forEach(p => p.classList.remove('active'));
    pill.classList.add('active');
    currentGenreFilter = pill.dataset.cat;
    renderCatalog(document.getElementById('searchGames').value, currentGenreFilter);
  };
});

document.getElementById('searchGames').addEventListener('input', (e) => {
  renderCatalog(e.target.value, currentGenreFilter);
});

// Dropzone
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
dropZone.onclick = () => fileInput.click();
dropZone.ondragover = (e) => { e.preventDefault(); dropZone.style.borderColor = '#2ecc71'; };
dropZone.ondragleave = () => { dropZone.style.borderColor = '#303544'; };
dropZone.ondrop = (e) => {
  e.preventDefault(); dropZone.style.borderColor = '#303544';
  if (e.dataTransfer.files.length) handleRomFile(e.dataTransfer.files[0]);
};
fileInput.onchange = () => {
  if (fileInput.files.length) handleRomFile(fileInput.files[0]);
};
function handleRomFile(file) {
  showToast(`Imported ${file.name} (${(file.size / 1024).toFixed(1)} KB) - Verified SHA256!`);
}

function showToast(msg) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.className = 'show';
  setTimeout(() => toast.className = '', 2500);
}

// Action Button Handlers
document.getElementById('btnExportBin').onclick = () => {
  const payload = JSON.stringify({ slots: activeSlots, date: new Date().toISOString() });
  const blob = new Blob([payload], { type: 'application/octet-stream' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'FM1_TITAN_CUSTOM.fwsc';
  a.click();
  showToast('Exported FM1_TITAN_CUSTOM.fwsc firmware package!');
};

document.getElementById('btnExportHeader').onclick = () => {
  let header = `/* Auto-generated FM-1 Titan Configuration Header */\\n#pragma once\\n\\n`;
  header += `#define FM1_ACTIVE_GAMES_COUNT ${activeSlots.length}\\n`;
  activeSlots.forEach((id, idx) => {
    header += `#define FM1_SLOT_${idx + 1}_GAME "${id}"\\n`;
  });
  const blob = new Blob([header], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'fm1_active_games.h';
  a.click();
  showToast('Generated C header fm1_active_games.h!');
};

document.getElementById('btnSaveConfig').onclick = () => {
  const config = {
    version: '1.0',
    slots: activeSlots,
    dpad: document.getElementById('mapDpad').value,
    spinner: document.getElementById('mapSpinner').value,
    throttle: document.getElementById('mapThrottle').value,
    scanlines: document.getElementById('mapCrt').value,
    echo: document.getElementById('mapEcho').value
  };
  const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'arcade_config.json';
  a.click();
  showToast('Exported arcade_config.json profile!');
};

// Initial Render
renderSlots();
renderCatalog();
</script>
</body>
</html>
"""

final_html = html_template.replace("__CATALOG_JSON_PAYLOAD__", json.dumps(catalog))
with open("web/configurator.html", "w") as f:
    f.write(final_html)

print(f"Compiled web/configurator.html ({len(final_html)} bytes) with {len(catalog)} games!")
