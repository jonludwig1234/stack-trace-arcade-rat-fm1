/**
 * Test Vintage Arcade Speech ROM Integration and Synthesizer Execution.
 */
const fs = require('fs');
const path = require('path');

const previewHtml = fs.readFileSync(path.join(__dirname, '../web/fm1_pacman_preview.html'), 'utf8');

console.log("=== VINTAGE SPEECH ROM FIDELITY TEST ===");

// 1. Verify UI Elements
const requiredElements = [
  'id="tabSpeech"',
  'id="shelfSpeech"',
  'id="speechStatusDisplay"',
  'id="card_VOX_INTRUDER"',
  'id="card_VOX_COIN"',
  'id="card_VOX_QBERT"',
  'id="card_VOX_SINISTAR"',
  'id="card_VOX_HUNGER"',
  'id="card_VOX_WIZARD"',
  'id="card_VOX_GORF"',
  'id="card_VOX_DRAGON"',
  '🗣️ SPEECH ROM (8)'
];

requiredElements.forEach(item => {
  if (!previewHtml.includes(item)) {
    throw new Error(`Missing expected element/text in HTML: ${item}`);
  }
});
console.log("✓ All 12 required UI elements & shelf cards present in HTML.");

// 2. Headless AudioContext and DOM Mock Execution Test
let audioCreatedNodes = [];
let audioPlayedSources = [];

class MockParam {
  constructor() { this.value = 0; }
  setValueAtTime(v, t) { this.value = v; }
  exponentialRampToValueAtTime(v, t) { this.value = v; }
  linearRampToValueAtTime(v, t) { this.value = v; }
}
class MockGain {
  constructor() {
    this.gain = new MockParam();
    audioCreatedNodes.push(this);
  }
  connect(dest) {}
}
class MockBufferSource {
  constructor() {
    this.buffer = null;
    audioCreatedNodes.push(this);
    audioPlayedSources.push(this);
  }
  connect(dest) {}
  start(t) {}
  stop(t) {}
}
class MockAudioContext {
  constructor() {
    this.currentTime = 100.0;
    this.sampleRate = 44100;
  }
  createGain() { return new MockGain(); }
  createBufferSource() { return new MockBufferSource(); }
  decodeAudioData(ab) {
    return Promise.resolve({
      duration: 2.0,
      length: 88200,
      numberOfChannels: 1,
      sampleRate: 44100
    });
  }
}

const mockDoc = {
  elements: {},
  getElementById(id) {
    if (!this.elements[id]) {
      this.elements[id] = {
        id: id,
        innerHTML: '',
        textContent: '',
        classList: {
          classes: new Set(),
          add(c) { this.classes.add(c); },
          remove(c) { this.classes.delete(c); },
          contains(c) { return this.classes.has(c); },
          toggle(c, force) {
            if (force === undefined) {
              if (this.classes.has(c)) this.classes.delete(c);
              else this.classes.add(c);
            } else {
              if (force) this.classes.add(c);
              else this.classes.delete(c);
            }
          }
        }
      };
    }
    return this.elements[id];
  },
  querySelectorAll(sel) {
    return [];
  }
};

const listeners = {};
const mockWindow = {
  addEventListener(event, fn) {
    listeners[event] = listeners[event] || [];
    listeners[event].push(fn);
  },
  dispatchEvent(event) {
    if (listeners[event.type]) {
      listeners[event.type].forEach(fn => fn(event));
    }
  }
};

let htmlAudioPlayed = [];
class MockAudio {
  constructor(src) {
    this.src = src;
    this.volume = 1.0;
  }
  play() {
    htmlAudioPlayed.push(this.src);
    return Promise.resolve();
  }
}

// Test Speech Synthesis sandbox
const vm = require('vm');
const sandbox = {
  window: mockWindow,
  document: mockDoc,
  audioCtx: new MockAudioContext(),
  filterNode: new MockGain(),
  masterGain: new MockGain(),
  Audio: MockAudio,
  fetch: (uri) => Promise.resolve({
    arrayBuffer: () => Promise.resolve(new ArrayBuffer(1024))
  }),
  initAudio: () => {},
  console: console,
  setTimeout: setTimeout,
  clearTimeout: clearTimeout,
  currentStudioTab: 'arcade',
  currentMode: 'arcade',
  stopCurrentGame: () => {},
  activeGame: 'pacman',
  switchActiveGame: () => {},
  setStudioTab: null,
  triggerSpeechRom: null,
  playSpeechSample: null,
  playArcadeSpeechSample: null
};

vm.createContext(sandbox);

// Extract the speech JS code from the HTML
const scriptMatch = previewHtml.match(/\/\/ =========================================================================\s*\/\/ AUTHENTIC VINTAGE ARCADE SPEECH & PCM SAMPLE-ROM SYNTHESIZER[\s\S]*?const playSpeechSample = playArcadeSpeechSample;/);
if (!scriptMatch) {
  throw new Error("Could not find speech synthesizer script in HTML!");
}

vm.runInContext(scriptMatch[0], sandbox);

// Also extract triggerSpeechRom & hotkeys definition
const triggerMatch = previewHtml.match(/function triggerSpeechRom\(id\)[\s\S]*?\/\/ Global hotkeys for Speech ROM[\s\S]*?\}\);/);
if (!triggerMatch) {
  throw new Error("Could not find triggerSpeechRom definition in HTML!");
}
vm.runInContext(triggerMatch[0], sandbox);

console.log("✓ Speech scripts successfully loaded into VM.");

// Test all 8 voice samples
const sampleIds = [
  'VOX_INTRUDER',
  'VOX_COIN',
  'VOX_QBERT',
  'VOX_SINISTAR',
  'VOX_HUNGER',
  'VOX_WIZARD',
  'VOX_GORF',
  'VOX_DRAGON'
];

async function runTests() {
  for (const id of sampleIds) {
    audioCreatedNodes = [];
    htmlAudioPlayed = [];
    audioPlayedSources = [];
    
    sandbox.triggerSpeechRom(id);
    // Give async fetch/decode a tick to resolve
    await new Promise(r => setTimeout(r, 10));
    
    if (audioPlayedSources.length === 0 && htmlAudioPlayed.length === 0) {
      throw new Error(`triggerSpeechRom(${id}) failed to trigger audio playback!`);
    }
    const sfxStatus = mockDoc.getElementById('sfxLastTriggered').innerHTML;
    const speechStatus = mockDoc.getElementById('speechStatusDisplay').innerHTML;
    console.log(`✓ ${id}: Triggered authentic arcade speech playback! Status: "${sfxStatus}"`);
  }

  // Also test legacy alias IDs: VOX_DANGER and VOX_ARCADE_RAT
  ['VOX_DANGER', 'VOX_ARCADE_RAT'].forEach(aliasId => {
    sandbox.triggerSpeechRom(aliasId);
    console.log(`✓ Legacy alias ${aliasId} dispatched successfully.`);
  });

  // Test keydown shortcuts
  let setStudioTabCalledWith = null;
  sandbox.setStudioTab = (tab) => {
    setStudioTabCalledWith = tab;
    sandbox.currentStudioTab = tab;
  };

  // Press 'v' to open speech tab
  listeners['keydown'].forEach(fn => fn({ key: 'v', preventDefault: () => {} }));
  if (setStudioTabCalledWith !== 'speech') {
    throw new Error(`Expected setStudioTab('speech') on key 'v', got: ${setStudioTabCalledWith}`);
  }
  console.log("✓ Keydown 'v' correctly toggles studio tab to 'speech'.");

  // While on speech tab, press '1' to trigger VOX_INTRUDER
  audioPlayedSources = [];
  listeners['keydown'].forEach(fn => fn({ key: '1', preventDefault: () => {} }));
  await new Promise(r => setTimeout(r, 10));
  if (audioPlayedSources.length === 0 && htmlAudioPlayed.length === 0) {
    throw new Error("Keydown '1' on speech tab failed to trigger VOX_INTRUDER!");
  }
  console.log("✓ Keydown '1' on speech tab correctly triggered VOX_INTRUDER.");

  // Press 'v' again to toggle back to arcade
  listeners['keydown'].forEach(fn => fn({ key: 'v', preventDefault: () => {} }));
  if (setStudioTabCalledWith !== 'arcade') {
    throw new Error(`Expected setStudioTab('arcade') on second key 'v', got: ${setStudioTabCalledWith}`);
  }
  console.log("✓ Second keydown 'v' correctly returns studio tab to 'arcade'.");

  console.log("\n>>> ALL AUTHENTIC VINTAGE SPEECH ROM INTEGRATION TESTS PASSED! <<<");
}

runTests().catch(err => {
  console.error("Test failed:", err);
  process.exit(1);
});
