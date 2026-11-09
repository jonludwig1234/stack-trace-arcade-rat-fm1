const fs = require('fs');
const html = fs.readFileSync('web/fm1_pacman_preview.html', 'utf8');

// Extract script
const match = html.match(/<script(?:\s+type="text\/javascript")?>([\s\S]*?)<\/script>/i);
if (!match) throw new Error("No script tag found in HTML");
const scriptCode = match[1];

// Setup mock browser globals
global.window = {
  addEventListener: () => {},
  innerWidth: 800,
  innerHeight: 600,
  location: { search: '' }
};
global.requestAnimationFrame = () => {};
global.Image = class {
  constructor() {
    this.src = '';
    this.onload = null;
  }
};
global.document = {
  createElement: (tag) => ({
    className: '',
    classList: { add: () => {}, remove: () => {}, toggle: () => {} },
    dataset: {},
    style: {},
    appendChild: () => {},
    innerHTML: '',
    textContent: ''
  }),
  getElementById: (id) => ({
    classList: { add: () => {}, remove: () => {}, toggle: () => {} },
    style: { setProperty: () => {} },
    innerHTML: '',
    textContent: '',
    appendChild: () => {},
    addEventListener: () => {},
    getContext: () => ({
      fillRect: () => {},
      clearRect: () => {},
      drawImage: () => {},
      fillText: () => {},
      beginPath: () => {},
      arc: () => {},
      fill: () => {},
      stroke: () => {},
      moveTo: () => {},
      lineTo: () => {},
      strokeRect: () => {},
      createLinearGradient: () => ({ addColorStop: () => {} }),
      createImageData: (w, h) => ({ data: new Uint8ClampedArray(w * h * 4) }),
      putImageData: () => {},
      save: () => {},
      restore: () => {},
      translate: () => {},
      rotate: () => {},
      scale: () => {},
      ellipse: () => {}
    })
  }),
  querySelectorAll: () => [],
  querySelector: () => ({
    classList: { add: () => {}, remove: () => {}, toggle: () => {} }
  }),
  addEventListener: () => {}
};

// Mock Web Audio
class MockGain {
  constructor() {
    this.gain = {
      value: 1,
      setValueAtTime: () => {},
      linearRampToValueAtTime: () => {},
      exponentialRampToValueAtTime: () => {}
    };
  }
  connect() {}
}
class MockOsc {
  constructor() {
    this.type = 'sine';
    this.frequency = {
      value: 440,
      setValueAtTime: () => {},
      exponentialRampToValueAtTime: () => {}
    };
  }
  connect() {}
  start() {}
  stop() {}
}

global.AudioContext = class {
  constructor() {
    this.currentTime = 0.5;
    this.sampleRate = 44100;
    this.destination = {};
  }
  createGain() { return new MockGain(); }
  createOscillator() { return new MockOsc(); }
  createBiquadFilter() {
    return {
      type: 'lowpass',
      frequency: { value: 6500, setValueAtTime: () => {} },
      Q: { value: 2 },
      connect: () => {}
    };
  }
  createDelay() { return { delayTime: { value: 0.28 }, connect: () => {} }; }
  createAnalyser() { return { fftSize: 64, connect: () => {} }; }
  createBuffer(channels, length, rate) {
    return { getChannelData: () => new Float32Array(length) };
  }
  createBufferSource() {
    return {
      buffer: null,
      connect: () => {},
      start: () => {},
      stop: () => {}
    };
  }
  createScriptProcessor() { return { connect: () => {} }; }
  resume() {}
};
global.window.AudioContext = global.AudioContext;

// Evaluate the simulator script and export to global
eval(scriptCode + `
global.liveSynth = liveSynth;
global.trackerEngine = trackerEngine;
global.onKeyTouch = onKeyTouch;
global.setMode = setMode;
Object.defineProperty(global, 'currentMode', { get: () => currentMode });
global.renderTrackerScreen = renderTrackerScreen;
global.toggleTracker = toggleTracker;
global.trackerStep = trackerStep;
global.cycleTrackerPattern = cycleTrackerPattern;
global.cycleSynthEngine = cycleSynthEngine;
global.cycleEnvelope = cycleEnvelope;
global.toggleArp = toggleArp;
`);

console.log('=== MULTI-ENGINE SYNTHESIZER VERIFICATION ===');
console.log('liveSynth exists:', typeof liveSynth !== 'undefined');
console.log('Available synth engines:', liveSynth.engineOrder);

// 1. Test each of the 5 synth engines
liveSynth.engineOrder.forEach(eng => {
  liveSynth.currentEngine = eng;
  console.log(`Testing engine [${eng}] (${liveSynth.engineNames[eng]})...`);
  // Play chord across 3 keys
  onKeyTouch(0, true);  // C3
  onKeyTouch(4, true);  // E3
  onKeyTouch(7, true);  // G3
  if (liveSynth.activeVoices.size !== 3) {
    throw new Error(`Expected 3 active voices for ${eng}, got ${liveSynth.activeVoices.size}`);
  }
  // Release chord
  onKeyTouch(0, false);
  onKeyTouch(4, false);
  onKeyTouch(7, false);
  if (liveSynth.activeVoices.size !== 0) {
    throw new Error(`Expected 0 active voices after release for ${eng}, got ${liveSynth.activeVoices.size}`);
  }
  console.log(` Engine [${eng}] polyphonic note on/off verified cleanly!`);
});

// 2. Test cycleSynthEngine, cycleEnvelope, toggleArp
const nextEng = cycleSynthEngine();
console.log('cycleSynthEngine returned:', nextEng);

cycleEnvelope();
console.log('Active envelope:', liveSynth.envelope);

toggleArp();
console.log('Arpeggiator toggled:', liveSynth.arp.active);
onKeyTouch(0, true);
onKeyTouch(7, true);
toggleArp();
console.log('Arpeggiator stopped cleanly:', !liveSynth.arp.active);

console.log('\n=== 16-STEP CHIPTUNE TRACKER VERIFICATION ===');
console.log('trackerEngine exists:', typeof trackerEngine !== 'undefined');
console.log('Loaded tracker patterns:', trackerEngine.patterns.length);
trackerEngine.patterns.forEach((p, idx) => {
  console.log(` Pattern ${idx + 1}: "${p.name}" (${p.bpm} BPM, ${p.chipType})`);
  if (p.steps.length !== 16) throw new Error(`Pattern ${p.name} must have 16 steps!`);
});

// Test start and step execution
setMode('tracker');
console.log('Current mode after setMode("tracker"):', currentMode);
if (!trackerEngine.playing) throw new Error('trackerEngine should be playing in tracker mode!');

// Simulate stepping 16 steps
const startStep = trackerEngine.step;
for (let s = 0; s < 16; s++) {
  trackerStep();
}
console.log('Stepped through 16 tracker steps successfully!');

// Test Tracker Screen rendering
renderTrackerScreen();
console.log('renderTrackerScreen executed without error!');

// Test Tracker Toggle / Stop
toggleTracker();
console.log('trackerEngine.playing after toggleTracker:', trackerEngine.playing);
if (trackerEngine.playing) throw new Error('Tracker should be stopped!');

cycleTrackerPattern();
console.log('Active pattern after cycle:', trackerEngine.patterns[trackerEngine.currentPatternIdx].name);

// Switch back to arcade
setMode('arcade');
console.log('Current mode after setMode("arcade"):', currentMode);
console.log('\nALL TRACKER & MULTI-ENGINE SYNTH CHECKS PASSED 100%!');
process.exit(0);
