const fs = require('fs');
const vm = require('vm');

console.log('=== GYRUSS MORTAL MECHANICS & CIRCULAR ANGLE TEST RIG ===');

const html = fs.readFileSync('web/fm1_pacman_preview.html', 'utf8');
const sIdx = html.indexOf('<script>');
const eIdx = html.lastIndexOf('</script>');
const jsCode = html.slice(sIdx + 8, eIdx);

const playedSounds = [];
const mockCtx = {
  save: () => {}, restore: () => {}, translate: () => {}, scale: () => {},
  rotate: () => {}, beginPath: () => {}, moveTo: () => {}, lineTo: () => {},
  stroke: () => {}, fill: () => {}, arc: () => {}, rect: () => {},
  roundRect: () => {}, strokeRect: () => {}, fillRect: () => {}, clearRect: () => {},
  drawImage: () => {}, fillText: () => {},
  createLinearGradient: () => ({ addColorStop: () => {} }),
  createRadialGradient: () => ({ addColorStop: () => {} }),
  createImageData: (w, h) => ({ data: new Uint8ClampedArray((w || 240) * (h || 240) * 4) }),
  putImageData: () => {}, font: '', fillStyle: '', strokeStyle: '', lineWidth: 1
};

function mockParam(val = 0) {
  return { value: val, setValueAtTime: () => {}, linearRampToValueAtTime: () => {}, exponentialRampToValueAtTime: () => {} };
}

class MockAudioContext {
  constructor() { this.destination = {}; this.sampleRate = 44100; this.currentTime = 0; }
  createGain() { return { gain: mockParam(1), connect: () => {} }; }
  createOscillator() { return { frequency: mockParam(440), type: 'sine', connect: () => {}, start: () => {}, stop: () => {} }; }
  createBiquadFilter() { return { frequency: mockParam(2000), Q: mockParam(1), type: 'lowpass', connect: () => {} }; }
  createDelay() { return { delayTime: mockParam(0.2), connect: () => {} }; }
  createScriptProcessor() { return { connect: () => {} }; }
  createAnalyser() { return { fftSize: 2048, getByteFrequencyData: () => {}, connect: () => {} }; }
  createBuffer() { return { getChannelData: () => new Float32Array(100) }; }
  createBufferSource() { return { connect: () => {}, start: () => {}, stop: () => {} }; }
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
  AudioContext: MockAudioContext,
  webkitAudioContext: MockAudioContext,
  window: {
    addEventListener: () => {},
    location: { search: '' },
    AudioContext: MockAudioContext,
    webkitAudioContext: MockAudioContext
  },
  document: {
    createElement: () => ({
      textContent: '', className: '', classList: { toggle: () => {}, add: () => {}, remove: () => {} },
      dataset: {}, style: {}, onclick: null, appendChild: () => {}, getContext: () => mockCtx, addEventListener: () => {}
    }),
    getElementById: () => ({
      textContent: '', className: '', classList: { toggle: () => {}, add: () => {}, remove: () => {} },
      style: {}, onclick: null, appendChild: () => {}, getContext: () => mockCtx, addEventListener: () => {}
    }),
    querySelectorAll: () => []
  }
};

vm.createContext(sandbox);
vm.runInContext(jsCode, sandbox);

// Hook SFX
vm.runInContext(`
  const origPlayArcadeSfx = playArcadeSfx;
  playArcadeSfx = function(name) {
    playedSounds.push(name);
    try { origPlayArcadeSfx(name); } catch(e) {}
  };
`, sandbox);

sandbox.playedSounds = playedSounds;
const gyruss = vm.runInContext('gyrussGame', sandbox);

// 1. Verify Circular Angle Normalization & Difference Helper
console.log('1. Testing Circular Angle Difference Helper & Modulo Wrapping...');
const testDiff1 = vm.runInContext(`gyrussAngleDiff(0.1, 6.20)`, sandbox);
const testDiff2 = vm.runInContext(`gyrussAngleDiff(15.0, 15.0 + Math.PI * 4)`, sandbox);
const testDiff3 = vm.runInContext(`gyrussAngleDiff(Math.PI, -Math.PI)`, sandbox);

console.log(`   gyrussAngleDiff(0.1, 6.20) = ${testDiff1.toFixed(3)} (expected ~0.183)`);
console.log(`   gyrussAngleDiff(15.0, 15.0 + 4*PI) = ${testDiff2.toFixed(3)} (expected 0.000)`);
console.log(`   gyrussAngleDiff(PI, -PI) = ${testDiff3.toFixed(3)} (expected 0.000)`);

if (testDiff1 > 0.25 || testDiff2 > 0.001 || testDiff3 > 0.001) {
  throw new Error('gyrussAngleDiff failed circular wrap test!');
}
console.log('   ✓ Circular angle arithmetic mathematically verified!');

// 2. Test Player Ship Hit by Enemy after Arbitrary Rotations
console.log('2. Testing Player Ship Hit by Enemy after Multi-Turn Rotation...');
playedSounds.length = 0;
vm.runInContext(`
  setMode('arcade');
  initGyrussGame();
  gyrussGame.invulnerable = 0;
  // Rotate ship 5 full turns (10 * PI radians)
  gyrussGame.angle = 10 * Math.PI + 1.25;
  gyrussGame.lives = 3;
  gyrussGame.enemies = [{
    angle: 1.25, // identical circular position!
    dist: 94,
    vDist: 0,
    vAngle: 0
  }];
  updateGyrussGame();
`, sandbox);

if (gyruss.lives !== 2 || gyruss.explosions.length === 0 || !playedSounds.includes('GYRUSS-EXP')) {
  throw new Error(`Player ship failed to die upon enemy collision! lives: ${gyruss.lives}, exp: ${gyruss.explosions.length}`);
}
console.log(`   ✓ Player successfully destroyed by enemy! lives: ${gyruss.lives}, explosions: ${gyruss.explosions.length}`);
console.log(`   ✓ Audio triggered: GYRUSS-EXP (${playedSounds.includes('GYRUSS-EXP')})`);

// 3. Test Player Ship Hit by Enemy Plasma Bullet
console.log('3. Testing Player Ship Hit by Enemy Plasma Bullet...');
playedSounds.length = 0;
vm.runInContext(`
  gyrussGame.invulnerable = 0;
  gyrussGame.respawnTimer = 0;
  gyrussGame.bullets = [{
    angle: gyrussGame.angle,
    dist: 94,
    vDist: 0
  }];
  updateGyrussGame();
`, sandbox);

if (gyruss.lives !== 1 || !playedSounds.includes('GYRUSS-EXP')) {
  throw new Error(`Player ship failed to die from enemy plasma bullet! lives: ${gyruss.lives}`);
}
console.log(`   ✓ Player successfully destroyed by plasma bullet! lives: ${gyruss.lives}`);

// 4. Test Final Life Loss and Transition to GAME OVER
console.log('4. Testing Final Life Loss & Authentic GAME OVER State Machine...');
playedSounds.length = 0;
vm.runInContext(`
  gyrussGame.invulnerable = 0;
  gyrussGame.respawnTimer = 0;
  gyrussGame.bullets = [{
    angle: gyrussGame.angle,
    dist: 94,
    vDist: 0
  }];
  updateGyrussGame();
`, sandbox);

if (gyruss.lives !== 0 || !gyruss.gameOver || !playedSounds.includes('DK-GAMEOVER')) {
  throw new Error(`Failed to enter GAME OVER! lives: ${gyruss.lives}, gameOver: ${gyruss.gameOver}`);
}
console.log(`   ✓ Lives depleted to 0 -> gyrussGame.gameOver: ${gyruss.gameOver}`);
console.log(`   ✓ Authentic Game Over fanfare played: ${playedSounds.includes('DK-GAMEOVER')}`);

// 5. Verify GAME OVER Overlay Rendering
console.log('5. Testing GAME OVER Overlay Rendering...');
vm.runInContext(`
  renderGyrussGame();
`, sandbox);
console.log('   ✓ renderGyrussGame() rendered GAME OVER screen cleanly!');

// 6. Test Restart from GAME OVER via 1P Start key
console.log('6. Testing Restart via 1P Start Key...');
vm.runInContext(`
  arcadeKeysDown['1'] = true;
  updateGyrussGame();
  arcadeKeysDown['1'] = false;
`, sandbox);

if (gyruss.gameOver || gyruss.lives !== 3) {
  throw new Error(`Failed to restart fresh game from Game Over! gameOver: ${gyruss.gameOver}, lives: ${gyruss.lives}`);
}
console.log(`   ✓ Fresh game successfully started! gameOver: ${gyruss.gameOver}, lives: ${gyruss.lives}`);

console.log('\n>>> ALL GYRUSS MORTAL MECHANICS & FINITE LIVES TESTS PASSED 100%! <<<');

process.exit(0);
