const fs = require('fs');
const vm = require('vm');

const html = fs.readFileSync('web/fm1_pacman_preview.html', 'utf8');
const match = html.match(/<script(?:\s+type="text\/javascript")?>([\s\S]*?)<\/script>/i);
if (!match) throw new Error("No script tag found in HTML");
const scriptCode = match[1];

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
      fillRect: () => {},
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
      arc: () => {},
      closePath: () => {},
      roundRect: () => {},
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

console.log("=== STRICT GAME ISOLATION VERIFICATION ===");

// 1. Skip splash
vm.runInContext(`skipSplashScreen();`, context);

// 2. Step 50 frames in Pac-Man
for (let f = 0; f < 50; f++) {
  vm.runInContext(`mainLoop();`, context);
}
const pacTickAfter50 = vm.runInContext(`animTick`, context);
console.log("Pac-Man running. animTick after 50 frames:", pacTickAfter50);
if (pacTickAfter50 <= 0) throw new Error("Pac-Man did not run!");

// 3. SWITCH TO CRAZY CLIMBER
console.log("Switching to Crazy Climber...");
vm.runInContext(`switchActiveGame('cclimber');`, context);

const tickAtClimberStart = vm.runInContext(`animTick`, context);
const wsgVolAtStart = vm.runInContext(`wsgVoices[0].vol + wsgVoices[1].vol + wsgVoices[2].vol`, context);
console.log("animTick when switching to Climber:", tickAtClimberStart);
console.log("WSG volume sum when switching to Climber:", wsgVolAtStart);
if (wsgVolAtStart !== 0) throw new Error("WSG voice volumes were not silenced on game switch!");

// 4. Run 100 frames of mainLoop while in Crazy Climber
for (let f = 0; f < 100; f++) {
  vm.runInContext(`mainLoop();`, context);
}

const tickAfter100Climber = vm.runInContext(`animTick`, context);
const wsgVolAfter100Climber = vm.runInContext(`wsgVoices[0].vol + wsgVoices[1].vol + wsgVoices[2].vol`, context);
console.log("animTick after 100 frames of Crazy Climber:", tickAfter100Climber);
console.log("WSG volume sum after 100 frames of Crazy Climber:", wsgVolAfter100Climber);

// THE CRITICAL CHECK: Pac-Man CPU must NOT have advanced a single cycle during Crazy Climber!
if (tickAfter100Climber !== tickAtClimberStart) {
  throw new Error(`FAIL: Pac-Man CPU continued running during Crazy Climber! (animTick went from ${tickAtClimberStart} to ${tickAfter100Climber})`);
}
if (wsgVolAfter100Climber !== 0) {
  throw new Error(`FAIL: Pac-Man WSG audio continued playing during Crazy Climber! (vol = ${wsgVolAfter100Climber})`);
}

console.log("SUCCESS: Pac-Man CPU was 100% frozen and WSG audio was 100% silent while playing Crazy Climber!");

// 5. Test switching to Tour Mode (Galaga)
console.log("Testing Tour Mode game isolation (Galaga)...");
vm.runInContext(`
  setMode('tour');
  tourState.gameIdx = 2; // Galaga
`, context);

const tickAtTourStart = vm.runInContext(`animTick`, context);
for (let f = 0; f < 60; f++) {
  vm.runInContext(`mainLoop();`, context);
}
const tickAfterTour = vm.runInContext(`animTick`, context);
const wsgVolTour = vm.runInContext(`wsgVoices[0].vol + wsgVoices[1].vol + wsgVoices[2].vol`, context);

if (tickAfterTour !== tickAtTourStart) {
  throw new Error(`FAIL: Pac-Man CPU ran during Galaga tour! (animTick changed from ${tickAtTourStart} to ${tickAfterTour})`);
}
if (wsgVolTour !== 0) {
  throw new Error(`FAIL: Pac-Man audio played during Galaga tour!`);
}

console.log("SUCCESS: Pac-Man CPU and audio were 100% frozen during Galaga Tour!");

// 6. Test switching back to Pac-Man
console.log("Switching back to Pac-Man...");
vm.runInContext(`switchActiveGame('pacman');`, context);
for (let f = 0; f < 20; f++) {
  vm.runInContext(`mainLoop();`, context);
}
const tickAfterResume = vm.runInContext(`animTick`, context);
console.log("Pac-Man resumed. animTick:", tickAfterResume);
if (tickAfterResume <= tickAfterTour) {
  throw new Error("Pac-Man did not resume after switching back!");
}

console.log("ALL GAME ISOLATION & CPU/AUDIO COLD-STOP TESTS PASSED 100%!");

process.exit(0);
