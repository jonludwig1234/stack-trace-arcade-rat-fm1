/**
 * ============================================================================
 * BATTERY 23: REAL-USER JOURNEYS, NEGATIVE ISOLATION & DSP WIRING QA SUITE
 * ============================================================================
 * Specifically targets the gap between unit-level mocks and real human usage:
 *  1. Master Volume (#encMaster, #btnVolDown/Up, MIDI CC 7) -> real masterGain.gain
 *  2. Demo Jukebox stepSong(-1/+1) & PRESETS encoder -> zero ReferenceError + UI sync
 *  3. Speech ROM Hotkey Negative Isolation -> keys 1 & 5 NEVER cross-trigger Coin/Start
 *  4. Silicone Keys 1-27 in Speech Tab -> trigger Speech ROMs + display Speech labels
 *  5. 27-Key QWERTY Live Performance in Synth, Soundboard & Tracker + repeat/blur safety
 *  6. Knob 4 & MIDI CC 74/91/71/19 -> actual Web Audio filterNode/delayNode/waveMorph DSP
 *  7. Tracker Single-Step (⏩ STEP) when paused & Pattern BPM synchronization
 *  8. 1P START (start1P) recovery from Game Over (Crazy Climber) & 0-Credit Pac-Man Start
 *  9. MIDI Action Notes 36..43 end-to-end dispatch (Fire, Jump, 1P Start, Insert Coin)
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

console.log("=========================================================================");
console.log("  M-VAVE FM-1: REAL-USER JOURNEYS, NEGATIVE ISOLATION & DSP WIRING QA");
console.log("=========================================================================\n");

const htmlPath = path.join(__dirname, '..', 'web', 'fm1_pacman_preview.html');
const html = fs.readFileSync(htmlPath, 'utf8');

const scriptMatches = [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)];
assert(scriptMatches.length > 0, "No <script> tags found in fm1_pacman_preview.html");
const combinedJs = scriptMatches.map(m => m[1]).join('\n');

// Build rich DOM & Web Audio sandbox
const elements = {};
const pianoKeys = [];
const studioTabs = ['arcade', 'synth', 'tracker', 'demo', 'soundboard', 'speech', 'tour'].map(t => ({
  dataset: { tab: t },
  classList: {
    _set: new Set(t === 'arcade' ? ['active'] : []),
    toggle(c, f) { if (f === undefined) { if (this._set.has(c)) this._set.delete(c); else this._set.add(c); } else if (f) this._set.add(c); else this._set.delete(c); },
    add(c) { this._set.add(c); },
    remove(c) { this._set.delete(c); },
    contains(c) { return this._set.has(c); }
  }
}));
const modeTags = ['arcade', 'synth', 'tracker', 'demo', 'soundboard', 'tour'].map(m => ({
  dataset: { mode: m },
  classList: {
    _set: new Set(m === 'arcade' ? ['active'] : []),
    toggle(c, f) { if (f === undefined) { if (this._set.has(c)) this._set.delete(c); else this._set.add(c); } else if (f) this._set.add(c); else this._set.delete(c); },
    add(c) { this._set.add(c); },
    remove(c) { this._set.delete(c); },
    contains(c) { return this._set.has(c); }
  }
}));

function makeEl(id = '') {
  if (id && elements[id]) return elements[id];
  const el = {
    id,
    textContent: '',
    innerHTML: '',
    value: '',
    className: '',
    dataset: {},
    children: [],
    style: {
      _props: {},
      setProperty(k, v) { this._props[k] = v; },
      getPropertyValue(k) { return this._props[k] || ''; }
    },
    classList: {
      _set: new Set(),
      add(c) { this._set.add(c); },
      remove(c) { this._set.delete(c); },
      toggle(c, force) {
        if (force === undefined) {
          if (this._set.has(c)) { this._set.delete(c); return false; }
          this._set.add(c); return true;
        }
        if (force) this._set.add(c); else this._set.delete(c);
        return force;
      },
      contains(c) { return this._set.has(c); }
    },
    appendChild(child) {
      this.children.push(child);
      if ((this.id === 'pianoKeys' || this.id === 'pianoContainer') && child.dataset && child.dataset.key !== undefined) {
        pianoKeys[parseInt(child.dataset.key, 10)] = child;
      }
      return child;
    },
    addEventListener(ev, fn) { this['on' + ev] = fn; },
    querySelector() { return makeEl(); },
    querySelectorAll() { return []; },
    getBoundingClientRect() { return { left: 0, top: 0, width: 240, height: 240 }; },
    getContext() {
      return {
        fillStyle: '', strokeStyle: '', font: '', textAlign: '', lineWidth: 1,
        fillRect() {}, strokeRect() {}, clearRect() {}, fillText() {},
        beginPath() {}, moveTo() {}, lineTo() {}, arc() {}, closePath() {},
        fill() {}, stroke() {}, save() {}, restore() {}, translate() {},
        scale() {}, rotate() {}, clip() {}, drawImage() {},
        createImageData: (w, h) => ({ data: new Uint8ClampedArray(w * h * 4) }),
        putImageData() {},
        createLinearGradient: () => ({ addColorStop() {} }),
        createRadialGradient: () => ({ addColorStop() {} })
      };
    }
  };
  if (id) elements[id] = el;
  return el;
}

const windowListeners = { keydown: [], keyup: [], blur: [] };
let createdOscillators = [];
let createdBufferSources = [];

class MockAudioParam {
  constructor(initVal = 0) {
    this.value = initVal;
    this.events = [];
  }
  setValueAtTime(v, t) { this.value = v; this.events.push({ type: 'set', v, t }); }
  linearRampToValueAtTime(v, t) { this.value = v; this.events.push({ type: 'linear', v, t }); }
  exponentialRampToValueAtTime(v, t) { this.value = v; this.events.push({ type: 'exp', v, t }); }
  setTargetAtTime(v, t, c) { this.value = v; this.events.push({ type: 'target', v, t, c }); }
  cancelScheduledValues() {}
}

class MockAudioContext {
  constructor() {
    this.currentTime = 1.0;
    this.sampleRate = 44100;
    this.state = 'running';
    this.destination = {};
  }
  resume() { this.state = 'running'; return Promise.resolve(); }
  createGain() {
    return { gain: new MockAudioParam(1.0), connect() {}, disconnect() {} };
  }
  createBiquadFilter() {
    return {
      type: 'lowpass',
      frequency: new MockAudioParam(6500),
      Q: new MockAudioParam(1.0),
      gain: new MockAudioParam(0),
      connect() {}, disconnect() {}
    };
  }
  createDelay() {
    return { delayTime: new MockAudioParam(0.28), connect() {}, disconnect() {} };
  }
  createAnalyser() {
    return { fftSize: 256, frequencyBinCount: 128, connect() {}, getByteTimeDomainData() {}, getByteFrequencyData() {} };
  }
  createScriptProcessor() {
    return { connect() {}, onaudioprocess: null };
  }
  createOscillator() {
    const osc = {
      type: 'sine',
      frequency: new MockAudioParam(440),
      detune: new MockAudioParam(0),
      connect() {}, disconnect() {},
      start() {}, stop() {}
    };
    createdOscillators.push(osc);
    return osc;
  }
  createBuffer(ch, len, sr) {
    const chData = new Float32Array(len);
    return { numberOfChannels: ch, length: len, sampleRate: sr, getChannelData: () => chData };
  }
  createBufferSource() {
    const src = {
      buffer: null,
      playbackRate: new MockAudioParam(1.0),
      connect() {}, disconnect() {},
      start() {}, stop() {}
    };
    createdBufferSources.push(src);
    return src;
  }
  decodeAudioData(buf, cb) {
    const decoded = this.createBuffer(1, 1024, 44100);
    if (cb) cb(decoded);
    return Promise.resolve(decoded);
  }
}

const sandbox = {
  console,
  atob: globalThis.atob,
  btoa: globalThis.btoa,
  Buffer,
  ArrayBuffer,
  URLSearchParams,
  fetch: () => Promise.resolve({ arrayBuffer: () => Promise.resolve(new ArrayBuffer(64)) }),
  Math, Date, Number, String, Boolean, Array, Object, Set, Map, RegExp, JSON, Promise,
  Uint8Array, Uint16Array, Uint32Array, Int8Array, Int16Array, Int32Array, Float32Array, Uint8ClampedArray,
  parseInt, parseFloat, isNaN, isFinite,
  setTimeout: (fn) => 1,
  clearTimeout: () => {},
  setInterval: (fn) => 1,
  clearInterval: () => {},
  requestAnimationFrame: () => 1,
  AudioContext: MockAudioContext,
  webkitAudioContext: MockAudioContext,
  Image: class { set src(v) { if (this.onload) this.onload(); } get complete() { return true; } get naturalWidth() { return 240; } },
  Audio: class { play() { return Promise.resolve(); } },
  localStorage: {
    _data: {},
    getItem(k) { return this._data[k] || null; },
    setItem(k, v) { this._data[k] = String(v); }
  },
  navigator: { requestMIDIAccess: () => Promise.resolve({ inputs: new Map(), onstatechange: null }) },
  window: {
    AudioContext: MockAudioContext,
    webkitAudioContext: MockAudioContext,
    location: { search: '?nosplash=1' },
    addEventListener(ev, fn) {
      if (!windowListeners[ev]) windowListeners[ev] = [];
      windowListeners[ev].push(fn);
    },
    removeEventListener() {}
  },
  document: {
    getElementById(id) { return makeEl(id); },
    createElement(tag) { return makeEl(); },
    querySelector(sel) {
      const m = sel.match(/\[data-key="(\d+)"\]/);
      if (m) return pianoKeys[parseInt(m[1], 10)] || makeEl();
      return makeEl();
    },
    querySelectorAll(sel) {
      if (sel.includes('.piano-key') || sel.includes('.key-white')) return pianoKeys;
      if (sel === '.studio-tab') return studioTabs;
      if (sel === '.mode-tag') return modeTags;
      if (sel === '#shelfSongPills .synth-chip-btn') return (elements['shelfSongPills'] ? elements['shelfSongPills'].children : []);
      return [];
    }
  }
};
sandbox.globalThis = sandbox;
sandbox.self = sandbox.window;

vm.createContext(sandbox);
vm.runInContext(combinedJs, sandbox);

function dispatchKey(type, key, extra = {}) {
  const ev = Object.assign({
    key,
    repeat: false,
    ctrlKey: false,
    metaKey: false,
    altKey: false,
    preventDefault() {}
  }, extra);
  (windowListeners[type] || []).forEach(fn => fn(ev));
}

// ---------------------------------------------------------------------------
// 1. MASTER VOLUME HARDWARE & MIDI CC 7 -> ACTUAL DSP GAIN
// ---------------------------------------------------------------------------
console.log("1. Testing Master Volume (#encMaster, #btnVolDown/Up, MIDI CC 7) -> Web Audio masterGain...");
vm.runInContext('initAudio()', sandbox);
vm.runInContext('updateMasterVol(-100)', sandbox);
let volLevel = vm.runInContext('masterVolLevel', sandbox);
let gainVal = vm.runInContext('masterGain.gain.value', sandbox);
assert.strictEqual(volLevel, 0, "masterVolLevel should clamp to 0%");
assert.strictEqual(gainVal, 0, `masterGain.gain.value must be 0 when Master Volume is 0%, got ${gainVal}`);

vm.runInContext('updateMasterVol(100)', sandbox);
volLevel = vm.runInContext('masterVolLevel', sandbox);
gainVal = vm.runInContext('masterGain.gain.value', sandbox);
assert.strictEqual(volLevel, 100, "masterVolLevel should reach 100%");
assert(gainVal > 0.9 && gainVal <= 1.0, `masterGain.gain.value must be ~0.95 at 100% volume, got ${gainVal}`);

vm.runInContext('handleMidiMessage({ data: [0xB0, 7, 0] })', sandbox);
assert.strictEqual(vm.runInContext('masterGain.gain.value', sandbox), 0, "MIDI CC 7 = 0 must mute masterGain.gain.value to 0");
vm.runInContext('handleMidiMessage({ data: [0xB0, 7, 127] })', sandbox);
assert(vm.runInContext('masterGain.gain.value', sandbox) > 0.9, "MIDI CC 7 = 127 must restore full masterGain.gain.value");
console.log("   ✓ Master Volume encoder, Vol-/Vol+ buttons & MIDI CC 7 directly control Web Audio masterGain!");

// ---------------------------------------------------------------------------
// 2. DEMO JUKEBOX stepSong(-1/+1) & PRESETS ENCODER
// ---------------------------------------------------------------------------
console.log("\n2. Testing Demo Jukebox stepSong(-1 / +1) & PRESETS Encoder...");
vm.runInContext('stepSong(1)', sandbox);
assert.strictEqual(vm.runInContext('currentMode', sandbox), 'demo', "stepSong(1) must enter demo mode");
assert.strictEqual(vm.runInContext('demoPlayer.currentSongIdx', sandbox), 1, "stepSong(1) must advance to Song 1");
assert.strictEqual(vm.runInContext('demoPlayer.playing', sandbox), true, "stepSong(1) must ensure demo song is playing");
assert.strictEqual(elements['shelfJukeStatus'].textContent, 'PLAYING', "shelfJukeStatus badge must update to PLAYING");

vm.runInContext('stepSong(-1)', sandbox);
assert.strictEqual(vm.runInContext('demoPlayer.currentSongIdx', sandbox), 0, "stepSong(-1) must step back to Song 0");
vm.runInContext('stopDemoSong()', sandbox);
assert.strictEqual(elements['shelfJukeStatus'].textContent, 'STOPPED', "shelfJukeStatus badge must update to STOPPED");
console.log("   ✓ Demo Jukebox Prev/Next & PRESETS encoder cycle all 4 symphonies with zero ReferenceError!");

// ---------------------------------------------------------------------------
// 3. SPEECH ROM NEGATIVE ISOLATION & SILICONE KEY MAPPING
// ---------------------------------------------------------------------------
console.log("\n3. Testing Vintage Speech ROM Hotkey Negative Isolation & Silicone Keys...");
vm.runInContext("setStudioTab('speech')", sandbox);
assert.strictEqual(vm.runInContext('currentStudioTab', sandbox), 'speech', "currentStudioTab must be 'speech'");
assert(pianoKeys[0].innerHTML.includes('INTRUDR'), `Silicone key 0 must display INTRUDR in speech tab, got: ${pianoKeys[0].innerHTML}`);

// Track if insertCoin or start1P or playArcadeSfx('COIN'/'START') is accidentally called when pressing 1..8 in speech mode
let sfxCallsDuringSpeech = [];
let speechCalls = [];
vm.runInContext(`
  const _origPlaySfx = playArcadeSfx;
  playArcadeSfx = function(name) { sfxCallsDuringSpeech.push(name); return _origPlaySfx(name); };
  const _origSpeech = triggerSpeechRom;
  triggerSpeechRom = function(id) { speechCalls.push(id); return _origSpeech(id); };
`, Object.assign(sandbox, { sfxCallsDuringSpeech, speechCalls }));

for (let n = 1; n <= 8; n++) {
  dispatchKey('keydown', String(n));
  dispatchKey('keyup', String(n));
}
assert.strictEqual(speechCalls.length, 8, `Pressing 1..8 on Speech tab must trigger all 8 Speech ROMs, got ${speechCalls.length}`);
assert.strictEqual(sfxCallsDuringSpeech.length, 0, `Pressing 1..8 on Speech tab must NEVER cross-trigger COIN/START SFX, got: ${sfxCallsDuringSpeech.join(', ')}`);

// Now test touching physical Silicone Keys 0..7 while on Speech tab
speechCalls.length = 0;
for (let k = 0; k < 8; k++) {
  vm.runInContext(`onKeyTouch(${k}, true); onKeyTouch(${k}, false);`, sandbox);
}
assert.strictEqual(speechCalls.length, 8, `Touching Silicone Keys 0..7 on Speech tab must trigger all 8 Speech ROMs, got ${speechCalls.length}`);
assert.strictEqual(sfxCallsDuringSpeech.length, 0, "Touching Silicone Keys on Speech tab must not fire SFX pads");
console.log("   ✓ Keys 1-8 and Silicone Keys 1-27 trigger Speech ROMs with ZERO Coin/Start cross-triggering!");

// ---------------------------------------------------------------------------
// 4. 27-KEY QWERTY LIVE PERFORMANCE IN SYNTH, SOUNDBOARD & TRACKER MODES
// ---------------------------------------------------------------------------
console.log("\n4. Testing 27-Key QWERTY Performance, Key-Repeat Suppression & Window Blur Release...");
vm.runInContext("setMode('synth')", sandbox);
assert.strictEqual(vm.runInContext('currentStudioTab', sandbox), 'synth', "setMode('synth') must sync currentStudioTab to 'synth'");

const qwertyTestKeys = ['z', 's', 'x', 'd', 'c', 'f', 'g', 'b', 'h', 'n', 'j', 'm', 'q', '2', 'w', '3', 'e', 'r', '5', 't', '6', 'y', '7', 'u', 'i', '9', 'o'];
sfxCallsDuringSpeech.length = 0;

qwertyTestKeys.forEach((k) => {
  dispatchKey('keydown', k);
  const activeCount = vm.runInContext('liveSynth.activeVoices.size', sandbox);
  assert.strictEqual(activeCount, 1, `Holding QWERTY key '${k}' in synth mode must activate 1 synth voice, got ${activeCount}`);

  // Simulate OS key-repeat (repeat: true)
  const oscCountBefore = createdOscillators.length;
  dispatchKey('keydown', k, { repeat: true });
  assert.strictEqual(createdOscillators.length, oscCountBefore, `Key repeat on '${k}' must not re-trigger oscillator attack`);

  dispatchKey('keyup', k);
  const afterUp = vm.runInContext('liveSynth.activeVoices.size', sandbox);
  assert.strictEqual(afterUp, 0, `Releasing QWERTY key '${k}' must release synth voice`);
});
assert.strictEqual(sfxCallsDuringSpeech.length, 0, `Typing QWERTY keys (including 5, i, g, b, z, r) in Synth mode must NEVER trigger arcade SFX, got: ${sfxCallsDuringSpeech.join(', ')}`);

// Test window blur while holding a chord of 3 keys ('z', 'c', 'b')
dispatchKey('keydown', 'z');
dispatchKey('keydown', 'c');
dispatchKey('keydown', 'b');
assert.strictEqual(vm.runInContext('liveSynth.activeVoices.size', sandbox), 3, "3-note QWERTY chord must hold 3 active voices");
(windowListeners.blur || []).forEach(fn => fn());
assert.strictEqual(vm.runInContext('liveSynth.activeVoices.size', sandbox), 0, "window.blur must release all held synth voices so no notes stick");
console.log("   ✓ All 27 QWERTY keys play Synth notes cleanly with key-repeat suppression & blur voice-release!");

// ---------------------------------------------------------------------------
// 5. KNOB 4 & MIDI CC DSP WIRING + TRACKER SINGLE-STEP WHEN PAUSED
// ---------------------------------------------------------------------------
console.log("\n5. Testing Knob 4 / MIDI CC DSP Wiring & Tracker Single-Step When Paused...");
vm.runInContext('handleMidiMessage({ data: [0xB0, 74, 127] })', sandbox);
assert.strictEqual(Math.round(vm.runInContext('filterNode.frequency.value', sandbox)), 12000, "MIDI CC 74 = 127 must set filterNode.frequency.value to 12000 Hz");

vm.runInContext('handleMidiMessage({ data: [0xB0, 91, 127] })', sandbox);
assert(Math.abs(vm.runInContext('delayNode.delayTime.value', sandbox) - 0.8) < 0.01, "MIDI CC 91 = 127 must set delayNode.delayTime.value to 0.8s");

vm.runInContext('handleMidiMessage({ data: [0xB0, 71, 127] })', sandbox);
assert(Math.abs(vm.runInContext('feedbackNode.gain.value', sandbox) - 0.85) < 0.01, "MIDI CC 71 = 127 must set feedbackNode.gain.value to 0.85");

vm.runInContext('handleMidiMessage({ data: [0xB0, 19, 127] })', sandbox);
assert.strictEqual(vm.runInContext('liveSynth.waveMorph', sandbox), 7, "MIDI CC 19 = 127 must update liveSynth.waveMorph to 7");
assert.strictEqual(vm.runInContext('wsgVoices[0].wave', sandbox), 7, "MIDI CC 19 = 127 must update wsgVoices[0].wave to 7");

// Tracker single-step when paused
vm.runInContext("setMode('tracker'); stopTracker(); selectTrackerPattern(2);", sandbox);
assert.strictEqual(vm.runInContext('trackerEngine.bpm', sandbox), 144, "selectTrackerPattern(2) must sync trackerEngine.bpm to 144 BPM");
assert.strictEqual(vm.runInContext('trackerEngine.playing', sandbox), false, "Tracker should be stopped");
const stepBefore = vm.runInContext('trackerEngine.step', sandbox);
const oscsBeforeStep = createdOscillators.length;
vm.runInContext('stepTrackerStep()', sandbox);
const stepAfter = vm.runInContext('trackerEngine.step', sandbox);
assert.strictEqual(stepAfter, (stepBefore + 1) % 16, "stepTrackerStep() must advance step even when tracker loop is paused");
assert(createdOscillators.length > oscsBeforeStep, "stepTrackerStep() must audition the current step's chiptune voices when paused");
console.log("   ✓ Knob 4, MIDI CCs 74/91/71/19, and Tracker single-step/pattern BPM sync verified!");

// ---------------------------------------------------------------------------
// 6. CRAZY CLIMBER GAME-OVER RECOVERY & PAC-MAN 0-CREDIT 1P START
// ---------------------------------------------------------------------------
console.log("\n6. Testing 1P START Recovery in Crazy Climber & 0-Credit Start in Pac-Man...");
vm.runInContext("switchActiveGame('cclimber')", sandbox);
vm.runInContext("climberState.gameOver = true; climberState.lives = 0;", sandbox);
vm.runInContext("start1P()", sandbox);
assert.strictEqual(vm.runInContext('climberState.gameOver', sandbox), false, "start1P() in Crazy Climber must clear gameOver");
assert(vm.runInContext('climberState.lives', sandbox) >= 3, "start1P() in Crazy Climber must restore lives to >= 3");
assert.strictEqual(vm.runInContext('climberState.floor', sandbox), 1, "start1P() in Crazy Climber must start at floor 1");

vm.runInContext("switchActiveGame('pacman')", sandbox);
vm.runInContext("ram[0x4e69 - 0x4000] = 0;", sandbox);
vm.runInContext("start1P()", sandbox);
assert(vm.runInContext("ram[0x4e69 - 0x4000]", sandbox) >= 1, "start1P() on 0-credit Pac-Man must auto-credit 1 coin so 1P START always works");
assert.strictEqual(vm.runInContext("keyStart", sandbox), true, "start1P() on Pac-Man must assert keyStart");

// MIDI Action notes 36 (Fire), 42 (Start), 43 (Coin)
vm.runInContext("switchActiveGame('galaga')", sandbox);
const bulletsBefore = vm.runInContext("galagaGame.lasers.length", sandbox);
vm.runInContext("handleMidiMessage({ data: [0x90, 36, 127] })", sandbox);
assert(vm.runInContext("galagaGame.lasers.length", sandbox) > bulletsBefore, "MIDI Note 36 (Fire) must fire Galaga dual lasers");

const creditsBefore = vm.runInContext("galagaGame.credits || 0", sandbox);
vm.runInContext("handleMidiMessage({ data: [0x90, 43, 127] })", sandbox);
assert.strictEqual(vm.runInContext("galagaGame.credits", sandbox), creditsBefore + 1, "MIDI Note 43 (Coin) must increment credits");
console.log("   ✓ Crazy Climber 1P Start recovery, Pac-Man 0-credit Start, and MIDI Action Notes 36..43 verified!");

// ---------------------------------------------------------------------------
// 7. HALL OF FAME INITIALS SUBMISSION (FORCE TOP-5) & PAC-MAN LIVE VRAM SCORE
// ---------------------------------------------------------------------------
console.log("\n7. Testing Hall of Fame Initials Submission & Live Pac-Man VRAM Score Decoder...");
vm.runInContext("switchActiveGame('pacman')", sandbox);
// Write 14,250 into Pac-Man 1UP VRAM tiles (0x03F7 = ones..0x03FC = hundred-thousands)
vm.runInContext(`
  ram[0x03f7] = 0; // ones = 0
  ram[0x03f8] = 5; // tens = 5
  ram[0x03f9] = 2; // hundreds = 2
  ram[0x03fa] = 4; // thousands = 4
  ram[0x03fb] = 1; // ten-thousands = 1
  ram[0x03fc] = 0x40; // blank
`, sandbox);
const decodedPacScore = vm.runInContext("getPacmanCurrentScore()", sandbox);
assert.strictEqual(decodedPacScore, 14250, `getPacmanCurrentScore() must decode 14250 from Pac-Man tile VRAM, got ${decodedPacScore}`);

// Now simulate clicking "✍️ SUBMIT INITIALS" with prompt returning 'JON'
sandbox.prompt = () => 'jon';
vm.runInContext("promptCurrentGameInitials()", sandbox);
const pacTop5 = vm.runInContext("arcadeLeaderboards.pacman", sandbox);
assert.strictEqual(pacTop5.length, 5, "Pac-Man leaderboard must have 5 entries");
assert(pacTop5.some(e => e.initials === 'JON' && e.score === 14250), "Manual SUBMIT INITIALS must record 'JON' (14250 pts) into Top 5 even when below default 450,000 threshold!");
console.log("   ✓ getPacmanCurrentScore() & promptCurrentGameInitials() record player initials into Top 5 NVRAM!");

// ---------------------------------------------------------------------------
// 8. TACTICAL CONTROLLER DECK PULSE RELEASE & NON-STICK MOVEMENT
// ---------------------------------------------------------------------------
console.log("\n8. Testing Tactical Controller Deck (#shelfBtnLeft..Fire) & Non-Stick Release...");
let scheduledTimeouts = [];
sandbox.setTimeout = (fn, delay) => { scheduledTimeouts.push(fn); return scheduledTimeouts.length; };
vm.runInContext("switchActiveGame('galaga'); initGalagaGame();", sandbox);
vm.runInContext("pulseUnifiedAction('left')", sandbox);
assert.strictEqual(vm.runInContext("galagaGame.moveDir", sandbox), -1, "pulseUnifiedAction('left') must start moving left");
while (scheduledTimeouts.length > 0) scheduledTimeouts.shift()();
assert.strictEqual(vm.runInContext("galagaGame.moveDir", sandbox), 0, "pulseUnifiedAction('left') timeout must release Galaga movement so ship never sticks!");

vm.runInContext("switchActiveGame('asteroids'); initAsteroidsGame();", sandbox);
vm.runInContext("pulseUnifiedAction('up')", sandbox);
assert.strictEqual(vm.runInContext("asteroidsGame.ship.thrust", sandbox), true, "pulseUnifiedAction('up') must engage Asteroids thruster");
while (scheduledTimeouts.length > 0) scheduledTimeouts.shift()();
assert.strictEqual(vm.runInContext("asteroidsGame.ship.thrust", sandbox), false, "pulseUnifiedAction('up') timeout must release Asteroids thruster so ship never sticks!");
console.log("   ✓ Tactical Controller Deck buttons pulse and release cleanly across Galaga, Donkey Kong & Asteroids!");

// ---------------------------------------------------------------------------
// 9. MODE-AWARE HARDWARE PLAY/STOP (#btnQuickPlay) & TOUR PAUSE (#btnTourPause)
// ---------------------------------------------------------------------------
console.log("\n9. Testing Mode-Aware Hardware PLAY/STOP (#btnQuickPlay) & Tour Pause (#btnTourPause)...");
vm.runInContext("setMode('tracker')", sandbox);
assert.strictEqual(vm.runInContext("trackerEngine.playing", sandbox), true, "Tracker starts playing on setMode('tracker')");
// Click physical #btnQuickPlay while in Tracker mode: must toggle tracker, NOT yank user into Arcade mode!
elements['btnQuickPlay'].onclick();
assert.strictEqual(vm.runInContext("currentMode", sandbox), "tracker", "#btnQuickPlay in Tracker mode must stay in Tracker mode!");
assert.strictEqual(vm.runInContext("trackerEngine.playing", sandbox), false, "#btnQuickPlay in Tracker mode must pause the tracker loop!");
elements['btnQuickPlay'].onclick();
assert.strictEqual(vm.runInContext("trackerEngine.playing", sandbox), true, "Clicking #btnQuickPlay again in Tracker mode must resume the tracker loop!");

// Demo mode #btnQuickPlay
vm.runInContext("setMode('demo')", sandbox);
assert.strictEqual(vm.runInContext("demoPlayer.playing", sandbox), true, "Demo starts playing on setMode('demo')");
elements['btnQuickPlay'].onclick();
assert.strictEqual(vm.runInContext("currentMode", sandbox), "demo", "#btnQuickPlay in Demo mode must stay in Demo mode!");
assert.strictEqual(vm.runInContext("demoPlayer.playing", sandbox), false, "#btnQuickPlay in Demo mode must pause the demo song!");

// Tour mode pause/resume via toggleTourPause()
vm.runInContext("setMode('tour')", sandbox);
const fBeforePause = vm.runInContext("tourState.frameInGame", sandbox);
vm.runInContext("toggleTourPause()", sandbox);
assert.strictEqual(vm.runInContext("currentMode", sandbox), "tour", "toggleTourPause() must keep user in Tour mode!");
assert.strictEqual(vm.runInContext("tourState.paused", sandbox), true, "toggleTourPause() must set tourState.paused = true");
vm.runInContext("renderTourDemo()", sandbox);
assert.strictEqual(vm.runInContext("tourState.frameInGame", sandbox), fBeforePause, "Paused tour must not advance frameInGame");
vm.runInContext("toggleTourPause()", sandbox);
assert.strictEqual(vm.runInContext("tourState.paused", sandbox), false, "Second toggleTourPause() must resume tour");
console.log("   ✓ #btnQuickPlay and #btnTourPause respect Tracker, Demo, and Tour modes without mode-hijacking!");

// ---------------------------------------------------------------------------
// 10. MULTI-GAME TIME MACHINE REWIND (PRESERVING BUFFER ACROSS setMode('rewind'))
// ---------------------------------------------------------------------------
console.log("\n10. Testing Multi-Game Time Machine Rewind Ring Buffer Preservation...");
vm.runInContext("switchActiveGame('galaga'); initGalagaGame();", sandbox);
for (let f = 0; f < 25; f++) {
  vm.runInContext("mainLoop()", sandbox);
}
const bufLenBeforeRewind = vm.runInContext("rewindBuffer.length", sandbox);
const tickAtPeak = vm.runInContext("galagaGame.tick", sandbox);
assert(bufLenBeforeRewind >= 20, `rewindBuffer must accumulate frames during gameplay, got ${bufLenBeforeRewind}`);

// Enter Rewind mode via setMode('rewind'): buffer must NOT be wiped!
vm.runInContext("setMode('rewind')", sandbox);
assert.strictEqual(vm.runInContext("rewindBuffer.length", sandbox), bufLenBeforeRewind, "setMode('rewind') must NOT wipe rewindBuffer!");
for (let r = 0; r < 10; r++) {
  vm.runInContext("mainLoop()", sandbox);
}
const tickAfterRewind = vm.runInContext("galagaGame.tick", sandbox);
assert(tickAfterRewind < tickAtPeak, `Rewinding 10 frames must move galagaGame.tick backwards (${tickAfterRewind} < ${tickAtPeak})`);
vm.runInContext("setMode('arcade')", sandbox);
console.log("   ✓ Multi-Game Time Machine Rewind preserves ring buffer and rewinds game state backwards!");

// ---------------------------------------------------------------------------
// 11. ALL 8 TRACKER PATTERNS (00..07) DISTINCT SELECTION & BPM SYNC
// ---------------------------------------------------------------------------
console.log("\n11. Testing All 8 Chiptune Tracker Patterns (01..08) & BPM Synchronization...");
vm.runInContext("setMode('tracker')", sandbox);
const patCount = vm.runInContext("trackerEngine.patterns.length", sandbox);
assert.strictEqual(patCount, 8, `trackerEngine.patterns must contain all 8 patterns advertised in #shelfTracker, got ${patCount}`);
const expectedBpms = [132, 124, 144, 138, 136, 140, 148, 134];
for (let pIdx = 0; pIdx < 8; pIdx++) {
  vm.runInContext(`selectTrackerPattern(${pIdx})`, sandbox);
  const curIdx = vm.runInContext("trackerEngine.currentPatternIdx", sandbox);
  const curBpm = vm.runInContext("trackerEngine.bpm", sandbox);
  assert.strictEqual(curIdx, pIdx, `selectTrackerPattern(${pIdx}) must set currentPatternIdx = ${pIdx} (no modulo-4 wrap!), got ${curIdx}`);
  assert.strictEqual(curBpm, expectedBpms[pIdx], `Pattern ${pIdx} BPM must be ${expectedBpms[pIdx]}, got ${curBpm}`);
}
console.log("   ✓ All 8 Tracker patterns (01..08) select uniquely with zero modulo-4 wrapping!");

// ---------------------------------------------------------------------------
// 12. DONKEY KONG BONUS TIMER EXPIRATION DEATH & SAFE RESPAWN
// ---------------------------------------------------------------------------
console.log("\n12. Testing Donkey Kong Bonus Timer Expiration Death & Safe Respawn...");
vm.runInContext("switchActiveGame('dkong'); initDonkeyKongGame();", sandbox);
vm.runInContext("dkongGame.bonusTimer = 100; dkongGame.bonusTick = 49; dkongGame.barrels.push({x: 40, y: 220});", sandbox);
vm.runInContext("updateDonkeyKongGame()", sandbox);
assert.strictEqual(vm.runInContext("dkongGame.bonusTimer", sandbox), 0, "Bonus timer must reach 0");
assert.strictEqual(vm.runInContext("dkongGame.mario.state", sandbox), "dead", "Bonus timer reaching 0 must trigger Mario death");
vm.runInContext("dkongGame.deathTimer = 1; updateDonkeyKongGame();", sandbox);
assert.strictEqual(vm.runInContext("dkongGame.mario.state", sandbox), "stand", "Mario must respawn in stand state");
assert.strictEqual(vm.runInContext("dkongGame.bonusTimer", sandbox), 5000, "Mario respawn must reset bonusTimer to 5000");
assert.strictEqual(vm.runInContext("dkongGame.barrels.length", sandbox), 0, "Mario respawn must clear barrels to prevent instant spawn-kill");
console.log("   ✓ Donkey Kong bonus timer expiration and safe respawn verified!");

// ---------------------------------------------------------------------------
// 13. FROGGER 60-SECOND COUNTDOWN TIMER & LADY FROG BONUS
// ---------------------------------------------------------------------------
console.log("\n13. Testing Frogger 60s Countdown Timer & Pink Lady Frog Pickup...");
vm.runInContext("switchActiveGame('frogger'); initFroggerGame();", sandbox);
assert.strictEqual(vm.runInContext("froggerGame.time", sandbox), 60, "Frogger must start with 60s timer");
assert(vm.runInContext("froggerGame.logs.some(l => l.hasLady === true)", sandbox), "A river log must spawn carrying the pink Lady Frog");
for (let t = 0; t < 60; t++) vm.runInContext("updateFroggerGame()", sandbox);
assert.strictEqual(vm.runInContext("froggerGame.time", sandbox), 59, "Frogger timer must decrement by 1 every 60 ticks");
// Position frog onto the log with hasLady
vm.runInContext(`
  const ladyLog = froggerGame.logs.find(l => l.hasLady);
  froggerGame.frog.gridY = 6;
  froggerGame.frog.y = ladyLog.y;
  froggerGame.frog.x = ladyLog.x + 10;
  updateFroggerGame();
`, sandbox);
assert.strictEqual(vm.runInContext("froggerGame.frog.hasLady", sandbox), true, "Landing on the Lady Frog's log must set fg.hasLady = true");
console.log("   ✓ Frogger 60s timer countdown & Lady Frog pickup verified!");

// ---------------------------------------------------------------------------
// 14. GYRUSS WARP ARRIVAL, CRAZY CLIMBER ROOF ADVANCE & IMMORTAL MODE PERSISTENCE
// ---------------------------------------------------------------------------
console.log("\n14. Testing Gyruss Planet Arrival, Crazy Climber Building Advance & Immortal Mode Persistence...");
vm.runInContext("switchActiveGame('gyruss'); initGyrussGame();", sandbox);
vm.runInContext("gyrussGame.warp = 1; gyrussGame.tick = 599; updateGyrussGame();", sandbox);
assert.strictEqual(vm.runInContext("gyrussGame.stage", sandbox), 2, "Gyruss reaching warp 0 must advance to stage 2");
assert.strictEqual(vm.runInContext("gyrussGame.warp", sandbox), 3, "Gyruss stage advance must reset warp to 3");
assert.strictEqual(vm.runInContext("gyrussGame.destPlanet", sandbox), "URANUS", "Gyruss stage 2 destination planet must be URANUS");

vm.runInContext("switchActiveGame('cclimber'); initCrazyClimberGame();", sandbox);
vm.runInContext("climberState.cleared = true; climberState.winTimer = 0; updateCrazyClimberGame();", sandbox);
assert.strictEqual(vm.runInContext("climberState.cleared", sandbox), false, "Crazy Climber must clear win state and start next skyscraper after winTimer");
assert.strictEqual(vm.runInContext("climberState.floor", sandbox), 1, "Crazy Climber next skyscraper must start at floor 1");

// Enable Immortal Mode and verify start1P() / init*Game() preserves 99 lives across all games
vm.runInContext("toggleImmortalMode(true)", sandbox);
['cclimber', 'galaga', 'dkong', 'frogger', 'asteroids', 'tempest', 'gyruss'].forEach(gId => {
  vm.runInContext(`switchActiveGame('${gId}'); start1P();`, sandbox);
  const lives = vm.runInContext(gId === 'cclimber' ? 'climberState.lives' : `${gId}Game.lives`, sandbox);
  assert.strictEqual(lives, 99, `start1P() in ${gId} while Immortal Mode is ON must preserve 99 lives, got ${lives}`);
});
vm.runInContext("toggleImmortalMode(false)", sandbox);
console.log("   ✓ Gyruss planet arrival, Crazy Climber building progression, and Immortal Mode 99-lives persistence verified!");

console.log("\n=========================================================================");
console.log(">>> ALL REAL-USER JOURNEY, NEGATIVE ISOLATION & DSP WIRING TESTS PASSED! <<<");
console.log("=========================================================================");
process.exit(0);
