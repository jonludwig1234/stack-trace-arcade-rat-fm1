const fs = require('fs');
const vm = require('vm');

console.log('=========================================================================');
console.log('      FULL QA: STAGE PROGRESSION, WIN CONDITIONS & LEVEL CLEARS          ');
console.log('=========================================================================\n');

const html = fs.readFileSync('web/fm1_pacman_preview.html', 'utf8');
const sIdx = html.indexOf('<script>');
const eIdx = html.lastIndexOf('</script>');
const jsCode = html.slice(sIdx + 8, eIdx);

const playedSounds = [];
const spokenPhrases = [];
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

// Hook SFX and Speech
vm.runInContext(`
  const origPlayArcadeSfx = playArcadeSfx;
  playArcadeSfx = function(name) {
    playedSounds.push(name);
    try { origPlayArcadeSfx(name); } catch(e) {}
  };
  const origSpeakPhrase = typeof speakPhrase !== 'undefined' ? speakPhrase : null;
  speakPhrase = function(phrase) {
    spokenPhrases.push(phrase);
    if (origSpeakPhrase) try { origSpeakPhrase(phrase); } catch(e) {}
  };
`, sandbox);
sandbox.playedSounds = playedSounds;
sandbox.spokenPhrases = spokenPhrases;

// 1. Donkey Kong Stage Clear & Level Progression
console.log('1. Testing Donkey Kong Stage Clear & Level 2 Progression...');
playedSounds.length = 0;
vm.runInContext(`
  initDonkeyKongGame();
  const initLevel = dkongGame.level;
  // Mario reaches Pauline on Tier 6
  dkongGame.mario.currentGirder = 6;
  dkongGame.mario.x = 120;
  dkongGame.mario.y = 34;
  updateDonkeyKongGame(); // triggers clear & DK-WIN
  if (!dkongGame.cleared || !playedSounds.includes('DK-WIN')) {
    throw new Error('Donkey Kong failed to trigger stage clear upon reaching Pauline!');
  }
  // Fast forward win timer to level transition
  dkongGame.winTimer = 1;
  updateDonkeyKongGame(); // transitions to Level 2
  if (dkongGame.level !== 2 || dkongGame.mario.currentGirder !== 0 || dkongGame.cleared) {
    throw new Error('Donkey Kong failed to transition to Level 2 Tier 0!');
  }
`, sandbox);
console.log('   ✓ Donkey Kong: Pauline reached -> DK-WIN played -> Level 2 reached on Tier 0!');

// 2. Crazy Climber Floor 50 Helicopter Rescue
console.log('2. Testing Crazy Climber Floor 50 Helicopter Rescue...');
playedSounds.length = 0;
spokenPhrases.length = 0;
vm.runInContext(`
  initCrazyClimberGame();
  climberState.floor = 49;
  climberState.col = 1;
  climberState.leftArm = 'down';
  climberStep('left', 'up'); // steps onto Floor 50
  if (!climberState.cleared || !playedSounds.includes('CLIMB-WIN') || !spokenPhrases.includes('STEP IN')) {
    throw new Error('Crazy Climber failed Floor 50 Helicopter rescue!');
  }
`, sandbox);
console.log('   ✓ Crazy Climber: Floor 50 reached -> Helicopter docked -> CLIMB-WIN & "STEP IN" speech triggered!');

// 3. Galaga Fleet Clear & Stage 3 Challenging Stage
console.log('3. Testing Galaga Fleet Clear & Challenging Stage Progression...');
vm.runInContext(`
  initGalagaGame();
  galagaGame.aliens = []; // wipe fleet
  updateGalagaGame(); // advances to stage 2
  if (galagaGame.stage !== 2) throw new Error('Galaga failed to advance to stage 2!');

  galagaGame.aliens = []; // wipe fleet
  updateGalagaGame(); // advances to stage 3 (challenging)
  if (galagaGame.stage !== 3 || !galagaGame.isChallengingStage) {
    throw new Error('Galaga failed to activate Stage 3 Challenging Stage!');
  }
`, sandbox);
console.log('   ✓ Galaga: Fleet wiped -> Stage 2 -> Stage 3 Challenging Stage successfully activated!');

// 4. Frogger 5 Home Bays Clear & Round Bonus
console.log('4. Testing Frogger 5 Home Bays Clear & Round Bonus...');
playedSounds.length = 0;
vm.runInContext(`
  initFroggerGame();
  const initScore = froggerGame.score;
  const bayXList = [20, 68, 116, 164, 212];
  // Land frog in all 5 bays sequentially
  for (let b = 0; b < 5; b++) {
    froggerGame.frog.gridY = 1;
    froggerGame.frog.x = bayXList[b];
    froggerGame.bayCrocodiles[b] = false;
    updateFroggerGame();
  }
  // When 5th bay fills, 1000 bonus is awarded and FROG-FANFARE plays, then bays reset for round 2
  if (froggerGame.score < 3500 || !playedSounds.includes('FROG-FANFARE')) {
    throw new Error('Failed to award 5-bay round bonus or play FROG-FANFARE! Score: ' + froggerGame.score);
  }
`, sandbox);
console.log('   ✓ Frogger: All 5 home bays occupied -> 500 PTS per bay + 1000 PTS round clear bonus awarded cleanly!');

// 5. Asteroids Field Clear & Sector Wave Progression
console.log('5. Testing Asteroids Field Clear & Sector Wave Progression...');
vm.runInContext(`
  initAsteroidsGame();
  asteroidsGame.rocks = []; // all asteroids destroyed
  updateAsteroidsGame(); // triggers wave increment
  if (asteroidsGame.level !== 2 || asteroidsGame.rocks.length === 0) {
    throw new Error('Asteroids failed to advance to Sector 2!');
  }
`, sandbox);
const astRocks = vm.runInContext('asteroidsGame.rocks.length', sandbox);
console.log(`   ✓ Asteroids: Field vaporized -> Sector 2 initiated with ${astRocks} large asteroids!`);

// 6. Tempest Tube Clear & Superzapper Recharge
console.log('6. Testing Tempest Tube Clear & Superzapper Recharge...');
vm.runInContext(`
  initTempestGame();
  tempestGame.superzapperUsed = true;
  tempestGame.enemies = []; // all enemies eliminated
  updateTempestGame(); // triggers tube warp
  if (tempestGame.tube !== 10 || tempestGame.superzapperUsed !== false) {
    throw new Error('Tempest failed to advance tube or recharge Superzapper!');
  }
`, sandbox);
console.log('   ✓ Tempest: Tube cleared -> Warped to Tube 10 -> Superzapper recharged to READY!');

console.log('\n=========================================================================');
console.log('>>> 100% STAGE PROGRESSION & WIN CONDITIONS QA PASSED! <<<');
console.log('=========================================================================');

process.exit(0);
