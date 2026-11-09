const fs = require('fs');
const html = fs.readFileSync('web/fm1_pacman_preview.html', 'utf8');
const match = html.match(/<script(?:\s+type="text\/javascript")?>([\s\S]*?)<\/script>/i);
const scriptCode = match[1];

function mockParam(val = 0) {
  return { value: val, setValueAtTime: () => {}, linearRampToValueAtTime: () => {}, exponentialRampToValueAtTime: () => {} };
}
const mockAudioCtxClass = class {
  constructor() { this.destination = {}; this.sampleRate = 44100; this.currentTime = 0; }
  createGain() { return { gain: mockParam(1), connect: () => {} }; }
  createOscillator() { return { frequency: mockParam(440), type: "sine", connect: () => {}, start: () => {}, stop: () => {} }; }
  createBiquadFilter() { return { frequency: mockParam(2000), Q: mockParam(1), type: "lowpass", connect: () => {} }; }
  createDelay() { return { delayTime: mockParam(0.2), connect: () => {} }; }
  createScriptProcessor() { return { connect: () => {} }; }
  createAnalyser() { return { fftSize: 2048, getByteFrequencyData: () => {}, connect: () => {} }; }
  createBuffer(c, l, s) { return { getChannelData: () => new Float32Array(l) }; }
  createBufferSource() { return { buffer: null, loop: false, connect: () => {}, start: () => {}, stop: () => {} }; }
};

global.window = {
  addEventListener: () => {},
  innerWidth: 800,
  innerHeight: 600,
  AudioContext: mockAudioCtxClass
};
global.AudioContext = mockAudioCtxClass;
global.Image = class { constructor() { this.src = ""; this.onload = null; } };
global.document = {
  createElement: () => ({ classList: { add: () => {}, remove: () => {}, toggle: () => {} }, dataset: {}, style: {}, appendChild: () => {} }),
  getElementById: (id) => ({ classList: { add: () => {}, remove: () => {}, toggle: () => {} }, style: {}, innerHTML: "", textContent: "", appendChild: () => {}, getContext: () => ({ fillRect: () => {}, clearRect: () => {}, drawImage: () => {}, fillText: () => {}, beginPath: () => {}, arc: () => {}, fill: () => {}, stroke: () => {}, moveTo: () => {}, lineTo: () => {}, createImageData: (w, h) => ({ data: new Uint8ClampedArray(w * h * 4) }), putImageData: () => {} }) }),
  querySelectorAll: () => [],
  addEventListener: () => {}
};
global.requestAnimationFrame = () => {};

const vm = require("vm");
const context = vm.createContext({ ...global, console, setTimeout, clearTimeout, setInterval, clearInterval });
vm.runInContext(scriptCode, context);

vm.runInContext(`
  splashState.active = false;
  for (let f = 0; f < 350; f++) stepCpuFrame();
  console.log("RAM sample at 0x00:", ram.slice(0, 32));
  console.log("RAM sample at 0x40 (video):", ram.slice(0x40, 0x60));
  console.log("RAM color ram at 0x440:", ram.slice(0x440, 0x460));
  console.log("paletteColors sample:", paletteColors.slice(0, 10));
  console.log("paletteRom sample:", paletteRom.slice(0, 20));
  console.log("tiles sample:", tiles.slice(0, 20));
  renderArcadeFrame();
  let distinctColors = new Set();
  for (let i = 0; i < arcadeBuf.length; i++) distinctColors.add(arcadeBuf[i]);
  console.log("distinctColors in arcadeBuf:", [...distinctColors].map(c => "0x" + (c>>>0).toString(16)));

  let distinctBuf32 = new Set();
  for (let i = 0; i < buf32.length; i++) distinctBuf32.add(buf32[i]);
  console.log("distinctColors in buf32:", [...distinctBuf32].map(c => "0x" + (c>>>0).toString(16)));
`, context);
