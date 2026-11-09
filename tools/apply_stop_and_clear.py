import re

with open("tools/build_hardware_template.py", "r") as f:
    code = f.read()

# 1. Update tour block in new_games_block (toggleTourDemo, nextTourGame, prevTourGame, launchCurrentTourGame)
old_tour_block = """function toggleTourDemo() {
  initAudio();
  if (currentMode === 'tour') setMode('arcade'); else setMode('tour');
}

function nextTourGame() {
  initAudio();
  tourState.frameInGame = 0;
  tourState.gameIdx = (tourState.gameIdx + 1) % tourState.games.length;
  playArcadeSfx('WARP');
}

function prevTourGame() {
  initAudio();
  tourState.frameInGame = 0;
  tourState.gameIdx = (tourState.gameIdx - 1 + tourState.games.length) % tourState.games.length;
  playArcadeSfx('WARP');
}

function launchCurrentTourGame() {
  const g = tourState.games[tourState.gameIdx];
  tourState.active = false;
  if (g.id === 'cclimber') switchActiveGame('cclimber'); else switchActiveGame('pacman');
  setMode('arcade');
  ensurePastBoot();
  insertCoin();
  setTimeout(start1P, 200);
}"""

new_tour_block = """function toggleTourDemo() {
  initAudio();
  stopCurrentGame();
  clearScreen('TOUR DEMO');
  if (currentMode === 'tour') {
    setMode('arcade');
    switchActiveGame(activeGame);
  } else {
    setMode('tour');
    renderTourDemo();
  }
}

function nextTourGame() {
  initAudio();
  stopCurrentGame();
  tourState.frameInGame = 0;
  tourState.gameIdx = (tourState.gameIdx + 1) % tourState.games.length;
  currentGameIdx = tourState.gameIdx;
  const enc = document.getElementById('encSelect');
  if (enc && enc.style && enc.style.setProperty) {
    enc.style.setProperty('--angle', `${(currentGameIdx / tourState.games.length * 270) - 135}deg`);
  }
  clearScreen(tourState.games[tourState.gameIdx].title);
  playArcadeSfx('WARP');
  renderTourDemo();
}

function prevTourGame() {
  initAudio();
  stopCurrentGame();
  tourState.frameInGame = 0;
  tourState.gameIdx = (tourState.gameIdx - 1 + tourState.games.length) % tourState.games.length;
  currentGameIdx = tourState.gameIdx;
  const enc = document.getElementById('encSelect');
  if (enc && enc.style && enc.style.setProperty) {
    enc.style.setProperty('--angle', `${(currentGameIdx / tourState.games.length * 270) - 135}deg`);
  }
  clearScreen(tourState.games[tourState.gameIdx].title);
  playArcadeSfx('WARP');
  renderTourDemo();
}

function launchCurrentTourGame() {
  const g = tourState.games[tourState.gameIdx];
  tourState.active = false;
  stopCurrentGame();
  clearScreen(g.title);
  if (g.id === 'cclimber') switchActiveGame('cclimber'); else switchActiveGame('pacman');
  setMode('arcade');
  ensurePastBoot();
  insertCoin();
  setTimeout(start1P, 200);
}"""

assert old_tour_block in code, "old_tour_block not found in build_hardware_template.py!"
code = code.replace(old_tour_block, new_tour_block)

# 2. Update stepGame in additional_bindings
old_step_game = """function stepGame(dir) {
  currentGameIdx = (currentGameIdx + dir + gameList.length) % gameList.length;
  if (encSelect && encSelect.style && encSelect.style.setProperty) encSelect.style.setProperty('--angle', `${(currentGameIdx / gameList.length * 270) - 135}deg`);
  const g = gameList[currentGameIdx];
  if (g === 'pacman' || g === 'cclimber') switchActiveGame(g);
  else {
    if (currentMode !== 'tour') toggleTourDemo();
    tourState.gameIdx = currentGameIdx;
    tourState.frameInGame = 0;
  }
}"""

new_step_game = """function stepGame(dir) {
  // First stop current game and clear screen
  stopCurrentGame();

  currentGameIdx = (currentGameIdx + dir + gameList.length) % gameList.length;
  if (encSelect && encSelect.style && encSelect.style.setProperty) {
    encSelect.style.setProperty('--angle', `${(currentGameIdx / gameList.length * 270) - 135}deg`);
  }
  const g = gameList[currentGameIdx];
  clearScreen(g.toUpperCase());
  if (g === 'pacman' || g === 'cclimber') {
    switchActiveGame(g);
  } else {
    if (currentMode !== 'tour') setMode('tour');
    tourState.gameIdx = currentGameIdx;
    tourState.frameInGame = 0;
    renderTourDemo();
  }
}"""

assert old_step_game in code, "old_step_game not found in build_hardware_template.py!"
code = code.replace(old_step_game, new_step_game)

# 3. In script_body replacements:
old_switch_game_full = """function switchActiveGame(gameId) {
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

new_switch_game_full = """// -------------------------------------------------------------------------
// GAME CONTROL & SCREEN BLANKING: STOP CURRENT GAME & CLEAR SCREEN
// -------------------------------------------------------------------------
function clearScreen(label) {
  if (typeof arcadeBuf !== 'undefined' && arcadeBuf) {
    arcadeBuf.fill(0xff000000);
  }
  if (typeof buf32 !== 'undefined' && buf32) {
    buf32.fill(0xff000000);
  }
  if (typeof ctx !== 'undefined' && ctx) {
    ctx.save();
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, 240, 240);
    if (label) {
      ctx.fillStyle = '#00ff66';
      ctx.font = 'bold 11px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(label.toUpperCase(), 120, 115);
      ctx.fillStyle = '#556677';
      ctx.font = '8px monospace';
      ctx.fillText('STANDBY · READY', 120, 132);
      ctx.textAlign = 'left';
    }
    ctx.restore();
  }
}

function stopCurrentGame() {
  // 1. Release all active input keys, d-pad, and pulse flags
  keyUp = false;
  keyDown = false;
  keyLeft = false;
  keyRight = false;
  keyCoin = false;
  keyStart = false;
  coinPulseFrames = 0;
  startPulseFrames = 0;
  isRewinding = false;

  // 2. Silence all synthesizer audio voices & stop demo song playback
  if (typeof stopDemoSong === 'function') {
    stopDemoSong();
  } else if (typeof pauseDemoSong === 'function') {
    pauseDemoSong();
  }
  if (typeof wsgVoices !== 'undefined' && wsgVoices) {
    for (let ch = 0; ch < 3; ch++) {
      if (wsgVoices[ch]) wsgVoices[ch].vol = 0;
    }
  }

  // 3. Reset rewind ring buffer and game states
  if (typeof rewindBuffer !== 'undefined' && rewindBuffer) {
    rewindBuffer.length = 0;
  }
  if (typeof tourState !== 'undefined' && tourState) {
    tourState.frameInGame = 0;
  }
  if (typeof climberState !== 'undefined' && climberState) {
    climberState.animTick = 0;
  }

  // 4. Immediately clear screen display buffer and canvas
  clearScreen();
}

function switchActiveGame(gameId) {
  initAudio();
  // FIRST: stop current game and clear screen
  stopCurrentGame();

  activeGame = gameId;
  currentMode = 'arcade';
  document.querySelectorAll('.mode-tag').forEach(t => t.classList.toggle('active', t.dataset.mode === 'arcade'));
  const btnPac = document.getElementById('btnGamePacman');
  const btnClimb = document.getElementById('btnGameClimber');
  const btnTour = document.getElementById('btnGameTour') || document.getElementById('btnTourAllRoms');
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
    climberState.floor = 42;
    climberState.score = 14850;
    climberState.animTick = 0;
    renderCrazyClimber();
  } else {
    document.getElementById('engineStatus').textContent = 'PAC-MAN (60 FPS Z80 + WSG)';
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● PAC-MAN ACTIVE';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Controls: <b>WASD</b> or <b>Arrow Keys</b> or <b>On-Screen D-Pad</b>';
    ensurePastBoot();
    renderArcadeFrame();
  }
}"""

# Remove old partial replacement from upgrade_boot_and_quality.py if present
code = re.sub(r'old_switch_game\s*=\s*""".*?"""\s*new_switch_game\s*=\s*""".*?"""\s*script_body\s*=\s*script_body\.replace\(old_switch_game,\s*new_switch_game\)', '', code, flags=re.DOTALL)

# Add full switchActiveGame replacement and setMode update
switch_replacement_code = '''
    # Replace switchActiveGame with full stopCurrentGame and clearScreen logic
    old_switch_full = """''' + old_switch_game_full + '''"""
    new_switch_full = """''' + new_switch_game_full + '''"""
    script_body = script_body.replace(old_switch_full, new_switch_full)

    # In setMode, stop current game when changing mode
    script_body = script_body.replace(
        "function setMode(mode) {\\n  currentMode = mode;",
        "function setMode(mode) {\\n  if (currentMode !== mode) stopCurrentGame();\\n  currentMode = mode;"
    )
'''

target_pos = code.find('old_init = """// Initialize Demo Songs UI')
if target_pos != -1:
    code = code[:target_pos] + switch_replacement_code + "\n    " + code[target_pos:]
else:
    raise ValueError("Target position for switch replacement not found!")

with open("tools/build_hardware_template.py", "w") as f:
    f.write(code)

print("Successfully applied stop-and-clear upgrades to tools/build_hardware_template.py!")
