/**
 * tools/test_sfx_fidelity_audit.js
 * Deep audio synthesis fidelity test for arcade-accurate SFX & BGM.
 */

const fs = require('fs');
const vm = require('vm');
const assert = require('assert');

const html = fs.readFileSync('web/fm1_pacman_preview.html', 'utf8');
const sIdx = html.indexOf('<script>');
const eIdx = html.lastIndexOf('</script>');
const jsCode = html.slice(sIdx + 8, eIdx);

const nodeEvents = [];

class MockAudioContext {
  constructor() {
    this.destination = {};
    this.sampleRate = 44100;
    this.currentTime = 0;
  }
  createGain() {
    const node = {
      gain: {
        val: 1,
        setValueAtTime: (v, t) => { node.gainVal = v; nodeEvents.push({ type: 'gainSet', v, t }); },
        linearRampToValueAtTime: (v, t) => { nodeEvents.push({ type: 'gainRamp', v, t }); },
        exponentialRampToValueAtTime: (v, t) => { nodeEvents.push({ type: 'gainExpRamp', v, t }); }
      },
      connect: (target) => {}
    };
    return node;
  }
  createOscillator() {
    const node = {
      frequency: {
        val: 440,
        setValueAtTime: (v, t) => { node.freq = v; nodeEvents.push({ type: 'oscFreqSet', v, t }); },
        exponentialRampToValueAtTime: (v, t) => { nodeEvents.push({ type: 'oscFreqExpRamp', v, t }); }
      },
      type: 'sine',
      connect: (target) => {},
      start: (t) => { nodeEvents.push({ type: 'oscStart', t, oscType: node.type }); },
      stop: (t) => { nodeEvents.push({ type: 'oscStop', t }); }
    };
    return node;
  }
  createBiquadFilter() {
    const node = {
      frequency: {
        val: 1000,
        setValueAtTime: (v, t) => { node.fltFreq = v; nodeEvents.push({ type: 'fltFreqSet', v, t }); },
        exponentialRampToValueAtTime: (v, t) => { nodeEvents.push({ type: 'fltFreqExpRamp', v, t }); }
      },
      Q: {
        val: 1,
        setValueAtTime: (v, t) => { nodeEvents.push({ type: 'fltQSet', v, t }); }
      },
      type: 'lowpass',
      connect: (target) => {}
    };
    return node;
  }
  createScriptProcessor() {
    return { connect: () => {} };
  }
  createDelay() {
    return { delayTime: { setValueAtTime: () => {} }, connect: () => {} };
  }
  createAnalyser() {
    return { fftSize: 2048, getByteFrequencyData: () => {}, connect: () => {} };
  }
  createBuffer(channels, length, sampleRate) {
    return { getChannelData: () => new Float32Array(length) };
  }
  createBufferSource() {
    return {
      connect: () => {},
      start: (t) => { nodeEvents.push({ type: 'noiseStart', t }); },
      stop: (t) => { nodeEvents.push({ type: 'noiseStop', t }); }
    };
  }
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
  putImageData: () => {}, font: '', fillStyle: '', strokeStyle: '', lineWidth: 1,
  ellipse: () => {}
};

const sandbox = {
  console: console,
  setTimeout: setTimeout, clearTimeout: clearTimeout,
  setInterval: () => {}, clearInterval: () => {},
  requestAnimationFrame: () => {}, cancelAnimationFrame: () => {},
  Math: Math,
  atob: (b64) => Buffer.from(b64, 'base64').toString('binary'),
  btoa: (bin) => Buffer.from(bin, 'binary').toString('base64'),
  Image: class { constructor() { this.src = ''; } },
  AudioContext: MockAudioContext,
  webkitAudioContext: MockAudioContext,
  window: { innerWidth: 800, innerHeight: 600, addEventListener: () => {}, location: { search: '' }, AudioContext: MockAudioContext, webkitAudioContext: MockAudioContext },
  document: {
    getElementById: () => ({ style: {}, classList: { add: () => {}, remove: () => {}, toggle: () => {} }, textContent: '', dataset: {}, getContext: () => mockCtx, appendChild: () => {} }),
    createElement: () => ({ style: {}, classList: { add: () => {}, remove: () => {}, toggle: () => {} }, textContent: '', dataset: {}, getContext: () => mockCtx, appendChild: () => {} }),
    querySelectorAll: () => []
  }
};

vm.createContext(sandbox);
vm.runInContext(jsCode, sandbox);

console.log("=========================================================================");
console.log("      ARCADE SFX & BGM SYNTHESIS FIDELITY AUDIT                          ");
console.log("=========================================================================\n");

function testSfx(sfxId, setupCode) {
  nodeEvents.length = 0;
  if (setupCode) vm.runInContext(setupCode, sandbox);
  vm.runInContext(`playArcadeSfx('${sfxId}');`, sandbox);
  return [...nodeEvents];
}

// 1. DK-WALK: alternating squeaks
console.log("1. Testing Donkey Kong Mario Walking Squeak Chirps (DK-WALK)...");
const walk1 = testSfx('DK-WALK');
const fSets1 = walk1.filter(e => e.type === 'oscFreqSet');
const fRamps1 = walk1.filter(e => e.type === 'oscFreqExpRamp');
assert(fSets1.length > 0 && fRamps1.length > 0, "DK-WALK must have freq set and ramp");
const startF1 = fSets1[0].v;
const endF1 = fRamps1[0].v;
console.log(`   ✓ Step 1: Start ${startF1} Hz -> End ${endF1} Hz`);
assert((startF1 === 850 && endF1 === 380) || (startF1 === 720 && endF1 === 310), "Step 1 should be authentic squeak");

const walk2 = testSfx('DK-WALK');
const fSets2 = walk2.filter(e => e.type === 'oscFreqSet');
const fRamps2 = walk2.filter(e => e.type === 'oscFreqExpRamp');
const startF2 = fSets2[0].v;
const endF2 = fRamps2[0].v;
console.log(`   ✓ Step 2: Start ${startF2} Hz -> End ${endF2} Hz`);
assert(startF1 !== startF2, "DK-WALK must alternate between two squeak pitches!");

// 2. DK-JUMP: continuous 8-step staircase
console.log("\n2. Testing Donkey Kong Spring Boing (DK-JUMP)...");
const jumpEvents = testSfx('DK-JUMP');
const jumpFreqs = jumpEvents.filter(e => e.type === 'oscFreqSet').map(e => e.v);
const jumpOscCount = jumpEvents.filter(e => e.type === 'oscStart').length;
console.log(`   ✓ Continuous single-oscillator: ${jumpOscCount === 1}`);
console.log(`   ✓ 8 DAC staircase steps: [${jumpFreqs.join(', ')}]`);
assert.strictEqual(jumpOscCount, 1, "DK-JUMP must use single continuous oscillator");
assert.strictEqual(jumpFreqs.length, 8, "DK-JUMP must have 8 frequency steps");
assert.deepStrictEqual(jumpFreqs, [262, 311, 370, 440, 523, 622, 740, 880]);

// 3. DK-HAMMER-TUNE: 16-note ragtime arpeggio
console.log("\n3. Testing Donkey Kong Hammer Arpeggio (DK-HAMMER-TUNE)...");
const hammerEvents = testSfx('DK-HAMMER-TUNE');
const hammerFreqs = hammerEvents.filter(e => e.type === 'oscFreqSet').map(e => e.v);
console.log(`   ✓ 16-note bouncy arpeggio: ${hammerFreqs.length} notes`);
assert.strictEqual(hammerFreqs.length, 16, "DK-HAMMER-TUNE must have 16 notes");
assert.deepStrictEqual(hammerFreqs, [523, 392, 523, 392, 659, 523, 659, 523, 698, 523, 698, 523, 587, 494, 587, 494]);

// 4. DK-DEATH: 8 descending notes + 3 halo angel pings
console.log("\n4. Testing Donkey Kong Mario Death Chime + Angel Halo Pings (DK-DEATH)...");
const dkDeathEvents = testSfx('DK-DEATH');
const dkDeathFreqs = dkDeathEvents.filter(e => e.type === 'oscFreqSet').map(e => e.v);
console.log(`   ✓ Descending chromatic notes (8): [${dkDeathFreqs.slice(0, 8).join(', ')}]`);
console.log(`   ✓ Angel halo pings (3): [${dkDeathFreqs.slice(8).join(', ')}]`);
assert.strictEqual(dkDeathFreqs.length, 11, "DK-DEATH must have 11 total notes (8 descent + 3 halo)");
assert.deepStrictEqual(dkDeathFreqs.slice(0, 8), [784, 740, 698, 659, 622, 587, 554, 523]);
assert.deepStrictEqual(dkDeathFreqs.slice(8), [1318, 1661, 1975]);

// 5. FROG-H: Ascending AY-3-8910 chirp
console.log("\n5. Testing Frogger Frog Hop Ascending Chirp (FROG-H)...");
const frogHopEvents = testSfx('FROG-H');
const fHopStart = frogHopEvents.find(e => e.type === 'oscFreqSet').v;
const fHopEnd = frogHopEvents.find(e => e.type === 'oscFreqExpRamp').v;
console.log(`   ✓ Hop frequency sweep: ${fHopStart} Hz -> ${fHopEnd} Hz`);
assert(fHopStart < fHopEnd, "Frog hop must be an ascending sweep, not descending!");
assert.strictEqual(fHopStart, 320);
assert.strictEqual(fHopEnd, 840);

// 6. GALAGA-FIRE: Dual WSG laser + transient click
console.log("\n6. Testing Galaga Dual Plasma Laser (GALAGA-FIRE)...");
const galagaFireEvents = testSfx('GALAGA-FIRE');
const galagaFireOscs = galagaFireEvents.filter(e => e.type === 'oscStart').length;
const galagaFireNoise = galagaFireEvents.some(e => e.type === 'noiseStart');
console.log(`   ✓ Dual WSG voices: ${galagaFireOscs === 2}`);
console.log(`   ✓ High-frequency click transient: ${galagaFireNoise}`);
assert.strictEqual(galagaFireOscs, 2, "GALAGA-FIRE must use dual voices");
assert(galagaFireNoise, "GALAGA-FIRE must have transient click");

// 7. GALAGA-INTRO: 17-note stage intro
console.log("\n7. Testing Galaga 17-Note Stage Intro Theme (GALAGA-INTRO)...");
const galagaIntroEvents = testSfx('GALAGA-INTRO');
const galagaIntroFreqs = galagaIntroEvents.filter(e => e.type === 'oscFreqSet').map(e => e.v);
console.log(`   ✓ Intro notes count: ${galagaIntroFreqs.length}`);
assert.strictEqual(galagaIntroFreqs.length, 17, "GALAGA-INTRO must have authentic 17 notes");
assert.deepStrictEqual(galagaIntroFreqs, [587, 494, 392, 587, 494, 392, 659, 523, 392, 659, 523, 392, 587, 494, 392, 587, 784]);

// 8. Multi-step gameplay BGMs (DK, Frogger, Climber, Galaga, Tempest, Gyruss)
console.log("\n8. Testing Period-Accurate Gameplay BGM Engines...");
// DK-BGM 4-step walking bass
const dkBass0 = testSfx('DK-BGM', 'dkongGame.bgmStep = 0;');
const dkBass0Freq = dkBass0.find(e => e.type === 'oscFreqSet').v;
const dkBass1 = testSfx('DK-BGM', 'dkongGame.bgmStep = 1;');
const dkBass1Freq = dkBass1.find(e => e.type === 'oscFreqSet').v;
console.log(`   ✓ DK-BGM 8035 walking bass: Step 0=${dkBass0Freq} Hz, Step 1=${dkBass1Freq} Hz`);
assert.strictEqual(dkBass0Freq, 92.5);
assert.strictEqual(dkBass1Freq, 98.0);

// FROG-BGM dual chiptune
const frogBgm0 = testSfx('FROG-BGM', 'froggerGame.bgmStep = 0;');
const frogBgm0Oscs = frogBgm0.filter(e => e.type === 'oscStart').length;
console.log(`   ✓ FROG-BGM Dual AY-3 voices (melody + bassline): ${frogBgm0Oscs} oscillators`);
assert(frogBgm0Oscs >= 2, "FROG-BGM must play melody and bassline concurrently");

// CLIMB-BGM Mancini swing strut
const climbBgm0 = testSfx('CLIMB-BGM', 'climberState.bgmStep = 0;');
const climbBgm0Oscs = climbBgm0.filter(e => e.type === 'oscStart').length;
console.log(`   ✓ CLIMB-BGM Mancini swing strut: ${climbBgm0Oscs} oscillators`);
assert(climbBgm0Oscs >= 2, "CLIMB-BGM must play melody and walking bass");

// GALAGA-BGM space fleet formation hum + sub-bass
const galagaBgm0 = testSfx('GALAGA-BGM', 'galagaGame.bgmStep = 0;');
const galagaBgm0Oscs = galagaBgm0.filter(e => e.type === 'oscStart').length;
console.log(`   ✓ GALAGA-BGM fleet formation hum + sub-bass: ${galagaBgm0Oscs} oscillators`);
assert(galagaBgm0Oscs >= 2, "GALAGA-BGM must include sub-bass drone");

// TEM-BGM POKEY vector arpeggio
const temBgm0 = testSfx('TEM-BGM', 'tempestGame.bgmStep = 0;');
const temBgm0Oscs = temBgm0.filter(e => e.type === 'oscStart').length;
console.log(`   ✓ TEM-BGM POKEY polyphonic vector pulse: ${temBgm0Oscs} oscillators`);
assert(temBgm0Oscs >= 2, "TEM-BGM must play polyphonic fifth interval");

// GYRUSS-BGM 42-step Bach Toccata & Fugue
const gyrussBgm0 = testSfx('GYRUSS-BGM', 'gyrussGame.bgmStep = 0;');
const gyrussBgm0Oscs = gyrussBgm0.filter(e => e.type === 'oscStart').length;
console.log(`   ✓ GYRUSS-BGM 5x PSG Bach Toccata & Fugue: ${gyrussBgm0Oscs} oscillators`);
assert(gyrussBgm0Oscs >= 2, "GYRUSS-BGM must play lead and pedal bass");

console.log("\n=========================================================================");
console.log(">>> ALL ARCADE SFX & BGM FIDELITY AUDIT CHECKS PASSED 100%! <<<");
console.log("=========================================================================");
