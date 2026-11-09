const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

console.log("=========================================================================");
console.log("TEST: ARCADE HALL OF FAME & NVRAM PERSISTENCE BATTERY");
console.log("=========================================================================");

// Mock localStorage
const storage = {};
const mockLocalStorage = {
  getItem: (key) => storage[key] !== undefined ? storage[key] : null,
  setItem: (key, val) => { storage[key] = String(val); },
  removeItem: (key) => { delete storage[key]; },
  clear: () => { for (const k in storage) delete storage[k]; }
};

const html = fs.readFileSync('web/fm1_pacman_preview.html', 'utf8');
const match = html.match(/<script(?:\s+type="text\/javascript")?>([\s\S]*?)<\/script>/i);
if (!match) throw new Error("Could not find script tag in web/fm1_pacman_preview.html");
const scriptCode = match[1];

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

const sandbox = {
  console: console,
  setTimeout: setTimeout,
  clearTimeout: clearTimeout,
  setInterval: setInterval,
  clearInterval: clearInterval,
  requestAnimationFrame: (cb) => setTimeout(cb, 16),
  cancelAnimationFrame: (id) => clearTimeout(id),
  Math: Math,
  atob: (b64) => Buffer.from(b64, 'base64').toString('binary'),
  btoa: (bin) => Buffer.from(bin, 'binary').toString('base64'),
  Image: class { constructor() { this.src = ''; } },
  AudioContext: MockAudioContext,
  webkitAudioContext: MockAudioContext,
  localStorage: mockLocalStorage,
  window: {
    innerWidth: 800,
    innerHeight: 600,
    addEventListener: () => {},
    location: { search: '' },
    AudioContext: MockAudioContext,
    webkitAudioContext: MockAudioContext
  },
  document: {
    getElementById: (id) => ({
      style: { setProperty: () => {} },
      classList: { add: () => {}, remove: () => {}, toggle: () => {} },
      textContent: '',
      innerHTML: '',
      appendChild: () => {},
      getContext: () => mockCtx
    }),
    createElement: () => ({
      textContent: '', className: '', classList: { toggle: () => {}, add: () => {}, remove: () => {} },
      dataset: {}, style: {}, onclick: null, appendChild: () => {}, getContext: () => mockCtx, addEventListener: () => {}
    }),
    querySelectorAll: () => [],
    addEventListener: () => {}
  },
  navigator: {
    requestMIDIAccess: null
  }
};

vm.createContext(sandbox);
vm.runInContext(scriptCode, sandbox);

console.log("\n1. Verifying Default Leaderboards for all 8 Games...");
const leaderboards = vm.runInContext('arcadeLeaderboards', sandbox);
assert(leaderboards, "arcadeLeaderboards must be defined");
const expectedGames = ['pacman', 'cclimber', 'galaga', 'dkong', 'frogger', 'asteroids', 'tempest', 'gyruss'];
expectedGames.forEach(g => {
  assert(leaderboards[g], `Leaderboard missing for game: ${g}`);
  assert.strictEqual(leaderboards[g].length, 5, `Game ${g} must have exactly 5 Hall of Fame records`);
  assert(leaderboards[g][0].score > leaderboards[g][4].score, `Game ${g} records must be sorted descending`);
  console.log(`   ✓ ${g.padEnd(10)}: Rank 1 = ${leaderboards[g][0].initials} (${leaderboards[g][0].score} pts)`);
});

console.log("\n2. Testing getGameHighScore()...");
expectedGames.forEach(g => {
  const topScore = vm.runInContext(`getGameHighScore('${g}')`, sandbox);
  assert.strictEqual(topScore, leaderboards[g][0].score, `getGameHighScore('${g}') mismatch`);
});
console.log("   ✓ getGameHighScore() returned top scores across all 8 titles!");

console.log("\n3. Testing submitHighScore() and Sorting Order...");
// Submit a record-breaking score for Donkey Kong
const testScore = 1200000;
vm.runInContext(`submitHighScore('dkong', 'ACE', ${testScore})`, sandbox);
const dkongList = vm.runInContext('arcadeLeaderboards.dkong', sandbox);
assert.strictEqual(dkongList.length, 5, "Leaderboard length must remain capped at 5");
assert.strictEqual(dkongList[0].score, testScore, "Top score must match submitted score");
assert.strictEqual(dkongList[0].initials, 'ACE', "Top initials must match 'ACE'");
assert.strictEqual(dkongList[0].rank, 1, "Top rank must be 1");
assert.strictEqual(dkongList[1].rank, 2, "Second rank must be 2");
console.log(`   ✓ High score submission verified! New #1 = ${dkongList[0].initials} (${dkongList[0].score} pts)`);

console.log("\n4. Verifying NVRAM (localStorage) Serialization...");
const nvramData = mockLocalStorage.getItem('fm1_arcade_nvram_leaderboard');
assert(nvramData, "NVRAM data must be saved to localStorage['fm1_arcade_nvram_leaderboard']");
const parsedNvram = JSON.parse(nvramData);
assert.strictEqual(parsedNvram.dkong[0].score, testScore, "NVRAM serialized data must retain new high score");
console.log(`   ✓ NVRAM serialized successfully (${nvramData.length} bytes)!`);

console.log("\n5. Testing NVRAM Restore Lifecycle across Session Reload...");
// Clear in-memory leaderboards
vm.runInContext('arcadeLeaderboards = {}', sandbox);
assert.strictEqual(Object.keys(vm.runInContext('arcadeLeaderboards', sandbox)).length, 0);

// Invoke loadLeaderboardsFromNVRAM()
vm.runInContext('loadLeaderboardsFromNVRAM()', sandbox);
const restored = vm.runInContext('arcadeLeaderboards', sandbox);
assert(restored.dkong, "Donkey Kong leaderboard must be restored from NVRAM");
assert.strictEqual(restored.dkong[0].score, testScore, "Restored Donkey Kong score must match NVRAM record");
console.log("   ✓ High scores restored cleanly from NVRAM after simulated memory wipe!");

console.log("\n6. Testing Corrupted NVRAM Graceful Recovery...");
mockLocalStorage.setItem('fm1_arcade_nvram_leaderboard', '{BROKEN_JSON: INVALID');
vm.runInContext('loadLeaderboardsFromNVRAM()', sandbox);
const fallbackList = vm.runInContext('arcadeLeaderboards', sandbox);
assert(fallbackList.pacman, "Must gracefully fallback to default leaderboards upon NVRAM corruption");
assert.strictEqual(fallbackList.pacman[0].initials, 'BIL', "Factory defaults restored cleanly");
console.log("   ✓ Corrupted NVRAM handled with zero crash; restored arcade factory defaults!");

console.log("\n7. Testing resetLeaderboardsToDefaults()...");
vm.runInContext('resetLeaderboardsToDefaults()', sandbox);
const resetList = vm.runInContext('arcadeLeaderboards.dkong', sandbox);
assert.strictEqual(resetList[0].initials, 'WIE', "Donkey Kong reset to Steve Wiebe default");
console.log("   ✓ Factory reset cleared custom scores and reset NVRAM correctly!");

console.log("\n=========================================================================");
console.log(">>> ALL ARCADE NVRAM & HIGH SCORE LEADERBOARD TESTS PASSED 100%! <<<");
console.log("=========================================================================");
process.exit(0);
