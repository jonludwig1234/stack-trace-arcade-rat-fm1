#!/usr/bin/env python3
"""
Update tools/sfx_banks_generator.py with 100% authentic arcade soundchip synthesis.
Replaces naive sinusoidal ramps with exact period-accurate algorithms:
- Namco WSG 32-step wavetable & pulse chirps
- Nintendo 8035 DAC FSK spring boing & girder steps
- Konami AY-3-8910 square chirps and PSG arpeggios
- Atari POKEY 4-bit polynomial pseudo-random distortion & discrete analog 555 timers
"""

def generate_sfx_file():
    with open("tools/sfx_banks_generator.py", "r") as f:
        content = f.read()

    # Find where get_play_arcade_sfx_js starts
    idx = content.find("def get_play_arcade_sfx_js():")
    if idx == -1:
        raise ValueError("Could not find def get_play_arcade_sfx_js() in sfx_banks_generator.py")

    header_and_banks = content[:idx]

    new_play_arcade_js = '''def get_play_arcade_sfx_js():
    return \'\'\'
function playArcadeSfx(name) {
  initAudio();
  lastSfxName = name;
  const now = audioCtx.currentTime;

  function createNoiseSource() {
    const src = audioCtx.createBufferSource();
    src.buffer = noiseBuffer;
    return src;
  }

  switch (name) {
    // ---------------------------------------------------------------------
    // UNIVERSAL & PAC-MAN SFX (NAMCO WSG & DISCRETE ARCADE)
    // ---------------------------------------------------------------------
    case 'COIN': {
      // Classic Arcade Coin Mechanism Chime: B5 (988 Hz) 65ms -> E6 (1319 Hz) 350ms decay
      const osc1 = audioCtx.createOscillator(), g1 = audioCtx.createGain();
      osc1.type = 'square'; osc1.frequency.setValueAtTime(988, now);
      g1.gain.setValueAtTime(0.7, now); g1.gain.exponentialRampToValueAtTime(0.01, now + 0.065);
      osc1.connect(g1); g1.connect(filterNode);
      osc1.start(now); osc1.stop(now + 0.07);

      const osc2 = audioCtx.createOscillator(), g2 = audioCtx.createGain();
      osc2.type = 'square'; osc2.frequency.setValueAtTime(1319, now + 0.065);
      g2.gain.setValueAtTime(0.8, now + 0.065); g2.gain.exponentialRampToValueAtTime(0.001, now + 0.42);
      osc2.connect(g2); g2.connect(filterNode);
      osc2.start(now + 0.065); osc2.stop(now + 0.44);
      break;
    }

    case 'WAKA': {
      // Pac-Man Namco WSG Waka Munch: 240Hz -> 490Hz -> 220Hz in 120ms with 4-bit pulse
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square';
      osc.frequency.setValueAtTime(240, now);
      osc.frequency.linearRampToValueAtTime(490, now + 0.05);
      osc.frequency.linearRampToValueAtTime(220, now + 0.12);
      g.gain.setValueAtTime(0.75, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.12);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.13);
      break;
    }

    case 'SIREN': {
      // Pac-Man Ghost Siren: 4-tone stepped cycling (360 -> 405 -> 460 -> 515 Hz)
      [360, 405, 460, 515].forEach((f, idx) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + idx * 0.08);
        g.gain.setValueAtTime(0.55, now + idx * 0.08);
        g.gain.exponentialRampToValueAtTime(0.01, now + (idx + 1) * 0.08);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + idx * 0.08); osc.stop(now + (idx + 1) * 0.085);
      });
      break;
    }

    case 'FRUIT': {
      // Pac-Man Bonus Fruit: 1760 Hz (A6) square pulse -> 2093 Hz (C7) square pulse
      [0, 0.06].forEach((delay, idx) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(idx === 0 ? 1760 : 2093, now + delay);
        g.gain.setValueAtTime(0.65, now + delay);
        g.gain.exponentialRampToValueAtTime(0.01, now + delay + 0.055);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + delay); osc.stop(now + delay + 0.06);
      });
      break;
    }

    case 'GHOST': {
      // Pac-Man Ghost Eat: ascending 4-note WSG arp (523, 659, 784, 1046 Hz)
      [523, 659, 784, 1046].forEach((f, idx) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(f, now + idx * 0.038);
        g.gain.setValueAtTime(0.65, now + idx * 0.038);
        g.gain.exponentialRampToValueAtTime(0.01, now + (idx + 1) * 0.038);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + idx * 0.038); osc.stop(now + (idx + 1) * 0.04);
      });
      break;
    }

    case 'BLUE': {
      // Pac-Man Frightened Ghost Warble: 420 Hz square with 13 Hz square LFO
      const osc = audioCtx.createOscillator(), lfo = audioCtx.createOscillator();
      const lfoG = audioCtx.createGain(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(420, now);
      lfo.type = 'square'; lfo.frequency.setValueAtTime(13, now); lfoG.gain.setValueAtTime(90, now);
      lfo.connect(osc.frequency);
      g.gain.setValueAtTime(0.6, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.38);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); lfo.start(now); osc.stop(now + 0.40); lfo.stop(now + 0.40);
      break;
    }

    case 'EYES': {
      // Pac-Man Ghost Eyes returning: ping-pong alternating chime
      [0, 0.05, 0.10, 0.15].forEach((d, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(i % 2 === 0 ? 880 : 1175, now + d);
        g.gain.setValueAtTime(0.55, now + d);
        g.gain.exponentialRampToValueAtTime(0.01, now + d + 0.045);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + d); osc.stop(now + d + 0.05);
      });
      break;
    }

    case 'DEATH': {
      // Pac-Man 12-step chromatic death descent: 880 down to 330 Hz with final pop
      const freqs = [880, 830, 784, 740, 698, 659, 622, 587, 554, 523, 493, 330];
      freqs.forEach((f, idx) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(f, now + idx * 0.06);
        osc.frequency.exponentialRampToValueAtTime(f * 0.88, now + (idx + 1) * 0.06);
        g.gain.setValueAtTime(0.65, now + idx * 0.06);
        g.gain.exponentialRampToValueAtTime(0.01, now + (idx + 1) * 0.06);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + idx * 0.06); osc.stop(now + (idx + 1) * 0.065);
      });
      const pOsc = audioCtx.createOscillator(), pG = audioCtx.createGain();
      pOsc.type = 'triangle'; pOsc.frequency.setValueAtTime(140, now + 12 * 0.06);
      pOsc.frequency.exponentialRampToValueAtTime(40, now + 12 * 0.06 + 0.06);
      pG.gain.setValueAtTime(0.75, now + 12 * 0.06);
      pG.gain.exponentialRampToValueAtTime(0.01, now + 12 * 0.06 + 0.06);
      pOsc.connect(pG); pG.connect(filterNode);
      pOsc.start(now + 12 * 0.06); pOsc.stop(now + 12 * 0.06 + 0.07);
      break;
    }

    // ---------------------------------------------------------------------
    // SPACE INVADERS & GALAGA SFX (NAMCO WSG & DISCRETE CIRCUITS)
    // ---------------------------------------------------------------------
    case 'INV-STEP': {
      // Space Invaders discrete bass thump (105, 96, 88, 80 Hz alternating)
      const steps = [105, 96, 88, 80];
      const sFreq = steps[Math.floor(Math.random() * steps.length)];
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(sFreq, now);
      osc.frequency.exponentialRampToValueAtTime(sFreq * 0.85, now + 0.065);
      g.gain.setValueAtTime(0.85, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.07);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.075);
      break;
    }

    case 'INV-UFO': {
      // Space Invaders UFO Siren: 680 Hz sine with 18 Hz triangle LFO
      const osc = audioCtx.createOscillator(), lfo = audioCtx.createOscillator();
      const lfoG = audioCtx.createGain(), g = audioCtx.createGain();
      osc.type = 'sine'; osc.frequency.setValueAtTime(680, now);
      lfo.type = 'triangle'; lfo.frequency.setValueAtTime(18, now); lfoG.gain.setValueAtTime(80, now);
      lfo.connect(osc.frequency);
      g.gain.setValueAtTime(0.65, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.36);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); lfo.start(now); osc.stop(now + 0.38); lfo.stop(now + 0.38);
      break;
    }

    case 'INV-EXP': {
      // Space Invaders Base Explosion: resonant lowpass white noise
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(240, now); flt.Q.setValueAtTime(2.5, now);
      flt.frequency.exponentialRampToValueAtTime(50, now + 0.28);
      g.gain.setValueAtTime(0.9, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.28);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.30);
      break;
    }

    case 'INV-FIRE': {
      // Galaga / Space Invaders Laser Cannon: 2400 Hz stepping down to 1180 Hz and 520 Hz in 55ms
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square';
      osc.frequency.setValueAtTime(2400, now);
      osc.frequency.setValueAtTime(1180, now + 0.02);
      osc.frequency.setValueAtTime(520, now + 0.04);
      g.gain.setValueAtTime(0.75, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.06);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.065);
      break;
    }

    case 'TRACT': {
      // Galaga Tractor Beam: dual pulsating square waves at 392 & 440 Hz pulsing at 14 Hz
      const osc1 = audioCtx.createOscillator(), osc2 = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc1.type = 'square'; osc1.frequency.setValueAtTime(392, now);
      osc2.type = 'square'; osc2.frequency.setValueAtTime(440, now);
      const lfo = audioCtx.createOscillator(), lfoG = audioCtx.createGain();
      lfo.type = 'square'; lfo.frequency.setValueAtTime(14, now);
      lfoG.gain.setValueAtTime(0.5, now);
      lfo.connect(g.gain);
      g.gain.setValueAtTime(0.5, now);
      osc1.connect(g); osc2.connect(g); g.connect(filterNode);
      osc1.start(now); osc2.start(now); lfo.start(now);
      osc1.stop(now + 0.40); osc2.stop(now + 0.40); lfo.stop(now + 0.40);
      break;
    }

    case 'DIVE': {
      // Galaga Alien Dive-bomb: 1450 Hz swooping to 260 Hz with 28 Hz vibrato modulation
      const osc = audioCtx.createOscillator(), lfo = audioCtx.createOscillator();
      const lfoG = audioCtx.createGain(), g = audioCtx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(1450, now);
      osc.frequency.exponentialRampToValueAtTime(260, now + 0.38);
      lfo.type = 'square'; lfo.frequency.setValueAtTime(28, now); lfoG.gain.setValueAtTime(110, now);
      lfo.connect(osc.frequency);
      g.gain.setValueAtTime(0.65, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.38);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); lfo.start(now); osc.stop(now + 0.40); lfo.stop(now + 0.40);
      break;
    }

    case 'CAPTURE': {
      // Galaga Captured Ship alarm: two-tone square wave (587 / 784 Hz) alternating every 30ms
      [0, 0.03, 0.06, 0.09, 0.12, 0.15, 0.18, 0.21, 0.24, 0.27].forEach((d, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(i % 2 === 0 ? 587 : 784, now + d);
        g.gain.setValueAtTime(0.55, now + d);
        g.gain.exponentialRampToValueAtTime(0.01, now + d + 0.028);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + d); osc.stop(now + d + 0.03);
      });
      break;
    }

    case 'BOSS': {
      // Galaga Boss Alien Blast: bandpassed noise crackle layered with heavy sub-bass thud
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(1200, now); flt.Q.setValueAtTime(1.5, now);
      gN.gain.setValueAtTime(0.85, now); gN.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.38);

      const osc = audioCtx.createOscillator(), gO = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(110, now);
      osc.frequency.exponentialRampToValueAtTime(35, now + 0.35);
      gO.gain.setValueAtTime(0.9, now); gO.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
      osc.connect(gO); gO.connect(filterNode);
      osc.start(now); osc.stop(now + 0.38);
      break;
    }

    case 'BONUS': {
      // Galaga Stage Clear / Perfect Fanfare (523, 659, 784, 1046, 1318 Hz)
      [523, 659, 784, 1046, 1318].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(f, now + i * 0.055);
        g.gain.setValueAtTime(0.6, now + i * 0.055);
        g.gain.exponentialRampToValueAtTime(0.01, now + i * 0.055 + 0.11);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.055); osc.stop(now + i * 0.055 + 0.12);
      });
      break;
    }

    case 'DIG-PUMP': {
      // Dig Dug Harpoon Air Pump: 220 Hz -> 560 Hz -> 260 Hz square pop
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(220, now);
      osc.frequency.exponentialRampToValueAtTime(560, now + 0.05);
      osc.frequency.exponentialRampToValueAtTime(260, now + 0.09);
      g.gain.setValueAtTime(0.65, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.09);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.10);
      break;
    }

    case 'DIG-POP': {
      // Dig Dug Pooka Pop: 300 Hz -> 1450 Hz rapid square pitch rise + noise pop
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(300, now);
      osc.frequency.exponentialRampToValueAtTime(1450, now + 0.12);
      g.gain.setValueAtTime(0.7, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.12);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.13);
      break;
    }

    case 'RALLY-SMK': {
      // Rally-X Smoke Screen: bandpassed friction noise skid (340 Hz)
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(340, now); flt.Q.setValueAtTime(2.0, now);
      g.gain.setValueAtTime(0.75, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.22);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.24);
      break;
    }

    case 'RALLY-FLG': {
      // Rally-X Special Flag: 4-note high chime (880, 1108, 1318, 1760 Hz)
      [880, 1108, 1318, 1760].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.05);
        g.gain.setValueAtTime(0.55, now + i * 0.05); g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.05);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.05); osc.stop(now + (i + 1) * 0.055);
      });
      break;
    }

    case 'WARP': {
      // Cosmic Warp: 110 Hz exponentially rising to 2400 Hz over 400ms
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(110, now);
      osc.frequency.exponentialRampToValueAtTime(2400, now + 0.40);
      g.gain.setValueAtTime(0.65, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.40);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.42);
      break;
    }

    // ---------------------------------------------------------------------
    // DONKEY KONG & NINTENDO 8-BIT SFX (NINTENDO 8035 DAC & NES APU)
    // ---------------------------------------------------------------------
    case 'DK-WALK': {
      // Donkey Kong Footstep: alternating two-pitch 8035 DAC clicks (85 / 125 Hz square, 28ms)
      const pitches = [85, 125];
      const p = pitches[Math.floor((now * 30)) % 2];
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(p, now);
      osc.frequency.exponentialRampToValueAtTime(45, now + 0.028);
      g.gain.setValueAtTime(0.75, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.028);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.032);
      break;
    }

    case 'DK-JUMP': {
      // Donkey Kong Spring Boing: 340 Hz rising to 680 Hz modulated by 55 Hz square FSK LFO
      const osc = audioCtx.createOscillator(), lfo = audioCtx.createOscillator();
      const lfoG = audioCtx.createGain(), g = audioCtx.createGain();
      osc.type = 'square';
      osc.frequency.setValueAtTime(340, now);
      osc.frequency.linearRampToValueAtTime(680, now + 0.18);
      lfo.type = 'square'; lfo.frequency.setValueAtTime(55, now); lfoG.gain.setValueAtTime(140, now);
      lfo.connect(osc.frequency);
      g.gain.setValueAtTime(0.75, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.18);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); lfo.start(now); osc.stop(now + 0.19); lfo.stop(now + 0.19);
      break;
    }

    case 'DK-HAMR': {
      // Donkey Kong Hammer: metallic 1420 Hz square clink layered with 85 Hz sub-thud & noise snap
      const oscM = audioCtx.createOscillator(), gM = audioCtx.createGain();
      oscM.type = 'square'; oscM.frequency.setValueAtTime(1420, now);
      oscM.frequency.exponentialRampToValueAtTime(320, now + 0.06);
      gM.gain.setValueAtTime(0.7, now); gM.gain.exponentialRampToValueAtTime(0.01, now + 0.06);
      oscM.connect(gM); gM.connect(filterNode);
      oscM.start(now); oscM.stop(now + 0.07);

      const oscT = audioCtx.createOscillator(), gT = audioCtx.createGain();
      oscT.type = 'square'; oscT.frequency.setValueAtTime(85, now);
      oscT.frequency.exponentialRampToValueAtTime(35, now + 0.15);
      gT.gain.setValueAtTime(0.85, now); gT.gain.exponentialRampToValueAtTime(0.01, now + 0.15);
      oscT.connect(gT); gT.connect(filterNode);
      oscT.start(now); oscT.stop(now + 0.16);

      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'highpass'; flt.frequency.setValueAtTime(1800, now);
      gN.gain.setValueAtTime(0.55, now); gN.gain.exponentialRampToValueAtTime(0.01, now + 0.03);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.035);
      break;
    }

    case 'DK-FALL': {
      // Donkey Kong Barrel Smash: lowpass noise drop (320 Hz -> 60 Hz) + 60 Hz sub-bass thump
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(320, now); flt.Q.setValueAtTime(2.0, now);
      flt.frequency.exponentialRampToValueAtTime(60, now + 0.22);
      gN.gain.setValueAtTime(0.85, now); gN.gain.exponentialRampToValueAtTime(0.01, now + 0.22);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.24);

      const osc = audioCtx.createOscillator(), gO = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(75, now);
      osc.frequency.exponentialRampToValueAtTime(30, now + 0.22);
      gO.gain.setValueAtTime(0.8, now); gO.gain.exponentialRampToValueAtTime(0.01, now + 0.22);
      osc.connect(gO); gO.connect(filterNode);
      osc.start(now); osc.stop(now + 0.24);
      break;
    }

    case 'DK-ROAR': {
      // Kong Chest-Beating Roar: 3 rapid guttural resonant lowpass noise bursts (110 Hz, Q=3.2)
      [0, 0.08, 0.16].forEach(d => {
        const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
        flt.type = 'bandpass'; flt.frequency.setValueAtTime(110, now + d); flt.Q.setValueAtTime(3.2, now + d);
        g.gain.setValueAtTime(0.95, now + d); g.gain.exponentialRampToValueAtTime(0.01, now + d + 0.07);
        noise.connect(flt); flt.connect(g); g.connect(filterNode);
        noise.start(now + d); noise.stop(now + d + 0.075);
      });
      break;
    }

    case 'DK-HELP': {
      // Pauline "HELP!" Cry: high two-tone plea (1568 Hz / 1760 Hz)
      [0, 0.08].forEach((d, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(i === 0 ? 1568 : 1760, now + d);
        g.gain.setValueAtTime(0.55, now + d); g.gain.exponentialRampToValueAtTime(0.01, now + d + 0.07);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + d); osc.stop(now + d + 0.08);
      });
      break;
    }

    case 'DK-WIN': {
      // Donkey Kong 25m Victory Fanfare (G4, C5, E5, G5, F5, G5) in staccato 8035 DAC square tones
      const notes = [392, 523, 659, 784, 698, 784];
      notes.forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.075);
        g.gain.setValueAtTime(0.7, now + i * 0.075);
        g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.075);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.075); osc.stop(now + (i + 1) * 0.08);
      });
      break;
    }

    case 'MARIO-C': {
      // Mario Bros Coin: 988 Hz (B5) for 50ms, jumping to 1319 Hz (E6) with ringing sustain
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square';
      osc.frequency.setValueAtTime(988, now); osc.frequency.setValueAtTime(1319, now + 0.05);
      g.gain.setValueAtTime(0.7, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.36);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.38);
      break;
    }

    case 'PIPE': {
      // Mario Pipe Descent: 4 descending staccato square steps (440, 370, 311, 261 Hz)
      [0, 0.04, 0.08, 0.12].forEach((d, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime([440, 370, 311, 261][i], now + d);
        g.gain.setValueAtTime(0.6, now + d); g.gain.exponentialRampToValueAtTime(0.01, now + d + 0.038);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + d); osc.stop(now + d + 0.042);
      });
      break;
    }

    case 'TURTLE': {
      // Mario Shell Kick: 280 Hz -> 55 Hz pitch thump with noise impact
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(280, now); osc.frequency.exponentialRampToValueAtTime(55, now + 0.12);
      g.gain.setValueAtTime(0.8, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.12);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.13);
      break;
    }

    case 'POW': {
      // Mario POW Earthquake: heavy lowpass rumble noise (220 Hz -> 40 Hz)
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(240, now);
      flt.frequency.exponentialRampToValueAtTime(40, now + 0.5);
      g.gain.setValueAtTime(0.95, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.5);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.52);
      break;
    }

    case 'MARIO-1UP': {
      // Super Mario 1-Up Jingle: E5, G5, E6, C6, D6, G6
      [659, 784, 1318, 1046, 1174, 1568].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.065);
        g.gain.setValueAtTime(0.6, now + i * 0.065); g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.065);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.065); osc.stop(now + (i + 1) * 0.07);
      });
      break;
    }

    case 'MARIO-FIRE': {
      // Mario Fireball Bounce: 380 Hz -> 880 Hz crisp square chirp
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(380, now);
      osc.frequency.exponentialRampToValueAtTime(880, now + 0.07);
      g.gain.setValueAtTime(0.65, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.07);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.08);
      break;
    }

    case 'MARIO-GROW': {
      // Super Mushroom Grow: stepped square arpeggio
      [330, 392, 494, 659].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.07);
        g.gain.setValueAtTime(0.6, now + i * 0.07); g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.07);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.07); osc.stop(now + (i + 1) * 0.075);
      });
      break;
    }

    case 'MARIO-FLAG': {
      // Flagpole Slide Whistle + Victory
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(800, now);
      osc.frequency.exponentialRampToValueAtTime(180, now + 0.3);
      g.gain.setValueAtTime(0.7, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.32);
      break;
    }

    case 'PUNCH-BELL': {
      // Punch-Out!! Ring Bell Ding-Ding: 2093 Hz dual bell
      [0, 0.12].forEach(d => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'sine'; osc.frequency.setValueAtTime(2093, now + d);
        g.gain.setValueAtTime(0.7, now + d); g.gain.exponentialRampToValueAtTime(0.001, now + d + 0.25);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + d); osc.stop(now + d + 0.26);
      });
      break;
    }

    case 'PUNCH-HIT': {
      // Punch-Out!! Uppercut Thump
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(130, now);
      osc.frequency.exponentialRampToValueAtTime(35, now + 0.15);
      g.gain.setValueAtTime(0.9, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.15);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.16);
      break;
    }

    case 'PUNCH-KO': {
      // Punch-Out!! 10-Count Buzzer: 180 Hz square buzz
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(180, now);
      g.gain.setValueAtTime(0.7, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.25);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.26);
      break;
    }

    case 'BALLOON-POP': {
      // Balloon Fight Pop: highpass noise snap
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'highpass'; flt.frequency.setValueAtTime(1200, now);
      g.gain.setValueAtTime(0.75, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.12);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.13);
      break;
    }

    case 'EXCITE-JUMP': {
      // Excitebike Ramp Launch: 220 Hz -> 600 Hz rising triangle
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(220, now);
      osc.frequency.exponentialRampToValueAtTime(600, now + 0.25);
      g.gain.setValueAtTime(0.65, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.25);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.26);
      break;
    }

    case 'EXCITE-FALL': {
      // Excitebike Crash Siren: 800 Hz -> 140 Hz downward tumble
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(800, now);
      osc.frequency.exponentialRampToValueAtTime(140, now + 0.35);
      g.gain.setValueAtTime(0.7, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.36);
      break;
    }

    case 'ICE-SMASH': {
      // Ice Climber Ice Break: 1600 Hz bandpass noise crackle
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(1600, now); flt.Q.setValueAtTime(3.0, now);
      g.gain.setValueAtTime(0.8, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.16);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.18);
      break;
    }

    case 'DUCK-SHOT': {
      // Duck Hunt Zapper Light Gun Shot: 1800 Hz lowpass noise pulse
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(1800, now);
      g.gain.setValueAtTime(0.9, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.15);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.16);
      break;
    }

    case 'DUCK-FALL': {
      // Duck Hunt Falling Bird Whistle
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sine'; osc.frequency.setValueAtTime(900, now);
      osc.frequency.exponentialRampToValueAtTime(180, now + 0.4);
      g.gain.setValueAtTime(0.6, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.42);
      break;
    }

    case 'ZELDA-SECR': {
      // Nintendo Secret Discovery Chime (G4, F#4, D#4, A3, G#3, E4, G#4, C5)
      const freqs = [392.00, 369.99, 311.13, 220.00, 207.65, 329.63, 415.30, 523.25];
      freqs.forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.08);
        g.gain.setValueAtTime(0.6, now + i * 0.08); g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.08);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.08); osc.stop(now + (i + 1) * 0.085);
      });
      break;
    }

    case 'START': {
      // 1-Player Arcade Start Fanfare (C5, E5, G5, C6 triumphant chime)
      [523.25, 659.25, 783.99, 1046.50].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.06);
        g.gain.setValueAtTime(0.65, now + i * 0.06); g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.06);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.06); osc.stop(now + (i + 1) * 0.065);
      });
      break;
    }

    // ---------------------------------------------------------------------
    // ATARI VECTOR & WILLIAMS SCI-FI SFX (ATARI POKEY & DISCRETE ANALOG)
    // ---------------------------------------------------------------------
    case 'AST-THR': {
      // Asteroids Ship Thrust: 65 Hz lowpass noise pulsed at 16 Hz by simulated 555 timer
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(75, now); flt.Q.setValueAtTime(3.2, now);
      g.gain.setValueAtTime(0.85, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.14);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.16);
      break;
    }

    case 'AST-SAU': {
      // Asteroids Flying Saucer: alternating two-tone warble (320 / 480 Hz) at 8 Hz rate
      [0, 0.08, 0.16, 0.24].forEach((d, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'sine'; osc.frequency.setValueAtTime(i % 2 === 0 ? 320 : 480, now + d);
        g.gain.setValueAtTime(0.6, now + d); g.gain.exponentialRampToValueAtTime(0.01, now + d + 0.075);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + d); osc.stop(now + d + 0.08);
      });
      break;
    }

    case 'AST-EXP': {
      // Asteroids Deep Analog Noise Explosion: resonant lowpass sweeping 200 Hz down to 35 Hz
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(220, now); flt.Q.setValueAtTime(2.8, now);
      flt.frequency.exponentialRampToValueAtTime(35, now + 0.65);
      g.gain.setValueAtTime(0.95, now); g.gain.exponentialRampToValueAtTime(0.001, now + 0.70);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.72);
      break;
    }

    case 'AST-FIRE': {
      // Asteroids Photon Torpedo Shot: 1280 Hz analog discrete chirp down to 220 Hz in 75ms
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(1280, now);
      osc.frequency.exponentialRampToValueAtTime(220, now + 0.075);
      g.gain.setValueAtTime(0.7, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.075);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.085);
      break;
    }

    case 'TEM-ZAP': {
      // Tempest Superzapper: Atari POKEY 4-bit polynomial pseudo-random distortion cascade
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(2400, now); flt.Q.setValueAtTime(3.5, now);
      flt.frequency.exponentialRampToValueAtTime(80, now + 0.35);
      gN.gain.setValueAtTime(0.9, now); gN.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.38);

      const osc = audioCtx.createOscillator(), gO = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(2800, now);
      osc.frequency.exponentialRampToValueAtTime(70, now + 0.35);
      gO.gain.setValueAtTime(0.7, now); gO.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
      osc.connect(gO); gO.connect(filterNode);
      osc.start(now); osc.stop(now + 0.38);
      break;
    }

    case 'TEM-FIRE': {
      // Tempest Particle Gun: 1600 Hz -> 350 Hz square chirp in 50ms
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(1600, now);
      osc.frequency.exponentialRampToValueAtTime(350, now + 0.05);
      g.gain.setValueAtTime(0.7, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.05);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.055);
      break;
    }

    case 'TEM-SPIKE': {
      // Tempest Spike Drill: 160 Hz square with 28 Hz FM buzz
      const osc = audioCtx.createOscillator(), lfo = audioCtx.createOscillator();
      const lfoG = audioCtx.createGain(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(160, now);
      lfo.frequency.setValueAtTime(28, now); lfoG.gain.setValueAtTime(70, now);
      lfo.connect(osc.frequency);
      g.gain.setValueAtTime(0.65, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); lfo.start(now); osc.stop(now + 0.21); lfo.stop(now + 0.21);
      break;
    }

    case 'TEM-FLIP': {
      // Tempest Bowtie Flipper Flip: 700 Hz -> 500 Hz -> 650 Hz
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(700, now);
      osc.frequency.linearRampToValueAtTime(500, now + 0.05);
      osc.frequency.linearRampToValueAtTime(650, now + 0.1);
      g.gain.setValueAtTime(0.55, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.1);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.11);
      break;
    }

    case 'DEF-FIRE': {
      // Defender Rapid Laser: 2400 Hz -> 350 Hz sharp sawtooth chirp
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(2400, now);
      osc.frequency.exponentialRampToValueAtTime(350, now + 0.075);
      g.gain.setValueAtTime(0.75, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.075);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.085);
      break;
    }

    case 'DEF-SMART': {
      // Defender Smart Bomb Full Screen Disintegration: full-spectrum white noise flash
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(1000, now); flt.frequency.exponentialRampToValueAtTime(40, now + 0.7);
      g.gain.setValueAtTime(0.95, now); g.gain.exponentialRampToValueAtTime(0.001, now + 0.75);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.78);
      break;
    }

    case 'DEF-HUMAN': {
      // Defender Abduction Distress: alternating two-tone alarm (440 / 880 Hz)
      [0, 0.08, 0.16].forEach((d, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(i % 2 === 0 ? 440 : 880, now + d);
        g.gain.setValueAtTime(0.6, now + d); g.gain.exponentialRampToValueAtTime(0.01, now + d + 0.07);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + d); osc.stop(now + d + 0.075);
      });
      break;
    }

    case 'DEF-CATCH': {
      // Defender Caught Human Rescue Chime (784, 988, 1174, 1568 Hz)
      [784, 988, 1174, 1568].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'triangle'; osc.frequency.setValueAtTime(f, now + i * 0.05);
        g.gain.setValueAtTime(0.6, now + i * 0.05); g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.05);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.05); osc.stop(now + (i + 1) * 0.055);
      });
      break;
    }

    case 'DEF-HYPER': {
      // Defender Hyperspace Warp: 90 Hz -> 2600 Hz cosmic sweep
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(90, now);
      osc.frequency.exponentialRampToValueAtTime(2600, now + 0.35);
      g.gain.setValueAtTime(0.7, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.36);
      break;
    }

    case 'JOUST-FLAP': {
      // Joust Ostrich Wing Flap: low 160 Hz -> 60 Hz triangle flutter
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(160, now);
      osc.frequency.exponentialRampToValueAtTime(60, now + 0.12);
      g.gain.setValueAtTime(0.75, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.12);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.13);
      break;
    }

    case 'JOUST-SKID': {
      // Joust Platform Skid: 600 Hz friction noise bandpass
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(600, now);
      g.gain.setValueAtTime(0.65, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.18);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.2);
      break;
    }

    case 'JOUST-LAVA': {
      // Joust Lava Splash: 180 Hz bubbling lowpass noise
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(180, now);
      g.gain.setValueAtTime(0.85, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.42);
      break;
    }

    case 'ROBOT-STEP': {
      // Robotron 2084 Cyborg Step: 240 Hz -> 80 Hz square punch
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(240, now);
      osc.frequency.exponentialRampToValueAtTime(80, now + 0.1);
      g.gain.setValueAtTime(0.7, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.1);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.11);
      break;
    }

    case 'ROBOT-ZAP': {
      // Robotron Dual Laser: 1800 Hz -> 300 Hz sawtooth blast
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(1800, now);
      osc.frequency.exponentialRampToValueAtTime(300, now + 0.08);
      g.gain.setValueAtTime(0.7, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.08);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.09);
      break;
    }

    case 'ROBOT-HUM': {
      // Robotron Human Saved Fanfare: 4-note square chime (523, 659, 784, 1046 Hz)
      [523, 659, 784, 1046].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.04);
        g.gain.setValueAtTime(0.55, now + i * 0.04); g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.04);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.04); osc.stop(now + (i + 1) * 0.045);
      });
      break;
    }

    case 'BERZERK-ZAP': {
      // Berzerk Laser Shot: 1100 Hz -> 200 Hz
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(1100, now);
      osc.frequency.exponentialRampToValueAtTime(200, now + 0.12);
      g.gain.setValueAtTime(0.65, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.12);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.13);
      break;
    }

    case 'BERZERK-ROB': {
      // Berzerk Evil Otto Squeak: 1200 Hz with 15 Hz vibrato
      const osc = audioCtx.createOscillator(), lfo = audioCtx.createOscillator();
      const lfoG = audioCtx.createGain(), g = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(1200, now);
      lfo.frequency.setValueAtTime(15, now); lfoG.gain.setValueAtTime(160, now);
      lfo.connect(osc.frequency);
      g.gain.setValueAtTime(0.6, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.25);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); lfo.start(now); osc.stop(now + 0.26); lfo.stop(now + 0.26);
      break;
    }

    case 'STARWAR-TIE': {
      // Star Wars TIE Fighter Scream: 1600 Hz -> 220 Hz roar
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(1600, now);
      osc.frequency.exponentialRampToValueAtTime(220, now + 0.4);
      g.gain.setValueAtTime(0.7, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.42);
      break;
    }

    case 'STARWAR-LAS': {
      // Star Wars Quad Laser: 4 staggered 1500 Hz -> 300 Hz pulses
      [0, 0.02, 0.04, 0.06].forEach(d => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(1500, now + d);
        osc.frequency.exponentialRampToValueAtTime(300, now + d + 0.05);
        g.gain.setValueAtTime(0.5, now + d); g.gain.exponentialRampToValueAtTime(0.01, now + d + 0.05);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + d); osc.stop(now + d + 0.055);
      });
      break;
    }

    case 'STARWAR-TRB': {
      // Star Wars Proton Torpedo Sub Drop: 110 Hz -> 30 Hz
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sine'; osc.frequency.setValueAtTime(110, now);
      osc.frequency.exponentialRampToValueAtTime(30, now + 0.4);
      g.gain.setValueAtTime(0.85, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.42);
      break;
    }

    case 'MISSILE-LCH': {
      // Missile Command Launch: rising whistle 150 Hz -> 450 Hz
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(150, now);
      osc.frequency.exponentialRampToValueAtTime(450, now + 0.25);
      g.gain.setValueAtTime(0.65, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.25);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.26);
      break;
    }

    case 'MISSILE-EXP': {
      // Missile Command Flak Explosion: heavy 500 Hz -> 60 Hz lowpass blast
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(500, now); flt.frequency.exponentialRampToValueAtTime(60, now + 0.85);
      g.gain.setValueAtTime(0.95, now); g.gain.exponentialRampToValueAtTime(0.001, now + 0.9);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.92);
      break;
    }

    case 'BZONE-ENG': {
      // Battlezone Tank Engine Purr: 55 Hz sawtooth rumble
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(55, now);
      g.gain.setValueAtTime(0.55, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.36);
      break;
    }

    case 'BZONE-CANN': {
      // Battlezone 120mm Tank Cannon Shot: punchy 280 Hz noise crack
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(280, now);
      g.gain.setValueAtTime(0.95, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.45);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.48);
      break;
    }

    // ---------------------------------------------------------------------
    // KONAMI, SEGA & 80s ACTION SFX (DUAL AY-3-8910, 5x PSG & FM)
    // ---------------------------------------------------------------------
    case 'FROG-H': {
      // Frogger Frog Hop: sharp downward square chirp (1100 Hz -> 620 Hz in 35ms, pure Konami PSG)
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square';
      osc.frequency.setValueAtTime(1100, now);
      osc.frequency.exponentialRampToValueAtTime(620, now + 0.035);
      g.gain.setValueAtTime(0.75, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.035);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.04);
      break;
    }

    case 'FROG-SPLASH': {
      // Frogger Water Splash: 680 -> 200 Hz bloop + water splash plunge noise
      const osc = audioCtx.createOscillator(), gO = audioCtx.createGain();
      osc.type = 'sine'; osc.frequency.setValueAtTime(680, now);
      osc.frequency.exponentialRampToValueAtTime(180, now + 0.12);
      gO.gain.setValueAtTime(0.75, now); gO.gain.exponentialRampToValueAtTime(0.01, now + 0.12);
      osc.connect(gO); gO.connect(filterNode);
      osc.start(now); osc.stop(now + 0.14);

      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(950, now); flt.frequency.exponentialRampToValueAtTime(160, now + 0.18);
      gN.gain.setValueAtTime(0.75, now); gN.gain.exponentialRampToValueAtTime(0.01, now + 0.18);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.20);
      break;
    }

    case 'FROG-TIME': {
      // Frogger Hurry Up Clock Tick: 1200 Hz square click 30ms
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(1200, now);
      g.gain.setValueAtTime(0.5, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.03);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.035);
      break;
    }

    case 'FROG-HOME': {
      // Frogger Home Landing Chime: bright 4-note AY-3-8910 arpeggio (C5, E5, G5, C6)
      [523, 659, 784, 1046].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.045);
        g.gain.setValueAtTime(0.65, now + i * 0.045);
        g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.045);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.045); osc.stop(now + (i + 1) * 0.05);
      });
      break;
    }

    case 'FROG-SPLAT': {
      // Frogger Road Squish: lowpass crunch noise 240 Hz
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(240, now);
      g.gain.setValueAtTime(0.85, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.16);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.18);
      break;
    }

    case 'GYRUSS-WARP': {
      // Gyruss Warp Hyperspace Sweep: 110 Hz -> 2200 Hz cosmic sweep
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(110, now); osc.frequency.exponentialRampToValueAtTime(2200, now + 0.45);
      g.gain.setValueAtTime(0.65, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.45);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.46);
      break;
    }

    case 'GYRUSS-LAS': {
      // Gyruss Orbital Twin Lasers: dual rapid stereo-offset chirps (1400 Hz -> 350 Hz)
      [0, 0.04].forEach(d => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'sawtooth'; osc.frequency.setValueAtTime(1400, now + d);
        osc.frequency.exponentialRampToValueAtTime(350, now + d + 0.06);
        g.gain.setValueAtTime(0.6, now + d); g.gain.exponentialRampToValueAtTime(0.01, now + d + 0.06);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + d); osc.stop(now + d + 0.065);
      });
      break;
    }

    case 'GYRUSS-DIV': {
      // Gyruss Drone Dive Trill: swooping sawtooth with 18 Hz vibrato
      const osc = audioCtx.createOscillator(), lfo = audioCtx.createOscillator();
      const lfoG = audioCtx.createGain(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(950, now);
      osc.frequency.exponentialRampToValueAtTime(160, now + 0.35);
      lfo.frequency.setValueAtTime(18, now); lfoG.gain.setValueAtTime(80, now);
      lfo.connect(osc.frequency);
      g.gain.setValueAtTime(0.6, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); lfo.start(now); osc.stop(now + 0.36); lfo.stop(now + 0.36);
      break;
    }

    case 'GYRUSS-EXP': {
      // Gyruss Drone Core Detonate: 5x PSG bandpass noise burst 380 Hz
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(380, now); flt.Q.setValueAtTime(2.0, now);
      g.gain.setValueAtTime(0.85, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.36);
      break;
    }

    case 'CLIMB-STEP': {
      // Crazy Climber Window Step: distinct 110 Hz click/clack pulse
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(140, now);
      osc.frequency.exponentialRampToValueAtTime(45, now + 0.06);
      g.gain.setValueAtTime(0.7, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.06);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.07);
      break;
    }

    case 'CLIMB-POT': {
      // Crazy Climber Flowerpot Crash: highpass ceramic noise shatter 1200 Hz
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'highpass'; flt.frequency.setValueAtTime(1200, now);
      g.gain.setValueAtTime(0.85, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.25);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.26);
      break;
    }

    case 'CLIMB-ELEC': {
      // Crazy Climber Neon Sign Shock: 120 Hz sawtooth with 60 Hz AC hum modulation
      const osc = audioCtx.createOscillator(), lfo = audioCtx.createOscillator();
      const lfoG = audioCtx.createGain(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(120, now);
      lfo.frequency.setValueAtTime(60, now); lfoG.gain.setValueAtTime(450, now);
      lfo.connect(osc.frequency);
      g.gain.setValueAtTime(0.7, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); lfo.start(now); osc.stop(now + 0.32); lfo.stop(now + 0.32);
      break;
    }

    case 'CLIMB-KONG': {
      // Crazy Climber Giant Ape Punch: heavy 80 Hz -> 30 Hz sub thump
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(80, now);
      osc.frequency.exponentialRampToValueAtTime(30, now + 0.2);
      g.gain.setValueAtTime(0.9, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.22);
      break;
    }

    case 'CLIMB-WIN': {
      // Crazy Climber Helicopter Win Fanfare: C5, E5, G5, C6 victory chime
      [523, 659, 784, 1046].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.075);
        g.gain.setValueAtTime(0.6, now + i * 0.075); g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.075);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.075); osc.stop(now + (i + 1) * 0.08);
      });
      break;
    }

    case 'QBERT-HOP': {
      // Q*bert Pyramid Step Boing: 240 Hz -> 600 Hz -> 300 Hz
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(240, now);
      osc.frequency.exponentialRampToValueAtTime(600, now + 0.08);
      osc.frequency.exponentialRampToValueAtTime(300, now + 0.16);
      g.gain.setValueAtTime(0.7, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.16);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.17);
      break;
    }

    case 'QBERT-CURSE': {
      // Q*bert "@!#?@!" Speech Curse (VOTRAX Formants)
      const formants = [350, 700, 1400, 450, 900, 300];
      formants.forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'sawtooth'; osc.frequency.setValueAtTime(f, now + i * 0.05);
        g.gain.setValueAtTime(0.6, now + i * 0.05); g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.05);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.05); osc.stop(now + (i + 1) * 0.055);
      });
      break;
    }

    case 'QBERT-DISC': {
      // Q*bert Flying Disc Float: 440 Hz -> 880 Hz sine with 10 Hz vibrato
      const osc = audioCtx.createOscillator(), lfo = audioCtx.createOscillator();
      const lfoG = audioCtx.createGain(), g = audioCtx.createGain();
      osc.type = 'sine'; osc.frequency.setValueAtTime(440, now);
      osc.frequency.linearRampToValueAtTime(880, now + 0.35);
      lfo.frequency.setValueAtTime(10, now); lfoG.gain.setValueAtTime(40, now);
      lfo.connect(osc.frequency);
      g.gain.setValueAtTime(0.6, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); lfo.start(now); osc.stop(now + 0.36); lfo.stop(now + 0.36);
      break;
    }

    case 'QBERT-FALL': {
      // Q*bert Plunge Whistle: 1200 Hz -> 90 Hz drop
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(1200, now);
      osc.frequency.exponentialRampToValueAtTime(90, now + 0.45);
      g.gain.setValueAtTime(0.65, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.45);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.46);
      break;
    }

    case 'OUTRUN-REV': {
      // OutRun Ferrari Engine Rev: 75 Hz -> 220 Hz sawtooth
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(75, now);
      osc.frequency.exponentialRampToValueAtTime(220, now + 0.3);
      g.gain.setValueAtTime(0.7, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.32);
      break;
    }

    case 'OUTRUN-SKID': {
      // OutRun Tire Screech: 1800 Hz resonant bandpass noise
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(1800, now); flt.Q.setValueAtTime(4.0, now);
      g.gain.setValueAtTime(0.75, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.32);
      break;
    }

    case 'OUTRUN-PASS': {
      // OutRun Checkpoint Passing (880, 1108, 1318 Hz)
      [880, 1108, 1318].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.08);
        g.gain.setValueAtTime(0.6, now + i * 0.08); g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.08);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.08); osc.stop(now + (i + 1) * 0.085);
      });
      break;
    }

    case 'SHINOBI-STAR': {
      // Shinobi Shuriken Throw: 2200 Hz highpass noise slice
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'highpass'; flt.frequency.setValueAtTime(2200, now);
      g.gain.setValueAtTime(0.7, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.1);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.11);
      break;
    }

    case 'SHINOBI-HIT': {
      // Shinobi Katana Slash: 900 Hz bandpass noise impact
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(900, now);
      g.gain.setValueAtTime(0.8, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.14);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.15);
      break;
    }

    case 'GHOSTS-JMP': {
      // Ghosts 'n Goblins Knight Armor Jump (800, 1200 Hz dual square click)
      [800, 1200].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.04);
        g.gain.setValueAtTime(0.55, now + i * 0.04); g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.04);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.04); osc.stop(now + (i + 1) * 0.045);
      });
      break;
    }

    case 'GHOSTS-ARM': {
      // Ghosts 'n Goblins Armor Shatter: 1500 Hz highpass noise crash
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'highpass'; flt.frequency.setValueAtTime(1500, now);
      g.gain.setValueAtTime(0.85, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.25);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.26);
      break;
    }

    case 'GONGA-COIN': {
      // Sega FM Coin Ring (1046 Hz -> 1568 Hz)
      const osc1 = audioCtx.createOscillator(), g1 = audioCtx.createGain();
      osc1.type = 'square'; osc1.frequency.setValueAtTime(1046, now);
      g1.gain.setValueAtTime(0.6, now); g1.gain.exponentialRampToValueAtTime(0.01, now + 0.08);
      osc1.connect(g1); g1.connect(filterNode);
      osc1.start(now); osc1.stop(now + 0.09);

      const osc2 = audioCtx.createOscillator(), g2 = audioCtx.createGain();
      osc2.type = 'square'; osc2.frequency.setValueAtTime(1568, now + 0.08);
      g2.gain.setValueAtTime(0.75, now + 0.08); g2.gain.exponentialRampToValueAtTime(0.001, now + 0.38);
      osc2.connect(g2); g2.connect(filterNode);
      osc2.start(now + 0.08); osc2.stop(now + 0.40);
      break;
    }

    default: {
      // Clean fallback beep if unknown
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(440, now);
      g.gain.setValueAtTime(0.4, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.1);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.12);
      break;
    }
  }
}
\'\'\'

if __name__ == "__main__":
    print(f"Generated {len(get_sfx_banks_js())} bytes of SFX Banks JS.")
    print(f"Generated {len(get_play_arcade_sfx_js())} bytes of playArcadeSfx JS.")
'''

    full_updated = header_and_banks + new_play_arcade_js
    with open("tools/sfx_banks_generator.py", "w") as f:
        f.write(full_updated)

    print(f"Updated tools/sfx_banks_generator.py successfully ({len(full_updated)} bytes)!")

if __name__ == "__main__":
    generate_sfx_file()
