const fs = require('fs');
const vm = require('vm');

console.log("=== VERIFYING STUDIO TABS, SHELVES, 8 ARCADE GAMES & SYNTH STUDIO ===");

const html = fs.readFileSync('web/fm1_pacman_preview.html', 'utf8');
const match = html.match(/<script(?:\s+type="text\/javascript")?>([\s\S]*?)<\/script>/i);
if (!match) throw new Error("No script tag found in HTML");
const scriptCode = match[1];

// Mock DOM
global.window = { addEventListener: () => {}, innerWidth: 1000, innerHeight: 800 };
global.Image = class { constructor() { this.src = ''; } };

const elements = {};
function getOrCreateElem(id) {
  if (!elements[id]) {
    elements[id] = {
      id: id,
      classList: {
        classes: new Set(),
        add: function(c) { this.classes.add(c); },
        remove: function(c) { this.classes.delete(c); },
        toggle: function(c, val) { if (val === undefined) val = !this.classes.has(c); if (val) this.classes.add(c); else this.classes.delete(c); },
        contains: function(c) { return this.classes.has(c); }
      },
      dataset: {},
      style: { setProperty: () => {} },
      innerHTML: '',
      textContent: '',
      appendChild: () => {},
      getContext: () => ({
        fillRect: () => {},
        clearRect: () => {},
        drawImage: () => {},
        fillText: () => {},
        beginPath: () => {},
        arc: () => {},
        fill: () => {},
        stroke: () => {},
        strokeRect: () => {},
        closePath: () => {},
        moveTo: () => {},
        lineTo: () => {},
        save: () => {},
        restore: () => {},
        translate: () => {},
        rotate: () => {},
        scale: () => {},
        ellipse: () => {},
        createLinearGradient: () => ({ addColorStop: () => {} }),
        createRadialGradient: () => ({ addColorStop: () => {} }),
        createImageData: (w, h) => ({ data: new Uint8ClampedArray((w || 240) * (h || 240) * 4) }),
        putImageData: () => {}
      })
    };
  }
  return elements[id];
}

global.document = {
  createElement: (tag) => getOrCreateElem('elem_' + Math.random()),
  getElementById: (id) => getOrCreateElem(id),
  querySelectorAll: () => [],
  addEventListener: () => {}
};

function mockParam(val = 0) {
  return { value: val, setValueAtTime: () => {}, linearRampToValueAtTime: () => {}, exponentialRampToValueAtTime: () => {} };
}
global.AudioContext = class {
  constructor() { this.destination = {}; this.sampleRate = 44100; this.currentTime = 0; }
  createGain() { return { gain: mockParam(1), connect: () => {} }; }
  createOscillator() { return { frequency: mockParam(440), type: 'sine', connect: () => {}, start: () => {}, stop: () => {} }; }
  createBiquadFilter() { return { frequency: mockParam(2000), Q: mockParam(1), type: 'lowpass', connect: () => {} }; }
  createDelay() { return { delayTime: mockParam(0.2), connect: () => {} }; }
  createScriptProcessor() { return { connect: () => {} }; }
  createAnalyser() { return { fftSize: 2048, getByteFrequencyData: () => {}, connect: () => {} }; }
  createBuffer() { return { getChannelData: () => new Float32Array(100) }; }
  createBufferSource() { return { connect: () => {}, start: () => {}, stop: () => {} }; }
};
global.window.AudioContext = global.AudioContext;
global.requestAnimationFrame = () => {};

const context = vm.createContext(global);
vm.runInContext(scriptCode, context);

const getVal = (expr) => vm.runInContext(expr, context);

// 1. Verify Studio Tab switching
console.log("1. Testing Studio Tabs...");
context.setStudioTab('synth');
if (getVal('currentStudioTab') !== 'synth') throw new Error("currentStudioTab should be 'synth'");
if (getVal('currentMode') !== 'synth') throw new Error("currentMode should be 'synth'");
console.log(" Studio tab successfully switched to 'synth'!");

// 2. Test Synth Studio functions
console.log("2. Testing Synth Studio Controls & Soundchips...");
context.setSynthEngine('pokey');
if (getVal('liveSynth.currentEngine') !== 'pokey') throw new Error("Synth engine should be 'pokey'");
context.setSynthEngine('dac');
if (getVal('liveSynth.currentEngine') !== 'dac') throw new Error("Synth engine should be 'dac'");
context.setSynthEngine('fm');
if (getVal('liveSynth.currentEngine') !== 'fm') throw new Error("Synth engine should be 'fm'");

context.setEnvelope('organ');
if (getVal('liveSynth.envelope') !== 'organ') throw new Error("Envelope should be 'organ'");

context.setSynthOctave(2);
if (getVal('liveSynth.octaveOffset') !== 2) throw new Error("Octave offset should be 2");

// Test Vector CRT oscilloscope render
context.renderSynthOscilloscope();
console.log(" renderSynthOscilloscope executed cleanly!");

// 3. Test All 8 Playable Arcade Games
console.log("3. Testing All 8 Playable Arcade Games in Arcade Vault...");
const all8Games = ['pacman', 'cclimber', 'galaga', 'dkong', 'frogger', 'asteroids', 'tempest', 'gyruss'];

for (const g of all8Games) {
  context.switchActiveGame(g);
  if (getVal('activeGame') !== g) throw new Error(`activeGame should be ${g}`);
  if (getVal('currentMode') !== 'arcade') throw new Error(`currentMode should be 'arcade' for ${g}`);
  console.log(` Switched to [${g.toUpperCase()}]: ${elements['engineStatus'].innerHTML || elements['engineStatus'].textContent}`);
}

// 4. Test 16-Step Tracker Controls
console.log("4. Testing 16-Step Tracker Controls...");
context.setStudioTab('tracker');
if (getVal('currentStudioTab') !== 'tracker') throw new Error("currentStudioTab should be 'tracker'");
if (getVal('currentMode') !== 'tracker') throw new Error("currentMode should be 'tracker'");
context.selectTrackerPattern(2);
if (getVal('trackerEngine.currentPatternIdx') !== 2) throw new Error("Tracker pattern should be 2");
context.stepTrackerStep();
console.log(" Tracker step executed cleanly!");

// 5. Test Return to Pac-Man
context.setStudioTab('arcade');
context.switchActiveGame('pacman');
if (getVal('activeGame') !== 'pacman') throw new Error("Active game should be pacman");

console.log("\nALL STUDIO WORKSPACES, 8 ARCADE GAMES & SYNTH STUDIO CHECKS PASSED 100%!");
process.exit(0);
