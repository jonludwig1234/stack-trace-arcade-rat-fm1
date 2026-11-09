/**
 * M-VAVE FM-1 · World-Class 64-Bar (120.0s @ 128 BPM) Chiptune, Synthwave & Jazz-Fusion Soundtrack Engine
 *
 * Inspired by Yuzo Koshiro (Streets of Rage / Wangan Midnight), Tim Follin (Silver Surfer / Solstice),
 * Mitch Murder / LukHash (OutRun Synthwave), and Daft Punk / Justice (French Electro Slap-Bass).
 *
 * Architectural Highlights:
 * - Exact 128.0 BPM Grid (1 beat = 0.46875s, 1 bar = 1.875s, 64 bars = 120.000s)
 * - 4 Rising Key Modulations across 4 Acts:
 *     Act I   (Bars 01–16, 00.0s–30.0s): C Dorian / C Minor 9 ("Cybernetic Overture & Neon Arcade")
 *     Act II  (Bars 17–32, 30.0s–60.0s): D Harmonic Minor ("Tim Follin Virtuoso Counterpoint & Dual-Chip Solo")
 *     Act III (Bars 33–48, 60.0s–90.0s): E Dorian Jazz-Funk ("Streets of Tokyo FM Rhodes & Slap-Bass Groove")
 *     Act IV  (Bars 49–64, 90.0s–120.0s): F Minor -> F Major9 Picardy Finale ("Vocal-Pocket Groove & Grand Finale")
 * - Studio DSP Processing:
 *     1. 6-Operator FM Brass & DX7 Electric Piano (Ratio + Feedback + Pitch Envelope)
 *     2. Expressive Dual-Chip Lead (Namco WSG + PWM Pulse/Saw) with Pitch-Bend Scoops, Trills & Portamento
 *     3. 60Hz Commodore SID / AY-3-8910 Arpeggiator with PWM Sweep & Stereo Panning
 *     4. French-Touch / Koshiro FM + ZDF 24dB/oct Ladder Filter Slap Bass (with ghost notes & octave pops)
 *     5. LinnDrum / 909 Hybrid Studio Kit (Sub Kick, Layered Snare + Stereo Clap, Gated Verb, 16th Hats, Ride Bell, Stereo Tom Fills, Risers)
 *     6. Juno-60 Dual-LFO Stereo Chorus + Dotted-8th Ping-Pong Delay + Stereo Hall FDN Reverb
 */

'use strict';

function composeMasterpieceBgm(SR, TOTAL_SAMPLES) {
  const DURATION = TOTAL_SAMPLES / SR;
  const dryL = new Float64Array(TOTAL_SAMPLES);
  const dryR = new Float64Array(TOTAL_SAMPLES);
  const chorusSendL = new Float64Array(TOTAL_SAMPLES);
  const chorusSendR = new Float64Array(TOTAL_SAMPLES);
  const delaySendL = new Float64Array(TOTAL_SAMPLES);
  const delaySendR = new Float64Array(TOTAL_SAMPLES);
  const reverbSendL = new Float64Array(TOTAL_SAMPLES);
  const reverbSendR = new Float64Array(TOTAL_SAMPLES);
  const noteEvents = [];

  const BPM = 128.0;
  const BEAT = 60.0 / BPM;        // 0.46875s
  const STEP = BEAT / 4.0;        // 0.1171875s (16th note)
  const BAR = BEAT * 4.0;         // 1.875s (64 bars = 120.0s)

  const m2f = (m) => 440.0 * Math.pow(2.0, (m - 69.0) / 12.0);

  function polyblep(t, dt) {
    if (t < dt) { t /= dt; return t + t - t * t - 1.0; }
    else if (t > 1.0 - dt) { t = (t - 1.0) / dt; return t * t + t + t + 1.0; }
    return 0.0;
  }

  // ==========================================================================
  // 1. INSTRUMENT 1: 6-OP FM BRASS STABS & DX7 RHODES ELECTRIC PIANO CHORDS
  // ==========================================================================
  function addFmPolyChord(startSec, durSec, midiNotes, patch = 'brass', gain = 0.11) {
    const s0 = Math.max(0, Math.floor(startSec * SR));
    const s1 = Math.min(TOTAL_SAMPLES, Math.floor((startSec + durSec) * SR));
    for (let nIdx = 0; nIdx < midiNotes.length; nIdx++) {
      const midi = midiNotes[nIdx];
      noteEvents.push({ t: Number(startSec.toFixed(3)), d: Number(durSec.toFixed(3)), ch: 5, m: midi });
      const baseFreq = m2f(midi);
      const pan = ((nIdx / Math.max(1, midiNotes.length - 1)) - 0.5) * 0.75;
      const gL = gain * Math.cos((pan + 1) * Math.PI * 0.25);
      const gR = gain * Math.sin((pan + 1) * Math.PI * 0.25);

      let phC1 = (nIdx * 0.17) % 1.0;
      let phC2 = (nIdx * 0.53) % 1.0;
      let phM1 = 0.0, phM2 = 0.0, fb = 0.0;

      for (let i = s0; i < s1; i++) {
        const rel = (i - s0) / SR;
        let sigL = 0.0, sigR = 0.0;

        if (patch === 'brass') {
          // YM2612 / DX7 Oberheim+FM Brass: subtle pitch scoop on attack + filter/index swell
          const pitchEnv = 1.0 - 0.012 * Math.exp(-rel * 45.0);
          const f = baseFreq * pitchEnv;
          const dt1 = (f * 0.998) / SR;
          const dt2 = (f * 1.0025) / SR;
          phC1 = (phC1 + dt1) % 1.0;
          phC2 = (phC2 + dt2) % 1.0;
          phM1 = (phM1 + dt1 * 1.0) % 1.0;
          phM2 = (phM2 + dt2 * 2.0) % 1.0;

          const idxEnv = (1.0 - Math.exp(-rel * 28.0)) * Math.exp(-rel * 2.4);
          const mod1 = Math.sin(2.0 * Math.PI * phM1 + fb * 0.65) * 1.85 * idxEnv;
          fb = mod1;
          const mod2 = Math.sin(2.0 * Math.PI * phM2) * 0.75 * Math.exp(-rel * 4.5);

          const saw1 = (2.0 * phC1 - 1.0) - polyblep(phC1, dt1);
          const saw2 = (2.0 * phC2 - 1.0) - polyblep(phC2, dt2);
          const fm1 = Math.sin(2.0 * Math.PI * phC1 + mod1);
          const fm2 = Math.sin(2.0 * Math.PI * phC2 + mod1 + mod2);

          const att = Math.min(1.0, rel / 0.018);
          const dec = 0.48 + 0.52 * Math.exp(-rel * 3.8);
          const relEnv = Math.min(1.0, Math.max(0.0, (durSec - rel) / 0.08));
          const env = att * dec * relEnv;

          sigL = (saw1 * 0.42 + fm1 * 0.58) * env;
          sigR = (saw2 * 0.42 + fm2 * 0.58) * env;
        } else {
          // Lush DX7 Rhodes / Warm Analog Pad Hybrid
          const dt1 = (baseFreq * 0.9975) / SR;
          const dt2 = (baseFreq * 1.0025) / SR;
          phC1 = (phC1 + dt1) % 1.0;
          phC2 = (phC2 + dt2) % 1.0;
          phM1 = (phM1 + dt1 * 14.0) % 1.0; // classic DX7 tine ratio 14:1 on attack
          phM2 = (phM2 + dt1 * 1.0) % 1.0;

          const tine = Math.sin(2.0 * Math.PI * phM1) * 0.42 * Math.exp(-rel * 14.0);
          const warmMod = Math.sin(2.0 * Math.PI * phM2) * 0.65 * Math.exp(-rel * 1.8);
          const saw1 = (2.0 * phC1 - 1.0) - polyblep(phC1, dt1);
          const saw2 = (2.0 * phC2 - 1.0) - polyblep(phC2, dt2);
          const car1 = Math.sin(2.0 * Math.PI * phC1 + warmMod + tine);
          const car2 = Math.sin(2.0 * Math.PI * phC2 + warmMod - tine);

          const att = Math.min(1.0, rel / 0.012);
          const dec = 0.45 + 0.55 * Math.exp(-rel * 2.2);
          const relEnv = Math.min(1.0, Math.max(0.0, (durSec - rel) / 0.14));
          const env = att * dec * relEnv;

          sigL = (car1 * 0.65 + saw1 * 0.35) * env;
          sigR = (car2 * 0.65 + saw2 * 0.35) * env;
        }

        dryL[i] += sigL * gL;
        dryR[i] += sigR * gR;
        chorusSendL[i] += sigL * gL * 0.65;
        chorusSendR[i] += sigR * gR * 0.65;
        reverbSendL[i] += sigL * gL * 0.38;
        reverbSendR[i] += sigR * gR * 0.38;
      }
    }
  }

  // ==========================================================================
  // 2. INSTRUMENT 2: VIRTUOSO DUAL-CHIP LEAD (WSG + PWM + PITCH BEND & TRILLS)
  // ==========================================================================
  // Custom 32-step Namco WSG harmonic wavetable (rich vocal/brass harmonics)
  const WSG_WAVE = new Float64Array(32);
  for (let w = 0; w < 32; w++) {
    const p = w / 32.0;
    WSG_WAVE[w] = Math.tanh(
      0.95 * Math.sin(2 * Math.PI * p) +
      0.55 * Math.sin(4 * Math.PI * p + 0.4) +
      0.38 * Math.sin(6 * Math.PI * p) +
      0.25 * Math.sin(8 * Math.PI * p - 0.3) +
      0.18 * Math.sin(10 * Math.PI * p)
    );
  }

  function addVirtuosoLead(startSec, durSec, midi, opts = {}) {
    if (midi <= 0) return;
    const prevMidi = opts.prevMidi || midi;
    const gain = opts.gain || 0.165;
    const pan = opts.pan !== undefined ? opts.pan : 0.08;
    const trillSemis = opts.trill || 0;      // e.g. +2 or +1 for Tim Follin 32nd-note trill
    const bendIn = opts.bendIn || 0;        // e.g. -2 semitone pitch-wheel scoop up into the note
    const slideTime = opts.slide || 0.032;
    const style = opts.style || 'lead';     // 'lead', 'harmony', 'pokey_solo'

    noteEvents.push({ t: Number(startSec.toFixed(3)), d: Number(durSec.toFixed(3)), ch: 1, m: midi });
    const s0 = Math.max(0, Math.floor(startSec * SR));
    const s1 = Math.min(TOTAL_SAMPLES, Math.floor((startSec + durSec) * SR));

    const targetF = m2f(midi);
    const fromF = bendIn !== 0 ? m2f(midi + bendIn) : (prevMidi > 0 ? m2f(prevMidi) : targetF);
    const gL = gain * Math.cos((pan + 1) * Math.PI * 0.25);
    const gR = gain * Math.sin((pan + 1) * Math.PI * 0.25);

    let ph1 = 0.0, ph2 = 0.25, phSub = 0.0;
    let lpf1 = 0.0, lpf2 = 0.0;

    for (let i = s0; i < s1; i++) {
      const rel = (i - s0) / SR;
      let curTarget = targetF;
      if (trillSemis !== 0 && rel > 0.04) {
        const trillStep = Math.floor((rel - 0.04) * (BPM / 60.0) * 8.0) % 2;
        if (trillStep === 1) curTarget = m2f(midi + trillSemis);
      }

      const glide = slideTime > 0 ? Math.min(1.0, rel / slideTime) : 1.0;
      const smoothGlide = glide * glide * (3.0 - 2.0 * glide);
      const baseF = fromF + (curTarget - fromF) * smoothGlide;

      // Expressive delayed 6.2Hz vibrato
      const vibOnset = Math.max(0.0, rel - 0.09);
      const vibDepth = Math.min(1.0, vibOnset / 0.12) * 0.0055;
      const vib = Math.sin(2.0 * Math.PI * 6.2 * vibOnset) * vibDepth;
      const f = baseF * (1.0 + vib);
      const dt = f / SR;

      ph1 = (ph1 + dt) % 1.0;
      ph2 = (ph2 + dt * 1.004) % 1.0;
      phSub = (phSub + dt * 0.5) % 1.0;

      // PWM duty cycle modulation (0.22 .. 0.48)
      const pw = 0.34 + 0.14 * Math.sin(2.0 * Math.PI * 3.2 * rel);
      const pulse = (ph1 < pw ? 1.0 : -1.0) + polyblep(ph1, dt) - polyblep((ph1 + 1.0 - pw) % 1.0, dt);
      const saw = (2.0 * ph2 - 1.0) - polyblep(ph2, dt);
      const wsg = WSG_WAVE[Math.floor(ph1 * 32) & 31];
      const subOct = (phSub < 0.5 ? 1.0 : -1.0) + polyblep(phSub, dt * 0.5) - polyblep((phSub + 0.5) % 1.0, dt * 0.5);

      let rawL, rawR;
      if (style === 'pokey_solo') {
        // Screaming Minimoog / Atari POKEY Sync Lead
        const syncF = f * (1.8 + 1.4 * Math.exp(-rel * 5.0));
        const syncWave = Math.sin(2.0 * Math.PI * ph1 * (syncF / f));
        rawL = pulse * 0.45 + syncWave * 0.40 + subOct * 0.25;
        rawR = saw * 0.45 + syncWave * 0.40 + subOct * 0.25;
      } else {
        rawL = pulse * 0.44 + wsg * 0.38 + subOct * 0.22;
        rawR = saw * 0.44 + wsg * 0.38 + subOct * 0.22;
      }

      // Dynamic filter brightness envelope
      const cut = Math.min(0.88, 0.25 + 0.60 * Math.exp(-rel * 3.5));
      lpf1 += cut * (rawL - lpf1);
      lpf2 += cut * (rawR - lpf2);

      const att = Math.min(1.0, rel / 0.004);
      const dec = 0.58 + 0.42 * Math.exp(-rel * 4.2);
      const relEnv = Math.min(1.0, Math.max(0.0, (durSec - rel) / 0.022));
      const env = att * dec * relEnv;

      const outL = Math.tanh(lpf1 * 1.25) * env * gL;
      const outR = Math.tanh(lpf2 * 1.25) * env * gR;

      dryL[i] += outL;
      dryR[i] += outR;
      delaySendL[i] += outL * 0.48;
      delaySendR[i] += outR * 0.48;
      reverbSendL[i] += outL * 0.35;
      reverbSendR[i] += outR * 0.35;
    }
  }

  // ==========================================================================
  // 3. INSTRUMENT 3: TIM FOLLIN 60Hz SID/AY ARPEGGIATOR & HARPSICHORD PLUCK
  // ==========================================================================
  function addSidArpVoice(startSec, durSec, chordNotes, gain = 0.088, pan = -0.38) {
    noteEvents.push({ t: Number(startSec.toFixed(3)), d: Number(durSec.toFixed(3)), ch: 2, m: chordNotes[0] });
    const s0 = Math.max(0, Math.floor(startSec * SR));
    const s1 = Math.min(TOTAL_SAMPLES, Math.floor((startSec + durSec) * SR));
    const gL = gain * Math.cos((pan + 1) * Math.PI * 0.25);
    const gR = gain * Math.sin((pan + 1) * Math.PI * 0.25);
    let ph = 0.0;
    for (let i = s0; i < s1; i++) {
      const rel = (i - s0) / SR;
      const stepIdx = Math.floor(rel * 60.0) % chordNotes.length;
      const f = m2f(chordNotes[stepIdx]);
      const dt = f / SR;
      ph = (ph + dt) % 1.0;
      const pw = 0.22 + 0.15 * Math.cos(rel * 8.0);
      const p = (ph < pw ? 1.0 : -1.0) + polyblep(ph, dt) - polyblep((ph + 1.0 - pw) % 1.0, dt);
      const env = Math.min(1.0, rel / 0.002) * (0.28 + 0.72 * Math.exp(-rel * 6.5)) * Math.min(1.0, Math.max(0.0, (durSec - rel) / 0.012));
      const sigL = p * env * gL;
      const sigR = p * env * gR;
      dryL[i] += sigL;
      dryR[i] += sigR;
      delaySendL[i] += sigL * 0.35;
      delaySendR[i] += sigR * 0.35;
    }
  }

  // ==========================================================================
  // 4. INSTRUMENT 4: YUZO KOSHIRO / FRENCH-ELECTRO SLAP FM + ANALOG SUB BASS
  // ==========================================================================
  function addSlapFunkBass(startSec, durSec, midi, vel = 1.0, isSlapPop = false) {
    if (midi <= 0) return;
    noteEvents.push({ t: Number(startSec.toFixed(3)), d: Number(durSec.toFixed(3)), ch: 3, m: midi });
    const s0 = Math.max(0, Math.floor(startSec * SR));
    const s1 = Math.min(TOTAL_SAMPLES, Math.floor((startSec + durSec) * SR));
    const f = m2f(midi);
    const dt = f / SR;
    let phC = 0.0, phM = 0.0, phSub = 0.0;
    let ic1 = 0.0, ic2 = 0.0;

    const baseGain = 0.255 * vel;
    for (let i = s0; i < s1; i++) {
      const rel = (i - s0) / SR;
      phC = (phC + dt) % 1.0;
      phM = (phM + dt * (isSlapPop ? 3.0 : 2.0)) % 1.0;
      phSub = (phSub + dt * 0.5) % 1.0;

      // YM2612 / TX81Z "Lately Bass" / Slap Bass FM index envelope
      const fmIdx = (isSlapPop ? 3.2 : 2.1) * Math.exp(-rel * (isSlapPop ? 32.0 : 18.0)) + 0.35;
      const fmWave = Math.sin(2.0 * Math.PI * phC + Math.sin(2.0 * Math.PI * phM) * fmIdx);
      const saw = (2.0 * phC - 1.0) - polyblep(phC, dt);
      const sub = Math.sin(2.0 * Math.PI * phC);
      const raw = fmWave * 0.52 + saw * 0.32 + sub * 0.48;

      // 24dB/oct ZDF SVF Low-Pass Filter with snappy funk envelope
      const cutHz = 140.0 + (isSlapPop ? 3400.0 : 2100.0) * vel * Math.exp(-rel * 22.0);
      const g = Math.tan(Math.PI * Math.min(0.42, cutHz / SR));
      const k = isSlapPop ? 0.42 : 0.55; // resonant bite
      const a1 = 1.0 / (1.0 + g * (g + k));
      const a2 = g * a1;
      const a3 = g * a2;
      const v3 = raw - ic2;
      const v1 = a1 * ic1 + a2 * v3;
      const v2 = ic2 + a2 * ic1 + a3 * v3;
      ic1 = 2.0 * v1 - ic1;
      ic2 = 2.0 * v2 - ic2;

      const att = Math.min(1.0, rel / 0.002);
      const dec = 0.42 + 0.58 * Math.exp(-rel * 7.5);
      const relEnv = Math.min(1.0, Math.max(0.0, (durSec - rel) / 0.010));
      const sig = Math.tanh(v2 * 1.55) * att * dec * relEnv * baseGain;

      dryL[i] += sig;
      dryR[i] += sig;
    }
  }

  // ==========================================================================
  // 5. INSTRUMENT 5: LINNDRUM / 909 STUDIO PERCUSSION & TRANSITION FX
  // ==========================================================================
  function addStudioDrum(startSec, type, vel = 1.0, pan = 0.0) {
    const midiMap = { KCK: 36, SNR: 38, CLP: 39, HHC: 42, HHO: 46, RID: 51, TOMH: 50, TOMM: 47, TOML: 43, CRS: 49 };
    noteEvents.push({ t: Number(startSec.toFixed(3)), d: 0.12, ch: 4, m: midiMap[type] || 36 });
    const s0 = Math.max(0, Math.floor(startSec * SR));
    let rng = ((s0 * 2654435761) ^ 0x5bf03635) | 0;
    const rand = () => { rng = (rng * 1664525 + 1013904223) | 0; return ((rng >>> 0) / 2147483648.0) - 1.0; };

    const gL = Math.cos((pan + 1) * Math.PI * 0.25);
    const gR = Math.sin((pan + 1) * Math.PI * 0.25);

    if (type === 'KCK') {
      const s1 = Math.min(TOTAL_SAMPLES, s0 + Math.floor(0.26 * SR));
      let ph = 0.0;
      for (let i = s0; i < s1; i++) {
        const rel = (i - s0) / SR;
        const f = 45.0 + 160.0 * Math.exp(-rel * 55.0) + 40.0 * Math.exp(-rel * 14.0);
        ph += f / SR;
        const click = (Math.sin(2.0 * Math.PI * 1800.0 * rel) * 0.5 + rand() * 0.5) * Math.exp(-rel * 220.0) * 0.35;
        const sub = Math.sin(2.0 * Math.PI * ph) * Math.exp(-rel * 11.5);
        const sig = Math.tanh((sub + click) * 1.65) * 0.42 * vel;
        dryL[i] += sig;
        dryR[i] += sig;
      }
    } else if (type === 'SNR') {
      const s1 = Math.min(TOTAL_SAMPLES, s0 + Math.floor(0.32 * SR));
      let ph1 = 0.0, ph2 = 0.0, lpL = 0.0, lpR = 0.0;
      for (let i = s0; i < s1; i++) {
        const rel = (i - s0) / SR;
        ph1 += (195.0 + 140.0 * Math.exp(-rel * 28.0)) / SR;
        ph2 += (330.0 + 180.0 * Math.exp(-rel * 35.0)) / SR;
        const body = (Math.sin(2.0 * Math.PI * ph1) * 0.65 + Math.sin(2.0 * Math.PI * ph2) * 0.35) * Math.exp(-rel * 22.0);
        // Multi-burst clap + crisp snare wires
        const clapBurst = (rel < 0.012 || (rel > 0.015 && rel < 0.025) || rel > 0.028) ? 1.0 : 0.25;
        const nL = rand() * clapBurst;
        const nR = rand() * clapBurst;
        lpL += 0.55 * (nL - lpL);
        lpR += 0.55 * (nR - lpR);
        // 80s gated snare envelope
        const wireEnv = (rel < 0.16 ? Math.exp(-rel * 8.5) : Math.exp(-(rel - 0.16) * 35.0) * 0.25);
        const outL = Math.tanh((body * 0.55 + lpL * wireEnv * 0.72) * 1.35) * 0.30 * vel;
        const outR = Math.tanh((body * 0.55 + lpR * wireEnv * 0.72) * 1.35) * 0.30 * vel;
        dryL[i] += outL;
        dryR[i] += outR;
        reverbSendL[i] += outL * 0.45;
        reverbSendR[i] += outR * 0.45;
      }
    } else if (type === 'HHC' || type === 'HHO' || type === 'RID') {
      const dur = type === 'HHO' ? 0.24 : (type === 'RID' ? 0.38 : 0.052);
      const dec = type === 'HHO' ? 13.0 : (type === 'RID' ? 8.5 : 65.0);
      const s1 = Math.min(TOTAL_SAMPLES, s0 + Math.floor(dur * SR));
      // 6 metallic square ratios (808/909 cymbal matrix) + highpass noise
      const freqs = [820, 1145, 1580, 2120, 3190, 4450];
      let prev = 0.0;
      for (let i = s0; i < s1; i++) {
        const rel = (i - s0) / SR;
        let metal = 0.0;
        for (let f of freqs) metal += (Math.sin(2.0 * Math.PI * f * rel) > 0 ? 0.16 : -0.16);
        const n = rand() * 0.65 + metal * 0.55;
        const hp = n - prev;
        prev = n * 0.88;
        const bell = type === 'RID' ? Math.sin(2.0 * Math.PI * 2840.0 * rel) * Math.exp(-rel * 16.0) * 0.35 : 0.0;
        const sig = (hp * Math.exp(-rel * dec) + bell) * 0.115 * vel;
        dryL[i] += sig * gL;
        dryR[i] += sig * gR;
      }
    } else if (type.startsWith('TOM')) {
      const fBase = type === 'TOMH' ? 145.0 : (type === 'TOMM' ? 110.0 : 82.0);
      const s1 = Math.min(TOTAL_SAMPLES, s0 + Math.floor(0.24 * SR));
      let ph = 0.0;
      for (let i = s0; i < s1; i++) {
        const rel = (i - s0) / SR;
        ph += (fBase + fBase * 0.95 * Math.exp(-rel * 22.0)) / SR;
        const slap = rand() * Math.exp(-rel * 95.0) * 0.28;
        const sig = Math.tanh((Math.sin(2.0 * Math.PI * ph) * Math.exp(-rel * 13.0) + slap) * 1.3) * 0.29 * vel;
        dryL[i] += sig * gL;
        dryR[i] += sig * gR;
        reverbSendL[i] += sig * gL * 0.42;
        reverbSendR[i] += sig * gR * 0.42;
      }
    } else if (type === 'CRS') {
      const s1 = Math.min(TOTAL_SAMPLES, s0 + Math.floor(1.15 * SR));
      let prevL = 0.0, prevR = 0.0;
      for (let i = s0; i < s1; i++) {
        const rel = (i - s0) / SR;
        const nL = rand(), nR = rand();
        const hpL = nL - prevL; prevL = nL * 0.84;
        const hpR = nR - prevR; prevR = nR * 0.84;
        const env = Math.exp(-rel * 3.2) * 0.135 * vel;
        dryL[i] += hpL * env;
        dryR[i] += hpR * env;
        reverbSendL[i] += hpL * env * 0.5;
        reverbSendR[i] += hpR * env * 0.5;
      }
    }
  }

  function addSweepRiser(startSec, durSec, gain = 0.09) {
    const s0 = Math.max(0, Math.floor(startSec * SR));
    const s1 = Math.min(TOTAL_SAMPLES, Math.floor((startSec + durSec) * SR));
    let rng = 987654321, ic1 = 0.0, ic2 = 0.0;
    for (let i = s0; i < s1; i++) {
      const p = (i - s0) / Math.max(1, s1 - s0);
      rng = (rng * 1664525 + 1013904223) | 0;
      const n = ((rng >>> 0) / 2147483648.0) - 1.0;
      const cut = 260.0 * Math.pow(22.0, p * p);
      const g = Math.tan(Math.PI * Math.min(0.42, cut / SR));
      const k = 0.35;
      const a1 = 1.0 / (1.0 + g * (g + k));
      const a2 = g * a1;
      const v3 = n - ic2;
      const v1 = a1 * ic1 + a2 * v3;
      const v2 = ic2 + a2 * ic1 + g * a2 * v3;
      ic1 = 2.0 * v1 - ic1;
      ic2 = 2.0 * v2 - ic2;
      const pan = Math.sin(p * Math.PI * 6.0) * 0.6;
      const sig = v1 * (p * p) * gain;
      dryL[i] += sig * (1.0 - pan * 0.5);
      dryR[i] += sig * (1.0 + pan * 0.5);
      reverbSendL[i] += sig * 0.5;
      reverbSendR[i] += sig * 0.5;
    }
  }

  // ==========================================================================
  // 6. COMPOSE FULL 64-BAR (120.0s) MULTI-ACT SCORE
  // ==========================================================================
  // Helper to schedule an expressive melodic phrase (array of [stepOffset, durSteps, midi, opts])
  function schedulePhrase(barStartSec, notes, defaultOpts = {}) {
    let prevM = 0;
    for (const n of notes) {
      const [st, durSt, m, o] = n;
      if (m > 0) {
        addVirtuosoLead(
          barStartSec + st * STEP,
          durSt * STEP * 0.94,
          m,
          Object.assign({}, defaultOpts, { prevMidi: prevM }, o || {})
        );
        prevM = m;
      }
    }
  }

  // Funky syncopated 16-step bass pattern generator per bar with octave slaps, chromatic walkups & ghost pops
  function scheduleFunkBassBar(barStartSec, root, fifth, walkPair, grooveType = 'koshiro') {
    if (grooveType === 'intro') {
      // Deep pulsing synthwave sub + 8th-note build
      addSlapFunkBass(barStartSec, STEP * 6, root, 1.05, false);
      addSlapFunkBass(barStartSec + 6 * STEP, STEP * 2, root + 12, 0.95, true);
      for (let s = 8; s < 16; s++) {
        const m = (s === 14) ? walkPair[0] : (s === 15 ? walkPair[1] : (s % 2 === 1 ? root + 12 : root));
        addSlapFunkBass(barStartSec + s * STEP, STEP * 0.85, m, s % 2 === 0 ? 1.0 : 0.85, s % 2 === 1);
      }
      return;
    }

    // Yuzo Koshiro / French-Touch 16-step syncopated slap bassline
    const pattern = [
      [0, 1.8, root, 1.15, false],
      [2, 0.85, root + 12, 0.95, true],
      [3, 0.85, root, 0.78, false],
      [4, 1.8, root + 12, 1.05, true],
      [6, 0.9, fifth, 0.90, false],
      [7, 0.9, root + 12, 0.95, true],
      [8, 1.8, root, 1.12, false],
      [10, 0.85, root + 12, 0.95, true],
      [11, 0.85, fifth, 0.85, false],
      [12, 0.9, root, 1.0, false],
      [13, 0.9, root + 12, 0.95, true],
      [14, 0.95, walkPair[0], 1.05, false],
      [15, 0.95, walkPair[1], 1.10, true]
    ];
    for (const [st, dSt, m, v, slap] of pattern) {
      if (barStartSec + st * STEP < DURATION) {
        addSlapFunkBass(barStartSec + st * STEP, dSt * STEP, m, v, slap);
      }
    }
  }

  // Studio drum pattern per bar with ghost snares, open hats, ride bell, and 4-bar/8-bar stereo tom fills
  function scheduleDrumBar(barIdx, barStartSec, useRide = false, isFillBar = false, isBreakBar = false) {
    if (barIdx % 4 === 0) addStudioDrum(barStartSec, 'CRS', 0.95);
    if (barIdx % 8 === 7) addSweepRiser(barStartSec, BAR, 0.085);

    for (let s = 0; s < 16; s++) {
      const t = barStartSec + s * STEP;
      if (t >= DURATION) break;

      if (isBreakBar && s >= 8) {
        // Explosive 8-step stereo tom & snare fill
        const fillDrums = [
          ['SNR', 0.9, 0.0], ['TOMH', 0.95, -0.45], ['TOMH', 1.0, -0.35], ['SNR', 1.0, 0.0],
          ['TOMM', 1.0, 0.0], ['TOMM', 1.05, 0.15], ['TOML', 1.1, 0.45], ['SNR', 1.15, 0.0]
        ];
        const [dType, dVel, dPan] = fillDrums[s - 8];
        addStudioDrum(t, dType, dVel, dPan);
        if (s === 8 || s === 12 || s === 14) addStudioDrum(t, 'KCK', 1.05);
        continue;
      }

      // Punchy syncopated Kick (1, 2-e/2-and, 3, 3-a, 4-and)
      if (s === 0 || s === 6 || s === 8 || (s === 11 && barIdx % 2 === 1) || (s === 14 && isFillBar)) {
        addStudioDrum(t, 'KCK', s === 0 || s === 8 ? 1.10 : 0.94);
      }

      // Snare on 2 and 4 + funky ghost notes on 7, 9, 15
      if (s === 4 || s === 12) {
        addStudioDrum(t, 'SNR', 1.08);
      } else if ((s === 7 || s === 9) && barIdx % 2 === 0) {
        addStudioDrum(t, 'SNR', 0.34); // ghost snare
      }

      // 4-Bar Mini Fill on steps 13, 14, 15
      if (isFillBar && s >= 13) {
        const tomMap = { 13: ['TOMH', -0.4], 14: ['TOMM', 0.1], 15: ['TOML', 0.45] };
        addStudioDrum(t, tomMap[s][0], 0.96, tomMap[s][1]);
      }

      // Stereo Hi-Hats & Ride Cymbal Bell
      if (useRide && s % 2 === 0) {
        addStudioDrum(t, 'RID', (s % 4 === 0) ? 0.88 : 0.65, 0.28);
      }
      if (s % 4 === 2) {
        addStudioDrum(t, 'HHO', 0.85, -0.25);
      } else {
        addStudioDrum(t, 'HHC', (s % 2 === 0) ? 0.72 : 0.46, -0.22);
      }
    }
  }

  // --------------------------------------------------------------------------
  // ACT I (Bars 0..15, 0.0s - 30.0s): C DORIAN / C MINOR 9 — "NEON ARCADE"
  // --------------------------------------------------------------------------
  const act1Chords = [
    // Bars 0..3 & 4..7: Cm9 -> AbMaj9 -> Fm11 -> G7#9(b13)
    { root: 36, fifth: 43, walk: [41, 43], chord: [60, 63, 67, 70, 74], arp: [60, 63, 67, 70, 74, 79] },
    { root: 32, fifth: 39, walk: [39, 40], chord: [56, 60, 63, 67, 70], arp: [56, 60, 63, 67, 72, 75] },
    { root: 29, fifth: 36, walk: [34, 36], chord: [53, 56, 60, 63, 67], arp: [53, 56, 60, 65, 68, 72] },
    { root: 31, fifth: 38, walk: [41, 43], chord: [55, 59, 63, 65, 70], arp: [55, 59, 62, 65, 68, 74] },
    // Bars 8..11: Turnaround variation: Cm9 -> Bb13 -> AbMaj7#11 -> G7alt
    { root: 36, fifth: 43, walk: [43, 41], chord: [60, 63, 67, 70, 74], arp: [60, 63, 67, 72, 74, 79] },
    { root: 34, fifth: 41, walk: [36, 34], chord: [58, 62, 65, 68, 72], arp: [58, 62, 65, 70, 74, 79] },
    { root: 32, fifth: 39, walk: [34, 36], chord: [56, 60, 63, 67, 74], arp: [56, 60, 63, 67, 74, 79] },
    { root: 31, fifth: 38, walk: [35, 37], chord: [55, 59, 63, 65, 70], arp: [55, 59, 63, 68, 71, 74] },
    // Bars 12..15: Soaring B-Section Pre-Modulation Lift: AbMaj9 -> Gm7 -> Fm9 -> A7alt (modulates to Dm!)
    { root: 32, fifth: 39, walk: [34, 35], chord: [56, 60, 63, 67, 70], arp: [60, 63, 67, 70, 75, 80] },
    { root: 31, fifth: 38, walk: [34, 31], chord: [55, 58, 62, 65, 69], arp: [58, 62, 65, 70, 74, 79] },
    { root: 29, fifth: 36, walk: [31, 32], chord: [53, 56, 60, 63, 67], arp: [56, 60, 65, 68, 72, 77] },
    { root: 33, fifth: 40, walk: [36, 37], chord: [57, 61, 64, 67, 70], arp: [57, 61, 64, 67, 70, 76] }
  ];

  for (let b = 0; b < 16; b++) {
    const tBar = b * BAR;
    const cData = b < 4 ? act1Chords[b] : act1Chords[b - 4];

    // Warm Rhodes pad + syncopated FM brass stabs on anticipations
    addFmPolyChord(tBar, BAR * 0.62, cData.chord, 'rhodes', 0.085);
    addFmPolyChord(tBar + 6 * STEP, STEP * 3.5, cData.chord, 'brass', 0.095);
    addFmPolyChord(tBar + 12 * STEP, STEP * 3.8, cData.chord, 'brass', 0.090);

    // 60Hz SID Arpeggiator on every 8th note
    for (let s = 0; s < 16; s += 2) {
      addSidArpVoice(tBar + s * STEP, STEP * 1.9, cData.arp, 0.082, (s % 4 === 0) ? -0.42 : 0.42);
    }

    scheduleFunkBassBar(tBar, cData.root, cData.fifth, cData.walk, b < 2 ? 'intro' : 'koshiro');
    scheduleDrumBar(b, tBar, b >= 8, b % 4 === 3, b === 15);
  }

  // Act I Expressive Lead Melodies (16 full bars of evolving melodic storytelling!)
  // Bars 0..3: Heroic Overture Fanfare
  schedulePhrase(0 * BAR, [[0, 6, 72, { bendIn: -2 }], [6, 2, 74], [8, 4, 75], [12, 2, 79], [14, 2, 77]]);
  schedulePhrase(1 * BAR, [[0, 6, 75, { trill: 2 }], [6, 2, 72], [8, 4, 70], [12, 4, 67]]);
  schedulePhrase(2 * BAR, [[0, 3, 68], [3, 3, 72], [6, 2, 75], [8, 4, 77, { bendIn: -1 }], [12, 2, 79], [14, 2, 80]]);
  schedulePhrase(3 * BAR, [[0, 4, 79, { trill: 1 }], [4, 2, 77], [6, 2, 75], [8, 2, 74], [10, 2, 75], [12, 4, 79]]);

  // Bars 4..7: Main Neon OutRun Hook (A1)
  schedulePhrase(4 * BAR, [[0, 3, 79, { bendIn: -2 }], [3, 1, 77], [4, 2, 75], [6, 2, 72], [8, 3, 74], [11, 1, 75], [12, 2, 77], [14, 2, 79]]);
  schedulePhrase(5 * BAR, [[0, 4, 80, { trill: 2 }], [4, 2, 79], [6, 2, 75], [8, 3, 72], [11, 1, 70], [12, 4, 72]]);
  schedulePhrase(6 * BAR, [[0, 2, 68], [2, 2, 72], [4, 2, 75], [6, 2, 77], [8, 3, 79, { bendIn: -2 }], [11, 1, 80], [12, 2, 82], [14, 2, 84]]);
  schedulePhrase(7 * BAR, [[0, 6, 83, { trill: 1 }], [6, 2, 80], [8, 2, 79], [10, 2, 77], [12, 2, 75], [14, 2, 74]]);

  // Bars 8..11: Answering High-Octave Virtuoso Hook (A2) + Harmony in 3rds
  schedulePhrase(8 * BAR, [[0, 3, 84, { bendIn: -2 }], [3, 1, 82], [4, 2, 79], [6, 2, 75], [8, 2, 77], [10, 2, 79], [12, 2, 82], [14, 2, 84]]);
  schedulePhrase(9 * BAR, [[0, 3, 86, { bendIn: -2 }], [3, 1, 84], [4, 2, 82], [6, 2, 79], [8, 4, 77, { trill: 2 }], [12, 4, 74]]);
  schedulePhrase(10 * BAR, [[0, 2, 75], [2, 2, 79], [4, 2, 80], [6, 2, 82], [8, 3, 84], [11, 1, 86], [12, 2, 87], [14, 2, 86]]);
  schedulePhrase(11 * BAR, [[0, 4, 86, { trill: 1 }], [4, 2, 83], [6, 2, 79], [8, 2, 77], [10, 2, 74], [12, 4, 79]]);

  // Bars 12..15: Soaring B-Section Bridge with Dual-Lead Harmony (Pan L & R) preparing Dm modulation!
  const bSecMain = [
    [[0, 4, 80, { bendIn: -2 }], [4, 2, 79], [6, 2, 75], [8, 4, 77], [12, 2, 79], [14, 2, 80]],
    [[0, 4, 79, { trill: 2 }], [4, 2, 77], [6, 2, 74], [8, 4, 75], [12, 2, 77], [14, 2, 79]],
    [[0, 3, 77], [3, 3, 80], [6, 2, 84], [8, 4, 82, { trill: 2 }], [12, 2, 80], [14, 2, 79]],
    [[0, 3, 81, { bendIn: -2 }], [3, 1, 79], [4, 2, 76], [6, 2, 73], [8, 2, 76], [10, 2, 79], [12, 2, 81], [14, 2, 85]]
  ];
  const bSecHarm = [
    [[0, 4, 75], [4, 2, 75], [6, 2, 72], [8, 4, 72], [12, 2, 75], [14, 2, 75]],
    [[0, 4, 74], [4, 2, 74], [6, 2, 70], [8, 4, 70], [12, 2, 74], [14, 2, 74]],
    [[0, 3, 72], [3, 3, 75], [6, 2, 80], [8, 4, 77], [12, 2, 75], [14, 2, 75]],
    [[0, 3, 76], [3, 1, 73], [4, 2, 69], [6, 2, 67], [8, 2, 69], [10, 2, 73], [12, 2, 76], [14, 2, 81]]
  ];
  for (let i = 0; i < 4; i++) {
    schedulePhrase((12 + i) * BAR, bSecMain[i], { pan: -0.25, gain: 0.145 });
    schedulePhrase((12 + i) * BAR, bSecHarm[i], { pan: 0.30, gain: 0.105 });
  }

  // --------------------------------------------------------------------------
  // ACT II (Bars 16..31, 30.0s - 60.0s): D HARMONIC MINOR — "VIRTUOSO COUNTERPOINT & SOLO"
  // --------------------------------------------------------------------------
  const act2Chords = [
    // Dm9 -> BbMaj9 -> Gm11 -> A7(b9,#9) -> Dm9 -> Cm9 -> F13 -> BbMaj7#11 -> A7alt
    { root: 38, fifth: 45, walk: [36, 37], chord: [62, 65, 69, 72, 76], arp: [62, 65, 69, 74, 77, 81] },
    { root: 34, fifth: 41, walk: [33, 31], chord: [58, 62, 65, 69, 72], arp: [58, 62, 65, 70, 74, 77] },
    { root: 31, fifth: 38, walk: [32, 33], chord: [55, 58, 62, 65, 69], arp: [55, 58, 62, 67, 70, 74] },
    { root: 33, fifth: 40, walk: [36, 37], chord: [57, 61, 64, 67, 70], arp: [57, 61, 64, 69, 73, 76] },
    { root: 38, fifth: 45, walk: [40, 36], chord: [62, 65, 69, 72, 76], arp: [62, 65, 69, 74, 77, 84] },
    { root: 36, fifth: 43, walk: [40, 41], chord: [60, 63, 67, 70, 74], arp: [60, 63, 67, 72, 76, 79] },
    { root: 34, fifth: 41, walk: [36, 37], chord: [58, 62, 65, 69, 76], arp: [58, 62, 65, 69, 74, 81] },
    { root: 33, fifth: 40, walk: [37, 39], chord: [57, 61, 64, 67, 73], arp: [57, 61, 64, 70, 73, 79] }
  ];

  for (let b = 16; b < 32; b++) {
    const tBar = b * BAR;
    const cData = act2Chords[(b - 16) % 8];

    addFmPolyChord(tBar, STEP * 5.5, cData.chord, 'brass', 0.095);
    addFmPolyChord(tBar + 6 * STEP, STEP * 4.5, cData.chord, 'rhodes', 0.088);
    addFmPolyChord(tBar + 11 * STEP, STEP * 4.5, cData.chord, 'brass', 0.092);

    for (let s = 0; s < 16; s += 2) {
      addSidArpVoice(tBar + s * STEP, STEP * 1.9, cData.arp, 0.085, (s % 4 === 0) ? 0.40 : -0.40);
    }

    scheduleFunkBassBar(tBar, cData.root, cData.fifth, cData.walk, 'koshiro');
    scheduleDrumBar(b, tBar, b >= 24, b % 4 === 3, b === 31);
  }

  // Bars 16..23: Tim Follin / Gyruss Baroque 16th-Note Neo-Classical Lead Theme
  schedulePhrase(16 * BAR, [[0,2,86,{bendIn:-2}], [2,1,84], [3,1,81], [4,2,77], [6,2,81], [8,2,86], [10,2,88,{trill:1}], [12,2,86], [14,2,84]]);
  schedulePhrase(17 * BAR, [[0,2,82], [2,1,81], [3,1,77], [4,2,74], [6,2,77], [8,2,82], [10,2,86,{trill:2}], [12,4,81]]);
  schedulePhrase(18 * BAR, [[0,2,79], [2,2,82], [4,2,86], [6,2,89], [8,3,88,{bendIn:-1}], [11,1,86], [12,2,82], [14,2,79]]);
  schedulePhrase(19 * BAR, [[0,2,81,{trill:1}], [2,2,79], [4,2,76], [6,2,73], [8,1,76], [9,1,79], [10,1,81], [11,1,82], [12,2,85], [14,2,88]]);
  schedulePhrase(20 * BAR, [[0,3,90,{bendIn:-2}], [3,1,88], [4,2,86], [6,2,81], [8,2,84], [10,2,86], [12,2,88], [14,2,89]]);
  schedulePhrase(21 * BAR, [[0,3,88,{trill:2}], [3,1,86], [4,2,84], [6,2,79], [8,2,81], [10,2,84], [12,4,86]]);
  schedulePhrase(22 * BAR, [[0,2,82], [2,2,86], [4,2,89], [6,2,93], [8,4,91,{bendIn:-2}], [12,2,89], [14,2,86]]);
  schedulePhrase(23 * BAR, [[0,4,88,{trill:1}], [4,2,85], [6,2,81], [8,2,79], [10,2,76], [12,4,81]]);

  // Bars 24..31: Blistering POKEY Sync + FM Lead Trading Solos (aligned with Chapter 4 Synth Studio!)
  schedulePhrase(24 * BAR, [[0,3,74,{bendIn:-2}], [3,1,77], [4,2,81], [6,2,84], [8,2,86,{trill:2}], [10,2,84], [12,2,81], [14,2,77]], { style: 'pokey_solo' });
  schedulePhrase(25 * BAR, [[0,2,82,{bendIn:-1}], [2,2,86], [4,2,89], [6,2,86], [8,3,84,{trill:2}], [11,1,81], [12,4,77]], { style: 'pokey_solo' });
  schedulePhrase(26 * BAR, [[0,1,79], [1,1,82], [2,1,86], [3,1,89], [4,3,91,{bendIn:-2}], [7,1,89], [8,2,86], [10,2,82], [12,4,79,{trill:3}]], { style: 'pokey_solo' });
  schedulePhrase(27 * BAR, [[0,2,81], [2,2,85], [4,2,88], [6,2,91], [8,4,93,{trill:1}], [12,2,91], [14,2,88]], { style: 'pokey_solo' });
  schedulePhrase(28 * BAR, [[0,4,86,{bendIn:-2}], [4,2,81], [6,2,77], [8,4,84,{trill:2}], [12,2,81], [14,2,76]]);
  schedulePhrase(29 * BAR, [[0,3,79,{bendIn:-2}], [3,1,84], [4,2,88], [6,2,91], [8,4,89,{trill:2}], [12,4,84]]);
  schedulePhrase(30 * BAR, [[0,2,82], [2,2,86], [4,2,89], [6,2,93], [8,3,94,{bendIn:-2}], [11,1,93], [12,2,89], [14,2,86]]);
  schedulePhrase(31 * BAR, [[0,3,88,{trill:1}], [3,1,85], [4,2,81], [6,2,79], [8,2,81], [10,2,83], [12,2,86], [14,2,90]]);

  // --------------------------------------------------------------------------
  // ACT III (Bars 32..47, 60.0s - 90.0s): E DORIAN JAZZ-FUNK — "STREETS OF TOKYO"
  // --------------------------------------------------------------------------
  const act3Chords = [
    // Em9 -> A13 -> Cmaj9(#11) -> Bm7b5 / E7#9 -> Am9 -> D13 -> Gmaj9 -> F#m7b5 / B7alt
    { root: 40, fifth: 47, walk: [42, 43], chord: [64, 67, 71, 74, 78], arp: [64, 67, 71, 74, 78, 83] },
    { root: 33, fifth: 40, walk: [35, 36], chord: [57, 61, 64, 67, 71], arp: [57, 61, 66, 69, 73, 76] },
    { root: 36, fifth: 43, walk: [38, 35], chord: [60, 64, 67, 71, 78], arp: [60, 64, 67, 71, 74, 78] },
    { root: 35, fifth: 42, walk: [38, 40], chord: [59, 62, 65, 68, 74], arp: [59, 64, 68, 71, 74, 79] },
    { root: 33, fifth: 40, walk: [35, 36], chord: [57, 60, 64, 67, 71], arp: [57, 60, 64, 69, 71, 76] },
    { root: 38, fifth: 45, walk: [40, 42], chord: [62, 66, 69, 72, 76], arp: [62, 66, 69, 74, 76, 81] },
    { root: 31, fifth: 38, walk: [33, 34], chord: [55, 59, 62, 66, 69], arp: [55, 59, 62, 67, 71, 74] },
    { root: 35, fifth: 42, walk: [38, 39], chord: [59, 63, 66, 69, 75], arp: [59, 63, 66, 71, 75, 78] }
  ];

  for (let b = 32; b < 48; b++) {
    const tBar = b * BAR;
    const cData = act3Chords[(b - 32) % 8];

    // Syncopated Jazz-Funk Rhodes & FM Brass comping
    addFmPolyChord(tBar, STEP * 3.5, cData.chord, 'rhodes', 0.092);
    addFmPolyChord(tBar + 4 * STEP, STEP * 2.5, cData.chord, 'brass', 0.095);
    addFmPolyChord(tBar + 7 * STEP, STEP * 4.5, cData.chord, 'rhodes', 0.088);
    addFmPolyChord(tBar + 12 * STEP, STEP * 3.5, cData.chord, 'brass', 0.092);

    for (let s = 0; s < 16; s += 2) {
      addSidArpVoice(tBar + s * STEP, STEP * 1.9, cData.arp, 0.082, (s % 4 === 0) ? -0.38 : 0.38);
    }

    scheduleFunkBassBar(tBar, cData.root, cData.fifth, cData.walk, 'koshiro');
    scheduleDrumBar(b, tBar, true, b % 4 === 3, b === 47);
  }

  // Bars 32..47: Catchy Tokyo Jazz-Fusion & Arcade Boss Lead Theme
  schedulePhrase(32 * BAR, [[0,3,79,{bendIn:-2}], [3,1,81], [4,2,83], [6,2,86], [8,3,85,{trill:1}], [11,1,83], [12,2,79], [14,2,76]]);
  schedulePhrase(33 * BAR, [[0,3,81,{bendIn:-2}], [3,1,83], [4,2,85], [6,2,88], [8,4,86,{trill:2}], [12,4,81]]);
  schedulePhrase(34 * BAR, [[0,2,83], [2,2,86], [4,2,88], [6,2,91], [8,3,90,{bendIn:-2}], [11,1,88], [12,2,86], [14,2,83]]);
  schedulePhrase(35 * BAR, [[0,3,86,{trill:2}], [3,1,83], [4,2,80], [6,2,76], [8,2,80], [10,2,83], [12,4,86]]);
  schedulePhrase(36 * BAR, [[0,3,84,{bendIn:-2}], [3,1,81], [4,2,79], [6,2,76], [8,2,79], [10,2,81], [12,2,84], [14,2,86]]);
  schedulePhrase(37 * BAR, [[0,3,86,{bendIn:-2}], [3,1,84], [4,2,81], [6,2,78], [8,4,81,{trill:1}], [12,4,86]]);
  schedulePhrase(38 * BAR, [[0,2,83], [2,2,86], [4,2,90], [6,2,91], [8,4,93,{bendIn:-2}], [12,2,91], [14,2,88]]);
  schedulePhrase(39 * BAR, [[0,4,90,{trill:1}], [4,2,87], [6,2,83], [8,2,81], [10,2,78], [12,4,83]]);
  // Bars 40..47: High-Octave Boss Anthem (leads right into SFX Soundboard!)
  for (let rep = 0; rep < 2; rep++) {
    const baseB = 40 + rep * 4;
    schedulePhrase((baseB + 0) * BAR, [[0,2,88,{bendIn:-2}], [2,2,86], [4,2,83], [6,2,79], [8,3,83], [11,1,86], [12,2,88], [14,2,91]]);
    schedulePhrase((baseB + 1) * BAR, [[0,3,90,{trill:2}], [3,1,88], [4,2,85], [6,2,81], [8,4,85], [12,4,88]]);
    schedulePhrase((baseB + 2) * BAR, [[0,2,84], [2,2,88], [4,2,91], [6,2,95], [8,4,93,{bendIn:-2}], [12,2,91], [14,2,88]]);
    schedulePhrase((baseB + 3) * BAR, [[0,4,90,{trill:1}], [4,2,87], [6,2,83], [8,2,84], [10,2,86], [12,4,91]]);
  }

  // --------------------------------------------------------------------------
  // ACT IV (Bars 48..63, 90.0s - 120.0s): F MINOR -> F MAJOR 9 PICARDY FINALE
  // --------------------------------------------------------------------------
  const act4Chords = [
    // Fm9 -> DbMaj9 -> Bbm11 -> C7#9(b13) -> Fm9 -> Eb13 -> DbMaj7#11 -> C7alt
    { root: 29, fifth: 36, walk: [31, 32], chord: [53, 56, 60, 63, 67], arp: [60, 65, 68, 72, 75, 79] },
    { root: 37, fifth: 44, walk: [36, 34], chord: [61, 65, 68, 72, 75], arp: [61, 65, 68, 72, 75, 80] },
    { root: 34, fifth: 41, walk: [34, 35], chord: [58, 61, 65, 68, 72], arp: [58, 61, 65, 70, 73, 77] },
    { root: 36, fifth: 43, walk: [39, 40], chord: [60, 64, 68, 70, 75], arp: [60, 64, 67, 70, 75, 79] },
    { root: 29, fifth: 36, walk: [36, 34], chord: [53, 56, 60, 63, 67], arp: [60, 65, 68, 72, 77, 80] },
    { root: 39, fifth: 46, walk: [38, 37], chord: [63, 67, 70, 73, 77], arp: [63, 67, 70, 75, 79, 82] },
    { root: 37, fifth: 44, walk: [39, 36], chord: [61, 65, 68, 72, 79], arp: [61, 65, 68, 72, 77, 84] },
    { root: 36, fifth: 43, walk: [39, 41], chord: [60, 64, 68, 70, 75], arp: [60, 64, 68, 72, 76, 80] }
  ];

  for (let b = 48; b < 62; b++) {
    const tBar = b * BAR;
    const cData = act4Chords[(b - 48) % 8];

    addFmPolyChord(tBar, BAR * 0.72, cData.chord, 'rhodes', 0.095);
    addFmPolyChord(tBar + 6 * STEP, STEP * 3.5, cData.chord, 'brass', 0.092);
    addFmPolyChord(tBar + 12 * STEP, STEP * 3.5, cData.chord, 'brass', 0.088);

    for (let s = 0; s < 16; s += 2) {
      addSidArpVoice(tBar + s * STEP, STEP * 1.9, cData.arp, 0.082, (s % 4 === 0) ? -0.42 : 0.42);
    }

    scheduleFunkBassBar(tBar, cData.root, cData.fifth, cData.walk, 'koshiro');
    scheduleDrumBar(b, tBar, b >= 56, b % 4 === 3, b === 61);
  }

  // Bars 48..61: Soaring F-Minor / Ab-Major Finale Lead Anthem
  for (let rep = 0; rep < 2; rep++) {
    const baseB = 48 + rep * 6;
    schedulePhrase((baseB + 0) * BAR, [[0,3,80,{bendIn:-2}], [3,1,84], [4,2,89], [6,2,87], [8,3,84,{trill:1}], [11,1,80], [12,4,77]]);
    schedulePhrase((baseB + 1) * BAR, [[0,3,85,{bendIn:-2}], [3,1,84], [4,2,80], [6,2,77], [8,4,80,{trill:2}], [12,4,84]]);
    schedulePhrase((baseB + 2) * BAR, [[0,2,82], [2,2,85], [4,2,89], [6,2,92], [8,4,91,{bendIn:-2}], [12,2,89], [14,2,85]]);
    schedulePhrase((baseB + 3) * BAR, [[0,4,88,{trill:1}], [4,2,85], [6,2,82], [8,2,79], [10,2,82], [12,4,88]]);
    if (baseB + 4 < 62) {
      schedulePhrase((baseB + 4) * BAR, [[0,3,92,{bendIn:-2}], [3,1,89], [4,2,87], [6,2,84], [8,4,87,{trill:2}], [12,4,92]]);
      schedulePhrase((baseB + 5) * BAR, [[0,3,91,{trill:2}], [3,1,89], [4,2,87], [6,2,84], [8,2,85], [10,2,88], [12,4,91]]);
    }
  }

  // Bars 62..63 (116.25s - 120.0s): Grand Symphonic F Major 9 (#11) Picardy Third Finale Cadence!
  const tFin = 62 * BAR;
  const picardyChord = [53, 60, 65, 69, 72, 76, 79, 83]; // F - C - F - A - C - E - G - B (FMaj9#11)
  addStudioDrum(tFin, 'CRS', 1.15);
  addStudioDrum(tFin, 'KCK', 1.20);
  addSlapFunkBass(tFin, 3.2, 29, 1.20, true); // Low F1 sub
  addFmPolyChord(tFin, 3.2, picardyChord, 'brass', 0.125);
  addFmPolyChord(tFin, 3.3, picardyChord, 'rhodes', 0.110);
  addVirtuosoLead(tFin, 3.1, 89, { bendIn: -2, gain: 0.175, pan: -0.25 }); // High F6
  addVirtuosoLead(tFin, 3.1, 84, { bendIn: -2, gain: 0.145, pan: 0.25 });  // High C6

  // ==========================================================================
  // 7. STUDIO FX BUS: JUNO-60 STEREO CHORUS + PING-PONG DELAY + HALL REVERB
  // ==========================================================================
  const outL = new Float64Array(TOTAL_SAMPLES);
  const outR = new Float64Array(TOTAL_SAMPLES);

  // 7a) Juno-60 Dual-LFO Stereo Chorus (modulating 7ms..13ms delay lines in opposite phase)
  const maxChorusBuf = Math.ceil(0.025 * SR);
  const chBufL = new Float64Array(maxChorusBuf);
  const chBufR = new Float64Array(maxChorusBuf);
  let chWrite = 0;

  // 7b) Dotted-8th (3 * STEP = 0.35156s) Stereo Ping-Pong Tape Delay with Warm High-Cut
  const dlySamples = Math.floor(3.0 * STEP * SR);
  const dlyBufL = new Float64Array(TOTAL_SAMPLES);
  const dlyBufR = new Float64Array(TOTAL_SAMPLES);
  let dlyLpL = 0.0, dlyLpR = 0.0;

  // 7c) 4-Comb + 2-Allpass Stereo Studio Hall Reverb
  const combLensL = [1557, 1617, 1491, 1422].map(n => Math.floor(n * (SR / 44100)));
  const combLensR = [1557 + 23, 1617 + 23, 1491 + 23, 1422 + 23].map(n => Math.floor(n * (SR / 44100)));
  const combsL = combLensL.map(l => new Float64Array(l));
  const combsR = combLensR.map(l => new Float64Array(l));
  const combIdxL = [0, 0, 0, 0], combIdxR = [0, 0, 0, 0];
  const combStoreL = [0, 0, 0, 0], combStoreR = [0, 0, 0, 0];

  const apLensL = [225, 556].map(n => Math.floor(n * (SR / 44100)));
  const apLensR = [225 + 19, 556 + 19].map(n => Math.floor(n * (SR / 44100)));
  const apL = apLensL.map(l => new Float64Array(l));
  const apR = apLensR.map(l => new Float64Array(l));
  const apIdxL = [0, 0], apIdxR = [0, 0];

  for (let i = 0; i < TOTAL_SAMPLES; i++) {
    const t = i / SR;

    // 1. Juno-60 Stereo Chorus
    chBufL[chWrite] = chorusSendL[i];
    chBufR[chWrite] = chorusSendR[i];
    const lfo = Math.sin(2.0 * Math.PI * 0.65 * t);
    const dL = (0.0095 + 0.0032 * lfo) * SR;
    const dR = (0.0095 - 0.0032 * lfo) * SR;
    const rIdxL = (chWrite - Math.floor(dL) + maxChorusBuf) % maxChorusBuf;
    const rIdxR = (chWrite - Math.floor(dR) + maxChorusBuf) % maxChorusBuf;
    const cOutL = chBufL[rIdxL] * 0.7 + chBufR[rIdxR] * 0.3;
    const cOutR = chBufR[rIdxR] * 0.7 + chBufL[rIdxL] * 0.3;
    chWrite = (chWrite + 1) % maxChorusBuf;

    // 2. Dotted-8th Stereo Ping-Pong Delay
    const prevDlyL = i >= dlySamples ? dlyBufR[i - dlySamples] : 0.0;
    const prevDlyR = i >= dlySamples ? dlyBufL[i - dlySamples] : 0.0;
    dlyLpL += 0.38 * ((delaySendL[i] + prevDlyL * 0.42) - dlyLpL);
    dlyLpR += 0.38 * ((delaySendR[i] + prevDlyR * 0.42) - dlyLpR);
    dlyBufL[i] = dlyLpL;
    dlyBufR[i] = dlyLpR;

    // 3. Stereo Hall Reverb
    const revInL = reverbSendL[i] + dlyLpL * 0.18;
    const revInR = reverbSendR[i] + dlyLpR * 0.18;
    let rSumL = 0.0, rSumR = 0.0;
    for (let c = 0; c < 4; c++) {
      const idxL = combIdxL[c];
      const outCL = combsL[c][idxL];
      combStoreL[c] = outCL * 0.78 + combStoreL[c] * 0.22;
      combsL[c][idxL] = revInL + combStoreL[c] * 0.82;
      combIdxL[c] = (idxL + 1) % combLensL[c];
      rSumL += outCL;

      const idxR = combIdxR[c];
      const outCR = combsR[c][idxR];
      combStoreR[c] = outCR * 0.78 + combStoreR[c] * 0.22;
      combsR[c][idxR] = revInR + combStoreR[c] * 0.82;
      combIdxR[c] = (idxR + 1) % combLensR[c];
      rSumR += outCR;
    }
    rSumL *= 0.22;
    rSumR *= 0.22;
    for (let a = 0; a < 2; a++) {
      const iaL = apIdxL[a];
      const bufOutL = apL[a][iaL];
      apL[a][iaL] = rSumL + bufOutL * 0.5;
      rSumL = bufOutL - rSumL * 0.5;
      apIdxL[a] = (iaL + 1) % apLensL[a];

      const iaR = apIdxR[a];
      const bufOutR = apR[a][iaR];
      apR[a][iaR] = rSumR + bufOutR * 0.5;
      rSumR = bufOutR - rSumR * 0.5;
      apIdxR[a] = (iaR + 1) % apLensR[a];
    }

    // Master Bus Summation + Soft-Clip Mastering Exciter
    const mixL = dryL[i] + cOutL * 0.55 + dlyLpL * 0.34 + rSumL * 0.32;
    const mixR = dryR[i] + cOutR * 0.55 + dlyLpR * 0.34 + rSumR * 0.32;
    outL[i] = Math.tanh(mixL * 1.18) * 0.94;
    outR[i] = Math.tanh(mixR * 1.18) * 0.94;
  }

  return { bgmL: outL, bgmR: outR, noteEvents };
}

module.exports = { composeMasterpieceBgm };
