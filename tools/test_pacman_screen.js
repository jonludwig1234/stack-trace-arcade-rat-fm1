const fs = require('fs');
const html = fs.readFileSync('web/fm1_pacman_preview.html', 'utf8');

// Extract script
const match = html.match(/<script(?:\s+type="text\/javascript")?>([\s\S]*?)<\/script>/i);
if (!match) throw new Error("No script tag found in HTML");
const scriptCode = match[1];

let pixelsDrawn = 0;
let putImageDataCount = 0;
let lastBuf = null;

// Mock DOM
global.window = {
  addEventListener: () => {},
  innerWidth: 800,
  innerHeight: 600
};
global.Image = class {
  constructor() { this.src = ''; this.onload = null; }
};
global.document = {
  createElement: () => ({
    classList: { add: () => {}, remove: () => {}, toggle: () => {} },
    dataset: {},
    style: {},
    appendChild: () => {}
  }),
  getElementById: (id) => ({
    classList: { add: () => {}, remove: () => {}, toggle: () => {} },
    style: {},
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
      moveTo: () => {},
      lineTo: () => {},
      createImageData: (w, h) => ({ data: new Uint8ClampedArray(w * h * 4) }),
      putImageData: (img, x, y) => {
        putImageDataCount++;
        lastBuf = new Uint32Array(img.data.buffer);
      }
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
  createScriptProcessor() { return { connect: () => {}, onaudioprocess: null }; }
  createAnalyser() { return { fftSize: 2048, getByteFrequencyData: () => {}, connect: () => {} }; }
  createBuffer(c, l, s) { return { getChannelData: () => new Float32Array(l) }; }
  createBufferSource() { return { buffer: null, loop: false, connect: () => {}, start: () => {}, stop: () => {} }; }
};
global.window.AudioContext = global.AudioContext;
global.requestAnimationFrame = (cb) => {};

const vm = require('vm');
const context = vm.createContext({
  ...global,
  console: console,
  setTimeout: setTimeout,
  clearTimeout: clearTimeout,
  setInterval: setInterval,
  clearInterval: clearInterval
});

vm.runInContext(scriptCode, context);

// Test mainLoop execution
console.log("Stepping frames...");
try {
  // Step through splash
  context.skipSplashScreen();
  console.log("Splash skipped. currentMode =", context.currentMode);

  // Run 400 frames of mainLoop
  for (let f = 0; f < 400; f++) {
    context.mainLoop();
  }
  console.log("400 frames executed! animTick =", context.animTick);

  // Check arcadeBuf & buf32 inside VM context
  const stats = vm.runInContext(`
    let nonZeroArcade = 0;
    for (let i = 0; i < arcadeBuf.length; i++) {
      if (arcadeBuf[i] !== 0 && arcadeBuf[i] !== 0xff000000) nonZeroArcade++;
    }
    let nonZeroBuf32 = 0;
    for (let i = 0; i < buf32.length; i++) {
      if (buf32[i] !== 0 && buf32[i] !== 0xff08090c && buf32[i] !== 0xff000000) nonZeroBuf32++;
    }
    ({ nonZeroArcade, nonZeroBuf32, animTick, currentMode, credits: ram[0x4e69 - 0x4000], tilesLen: tiles.length, spritesLen: sprites.length })
  `, context);
  console.log("Stats from VM:", stats);

} catch (err) {
  console.error("Frame execution error:", err);
}
