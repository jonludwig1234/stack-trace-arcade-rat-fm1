import re

print("=== FIXING AND REBUILDING HARDWARE TEMPLATE & SIMULATOR ===")

with open("tools/build_hardware_template.py", "r") as f:
    code = f.read()

# 1. Fix the broken script_idx at the top of build_hardware_template.py
broken_snippet_start = 'script_idx = content.find("<script>'
broken_snippet_end = '")\n    if script_idx == -1:'

pos_s = code.find(broken_snippet_start)
pos_e = code.find(broken_snippet_end)

if pos_s != -1 and pos_e != -1:
    fixed_start = 'script_idx = content.find("<script>")\n    if script_idx == -1:'
    code = code[:pos_s] + fixed_start + code[pos_e + len(broken_snippet_end):]
    print("Fixed script_idx at top of build_hardware_template.py!")

# 2. Make sure switchActiveGame calls updateMissionCard(gameId)
if "if (typeof updateMissionCard === 'function') updateMissionCard(gameId);" not in code:
    old_switch_pac = "ensurePastBoot();\n    renderArcadeFrame();\n  }\n}"
    new_switch_pac = "ensurePastBoot();\n    renderArcadeFrame();\n  }\n  if (typeof updateMissionCard === 'function') updateMissionCard(gameId);\n}"
    if old_switch_pac in code:
        code = code.replace(old_switch_pac, new_switch_pac, 1)
        print("Hooked updateMissionCard into switchActiveGame.")

# 3. Add Jukebox UI Shelf synchronization to playDemoSong, pauseDemoSong, stopDemoSong, selectDemoSong
old_play_demo = """function playDemoSong() {
  initAudio();
  if (demoPlayer.playing) return;
  demoPlayer.playing = true;
  document.getElementById('btnJukePlay').textContent = '⏸ PAUSE';
  document.getElementById('btnJukePlay').classList.add('playing');
  document.getElementById('jukeStatus').textContent = 'PLAYING';
  
  scheduleDemoTick();
}"""

new_play_demo = """function playDemoSong() {
  initAudio();
  if (demoPlayer.playing) return;
  demoPlayer.playing = true;
  const btn = document.getElementById('btnJukePlay');
  if (btn) { btn.textContent = '⏸ PAUSE'; btn.classList.add('playing'); }
  const st = document.getElementById('jukeStatus');
  if (st) st.textContent = 'PLAYING';
  const shelfSt = document.getElementById('shelfJukeStatus');
  if (shelfSt) { shelfSt.textContent = 'PLAYING'; shelfSt.style.color = '#00ff66'; }
  const btnShelf = document.getElementById('btnShelfPlay');
  if (btnShelf) btnShelf.textContent = '⏸ PAUSE';
  
  scheduleDemoTick();
}"""

old_pause_demo = """function pauseDemoSong() {
  demoPlayer.playing = false;
  if (demoPlayer.timer) clearTimeout(demoPlayer.timer);
  demoPlayer.timer = null;
  document.getElementById('btnJukePlay').textContent = '▶ PLAY SONG';
  document.getElementById('btnJukePlay').classList.remove('playing');
  document.getElementById('jukeStatus').textContent = 'PAUSED';
}"""

new_pause_demo = """function pauseDemoSong() {
  demoPlayer.playing = false;
  if (demoPlayer.timer) clearTimeout(demoPlayer.timer);
  demoPlayer.timer = null;
  const btn = document.getElementById('btnJukePlay');
  if (btn) { btn.textContent = '▶ PLAY SONG'; btn.classList.remove('playing'); }
  const st = document.getElementById('jukeStatus');
  if (st) st.textContent = 'PAUSED';
  const shelfSt = document.getElementById('shelfJukeStatus');
  if (shelfSt) { shelfSt.textContent = 'PAUSED'; shelfSt.style.color = '#f5a623'; }
  const btnShelf = document.getElementById('btnShelfPlay');
  if (btnShelf) btnShelf.textContent = '▶ PLAY';
}"""

old_stop_demo = """function stopDemoSong() {
  pauseDemoSong();
  demoPlayer.step = 0;
  demoPlayer.vuLevels.fill(0);
  document.getElementById('jukeStatus').textContent = 'STOPPED';
  updateJukeboxUI();
}"""

new_stop_demo = """function stopDemoSong() {
  pauseDemoSong();
  demoPlayer.step = 0;
  demoPlayer.vuLevels.fill(0);
  const st = document.getElementById('jukeStatus');
  if (st) st.textContent = 'STOPPED';
  const shelfSt = document.getElementById('shelfJukeStatus');
  if (shelfSt) { shelfSt.textContent = 'STOPPED'; shelfSt.style.color = '#8fa5a0'; }
  updateJukeboxUI();
}"""

old_select_demo = """function selectDemoSong(idx) {
  demoPlayer.currentSongIdx = idx;
  document.querySelectorAll('.song-pill').forEach((p, i) => p.classList.toggle('active', i === idx));
  demoPlayer.step = 0;
  updateJukeboxUI();
}"""

new_select_demo = """function selectDemoSong(idx) {
  demoPlayer.currentSongIdx = idx;
  document.querySelectorAll('.song-pill').forEach((p, i) => p.classList.toggle('active', i === idx));
  document.querySelectorAll('#shelfSongPills .synth-chip-btn').forEach((p, i) => p.classList.toggle('active', i === idx));
  demoPlayer.step = 0;
  updateJukeboxUI();
}"""

# Check if these need replacement
if old_play_demo in code:
    code = code.replace(old_play_demo, new_play_demo)
    print("Replaced playDemoSong with shelf-synced version.")
if old_pause_demo in code:
    code = code.replace(old_pause_demo, new_pause_demo)
    print("Replaced pauseDemoSong with shelf-synced version.")
if old_stop_demo in code:
    code = code.replace(old_stop_demo, new_stop_demo)
    print("Replaced stopDemoSong with shelf-synced version.")
if old_select_demo in code:
    code = code.replace(old_select_demo, new_select_demo)
    print("Replaced selectDemoSong with shelf-synced version.")

# 4. Remove duplicate handleUnifiedAction block if present
dup_act = """// Unified D-Pad and Screen Touch Handlers for ALL 8 Arcade Games
function handleUnifiedAction(act) {
  initAudio();
  if (activeGame === 'pacman') {
    if (act === 'up') { keyUp = true; keyDown = false; }
    else if (act === 'down') { keyDown = true; keyUp = false; }
    else if (act === 'left') { keyLeft = true; keyRight = false; }
    else if (act === 'right') { keyRight = true; keyLeft = false; }
    else if (act === 'action') { quickPlay(); }
  } else if (activeGame === 'cclimber') {
    if (act === 'up') climberStep('right', 'up');
    else if (act === 'down') climberStep('right', 'down');
    else if (act === 'left') climberState.col = Math.max(0, climberState.col - 1);
    else if (act === 'right') climberState.col = Math.min(3, climberState.col + 1);
    else if (act === 'action') climberStep('left', 'up');
  } else if (activeGame === 'dkong') {
    if (act === 'up') dkongClimbUp();
    else if (act === 'down') dkongClimbDown();
    else if (act === 'left') { dkongGame.mario.x = Math.max(20, dkongGame.mario.x - 8); dkongGame.mario.facing = 'left'; }
    else if (act === 'right') { dkongGame.mario.x = Math.min(220, dkongGame.mario.x + 8); dkongGame.mario.facing = 'right'; }
    else if (act === 'action') dkongJump();
  } else if (activeGame === 'galaga') {
    if (act === 'left') galagaGame.shipX = Math.max(16, galagaGame.shipX - 12);
    else if (act === 'right') galagaGame.shipX = Math.min(224, galagaGame.shipX + 12);
    else if (act === 'up' || act === 'action') galagaFire();
  } else if (activeGame === 'frogger') {
    if (act === 'up') froggerHop('up');
    else if (act === 'down') froggerHop('down');
    else if (act === 'left') froggerHop('left');
    else if (act === 'right') froggerHop('right');
  } else if (activeGame === 'asteroids') {
    if (act === 'left') asteroidsGame.ship.angle -= 0.3;
    else if (act === 'right') asteroidsGame.ship.angle += 0.3;
    else if (act === 'up') {
      asteroidsGame.ship.vx += Math.cos(asteroidsGame.ship.angle) * 0.8;
      asteroidsGame.ship.vy += Math.sin(asteroidsGame.ship.angle) * 0.8;
      playArcadeSfx('AST-THR');
    } else if (act === 'down') asteroidsHyperspace();
    else if (act === 'action') asteroidsFire();
  } else if (activeGame === 'tempest') {
    if (act === 'left') tempestGame.segment = (tempestGame.segment - 1 + 16) % 16;
    else if (act === 'right') tempestGame.segment = (tempestGame.segment + 1) % 16;
    else if (act === 'up') tempestSuperzapper();
    else if (act === 'action') tempestFire();
  } else if (activeGame === 'gyruss') {
    if (act === 'left') gyrussGame.angle -= 0.25;
    else if (act === 'right') gyrussGame.angle += 0.25;
    else if (act === 'action' || act === 'up') gyrussFire();
  }
}

const dpadU = document.getElementById('dpadUp');
if (dpadU) dpadU.onclick = () => handleUnifiedAction('up');
const dpadD = document.getElementById('dpadDown');
if (dpadD) dpadD.onclick = () => handleUnifiedAction('down');
const dpadL = document.getElementById('dpadLeft');
if (dpadL) dpadL.onclick = () => handleUnifiedAction('left');
const dpadR = document.getElementById('dpadRight');
if (dpadR) dpadR.onclick = () => handleUnifiedAction('right');

const btnQP = document.getElementById('btnQuickPlay');
if (btnQP) {
  const origQP = btnQP.onclick;
  btnQP.onclick = () => {
    if (activeGame === 'pacman') { if (typeof quickPlay === 'function') quickPlay(); }
    else handleUnifiedAction('action');
  };
}

// Screen Quadrant Click Steering
const screenBez = document.getElementById('screenBezel');
if (screenBez && typeof screenBez.addEventListener === 'function') {
  screenBez.addEventListener('click', (e) => {
    const rect = screenBez.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const cx = rect.width / 2;
    const cy = rect.height / 2;
    const dx = x - cx;
    const dy = y - cy;
    if (Math.abs(dx) > Math.abs(dy)) {
      handleUnifiedAction(dx > 0 ? 'right' : 'left');
    } else {
      handleUnifiedAction(dy > 0 ? 'down' : 'up');
    }
  });
}"""

if code.count(dup_act) > 1:
    code = code.replace(dup_act, "", 1)
    print("Removed duplicate handleUnifiedAction block.")

# 5. Insert ARCADE_MISSIONS, populateShelfSongPills, toggleScreenZoom, and deck wiring into additional_bindings
extra_wiring = """
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
// ON-SCREEN CONTROLLER DECK & KEY ILLUMINATION
// -------------------------------------------------------------------------
const cLeft = document.getElementById('ctrlBtnLeft');
if (cLeft) cLeft.onclick = () => handleUnifiedAction('left');
const cUp = document.getElementById('ctrlBtnUp');
if (cUp) cUp.onclick = () => handleUnifiedAction('up');
const cDown = document.getElementById('ctrlBtnDown');
if (cDown) cDown.onclick = () => handleUnifiedAction('down');
const cRight = document.getElementById('ctrlBtnRight');
if (cRight) cRight.onclick = () => handleUnifiedAction('right');
const cFire = document.getElementById('ctrlBtnFire');
if (cFire) cFire.onclick = () => handleUnifiedAction('action');
const cCoin = document.getElementById('ctrlBtnCoin');
if (cCoin) cCoin.onclick = () => insertCoin();
const cStart = document.getElementById('ctrlBtnStart');
if (cStart) cStart.onclick = () => start1P();
const cZoom = document.getElementById('ctrlBtnZoom');
if (cZoom) cZoom.onclick = () => toggleScreenZoom();
const cZoomCap = document.getElementById('btnZoomScreen');
if (cZoomCap) cZoomCap.onclick = () => toggleScreenZoom();

// Keyboard button illumination
window.addEventListener('keydown', (e) => {
  const k = e.key.toLowerCase();
  if (k === 'a' || e.key === 'ArrowLeft') { if (cLeft) cLeft.classList.add('pressed'); }
  if (k === 'd' || e.key === 'ArrowRight') { if (cRight) cRight.classList.add('pressed'); }
  if (k === 'w' || e.key === 'ArrowUp') { if (cUp) cUp.classList.add('pressed'); }
  if (k === 's' || e.key === 'ArrowDown') { if (cDown) cDown.classList.add('pressed'); }
  if (e.key === ' ' || e.key === 'Enter') { if (cFire) cFire.classList.add('pressed'); }
  if (k === '1' || k === 'c') { if (cCoin) cCoin.classList.add('pressed'); }
  if (k === '5' || k === 'p') { if (cStart) cStart.classList.add('pressed'); }
  if (k === 'z') { toggleScreenZoom(); }
});

window.addEventListener('keyup', (e) => {
  const k = e.key.toLowerCase();
  if (k === 'a' || e.key === 'ArrowLeft') { if (cLeft) cLeft.classList.remove('pressed'); }
  if (k === 'd' || e.key === 'ArrowRight') { if (cRight) cRight.classList.remove('pressed'); }
  if (k === 'w' || e.key === 'ArrowUp') { if (cUp) cUp.classList.remove('pressed'); }
  if (k === 's' || e.key === 'ArrowDown') { if (cDown) cDown.classList.remove('pressed'); }
  if (e.key === ' ' || e.key === 'Enter') { if (cFire) cFire.classList.remove('pressed'); }
  if (k === '1' || k === 'c') { if (cCoin) cCoin.classList.remove('pressed'); }
  if (k === '5' || k === 'p') { if (cStart) cStart.classList.remove('pressed'); }
});

// Initial population of pills & mission card
if (typeof populateShelfSongPills === 'function') populateShelfSongPills();
if (typeof updateMissionCard === 'function') updateMissionCard(activeGame || 'pacman');
"""

if "ARCADE_MISSIONS" not in code:
    code = code.replace('additional_bindings = """', 'additional_bindings = """' + extra_wiring)
    print("Injected extra_wiring into additional_bindings.")

with open("tools/build_hardware_template.py", "w") as f:
    f.write(code)

print("Saved updated tools/build_hardware_template.py successfully!")
