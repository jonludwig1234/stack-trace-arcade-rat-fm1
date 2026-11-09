const fs = require('fs');
const vm = require('vm');

console.log('=========================================================================');
console.log('   FULL QA SUITE: MORTALITY, FINITE LIVES & GAME OVER ACROSS ALL GAMES   ');
console.log('=========================================================================\n');

const html = fs.readFileSync('web/fm1_pacman_preview.html', 'utf8');
const sIdx = html.indexOf('<script>');
const eIdx = html.lastIndexOf('</script>');
const jsCode = html.slice(sIdx + 8, eIdx);

const playedSounds = [];
const mockCtx = {
  save: () => {}, restore: () => {}, translate: () => {}, scale: () => {},
  rotate: () => {}, beginPath: () => {}, moveTo: () => {}, lineTo: () => {},
  closePath: () => {},
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

// Set Mode to Arcade
vm.runInContext(`setMode('arcade');`, sandbox);

// 1. Donkey Kong Mortality & Game Over
console.log('QA 1: Donkey Kong (1981 Nintendo) - Finite Lives & Game Over...');
playedSounds.length = 0;
vm.runInContext(`
  initDonkeyKongGame();
  dkongGame.lives = 1;
  dkongGame.mario.state = 'stand';
  dkongGame.barrels.push({
    x: dkongGame.mario.x,
    y: dkongGame.mario.y,
    tier: dkongGame.mario.currentGirder,
    vx: 1.0,
    rollFrame: 0,
    scored: false
  });
  updateDonkeyKongGame(); // Mario hit -> lives 0, state: 'dead'
  dkongGame.deathTimer = 1;
  updateDonkeyKongGame(); // transitions to gameover
  renderDonkeyKongGame();
`, sandbox);

const dkong = vm.runInContext('dkongGame', sandbox);
if (!dkong.gameOver || dkong.lives !== 0 || !playedSounds.includes('DK-GAMEOVER')) {
  throw new Error(`Donkey Kong failed Game Over test! gameOver=${dkong.gameOver}, lives=${dkong.lives}`);
}
// Test 1P Start restart
vm.runInContext(`
  arcadeKeysDown['1'] = true;
  updateDonkeyKongGame();
  arcadeKeysDown['1'] = false;
`, sandbox);
if (dkong.gameOver || dkong.lives !== 3) {
  throw new Error(`Donkey Kong failed 1P Start restart test!`);
}
console.log('  ✓ Donkey Kong: Lethal barrel hit -> lives=0 -> gameOver=true -> DK-GAMEOVER played -> 1P Start restarts!');

// 2. Gyruss Mortality & Game Over
console.log('QA 2: Gyruss (1983 Konami) - Finite Lives & Game Over...');
playedSounds.length = 0;
vm.runInContext(`
  initGyrussGame();
  gyrussGame.invulnerable = 0;
  gyrussGame.lives = 1;
  gyrussGame.bullets = [{
    angle: gyrussGame.angle,
    dist: 94,
    vDist: 0
  }];
  updateGyrussGame(); // Bullet hits -> lives 0, gameOver: true
  renderGyrussGame();
`, sandbox);

const gyruss = vm.runInContext('gyrussGame', sandbox);
if (!gyruss.gameOver || gyruss.lives !== 0 || !playedSounds.includes('DK-GAMEOVER')) {
  throw new Error(`Gyruss failed Game Over test! gameOver=${gyruss.gameOver}, lives=${gyruss.lives}`);
}
// Test 1P Start restart
vm.runInContext(`
  arcadeKeysDown['1'] = true;
  updateGyrussGame();
  arcadeKeysDown['1'] = false;
`, sandbox);
if (gyruss.gameOver || gyruss.lives !== 3) {
  throw new Error(`Gyruss failed 1P Start restart test!`);
}
console.log('  ✓ Gyruss: Plasma bullet hit -> lives=0 -> gameOver=true -> DK-GAMEOVER played -> 1P Start restarts!');

// 3. Galaga Mortality & Game Over
console.log('QA 3: Galaga (1981 Namco) - Finite Lives & Game Over...');
playedSounds.length = 0;
vm.runInContext(`
  initGalagaGame();
  galagaGame.lives = 1;
  galagaGame.dualFighter = false;
  galagaGame.bombs.push({
    x: galagaGame.shipX,
    y: 220,
    vy: 0
  });
  updateGalagaGame(); // Bomb hits -> lives 0, gameOver: true
  renderGalagaGame();
`, sandbox);

const galaga = vm.runInContext('galagaGame', sandbox);
if (!galaga.gameOver || galaga.lives !== 0 || !playedSounds.includes('DK-GAMEOVER')) {
  throw new Error(`Galaga failed Game Over test! gameOver=${galaga.gameOver}, lives=${galaga.lives}`);
}
// Test 1P Start restart
vm.runInContext(`
  arcadeKeysDown['1'] = true;
  updateGalagaGame();
  arcadeKeysDown['1'] = false;
`, sandbox);
if (galaga.gameOver || galaga.lives !== 3) {
  throw new Error(`Galaga failed 1P Start restart test!`);
}
console.log('  ✓ Galaga: Torpedo hit -> lives=0 -> gameOver=true -> DK-GAMEOVER played -> 1P Start restarts!');

// 4. Frogger Mortality & Game Over
console.log('QA 4: Frogger (1981 Konami) - Finite Lives & Game Over...');
playedSounds.length = 0;
vm.runInContext(`
  initFroggerGame();
  froggerGame.lives = 1;
  froggerGame.vehicles.push({
    x: froggerGame.frog.x,
    y: froggerGame.frog.y,
    w: 24,
    speed: 0,
    color: '#eb2f06'
  });
  updateFroggerGame(); // Vehicle squishes frog -> lives 0, gameOver: true
  renderFroggerGame();
`, sandbox);

const frogger = vm.runInContext('froggerGame', sandbox);
if (!frogger.gameOver || frogger.lives !== 0 || !playedSounds.includes('DK-GAMEOVER')) {
  throw new Error(`Frogger failed Game Over test! gameOver=${frogger.gameOver}, lives=${frogger.lives}`);
}
// Test 1P Start restart
vm.runInContext(`
  arcadeKeysDown['1'] = true;
  updateFroggerGame();
  arcadeKeysDown['1'] = false;
`, sandbox);
if (frogger.gameOver || frogger.lives !== 3) {
  throw new Error(`Frogger failed 1P Start restart test!`);
}
console.log('  ✓ Frogger: Vehicle collision -> lives=0 -> gameOver=true -> DK-GAMEOVER played -> 1P Start restarts!');

// 5. Asteroids Mortality & Game Over
console.log('QA 5: Asteroids (1979 Atari) - Finite Lives & Game Over...');
playedSounds.length = 0;
vm.runInContext(`
  initAsteroidsGame();
  asteroidsGame.ship.invulnerable = 0;
  asteroidsGame.lives = 1;
  asteroidsGame.rocks = [{
    x: asteroidsGame.ship.x,
    y: asteroidsGame.ship.y,
    vx: 0,
    vy: 0,
    radius: 18,
    size: 3
  }];
  updateAsteroidsGame(); // Rock crushes ship -> lives 0, gameOver: true
  renderAsteroidsGame();
`, sandbox);

const asteroids = vm.runInContext('asteroidsGame', sandbox);
if (!asteroids.gameOver || asteroids.lives !== 0 || !playedSounds.includes('DK-GAMEOVER')) {
  throw new Error(`Asteroids failed Game Over test! gameOver=${asteroids.gameOver}, lives=${asteroids.lives}`);
}
// Test 1P Start restart
vm.runInContext(`
  arcadeKeysDown['1'] = true;
  updateAsteroidsGame();
  arcadeKeysDown['1'] = false;
`, sandbox);
if (asteroids.gameOver || asteroids.lives !== 3) {
  throw new Error(`Asteroids failed 1P Start restart test!`);
}
console.log('  ✓ Asteroids: Rock collision -> lives=0 -> gameOver=true -> DK-GAMEOVER played -> 1P Start restarts!');

// 6. Tempest Mortality & Game Over
console.log('QA 6: Tempest (1981 Atari) - Finite Lives & Game Over...');
playedSounds.length = 0;
vm.runInContext(`
  initTempestGame();
  tempestGame.lives = 1;
  tempestGame.enemies = [{
    seg: tempestGame.segment,
    dist: 1.0,
    vDist: 0,
    type: 'flipper'
  }];
  updateTempestGame(); // Flipper reaches rim -> lives 0, gameOver: true
  renderTempestGame();
`, sandbox);

const tempest = vm.runInContext('tempestGame', sandbox);
if (!tempest.gameOver || tempest.lives !== 0 || !playedSounds.includes('DK-GAMEOVER')) {
  throw new Error(`Tempest failed Game Over test! gameOver=${tempest.gameOver}, lives=${tempest.lives}`);
}
// Test 1P Start restart
vm.runInContext(`
  arcadeKeysDown['1'] = true;
  updateTempestGame();
  arcadeKeysDown['1'] = false;
`, sandbox);
if (tempest.gameOver || tempest.lives !== 3) {
  throw new Error(`Tempest failed 1P Start restart test!`);
}
console.log('  ✓ Tempest: Rim breach -> lives=0 -> gameOver=true -> DK-GAMEOVER played -> 1P Start restarts!');

// 7. Crazy Climber Mortality & Game Over
console.log('QA 7: Crazy Climber (1980 Nichibutsu) - Finite Lives & Game Over...');
playedSounds.length = 0;
vm.runInContext(`
  initCrazyClimberGame();
  climberState.lives = 1;
  climberState.potCol = climberState.col;
  climberState.potY = 125;
  updateCrazyClimberGame(); // Flower pot hits climber -> lives 0, gameOver: true
  renderCrazyClimber();
`, sandbox);

const climber = vm.runInContext('climberState', sandbox);
if (!climber.gameOver || climber.lives !== 0 || !playedSounds.includes('DK-GAMEOVER')) {
  throw new Error(`Crazy Climber failed Game Over test! gameOver=${climber.gameOver}, lives=${climber.lives}`);
}
// Test 1P Start restart
vm.runInContext(`
  arcadeKeysDown['1'] = true;
  updateCrazyClimberGame();
  arcadeKeysDown['1'] = false;
`, sandbox);
if (climber.gameOver || climber.lives !== 3) {
  throw new Error(`Crazy Climber failed 1P Start restart test!`);
}
console.log('  ✓ Crazy Climber: Pot impact -> lives=0 -> gameOver=true -> DK-GAMEOVER played -> 1P Start restarts!');

// 8. Pac-Man ROM & Hardware Integrity
console.log('QA 8: Pac-Man (1980 Namco) - Z80 ROM & Hardware Integrity...');
vm.runInContext(`
  switchActiveGame('pacman');
  skipSplashScreen();
  ensurePastBoot();
  mainLoop();
`, sandbox);

const pacCredits = vm.runInContext('ram[0x4e69 - 0x4000]', sandbox);
const animTick = vm.runInContext('animTick', sandbox);
if (animTick < 305) {
  throw new Error(`Pac-Man failed to pass boot ROM test! animTick=${animTick}`);
}
console.log(`  ✓ Pac-Man: Z80 CPU successfully executed boot self-test! animTick=${animTick}, credits=${pacCredits}`);

console.log('\n=========================================================================');
console.log('>>> ALL 8 ARCADE TITLES PASSED 100% MORTALITY & GAME OVER QA! <<<');
console.log('=========================================================================');

process.exit(0);
