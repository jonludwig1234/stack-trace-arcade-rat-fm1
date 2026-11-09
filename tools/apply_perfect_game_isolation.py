import re

with open("tools/build_hardware_template.py", "r") as f:
    code = f.read()

# 1. Update the replacement for ensurePastBoot & Pac-Man controls to include safeTimeout & activeGame guard
old_pacman_controls = """function ensurePastBoot() {
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

new_pacman_controls = """let activeGameTimeouts = [];
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
  }
}

function start1P() {
  initAudio();
  if (activeGame === 'pacman') {
    ensurePastBoot();
    startPulseFrames = 12;
    keyStart = true;
    safeTimeout(() => { keyStart = false; }, 200);
  } else if (activeGame === 'cclimber') {
    climberState.floor = 42;
    climberState.score = 14850;
    playArcadeSfx('WARP');
  }
}

function quickPlay() {
  initAudio();
  if (activeGame === 'cclimber') {
    climberStep('right', 'up');
    return;
  }
  setMode('arcade');
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

  document.getElementById('hudStatus').className = 'hud-badge';
  document.getElementById('hudStatus').textContent = '● PLAYING: LIVE!';
}"""

# 2. Update keyboard listener in simulator_template.html.bak to prevent keys from falling through across games
old_keyboard_block = """  if (activeGame === 'cclimber') {
    if (k === 'w') { climberStep('left', 'up'); e.preventDefault(); return; }
    else if (k === 's') { climberStep('left', 'down'); e.preventDefault(); return; }
    else if (e.key === 'ArrowUp') { climberStep('right', 'up'); e.preventDefault(); return; }
    else if (e.key === 'ArrowDown') { climberStep('right', 'down'); e.preventDefault(); return; }
    else if (k === 'a' || e.key === 'ArrowLeft') { climberState.col = Math.max(0, climberState.col - 1); e.preventDefault(); return; }
    else if (k === 'd' || e.key === 'ArrowRight') { climberState.col = Math.min(3, climberState.col + 1); e.preventDefault(); return; }
  }

  if (e.key === 'ArrowUp' || k === 'w') { keyUp = true; keyDown = false; e.preventDefault(); }
  else if (e.key === 'ArrowDown' || k === 's') { keyDown = true; keyUp = false; e.preventDefault(); }
  else if (e.key === 'ArrowLeft' || k === 'a') { keyLeft = true; keyRight = false; e.preventDefault(); }
  else if (e.key === 'ArrowRight' || k === 'd') { keyRight = true; keyLeft = false; e.preventDefault(); }
  else if (k === '1' || k === 'c') { insertCoin(); }
  else if (k === '5' || k === 'p' || e.key === 'Enter') { start1P(); }
  else if (e.key === ' ') { quickPlay(); e.preventDefault(); }"""

new_keyboard_block = """  if (currentMode === 'tour') {
    if (e.key === ' ' || e.key === 'Enter' || k === '1' || k === 'c') {
      launchCurrentTourGame();
      e.preventDefault();
      return;
    }
    if (e.key === 'ArrowRight' || k === 'd' || k === 'n') {
      nextTourGame();
      e.preventDefault();
      return;
    }
    if (e.key === 'ArrowLeft' || k === 'a' || k === 'p') {
      prevTourGame();
      e.preventDefault();
      return;
    }
    e.preventDefault();
    return;
  }

  if (activeGame === 'cclimber') {
    if (k === 'w') { climberStep('left', 'up'); e.preventDefault(); return; }
    else if (k === 's') { climberStep('left', 'down'); e.preventDefault(); return; }
    else if (e.key === 'ArrowUp') { climberStep('right', 'up'); e.preventDefault(); return; }
    else if (e.key === 'ArrowDown') { climberStep('right', 'down'); e.preventDefault(); return; }
    else if (k === 'a' || e.key === 'ArrowLeft') { climberState.col = Math.max(0, climberState.col - 1); e.preventDefault(); return; }
    else if (k === 'd' || e.key === 'ArrowRight') { climberState.col = Math.min(3, climberState.col + 1); e.preventDefault(); return; }
    if (k === '1' || k === 'c' || k === '5' || k === 'p' || e.key === 'Enter' || e.key === ' ') {
      playArcadeSfx('WARP');
      e.preventDefault();
      return;
    }
    return;
  }

  // Pac-Man specific keyboard routing (strictly isolated to Pac-Man)
  if (activeGame === 'pacman') {
    if (e.key === 'ArrowUp' || k === 'w') { keyUp = true; keyDown = false; e.preventDefault(); }
    else if (e.key === 'ArrowDown' || k === 's') { keyDown = true; keyUp = false; e.preventDefault(); }
    else if (e.key === 'ArrowLeft' || k === 'a') { keyLeft = true; keyRight = false; e.preventDefault(); }
    else if (e.key === 'ArrowRight' || k === 'd') { keyRight = true; keyLeft = false; e.preventDefault(); }
    else if (k === '1' || k === 'c') { insertCoin(); }
    else if (k === '5' || k === 'p' || e.key === 'Enter') { start1P(); }
    else if (e.key === ' ') { quickPlay(); e.preventDefault(); }
  }"""

# 3. Update mainLoop CPU execution and HUD update to strictly isolate Pac-Man
old_mainloop_cpu_block = """  // During boot test (< frame 305), run CPU at 5x speed so game boots in < 0.6 seconds!
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

new_mainloop_cpu_block = """  // Pac-Man CPU execution: STRICTLY isolated to when Pac-Man is the selected active game!
  const isPacmanRunning = ((currentMode === 'arcade' || currentMode === 'glitch' || currentMode === 'rewind') && activeGame === 'pacman') ||
                          (currentMode === 'tour' && tourState.games[tourState.gameIdx] && tourState.games[tourState.gameIdx].id === 'pacman');

  if (isPacmanRunning) {
    if (animTick < 320) {
      ensurePastBoot();
    } else {
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
  } else {
    // Pac-Man is NOT running: completely silence WSG wavetable audio voices so NO sound leaks!
    for (let ch = 0; ch < 3; ch++) {
      if (wsgVoices && wsgVoices[ch]) {
        wsgVoices[ch].vol = 0;
        wsgVoices[ch].freq = 0;
      }
    }
  }

  // Update HUD info for active game
  if (activeGame === 'pacman') {
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
    }
  } else if (activeGame === 'cclimber') {
    document.getElementById('hudCredits').textContent = `FLOOR: ${climberState.floor}F`;
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = `● SCORE: ${climberState.score}`;
  }"""

# 4. Update stopCurrentGame to cancel active timeouts and silence WSG completely
stop_current_game_code = """function stopCurrentGame() {
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

  // 3. Complete audio silencing: mute all WSG synth channels & stop demo songs
  if (typeof stopDemoSong === 'function') {
    stopDemoSong();
  } else if (typeof pauseDemoSong === 'function') {
    pauseDemoSong();
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
  }

  // 5. Immediately clear screen display buffer and canvas
  clearScreen();
}"""

# Let's inspect where old_pacman_controls and old_boot_loop were being handled in build_hardware_template.py
# In build_hardware_template.py, we had:
# script_body = script_body.replace(old_boot_loop, new_boot_loop)
# Let's replace the boot loop replacement with the full mainloop replacement:
assert 'script_body.replace(old_boot_loop, new_boot_loop)' in code

# Replace old boot loop replacement with full mainloop cpu block replacement
code = code.replace(
    '''    old_boot_loop = """  // During boot test (< frame 305), run CPU at 5x speed so game boots in < 0.6 seconds!
  if (animTick < 305) {
    for (let fast = 0; fast < 5 && animTick < 305; fast++) {
      stepCpuFrame();
    }
  } else {"""

    new_boot_loop = """  // Instant 0ms boot: fast-forward past memory self-test immediately
  if (animTick < 320) {
    ensurePastBoot();
  } else {"""
    script_body = script_body.replace(old_boot_loop, new_boot_loop)''',
    f'''    old_cpu_block = """{old_mainloop_cpu_block}"""
    new_cpu_block = """{new_mainloop_cpu_block}"""
    script_body = script_body.replace(old_cpu_block, new_cpu_block)

    old_kbd = """{old_keyboard_block}"""
    new_kbd = """{new_keyboard_block}"""
    script_body = script_body.replace(old_kbd, new_kbd)'''
)

# Update ensurePastBoot block replacement in build_hardware_template.py
old_ensure_replace = '''    script_body = script_body.replace(
        """function ensurePastBoot() {
  let safety = 0;
  while (animTick < 305 && safety < 350) {
    stepCpuFrame();
    safety++;
  }
}""",
        """function ensurePastBoot() {
  let safety = 0;
  while (animTick < 320 && safety < 350) {
    stepCpuFrame();
    safety++;
  }
}"""
    )'''

new_ensure_replace = f'''    old_ctrls = """{old_pacman_controls}"""
    new_ctrls = """{new_pacman_controls}"""
    script_body = script_body.replace(old_ctrls, new_ctrls)'''

assert old_ensure_replace in code, "old_ensure_replace not found in build_hardware_template.py!"
code = code.replace(old_ensure_replace, new_ensure_replace)

# Update stopCurrentGame in new_switch_full
old_stop_in_switch = """function stopCurrentGame() {
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
}"""

assert old_stop_in_switch in code, "old_stop_in_switch not found in build_hardware_template.py!"
code = code.replace(old_stop_in_switch, stop_current_game_code)

with open("tools/build_hardware_template.py", "w") as f:
    f.write(code)

print("Successfully applied perfect game isolation to tools/build_hardware_template.py!")
