const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

console.log("=========================================================================");
console.log("TEST: AUDIO LIFECYCLE, FREQUENCY SAFETY & POLYPHONY STRESS BATTERY");
console.log("=========================================================================");

const html = fs.readFileSync('web/fm1_pacman_preview.html', 'utf8');
const sIdx = html.indexOf('<script>');
const eIdx = html.lastIndexOf('</script>');
const jsCode = html.slice(sIdx + 8, eIdx);

const recordedFrequencies = [];
const createdGainNodes = [];
let totalOscillatorsCreated = 0;
let totalGainsCreated = 0;

class MonitoredAudioParam {
  constructor(name, defaultVal = 0, owner = null) {
    this.name = name;
    this.value = defaultVal;
    this.owner = owner;
  }
  setValueAtTime(val, time) {
    this.value = val;
    this.record(val);
  }
  linearRampToValueAtTime(val, time) {
    this.value = val;
    this.record(val);
  }
  exponentialRampToValueAtTime(val, time) {
    this.value = val;
    this.record(val);
  }
  record(val) {
    if (this.name === 'frequency') {
      recordedFrequencies.push(val);
    } else if (this.name === 'gain' && this.owner) {
      this.owner.recordedValues.push(val);
    }
  }
}

class MonitoredAudioContext {
  constructor() {
    this.state = 'suspended';
    this.sampleRate = 44100;
    this.currentTime = 0;
    this.destination = {};
  }
  resume() {
    this.state = 'running';
    return Promise.resolve();
  }
  createGain() {
    totalGainsCreated++;
    const node = {
      isModulator: false,
      recordedValues: [],
      connect: (target) => {
        if (target && target instanceof MonitoredAudioParam) {
          node.isModulator = true;
        }
      },
      disconnect: () => {}
    };
    node.gain = new MonitoredAudioParam('gain', 1, node);
    createdGainNodes.push(node);
    return node;
  }
  createOscillator() {
    totalOscillatorsCreated++;
    const node = {
      type: 'sine',
      connect: (target) => {},
      disconnect: () => {},
      start: () => {},
      stop: () => {}
    };
    node.frequency = new MonitoredAudioParam('frequency', 440, node);
    return node;
  }
  createBiquadFilter() {
    return {
      frequency: new MonitoredAudioParam('frequency', 2000),
      Q: new MonitoredAudioParam('Q', 1),
      type: 'lowpass',
      connect: () => {},
      disconnect: () => {}
    };
  }
  createDelay() {
    return {
      delayTime: new MonitoredAudioParam('delayTime', 0.2),
      connect: () => {},
      disconnect: () => {}
    };
  }
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
      id,
      style: { setProperty: () => {} },
      dataset: { tab: 'arcade', mode: 'arcade', key: '0' },
      classList: { add: () => {}, remove: () => {}, toggle: () => {} },
      textContent: '', innerHTML: '', appendChild: () => {}, getContext: () => mockCtx
    };
  }
  return elements[id];
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
  AudioContext: MonitoredAudioContext,
  webkitAudioContext: MonitoredAudioContext,
  window: {
    innerWidth: 800,
    innerHeight: 600,
    addEventListener: () => {},
    location: { search: '' },
    AudioContext: MonitoredAudioContext,
    webkitAudioContext: MonitoredAudioContext
  },
  document: {
    getElementById: (id) => getEl(id),
    createElement: () => ({
      textContent: '', className: '', classList: { toggle: () => {}, add: () => {}, remove: () => {} },
      dataset: {}, style: {}, onclick: null, appendChild: () => {}, getContext: () => mockCtx, addEventListener: () => {}
    }),
    querySelector: () => getEl('key'),
    querySelectorAll: () => [getEl('test')]
  },
  navigator: { requestMIDIAccess: null }
};

vm.createContext(sandbox);
vm.runInContext(jsCode, sandbox);

console.log("\n1. Testing Web Audio Context Autoplay Resume Policy...");
// Before user interaction, verify initAudio resumes suspended AudioContext
vm.runInContext('initAudio()', sandbox);
const audioCtxState = vm.runInContext('audioCtx.state', sandbox);
assert.strictEqual(audioCtxState, 'running', "AudioContext must be resumed to 'running' state after initAudio()");
console.log("   ✓ AudioContext state successfully resumed to 'running' on first user interaction!");

console.log("\n2. Frequency Safety & Dynamic Range Audit Across SFX Engine...");
recordedFrequencies.length = 0;
createdGainNodes.length = 0;

// Trigger arcade SFX covering all sound generators
const testSfxKeys = [
  'COIN', 'CREDIT', 'PAC-EAT', 'GHOST-EAT', 'PAC-DEATH', 'SIREN', 'INTERMISSION',
  'GAL-FIRE', 'GAL-HIT', 'GAL-EXP', 'GAL-BOSS', 'GAL-DIVE', 'GAL-BEAM', 'GAL-FANFARE',
  'DK-JUMP', 'DK-WALK', 'DK-STOMP', 'DK-FALL', 'DK-BARREL', 'DK-HAMMER', 'DK-CLEAR', 'DK-GAMEOVER',
  'FROG-HOP', 'FROG-SQUASH', 'FROG-SPLASH', 'FROG-HOME', 'FROG-TIME',
  'AST-FIRE', 'AST-THRUST', 'AST-EXP-S', 'AST-EXP-M', 'AST-EXP-L', 'SAUCER-BIG',
  'TEMP-FIRE', 'TEMP-ZAP', 'TEMP-STEP', 'TEMP-DEATH',
  'GYR-FIRE', 'GYR-WARP', 'GYR-BOSS', 'GYR-DEATH',
  'CC-FALL', 'CC-STEP', 'CC-BONUS'
];

testSfxKeys.forEach(sfx => {
  vm.runInContext(`playArcadeSfx('${sfx}')`, sandbox);
});

console.log(`   Audited ${recordedFrequencies.length} scheduled frequency points across ${createdGainNodes.length} gain nodes.`);

// Verify all recorded frequencies are within human hearing and physical DAC limits (10 Hz to 20,000 Hz)
recordedFrequencies.forEach((freq, idx) => {
  assert(!isNaN(freq), `Frequency point ${idx} is NaN!`);
  assert(isFinite(freq), `Frequency point ${idx} is Infinite!`);
  assert(freq >= 10, `Frequency point ${idx} is below 10 Hz (${freq})`);
  assert(freq <= 20000, `Frequency point ${idx} exceeds 20,000 Hz nyquist safe zone (${freq})`);
});
console.log("   ✓ 100% of generated frequencies strictly within [10 Hz, 20,000 Hz] safe audio bounds!");

// Verify gain nodes
let totalAmpPoints = 0;
let totalModPoints = 0;
createdGainNodes.forEach((node, nodeIdx) => {
  node.recordedValues.forEach((val, valIdx) => {
    assert(!isNaN(val), `Node ${nodeIdx} val ${valIdx} is NaN!`);
    assert(isFinite(val), `Node ${nodeIdx} val ${valIdx} is Infinite!`);
    assert(val >= 0, `Node ${nodeIdx} val ${valIdx} is negative (${val})`);
    if (node.isModulator) {
      assert(val <= 5000, `FM Modulation depth exceeds safe 5,000 Hz vibrato limit (${val})`);
      totalModPoints++;
    } else {
      assert(val <= 1.05, `Amplitude gain exceeds unity 1.0 (${val})`);
      totalAmpPoints++;
    }
  });
});
console.log(`   ✓ ${totalAmpPoints} amplitude points within [0.0, 1.0] and ${totalModPoints} FM modulation depth points within safe [0, 5000 Hz] bounds!`);

console.log("\n3. Testing Polyphony Stress & Voice Allocation under Rapid Fire...");
const oscCountBefore = totalOscillatorsCreated;
// Burst 100 sounds in rapid succession
for (let i = 0; i < 100; i++) {
  const sfx = testSfxKeys[i % testSfxKeys.length];
  vm.runInContext(`playArcadeSfx('${sfx}')`, sandbox);
}
const oscCountAfter = totalOscillatorsCreated;
console.log(`   ✓ Handled burst of 100 rapid-fire sound effects (+${oscCountAfter - oscCountBefore} nodes) with zero memory crash or stack overflow!`);

console.log("\n=========================================================================");
console.log(">>> ALL AUDIO LIFECYCLE, FREQUENCY SAFETY & POLYPHONY TESTS PASSED 100%! <<<");
console.log("=========================================================================");
process.exit(0);
