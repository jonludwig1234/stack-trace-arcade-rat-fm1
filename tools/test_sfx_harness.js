// Test harness to verify all 108 SFX sound synthesizers run without errors
const fs = require('fs');

class MockAudioParam {
  constructor(v = 0) { this.value = v; }
  setValueAtTime() {}
  linearRampToValueAtTime() {}
  exponentialRampToValueAtTime() {}
}

class MockAudioNode {
  constructor() {
    this.frequency = new MockAudioParam(440);
    this.gain = new MockAudioParam(1);
    this.Q = new MockAudioParam(1);
    this.delayTime = new MockAudioParam(0.2);
  }
  connect() {}
  start() {}
  stop() {}
}

class MockAudioContext {
  constructor() {
    this.currentTime = 10.0;
    this.sampleRate = 44100;
  }
  createGain() { return new MockAudioNode(); }
  createOscillator() { return new MockAudioNode(); }
  createBiquadFilter() { return new MockAudioNode(); }
  createDelay() { return new MockAudioNode(); }
  createBuffer(c, l, s) { return { getChannelData: () => new Float32Array(l) }; }
  createBufferSource() { return { buffer: null, connect() {}, start() {}, stop() {} }; }
}

global.audioCtx = new MockAudioContext();
global.filterNode = new MockAudioNode();
global.masterGain = new MockAudioNode();
global.noiseBuffer = { getChannelData: () => new Float32Array(44100) };
global.initAudio = () => {};
global.lastSfxName = '';

console.log("Mock audio environment initialized successfully.");
