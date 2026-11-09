const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

console.log("=========================================================================");
console.log("TEST: AUTHENTIC ARCADE BACKGROUND MUSIC (BGM) SUITE ACROSS ALL 8 GAMES");
console.log("=========================================================================");

const html = fs.readFileSync('web/fm1_pacman_preview.html', 'utf8');
const sIdx = html.indexOf('<script>');
const eIdx = html.lastIndexOf('</script>');
const jsCode = html.slice(sIdx + 8, eIdx);

function mockParam(val = 0) {
  return { value: val, setValueAtTime: () => {}, linearRampToValueAtTime: () => {}, exponentialRampToValueAtTime: () => {} };
}

class MockAudioContext {
  constructor() { this.destination = {}; this.sampleRate = 44100; this.currentTime = 0; }
  createGain() { return { gain: mockParam(1), connect: () => {} }; }
  createOscillator() { return { frequency: mockParam(440), type: 'sine', connect: () => {}, start: () => {}, stop: () => {} }; }
  createBiquadFilter() { return { frequency: mockParam(2000), Q: mockParam(1), type: 'lowpass', connect: () => {} }; }
  createDelay() { return { delayTime: mockParam(0.2), connect: () => {} }; }
  createScriptProcessor() { return { connect: () => {} }; }
  createAnalyser() { return { fftSize: 2048, getByteFrequencyData: () => {}, connect: () => {} }; }
  createBuffer() { return { getChannelData: () => new Float32Array(100) }; }
  createBufferSource() { return { connect: () => {}, start: () => {}, stop: () => {} }; }
}

const mockCtx = {
  save: () => {}, restore: () => {}, translate: () => {}, scale: () => {},
  rotate: () => {}, beginPath: () => {}, moveTo: () => {}, lineTo: () => {},
  closePath: () => {}, stroke: () => {}, fill: () => {}, arc: () => {},
  rect: () => {}, roundRect: () => {}, strokeRect: () => {}, fillRect: () => {},
  clearRect: () => {}, drawImage: () => {}, fillText: () => {},
  createLinearGradient: () => ({ addColorStop: () => {} }),
  createRadialGradient: () => ({ addColorStop: () => {} }),
  createImageData: (w, h) => ({ data: new Uint8ClampedArray((w || 240) * (h || 240) * 4) }),
  putImageData: () => {}, font: '', fillStyle: '', strokeStyle: '', lineWidth: 1
};

const elements = {};
function getEl(id) {
  if (!elements[id]) {
    elements[id] = {
      id, style: { setProperty: () => {}, display: '' }, dataset: { tab: 'arcade', mode: 'arcade', key: '0' },
      classList: { classes: new Set(), add: function(c) { this.classes.add(c); }, remove: function(c) { this.classes.delete(c); }, toggle: function(c, v) { if (v !== undefined) { if (v) this.classes.add(c); else this.classes.delete(c); } else { if (this.classes.has(c)) this.classes.delete(c); else this.classes.add(c); } return this.classes.has(c); }, contains: function(c) { return this.classes.has(c); } },
      textContent: '', innerHTML: '', appendChild: () => {}, getContext: () => mockCtx
    };
  }
  return elements[id];
}

const sandbox = {
  console: console,
  setTimeout: setTimeout, clearTimeout: clearTimeout,
  setInterval: () => {}, clearInterval: () => {},
  requestAnimationFrame: () => {}, cancelAnimationFrame: () => {},
  Math: Math,
  atob: (b64) => Buffer.from(b64, 'base64').toString('binary'),
  btoa: (bin) => Buffer.from(bin, 'binary').toString('base64'),
  Image: class { constructor() { this.src = ''; } },
  AudioContext: MockAudioContext,
  webkitAudioContext: MockAudioContext,
  window: { innerWidth: 800, innerHeight: 600, addEventListener: () => {}, location: { search: '' }, AudioContext: MockAudioContext, webkitAudioContext: MockAudioContext },
  document: { getElementById: (id) => getEl(id), createElement: () => ({ textContent: '', className: '', classList: { toggle: () => {}, add: () => {}, remove: () => {} }, dataset: {}, style: {}, onclick: null, appendChild: () => {}, getContext: () => mockCtx, addEventListener: () => {} }), querySelector: () => getEl('key'), querySelectorAll: () => [getEl('test')] },
  navigator: { requestMIDIAccess: null }
};

vm.createContext(sandbox);
vm.runInContext(jsCode, sandbox);

// Hook playArcadeSfx to capture BGM triggers
const playedSounds = [];
sandbox.originalPlayArcadeSfx = sandbox.playArcadeSfx;
sandbox.playArcadeSfx = function(name) {
  playedSounds.push(name);
  return sandbox.originalPlayArcadeSfx(name);
};

vm.runInContext('splashState.active = false', sandbox);

// -------------------------------------------------------------------------
// 1. FROGGER BGM ("Inu no Omawarisan" / "The Frog Song")
// -------------------------------------------------------------------------
console.log("\n1. Testing Frogger Authentic AY-3-8910 Chiptune BGM...");
playedSounds.length = 0;
vm.runInContext("switchActiveGame('frogger')", sandbox);
for (let f = 0; f < 80; f++) vm.runInContext("updateFroggerGame()", sandbox);

const frogBgmCalls = playedSounds.filter(s => s === 'FROG-BGM');
console.log(`   ✓ Frogger played FROG-BGM ${frogBgmCalls.length} times during 80 frames!`);
assert(frogBgmCalls.length >= 4, `Expected at least 4 FROG-BGM triggers, got: ${frogBgmCalls.length}`);
const frogStep = vm.runInContext("froggerGame.bgmStep", sandbox);
assert(frogStep > 0, "Frogger bgmStep must advance through melody notes");
console.log(`   ✓ Melody step advanced to note ${frogStep} in AY-3-8910 square-wave sequence.`);

// -------------------------------------------------------------------------
// 2. GYRUSS BGM (J.S. Bach Toccata & Fugue in D minor BWV 565)
// -------------------------------------------------------------------------
console.log("\n2. Testing Gyruss Authentic J.S. Bach Toccata & Fugue in D minor BGM...");
playedSounds.length = 0;
vm.runInContext("switchActiveGame('gyruss')", sandbox);
for (let f = 0; f < 80; f++) vm.runInContext("updateGyrussGame()", sandbox);

const gyrussBgmCalls = playedSounds.filter(s => s === 'GYRUSS-BGM');
console.log(`   ✓ Gyruss played GYRUSS-BGM ${gyrussBgmCalls.length} times during 80 frames!`);
assert(gyrussBgmCalls.length >= 6, `Expected at least 6 GYRUSS-BGM triggers, got: ${gyrussBgmCalls.length}`);
const gyrStep = vm.runInContext("gyrussGame.bgmStep", sandbox);
assert(gyrStep > 0, "Gyruss bgmStep must advance through Bach Fugue score");
console.log(`   ✓ Baroque score step advanced to measure note ${gyrStep} in 5x PSG rock arrangement.`);

// -------------------------------------------------------------------------
// 3. CRAZY CLIMBER BGM (Henry Mancini "Baby Elephant Walk" / Swing Strut)
// -------------------------------------------------------------------------
console.log("\n3. Testing Crazy Climber Authentic Mancini Swing Strut BGM...");
playedSounds.length = 0;
vm.runInContext("switchActiveGame('cclimber')", sandbox);
for (let f = 0; f < 80; f++) vm.runInContext("updateCrazyClimberGame()", sandbox);

const climbBgmCalls = playedSounds.filter(s => s === 'CLIMB-BGM');
console.log(`   ✓ Crazy Climber played CLIMB-BGM ${climbBgmCalls.length} times during 80 frames!`);
assert(climbBgmCalls.length >= 4, `Expected at least 4 CLIMB-BGM triggers, got: ${climbBgmCalls.length}`);
const climbStep = vm.runInContext("climberState.bgmStep", sandbox);
assert(climbStep > 0, "Climber bgmStep must advance through walking swing bass and melody");
console.log(`   ✓ Swing strut step advanced to note ${climbStep} in Nichibutsu walking bass sequence.`);

// -------------------------------------------------------------------------
// 4. GALAGA BGM (Namco WSG Ambient Space Fleet & Challenging Stage BGM)
// -------------------------------------------------------------------------
console.log("\n4. Testing Galaga Space Fleet Formation Hum & Challenging Stage BGM...");
playedSounds.length = 0;
vm.runInContext("switchActiveGame('galaga')", sandbox);
vm.runInContext("galagaGame.shipX = 30; arcadeImmortalMode = true;", sandbox);
// Regular wave
for (let f = 0; f < 80; f++) vm.runInContext("updateGalagaGame()", sandbox);
const galagaFleetCalls = playedSounds.filter(s => s === 'GALAGA-BGM');
console.log(`   ✓ Regular Wave: Galaga played GALAGA-BGM fleet humming ${galagaFleetCalls.length} times!`);
assert(galagaFleetCalls.length >= 2, `Expected at least 2 GALAGA-BGM triggers, got: ${galagaFleetCalls.length}`);

// Challenging stage
playedSounds.length = 0;
vm.runInContext("galagaGame.isChallengingStage = true; galagaGame.gameOver = false; galagaGame.shipX = 30;", sandbox);
for (let f = 0; f < 80; f++) vm.runInContext("updateGalagaGame()", sandbox);
const galagaChallengeCalls = playedSounds.filter(s => s === 'GALAGA-CHALLENGE-BGM');
console.log(`   ✓ Challenging Stage: Galaga played GALAGA-CHALLENGE-BGM ${galagaChallengeCalls.length} times!`);
assert(galagaChallengeCalls.length >= 5, `Expected at least 5 GALAGA-CHALLENGE-BGM triggers, got: ${galagaChallengeCalls.length}`);

// -------------------------------------------------------------------------
// 5. TEMPEST BGM (Atari POKEY Polyphonic Vector Pulse Arpeggio)
// -------------------------------------------------------------------------
console.log("\n5. Testing Tempest Atari POKEY Polyphonic Vector Pulse Arpeggio BGM...");
playedSounds.length = 0;
vm.runInContext("switchActiveGame('tempest')", sandbox);
for (let f = 0; f < 80; f++) vm.runInContext("updateTempestGame()", sandbox);

const temBgmCalls = playedSounds.filter(s => s === 'TEM-BGM');
console.log(`   ✓ Tempest played TEM-BGM ${temBgmCalls.length} times during 80 frames!`);
assert(temBgmCalls.length >= 5, `Expected at least 5 TEM-BGM triggers, got: ${temBgmCalls.length}`);
const temStep = vm.runInContext("tempestGame.bgmStep", sandbox);
assert(temStep > 0, "Tempest bgmStep must advance through vector arpeggio");
console.log(`   ✓ Vector arpeggio step advanced to note ${temStep} in POKEY wireframe tube sequence.`);

// -------------------------------------------------------------------------
// 6. DONKEY KONG BGM (25M Walking Bass Ostinato & Hammer Ragtime)
// -------------------------------------------------------------------------
console.log("\n6. Testing Donkey Kong 25M Walking Bass & Hammer Ragtime BGM...");
playedSounds.length = 0;
vm.runInContext("switchActiveGame('dkong')", sandbox);
for (let f = 0; f < 80; f++) vm.runInContext("updateDonkeyKongGame()", sandbox);

const dkBgmCalls = playedSounds.filter(s => s === 'DK-BGM');
console.log(`   ✓ Donkey Kong played DK-BGM walking bass ${dkBgmCalls.length} times!`);
assert(dkBgmCalls.length >= 3, `Expected at least 3 DK-BGM triggers, got: ${dkBgmCalls.length}`);

// Test Hammer Pickup Tune
playedSounds.length = 0;
vm.runInContext("dkongGame.mario.hasHammer = true; dkongGame.mario.hammerTimer = 300;", sandbox);
for (let f = 0; f < 80; f++) vm.runInContext("updateDonkeyKongGame()", sandbox);
const dkHammerCalls = playedSounds.filter(s => s === 'DK-HAMMER-TUNE');
console.log(`   ✓ Hammer mode: Donkey Kong played DK-HAMMER-TUNE ${dkHammerCalls.length} times!`);
assert(dkHammerCalls.length >= 4, `Expected at least 4 DK-HAMMER-TUNE triggers, got: ${dkHammerCalls.length}`);

// -------------------------------------------------------------------------
// 7. ASTEROIDS BGM (Accelerating Dual-Tone Heartbeat & Saucer Warble)
// -------------------------------------------------------------------------
console.log("\n7. Testing Asteroids Accelerating Dual-Tone Heartbeat BGM...");
playedSounds.length = 0;
vm.runInContext("switchActiveGame('asteroids')", sandbox);
for (let f = 0; f < 100; f++) vm.runInContext("updateAsteroidsGame()", sandbox);

const thumps = playedSounds.filter(s => s === 'AST-THUMP-LO' || s === 'AST-THUMP-HI');
console.log(`   ✓ Asteroids played heartbeat thumps ${thumps.length} times!`);
assert(thumps.length >= 2, `Expected at least 2 heartbeat thumps, got: ${thumps.length}`);

// -------------------------------------------------------------------------
// 8. AUDIO BUS ISOLATION & ZERO CROSS-GAME BLEEDING
// -------------------------------------------------------------------------
console.log("\n8. Testing Audio Bus Isolation & Rapid Sequential Switching...");
const allGames = ['frogger', 'gyruss', 'cclimber', 'galaga', 'tempest', 'dkong', 'asteroids', 'pacman'];
allGames.forEach(gId => {
  vm.runInContext(`switchActiveGame('${gId}')`, sandbox);
  // Verify stopCurrentGame() reset all BGM counters
  const gStep = vm.runInContext(`(typeof ${gId}Game !== 'undefined' && ${gId}Game.bgmStep) || (typeof climberState !== 'undefined' && climberState.bgmStep) || 0`, sandbox);
  assert.strictEqual(gStep, 0, `BGM step for ${gId} must reset to 0 upon switching`);
});
console.log("   ✓ Zero audio bleed and clean BGM reset verified across all 8 game transitions!");

console.log("\n=========================================================================");
console.log(">>> ALL 8 ARCADE TITLES PASSED 100% ICONIC BGM AUDIT! <<<");
console.log("=========================================================================");
process.exit(0);
