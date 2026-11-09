const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

console.log("=========================================================================");
console.log("TEST: UNIVERSAL IMMORTAL (GOD) MODE & LEVEL SKIP ENGINE (ALL 8 GAMES)");
console.log("=========================================================================");

const html = fs.readFileSync('web/fm1_pacman_preview.html', 'utf8');
const sIdx = html.indexOf('<script>');
const eIdx = html.lastIndexOf('</script>');
const jsCode = html.slice(sIdx + 8, eIdx);

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

const elements = {};
function getEl(id) {
  if (!elements[id]) {
    elements[id] = {
      id,
      style: { setProperty: () => {}, display: '' },
      dataset: { tab: 'arcade', mode: 'arcade', key: '0' },
      classList: {
        classes: new Set(),
        add: function(c) { this.classes.add(c); },
        remove: function(c) { this.classes.delete(c); },
        toggle: function(c, v) { if (v !== undefined) { if (v) this.classes.add(c); else this.classes.delete(c); } else { if (this.classes.has(c)) this.classes.delete(c); else this.classes.add(c); } return this.classes.has(c); },
        contains: function(c) { return this.classes.has(c); }
      },
      textContent: '', innerHTML: '', appendChild: () => {}, getContext: () => mockCtx
    };
  }
  return elements[id];
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
    innerWidth: 800,
    innerHeight: 600,
    addEventListener: () => {},
    location: { search: '' },
    AudioContext: MockAudioContext,
    webkitAudioContext: MockAudioContext
  },
  document: {
    getElementById: (id) => getEl(id),
    createElement: () => ({
      textContent: '', className: '', classList: { toggle: () => {}, add: () => {}, remove: () => {} },
      dataset: {}, style: {}, onclick: null, appendChild: () => {}, getContext: () => mockCtx, addEventListener: () => {}
    }),
    querySelector: () => getEl('key'),
    querySelectorAll: () => [getEl('test')]
  },
  navigator: { requestMIDIAccess: null }
};

vm.createContext(sandbox);
vm.runInContext(jsCode, sandbox);

console.log("\n=========================================================================");
console.log("PHASE 1: TESTING IMMORTAL (GOD) MODE ACROSS ALL 8 ARCADE TITLES");
console.log("=========================================================================");

// 1. Verify toggleImmortalMode toggles on
const godActive = vm.runInContext('toggleImmortalMode(true)', sandbox);
assert.strictEqual(godActive, true, "toggleImmortalMode(true) must return true");
assert.strictEqual(vm.runInContext('arcadeImmortalMode', sandbox), true, "arcadeImmortalMode must be true");
console.log("   ✓ toggleImmortalMode(true) engaged global UNLIMITED LIVES!");

// 2. Test Pac-Man Z80 Unlimited Lives Patch
console.log("\n1. Testing Pac-Man Authentic Z80 ROM Unlimited Lives Patch...");
const pByte1 = vm.runInContext('prgRom[0x0315]', sandbox);
const pByte2 = vm.runInContext('prgRom[0x0316]', sandbox);
assert.strictEqual(pByte1, 0x00, "Pac-Man ROM 0x0315 must be patched to 0x00 (NOP)");
assert.strictEqual(pByte2, 0x00, "Pac-Man ROM 0x0316 must be patched to 0x00 (NOP)");
const pacLives = vm.runInContext('ram[0x4e6e - 0x4000]', sandbox);
assert.strictEqual(pacLives, 99, "Pac-Man RAM lives at 0x4e6e must be set to 99 (Unlimited Lives)");
console.log("   ✓ Pac-Man Z80 Program ROM verified patched with authentic NOP SUB 1 unlimited lives routine!");

// 3. Test Donkey Kong Unlimited Lives
console.log("\n2. Testing Donkey Kong Mario Unlimited Lives (Barrels & Fireballs)...");
vm.runInContext("switchActiveGame('dkong')", sandbox);
const dkong = vm.runInContext('dkongGame', sandbox);
dkong.mario.state = 'stand';
dkong.lives = 99;
dkong.gameOver = false;
// Spawn barrel directly on Mario
dkong.barrels.push({
  x: dkong.mario.x,
  y: dkong.mario.y,
  tier: dkong.mario.currentGirder,
  vx: 0,
  vy: 0,
  rollFrame: 0,
  scored: false,
  state: 'rolling'
});
vm.runInContext('updateDonkeyKongGame()', sandbox);
assert.strictEqual(dkong.lives, 99, "Donkey Kong lives must remain 99 when immortal (unlimited lives)");
assert.strictEqual(dkong.mario.state, 'dead', "Mario enters dead animation state on hit");
assert.strictEqual(dkong.gameOver, false, "Game Over must not trigger when immortal");
// Advance death timer to simulate complete respawn
dkong.deathTimer = 1;
vm.runInContext('updateDonkeyKongGame()', sandbox);
assert.strictEqual(dkong.mario.state, 'stand', "Mario respawns to stand state with unlimited lives intact");
assert.strictEqual(dkong.mario.x, 40, "Mario respawns at girder 0 starting position");
assert.strictEqual(dkong.lives, 99, "Donkey Kong lives remain 99 after respawn");
console.log("   ✓ Mario plays authentic death sequence and respawns with UNLIMITED LIVES (Lives: 99, State: stand)!");

// 4. Test Galaga Unlimited Lives
console.log("\n3. Testing Galaga Ship Unlimited Lives (Kamikaze Aliens & Bombs)...");
vm.runInContext("switchActiveGame('galaga')", sandbox);
const galaga = vm.runInContext('galagaGame', sandbox);
galaga.shipX = 120;
galaga.lives = 99;
galaga.gameOver = false;
// Spawn diving alien on ship
galaga.aliens.push({ x: 120, y: 220, state: 'dive', homeX: 120, homeY: 40, diveTick: 10, type: 'boss', hp: 2 });
// Spawn bomb on ship
galaga.bombs.push({ x: 120, y: 220, vy: 2 });
vm.runInContext('updateGalagaGame()', sandbox);
assert.strictEqual(galaga.lives, 99, "Galaga lives must remain 99 when immortal (unlimited lives)");
assert.strictEqual(galaga.gameOver, false, "Galaga must not Game Over when immortal");
assert(galaga.explosions.length > 0, "Galaga ship creates authentic death explosion on hit");
console.log("   ✓ Galaga fighter explodes authentically and respawns with UNLIMITED LIVES (Lives: 99)!");

// 5. Test Frogger Unlimited Lives
console.log("\n4. Testing Frogger Unlimited Lives (Traffic Squish & River Drowning)...");
vm.runInContext("switchActiveGame('frogger')", sandbox);
const frogger = vm.runInContext('froggerGame', sandbox);
frogger.frog.x = 100;
frogger.frog.y = 100;
frogger.frog.gridY = 4; // in deep river without log
frogger.lives = 99;
frogger.gameOver = false;
// Put truck directly on frog
frogger.vehicles.push({ x: 100, y: 100, speed: 2, w: 24, type: 'truck' });
vm.runInContext('updateFroggerGame()', sandbox);
assert.strictEqual(frogger.lives, 99, "Frogger lives must remain 99 when immortal (unlimited lives)");
assert.strictEqual(frogger.gameOver, false, "Frogger must not Game Over when immortal");
assert.strictEqual(frogger.frog.x, 120, "Frogger respawns at bottom starting dock");
assert.strictEqual(frogger.frog.y, 224, "Frogger respawns at bottom starting dock");
console.log("   ✓ Frogger plays splat/splash and respawns at bottom dock with UNLIMITED LIVES (Lives: 99)!");

// 6. Test Asteroids Unlimited Lives
console.log("\n5. Testing Asteroids Unlimited Lives (Asteroid Impacts & Saucer Torpedoes)...");
vm.runInContext("switchActiveGame('asteroids')", sandbox);
const ast = vm.runInContext('asteroidsGame', sandbox);
ast.ship.x = 120;
ast.ship.y = 120;
ast.ship.invulnerable = 0;
ast.lives = 99;
ast.gameOver = false;
// Put large asteroid on ship
ast.rocks.push({ x: 120, y: 120, vx: 0, vy: 0, radius: 18, size: 3 });
// Put saucer sniper bullet on ship
ast.saucerBullets.push({ x: 120, y: 120, vx: 1, vy: 1, life: 50 });
vm.runInContext('updateAsteroidsGame()', sandbox);
assert.strictEqual(ast.lives, 99, "Asteroids lives must remain 99 when immortal (unlimited lives)");
assert.strictEqual(ast.gameOver, false, "Asteroids must not Game Over when immortal");
assert.strictEqual(ast.ship.x, 120, "Ship respawns at center");
assert(ast.ship.invulnerable > 0, "Ship gains respawn invulnerability shield");
console.log("   ✓ Asteroids ship explodes and respawns with UNLIMITED LIVES (Lives: 99)!");

// 7. Test Tempest Unlimited Lives
console.log("\n6. Testing Tempest Unlimited Lives (Flipper & Spiker Rim Breaches)...");
vm.runInContext("switchActiveGame('tempest')", sandbox);
const tem = vm.runInContext('tempestGame', sandbox);
tem.segment = 4;
tem.lives = 99;
tem.gameOver = false;
// Place flipper right at player rim segment
tem.enemies.push({ seg: 4, dist: 1.05, vDist: 0.01, type: 'flipper' });
vm.runInContext('updateTempestGame()', sandbox);
assert.strictEqual(tem.lives, 99, "Tempest lives must remain 99 when immortal (unlimited lives)");
assert.strictEqual(tem.gameOver, false, "Tempest must not Game Over when immortal");
console.log("   ✓ Tempest claw blaster destroyed and tube reset with UNLIMITED LIVES (Lives: 99)!");

// 8. Test Gyruss Unlimited Lives
console.log("\n7. Testing Gyruss Unlimited Lives (Direct Ship Impact & Outward Plasma)...");
vm.runInContext("switchActiveGame('gyruss')", sandbox);
const gyr = vm.runInContext('gyrussGame', sandbox);
gyr.angle = 1.5;
gyr.invulnerable = 0;
gyr.lives = 99;
gyr.gameOver = false;
// Place enemy on player ship coordinates
gyr.enemies.push({ angle: 1.5, dist: 96, vAngle: 0, vDist: 0 });
// Place outward plasma bullet on player ship
gyr.bullets.push({ angle: 1.5, dist: 96, vDist: 2 });
vm.runInContext('updateGyrussGame()', sandbox);
assert.strictEqual(gyr.lives, 99, "Gyruss lives must remain 99 when immortal (unlimited lives)");
assert.strictEqual(gyr.gameOver, false, "Gyruss must not Game Over when immortal");
assert(gyr.explosions.length > 0, "Gyruss ship creates 360 debris explosion on hit");
assert(gyr.respawnTimer > 0, "Gyruss ship respawns with active timer");
console.log("   ✓ Gyruss starfighter explodes with 360 debris and respawns with UNLIMITED LIVES (Lives: 99)!");

// 9. Test Crazy Climber Unlimited Lives
console.log("\n8. Testing Crazy Climber Unlimited Lives (Falling Flowerpots & Gorilla Punches)...");
vm.runInContext("switchActiveGame('cclimber')", sandbox);
const cc = vm.runInContext('climberState', sandbox);
cc.col = 2;
cc.floor = 20;
cc.potCol = 2;
cc.potY = 125; // hit zone
cc.lives = 99;
cc.gameOver = false;
vm.runInContext('updateCrazyClimberGame()', sandbox);
assert.strictEqual(cc.lives, 99, "Crazy Climber lives must remain 99 when immortal (unlimited lives)");
assert.strictEqual(cc.gameOver, false, "Crazy Climber must not Game Over when immortal");
assert.strictEqual(cc.floor, 18, "Climber authentically drops 2 floors from flowerpot hit");
console.log("   ✓ Crazy Climber drops floors and continues climbing with UNLIMITED LIVES (Lives: 99, Floor: 18)!");

// 10. Test toggleImmortalMode(false) restores mortality
console.log("\n9. Testing toggleImmortalMode(false) Clean Deactivation & ROM Restoration...");
vm.runInContext('toggleImmortalMode(false)', sandbox);
assert.strictEqual(vm.runInContext('arcadeImmortalMode', sandbox), false);
const restoredPByte = vm.runInContext('prgRom[0x0315]', sandbox);
assert.strictEqual(restoredPByte, 0xd6, "Pac-Man ROM must restore SUB 1 (0xD6) opcode when immortal mode disabled");
const restoredPacLives = vm.runInContext('ram[0x4e6e - 0x4000]', sandbox);
assert.strictEqual(restoredPacLives, 3, "Pac-Man RAM lives must restore to authentic 3 lives");
console.log("   ✓ Immortal mode disabled cleanly; original Pac-Man ROM code and authentic 3 lives restored!");

console.log("\n=========================================================================");
console.log("PHASE 2: TESTING LEVEL SKIP (STAGE WARP) ACROSS ALL 8 ARCADE TITLES");
console.log("=========================================================================");

// 1. Pac-Man Level Skip (Stage Warp & Full Maze Replenishment)
console.log("\n1. Testing Pac-Man Level Skip (Stage Warp & Full Maze Replenishment)...");
vm.runInContext("switchActiveGame('pacman')", sandbox);
const pacRam = vm.runInContext('ram', sandbox);

// Simulate partially cleared maze (50 dots eaten, 1 energizer eaten)
pacRam[0x4e0e - 0x4000] = 50;
pacRam[100] = 0x40; // blank out an energizer
pacRam[98] = 0x40;  // blank out a dot

const pacSkipRes = vm.runInContext('skipCurrentLevel()', sandbox);
assert(pacSkipRes.includes('PAC-MAN'), "Must return Pac-Man level skip banner");

// Verify that all 240 pellets and 4 energizers are fully replenished:
let pacDots = 0, pacEnergizers = 0;
for (let i = 0; i < 0x400; i++) {
  if (pacRam[i] === 0x10) pacDots++;
  if (pacRam[i] === 0x14) pacEnergizers++;
}
assert.strictEqual(pacDots, 240, "Pac-Man maze must always have exactly 240 pellets on level skip");
assert.strictEqual(pacEnergizers, 4, "Pac-Man maze must always have exactly 4 energizers (power pills) on level skip");
assert.strictEqual(pacRam[0x4e0e - 0x4000], 0, "Remaining dots counter must be reset to 0 for fresh maze");
assert.strictEqual(pacRam[0x4e14 - 0x4000], 1, "Energizer master subsystem flag must be active (1) so power pills work");
assert.strictEqual(pacRam[100], 0x14, "Energizer tile 100 must be restored");
assert.strictEqual(pacRam[98], 0x10, "Dot tile 98 must be restored");
console.log(`   ✓ ${pacSkipRes} verified (240 pellets & 4 power pills replenished, energizer subsystem active)!`);

// 2. Donkey Kong Level Skip
console.log("\n2. Testing Donkey Kong Level Skip (Stage Advance)...");
vm.runInContext("switchActiveGame('dkong')", sandbox);
const dkongLvlBefore = vm.runInContext('dkongGame.level', sandbox);
const dkongSkipRes = vm.runInContext('skipCurrentLevel()', sandbox);
const dkongLvlAfter = vm.runInContext('dkongGame.level', sandbox);
assert.strictEqual(dkongLvlAfter, dkongLvlBefore + 1, "Donkey Kong level must advance by 1");
assert.strictEqual(vm.runInContext('dkongGame.cleared', sandbox), false);
assert.strictEqual(vm.runInContext('dkongGame.mario.state', sandbox), 'stand');
console.log(`   ✓ ${dkongSkipRes}: Advanced from Level ${dkongLvlBefore} -> Level ${dkongLvlAfter}!`);

// 3. Galaga Level Skip
console.log("\n3. Testing Galaga Level Skip (Wave Advance)...");
vm.runInContext("switchActiveGame('galaga')", sandbox);
const galagaStageBefore = vm.runInContext('galagaGame.stage', sandbox);
const galagaSkipRes = vm.runInContext('skipCurrentLevel()', sandbox);
const galagaStageAfter = vm.runInContext('galagaGame.stage', sandbox);
assert.strictEqual(galagaStageAfter, galagaStageBefore + 1, "Galaga stage must advance by 1");
assert(vm.runInContext('galagaGame.aliens.length', sandbox) > 0, "New alien fleet must be spawned");
console.log(`   ✓ ${galagaSkipRes}: Advanced from Stage ${galagaStageBefore} -> Stage ${galagaStageAfter}!`);

// 4. Frogger Level Skip
console.log("\n4. Testing Frogger Level Skip (Round Advance)...");
vm.runInContext("switchActiveGame('frogger')", sandbox);
const froggerLvlBefore = vm.runInContext('froggerGame.level', sandbox);
const froggerSkipRes = vm.runInContext('skipCurrentLevel()', sandbox);
const froggerLvlAfter = vm.runInContext('froggerGame.level', sandbox);
const bays = vm.runInContext('froggerGame.homeBays', sandbox);
assert.strictEqual(froggerLvlAfter, froggerLvlBefore + 1, "Frogger level must advance by 1");
assert(bays.every(b => b === false), "Home bays must reset to false for new round");
console.log(`   ✓ ${froggerSkipRes}: Advanced from Level ${froggerLvlBefore} -> Level ${froggerLvlAfter}!`);

// 5. Asteroids Level Skip
console.log("\n5. Testing Asteroids Level Skip (Sector Advance)...");
vm.runInContext("switchActiveGame('asteroids')", sandbox);
const astLvlBefore = vm.runInContext('asteroidsGame.level', sandbox);
const astSkipRes = vm.runInContext('skipCurrentLevel()', sandbox);
const astLvlAfter = vm.runInContext('asteroidsGame.level', sandbox);
assert.strictEqual(astLvlAfter, astLvlBefore + 1, "Asteroids sector must advance by 1");
assert(vm.runInContext('asteroidsGame.rocks.length', sandbox) > 0, "New rock field must be generated");
console.log(`   ✓ ${astSkipRes}: Advanced from Sector ${astLvlBefore} -> Sector ${astLvlAfter}!`);

// 6. Tempest Level Skip
console.log("\n6. Testing Tempest Level Skip (Tube Advance)...");
vm.runInContext("switchActiveGame('tempest')", sandbox);
const temTubeBefore = vm.runInContext('tempestGame.tube', sandbox);
const temSkipRes = vm.runInContext('skipCurrentLevel()', sandbox);
const temTubeAfter = vm.runInContext('tempestGame.tube', sandbox);
assert.strictEqual(temTubeAfter, temTubeBefore + 1, "Tempest tube must advance by 1");
assert.strictEqual(vm.runInContext('tempestGame.superzapperUsed', sandbox), false, "Superzapper must be recharged");
console.log(`   ✓ ${temSkipRes}: Advanced from Tube ${temTubeBefore} -> Tube ${temTubeAfter}!`);

// 7. Gyruss Level Skip
console.log("\n7. Testing Gyruss Level Skip (Warp Towards Earth)...");
vm.runInContext("switchActiveGame('gyruss')", sandbox);
const gyrStageBefore = vm.runInContext('gyrussGame.stage', sandbox);
const gyrSkipRes = vm.runInContext('skipCurrentLevel()', sandbox);
const gyrStageAfter = vm.runInContext('gyrussGame.stage', sandbox);
assert.strictEqual(gyrStageAfter, gyrStageBefore + 1, "Gyruss stage must advance by 1");
console.log(`   ✓ ${gyrSkipRes}: Advanced from Warp ${gyrStageBefore} -> Warp ${gyrStageAfter}!`);

// 8. Crazy Climber Level Skip
console.log("\n8. Testing Crazy Climber Level Skip (Building Advance)...");
vm.runInContext("switchActiveGame('cclimber')", sandbox);
const ccBldgBefore = vm.runInContext('climberState.building || 1', sandbox);
const ccSkipRes = vm.runInContext('skipCurrentLevel()', sandbox);
const ccBldgAfter = vm.runInContext('climberState.building', sandbox);
assert.strictEqual(ccBldgAfter, ccBldgBefore + 1, "Crazy Climber building must advance by 1");
assert.strictEqual(vm.runInContext('climberState.floor', sandbox), 1, "Floor must reset to ground level 1");
console.log(`   ✓ ${ccSkipRes}: Advanced from Skyscraper ${ccBldgBefore} -> Skyscraper ${ccBldgAfter}!`);

console.log("\n=========================================================================");
console.log(">>> ALL IMMORTAL (GOD) MODE & LEVEL SKIP TESTS PASSED 100%! <<<");
console.log("=========================================================================");
process.exit(0);
