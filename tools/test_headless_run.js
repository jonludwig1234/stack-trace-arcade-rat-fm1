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
  innerHeight: 600
};
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
      strokeRect: () => {},
      moveTo: () => {},
      lineTo: () => {},
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
  addEventListener: () => {}
};
function mockParam(val = 0) {
  return {
    value: val,
    setValueAtTime: () => {},
    linearRampToValueAtTime: () => {},
    exponentialRampToValueAtTime: () => {}
  };
}

global.AudioContext = class {
  constructor() {
    this.destination = {};
    this.sampleRate = 44100;
    this.currentTime = 0;
  }
  createGain() { return { gain: mockParam(1), connect: () => {} }; }
  createOscillator() { return { frequency: mockParam(440), type: 'sine', connect: () => {}, start: () => {}, stop: () => {} }; }
  createBiquadFilter() { return { frequency: mockParam(2000), Q: mockParam(1), type: 'lowpass', connect: () => {} }; }
  createDelay() { return { delayTime: mockParam(0.2), connect: () => {} }; }
  createScriptProcessor() { return { connect: () => {}, onaudioprocess: null }; }
  createAnalyser() { return { fftSize: 2048, getByteFrequencyData: (arr) => arr.fill(128), connect: () => {} }; }
  createBuffer(channels, length, sampleRate) { return { getChannelData: () => new Float32Array(length) }; }
  createBufferSource() { return { buffer: null, loop: false, connect: () => {}, start: () => {}, stop: () => {} }; }
};
global.window.AudioContext = global.AudioContext;
global.requestAnimationFrame = (cb) => setTimeout(cb, 16);

// Evaluate script in sandbox
try {
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
  console.log("Headless script execution passed!");

  // Test game switching & climber climbing inside context
  const climberResult = vm.runInContext(`
    switchActiveGame('cclimber');
    climberStep('left', 'up');
    climberStep('right', 'up');
    ({ floor: climberState.floor, score: climberState.score, activeGame: activeGame })
  `, context);
  console.log("Climber state:", climberResult);
  if (climberResult.floor <= 0) throw new Error("Climber did not climb!");

  // Test 27 SFX invocation inside context
  vm.runInContext(`
    initAudio();
    sfxNames.forEach(name => playArcadeSfx(name));
  `, context);
  console.log("Successfully invoked all 27 SFX synthesizers without crash!");

  console.log("ALL HEADLESS RUNTIME CHECKS PASSED!");
  process.exit(0);
} catch (err) {
  console.error("Runtime evaluation error:", err);
  process.exit(1);
}
