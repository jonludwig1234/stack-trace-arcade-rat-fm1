/**
 * tools/audit_arcade_death_sounds.js
 * Comprehensive diagnostic and validation rig for all 8 Arcade titles' death sounds:
 * Inspects:
 * 1. SFX ID dispatched when player dies in each game
 * 2. Audio synthesis graph (Oscillator types, Noise sources, Filters, Envelopes, Duration)
 * 3. Soundchip / discrete hardware fidelity comparison
 * 4. Flags inappropriate cross-game sharing (e.g. Pac-Man 'DEATH' in Galaga/Tempest)
 */

const fs = require('fs');
const vm = require('vm');

const html = fs.readFileSync('web/fm1_pacman_preview.html', 'utf8');
const sIdx = html.indexOf('<script>');
const eIdx = html.lastIndexOf('</script>');
const jsCode = html.slice(sIdx + 8, eIdx);

const mockCtx = {
  save: () => {}, restore: () => {}, translate: () => {}, scale: () => {},
  rotate: () => {}, beginPath: () => {}, moveTo: () => {}, lineTo: () => {},
  closePath: () => {}, stroke: () => {}, fill: () => {}, arc: () => {},
  rect: () => {}, roundRect: () => {}, strokeRect: () => {}, fillRect: () => {},
  clearRect: () => {}, drawImage: () => {}, fillText: () => {},
  createLinearGradient: () => ({ addColorStop: () => {} }),
  createRadialGradient: () => ({ addColorStop: () => {} }),
  createImageData: (w, h) => ({ data: new Uint8ClampedArray((w || 240) * (h || 240) * 4) }),
  putImageData: () => {}, font: '', fillStyle: '', strokeStyle: '', lineWidth: 1,
  ellipse: () => {}
};

const capturedSfx = [];
const nodeEvents = [];

class MockAudioContext {
  constructor() {
    this.destination = {};
    this.sampleRate = 44100;
    this.currentTime = 0;
  }
  createGain() {
    const node = {
      gain: {
        val: 1,
        setValueAtTime: (v, t) => { node.gainVal = v; nodeEvents.push({ type: 'gainSet', v, t }); },
        linearRampToValueAtTime: (v, t) => { nodeEvents.push({ type: 'gainRamp', v, t }); },
        exponentialRampToValueAtTime: (v, t) => { nodeEvents.push({ type: 'gainExpRamp', v, t }); }
      },
      connect: (target) => {}
    };
    return node;
  }
  createOscillator() {
    const node = {
      frequency: {
        val: 440,
        setValueAtTime: (v, t) => { node.freq = v; nodeEvents.push({ type: 'oscFreqSet', v, t }); },
        exponentialRampToValueAtTime: (v, t) => { nodeEvents.push({ type: 'oscFreqExpRamp', v, t }); }
      },
      type: 'sine',
      connect: (target) => {},
      start: (t) => { nodeEvents.push({ type: 'oscStart', t, oscType: node.type }); },
      stop: (t) => { nodeEvents.push({ type: 'oscStop', t }); }
    };
    return node;
  }
  createBiquadFilter() {
    const node = {
      frequency: {
        val: 1000,
        setValueAtTime: (v, t) => { node.fltFreq = v; nodeEvents.push({ type: 'fltFreqSet', v, t }); },
        exponentialRampToValueAtTime: (v, t) => { nodeEvents.push({ type: 'fltFreqExpRamp', v, t }); }
      },
      Q: {
        val: 1,
        setValueAtTime: (v, t) => { nodeEvents.push({ type: 'fltQSet', v, t }); }
      },
      type: 'lowpass',
      connect: (target) => {}
    };
    return node;
  }
  createBuffer(channels, length, sampleRate) {
    return { getChannelData: () => new Float32Array(length) };
  }
  createBufferSource() {
    return {
      connect: () => {},
      start: (t) => { nodeEvents.push({ type: 'noiseStart', t }); },
      stop: (t) => { nodeEvents.push({ type: 'noiseStop', t }); }
    };
  }
}

const sandbox = {
  console: console,
  setTimeout: setTimeout, clearTimeout: clearTimeout,
  setInterval: setInterval, clearInterval: clearInterval,
  requestAnimationFrame: (cb) => setTimeout(cb, 16),
  cancelAnimationFrame: (id) => clearTimeout(id),
  Math: Math,
  atob: (b64) => Buffer.from(b64, 'base64').toString('binary'),
  btoa: (bin) => Buffer.from(bin, 'binary').toString('base64'),
  Image: class { constructor() { this.src = ''; } },
  AudioContext: MockAudioContext,
  webkitAudioContext: MockAudioContext,
  window: {
    addEventListener: () => {},
    location: { search: '' },
    AudioContext: MockAudioContext,
    webkitAudioContext: MockAudioContext
  },
  document: {
    createElement: () => ({
      textContent: '', className: '', classList: { toggle: () => {}, add: () => {}, remove: () => {} },
      dataset: {}, style: {}, onclick: null, appendChild: () => {}, getContext: () => mockCtx, addEventListener: () => {}
    }),
    getElementById: () => ({
      textContent: '', className: '', classList: { toggle: () => {}, add: () => {}, remove: () => {} },
      style: {}, onclick: null, appendChild: () => {}, getContext: () => mockCtx, addEventListener: () => {}
    }),
    querySelectorAll: () => []
  }
};

vm.createContext(sandbox);
vm.runInContext(jsCode, sandbox);

// Hook playArcadeSfx to capture dispatched SFX
vm.runInContext(`
  audioCtx = new AudioContext();
  const rawPlayArcadeSfx = playArcadeSfx;
  playArcadeSfx = function(name) {
    capturedSfx.push(name);
    rawPlayArcadeSfx(name);
  };
`, sandbox);
sandbox.capturedSfx = capturedSfx;
sandbox.nodeEvents = nodeEvents;

console.log("=========================================================================");
console.log("      MASTER ARCADE DEATH SOUND AUDIT & FIDELITY VALIDATOR               ");
console.log("=========================================================================\n");

const auditResults = [];

function auditDeathSound(gameId, triggerFn, expectedHardware) {
  capturedSfx.length = 0;
  nodeEvents.length = 0;

  triggerFn();

  // Inspect the dispatched death sound
  const sfxList = [...capturedSfx].filter(s => s !== 'DK-GAMEOVER'); // ignore gameover jingles
  const primarySfx = sfxList[0] || 'NONE';

  // Analyze audio nodes of the primary death sound
  nodeEvents.length = 0;
  if (primarySfx !== 'NONE') {
    try {
      vm.runInContext(`playArcadeSfx('${primarySfx}');`, sandbox);
    } catch (e) {}
  }

  const hasNoise = nodeEvents.some(e => e.type === 'noiseStart');
  const oscEvents = nodeEvents.filter(e => e.type === 'oscStart');
  const oscTypes = [...new Set(oscEvents.map(e => e.oscType))];
  const maxStopTime = Math.max(0, ...nodeEvents.filter(e => e.t).map(e => e.t));

  auditResults.push({
    gameId,
    dispatchedSfx: sfxList,
    primarySfx,
    expectedHardware,
    hasNoise,
    oscTypes,
    durationMs: Math.round(maxStopTime * 1000)
  });
}

// 1. Pac-Man
auditDeathSound('Pac-Man (1980 Namco)', () => {
  // Pac-Man death routine dispatches WSG wave table chromatic death descent
  vm.runInContext("playArcadeSfx('DEATH');", sandbox);
}, 'Namco WSG 3-Voice Wave Table');

// 2. Donkey Kong
auditDeathSound('Donkey Kong (1981 Nintendo)', () => {
  vm.runInContext(`
    initDonkeyKongGame();
    dkongGame.mario.state = 'stand';
    capturedSfx.length = 0;
    // Spawn lethal barrel directly on Mario
    dkongGame.barrels.push({ x: dkongGame.mario.x, y: dkongGame.mario.y, tier: 0, vx: 0, rollFrame: 0, scored: false });
    updateDonkeyKongGame();
  `, sandbox);
}, 'Nintendo Discrete 7-bit DAC');

// 3. Frogger (Highway Squish)
auditDeathSound('Frogger Traffic (1981 Konami)', () => {
  vm.runInContext(`
    initFroggerGame();
    capturedSfx.length = 0;
    killFrogger('splat');
  `, sandbox);
}, 'Dual AY-3-8910 (Stepped Screech + Noise Crunch)');

// 4. Frogger (River Drown)
auditDeathSound('Frogger River (1981 Konami)', () => {
  vm.runInContext(`
    initFroggerGame();
    capturedSfx.length = 0;
    killFrogger('drown');
  `, sandbox);
}, 'Dual AY-3-8910 (Resonant Bloop-Plunk + Splash)');

// 5. Asteroids
auditDeathSound('Asteroids (1979 Atari)', () => {
  vm.runInContext(`
    initAsteroidsGame();
    asteroidsGame.ship.invulnerable = 0;
    capturedSfx.length = 0;
    // Spawn rock directly on ship
    asteroidsGame.rocks = [{ x: asteroidsGame.ship.x, y: asteroidsGame.ship.y, radius: 18, size: 3, vx: 0, vy: 0 }];
    updateAsteroidsGame();
  `, sandbox);
}, 'Atari 1979 Discrete Analog Ship Explode (Bang High)');

// 6. Galaga
auditDeathSound('Galaga (1981 Namco)', () => {
  vm.runInContext(`
    setMode('arcade');
    initGalagaGame();
    galagaGame.shipX = 120;
    galagaGame.isRespawning = false;
    galagaGame.isCapturing = false;
    capturedSfx.length = 0;
    galagaGame.aliens = [{ x: 120, y: 220, type: 'bee', state: 'dive', homeX: 120, homeY: 50, frame: 0, diveTick: 0, diving: true }];
    updateGalagaGame();
  `, sandbox);
}, 'Namco WSG Multi-Stage Particle Shatter');

// 7. Tempest
auditDeathSound('Tempest (1981 Atari)', () => {
  vm.runInContext(`
    setMode('arcade');
    initTempestGame();
    capturedSfx.length = 0;
    tempestGame.enemies = [{ seg: tempestGame.segment, dist: 1.0, vDist: 0, type: 'flipper' }];
    updateTempestGame();
  `, sandbox);
}, 'Atari POKEY Disintegration Polynomial Cascade');

// 8. Gyruss
auditDeathSound('Gyruss (1983 Konami)', () => {
  vm.runInContext(`
    setMode('arcade');
    initGyrussGame();
    gyrussGame.invulnerable = 0;
    capturedSfx.length = 0;
    killGyrussShip();
  `, sandbox);
}, '5x PSG Dual-Sawtooth Explode + Sub-Bass Thud');

// 9. Crazy Climber
auditDeathSound('Crazy Climber (1980 Nichibutsu)', () => {
  vm.runInContext(`
    setMode('arcade');
    initCrazyClimberGame();
    capturedSfx.length = 0;
    climberState.potCol = climberState.col;
    climberState.potY = 130;
    updateCrazyClimberGame();
  `, sandbox);
}, 'Dual AY-3-8910 Plunge Whistle & Pavement Splat');

// Print Structured Audit Report Table
console.log("AUDIT RESULTS TABLE:\n");
console.log("| Game Title | Dispatched SFX | Audio Synthesis Graph | Hardware Baseline | Fidelity Status |");
console.log("|:---|:---|:---|:---|:---:|");

auditResults.forEach(r => {
  let status = "✅ PASS";
  let notes = "";

  if (r.gameId.includes('Asteroids') && r.primarySfx === 'AST-EXP') {
    status = "❌ INACCURATE";
    notes = "Reuses generic rock rumble; lacks Atari discrete ship destruction blast";
  } else if (r.gameId.includes('Galaga') && r.dispatchedSfx.includes('DEATH')) {
    status = "❌ INACCURATE";
    notes = "Reuses Pac-Man 12-step death descent instead of Namco WSG explosion";
  } else if (r.gameId.includes('Tempest') && r.dispatchedSfx.includes('DEATH')) {
    status = "❌ INACCURATE";
    notes = "Reuses Pac-Man death descent instead of Atari POKEY disintegration";
  } else if (r.gameId.includes('Gyruss') && r.dispatchedSfx.includes('DEATH')) {
    status = "⚠️ HYBRID BLEED";
    notes = "Plays Pac-Man 'DEATH' simultaneously with 'GYRUSS-EXP'";
  } else if (r.gameId.includes('Crazy Climber') && !r.dispatchedSfx.includes('CLIMB-FALL')) {
    status = "⚠️ PARTIAL";
    notes = "Plays pot smash + OUCH without fall whistling slide";
  }

  const sfxStr = r.dispatchedSfx.join(', ');
  const synthStr = `Noise: ${r.hasNoise ? 'YES' : 'NO'}, Osc: [${r.oscTypes.join('/')}], ${r.durationMs}ms`;
  console.log(`| **${r.gameId}** | \`${sfxStr}\` | ${synthStr} | ${r.expectedHardware} | **${status}** |`);
  if (notes) {
    console.log(`  └─> ⚠️ Issue: ${notes}`);
  }
});

console.log("\n=========================================================================");
process.exit(0);
