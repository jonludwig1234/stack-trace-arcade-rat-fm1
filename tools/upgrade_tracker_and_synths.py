#!/usr/bin/env python3
"""
Upgrade M-VAVE FM-1 with authentic Multi-Engine Synthesizer & 16-Step Chiptune Tracker.
"""
import re

def update_template_bak():
    with open("tools/simulator_template.html.bak", "r") as f:
        code = f.read()

    # 1. Insert liveSynth and trackerEngine right after playTrackNote definition
    synth_and_tracker_code = """
// -------------------------------------------------------------------------
// LIVE MULTI-ENGINE CHIPTUNE & FM SYNTHESIZER
// -------------------------------------------------------------------------
const liveSynth = {
  currentEngine: 'wsg', // 'wsg', 'ay8910', 'pokey', 'dac', 'fm'
  engineNames: {
    wsg: 'Namco WSG 3-Voice Wavetable',
    ay8910: 'AY-3-8910 Chiptune PSG',
    pokey: 'Atari POKEY Distortion Synth',
    dac: 'Nintendo Arcade DAC (NES)',
    fm: 'M-VAVE FM-1 6-Operator FM'
  },
  engineOrder: ['wsg', 'ay8910', 'pokey', 'dac', 'fm'],
  octaveOffset: 0, // -2 to +2
  activeVoices: new Map(), // keyIdx -> { oscs: [], gain: gainNode }
  arp: {
    active: false,
    timer: null,
    heldKeys: [],
    stepIdx: 0,
    speedMs: 125
  },
  envelope: 'lead', // 'lead', 'pluck', 'pad', 'organ'
  waveMorph: 0, // 0..7
  lfo: {
    active: false,
    rate: 6.0,
    depth: 18
  }
};

function cycleSynthEngine() {
  const idx = liveSynth.engineOrder.indexOf(liveSynth.currentEngine);
  liveSynth.currentEngine = liveSynth.engineOrder[(idx + 1) % liveSynth.engineOrder.length];
  const name = liveSynth.engineNames[liveSynth.currentEngine];
  const status = document.getElementById('engineStatus');
  if (status) status.innerHTML = `SYNTH ENGINE: <b>${name}</b>`;
  const hud = document.getElementById('hudStatus');
  if (hud) hud.textContent = `● SYNTH: ${liveSynth.currentEngine.toUpperCase()}`;
  playStartupChimeMini();
  return name;
}

function cycleEnvelope() {
  const envs = ['lead', 'pluck', 'pad', 'organ'];
  const idx = envs.indexOf(liveSynth.envelope);
  liveSynth.envelope = envs[(idx + 1) % envs.length];
  const status = document.getElementById('engineStatus');
  if (status) status.innerHTML = `ENVELOPE: <b>${liveSynth.envelope.toUpperCase()}</b>`;
}

function toggleLfo() {
  liveSynth.lfo.active = !liveSynth.lfo.active;
  const status = document.getElementById('engineStatus');
  if (status) status.innerHTML = `LFO VIBRATO: <b>${liveSynth.lfo.active ? 'ON (6.0 Hz)' : 'OFF'}</b>`;
}

function toggleArp() {
  liveSynth.arp.active = !liveSynth.arp.active;
  const btn = document.getElementById('btnArp');
  if (btn) btn.classList.toggle('active', liveSynth.arp.active);
  const status = document.getElementById('engineStatus');
  if (status) status.innerHTML = `ARPEGGIATOR: <b>${liveSynth.arp.active ? 'ON (1/16th)' : 'OFF'}</b>`;
  if (!liveSynth.arp.active && liveSynth.arp.timer) {
    clearInterval(liveSynth.arp.timer);
    liveSynth.arp.timer = null;
  }
}

function playStartupChimeMini() {
  if (!audioCtx) return;
  const now = audioCtx.currentTime;
  const osc = audioCtx.createOscillator();
  const g = audioCtx.createGain();
  osc.type = 'triangle';
  osc.frequency.setValueAtTime(523.25, now);
  osc.frequency.exponentialRampToValueAtTime(1046.50, now + 0.08);
  g.gain.setValueAtTime(0.2, now);
  g.gain.exponentialRampToValueAtTime(0.001, now + 0.09);
  osc.connect(g);
  g.connect(filterNode);
  osc.start(now);
  osc.stop(now + 0.1);
}

function triggerSynthVoice(keyIdx, autoReleaseSec) {
  if (!audioCtx) return;
  const now = audioCtx.currentTime;
  releaseSynthVoice(keyIdx);

  // Map 27 keys starting at C3 (MIDI 48)
  const midiNote = 48 + keyIdx + (liveSynth.octaveOffset * 12);
  const freq = 440 * Math.pow(2, (midiNote - 69) / 12);

  const gainNode = audioCtx.createGain();
  const oscs = [];
  const engine = liveSynth.currentEngine;
  let targetVol = 0.32;

  if (engine === 'wsg') {
    // Namco WSG 3-Voice Wavetable
    const osc = audioCtx.createOscillator();
    const w = liveSynth.waveMorph % 8;
    if (w === 0) osc.type = 'triangle';
    else if (w === 1) osc.type = 'sawtooth';
    else if (w === 2) osc.type = 'square';
    else if (w === 3) osc.type = 'sine';
    else osc.type = (w % 2 === 0) ? 'triangle' : 'square';
    osc.frequency.setValueAtTime(freq, now);
    osc.connect(gainNode);
    oscs.push(osc);

    // Warm sub-oscillator
    const sub = audioCtx.createOscillator();
    sub.type = 'triangle';
    sub.frequency.setValueAtTime(freq * 0.5, now);
    const subGain = audioCtx.createGain();
    subGain.gain.setValueAtTime(0.18, now);
    sub.connect(subGain);
    subGain.connect(gainNode);
    oscs.push(sub);

  } else if (engine === 'ay8910') {
    // AY-3-8910 Arcade PSG (Square Wave)
    const osc = audioCtx.createOscillator();
    osc.type = 'square';
    osc.frequency.setValueAtTime(freq, now);
    osc.connect(gainNode);
    oscs.push(osc);

    // Detuned second square for thick arcade chorus
    const osc2 = audioCtx.createOscillator();
    osc2.type = 'square';
    osc2.frequency.setValueAtTime(freq * 1.004, now);
    const g2 = audioCtx.createGain();
    g2.gain.setValueAtTime(0.35, now);
    osc2.connect(g2);
    g2.connect(gainNode);
    oscs.push(osc2);

  } else if (engine === 'pokey') {
    // Atari POKEY Distortion Synth
    const osc = audioCtx.createOscillator();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(freq, now);

    const distMod = audioCtx.createOscillator();
    distMod.frequency.setValueAtTime(freq * 1.5, now);
    const distGain = audioCtx.createGain();
    distGain.gain.setValueAtTime(25 + liveSynth.waveMorph * 10, now);
    distMod.connect(distGain);
    distGain.connect(osc.frequency);
    distMod.start(now);
    oscs.push(distMod);

    osc.connect(gainNode);
    oscs.push(osc);
    targetVol = 0.28;

  } else if (engine === 'dac') {
    // Nintendo Arcade DAC (NES)
    const osc = audioCtx.createOscillator();
    osc.type = keyIdx < 8 ? 'triangle' : 'square';
    osc.frequency.setValueAtTime(freq, now);
    osc.connect(gainNode);
    oscs.push(osc);

  } else if (engine === 'fm') {
    // M-VAVE FM-1 6-Operator FM Synthesizer
    const carrier = audioCtx.createOscillator();
    const modulator = audioCtx.createOscillator();
    const modGain = audioCtx.createGain();

    const harmonicRatio = [1, 2, 3, 3.5, 4, 5, 7, 0.5][liveSynth.waveMorph % 8];
    modulator.frequency.setValueAtTime(freq * harmonicRatio, now);
    const modDepth = (liveSynth.waveMorph + 1) * 120 + 80;
    modGain.gain.setValueAtTime(modDepth, now);
    modGain.gain.exponentialRampToValueAtTime(Math.max(1, modDepth * 0.1), now + 0.45);

    modulator.connect(modGain);
    modGain.connect(carrier.frequency);

    carrier.frequency.setValueAtTime(freq, now);
    carrier.connect(gainNode);

    modulator.start(now);
    oscs.push(modulator);
    oscs.push(carrier);
    targetVol = 0.30;
  }

  // LFO Vibrato
  if (liveSynth.lfo.active) {
    const lfoOsc = audioCtx.createOscillator();
    const lfoGain = audioCtx.createGain();
    lfoOsc.frequency.setValueAtTime(liveSynth.lfo.rate, now);
    lfoGain.gain.setValueAtTime(liveSynth.lfo.depth, now);
    lfoOsc.connect(lfoGain);
    if (oscs.length > 0) lfoGain.connect(oscs[0].frequency);
    lfoOsc.start(now);
    oscs.push(lfoOsc);
  }

  // Envelope Shaping
  gainNode.gain.setValueAtTime(0.001, now);
  if (liveSynth.envelope === 'lead') {
    gainNode.gain.linearRampToValueAtTime(targetVol, now + 0.005);
    gainNode.gain.exponentialRampToValueAtTime(targetVol * 0.72, now + 0.14);
  } else if (liveSynth.envelope === 'pluck') {
    gainNode.gain.linearRampToValueAtTime(targetVol, now + 0.003);
    gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
  } else if (liveSynth.envelope === 'pad') {
    gainNode.gain.linearRampToValueAtTime(targetVol, now + 0.18);
    gainNode.gain.exponentialRampToValueAtTime(targetVol * 0.75, now + 0.4);
  } else { // organ
    gainNode.gain.linearRampToValueAtTime(targetVol, now + 0.004);
  }

  gainNode.connect(filterNode);

  oscs.forEach(o => {
    try { o.start(now); } catch(e){}
  });

  if (autoReleaseSec) {
    const stopTime = now + autoReleaseSec;
    gainNode.gain.setValueAtTime(targetVol, stopTime - 0.03);
    gainNode.gain.exponentialRampToValueAtTime(0.001, stopTime);
    oscs.forEach(o => {
      try { o.stop(stopTime); } catch(e){}
    });
  } else {
    liveSynth.activeVoices.set(keyIdx, { oscs, gain: gainNode });
  }
}

function releaseSynthVoice(keyIdx) {
  if (!liveSynth.activeVoices.has(keyIdx)) return;
  const voice = liveSynth.activeVoices.get(keyIdx);
  liveSynth.activeVoices.delete(keyIdx);
  if (!audioCtx) return;
  const now = audioCtx.currentTime;
  try {
    voice.gain.gain.setValueAtTime(voice.gain.gain.value, now);
    voice.gain.gain.exponentialRampToValueAtTime(0.001, now + 0.06);
    voice.oscs.forEach(o => {
      try { o.stop(now + 0.07); } catch(e){}
    });
  } catch(e){}
}

function playLiveSynthNote(keyIdx, isDown) {
  initAudio();
  if (!audioCtx) return;

  if (liveSynth.arp.active) {
    if (isDown) {
      if (!liveSynth.arp.heldKeys.includes(keyIdx)) liveSynth.arp.heldKeys.push(keyIdx);
      if (!liveSynth.arp.timer) {
        liveSynth.arp.stepIdx = 0;
        const tickArp = () => {
          if (liveSynth.arp.heldKeys.length === 0) return;
          const k = liveSynth.arp.heldKeys[liveSynth.arp.stepIdx % liveSynth.arp.heldKeys.length];
          triggerSynthVoice(k, 0.1);
          liveSynth.arp.stepIdx++;
        };
        tickArp();
        liveSynth.arp.timer = setInterval(tickArp, 120);
      }
    } else {
      liveSynth.arp.heldKeys = liveSynth.arp.heldKeys.filter(k => k !== keyIdx);
      if (liveSynth.arp.heldKeys.length === 0 && liveSynth.arp.timer) {
        clearInterval(liveSynth.arp.timer);
        liveSynth.arp.timer = null;
      }
    }
    return;
  }

  if (isDown) {
    triggerSynthVoice(keyIdx);
  } else {
    releaseSynthVoice(keyIdx);
  }
}

// -------------------------------------------------------------------------
// 16-STEP CHIPTUNE TRACKER & SEQUENCER ENGINE
// -------------------------------------------------------------------------
const trackerEngine = {
  bpm: 132,
  playing: false,
  step: 0,
  timer: null,
  currentPatternIdx: 0,
  vuLevels: [0, 0, 0, 0], // CH1: WSG Bass, CH2: AY Lead, CH3: POKEY Arp, CH4: Drum
  patterns: [
    {
      name: 'ARCADE RAT THEME',
      bpm: 132,
      chipType: 'WSG+AY+POK+DAC',
      steps: [
        [[38, 14], [62, 14], [74, 12], 'KCK'],
        [[ 0,  0], [ 0,  0], [77, 12], 'HHT'],
        [[38, 14], [65, 13], [81, 12], '---'],
        [[ 0,  0], [ 0,  0], [77, 12], 'HHT'],
        [[41, 14], [67, 14], [74, 12], 'SNR'],
        [[ 0,  0], [ 0,  0], [76, 12], 'HHT'],
        [[43, 14], [69, 14], [77, 12], '---'],
        [[ 0,  0], [72, 13], [79, 12], 'HHT'],
        [[45, 14], [74, 15], [81, 12], 'KCK'],
        [[ 0,  0], [ 0,  0], [79, 12], 'HHT'],
        [[43, 14], [72, 14], [77, 12], '---'],
        [[ 0,  0], [ 0,  0], [76, 12], 'HHT'],
        [[41, 14], [69, 14], [74, 12], 'SNR'],
        [[ 0,  0], [67, 13], [72, 12], 'ZAP'],
        [[40, 14], [65, 14], [74, 12], 'KCK'],
        [[36, 14], [64, 13], [72, 12], 'HHT']
      ]
    },
    {
      name: 'PAC-MANIA DUB',
      bpm: 124,
      chipType: 'WSG+TAPE DUB',
      steps: [
        [[36, 15], [60, 14], [67, 13], 'KCK'],
        [[ 0,  0], [ 0,  0], [ 0,  0], 'HHT'],
        [[36, 13], [63, 13], [70, 12], '---'],
        [[ 0,  0], [65, 14], [ 0,  0], 'HHT'],
        [[41, 15], [67, 14], [72, 13], 'SNR'],
        [[ 0,  0], [ 0,  0], [ 0,  0], 'HHT'],
        [[41, 13], [65, 13], [67, 12], '---'],
        [[ 0,  0], [63, 13], [ 0,  0], 'ZAP'],
        [[43, 15], [72, 15], [75, 13], 'KCK'],
        [[ 0,  0], [ 0,  0], [ 0,  0], 'HHT'],
        [[43, 13], [70, 13], [72, 12], '---'],
        [[ 0,  0], [67, 14], [ 0,  0], 'HHT'],
        [[41, 15], [65, 14], [68, 13], 'SNR'],
        [[ 0,  0], [ 0,  0], [ 0,  0], 'ZAP'],
        [[38, 14], [63, 14], [67, 12], 'KCK'],
        [[39, 14], [62, 13], [65, 12], 'HHT']
      ]
    },
    {
      name: 'GYRUSS SPEED RUN',
      bpm: 144,
      chipType: 'AY-3-8910 BAROQUE',
      steps: [
        [[38, 15], [74, 15], [62, 14], 'KCK'],
        [[38, 13], [73, 14], [62, 12], 'HHT'],
        [[38, 15], [74, 15], [65, 14], '---'],
        [[38, 13], [76, 14], [65, 12], 'HHT'],
        [[41, 15], [77, 15], [69, 14], 'SNR'],
        [[41, 13], [76, 14], [69, 12], 'HHT'],
        [[41, 15], [74, 15], [65, 14], '---'],
        [[41, 13], [73, 14], [65, 12], 'HHT'],
        [[43, 15], [70, 15], [67, 14], 'KCK'],
        [[43, 13], [72, 14], [67, 12], 'HHT'],
        [[43, 15], [74, 15], [70, 14], '---'],
        [[43, 13], [76, 14], [70, 12], 'HHT'],
        [[45, 15], [77, 15], [74, 14], 'SNR'],
        [[45, 13], [79, 14], [74, 12], 'ZAP'],
        [[45, 15], [81, 15], [77, 14], 'KCK'],
        [[43, 14], [79, 14], [76, 12], 'HHT']
      ]
    },
    {
      name: 'CYBER LABYRINTH',
      bpm: 138,
      chipType: '6-OP FM + POKEY',
      steps: [
        [[36, 15], [60, 14], [72, 13], 'KCK'],
        [[ 0,  0], [ 0,  0], [75, 12], 'HHT'],
        [[36, 14], [63, 13], [72, 13], 'KCK'],
        [[ 0,  0], [67, 14], [79, 12], 'HHT'],
        [[41, 15], [68, 15], [80, 14], 'SNR'],
        [[ 0,  0], [ 0,  0], [79, 12], 'HHT'],
        [[41, 14], [67, 14], [75, 13], '---'],
        [[ 0,  0], [63, 13], [72, 12], 'ZAP'],
        [[44, 15], [72, 15], [84, 14], 'KCK'],
        [[ 0,  0], [ 0,  0], [80, 12], 'HHT'],
        [[44, 14], [70, 14], [84, 13], 'KCK'],
        [[ 0,  0], [68, 14], [79, 12], 'HHT'],
        [[43, 15], [67, 15], [75, 14], 'SNR'],
        [[ 0,  0], [ 0,  0], [72, 12], 'ZAP'],
        [[41, 14], [65, 14], [70, 13], 'KCK'],
        [[38, 14], [63, 13], [67, 12], 'HHT']
      ]
    }
  ]
};

function midiToStr(note) {
  if (!note || note === 0) return '---';
  const names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
  const name = names[note % 12];
  const oct = Math.floor(note / 12) - 1;
  return (name.length === 1 ? name + '-' : name) + oct;
}

function playTrackerVoice(engine, midiNote, vol, durSec, time) {
  if (!audioCtx || !midiNote || vol <= 0) return;
  const now = time || audioCtx.currentTime;
  const freq = 440 * Math.pow(2, (midiNote - 69) / 12);
  const gainNode = audioCtx.createGain();
  const normalizedVol = (vol / 15.0) * 0.38;

  const osc = audioCtx.createOscillator();
  if (engine === 'wsg') {
    osc.type = 'triangle';
  } else if (engine === 'ay8910') {
    osc.type = 'square';
  } else if (engine === 'pokey') {
    osc.type = 'sawtooth';
  } else {
    osc.type = 'square';
  }

  osc.frequency.setValueAtTime(freq, now);
  gainNode.gain.setValueAtTime(normalizedVol, now);
  gainNode.gain.exponentialRampToValueAtTime(0.001, now + durSec * 0.92);

  osc.connect(gainNode);
  gainNode.connect(filterNode);

  osc.start(now);
  osc.stop(now + durSec);
}

function playArcadeDrum(type, vol, time) {
  if (!audioCtx || !type || type === '---') return;
  const now = time || audioCtx.currentTime;
  const normVol = (vol / 15.0) * 0.55;

  if (type === 'KCK') {
    const osc = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    osc.frequency.setValueAtTime(160, now);
    osc.frequency.exponentialRampToValueAtTime(38, now + 0.12);
    g.gain.setValueAtTime(normVol, now);
    g.gain.exponentialRampToValueAtTime(0.001, now + 0.14);
    osc.connect(g);
    g.connect(filterNode);
    osc.start(now);
    osc.stop(now + 0.15);
  } else if (type === 'SNR') {
    if (noiseBuffer) {
      const src = audioCtx.createBufferSource();
      src.buffer = noiseBuffer;
      const flt = audioCtx.createBiquadFilter();
      flt.type = 'bandpass';
      flt.frequency.setValueAtTime(1400, now);
      const g = audioCtx.createGain();
      g.gain.setValueAtTime(normVol * 0.85, now);
      g.gain.exponentialRampToValueAtTime(0.001, now + 0.16);
      src.connect(flt);
      flt.connect(g);
      g.connect(filterNode);
      src.start(now);
      src.stop(now + 0.17);
    }
    const osc = audioCtx.createOscillator();
    const tg = audioCtx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(220, now);
    osc.frequency.exponentialRampToValueAtTime(80, now + 0.08);
    tg.gain.setValueAtTime(normVol * 0.5, now);
    tg.gain.exponentialRampToValueAtTime(0.001, now + 0.09);
    osc.connect(tg);
    tg.connect(filterNode);
    osc.start(now);
    osc.stop(now + 0.1);
  } else if (type === 'HHT') {
    if (noiseBuffer) {
      const src = audioCtx.createBufferSource();
      src.buffer = noiseBuffer;
      const flt = audioCtx.createBiquadFilter();
      flt.type = 'highpass';
      flt.frequency.setValueAtTime(7500, now);
      const g = audioCtx.createGain();
      g.gain.setValueAtTime(normVol * 0.6, now);
      g.gain.exponentialRampToValueAtTime(0.001, now + 0.045);
      src.connect(flt);
      flt.connect(g);
      g.connect(filterNode);
      src.start(now);
      src.stop(now + 0.05);
    }
  } else if (type === 'ZAP') {
    const osc = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(1800, now);
    osc.frequency.exponentialRampToValueAtTime(120, now + 0.15);
    g.gain.setValueAtTime(normVol * 0.7, now);
    g.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
    osc.connect(g);
    g.connect(filterNode);
    osc.start(now);
    osc.stop(now + 0.16);
  }
}

function trackerStep() {
  if (!trackerEngine.playing) return;
  const pat = trackerEngine.patterns[trackerEngine.currentPatternIdx];
  const stepMs = (60000 / trackerEngine.bpm) / 4;
  const now = audioCtx ? audioCtx.currentTime : 0;

  const stepData = pat.steps[trackerEngine.step];
  if (stepData) {
    // CH1: WSG Bass
    if (stepData[0][0] > 0) {
      playTrackerVoice('wsg', stepData[0][0], stepData[0][1], stepMs / 1000, now);
      trackerEngine.vuLevels[0] = stepData[0][1] / 15.0;
    } else {
      trackerEngine.vuLevels[0] *= 0.6;
    }

    // CH2: AY Lead
    if (stepData[1][0] > 0) {
      playTrackerVoice('ay8910', stepData[1][0], stepData[1][1], stepMs / 1000, now);
      trackerEngine.vuLevels[1] = stepData[1][1] / 15.0;
    } else {
      trackerEngine.vuLevels[1] *= 0.6;
    }

    // CH3: POKEY Arp
    if (stepData[2][0] > 0) {
      playTrackerVoice('pokey', stepData[2][0], stepData[2][1], stepMs / 1000, now);
      trackerEngine.vuLevels[2] = stepData[2][1] / 15.0;
    } else {
      trackerEngine.vuLevels[2] *= 0.6;
    }

    // CH4: Drums
    if (stepData[3] && stepData[3] !== '---') {
      playArcadeDrum(stepData[3], 15, now);
      trackerEngine.vuLevels[3] = 1.0;
    } else {
      trackerEngine.vuLevels[3] *= 0.6;
    }
  }

  // Advance step
  trackerEngine.step = (trackerEngine.step + 1) % 16;
  trackerEngine.timer = setTimeout(trackerStep, stepMs);
}

function startTracker() {
  initAudio();
  if (trackerEngine.playing) return;
  trackerEngine.playing = true;
  trackerStep();
  const btn = document.getElementById('btnQuickPlay');
  if (btn) btn.innerHTML = 'STOP<small>SPACE</small>';
}

function stopTracker() {
  trackerEngine.playing = false;
  if (trackerEngine.timer) {
    clearTimeout(trackerEngine.timer);
    trackerEngine.timer = null;
  }
  trackerEngine.vuLevels = [0, 0, 0, 0];
  const btn = document.getElementById('btnQuickPlay');
  if (btn) btn.innerHTML = 'PLAY<small>SPACE</small>';
}

function toggleTracker() {
  if (trackerEngine.playing) stopTracker();
  else startTracker();
}

function cycleTrackerPattern() {
  trackerEngine.currentPatternIdx = (trackerEngine.currentPatternIdx + 1) % trackerEngine.patterns.length;
  trackerEngine.bpm = trackerEngine.patterns[trackerEngine.currentPatternIdx].bpm;
  trackerEngine.step = 0;
  const status = document.getElementById('engineStatus');
  if (status) status.innerHTML = `TRACKER: <b>${trackerEngine.patterns[trackerEngine.currentPatternIdx].name}</b> (${trackerEngine.bpm} BPM)`;
}

function renderTrackerScreen() {
  // Deep CRT Dark Background
  ctx.fillStyle = '#0a0d14';
  ctx.fillRect(0, 0, 240, 240);

  const pat = trackerEngine.patterns[trackerEngine.currentPatternIdx];

  // 1. Header Bar (Y: 0..26)
  ctx.fillStyle = '#121622';
  ctx.fillRect(0, 0, 240, 26);
  ctx.strokeStyle = '#253045';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(0, 26); ctx.lineTo(240, 26);
  ctx.stroke();

  // Mode title
  ctx.fillStyle = '#00ff66';
  ctx.font = 'bold 9px monospace';
  ctx.textAlign = 'left';
  ctx.fillText('● TRACKER 16-STEP', 8, 11);

  // Status badge & BPM
  ctx.font = 'bold 8px monospace';
  if (trackerEngine.playing) {
    ctx.fillStyle = '#00ff88';
    ctx.fillText(`▶ RUN ${trackerEngine.bpm} BPM`, 130, 11);
  } else {
    ctx.fillStyle = '#f5a623';
    ctx.fillText(`■ STOP ${trackerEngine.bpm} BPM`, 130, 11);
  }

  // Pattern name
  ctx.fillStyle = '#8ea4b8';
  ctx.font = '7.5px monospace';
  ctx.fillText(`P${trackerEngine.currentPatternIdx + 1}: ${pat.name.slice(0, 18)}`, 8, 22);
  ctx.fillStyle = '#557788';
  ctx.textAlign = 'right';
  ctx.fillText(pat.chipType.slice(0, 14), 232, 22);

  // 2. Track Columns Header (Y: 28..38)
  ctx.textAlign = 'left';
  ctx.fillStyle = '#151b28';
  ctx.fillRect(0, 27, 240, 12);
  ctx.font = '7.5px monospace';
  ctx.fillStyle = '#556677';
  ctx.fillText('STP', 6, 36);
  ctx.fillStyle = '#f5a623';
  ctx.fillText('CH1:BAS', 36, 36);
  ctx.fillStyle = '#00e5ff';
  ctx.fillText('CH2:LED', 88, 36);
  ctx.fillStyle = '#a55eea';
  ctx.fillText('CH3:ARP', 140, 36);
  ctx.fillStyle = '#ff6b81';
  ctx.fillText('CH4:DRM', 192, 36);

  // 3. Step Matrix (Y: 40..184) - 9 visible rows centered on current step
  const curStep = trackerEngine.step;
  for (let r = -4; r <= 4; r++) {
    const sIdx = (curStep + r + 16) % 16;
    const y = 112 + r * 15;
    const isCurrent = (r === 0);
    const stepData = pat.steps[sIdx];

    if (isCurrent) {
      // High-visibility glowing neon playhead row bar
      ctx.fillStyle = 'rgba(0, 255, 102, 0.22)';
      ctx.fillRect(2, y - 10, 236, 14);
      ctx.strokeStyle = 'rgba(0, 255, 136, 0.7)';
      ctx.lineWidth = 1;
      ctx.strokeRect(2, y - 10, 236, 14);

      // Playhead arrow
      ctx.fillStyle = '#00ff88';
      ctx.font = 'bold 8px monospace';
      ctx.fillText('►', 4, y);
    }

    // Step index
    ctx.font = isCurrent ? 'bold 8px monospace' : '7.5px monospace';
    ctx.fillStyle = isCurrent ? '#00ff88' : (sIdx % 4 === 0 ? '#8fa5a0' : '#445566');
    ctx.fillText(String(sIdx).padStart(2, '0'), 14, y);

    // Channel 1: Bass
    const ch1 = stepData[0];
    ctx.fillStyle = isCurrent ? '#ffffff' : (ch1[0] > 0 ? '#f5a623' : '#334455');
    ctx.fillText(ch1[0] > 0 ? `${midiToStr(ch1[0])} ${String(ch1[1]).padStart(2,' ')}` : '--- --', 36, y);

    // Channel 2: Lead
    const ch2 = stepData[1];
    ctx.fillStyle = isCurrent ? '#ffffff' : (ch2[0] > 0 ? '#00e5ff' : '#334455');
    ctx.fillText(ch2[0] > 0 ? `${midiToStr(ch2[0])} ${String(ch2[1]).padStart(2,' ')}` : '--- --', 88, y);

    // Channel 3: Arp
    const ch3 = stepData[2];
    ctx.fillStyle = isCurrent ? '#ffffff' : (ch3[0] > 0 ? '#c780ff' : '#334455');
    ctx.fillText(ch3[0] > 0 ? `${midiToStr(ch3[0])} ${String(ch3[1]).padStart(2,' ')}` : '--- --', 140, y);

    // Channel 4: Drum
    const ch4 = stepData[3];
    ctx.fillStyle = isCurrent ? '#ffffff' : (ch4 !== '---' ? '#ff6b81' : '#334455');
    ctx.fillText(ch4, 192, y);
  }

  // 4. VU Peak Meters (Y: 184..208)
  ctx.fillStyle = '#10141e';
  ctx.fillRect(0, 185, 240, 24);
  ctx.strokeStyle = '#222d3e';
  ctx.strokeRect(0, 185, 240, 24);

  const vuCoords = [36, 88, 140, 192];
  const vuColors = ['#f5a623', '#00e5ff', '#a55eea', '#ff6b81'];
  for (let ch = 0; ch < 4; ch++) {
    const x = vuCoords[ch];
    const vu = trackerEngine.vuLevels[ch] || 0;
    const h = Math.round(vu * 18);

    ctx.fillStyle = '#1c2434';
    ctx.fillRect(x, 188, 38, 18);

    ctx.fillStyle = vuColors[ch];
    ctx.fillRect(x + 1, 206 - h, 36, h);

    trackerEngine.vuLevels[ch] *= 0.88;
  }

  // 5. 16-Step Chaser LED Pips (Y: 212..223)
  for (let s = 0; s < 16; s++) {
    const px = 12 + s * 14.2;
    const isLit = (s === curStep);
    ctx.beginPath();
    ctx.arc(px, 218, isLit ? 3.5 : 2, 0, Math.PI * 2);
    if (isLit) {
      ctx.fillStyle = '#00ff66';
      ctx.shadowColor = '#00ff66';
      ctx.shadowBlur = 8;
      ctx.fill();
      ctx.shadowBlur = 0;
    } else {
      ctx.fillStyle = s % 4 === 0 ? '#385544' : '#1c2822';
      ctx.fill();
    }
  }

  // 6. Footer Controls Hint (Y: 226..238)
  ctx.fillStyle = '#00ffcc';
  ctx.font = '7px monospace';
  ctx.textAlign = 'center';
  ctx.fillText('[SPACE]=PLAY/STOP · [KEYS]=LIVE JAM · [K1-4]=DSP', 120, 235);
}
"""

    target = "  osc.connect(gainNode); gainNode.connect(filterNode);\n    osc.start(startTime); osc.stop(startTime + dur);\n  }\n}"
    if target in code:
        code = code.replace(target, target + "\n" + synth_and_tracker_code)
        print("Successfully injected liveSynth and trackerEngine into template.bak!")
    else:
        print("Target for liveSynth injection not found!")
        return False

    # 2. Update onKeyTouch to call playLiveSynthNote
    old_key_touch = """  if (currentMode === 'tracker' || currentMode === 'vector' || currentMode === 'arcade') {
    if (isDown) {
      const freqHz = 130.81 * Math.pow(2, keyIdx / 12);
      wsgVoices[0].freq = Math.round(freqHz * 10.922667);
      wsgVoices[0].vol = 14;
    } else {
      wsgVoices[0].vol = 0;
    }
  }"""
    new_key_touch = """  // Live Multi-Engine Synthesizer across Tracker, Synth, Arcade, Vector
  playLiveSynthNote(keyIdx, isDown);"""
    if old_key_touch in code:
        code = code.replace(old_key_touch, new_key_touch)
        print("Successfully updated onKeyTouch!")
    else:
        print("old_key_touch target not found!")
        return False

    # 3. Update setMode for tracker mode
    old_tracker_mode = """      else if (mode === 'tracker') document.getElementById('engineStatus').textContent = '16-STEP CHIPTUNE TRACKER';"""
    new_tracker_mode = """      else if (mode === 'tracker') {
        document.getElementById('engineStatus').innerHTML = `16-STEP CHIPTUNE TRACKER: <b>${trackerEngine.patterns[trackerEngine.currentPatternIdx].name}</b> (${trackerEngine.bpm} BPM)`;
        document.getElementById('hudStatus').textContent = '● TRACKER (16-STEP CHIPTUNE)';
        startTracker();
      }"""
    if old_tracker_mode in code:
        code = code.replace(old_tracker_mode, new_tracker_mode)
        print("Successfully updated setMode for tracker!")
    else:
        print("old_tracker_mode target not found!")
        return False

    # Also stopTracker when leaving tracker mode
    old_pause_demo = """    if (mode === 'demo') {
      document.getElementById('engineStatus').textContent = 'DEMO SONGS JUKEBOX ACTIVE';
      playDemoSong();
    } else {
      pauseDemoSong();"""
    new_pause_demo = """    if (mode !== 'tracker') {
      stopTracker();
    }
    if (mode === 'demo') {
      document.getElementById('engineStatus').textContent = 'DEMO SONGS JUKEBOX ACTIVE';
      playDemoSong();
    } else {
      pauseDemoSong();"""
    if old_pause_demo in code:
        code = code.replace(old_pause_demo, new_pause_demo)
        print("Successfully updated stopTracker on mode switch!")
    else:
        print("old_pause_demo target not found!")
        return False

    # 4. Update mainLoop tracker rendering
    old_main_tracker = """  } else if (currentMode === 'tracker') {
    buf32.fill(0xff12141a);
    ctx.putImageData(imgData, 0, 0);
    ctx.fillStyle = '#f5a623';
    ctx.font = 'bold 12px monospace';
    ctx.fillText('16-STEP CHIPTUNE TRACKER', 12, 22);
  }"""
    new_main_tracker = """  } else if (currentMode === 'tracker') {
    renderTrackerScreen();
  }"""
    if old_main_tracker in code:
        code = code.replace(old_main_tracker, new_main_tracker)
        print("Successfully updated mainLoop tracker rendering!")
    else:
        print("old_main_tracker target not found!")
        return False

    # 5. Wire Spacebar to toggle tracker when in tracker mode
    old_space = """  else if (e.key === ' ') { quickPlay(); e.preventDefault(); }"""
    new_space = """  else if (e.key === ' ') {
    if (currentMode === 'tracker') toggleTracker();
    else if (currentMode === 'demo') { if (demoPlayer.playing) pauseDemoSong(); else playDemoSong(); }
    else quickPlay();
    e.preventDefault();
  }"""
    if old_space in code:
        code = code.replace(old_space, new_space)
        print("Successfully updated spacebar handler!")
    else:
        print("old_space target not found!")
        return False

    with open("tools/simulator_template.html.bak", "w") as f:
        f.write(code)

    return True

def update_builder():
    with open("tools/build_hardware_template.py", "r") as f:
        code = f.read()

    # In additional_bindings, wire up panel buttons btnScl, btnEnv, btnLfo, btnArp, btnSeqJuke, btnQuickPlay
    old_btn_quick = "document.getElementById('btnQuickPlay').onclick = () => { skipSplashScreen(); quickPlay(); };"
    new_btn_quick = """document.getElementById('btnQuickPlay').onclick = () => {
  skipSplashScreen();
  if (currentMode === 'tracker') toggleTracker();
  else if (currentMode === 'demo') { if (demoPlayer.playing) pauseDemoSong(); else playDemoSong(); }
  else quickPlay();
};"""
    if old_btn_quick in code:
        code = code.replace(old_btn_quick, new_btn_quick)
        print("Successfully updated btnQuickPlay in builder!")

    old_btn_seq = "const btnSeqJ = document.getElementById('btnSeqJuke');\nif (btnSeqJ) btnSeqJ.onclick = () => {\n  if (demoPlayer.playing) pauseDemoSong(); else playDemoSong();\n};"
    new_btn_seq = """const btnSeqJ = document.getElementById('btnSeqJuke');
if (btnSeqJ) btnSeqJ.onclick = () => {
  if (currentMode === 'tracker') toggleTracker();
  else if (currentMode === 'demo') { if (demoPlayer.playing) pauseDemoSong(); else playDemoSong(); }
  else setMode('tracker');
};"""
    if old_btn_seq in code:
        code = code.replace(old_btn_seq, new_btn_seq)
        print("Successfully updated btnSeqJ in builder!")

    # Wire SCL, ENV, LFO, ARP in additional_bindings
    extra_panel_buttons = """
// Function Buttons: SCL (Engine), ENV (Envelope), LFO (Vibrato), ARP (Arpeggiator)
const btnScl = document.getElementById('btnScl');
if (btnScl) btnScl.onclick = () => {
  if (currentMode === 'tracker') cycleTrackerPattern();
  else cycleSynthEngine();
};

const btnEnv = document.getElementById('btnEnv');
if (btnEnv) btnEnv.onclick = () => cycleEnvelope();

const btnLfo = document.getElementById('btnLfo');
if (btnLfo) btnLfo.onclick = () => toggleLfo();

const btnArp = document.getElementById('btnArp');
if (btnArp) btnArp.onclick = () => toggleArp();

// Octave Shifters in Synth / Tracker modes
const btnOctM = document.getElementById('btnOctMinus');
if (btnOctM) btnOctM.onclick = () => {
  initAudio();
  if (activeGame === 'cclimber' && currentMode === 'arcade') climberStep('left', 'down');
  else {
    liveSynth.octaveOffset = Math.max(-2, liveSynth.octaveOffset - 1);
    const st = document.getElementById('engineStatus');
    if (st) st.innerHTML = `SYNTH OCTAVE: <b>${liveSynth.octaveOffset >= 0 ? '+' : ''}${liveSynth.octaveOffset}</b>`;
  }
};

const btnOctP = document.getElementById('btnOctPlus');
if (btnOctP) btnOctP.onclick = () => {
  initAudio();
  if (activeGame === 'cclimber' && currentMode === 'arcade') climberStep('right', 'up');
  else {
    liveSynth.octaveOffset = Math.min(2, liveSynth.octaveOffset + 1);
    const st = document.getElementById('engineStatus');
    if (st) st.innerHTML = `SYNTH OCTAVE: <b>${liveSynth.octaveOffset >= 0 ? '+' : ''}${liveSynth.octaveOffset}</b>`;
  }
};
"""
    # Replace old Octave button handlers
    old_oct_section = """const btnOctM = document.getElementById('btnOctMinus');
if (btnOctM) btnOctM.onclick = () => {
  initAudio();
  if (activeGame === 'cclimber') climberStep('left', 'down');
  else playArcadeSfx('DK-WALK');
};

const btnOctP = document.getElementById('btnOctPlus');
if (btnOctP) btnOctP.onclick = () => {
  initAudio();
  if (activeGame === 'cclimber') climberStep('right', 'up');
  else playArcadeSfx('DK-JUMP');
};"""
    if old_oct_section in code:
        code = code.replace(old_oct_section, extra_panel_buttons)
        print("Successfully updated function buttons in builder!")
    else:
        print("old_oct_section not found in builder!")

    # Update Knob 4 (WAVE/BEND) to morph synth timbre & display active status
    old_knob4 = """setupKnob('knob4', 0, 7, 0, (v) => `WSG ${Math.round(v)}`, (v) => {
  const w = Math.round(v);
  wsgVoices[0].wave = w; wsgVoices[1].wave = w; wsgVoices[2].wave = w;
  document.getElementById('valKnob4').textContent = `WSG ${w}`;
});"""
    new_knob4 = """setupKnob('knob4', 0, 7, 0, (v) => `WSG ${Math.round(v)}`, (v) => {
  const w = Math.round(v);
  if (typeof liveSynth !== 'undefined') liveSynth.waveMorph = w;
  wsgVoices[0].wave = w; wsgVoices[1].wave = w; wsgVoices[2].wave = w;
  const label = (typeof liveSynth !== 'undefined' && liveSynth.currentEngine === 'fm') ? `FM ${w + 1}` :
                (typeof liveSynth !== 'undefined' && liveSynth.currentEngine === 'pokey') ? `DIST ${w * 14}%` :
                (currentMode === 'tracker') ? `TIMBRE ${w}` : `WSG ${w}`;
  document.getElementById('valKnob4').textContent = label;
});"""
    if old_knob4 in code:
        code = code.replace(old_knob4, new_knob4)
        print("Successfully updated knob4 handler in builder!")

    with open("tools/build_hardware_template.py", "w") as f:
        f.write(code)

    return True

if __name__ == "__main__":
    ok1 = update_template_bak()
    ok2 = update_builder()
    print("Updates complete. Success:", ok1 and ok2)
