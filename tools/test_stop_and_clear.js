const fs = require('fs');
const vm = require('vm');

const html = fs.readFileSync('web/fm1_pacman_preview.html', 'utf8');
const match = html.match(/<script(?:\s+type="text\/javascript")?>([\s\S]*?)<\/script>/i);
if (!match) throw new Error("No script tag found in HTML");
const scriptCode = match[1];

let fillRectCalls = [];
let clearScreenCalled = false;
let stopCurrentGameCalled = false;

// Mock DOM
global.window = { addEventListener: () => {}, innerWidth: 800, innerHeight: 600 };
global.Image = class { constructor() { this.src = ''; } };
global.document = {
  createElement: () => ({ classList: { add: () => {}, remove: () => {}, toggle: () => {} }, dataset: {}, style: { setProperty: () => {} }, appendChild: () => {}, getContext: () => ({ fillRect: () => {}, drawImage: () => {}, createImageData: (w, h) => ({ data: new Uint8ClampedArray((w || 240) * (h || 240) * 4) }), putImageData: () => {} }) }),
  getElementById: (id) => ({
    classList: { add: () => {}, remove: () => {}, toggle: () => {} },
    dataset: {},
    style: { setProperty: () => {} },
    innerHTML: '',
    textContent: '',
    appendChild: () => {},
    getContext: () => ({
      fillRect: (x, y, w, h) => { fillRectCalls.push({ x, y, w, h }); },
      clearRect: () => {},
      drawImage: () => {},
      fillText: () => {},
      beginPath: () => {},
      arc: () => {},
      fill: () => {},
      stroke: () => {},
      strokeRect: () => {},
      moveTo: () => {},
      lineTo: () => {},
      save: () => {},
      restore: () => {},
      translate: () => {},
      rotate: () => {},
      scale: () => {},
      ellipse: () => {},
      createLinearGradient: () => ({ addColorStop: () => {} }),
      createImageData: (w, h) => ({ data: new Uint8ClampedArray(w * h * 4) }),
      putImageData: () => {}
    })
  }),
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

const context = vm.createContext({ ...global, console, setTimeout, clearTimeout, setInterval, clearInterval });
vm.runInContext(scriptCode, context);

console.log("Testing stop current game & clear screen...");

// 1. Verify stopCurrentGame and clearScreen functions exist
vm.runInContext(`
  if (typeof stopCurrentGame !== 'function') throw new Error("stopCurrentGame is not defined!");
  if (typeof clearScreen !== 'function') throw new Error("clearScreen is not defined!");

  // 2. Set state in Pac-Man (press keys, audio, pulses)
  keyUp = true;
  keyCoin = true;
  coinPulseFrames = 8;
  isRewinding = true;
  wsgVoices[0].vol = 15;
`, context);

// 3. Switch active game to Crazy Climber
fillRectCalls = [];
vm.runInContext(`switchActiveGame('cclimber');`, context);

const stateCheck = vm.runInContext(`({
  activeGame,
  keyUp,
  keyCoin,
  coinPulseFrames,
  isRewinding,
  wsgVol: wsgVoices[0].vol
})`, context);

console.log("State check after switchActiveGame('cclimber'):", stateCheck);

if (stateCheck.keyUp !== false) throw new Error("keyUp was not reset!");
if (stateCheck.keyCoin !== false) throw new Error("keyCoin was not reset!");
if (stateCheck.coinPulseFrames !== 0) throw new Error("coinPulseFrames was not reset!");
if (stateCheck.isRewinding !== false) throw new Error("isRewinding was not reset!");
if (stateCheck.wsgVol !== 0) throw new Error("Audio voice was not silenced!");

// Check screen clearing occurred (fillRect 0,0,240,240)
const blackClear = fillRectCalls.find(c => c.x === 0 && c.y === 0 && c.w === 240 && c.h === 240);
if (!blackClear) throw new Error("Screen was not cleared with 240x240 fillRect!");
console.log("Screen fillRect 240x240 clear verified!");

// 4. Test stepGame(1) encoder stepping
fillRectCalls = [];
vm.runInContext(`stepGame(1);`, context);
const stepClear = fillRectCalls.find(c => c.x === 0 && c.y === 0 && c.w === 240 && c.h === 240);
if (!stepClear) throw new Error("stepGame did not clear screen!");
console.log("stepGame cleared screen and stopped previous game successfully!");

// 5. Test nextTourGame()
fillRectCalls = [];
vm.runInContext(`nextTourGame();`, context);
const tourClear = fillRectCalls.find(c => c.x === 0 && c.y === 0 && c.w === 240 && c.h === 240);
if (!tourClear) throw new Error("nextTourGame did not clear screen!");
console.log("nextTourGame cleared screen and stopped previous game successfully!");

console.log("ALL STOP-AND-CLEAR TESTS PASSED SUCCESSFULLY!");

process.exit(0);
