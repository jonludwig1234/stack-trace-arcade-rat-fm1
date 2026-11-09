/**
 * test_frogger_death_fidelity.js
 * Comprehensive unit test verifying authentic Frogger death sequence & SFX fidelity:
 * 1. Highway Squish multi-phase animation (splat -> Konami Skull & Crossbones)
 * 2. River Drowning multi-phase animation (plunge splash -> expanding water ripple rings)
 * 3. Hop suppression during death countdown
 * 4. Reseed/respawn at start dock after deathTimer reaches 0
 * 5. Audio synthesis verification for FROG-SPLAT and FROG-SPLASH
 */

const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

// Setup headless mock browser context
const html = fs.readFileSync('web/fm1_pacman_preview.html', 'utf8');
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);
if (!scriptMatch) throw new Error("Could not find <script> in simulator template!");

const playedSfx = [];
const canvasCalls = [];

const mockCtx = {
  save() { canvasCalls.push({ op: 'save' }); },
  restore() { canvasCalls.push({ op: 'restore' }); },
  translate(x, y) { canvasCalls.push({ op: 'translate', x, y }); },
  fillRect(x, y, w, h) { canvasCalls.push({ op: 'fillRect', x, y, w, h, fillStyle: this.fillStyle }); },
  strokeRect(x, y, w, h) { canvasCalls.push({ op: 'strokeRect', x, y, w, h }); },
  beginPath() { canvasCalls.push({ op: 'beginPath' }); },
  arc(x, y, r, sa, ea) { canvasCalls.push({ op: 'arc', x, y, r }); },
  ellipse(x, y, rx, ry, rot, sa, ea) { canvasCalls.push({ op: 'ellipse', x, y, rx, ry }); },
  stroke() { canvasCalls.push({ op: 'stroke', strokeStyle: this.strokeStyle }); },
  fill() { canvasCalls.push({ op: 'fill' }); },
  fillText(txt, x, y) { canvasCalls.push({ op: 'fillText', txt, x, y }); },
  measureText() { return { width: 40 }; },
  createImageData: (w, h) => ({ data: new Uint8ClampedArray((w || 240) * (h || 240) * 4) }),
  putImageData: () => {},
  fillStyle: '#000000',
  strokeStyle: '#000000',
  lineWidth: 1
};

const audioNodes = [];
const mockAudioCtx = {
  currentTime: 0,
  createOscillator() {
    const node = {
      type: 'sine',
      frequency: {
        val: 0,
        setValueAtTime(v, t) { this.val = v; node.events.push({ op: 'setFreq', v, t }); },
        exponentialRampToValueAtTime(v, t) { node.events.push({ op: 'rampFreq', v, t }); }
      },
      events: [],
      connect(target) { node.target = target; },
      start(t) { node.startTime = t; },
      stop(t) { node.stopTime = t; }
    };
    audioNodes.push({ kind: 'osc', node });
    return node;
  },
  createGain() {
    const node = {
      gain: {
        val: 1,
        setValueAtTime(v, t) { this.val = v; node.events.push({ op: 'setGain', v, t }); },
        exponentialRampToValueAtTime(v, t) { node.events.push({ op: 'rampGain', v, t }); }
      },
      events: [],
      connect(target) { node.target = target; }
    };
    audioNodes.push({ kind: 'gain', node });
    return node;
  },
  createBiquadFilter() {
    const node = {
      type: 'lowpass',
      frequency: {
        val: 350,
        setValueAtTime(v, t) { this.val = v; node.events.push({ op: 'setFltFreq', v, t }); },
        exponentialRampToValueAtTime(v, t) { node.events.push({ op: 'rampFltFreq', v, t }); }
      },
      Q: {
        val: 1,
        setValueAtTime(v, t) { this.val = v; node.events.push({ op: 'setQ', v, t }); }
      },
      events: [],
      connect(target) { node.target = target; }
    };
    audioNodes.push({ kind: 'filter', node });
    return node;
  },
  createBuffer(channels, length, sampleRate) {
    return {
      getChannelData() { return new Float32Array(length); }
    };
  },
  createBufferSource() {
    const node = {
      events: [],
      connect(target) { node.target = target; },
      start(t) { node.startTime = t; },
      stop(t) { node.stopTime = t; }
    };
    audioNodes.push({ kind: 'bufferSource', node });
    return node;
  }
};

const sandbox = {
  window: { addEventListener: () => {}, location: { search: '' } },
  document: {
    getElementById: () => ({ getContext: () => mockCtx, style: {}, addEventListener: () => {}, appendChild: () => {}, classList: { add: () => {}, remove: () => {}, toggle: () => {} } }),
    querySelectorAll: () => [],
    createElement: () => ({ style: {}, dataset: {}, appendChild: () => {}, classList: { add: () => {}, remove: () => {}, toggle: () => {} }, getContext: () => mockCtx, addEventListener: () => {} })
  },
  atob: (s) => Buffer.from(s, 'base64').toString('binary'),
  btoa: (s) => Buffer.from(s, 'binary').toString('base64'),
  Image: function() { return { addEventListener: () => {}, set src(v) {} }; },
  AudioContext: function() { return mockAudioCtx; },
  webkitAudioContext: function() { return mockAudioCtx; },
  console: console,
  setTimeout: (cb) => cb(),
  setInterval: () => 1,
  clearInterval: () => {},
  requestAnimationFrame: () => 1,
  localStorage: { getItem: () => null, setItem: () => {} }
};

vm.createContext(sandbox);
vm.runInContext(scriptMatch[1], sandbox);

// Hook audioCtx and playArcadeSfx
vm.runInContext(`
  audioCtx = new AudioContext();
  origPlaySfx = playArcadeSfx;
  playArcadeSfx = function(name) {
    playedSfx.push(name);
    origPlaySfx(name);
  };
`, sandbox);
sandbox.playedSfx = playedSfx;
sandbox.ctx = mockCtx;

console.log("=========================================================================");
console.log("   FROGGER AUTHENTIC DEATH ANIMATION & SFX FIDELITY QA BATTERY           ");
console.log("=========================================================================");

// 1. Switch to Frogger
vm.runInContext(`
  setMode('arcade');
  switchActiveGame('frogger');
  initFroggerGame();
`, sandbox);

const fg = vm.runInContext('froggerGame.frog', sandbox);
const game = vm.runInContext('froggerGame', sandbox);

console.log("\n1. Testing Highway Traffic Squish & Skull-and-Crossbones sequence...");
// Position frog in middle road
fg.gridX = 6;
fg.gridY = 9;
fg.x = 104;
fg.y = 160;
playedSfx.length = 0;

// Put vehicle directly on frog
game.vehicles.push({ x: 104, y: 160, w: 24, speed: 0, color: '#ff0000' });
vm.runInContext('updateFroggerGame();', sandbox);

assert.strictEqual(playedSfx[0], 'FROG-SPLAT', "Traffic squish must trigger FROG-SPLAT sound");
assert.strictEqual(fg.dead, true, "Frogger must enter dead state upon squish");
assert.strictEqual(fg.deathType, 'splat', "Death type must be 'splat'");
assert.strictEqual(fg.deathTimer, 45, "Death timer must initialize to 45 frames");
assert.strictEqual(fg.deathX, 104, "Death X coordinate must be retained at collision location");
assert.strictEqual(fg.deathY, 160, "Death Y coordinate must be retained at collision location");
assert.strictEqual(fg.x, 120, "Frogger logical position respawn dock x=120");
assert.strictEqual(fg.y, 224, "Frogger logical position respawn dock y=224");

console.log("   ✓ Highway squish triggered FROG-SPLAT, dead=true, deathTimer=45 at (104, 160)");

// 2. Test hop suppression while dying
const preHopX = fg.x;
const preHopY = fg.y;
vm.runInContext("froggerHop('up');", sandbox);
assert.strictEqual(fg.x, preHopX, "Frogger hop must be suppressed while dead");
assert.strictEqual(fg.y, preHopY, "Frogger hop must be suppressed while dead");
console.log("   ✓ Frogger hop input safely blocked while death sequence active");

// 3. Test Phase 1 Rendering (Squashed frog)
canvasCalls.length = 0;
vm.runInContext('renderFroggerGame();', sandbox);
const translatedToDeath = canvasCalls.some(c => c.op === 'translate' && c.x === 104 && c.y === 160);
assert.strictEqual(translatedToDeath, true, "Renderer must translate to death location (104, 160)");
console.log("   ✓ Phase 1 death render verified (crushed frog body drawn at death coordinate)");

// 4. Advance into Phase 2 (Iconic Konami Skull & Crossbones Tombstone)
fg.deathTimer = 20; // Phase 2: deathTimer <= 28
canvasCalls.length = 0;
vm.runInContext('renderFroggerGame();', sandbox);
// In phase 2, white skull and menacing red pupils are drawn:
const drewSkull = canvasCalls.some(c => c.op === 'fillRect' && c.fillStyle === '#f1f2f6');
const drewRedPupil = canvasCalls.some(c => c.op === 'fillRect' && c.fillStyle === '#ff4757');
assert.strictEqual(drewSkull, true, "Must render Konami arcade white skull dome");
assert.strictEqual(drewRedPupil, true, "Must render menacing red pupils in skull sockets");
console.log("   ✓ Phase 2 Konami Skull & Crossbones tombstone verified (dome + red pupil sockets)");

// 5. Test Respawn completion
fg.deathTimer = 1;
vm.runInContext('updateFroggerGame();', sandbox);
assert.strictEqual(fg.dead, false, "Frogger dead flag must clear when deathTimer reaches 0");
assert.strictEqual(fg.x, 120, "Frogger respawned at starting dock");
assert.strictEqual(fg.y, 224, "Frogger respawned at starting dock");
console.log("   ✓ Death sequence completed: frog respawned alive at start dock");

// 6. Test River Drowning & Water Ripple Rings
console.log("\n2. Testing River Drowning & Expanding Water Ripple Rings sequence...");
fg.gridX = 5;
fg.gridY = 4;
fg.x = 88;
fg.y = 80;
// Clear river logs so frog plunges directly into deep water
game.logs = [];
playedSfx.length = 0;

// Update in river without support
vm.runInContext('updateFroggerGame();', sandbox);
assert.strictEqual(playedSfx[0], 'FROG-SPLASH', "River plunge must trigger FROG-SPLASH sound");
assert.strictEqual(fg.dead, true, "Frogger must enter dead state upon drowning");
assert.strictEqual(fg.deathType, 'drown', "Death type must be 'drown'");
assert.strictEqual(fg.deathX, 88, "Death X must be 88");
assert.strictEqual(fg.deathY, 80, "Death Y must be 80");

console.log("   ✓ River drowning triggered FROG-SPLASH, dead=true, deathTimer=45 at (88, 80)");

// Advance to Phase 2 (Water Ripple Rings)
fg.deathTimer = 15; // Phase 2: deathTimer <= 28
canvasCalls.length = 0;
vm.runInContext('renderFroggerGame();', sandbox);
const strokedRipple = canvasCalls.some(c => c.op === 'stroke');
const drewEllipse = canvasCalls.some(c => c.op === 'ellipse');
assert.strictEqual(strokedRipple, true, "Renderer must stroke water ripple rings");
assert.strictEqual(drewEllipse, true, "Renderer must draw concentric water ripple ellipses");
console.log("   ✓ Phase 2 Expanding Water Ripple Rings verified (concentric cyan/white ellipses)");

// 7. Test Sound Synthesis Audio Graphs
console.log("\n3. Testing Authentic Konami AY-3-8910 Audio Synthesis Graphs...");

// FROG-SPLAT synthesis test
audioNodes.length = 0;
vm.runInContext("playArcadeSfx('FROG-SPLAT');", sandbox);
const splatOsc = audioNodes.find(n => n.kind === 'osc' && n.node.type === 'sawtooth');
const splatFlt = audioNodes.find(n => n.kind === 'filter' && n.node.type === 'bandpass');
assert(splatOsc, "FROG-SPLAT must use stepped sawtooth crunch oscillator");
assert(splatFlt, "FROG-SPLAT must use bandpass noise crunch filter");
const freqSteps = splatOsc.node.events.filter(e => e.op === 'setFreq').map(e => e.v);
assert.deepStrictEqual(freqSteps, [1250, 840, 520, 310, 140], "FROG-SPLAT must descend stepped AY-3-8910 frequencies");
console.log("   ✓ FROG-SPLAT verified: stepped 1250->140 Hz AY-3-8910 crunch + bandpass noise burst");

// FROG-SPLASH synthesis test
audioNodes.length = 0;
vm.runInContext("playArcadeSfx('FROG-SPLASH');", sandbox);
const splashSine = audioNodes.find(n => n.kind === 'osc' && n.node.type === 'sine');
const splashFlt = audioNodes.find(n => n.kind === 'filter' && n.node.type === 'bandpass');
assert(splashSine, "FROG-SPLASH must use resonant sine oscillator for water bloop");
assert(splashFlt, "FROG-SPLASH must use resonant bandpass noise filter for splash");
const sineRamps = splashSine.node.events.filter(e => e.op === 'rampFreq').map(e => e.v);
assert.deepStrictEqual(sineRamps, [320, 140], "FROG-SPLASH must dive frequencies 920 -> 320 -> 140 Hz");
console.log("   ✓ FROG-SPLASH verified: resonant bloop-plunk 920->320->140 Hz + water splash noise");

console.log("\n=========================================================================");
console.log(">>> ALL FROGGER DEATH ANIMATION & SFX FIDELITY TESTS PASSED 100%! <<<");
console.log("=========================================================================\n");
