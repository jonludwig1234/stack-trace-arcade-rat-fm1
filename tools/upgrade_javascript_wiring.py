import re

print("=== INJECTING UPGRADED JAVASCRIPT WIRING ===")

with open("tools/build_hardware_template.py", "r") as f:
    content = f.read()

# 1. Update Crazy Climber autonomous attract AI in renderCrazyClimber
old_cc_end = """  // Left & Right Limestone Art-Deco Pilasters"""
new_cc_ai = """  // Autonomous Attract Tour Mode Climbing AI
  if (currentMode === 'tour') {
    if (tick % 24 < 12) climberStep('left', 'up');
    else climberStep('right', 'up');
    if (climberState.potCol === climberState.col && climberState.potY > 50 && climberState.potY < 150) {
      climberState.col = (climberState.col + 1) % 4;
    }
  }

  // Left & Right Limestone Art-Deco Pilasters"""

if old_cc_end in content and "Autonomous Attract Tour Mode Climbing AI" not in content:
    content = content.replace(old_cc_end, new_cc_ai)
    print("Added autonomous attract AI to Crazy Climber.")

# 2. Update renderTourHud with countdown and pulsing prompt
old_hud_target = """function renderTourHud(game, f) {
  // Semi-Transparent HUD Bar at top
  ctx.fillStyle = 'rgba(6, 9, 14, 0.88)';
  ctx.fillRect(0, 0, 240, 22);

  ctx.fillStyle = '#f5a623';
  ctx.font = 'bold 10px monospace';
  ctx.fillText(game.title, 8, 15);

  ctx.fillStyle = '#00ff66';
  ctx.font = '9px monospace';
  ctx.fillText(game.year, 150, 15);

  // Bottom Technical Telemetry & Arcade Hardware Badge
  ctx.fillStyle = 'rgba(6, 9, 14, 0.90)';
  ctx.fillRect(0, 220, 240, 20);

  ctx.fillStyle = '#00e5ff';
  ctx.font = 'bold 8px monospace';
  ctx.fillText(`HW: ${game.cpu} · ${game.sound}`, 8, 233);
}"""

new_hud_target = """function renderTourHud(game, f) {
  // Semi-Transparent HUD Bar at top
  ctx.fillStyle = 'rgba(6, 9, 14, 0.92)';
  ctx.fillRect(0, 0, 240, 26);

  ctx.fillStyle = '#f5a623';
  ctx.font = 'bold 10px monospace';
  ctx.fillText(game.title, 8, 14);

  // Countdown timer until next game
  const fRem = tourState.framesPerGame - (f % tourState.framesPerGame);
  const secRem = Math.ceil(fRem / 60);
  ctx.fillStyle = '#00ff66';
  ctx.font = '8px monospace';
  ctx.fillText(`NEXT IN ${secRem}s`, 172, 14);

  // Animated green progress bar
  ctx.fillStyle = 'rgba(0, 255, 102, 0.25)';
  ctx.fillRect(8, 20, 224, 3);
  ctx.fillStyle = '#00ff66';
  ctx.fillRect(8, 20, 224 * (1 - fRem / tourState.framesPerGame), 3);

  // Update shelf tour timer if element exists
  const stTag = document.getElementById('shelfTourTimer');
  if (stTag) stTag.textContent = `${game.title} (NEXT IN ${secRem}s)`;

  // Bottom Technical Telemetry & Pulsing Prompt
  ctx.fillStyle = 'rgba(6, 9, 14, 0.92)';
  ctx.fillRect(0, 214, 240, 26);

  ctx.fillStyle = '#00e5ff';
  ctx.font = 'bold 8px monospace';
  ctx.fillText(`HW: ${game.cpu}`, 8, 225);

  const pulse = Math.sin(f * 0.15) > 0;
  ctx.fillStyle = pulse ? '#fffa65' : '#ffffff';
  ctx.font = 'bold 9px monospace';
  ctx.fillText('⚡ TAP / SPACE TO PLAY NOW!', 34, 236);
}"""

if old_hud_target in content:
    content = content.replace(old_hud_target, new_hud_target)
    print("Upgraded renderTourHud with countdown and pulsing prompt.")

# 3. Add Mission Cards definition & populateShelfSongPills
extra_js = """
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
"""

if "ARCADE_MISSIONS" not in content:
    idx_script = content.find("<script>")
    content = content[:idx_script + 8] + "\n" + extra_js + "\n" + content[idx_script + 8:]
    print("Injected ARCADE_MISSIONS, populateShelfSongPills, and toggleScreenZoom.")

# 4. Update switchActiveGame to call updateMissionCard
old_switch_hook = "activeGame = gameId;"
new_switch_hook = "activeGame = gameId;\n  if (typeof updateMissionCard === 'function') updateMissionCard(gameId);"
if old_switch_hook in content and "updateMissionCard(gameId)" not in content:
    content = content.replace(old_switch_hook, new_switch_hook, 1)
    print("Hooked updateMissionCard into switchActiveGame.")

# 5. Wire the on-screen controller deck and keypress illumination
deck_wiring = """
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

// Populate shelf pills and initial mission card
if (typeof populateShelfSongPills === 'function') populateShelfSongPills();
if (typeof updateMissionCard === 'function') updateMissionCard(activeGame || 'pacman');
"""

if "ctrlBtnLeft" not in content:
    idx_last_script = content.rfind("</script>")
    content = content[:idx_last_script] + "\n" + deck_wiring + "\n" + content[idx_last_script:]
    print("Injected controller deck wiring and keyboard illumination.")

with open("tools/build_hardware_template.py", "w") as f:
    f.write(content)

print("build_hardware_template.py updated with all JavaScript wiring!")
