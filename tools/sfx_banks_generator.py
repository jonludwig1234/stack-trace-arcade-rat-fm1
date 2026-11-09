#!/usr/bin/env python3
"""
Generate the multi-bank iconic arcade SFX engine for M-VAVE FM-1.
Contains 4 Master Sound Banks (108 total curated sounds across 1978-1987)
with authentic Web Audio chiptune synthesis algorithms.
"""

def get_sfx_banks_js():
    return '''
// =========================================================================
// 4 MASTER ICONIC ARCADE SFX BANKS (108 CURATED ARCADE SOUNDS)
// =========================================================================
const SFX_BANKS = [
  {
    id: 'bank_golden',
    name: 'BANK 1: GOLDEN AGE ARCADE (1978–1982)',
    shortName: 'BANK 1: GOLDEN AGE',
    subtitle: 'Namco, Midway & Atari (1978–1982) · Pac-Man, Space Invaders, Galaga, Asteroids · WSG Wavetable & POKEY',
    icon: '🟡',
    color: '#f5a623',
    sounds: [
      { id: 'WAKA', name: 'Waka Chomp', chip: 'WSG 3-V', game: 'Pac-Man', icon: '🟡', color: '#f5a623' },
      { id: 'SIREN', name: 'Ghost Siren', chip: 'WSG 3-V', game: 'Pac-Man', icon: '🚨', color: '#ff4757' },
      { id: 'FRUIT', name: 'Bonus Fruit', chip: 'WSG 3-V', game: 'Pac-Man', icon: '🍒', color: '#ff6b81' },
      { id: 'GHOST', name: 'Ghost Eat', chip: 'WSG 3-V', game: 'Pac-Man', icon: '👻', color: '#70a1ff' },
      { id: 'BLUE', name: 'Blue Warble', chip: 'WSG 3-V', game: 'Pac-Man', icon: '🔵', color: '#1e90ff' },
      { id: 'EYES', name: 'Ghost Eyes', chip: 'WSG 3-V', game: 'Pac-Man', icon: '👀', color: '#ffffff' },
      { id: 'DEATH', name: 'Pac Death', chip: 'WSG 3-V', game: 'Pac-Man', icon: '💀', color: '#ff6348' },
      { id: 'INV-STEP', name: 'Alien March', chip: 'Discrete', game: 'Space Inv', icon: '👾', color: '#2ed573' },
      { id: 'INV-UFO', name: 'UFO Siren', chip: 'Discrete', game: 'Space Inv', icon: '🛸', color: '#ff4757' },
      { id: 'INV-EXP', name: 'Base Explode', chip: 'Noise Fltr', game: 'Space Inv', icon: '💥', color: '#ffa502' },
      { id: 'INV-FIRE', name: 'Laser Cannon', chip: 'Pulse Gen', game: 'Space Inv', icon: '⚡', color: '#70a1ff' },
      { id: 'TRACT', name: 'Tractor Beam', chip: 'WSG 3-V', game: 'Galaga', icon: '🌀', color: '#00e5ff' },
      { id: 'DIVE', name: 'Alien Dive', chip: 'WSG 3-V', game: 'Galaga', icon: '🚀', color: '#ff6b81' },
      { id: 'CAPTURE', name: 'Ship Capture', chip: 'WSG 3-V', game: 'Galaga', icon: '🛸', color: '#e056fd' },
      { id: 'BOSS', name: 'Boss Blast', chip: 'Noise BPF', game: 'Galaga', icon: '💥', color: '#ff4757' },
      { id: 'BONUS', name: 'Stage Clear', chip: 'WSG 3-V', game: 'Galaga', icon: '⭐', color: '#feca57' },
      { id: 'AST-THR', name: 'Ship Thrust', chip: 'POKEY PBF', game: 'Asteroids', icon: '🔥', color: '#ff7f50' },
      { id: 'AST-SAU', name: 'Saucer Siren', chip: 'POKEY Sine', game: 'Asteroids', icon: '🛸', color: '#2ed573' },
      { id: 'AST-EXP', name: 'Rock Explode', chip: 'POKEY LPF', game: 'Asteroids', icon: '💥', color: '#ff4757' },
      { id: 'TEM-ZAP', name: 'Superzapper', chip: 'POKEY Sweep', game: 'Tempest', icon: '⚡', color: '#00e5ff' },
      { id: 'TEM-FIRE', name: 'Particle Gun', chip: 'POKEY Pulse', game: 'Tempest', icon: '✨', color: '#a55eea' },
      { id: 'DIG-PUMP', name: 'Harpoon Pump', chip: 'WSG 3-V', game: 'Dig Dug', icon: '🎈', color: '#2ed573' },
      { id: 'DIG-POP', name: 'Pooka Pop', chip: 'Noise Burst', game: 'Dig Dug', icon: '💥', color: '#ff6b81' },
      { id: 'RALLY-SMK', name: 'Smoke Screen', chip: 'WSG Noise', game: 'Rally-X', icon: '💨', color: '#747d8c' },
      { id: 'RALLY-FLG', name: 'Special Flag', chip: 'WSG 3-V', game: 'Rally-X', icon: '🚩', color: '#ff4757' },
      { id: 'WARP', name: 'Cosmic Warp', chip: 'PSG Saw', game: 'Gyruss', icon: '🌌', color: '#3742fa' },
      { id: 'COIN', name: 'Coin Drop', chip: 'WSG/DAC', game: 'Universal', icon: '🪙', color: '#f5cd79' }
    ]
  },
  {
    id: 'bank_nintendo',
    name: 'BANK 2: NINTENDO 8-BIT ARCADE (1981–1985)',
    shortName: 'BANK 2: NINTENDO 8-BIT',
    subtitle: 'Nintendo R&D1 & Miyamoto (1981–1985) · Donkey Kong, Mario Bros, Punch-Out!! · 7-bit DAC & APU',
    icon: '🦍',
    color: '#ff4757',
    sounds: [
      { id: 'DK-WALK', name: 'Mario Step', chip: '7-bit DAC', game: 'Donkey Kong', icon: '👞', color: '#ff6b81' },
      { id: 'DK-JUMP', name: 'Spring Boing', chip: '7-bit DAC', game: 'Donkey Kong', icon: '🦘', color: '#ff4757' },
      { id: 'DK-HAMR', name: 'Mallet Pound', chip: '7-bit DAC', game: 'Donkey Kong', icon: '🔨', color: '#ffa502' },
      { id: 'DK-FALL', name: 'Barrel Smash', chip: '7-bit DAC', game: 'Donkey Kong', icon: '🛢️', color: '#a0522d' },
      { id: 'DK-ROAR', name: 'Kong Roar', chip: 'Noise/DAC', game: 'Donkey Kong', icon: '🦍', color: '#ff6348' },
      { id: 'DK-HELP', name: 'Pauline Cry', chip: '7-bit DAC', game: 'Donkey Kong', icon: '🎀', color: '#ff9ff3' },
      { id: 'DK-WIN', name: 'Level Clear', chip: '7-bit DAC', game: 'Donkey Kong', icon: '🏆', color: '#feca57' },
      { id: 'MARIO-C', name: 'Mario Coin', chip: 'NES APU', game: 'Mario Bros', icon: '🪙', color: '#f5cd79' },
      { id: 'PIPE', name: 'Pipe Warp', chip: 'NES APU', game: 'Mario Bros', icon: '🧪', color: '#2ed573' },
      { id: 'TURTLE', name: 'Shell Kick', chip: 'NES APU', game: 'Mario Bros', icon: '🐢', color: '#26de81' },
      { id: 'POW', name: 'POW Quake', chip: 'Noise LPF', game: 'Mario Bros', icon: '⚡', color: '#45aaf2' },
      { id: 'MARIO-1UP', name: '1-Up Jingle', chip: 'NES APU', game: 'Super Mario', icon: '🍄', color: '#2ed573' },
      { id: 'MARIO-FIRE', name: 'Fireball', chip: 'NES APU', game: 'Super Mario', icon: '🔥', color: '#ff6348' },
      { id: 'MARIO-GROW', name: 'Mushroom Grow', chip: 'NES APU', game: 'Super Mario', icon: '🍄', color: '#ff4757' },
      { id: 'MARIO-FLAG', name: 'Flag Slide', chip: 'NES APU', game: 'Super Mario', icon: '🚩', color: '#feca57' },
      { id: 'PUNCH-BELL', name: 'Ring Bell', chip: 'Dual Bell', game: 'Punch-Out!!', icon: '🔔', color: '#f1c40f' },
      { id: 'PUNCH-HIT', name: 'Jaw Uppercut', chip: 'Noise/Sub', game: 'Punch-Out!!', icon: '🥊', color: '#e74c3c' },
      { id: 'PUNCH-KO', name: 'KO Buzzer', chip: 'Square Buz', game: 'Punch-Out!!', icon: '⏱️', color: '#e67e22' },
      { id: 'BALLOON-POP', name: 'Balloon Pop', chip: 'NES APU', game: 'Balloon Fgt', icon: '🎈', color: '#ff7675' },
      { id: 'EXCITE-JUMP', name: 'Ramp Launch', chip: 'NES APU', game: 'Excitebike', icon: '🏍️', color: '#fdcb6e' },
      { id: 'EXCITE-FALL', name: 'Bike Crash', chip: 'Noise Sweep', game: 'Excitebike', icon: '💥', color: '#d63031' },
      { id: 'ICE-SMASH', name: 'Ice Shatter', chip: 'Noise/DAC', game: 'Ice Climber', icon: '🧊', color: '#74b9ff' },
      { id: 'DUCK-SHOT', name: 'Zapper Shot', chip: 'Audio Pulse', game: 'Duck Hunt', icon: '🎯', color: '#e17055' },
      { id: 'DUCK-FALL', name: 'Bird Drop', chip: 'Pitch Drop', game: 'Duck Hunt', icon: '🦆', color: '#00b894' },
      { id: 'ZELDA-SECR', name: 'Secret Chime', chip: 'NES APU', game: 'Zelda Arcade', icon: '✨', color: '#f1c40f' },
      { id: 'START', name: '1P Arcade Go', chip: 'Chiptune Arp', game: 'Universal', icon: '▶', color: '#00ff66' },
      { id: 'COIN', name: 'Arcade Coin', chip: '7-bit DAC', game: 'Universal', icon: '🪙', color: '#f5cd79' }
    ]
  },
  {
    id: 'bank_vector',
    name: 'BANK 3: ATARI VECTOR & SCI-FI (1979–1984)',
    shortName: 'BANK 3: ATARI VECTOR',
    subtitle: 'Atari, Taito & Williams (1979–1984) · Defender, Asteroids, Tempest, Robotron · POKEY & Quadrascan',
    icon: '☄️',
    color: '#00e5ff',
    sounds: [
      { id: 'DEF-FIRE', name: 'Rapid Laser', chip: 'Williams 6800', game: 'Defender', icon: '⚡', color: '#00e5ff' },
      { id: 'DEF-SMART', name: 'Smart Bomb', chip: 'Noise Flash', game: 'Defender', icon: '💥', color: '#ff4757' },
      { id: 'DEF-HUMAN', name: 'Abduction Alert', chip: 'Williams 6800', game: 'Defender', icon: '🚨', color: '#ffa502' },
      { id: 'DEF-CATCH', name: 'Rescue Chime', chip: 'Williams 6800', game: 'Defender', icon: '🦸', color: '#2ed573' },
      { id: 'DEF-HYPER', name: 'Hyperspace', chip: 'Pitch Sweep', game: 'Defender', icon: '🌌', color: '#a55eea' },
      { id: 'JOUST-FLAP', name: 'Ostrich Flap', chip: 'Low Reson', game: 'Joust', icon: '🪶', color: '#f39c12' },
      { id: 'JOUST-SKID', name: 'Platform Skid', chip: 'Friction Fltr', game: 'Joust', icon: '💨', color: '#d35400' },
      { id: 'JOUST-LAVA', name: 'Lava Splash', chip: 'Noise Sub', game: 'Joust', icon: '🌋', color: '#e74c3c' },
      { id: 'ROBOT-STEP', name: 'Cyborg Clank', chip: 'Square Mod', game: 'Robotron', icon: '🤖', color: '#3498db' },
      { id: 'ROBOT-ZAP', name: 'Dual Laser', chip: 'Williams 6800', game: 'Robotron', icon: '⚡', color: '#00e5ff' },
      { id: 'ROBOT-HUM', name: 'Family Saved', chip: 'Williams 6800', game: 'Robotron', icon: '👨‍👩‍👧', color: '#2ecc71' },
      { id: 'BERZERK-ZAP', name: 'Laser Fire', chip: 'Voice Chip', game: 'Berzerk', icon: '🔫', color: '#e67e22' },
      { id: 'BERZERK-ROB', name: 'Evil Otto', chip: 'Squeak LFO', game: 'Berzerk', icon: '😈', color: '#f1c40f' },
      { id: 'AST-THR', name: 'Thrust Burn', chip: 'POKEY PBF', game: 'Asteroids', icon: '🔥', color: '#e17055' },
      { id: 'AST-FIRE', name: 'Photon Torpedo', chip: 'POKEY Pulse', game: 'Asteroids', icon: '✨', color: '#00d2d3' },
      { id: 'AST-SAU', name: 'Saucer Alert', chip: 'POKEY Sine', game: 'Asteroids', icon: '🛸', color: '#10ac84' },
      { id: 'AST-EXP', name: 'Vector Bang', chip: 'POKEY LPF', game: 'Asteroids', icon: '💥', color: '#ee5253' },
      { id: 'TEM-ZAP', name: 'Electric Zap', chip: 'POKEY Sweep', game: 'Tempest', icon: '⚡', color: '#0abde3' },
      { id: 'TEM-SPIKE', name: 'Spike Drill', chip: 'POKEY Buzz', game: 'Tempest', icon: '🔩', color: '#5f27cd' },
      { id: 'TEM-FLIP', name: 'Flipper Flip', chip: 'POKEY Trill', game: 'Tempest', icon: '🔄', color: '#ff9ff3' },
      { id: 'STARWAR-TIE', name: 'TIE Screamer', chip: 'Quad POKEY', game: 'Star Wars', icon: '🛸', color: '#c8d6e5' },
      { id: 'STARWAR-LAS', name: 'X-Wing Quad', chip: 'Quad POKEY', game: 'Star Wars', icon: '🔴', color: '#ff4757' },
      { id: 'STARWAR-TRB', name: 'Proton Trench', chip: 'Sub Pulse', game: 'Star Wars', icon: '🎯', color: '#feca57' },
      { id: 'MISSILE-LCH', name: 'ICBM Launch', chip: 'POKEY Low', game: 'Missile Cmd', icon: '🚀', color: '#ff7675' },
      { id: 'MISSILE-EXP', name: 'Flak Bloom', chip: 'Noise Decay', game: 'Missile Cmd', icon: '💥', color: '#fdcb6e' },
      { id: 'BZONE-ENG', name: 'Tank Diesel', chip: 'POKEY Sub', game: 'Battlezone', icon: '🛡️', color: '#636e72' },
      { id: 'BZONE-CANN', name: '120mm Blast', chip: 'POKEY Bang', game: 'Battlezone', icon: '💥', color: '#ff6b6b' }
    ]
  },
  {
    id: 'bank_konami_sega',
    name: 'BANK 4: KONAMI, SEGA & 80s ACTION (1981–1987)',
    shortName: 'BANK 4: KONAMI & SEGA',
    subtitle: 'Konami, Nichibutsu, Sega & Gottlieb (1981–1987) · Frogger, Gyruss, Crazy Climber, Q*bert, OutRun · Dual AY-3 & FM',
    icon: '🐸',
    color: '#2ed573',
    sounds: [
      { id: 'FROG-H', name: 'Frog Hop', chip: 'Dual AY-3', game: 'Frogger', icon: '🐸', color: '#2ed573' },
      { id: 'FROG-SPLASH', name: 'River Splash', chip: 'Water Bloop', game: 'Frogger', icon: '💧', color: '#00d2d3' },
      { id: 'FROG-TIME', name: 'Hurry Up!', chip: 'Dual AY-3', game: 'Frogger', icon: '⏰', color: '#ffa502' },
      { id: 'FROG-HOME', name: 'Home Landing', chip: 'Dual AY-3', game: 'Frogger', icon: '🪷', color: '#26de81' },
      { id: 'FROG-SPLAT', name: 'Traffic Squish', chip: 'Noise Thump', game: 'Frogger', icon: '🚗', color: '#ff4757' },
      { id: 'GYRUSS-WARP', name: 'Hyper Warp', chip: '5x PSG', game: 'Gyruss', icon: '🌌', color: '#3742fa' },
      { id: 'GYRUSS-LAS', name: 'Orbital Twin', chip: '5x PSG', game: 'Gyruss', icon: '⚡', color: '#70a1ff' },
      { id: 'GYRUSS-DIV', name: 'Drone Dive', chip: '5x PSG', game: 'Gyruss', icon: '🛸', color: '#ff6b81' },
      { id: 'GYRUSS-EXP', name: 'Core Detonate', chip: '5x PSG Noise', game: 'Gyruss', icon: '💥', color: '#ff4757' },
      { id: 'CLIMB-STEP', name: 'Window Step', chip: 'Dual AY-3', game: 'Crazy Climber', icon: '🧗', color: '#ff9f1c' },
      { id: 'CLIMB-POT', name: 'Flowerpot Smash', chip: 'Noise Crash', game: 'Crazy Climber', icon: '🪴', color: '#e67e22' },
      { id: 'CLIMB-ELEC', name: 'Neon Shock', chip: 'Buzz Saw', game: 'Crazy Climber', icon: '⚡', color: '#f1c40f' },
      { id: 'CLIMB-KONG', name: 'Ape Punch', chip: 'Dual AY-3', game: 'Crazy Climber', icon: '🦍', color: '#d35400' },
      { id: 'CLIMB-WIN', name: 'Chopper Win', chip: 'Dual AY-3', game: 'Crazy Climber', icon: '🚁', color: '#2ecc71' },
      { id: 'QBERT-HOP', name: 'Pyramid Boing', chip: 'Gottlieb DAC', game: 'Q*bert', icon: '🟧', color: '#ff793f' },
      { id: 'QBERT-CURSE', name: '@!#?@! Curse', chip: 'VOTRAX Voice', game: 'Q*bert', icon: '🤬', color: '#cd6133' },
      { id: 'QBERT-DISC', name: 'Flying Disc', chip: 'Gottlieb DAC', game: 'Q*bert', icon: '🛸', color: '#ffb142' },
      { id: 'QBERT-FALL', name: 'Plunge Whistle', chip: 'Pitch Drop', game: 'Q*bert', icon: '💨', color: '#33d9b2' },
      { id: 'OUTRUN-REV', name: 'Ferrari Rev', chip: 'YM2151 FM', game: 'OutRun', icon: '🏎️', color: '#ff5252' },
      { id: 'OUTRUN-SKID', name: 'Tire Screech', chip: 'FM Noise', game: 'OutRun', icon: '🛞', color: '#ff793f' },
      { id: 'OUTRUN-PASS', name: 'Checkpoint!', chip: 'YM2151 FM', game: 'OutRun', icon: '🏁', color: '#34ace0' },
      { id: 'SHINOBI-STAR', name: 'Shuriken', chip: 'YM2151 FM', game: 'Shinobi', icon: '⭐', color: '#706fd3' },
      { id: 'SHINOBI-HIT', name: 'Katana Slash', chip: 'White Noise', game: 'Shinobi', icon: '🗡️', color: '#b33939' },
      { id: 'GHOSTS-JMP', name: 'Armor Clank', chip: 'YM2203 FM', game: 'Ghosts n Gob', icon: '🛡️', color: '#aaa69d' },
      { id: 'GHOSTS-ARM', name: 'Armor Break', chip: 'YM2203 FM', game: 'Ghosts n Gob', icon: '🦴', color: '#d1ccc0' },
      { id: 'GONGA-COIN', name: 'Sega Coin Ring', chip: 'FM Chime', game: 'Sega Arcade', icon: '🪙', color: '#f5cd79' },
      { id: 'BONUS', name: 'Victory Fanfare', chip: 'Dual AY-3', game: 'Universal', icon: '🎉', color: '#ffb142' }
    ]
  }
];

let currentSfxBank = 0;
let sfxNames = SFX_BANKS[0].sounds.map(s => s.id);
let lastSfxName = '';

// Soundboard cycling state variables for authentic multi-step arcade realism
let _pacWakaCycle = 0;
let _invStepCycle = 0;
let _dkStepCycle = 0;
let _dkBgmStep = 0;
let _frogBgmStep = 0;
let _climbBgmStep = 0;
let _galagaBgmStep = 0;
let _galagaChallStep = 0;
let _temBgmStep = 0;
let _gyrussBgmStep = 0;

function getSfxCategoryColor(idx) {
  const bank = (typeof SFX_BANKS !== 'undefined' && SFX_BANKS[currentSfxBank]) ? SFX_BANKS[currentSfxBank] : null;
  if (bank && bank.sounds && bank.sounds[idx]) {
    return bank.sounds[idx].color;
  }
  if (idx < 7) return '#f5a623';
  if (idx < 12) return '#00e5ff';
  if (idx < 16) return '#ff9f1c';
  if (idx < 20) return '#ff4757';
  if (idx < 23) return '#2ecc71';
  return '#a55eea';
}

function switchSfxBank(idx) {
  initAudio();
  currentSfxBank = (idx >= 0 && idx < SFX_BANKS.length) ? idx : 0;
  const bank = SFX_BANKS[currentSfxBank];
  sfxNames = bank.sounds.map(s => s.id);

  document.querySelectorAll('.sfx-bank-btn').forEach((btn, i) => {
    btn.classList.toggle('active', i === currentSfxBank);
  });

  const tag = document.getElementById('sfxBankTag');
  if (tag) {
    tag.textContent = bank.shortName + ' (' + bank.sounds.length + ' SFX)';
    tag.style.color = bank.color;
    tag.style.borderColor = bank.color;
  }
  const desc = document.getElementById('sfxBankDesc');
  if (desc) desc.textContent = bank.subtitle;

  renderSoundboardPads();
  if (typeof updateKeyLabels === 'function') updateKeyLabels();

  if (typeof currentMode !== 'undefined' && currentMode === 'soundboard') {
    const st = document.getElementById('engineStatus');
    if (st) st.innerHTML = 'ARCADE SOUNDBOARD: <b>' + bank.name + '</b>';
  }
}

function renderSoundboardPads() {
  const container = document.getElementById('soundboardPadsGrid');
  if (!container || typeof SFX_BANKS === 'undefined') return;
  container.innerHTML = '';
  const bank = SFX_BANKS[currentSfxBank];
  bank.sounds.forEach((s, idx) => {
    const pad = document.createElement('div');
    pad.className = 'sfx-pad';
    pad.id = 'sfxPad_' + idx;
    if (pad.style && pad.style.setProperty) {
      pad.style.setProperty('--pad-color', s.color);
      pad.style.setProperty('--pad-glow', s.color + '80');
    }
    pad.innerHTML = `
      <span class="sfx-pad-num">${String(idx + 1).padStart(2, '0')}</span>
      <span class="sfx-pad-icon">${s.icon}</span>
      <span class="sfx-pad-name" style="color:${s.color}">${s.name}</span>
      <span class="sfx-pad-game">${s.game}</span>
      <span class="sfx-pad-chip">${s.chip}</span>
    `;
    pad.onclick = () => triggerSoundboardPad(idx);
    container.appendChild(pad);
  });
}

function triggerSoundboardPad(idx) {
  initAudio();
  const bank = SFX_BANKS[currentSfxBank];
  if (!bank || !bank.sounds[idx]) return;
  const s = bank.sounds[idx];

  playArcadeSfx(s.id);

  const pad = document.getElementById('sfxPad_' + idx);
  if (pad) {
    pad.classList.add('active');
    setTimeout(() => pad.classList.remove('active'), 180);
  }

  const keyEl = document.querySelector(`[data-key="${idx}"]`);
  if (keyEl) {
    keyEl.classList.add('active', 'lit');
    setTimeout(() => keyEl.classList.remove('active', 'lit'), 180);
  }

  const lastEl = document.getElementById('sfxLastTriggered');
  if (lastEl) {
    lastEl.innerHTML = `PLAYING: <b style="color:${s.color};">${s.id}</b> (${s.name} · ${s.game} · ${s.chip})`;
  }

  const midiLed = document.getElementById('midiLed');
  if (midiLed) {
    midiLed.classList.add('active');
    setTimeout(() => midiLed.classList.remove('active'), 120);
  }
}
'''
def get_play_arcade_sfx_js():
    return '''
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
    // =====================================================================
    // BANK 1: GOLDEN AGE ARCADE (1978–1982) · NAMCO WSG, TAITO & ATARI POKEY
    // =====================================================================

    case 'WAKA': {
      // Pac-Man (1980 Namco): Authentic Namco WSG Alternating Chomp Munch
      // Alternates between Waka A (low-to-high scoop) and Waka B (high-to-low crunch)
      // Combines triangle wave fundamental with subtle square overtone (WSG 4-bit PROM wavetable)
      _pacWakaCycle = 1 - _pacWakaCycle;
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle';
      const oscHarm = audioCtx.createOscillator(), gHarm = audioCtx.createGain();
      oscHarm.type = 'square';

      if (_pacWakaCycle === 0) {
        // Waka 1: 185 Hz -> 495 Hz scoop
        osc.frequency.setValueAtTime(185, now);
        osc.frequency.exponentialRampToValueAtTime(495, now + 0.055);
        oscHarm.frequency.setValueAtTime(370, now);
        oscHarm.frequency.exponentialRampToValueAtTime(990, now + 0.055);
      } else {
        // Waka 2: 495 Hz -> 210 Hz descent
        osc.frequency.setValueAtTime(495, now);
        osc.frequency.exponentialRampToValueAtTime(210, now + 0.065);
        oscHarm.frequency.setValueAtTime(990, now);
        oscHarm.frequency.exponentialRampToValueAtTime(420, now + 0.065);
      }

      g.gain.setValueAtTime(0.70, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.075);
      gHarm.gain.setValueAtTime(0.25, now);
      gHarm.gain.exponentialRampToValueAtTime(0.01, now + 0.075);

      osc.connect(g); oscHarm.connect(gHarm);
      g.connect(filterNode); gHarm.connect(filterNode);
      osc.start(now); oscHarm.start(now);
      osc.stop(now + 0.08); oscHarm.stop(now + 0.08);
      break;
    }

    case 'SIREN': {
      // Pac-Man Ghost Siren: Continuous rising and falling pitch sweep with WSG body
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(392, now);
      osc.frequency.linearRampToValueAtTime(587, now + 0.18);
      osc.frequency.linearRampToValueAtTime(392, now + 0.36);
      g.gain.setValueAtTime(0.65, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.38);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.39);
      break;
    }

    case 'FRUIT': {
      // Pac-Man Bonus Fruit Eat: High dual-tone Namco WSG chime: 1568 Hz (50ms) -> 2093 Hz (240ms)
      const osc1 = audioCtx.createOscillator(), g1 = audioCtx.createGain();
      osc1.type = 'square'; osc1.frequency.setValueAtTime(1568, now);
      g1.gain.setValueAtTime(0.65, now);
      g1.gain.exponentialRampToValueAtTime(0.01, now + 0.05);
      osc1.connect(g1); g1.connect(filterNode);
      osc1.start(now); osc1.stop(now + 0.055);

      const osc2 = audioCtx.createOscillator(), g2 = audioCtx.createGain();
      osc2.type = 'square'; osc2.frequency.setValueAtTime(2093, now + 0.05);
      g2.gain.setValueAtTime(0.70, now + 0.05);
      g2.gain.exponentialRampToValueAtTime(0.001, now + 0.30);
      osc2.connect(g2); g2.connect(filterNode);
      osc2.start(now + 0.05); osc2.stop(now + 0.32);
      break;
    }

    case 'GHOST': {
      // Pac-Man Ghost Eat: Rapid 5-tone ascending WSG arpeggio (G4, C5, E5, G5, C6) in 28ms staccato bursts
      [392, 523, 659, 784, 1046].forEach((f, idx) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(f, now + idx * 0.028);
        g.gain.setValueAtTime(0.65, now + idx * 0.028);
        g.gain.exponentialRampToValueAtTime(0.01, now + (idx + 1) * 0.028);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + idx * 0.028); osc.stop(now + (idx + 1) * 0.03);
      });
      break;
    }

    case 'BLUE': {
      // Pac-Man Frightened Ghost Warble: 466 Hz (Bb4) / 622 Hz (Eb5) alternating with 6 Hz wobble
      const osc = audioCtx.createOscillator(), lfo = audioCtx.createOscillator();
      const lfoG = audioCtx.createGain(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(466, now);
      lfo.type = 'square'; lfo.frequency.setValueAtTime(6.5, now); lfoG.gain.setValueAtTime(156, now);
      lfo.connect(lfoG); lfoG.connect(osc.frequency);
      g.gain.setValueAtTime(0.65, now); g.gain.exponentialRampToValueAtTime(0.01, now + 0.38);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); lfo.start(now); osc.stop(now + 0.40); lfo.stop(now + 0.40);
      break;
    }

    case 'EYES': {
      // Pac-Man Ghost Eyes Returning: Fast ping-pong two-tone pulse at 1175 Hz (D6) and 1568 Hz (G6)
      [0, 0.045, 0.09, 0.135, 0.18].forEach((d, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(i % 2 === 0 ? 1175 : 1568, now + d);
        g.gain.setValueAtTime(0.60, now + d);
        g.gain.exponentialRampToValueAtTime(0.01, now + d + 0.04);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + d); osc.stop(now + d + 0.045);
      });
      break;
    }

    case 'DEATH': {
      // Pac-Man (1980 Namco): 11-Step Chromatic WSG Death Descent followed by double pop
      const freqs = [890, 840, 794, 750, 708, 668, 630, 595, 561, 529, 499];
      freqs.forEach((f, idx) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(f, now + idx * 0.055);
        osc.frequency.exponentialRampToValueAtTime(f * 0.90, now + (idx + 1) * 0.055);
        g.gain.setValueAtTime(0.65, now + idx * 0.055);
        g.gain.exponentialRampToValueAtTime(0.01, now + (idx + 1) * 0.055);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + idx * 0.055); osc.stop(now + (idx + 1) * 0.058);
      });

      // Authentic double pop at end
      const tPop1 = now + 11 * 0.055;
      const p1 = audioCtx.createOscillator(), gP1 = audioCtx.createGain();
      p1.type = 'triangle'; p1.frequency.setValueAtTime(175, tPop1);
      p1.frequency.exponentialRampToValueAtTime(45, tPop1 + 0.045);
      gP1.gain.setValueAtTime(0.75, tPop1); gP1.gain.exponentialRampToValueAtTime(0.01, tPop1 + 0.045);
      p1.connect(gP1); gP1.connect(filterNode);
      p1.start(tPop1); p1.stop(tPop1 + 0.05);

      const tPop2 = tPop1 + 0.06;
      const p2 = audioCtx.createOscillator(), gP2 = audioCtx.createGain();
      p2.type = 'triangle'; p2.frequency.setValueAtTime(130, tPop2);
      p2.frequency.exponentialRampToValueAtTime(35, tPop2 + 0.05);
      gP2.gain.setValueAtTime(0.80, tPop2); gP2.gain.exponentialRampToValueAtTime(0.01, tPop2 + 0.05);
      p2.connect(gP2); gP2.connect(filterNode);
      p2.start(tPop2); p2.stop(tPop2 + 0.055);
      break;
    }

    case 'INV-STEP': {
      // Space Invaders (1978 Taito): Authentic 4-Beat Marching Bass Thud
      // Cycles sequentially through the 4 discrete tank frequencies:
      // Beat 1: 58.7 Hz (D2) | Beat 2: 55.4 Hz (C#2) | Beat 3: 52.3 Hz (C2) | Beat 4: 49.0 Hz (B1)
      const invFrequencies = [58.7, 55.4, 52.3, 49.0];
      const sFreq = invFrequencies[_invStepCycle % 4];
      _invStepCycle = (_invStepCycle + 1) % 4;

      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(sFreq, now);
      osc.frequency.exponentialRampToValueAtTime(sFreq * 0.82, now + 0.08);
      g.gain.setValueAtTime(0.95, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.09);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.095);

      const oscClick = audioCtx.createOscillator(), gClick = audioCtx.createGain();
      oscClick.type = 'square';
      oscClick.frequency.setValueAtTime(sFreq * 2.5, now);
      oscClick.frequency.exponentialRampToValueAtTime(sFreq, now + 0.025);
      gClick.gain.setValueAtTime(0.60, now);
      gClick.gain.exponentialRampToValueAtTime(0.01, now + 0.025);
      oscClick.connect(gClick); gClick.connect(filterNode);
      oscClick.start(now); oscClick.stop(now + 0.03);
      break;
    }

    case 'INV-UFO': {
      // Space Invaders (1978 Taito): Flying Saucer Siren (450 Hz / 495 Hz toggling every 55ms)
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square';
      const lfo = audioCtx.createOscillator(), lfoG = audioCtx.createGain();
      lfo.type = 'square'; lfo.frequency.setValueAtTime(9.5, now);
      lfoG.gain.setValueAtTime(45, now);
      lfo.connect(lfoG); lfoG.connect(osc.frequency);
      osc.frequency.setValueAtTime(472, now);
      g.gain.setValueAtTime(0.65, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.38);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); lfo.start(now);
      osc.stop(now + 0.40); lfo.stop(now + 0.40);
      break;
    }

    case 'INV-EXP': {
      // Space Invaders (1978 Taito): Base / Alien Explosion
      // Resonant white noise burst sweeping from 1400 Hz down to 65 Hz over 400ms + sub thud
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(1400, now); flt.Q.setValueAtTime(3.5, now);
      flt.frequency.exponentialRampToValueAtTime(65, now + 0.38);
      gN.gain.setValueAtTime(0.95, now);
      gN.gain.exponentialRampToValueAtTime(0.01, now + 0.40);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.42);

      const osc = audioCtx.createOscillator(), gO = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(80, now);
      osc.frequency.exponentialRampToValueAtTime(35, now + 0.25);
      gO.gain.setValueAtTime(0.70, now);
      gO.gain.exponentialRampToValueAtTime(0.01, now + 0.25);
      osc.connect(gO); gO.connect(filterNode);
      osc.start(now); osc.stop(now + 0.27);
      break;
    }

    case 'INV-LASER':
    case 'INV-FIRE': {
      // Space Invaders (1978 Taito): Laser Cannon Fire
      // Discrete analog circuit sweep: 3900 Hz exponentially swooping to 340 Hz in 160ms
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(3900, now);
      osc.frequency.exponentialRampToValueAtTime(340, now + 0.16);
      g.gain.setValueAtTime(0.80, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.16);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.17);

      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'highpass'; flt.frequency.setValueAtTime(3000, now);
      gN.gain.setValueAtTime(0.40, now);
      gN.gain.exponentialRampToValueAtTime(0.01, now + 0.03);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.035);
      break;
    }

    case 'TRACT': {
      // Galaga (1981 Namco): Authentic Tractor Beam
      // Dual Namco WSG voices at 185 Hz and 370 Hz modulated by 24 Hz square AM gate
      const osc1 = audioCtx.createOscillator(), osc2 = audioCtx.createOscillator();
      const g = audioCtx.createGain(), lfo = audioCtx.createOscillator(), lfoG = audioCtx.createGain();
      osc1.type = 'square'; osc1.frequency.setValueAtTime(185, now);
      osc2.type = 'sawtooth'; osc2.frequency.setValueAtTime(370, now);
      lfo.type = 'square'; lfo.frequency.setValueAtTime(24, now);
      lfoG.gain.setValueAtTime(0.5, now);
      try { lfo.connect(lfoG); lfoG.connect(g.gain); } catch (e) {}
      g.gain.setValueAtTime(0.5, now);
      osc1.connect(g); osc2.connect(g); g.connect(filterNode);
      osc1.start(now); osc2.start(now); lfo.start(now);
      osc1.stop(now + 0.42); osc2.stop(now + 0.42); lfo.stop(now + 0.42);
      break;
    }

    case 'DIVE': {
      // Galaga (1981 Namco): Alien Dive-Bomb Swoop
      // WSG frequency swoop: 1550 Hz down to 240 Hz with 28 Hz vibrato LFO
      const osc = audioCtx.createOscillator(), lfo = audioCtx.createOscillator();
      const lfoG = audioCtx.createGain(), g = audioCtx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(1550, now);
      osc.frequency.exponentialRampToValueAtTime(240, now + 0.38);
      lfo.type = 'square'; lfo.frequency.setValueAtTime(28, now);
      lfoG.gain.setValueAtTime(110, now);
      try { lfo.connect(lfoG); lfoG.connect(osc.frequency); } catch (e) {}
      g.gain.setValueAtTime(0.70, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.38);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); lfo.start(now);
      osc.stop(now + 0.40); lfo.stop(now + 0.40);
      break;
    }

    case 'CAPTURE': {
      // Galaga (1981 Namco): Ship Captured Alarm (659 Hz / 880 Hz alternating every 32ms)
      [0, 0.032, 0.064, 0.096, 0.128, 0.160, 0.192, 0.224, 0.256, 0.288].forEach((d, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(i % 2 === 0 ? 659 : 880, now + d);
        g.gain.setValueAtTime(0.60, now + d);
        g.gain.exponentialRampToValueAtTime(0.01, now + d + 0.03);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + d); osc.stop(now + d + 0.032);
      });
      break;
    }

    case 'BOSS': {
      // Galaga (1981 Namco): Boss Galaga Explosion (two-stage blast + 95 Hz sub-decay)
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(1800, now); flt.Q.setValueAtTime(2.2, now);
      flt.frequency.exponentialRampToValueAtTime(320, now + 0.35);
      gN.gain.setValueAtTime(0.90, now);
      gN.gain.exponentialRampToValueAtTime(0.01, now + 0.38);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.40);

      const osc = audioCtx.createOscillator(), gO = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(95, now);
      osc.frequency.exponentialRampToValueAtTime(32, now + 0.35);
      gO.gain.setValueAtTime(0.85, now);
      gO.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
      osc.connect(gO); gO.connect(filterNode);
      osc.start(now); osc.stop(now + 0.38);
      break;
    }

    case 'GALAGA-DEATH': {
      // Galaga Authentic WSG Starfighter Explode: Resonant bandpass sweep + WSG pitch dive (540 -> 65 Hz)
      const t = now;
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'bandpass';
      flt.frequency.setValueAtTime(1800, t);
      flt.frequency.exponentialRampToValueAtTime(180, t + 0.70);
      flt.Q.setValueAtTime(3.2, t);
      gN.gain.setValueAtTime(0.95, t);
      gN.gain.exponentialRampToValueAtTime(0.01, t + 0.75);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(t); noise.stop(t + 0.78);

      const osc = audioCtx.createOscillator(), gO = audioCtx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(540, t);
      osc.frequency.exponentialRampToValueAtTime(65, t + 0.65);
      gO.gain.setValueAtTime(0.75, t);
      gO.gain.exponentialRampToValueAtTime(0.01, t + 0.70);
      osc.connect(gO); gO.connect(filterNode);
      osc.start(t); osc.stop(t + 0.72);
      break;
    }

    case 'BONUS': {
      // Galaga Stage Clear / Fanfare: Namco WSG 5-note arpeggio (C5, E5, G5, C6, E6)
      [523, 659, 784, 1046, 1318].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.055);
        g.gain.setValueAtTime(0.70, now + i * 0.055);
        g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.055);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.055); osc.stop(now + (i + 1) * 0.06);
      });
      break;
    }

    case 'AST-THR': {
      // Asteroids (1979 Atari): Ship Thrust Rumble
      // POKEY shift register noise pulsed at 24 Hz through resonant 85 Hz lowpass filter
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(85, now); flt.Q.setValueAtTime(3.5, now);
      const lfo = audioCtx.createOscillator(), lfoG = audioCtx.createGain();
      lfo.type = 'square'; lfo.frequency.setValueAtTime(24, now);
      lfoG.gain.setValueAtTime(0.5, now);
      lfo.connect(lfoG); lfoG.connect(g.gain);
      g.gain.setValueAtTime(0.5, now);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); lfo.start(now);
      noise.stop(now + 0.22); lfo.stop(now + 0.22);
      break;
    }

    case 'AST-SAU': {
      // Asteroids Saucer Alarm: Alternating 880 Hz / 980 Hz square wave switching every 65ms
      [0, 0.065, 0.13, 0.195, 0.26].forEach((d, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(i % 2 === 0 ? 880 : 980, now + d);
        g.gain.setValueAtTime(0.60, now + d);
        g.gain.exponentialRampToValueAtTime(0.01, now + d + 0.06);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + d); osc.stop(now + d + 0.065);
      });
      break;
    }

    case 'AST-EXP': {
      // Asteroids Rock Explosion: Resonant white noise burst through 120 Hz lowpass filter
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(140, now); flt.Q.setValueAtTime(2.8, now);
      flt.frequency.exponentialRampToValueAtTime(35, now + 0.65);
      g.gain.setValueAtTime(0.95, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.70);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.75);
      break;
    }

    case 'AST-DEATH':
    case 'AST-SHIP-EXPLODE': {
      // Asteroids (1979 Atari): Ship Explode (High Bang discrete circuit)
      // High-energy noise transient + 1800 Hz to 90 Hz bandpass burst decaying over 800ms
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(1800, now); flt.Q.setValueAtTime(2.2, now);
      flt.frequency.exponentialRampToValueAtTime(90, now + 0.75);
      gN.gain.setValueAtTime(0.98, now);
      gN.gain.exponentialRampToValueAtTime(0.01, now + 0.80);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.82);

      const osc = audioCtx.createOscillator(), gO = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(75, now);
      osc.frequency.exponentialRampToValueAtTime(25, now + 0.70);
      gO.gain.setValueAtTime(0.85, now);
      gO.gain.exponentialRampToValueAtTime(0.01, now + 0.72);
      osc.connect(gO); gO.connect(filterNode);
      osc.start(now); osc.stop(now + 0.75);
      break;
    }

    case 'AST-FIRE': {
      // Asteroids Photon Torpedo: Sharp POKEY chirp 2400 Hz down to 260 Hz in 45ms
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(2400, now);
      osc.frequency.exponentialRampToValueAtTime(260, now + 0.045);
      g.gain.setValueAtTime(0.80, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.045);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.05);
      break;
    }

    case 'TEM-ZAP': {
      // Tempest Superzapper: Multi-octave electric zap: 3600 Hz down to 120 Hz with noise crackle
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(3600, now);
      osc.frequency.exponentialRampToValueAtTime(120, now + 0.28);
      g.gain.setValueAtTime(0.85, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.28);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.30);

      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'highpass'; flt.frequency.setValueAtTime(2200, now);
      gN.gain.setValueAtTime(0.55, now);
      gN.gain.exponentialRampToValueAtTime(0.01, now + 0.22);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.24);
      break;
    }

    case 'TEM-DEATH': {
      // Tempest (1981 Atari): Disintegration Polynomial Cascade
      const t = now;
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'lowpass';
      flt.frequency.setValueAtTime(3200, t);
      flt.frequency.exponentialRampToValueAtTime(75, t + 0.68);
      gN.gain.setValueAtTime(0.95, t);
      gN.gain.exponentialRampToValueAtTime(0.01, t + 0.70);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(t); noise.stop(t + 0.72);

      const osc = audioCtx.createOscillator(), gO = audioCtx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(1200, t);
      osc.frequency.exponentialRampToValueAtTime(45, t + 0.65);
      gO.gain.setValueAtTime(0.70, t);
      gO.gain.exponentialRampToValueAtTime(0.01, t + 0.68);
      osc.connect(gO); gO.connect(filterNode);
      osc.start(t); osc.stop(t + 0.70);
      break;
    }

    case 'TEM-FIRE': {
      // Tempest Particle Gun: Sharp POKEY particle shot: 2400 Hz decaying to 500 Hz in 40ms
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(2400, now);
      osc.frequency.exponentialRampToValueAtTime(500, now + 0.04);
      g.gain.setValueAtTime(0.75, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.04);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.045);
      break;
    }

    case 'TEM-SPIKE': {
      // Tempest Spike Drill: Buzzing POKEY square wave (180 Hz) with 60 Hz AM modulation
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(180, now);
      const lfo = audioCtx.createOscillator(), lfoG = audioCtx.createGain();
      lfo.type = 'square'; lfo.frequency.setValueAtTime(60, now);
      lfoG.gain.setValueAtTime(0.5, now);
      lfo.connect(lfoG); lfoG.connect(g.gain);
      g.gain.setValueAtTime(0.60, now);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); lfo.start(now);
      osc.stop(now + 0.20); lfo.stop(now + 0.20);
      break;
    }

    case 'TEM-FLIP': {
      // Tempest Flipper Flip: Alternating 600 Hz and 750 Hz trill every 22ms
      [0, 0.022, 0.044, 0.066].forEach((d, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(i % 2 === 0 ? 600 : 750, now + d);
        g.gain.setValueAtTime(0.55, now + d);
        g.gain.exponentialRampToValueAtTime(0.01, now + d + 0.02);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + d); osc.stop(now + d + 0.022);
      });
      break;
    }

    case 'DIG-PUMP': {
      // Dig Dug Harpoon Pump: Namco WSG two-stage pump: 370 Hz (50ms) -> 587 Hz (50ms)
      const osc1 = audioCtx.createOscillator(), g1 = audioCtx.createGain();
      osc1.type = 'square'; osc1.frequency.setValueAtTime(370, now);
      g1.gain.setValueAtTime(0.65, now);
      g1.gain.exponentialRampToValueAtTime(0.01, now + 0.05);
      osc1.connect(g1); g1.connect(filterNode);
      osc1.start(now); osc1.stop(now + 0.052);

      const osc2 = audioCtx.createOscillator(), g2 = audioCtx.createGain();
      osc2.type = 'square'; osc2.frequency.setValueAtTime(587, now + 0.05);
      g2.gain.setValueAtTime(0.70, now + 0.05);
      g2.gain.exponentialRampToValueAtTime(0.01, now + 0.10);
      osc2.connect(g2); g2.connect(filterNode);
      osc2.start(now + 0.05); osc2.stop(now + 0.105);
      break;
    }

    case 'DIG-POP': {
      // Dig Dug Pooka Pop: Loud pop: 740 Hz down to 90 Hz sweep layered with highpass noise snap
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(740, now);
      osc.frequency.exponentialRampToValueAtTime(90, now + 0.08);
      g.gain.setValueAtTime(0.85, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.085);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.09);

      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'highpass'; flt.frequency.setValueAtTime(1500, now);
      gN.gain.setValueAtTime(0.65, now);
      gN.gain.exponentialRampToValueAtTime(0.01, now + 0.06);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.07);
      break;
    }

    case 'RALLY-SMK': {
      // Rally-X Smoke Screen: Bandpass noise puff (450 Hz, Q=2.0) with rapid 120ms decay
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(450, now); flt.Q.setValueAtTime(2.0, now);
      g.gain.setValueAtTime(0.75, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.12);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.13);
      break;
    }

    case 'RALLY-FLG': {
      // Rally-X Special Flag: Sparkling 6-note arpeggio (587, 740, 880, 1175, 880, 1175 Hz)
      [587, 740, 880, 1175, 880, 1175].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.04);
        g.gain.setValueAtTime(0.65, now + i * 0.04);
        g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.04);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.04); osc.stop(now + (i + 1) * 0.045);
      });
      break;
    }

    case 'WARP': {
      // Gyruss Cosmic Warp: Dual detuned sawtooth oscillators sweeping exponentially from 110 Hz to 2800 Hz
      const osc1 = audioCtx.createOscillator(), osc2 = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc1.type = 'sawtooth'; osc1.frequency.setValueAtTime(110, now);
      osc1.frequency.exponentialRampToValueAtTime(2800, now + 0.42);
      osc2.type = 'sawtooth'; osc2.frequency.setValueAtTime(114, now);
      osc2.frequency.exponentialRampToValueAtTime(2840, now + 0.42);
      g.gain.setValueAtTime(0.65, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.42);
      osc1.connect(g); osc2.connect(g); g.connect(filterNode);
      osc1.start(now); osc2.start(now);
      osc1.stop(now + 0.44); osc2.stop(now + 0.44);
      break;
    }

    case 'COIN': {
      // Classic Arcade Coin Mechanism Chime: B5 (988 Hz) 60ms pulse -> E6 (1319 Hz) 380ms ring
      const osc1 = audioCtx.createOscillator(), g1 = audioCtx.createGain();
      osc1.type = 'square'; osc1.frequency.setValueAtTime(988, now);
      g1.gain.setValueAtTime(0.70, now); g1.gain.exponentialRampToValueAtTime(0.01, now + 0.06);
      osc1.connect(g1); g1.connect(filterNode);
      osc1.start(now); osc1.stop(now + 0.065);

      const osc2 = audioCtx.createOscillator(), g2 = audioCtx.createGain();
      osc2.type = 'square'; osc2.frequency.setValueAtTime(1319, now + 0.06);
      g2.gain.setValueAtTime(0.80, now + 0.06); g2.gain.exponentialRampToValueAtTime(0.001, now + 0.42);
      osc2.connect(g2); g2.connect(filterNode);
      osc2.start(now + 0.06); osc2.stop(now + 0.44);
      break;
    }

    // =====================================================================
    // BANK 2: NINTENDO 8-BIT ARCADE (1981–1985) · 8035 DAC & NES APU
    // =====================================================================

    case 'DK-WALK': {
      // Donkey Kong (1981 Nintendo): Mario Footstep Squeak Chirp (8035 DAC)
      // Alternating 8035 DAC squeak chirps: Step A (850 -> 380 Hz) and Step B (720 -> 310 Hz)
      _dkStepCycle = 1 - (_dkStepCycle || 0);
      const startF = _dkStepCycle === 0 ? 850 : 720;
      const endF = _dkStepCycle === 0 ? 380 : 310;
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square';
      osc.frequency.setValueAtTime(startF, now);
      osc.frequency.exponentialRampToValueAtTime(endF, now + 0.024);
      g.gain.setValueAtTime(0.70, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.026);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.030);
      break;
    }

    case 'DK-JUMP': {
      // Donkey Kong (1981 Nintendo): Authentic Continuous Spring Boing
      // 8-step FSK staircase frequency chirp generated continuously by Nintendo 8035 microcontroller DAC
      const dkPitches = [262, 311, 370, 440, 523, 622, 740, 880];
      const stepDur = 0.019;
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square';
      dkPitches.forEach((f, idx) => {
        osc.frequency.setValueAtTime(f, now + idx * stepDur);
      });
      g.gain.setValueAtTime(0.75, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + dkPitches.length * stepDur + 0.01);
      osc.connect(g); g.connect(filterNode);
      osc.start(now);
      osc.stop(now + dkPitches.length * stepDur + 0.015);
      break;
    }

    case 'DK-HAMR': {
      // Donkey Kong Hammer: High metallic clink (1480 + 2200 Hz) + noise click + 75 Hz barrel thud
      const oscM1 = audioCtx.createOscillator(), oscM2 = audioCtx.createOscillator(), gM = audioCtx.createGain();
      oscM1.type = 'square'; oscM1.frequency.setValueAtTime(1480, now);
      oscM2.type = 'square'; oscM2.frequency.setValueAtTime(2200, now);
      gM.gain.setValueAtTime(0.65, now);
      gM.gain.exponentialRampToValueAtTime(0.01, now + 0.06);
      oscM1.connect(gM); oscM2.connect(gM); gM.connect(filterNode);
      oscM1.start(now); oscM2.start(now);
      oscM1.stop(now + 0.07); oscM2.stop(now + 0.07);

      const oscT = audioCtx.createOscillator(), gT = audioCtx.createGain();
      oscT.type = 'triangle'; oscT.frequency.setValueAtTime(75, now);
      oscT.frequency.exponentialRampToValueAtTime(30, now + 0.16);
      gT.gain.setValueAtTime(0.90, now);
      gT.gain.exponentialRampToValueAtTime(0.01, now + 0.16);
      oscT.connect(gT); gT.connect(filterNode);
      oscT.start(now); oscT.stop(now + 0.18);
      break;
    }

    case 'DK-FALL': {
      // Donkey Kong Barrel Smash: 8035 DAC stepped pitch drop (260 -> 55 Hz) + resonant lowpass noise
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(260, now);
      osc.frequency.exponentialRampToValueAtTime(55, now + 0.22);
      g.gain.setValueAtTime(0.85, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.24);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.25);

      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(320, now); flt.Q.setValueAtTime(2.2, now);
      flt.frequency.exponentialRampToValueAtTime(60, now + 0.22);
      gN.gain.setValueAtTime(0.85, now);
      gN.gain.exponentialRampToValueAtTime(0.01, now + 0.22);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.24);
      break;
    }

    case 'DK-ROAR': {
      // Kong Chest-Beating Roar: 3 deep resonant guttural bursts at 95 Hz
      [0, 0.08, 0.16].forEach(d => {
        const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
        flt.type = 'bandpass'; flt.frequency.setValueAtTime(95, now + d); flt.Q.setValueAtTime(3.5, now + d);
        g.gain.setValueAtTime(0.95, now + d); g.gain.exponentialRampToValueAtTime(0.01, now + d + 0.07);
        noise.connect(flt); flt.connect(g); g.connect(filterNode);
        noise.start(now + d); noise.stop(now + d + 0.075);
      });
      break;
    }

    case 'DK-HELP': {
      // Pauline "HELP!" Cry: High two-tone plea: 1568 Hz (G6) then 1760 Hz (A6) with vibrato
      [0, 0.08].forEach((d, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(i === 0 ? 1568 : 1760, now + d);
        g.gain.setValueAtTime(0.60, now + d); g.gain.exponentialRampToValueAtTime(0.01, now + d + 0.07);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + d); osc.stop(now + d + 0.08);
      });
      break;
    }

    case 'DK-WIN': {
      // Donkey Kong 25m Victory Fanfare: Nintendo 8035 DAC square melody (G4, C5, E5, G5, F5, G5)
      const notes = [392, 523, 659, 784, 698, 784];
      notes.forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.075);
        g.gain.setValueAtTime(0.70, now + i * 0.075);
        g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.075);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.075); osc.stop(now + (i + 1) * 0.08);
      });
      break;
    }

    case 'MARIO-C': {
      // Mario Bros / NES APU Coin: B5 (988 Hz) for 55ms then E6 (1319 Hz) ringing for 380ms
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square';
      osc.frequency.setValueAtTime(988, now);
      osc.frequency.setValueAtTime(1319, now + 0.055);
      g.gain.setValueAtTime(0.75, now);
      g.gain.exponentialRampToValueAtTime(0.001, now + 0.38);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.40);
      break;
    }

    case 'PIPE': {
      // Mario Pipe Warp: APU descending 8-step arpeggio (392 down to 262 Hz in 35ms steps)
      const pipeNotes = [392, 370, 349, 330, 311, 294, 277, 262];
      pipeNotes.forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.035);
        g.gain.setValueAtTime(0.65, now + i * 0.035);
        g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.035);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.035); osc.stop(now + (i + 1) * 0.04);
      });
      break;
    }

    case 'TURTLE': {
      // Shell Kick: Highpass noise click + 220 Hz down to 50 Hz pitch drop in 65ms
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(220, now);
      osc.frequency.exponentialRampToValueAtTime(50, now + 0.065);
      g.gain.setValueAtTime(0.85, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.07);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.075);
      break;
    }

    case 'POW': {
      // Mario Bros POW Block: Screen-shaking 50 Hz sub-bass rumble + 180 Hz lowpass noise burst
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(180, now); flt.Q.setValueAtTime(3.0, now);
      flt.frequency.exponentialRampToValueAtTime(35, now + 0.45);
      gN.gain.setValueAtTime(0.95, now);
      gN.gain.exponentialRampToValueAtTime(0.01, now + 0.50);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.52);

      const osc = audioCtx.createOscillator(), gO = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(55, now);
      osc.frequency.exponentialRampToValueAtTime(25, now + 0.45);
      gO.gain.setValueAtTime(0.85, now);
      gO.gain.exponentialRampToValueAtTime(0.01, now + 0.48);
      osc.connect(gO); gO.connect(filterNode);
      osc.start(now); osc.stop(now + 0.50);
      break;
    }

    case 'MARIO-1UP': {
      // Super Mario Bros (1985 Nintendo): Authentic 6-Note 1-Up Jingle on APU square wave
      // E5 (659), G5 (784), E6 (1319), C6 (1047), D6 (1175), G6 (1568)
      const notes1Up = [659, 784, 1319, 1047, 1175, 1568];
      const dur = 0.055;
      notes1Up.forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(f, now + i * dur);
        g.gain.setValueAtTime(0.65, now + i * dur);
        g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * dur);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * dur); osc.stop(now + (i + 1) * dur + 0.005);
      });
      break;
    }

    case 'MARIO-FIRE': {
      // Super Mario Fireball: Rapid APU chirp (1100 Hz dropping to 280 Hz in 42ms)
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(1100, now);
      osc.frequency.exponentialRampToValueAtTime(280, now + 0.042);
      g.gain.setValueAtTime(0.75, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.042);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.045);
      break;
    }

    case 'MARIO-GROW': {
      // Super Mario Mushroom Grow: Ascending 5-note sequence (C4, G4, C5, G5, C6) in 32ms bursts
      [261, 392, 523, 784, 1046].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.032);
        g.gain.setValueAtTime(0.65, now + i * 0.032);
        g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.032);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.032); osc.stop(now + (i + 1) * 0.035);
      });
      break;
    }

    case 'MARIO-FLAG': {
      // Flagpole Slide: 16-step chromatic descending square wave scale from 784 down to 196 Hz
      const steps = 16;
      for (let i = 0; i < steps; i++) {
        const f = 784 * Math.pow(0.5, i / steps);
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.025);
        g.gain.setValueAtTime(0.60, now + i * 0.025);
        g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.025);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.025); osc.stop(now + (i + 1) * 0.028);
      }
      break;
    }

    case 'PUNCH-BELL': {
      // Punch-Out!! Ring Bell: Dual metallic bell chime (1568 Hz & 2093 Hz with 850ms decay)
      [1568, 2093].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'sine'; osc.frequency.setValueAtTime(f, now);
        g.gain.setValueAtTime(0.70 / (i + 1), now);
        g.gain.exponentialRampToValueAtTime(0.001, now + 0.85);
        osc.connect(g); g.connect(filterNode);
        osc.start(now); osc.stop(now + 0.88);
      });
      break;
    }

    case 'PUNCH-HIT': {
      // Punch-Out!! Jaw Uppercut: Bandpass noise crackle (750 Hz) + deep 130 -> 35 Hz body thud
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(750, now); flt.Q.setValueAtTime(2.5, now);
      gN.gain.setValueAtTime(0.85, now);
      gN.gain.exponentialRampToValueAtTime(0.01, now + 0.16);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.18);

      const osc = audioCtx.createOscillator(), gO = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(130, now);
      osc.frequency.exponentialRampToValueAtTime(35, now + 0.16);
      gO.gain.setValueAtTime(0.90, now);
      gO.gain.exponentialRampToValueAtTime(0.01, now + 0.18);
      osc.connect(gO); gO.connect(filterNode);
      osc.start(now); osc.stop(now + 0.20);
      break;
    }

    case 'PUNCH-KO': {
      // Punch-Out!! KO Buzzer: Harsh 110 Hz square buzzer pulsed 3 times
      [0, 0.10, 0.20].forEach(d => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(110, now + d);
        g.gain.setValueAtTime(0.75, now + d);
        g.gain.exponentialRampToValueAtTime(0.01, now + d + 0.08);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + d); osc.stop(now + d + 0.085);
      });
      break;
    }

    case 'BALLOON-POP': {
      // Balloon Fight Pop: Highpass noise snap + 550 Hz down to 120 Hz drop
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(550, now);
      osc.frequency.exponentialRampToValueAtTime(120, now + 0.07);
      g.gain.setValueAtTime(0.75, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.075);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.08);
      break;
    }

    case 'EXCITE-JUMP': {
      // Excitebike Ramp Launch: APU pulse revving from 160 Hz up to 480 Hz
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(160, now);
      osc.frequency.exponentialRampToValueAtTime(480, now + 0.18);
      g.gain.setValueAtTime(0.70, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.18);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.19);
      break;
    }

    case 'EXCITE-FALL': {
      // Excitebike Crash: Tumbling noise burst + skid
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(800, now); flt.Q.setValueAtTime(2.0, now);
      flt.frequency.exponentialRampToValueAtTime(140, now + 0.28);
      g.gain.setValueAtTime(0.85, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.30);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.32);
      break;
    }

    case 'ICE-SMASH': {
      // Ice Climber Shatter: Sparkling 3200 Hz highpass noise burst
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'highpass'; flt.frequency.setValueAtTime(3200, now);
      g.gain.setValueAtTime(0.75, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.14);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.15);
      break;
    }

    case 'DUCK-SHOT': {
      // Duck Hunt Zapper Shot: Light-gun trigger click + 90 Hz body thud
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(1400, now);
      osc.frequency.exponentialRampToValueAtTime(90, now + 0.08);
      g.gain.setValueAtTime(0.90, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.085);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.09);
      break;
    }

    case 'DUCK-FALL': {
      // Duck Hunt Bird Drop: Slide whistle dropping from 1200 down to 220 Hz
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sine'; osc.frequency.setValueAtTime(1200, now);
      osc.frequency.exponentialRampToValueAtTime(220, now + 0.45);
      g.gain.setValueAtTime(0.75, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.45);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.48);
      break;
    }

    case 'ZELDA-SECR': {
      // The Legend of Zelda (1986 Nintendo): Secret Discovery Chime
      // G4 (392), F#4 (370), D#4 (311), A3 (220), G#3 (207), E4 (330), G#4 (415), C5 (523)
      const zeldaNotes = [392, 370, 311, 220, 207, 330, 415, 523];
      const zDur = 0.065;
      zeldaNotes.forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(f, now + i * zDur);
        g.gain.setValueAtTime(0.65, now + i * zDur);
        g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * zDur);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * zDur); osc.stop(now + (i + 1) * zDur + 0.005);
      });
      break;
    }

    case 'START': {
      // Universal Arcade 1P Start Arpeggio: C5, G5, C6, E6 in bright chiptune
      [523, 784, 1046, 1318].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.05);
        g.gain.setValueAtTime(0.65, now + i * 0.05);
        g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.05);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.05); osc.stop(now + (i + 1) * 0.055);
      });
      break;
    }

    // =====================================================================
    // BANK 3: ATARI VECTOR & SCI-FI (1979–1984) · DEFENDER, TEMPEST & POKEY
    // =====================================================================

    case 'DEF-FIRE': {
      // Defender (1980 Williams): Rapid Laser
      // Williams 6808 DAC logarithmic downward sweep: 3800 Hz down to 220 Hz in 85ms
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(3800, now);
      osc.frequency.exponentialRampToValueAtTime(220, now + 0.085);
      g.gain.setValueAtTime(0.85, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.085);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.09);

      const oscSub = audioCtx.createOscillator(), gSub = audioCtx.createGain();
      oscSub.type = 'square';
      oscSub.frequency.setValueAtTime(1900, now);
      oscSub.frequency.exponentialRampToValueAtTime(110, now + 0.085);
      gSub.gain.setValueAtTime(0.35, now);
      gSub.gain.exponentialRampToValueAtTime(0.01, now + 0.085);
      oscSub.connect(gSub); gSub.connect(filterNode);
      oscSub.start(now); oscSub.stop(now + 0.09);
      break;
    }

    case 'DEF-SMART': {
      // Defender (1980 Williams): Smart Bomb Full-Screen Detonation
      // Multi-stage explosion: high-frequency 4 kHz flash decaying into a roaring 1.2s rumbling lowpass sweep
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'lowpass';
      flt.frequency.setValueAtTime(1600, now);
      flt.frequency.exponentialRampToValueAtTime(45, now + 1.15);
      flt.Q.setValueAtTime(3.0, now);
      gN.gain.setValueAtTime(0.98, now);
      gN.gain.exponentialRampToValueAtTime(0.005, now + 1.20);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 1.25);

      const osc = audioCtx.createOscillator(), gO = audioCtx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(160, now);
      osc.frequency.exponentialRampToValueAtTime(28, now + 1.10);
      gO.gain.setValueAtTime(0.85, now);
      gO.gain.exponentialRampToValueAtTime(0.005, now + 1.15);
      osc.connect(gO); gO.connect(filterNode);
      osc.start(now); osc.stop(now + 1.20);
      break;
    }

    case 'DEF-HUMAN': {
      // Defender Abduction Siren: Williams two-tone warble (980 Hz / 1320 Hz alternating at 18 Hz)
      const osc = audioCtx.createOscillator(), lfo = audioCtx.createOscillator();
      const lfoG = audioCtx.createGain(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(1150, now);
      lfo.type = 'square'; lfo.frequency.setValueAtTime(18, now);
      lfoG.gain.setValueAtTime(170, now);
      lfo.connect(lfoG); lfoG.connect(osc.frequency);
      g.gain.setValueAtTime(0.70, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.40);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); lfo.start(now);
      osc.stop(now + 0.42); lfo.stop(now + 0.42);
      break;
    }

    case 'DEF-CATCH': {
      // Defender Rescue Human: Ascending Williams DAC arpeggio (440, 554, 659, 880, 1108 Hz)
      [440, 554, 659, 880, 1108].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.045);
        g.gain.setValueAtTime(0.65, now + i * 0.045);
        g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.045);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.045); osc.stop(now + (i + 1) * 0.05);
      });
      break;
    }

    case 'DEF-HYPER': {
      // Defender Hyperspace: Glitchy swept noise burst + pitch warp
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(1200, now); flt.Q.setValueAtTime(3.0, now);
      flt.frequency.exponentialRampToValueAtTime(180, now + 0.28);
      gN.gain.setValueAtTime(0.85, now);
      gN.gain.exponentialRampToValueAtTime(0.01, now + 0.30);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.32);

      const osc = audioCtx.createOscillator(), gO = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(600, now);
      osc.frequency.exponentialRampToValueAtTime(80, now + 0.28);
      gO.gain.setValueAtTime(0.70, now);
      gO.gain.exponentialRampToValueAtTime(0.01, now + 0.30);
      osc.connect(gO); gO.connect(filterNode);
      osc.start(now); osc.stop(now + 0.32);
      break;
    }

    case 'JOUST-FLAP': {
      // Joust Ostrich Wing Flap: Williams 6808 low resonant flap (85 Hz square wave through lowpass filter)
      const osc = audioCtx.createOscillator(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(85, now);
      osc.frequency.exponentialRampToValueAtTime(35, now + 0.07);
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(160, now);
      g.gain.setValueAtTime(0.90, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.075);
      osc.connect(flt); flt.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.08);
      break;
    }

    case 'JOUST-SKID': {
      // Joust Platform Skid: Friction noise burst modulated at 25 Hz
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(950, now); flt.Q.setValueAtTime(2.5, now);
      g.gain.setValueAtTime(0.75, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.15);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.16);
      break;
    }

    case 'JOUST-LAVA': {
      // Joust Lava Splash: Bubbling lowpass noise + sub-bass splash
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(280, now); flt.Q.setValueAtTime(3.0, now);
      flt.frequency.exponentialRampToValueAtTime(50, now + 0.30);
      g.gain.setValueAtTime(0.85, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.32);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.35);
      break;
    }

    case 'ROBOT-STEP': {
      // Robotron 2084 Cyborg Step: 160 Hz square wave with rapid pitch bounce
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(160, now);
      osc.frequency.setValueAtTime(240, now + 0.02);
      osc.frequency.setValueAtTime(90, now + 0.04);
      g.gain.setValueAtTime(0.75, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.07);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.075);
      break;
    }

    case 'ROBOT-ZAP': {
      // Robotron Dual Laser: Williams sound board: 4200 Hz down to 450 Hz in 55ms
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(4200, now);
      osc.frequency.exponentialRampToValueAtTime(450, now + 0.055);
      g.gain.setValueAtTime(0.85, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.055);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.06);
      break;
    }

    case 'ROBOT-HUM': {
      // Robotron Human Saved: Williams warm 4-note ascending chime (523, 659, 784, 1046 Hz)
      [523, 659, 784, 1046].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'triangle'; osc.frequency.setValueAtTime(f, now + i * 0.04);
        g.gain.setValueAtTime(0.70, now + i * 0.04);
        g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.04);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.04); osc.stop(now + (i + 1) * 0.045);
      });
      break;
    }

    case 'BERZERK-ZAP': {
      // Berzerk Laser Gun: TSI S14001A digital crunch laser: 3200 Hz down to 320 Hz
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(3200, now);
      osc.frequency.exponentialRampToValueAtTime(320, now + 0.075);
      g.gain.setValueAtTime(0.80, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.075);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.08);
      break;
    }

    case 'BERZERK-ROB': {
      // Berzerk Evil Otto Bouncing: High spring bounce (1400 -> 2400 -> 1400 Hz triangle wave)
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(1400, now);
      osc.frequency.linearRampToValueAtTime(2400, now + 0.06);
      osc.frequency.linearRampToValueAtTime(1400, now + 0.12);
      g.gain.setValueAtTime(0.75, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.13);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.14);
      break;
    }

    case 'STARWAR-TIE': {
      // Star Wars (1983 Atari): TIE Fighter Screamer
      // Quad-POKEY screeching twin ion engine: 1850 Hz sawtooth with heavy 42 Hz pitch vibrato
      const osc = audioCtx.createOscillator(), lfo = audioCtx.createOscillator();
      const lfoG = audioCtx.createGain(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(1850, now);
      lfo.type = 'sawtooth'; lfo.frequency.setValueAtTime(42, now);
      lfoG.gain.setValueAtTime(160, now);
      lfo.connect(lfoG); lfoG.connect(osc.frequency);
      const flt = audioCtx.createBiquadFilter();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(1800, now); flt.Q.setValueAtTime(2.0, now);
      g.gain.setValueAtTime(0.80, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.45);
      osc.connect(flt); flt.connect(g); g.connect(filterNode);
      osc.start(now); lfo.start(now);
      osc.stop(now + 0.48); lfo.stop(now + 0.48);
      break;
    }

    case 'STARWAR-LAS': {
      // Star Wars X-Wing Quad Laser: 4 rapid laser chirps (3200 -> 380 Hz) spaced 22ms apart
      [0, 0.022, 0.044, 0.066].forEach(d => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'sawtooth'; osc.frequency.setValueAtTime(3200, now + d);
        osc.frequency.exponentialRampToValueAtTime(380, now + d + 0.045);
        g.gain.setValueAtTime(0.70, now + d);
        g.gain.exponentialRampToValueAtTime(0.01, now + d + 0.045);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + d); osc.stop(now + d + 0.05);
      });
      break;
    }

    case 'STARWAR-TRB': {
      // Star Wars Proton Torpedo: Sub-bass blast + laser drop
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(2200, now);
      osc.frequency.exponentialRampToValueAtTime(45, now + 0.25);
      g.gain.setValueAtTime(0.85, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.28);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.30);
      break;
    }

    case 'MISSILE-LCH': {
      // Missile Command ICBM Launch: Low rumble rising from 40 to 180 Hz with white noise trail
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(40, now);
      osc.frequency.exponentialRampToValueAtTime(180, now + 0.38);
      g.gain.setValueAtTime(0.70, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.40);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.42);

      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(220, now);
      gN.gain.setValueAtTime(0.50, now);
      gN.gain.exponentialRampToValueAtTime(0.01, now + 0.38);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.40);
      break;
    }

    case 'MISSILE-EXP': {
      // Missile Command Flak Explosion: Expanding blooming noise cloud decaying over 1.2s
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(1200, now); flt.Q.setValueAtTime(2.0, now);
      flt.frequency.exponentialRampToValueAtTime(35, now + 1.15);
      g.gain.setValueAtTime(0.95, now);
      g.gain.exponentialRampToValueAtTime(0.005, now + 1.20);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 1.25);
      break;
    }

    case 'BZONE-ENG': {
      // Battlezone Tank Diesel: 36 Hz square wave modulated at 10 Hz
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(36, now);
      const lfo = audioCtx.createOscillator(), lfoG = audioCtx.createGain();
      lfo.type = 'square'; lfo.frequency.setValueAtTime(10, now);
      lfoG.gain.setValueAtTime(0.5, now);
      lfo.connect(lfoG); lfoG.connect(g.gain);
      g.gain.setValueAtTime(0.65, now);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); lfo.start(now);
      osc.stop(now + 0.38); lfo.stop(now + 0.38);
      break;
    }

    case 'BZONE-CANN': {
      // Battlezone 120mm Tank Cannon: 75 Hz sub-thump + 600ms rolling bass rumble
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(180, now); flt.Q.setValueAtTime(2.5, now);
      flt.frequency.exponentialRampToValueAtTime(40, now + 0.55);
      gN.gain.setValueAtTime(0.95, now);
      gN.gain.exponentialRampToValueAtTime(0.01, now + 0.60);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.65);

      const osc = audioCtx.createOscillator(), gO = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(75, now);
      osc.frequency.exponentialRampToValueAtTime(28, now + 0.35);
      gO.gain.setValueAtTime(0.85, now);
      gO.gain.exponentialRampToValueAtTime(0.01, now + 0.38);
      osc.connect(gO); gO.connect(filterNode);
      osc.start(now); osc.stop(now + 0.40);
      break;
    }

    // =====================================================================
    // BANK 4: KONAMI, SEGA & 80s ACTION (1981–1987) · AY-3-8910, FM & VOTRAX
    // =====================================================================

    case 'FROG-H': {
      // Frogger (1981 Konami): Authentic Frog Hop: Konami Dual AY-3-8910 sharp ascending square chirp (320 Hz -> 840 Hz in 38ms)
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square';
      osc.frequency.setValueAtTime(320, now);
      osc.frequency.exponentialRampToValueAtTime(840, now + 0.038);
      g.gain.setValueAtTime(0.75, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.038);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.042);
      break;
    }

    case 'FROG-SPLASH': {
      // Frogger River Splash: Resonant bloop-plunk: 920 -> 320 -> 140 Hz + water splash noise
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(920, now);
      osc.frequency.exponentialRampToValueAtTime(320, now + 0.08);
      osc.frequency.exponentialRampToValueAtTime(140, now + 0.22);
      g.gain.setValueAtTime(0.80, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.24);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.26);

      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(1600, now); flt.Q.setValueAtTime(2.0, now);
      gN.gain.setValueAtTime(0.65, now);
      gN.gain.exponentialRampToValueAtTime(0.01, now + 0.22);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.24);
      break;
    }

    case 'FROG-TIME': {
      // Frogger Hurry Up Warning: Alternating 880 Hz and 1175 Hz square beeps every 50ms
      [0, 0.05, 0.10, 0.15].forEach((d, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(i % 2 === 0 ? 880 : 1175, now + d);
        g.gain.setValueAtTime(0.65, now + d);
        g.gain.exponentialRampToValueAtTime(0.01, now + d + 0.045);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + d); osc.stop(now + d + 0.05);
      });
      break;
    }

    case 'FROG-HOME': {
      // Frogger Home Landing: 3-note landing jingle: C5 (523), E5 (659), G5 (784)
      [523, 659, 784].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.06);
        g.gain.setValueAtTime(0.65, now + i * 0.06);
        g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.06);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.06); osc.stop(now + (i + 1) * 0.065);
      });
      break;
    }

    case 'FROG-SPLAT': {
      // Frogger Traffic Squish: Stepped AY-3-8910 sawtooth crunch (1250 -> 840 -> 520 -> 310 -> 140 Hz) + bandpass noise
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth';
      const steps = [1250, 840, 520, 310, 140];
      steps.forEach((f, idx) => {
        osc.frequency.setValueAtTime(f, now + idx * 0.025);
      });
      g.gain.setValueAtTime(0.85, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.16);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.18);

      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(800, now); flt.Q.setValueAtTime(2.5, now);
      gN.gain.setValueAtTime(0.90, now);
      gN.gain.exponentialRampToValueAtTime(0.01, now + 0.22);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.24);
      break;
    }

    case 'GYRUSS-WARP': {
      // Gyruss 5x PSG Hyper Warp: Dual detuned sawtooth sweeps (140 -> 2800 Hz)
      const osc1 = audioCtx.createOscillator(), osc2 = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc1.type = 'sawtooth'; osc1.frequency.setValueAtTime(140, now);
      osc1.frequency.exponentialRampToValueAtTime(2800, now + 0.40);
      osc2.type = 'sawtooth'; osc2.frequency.setValueAtTime(144, now);
      osc2.frequency.exponentialRampToValueAtTime(2850, now + 0.40);
      g.gain.setValueAtTime(0.65, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.42);
      osc1.connect(g); osc2.connect(g); g.connect(filterNode);
      osc1.start(now); osc2.start(now);
      osc1.stop(now + 0.44); osc2.stop(now + 0.44);
      break;
    }

    case 'GYRUSS-LAS': {
      // Gyruss Orbital Twin Laser: Dual square chirps at 2200 and 2400 Hz sweeping to 480 Hz
      const osc1 = audioCtx.createOscillator(), osc2 = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc1.type = 'square'; osc1.frequency.setValueAtTime(2200, now);
      osc1.frequency.exponentialRampToValueAtTime(480, now + 0.05);
      osc2.type = 'square'; osc2.frequency.setValueAtTime(2400, now);
      osc2.frequency.exponentialRampToValueAtTime(520, now + 0.05);
      g.gain.setValueAtTime(0.70, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.055);
      osc1.connect(g); osc2.connect(g); g.connect(filterNode);
      osc1.start(now); osc2.start(now);
      osc1.stop(now + 0.06); osc2.stop(now + 0.06);
      break;
    }

    case 'GYRUSS-DIV': {
      // Gyruss Drone Dive Siren: 1200 down to 260 Hz with 26 Hz vibrato
      const osc = audioCtx.createOscillator(), lfo = audioCtx.createOscillator();
      const lfoG = audioCtx.createGain(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(1200, now);
      osc.frequency.exponentialRampToValueAtTime(260, now + 0.35);
      lfo.type = 'square'; lfo.frequency.setValueAtTime(26, now);
      lfoG.gain.setValueAtTime(95, now);
      lfo.connect(lfoG); lfoG.connect(osc.frequency);
      g.gain.setValueAtTime(0.70, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.36);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); lfo.start(now);
      osc.stop(now + 0.38); lfo.stop(now + 0.38);
      break;
    }

    case 'GYRUSS-EXP': {
      // Gyruss Core Explosion: 5x PSG dual-sawtooth explode + noise blast + sub-bass thud
      const t = now;
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'bandpass';
      flt.frequency.setValueAtTime(1200, t);
      flt.frequency.exponentialRampToValueAtTime(80, t + 0.58);
      gN.gain.setValueAtTime(0.95, t);
      gN.gain.exponentialRampToValueAtTime(0.01, t + 0.60);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(t); noise.stop(t + 0.62);

      const osc = audioCtx.createOscillator(), gO = audioCtx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(260, t);
      osc.frequency.exponentialRampToValueAtTime(32, t + 0.55);
      gO.gain.setValueAtTime(0.85, t);
      gO.gain.exponentialRampToValueAtTime(0.01, t + 0.58);
      osc.connect(gO); gO.connect(filterNode);
      osc.start(t); osc.stop(t + 0.60);
      break;
    }

    case 'CLIMB-STEP': {
      // Crazy Climber Window Step: Dual square clicks at 220 and 330 Hz
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(220, now);
      osc.frequency.setValueAtTime(330, now + 0.02);
      g.gain.setValueAtTime(0.65, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.04);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.045);
      break;
    }

    case 'CLIMB-POT': {
      // Crazy Climber Flowerpot Smash: Bandpass noise crash (1800 Hz) + 620 -> 120 Hz square thud
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(1800, now); flt.Q.setValueAtTime(3.0, now);
      flt.frequency.exponentialRampToValueAtTime(350, now + 0.22);
      gN.gain.setValueAtTime(0.90, now);
      gN.gain.exponentialRampToValueAtTime(0.01, now + 0.24);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.26);

      const osc = audioCtx.createOscillator(), gO = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(620, now);
      osc.frequency.exponentialRampToValueAtTime(120, now + 0.15);
      gO.gain.setValueAtTime(0.65, now);
      gO.gain.exponentialRampToValueAtTime(0.01, now + 0.16);
      osc.connect(gO); gO.connect(filterNode);
      osc.start(now); osc.stop(now + 0.18);
      break;
    }

    case 'CLIMB-ELEC': {
      // Crazy Climber Neon Sign Shock: 60 Hz hum + 120 Hz saw with 30 Hz tremolo
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(120, now);
      const lfo = audioCtx.createOscillator(), lfoG = audioCtx.createGain();
      lfo.type = 'square'; lfo.frequency.setValueAtTime(30, now);
      lfoG.gain.setValueAtTime(0.5, now);
      lfo.connect(lfoG); lfoG.connect(g.gain);
      g.gain.setValueAtTime(0.70, now);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); lfo.start(now);
      osc.stop(now + 0.32); lfo.stop(now + 0.32);
      break;
    }

    case 'CLIMB-KONG': {
      // Crazy Climber Ape Punch: Heavy fist impact thud (120 -> 40 Hz + lowpass noise)
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(120, now);
      osc.frequency.exponentialRampToValueAtTime(40, now + 0.16);
      g.gain.setValueAtTime(0.90, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.18);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.20);
      break;
    }

    case 'CLIMB-WIN': {
      // Crazy Climber Helicopter Rescue: Triumphant AY-3 victory fanfare: C5, D5, E5, G5, C6
      [523, 587, 659, 784, 1046].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.08);
        g.gain.setValueAtTime(0.65, now + i * 0.08);
        g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.08);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.08); osc.stop(now + (i + 1) * 0.085);
      });
      break;
    }

    case 'QBERT-HOP': {
      // Q*bert (1982 Gottlieb): Pyramid Boing: Gottlieb DAC spring boing: 160 -> 540 -> 280 Hz
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(160, now);
      osc.frequency.exponentialRampToValueAtTime(540, now + 0.08);
      osc.frequency.exponentialRampToValueAtTime(280, now + 0.16);
      g.gain.setValueAtTime(0.80, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.17);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.18);
      break;
    }

    case 'QBERT-CURSE': {
      // Q*bert @!#?@! Swear Curse: Direct dispatch to authentic digitized VOTRAX SC-01 speech recording!
      if (typeof playArcadeSpeechSample === 'function') {
        playArcadeSpeechSample('VOX_QBERT');
      } else {
        const formants = [450, 1150, 2200, 380, 890, 1600, 520, 1400];
        formants.forEach((f, i) => {
          const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
          osc.type = 'sawtooth'; osc.frequency.setValueAtTime(f, now + i * 0.045);
          g.gain.setValueAtTime(0.65, now + i * 0.045);
          g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.045);
          osc.connect(g); g.connect(filterNode);
          osc.start(now + i * 0.045); osc.stop(now + (i + 1) * 0.05);
        });
      }
      break;
    }

    case 'QBERT-DISC': {
      // Q*bert Flying Disc: 880 Hz sine wave with 35 Hz FM rising
      const osc = audioCtx.createOscillator(), lfo = audioCtx.createOscillator();
      const lfoG = audioCtx.createGain(), g = audioCtx.createGain();
      osc.type = 'sine'; osc.frequency.setValueAtTime(880, now);
      osc.frequency.exponentialRampToValueAtTime(1400, now + 0.35);
      lfo.type = 'sine'; lfo.frequency.setValueAtTime(35, now);
      lfoG.gain.setValueAtTime(120, now);
      lfo.connect(lfoG); lfoG.connect(osc.frequency);
      g.gain.setValueAtTime(0.70, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); lfo.start(now);
      osc.stop(now + 0.38); lfo.stop(now + 0.38);
      break;
    }

    case 'QBERT-FALL': {
      // Q*bert Plunge Whistle: Smooth logarithmic slide whistle plunging from 1650 down to 110 Hz over 850ms
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(1650, now);
      osc.frequency.exponentialRampToValueAtTime(110, now + 0.85);
      g.gain.setValueAtTime(0.80, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.85);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.88);
      break;
    }

    case 'OUTRUN-REV': {
      // OutRun (1986 Sega): Ferrari Testarossa Engine Rev (YM2151 FM brassy saw engine revving from 65 to 260 Hz)
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(65, now);
      osc.frequency.exponentialRampToValueAtTime(260, now + 0.32);
      const lfo = audioCtx.createOscillator(), lfoG = audioCtx.createGain();
      lfo.type = 'sawtooth'; lfo.frequency.setValueAtTime(32, now);
      lfoG.gain.setValueAtTime(25, now);
      lfo.connect(lfoG); lfoG.connect(osc.frequency);
      g.gain.setValueAtTime(0.75, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); lfo.start(now);
      osc.stop(now + 0.36); lfo.stop(now + 0.36);
      break;
    }

    case 'OUTRUN-SKID': {
      // OutRun Tire Screech: Resonant FM noise modulation (2600 -> 1700 Hz) with tire squeal resonance
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(2600, now); flt.Q.setValueAtTime(5.0, now);
      flt.frequency.exponentialRampToValueAtTime(1700, now + 0.30);
      gN.gain.setValueAtTime(0.85, now);
      gN.gain.exponentialRampToValueAtTime(0.01, now + 0.32);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.34);

      const osc = audioCtx.createOscillator(), gO = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(1850, now);
      osc.frequency.exponentialRampToValueAtTime(1350, now + 0.30);
      gO.gain.setValueAtTime(0.40, now);
      gO.gain.exponentialRampToValueAtTime(0.01, now + 0.32);
      osc.connect(gO); gO.connect(filterNode);
      osc.start(now); osc.stop(now + 0.34);
      break;
    }

    case 'OUTRUN-PASS': {
      // OutRun Checkpoint: Bright sparkling Sega FM bell chord (880 Hz + 1760 Hz + 2640 Hz)
      [880, 1760, 2640].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'sine'; osc.frequency.setValueAtTime(f, now);
        g.gain.setValueAtTime(0.65 / (i + 1), now);
        g.gain.exponentialRampToValueAtTime(0.001, now + 0.45);
        osc.connect(g); g.connect(filterNode);
        osc.start(now); osc.stop(now + 0.48);
      });
      break;
    }

    case 'SHINOBI-STAR': {
      // Shinobi Shuriken: FM blade whoosh + metallic hit
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(1800, now);
      osc.frequency.exponentialRampToValueAtTime(400, now + 0.06);
      g.gain.setValueAtTime(0.65, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.065);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.07);
      break;
    }

    case 'SHINOBI-HIT': {
      // Shinobi Katana Slash: Sharp blade slice noise + flesh impact thud
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(1200, now); flt.Q.setValueAtTime(2.2, now);
      gN.gain.setValueAtTime(0.85, now);
      gN.gain.exponentialRampToValueAtTime(0.01, now + 0.12);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.14);

      const osc = audioCtx.createOscillator(), gO = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(150, now);
      osc.frequency.exponentialRampToValueAtTime(45, now + 0.10);
      gO.gain.setValueAtTime(0.80, now);
      gO.gain.exponentialRampToValueAtTime(0.01, now + 0.12);
      osc.connect(gO); gO.connect(filterNode);
      osc.start(now); osc.stop(now + 0.14);
      break;
    }

    case 'GHOSTS-JMP': {
      // Ghosts 'n Goblins Armor Jump: Capcom YM2203 metallic clank (850 + 1380 Hz)
      [850, 1380].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.035);
        g.gain.setValueAtTime(0.60, now + i * 0.035);
        g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.035);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.035); osc.stop(now + (i + 1) * 0.04);
      });
      break;
    }

    case 'GHOSTS-ARM': {
      // Ghosts 'n Goblins Armor Shatter: Cascading noise burst + crumbling metal fragments
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'highpass'; flt.frequency.setValueAtTime(1600, now);
      g.gain.setValueAtTime(0.90, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.26);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.28);
      break;
    }

    case 'GONGA-COIN': {
      // Sega Classic Arcade Coin: Sparkling FM bell (1046 Hz -> 2093 Hz)
      [1046, 2093].forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'sine'; osc.frequency.setValueAtTime(f, now + i * 0.06);
        g.gain.setValueAtTime(0.70, now + i * 0.06);
        g.gain.exponentialRampToValueAtTime(0.001, now + (i === 0 ? 0.06 : 0.40));
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.06); osc.stop(now + (i === 0 ? 0.065 : 0.42));
      });
      break;
    }

    // =====================================================================
    // AUXILIARY & IN-GAME GAMEPLAY SOUND EFFECTS
    // =====================================================================

    case 'CLIMB-FALL': {
      // Crazy Climber Plunge Whistle
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'sine'; osc.frequency.setValueAtTime(1400, now);
      osc.frequency.exponentialRampToValueAtTime(180, now + 0.25);
      g.gain.setValueAtTime(0.75, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.26);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.28);
      break;
    }

    case 'CLIMB-SPLAT': {
      // Crazy Climber Pavement Splat
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'lowpass'; flt.frequency.setValueAtTime(600, now);
      g.gain.setValueAtTime(0.85, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.20);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.22);
      break;
    }

    case 'CLIMB-SLIP': {
      // Crazy Climber Window Slip Chirp
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(520, now);
      osc.frequency.exponentialRampToValueAtTime(180, now + 0.08);
      g.gain.setValueAtTime(0.70, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.08);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.085);
      break;
    }

    case 'DK-INTRO': {
      // Donkey Kong 8035 DAC Level Intro Fanfare ("How High Can You Get?")
      const introNotes = [
        { f: 587, d: 0.08 }, { f: 740, d: 0.08 }, { f: 880, d: 0.08 },
        { f: 1175, d: 0.15 }, { f: 1109, d: 0.08 }, { f: 988, d: 0.08 },
        { f: 880, d: 0.15 }, { f: 784, d: 0.08 }, { f: 740, d: 0.08 },
        { f: 659, d: 0.15 }, { f: 587, d: 0.28 }
      ];
      let tOffset = 0;
      introNotes.forEach(n => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(n.f, now + tOffset);
        g.gain.setValueAtTime(0.65, now + tOffset);
        g.gain.exponentialRampToValueAtTime(0.01, now + tOffset + n.d);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + tOffset); osc.stop(now + tOffset + n.d + 0.01);
        tOffset += n.d;
      });
      break;
    }

    case 'DK-ROLL': {
      // Donkey Kong rhythmic wooden barrel rolling tap
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(65, now);
      osc.frequency.exponentialRampToValueAtTime(30, now + 0.04);
      g.gain.setValueAtTime(0.60, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.045);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.05);
      break;
    }

    case 'DK-HAMMER-TUNE': {
      // Donkey Kong (1981 Nintendo): Authentic 16-note rapid bouncy hammer ragtime arpeggio
      const notes = [523, 392, 523, 392, 659, 523, 659, 523, 698, 523, 698, 523, 587, 494, 587, 494];
      const noteDur = 0.048;
      notes.forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * noteDur);
        g.gain.setValueAtTime(0.65, now + i * noteDur);
        g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * noteDur - 0.004);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * noteDur); osc.stop(now + (i + 1) * noteDur);
      });
      break;
    }

    case 'DK-DEATH': {
      // Donkey Kong (1981 Nintendo): Mario Death Chime & Halo Angel Pings
      // 8 descending chromatic steps (G5 down to C5) followed by 3 high halo angel pings (E6, G#6, B6)
      const descNotes = [784, 740, 698, 659, 622, 587, 554, 523];
      const stepDur = 0.055;
      descNotes.forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * stepDur);
        g.gain.setValueAtTime(0.65, now + i * stepDur);
        g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * stepDur);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * stepDur); osc.stop(now + (i + 1) * stepDur + 0.005);
      });
      const haloPings = [
        { f: 1318, t: 0.50 }, // E6
        { f: 1661, t: 0.62 }, // G#6
        { f: 1975, t: 0.74 }  // B6
      ];
      haloPings.forEach(p => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(p.f, now + p.t);
        g.gain.setValueAtTime(0.50, now + p.t);
        g.gain.exponentialRampToValueAtTime(0.01, now + p.t + 0.11);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + p.t); osc.stop(now + p.t + 0.12);
      });
      break;
    }

    case 'DK-FIRE': {
      // Donkey Kong Fireball sizzle
      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), g = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(1400, now); flt.Q.setValueAtTime(3.0, now);
      g.gain.setValueAtTime(0.60, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.10);
      noise.connect(flt); flt.connect(g); g.connect(filterNode);
      noise.start(now); noise.stop(now + 0.12);
      break;
    }

    case 'DK-GAMEOVER': {
      // Donkey Kong Game Over Fanfare
      const notes = [392, 349, 330, 294, 262, 247, 196];
      notes.forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.09);
        g.gain.setValueAtTime(0.70, now + i * 0.09);
        g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.09);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.09); osc.stop(now + (i + 1) * 0.095);
      });
      break;
    }

    case 'GALAGA-FIRE': {
      // Galaga (1981 Namco): Authentic Dual WSG Plasma Laser Chirp
      // Voice 1 (1760 -> 440 Hz) + Voice 2 (880 -> 220 Hz) + high-frequency transient click
      const osc1 = audioCtx.createOscillator(), g1 = audioCtx.createGain();
      osc1.type = 'square'; osc1.frequency.setValueAtTime(1760, now);
      osc1.frequency.exponentialRampToValueAtTime(440, now + 0.048);
      g1.gain.setValueAtTime(0.65, now);
      g1.gain.exponentialRampToValueAtTime(0.01, now + 0.048);
      osc1.connect(g1); g1.connect(filterNode);
      osc1.start(now); osc1.stop(now + 0.052);

      const osc2 = audioCtx.createOscillator(), g2 = audioCtx.createGain();
      osc2.type = 'square'; osc2.frequency.setValueAtTime(880, now);
      osc2.frequency.exponentialRampToValueAtTime(220, now + 0.048);
      g2.gain.setValueAtTime(0.50, now);
      g2.gain.exponentialRampToValueAtTime(0.01, now + 0.048);
      osc2.connect(g2); g2.connect(filterNode);
      osc2.start(now); osc2.stop(now + 0.052);

      const noise = createNoiseSource(), flt = audioCtx.createBiquadFilter(), gN = audioCtx.createGain();
      flt.type = 'bandpass'; flt.frequency.setValueAtTime(2500, now); flt.Q.setValueAtTime(2.0, now);
      gN.gain.setValueAtTime(0.40, now);
      gN.gain.exponentialRampToValueAtTime(0.01, now + 0.012);
      noise.connect(flt); flt.connect(gN); gN.connect(filterNode);
      noise.start(now); noise.stop(now + 0.015);
      break;
    }

    case 'GALAGA-INTRO': {
      // Galaga (1981 Namco): Authentic 17-note Stage Intro Theme
      const introNotes = [
        587, 494, 392, 587, 494, 392,
        659, 523, 392, 659, 523, 392,
        587, 494, 392, 587, 784
      ];
      const stepDur = 0.065;
      introNotes.forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(f, now + i * stepDur);
        const dur = (i === introNotes.length - 1) ? 0.22 : 0.058;
        g.gain.setValueAtTime(0.65, now + i * stepDur);
        g.gain.exponentialRampToValueAtTime(0.01, now + i * stepDur + dur);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * stepDur); osc.stop(now + i * stepDur + dur + 0.01);
      });
      break;
    }

    case 'AST-THUMP-LO': {
      // Asteroids Low Heartbeat Thump
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(75, now);
      osc.frequency.exponentialRampToValueAtTime(35, now + 0.06);
      g.gain.setValueAtTime(0.85, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.065);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.07);
      break;
    }

    case 'AST-THUMP-HI': {
      // Asteroids High Heartbeat Thump
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(105, now);
      osc.frequency.exponentialRampToValueAtTime(45, now + 0.06);
      g.gain.setValueAtTime(0.85, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.065);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.07);
      break;
    }

    case 'TEM-SPIN': {
      // Tempest Blaster Rotary Tick
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(1200, now);
      osc.frequency.exponentialRampToValueAtTime(400, now + 0.02);
      g.gain.setValueAtTime(0.55, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.022);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.025);
      break;
    }

    case 'FROG-FANFARE': {
      // Frogger Stage Clear Fanfare
      const notes = [523, 659, 784, 1046];
      notes.forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'square'; osc.frequency.setValueAtTime(f, now + i * 0.06);
        g.gain.setValueAtTime(0.65, now + i * 0.06);
        g.gain.exponentialRampToValueAtTime(0.01, now + (i + 1) * 0.06);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + i * 0.06); osc.stop(now + (i + 1) * 0.065);
      });
      break;
    }

    case 'GYRUSS-TUNE': {
      // Gyruss (1983 Konami): Stage Intro Toccata Flourish
      const toccataNotes = [587, 523, 587, 440, 523, 392, 440, 370, 294];
      const durs = [0.08, 0.08, 0.20, 0.08, 0.08, 0.08, 0.16, 0.08, 0.28];
      let tOff = 0;
      toccataNotes.forEach((f, i) => {
        const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
        osc.type = 'sawtooth'; osc.frequency.setValueAtTime(f, now + tOff);
        g.gain.setValueAtTime(0.58, now + tOff);
        g.gain.exponentialRampToValueAtTime(0.01, now + tOff + durs[i]);
        osc.connect(g); g.connect(filterNode);
        osc.start(now + tOff); osc.stop(now + tOff + durs[i] + 0.01);
        tOff += durs[i];
      });
      break;
    }

    case 'GYRUSS-BGM': {
      // Gyruss (1983 Konami): Authentic 5x PSG J.S. Bach Toccata & Fugue in D minor BWV 565
      if (typeof _gyrussBgmStep === 'undefined') _gyrussBgmStep = 0;
      const step = (typeof gyrussGame !== 'undefined' && gyrussGame.bgmStep !== undefined)
        ? gyrussGame.bgmStep
        : (_gyrussBgmStep = (_gyrussBgmStep + 1) % 42);
      const gyrussMelody = [
        587, 523, 587, 0, 494, 440, 392, 370, 392, 0,
        440, 0, 587, 0, 587, 523, 587, 440, 523, 392,
        440, 370, 392, 440, 494, 523, 587, 659, 698, 659,
        587, 523, 494, 440, 392, 370, 294, 330, 370, 440,
        587, 0
      ];
      const gyrussBass = [
        147, 147, 147, 0, 147, 147, 147, 147, 147, 0,
        220, 0, 147, 0, 147, 147, 147, 220, 147, 196,
        220, 185, 196, 220, 247, 262, 294, 330, 349, 330,
        294, 262, 247, 220, 196, 185, 147, 165, 185, 220,
        294, 0
      ];
      const mNote = gyrussMelody[Math.abs(step) % 42];
      const bNote = gyrussBass[Math.abs(step) % 42];
      if (mNote > 0) {
        const oscM = audioCtx.createOscillator(), gM = audioCtx.createGain();
        oscM.type = 'sawtooth'; oscM.frequency.setValueAtTime(mNote, now);
        gM.gain.setValueAtTime(0.50, now);
        gM.gain.exponentialRampToValueAtTime(0.01, now + 0.082);
        oscM.connect(gM); gM.connect(filterNode);
        oscM.start(now); oscM.stop(now + 0.088);
      }
      if (bNote > 0) {
        const oscB = audioCtx.createOscillator(), gB = audioCtx.createGain();
        oscB.type = 'square'; oscB.frequency.setValueAtTime(bNote, now);
        gB.gain.setValueAtTime(0.42, now);
        gB.gain.exponentialRampToValueAtTime(0.01, now + 0.082);
        oscB.connect(gB); gB.connect(filterNode);
        oscB.start(now); oscB.stop(now + 0.088);
      }
      break;
    }

    case 'DK-BGM': {
      // Donkey Kong (1981 Nintendo): Authentic 25M Walking Bass Ostinato (8035 DAC)
      // 4-step chromatic walking bass: F#2 (92.5), G2 (98.0), G#2 (103.8), A2 (110.0)
      if (typeof _dkBgmStep === 'undefined') _dkBgmStep = 0;
      const step = (typeof dkongGame !== 'undefined' && dkongGame.bgmStep !== undefined)
        ? dkongGame.bgmStep
        : (_dkBgmStep = (_dkBgmStep + 1) % 4);
      const dkBassPitches = [92.5, 98.0, 103.8, 110.0];
      const pitch = dkBassPitches[Math.abs(step) % 4];
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square';
      osc.frequency.setValueAtTime(pitch, now);
      g.gain.setValueAtTime(0.70, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.082);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.088);
      break;
    }

    case 'FROG-BGM': {
      // Frogger (1981 Konami): Authentic Dual AY-3-8910 BGM ("Inu no Omawarisan" / "The Frog Song")
      if (typeof _frogBgmStep === 'undefined') _frogBgmStep = 0;
      const step = (typeof froggerGame !== 'undefined' && froggerGame.bgmStep !== undefined)
        ? froggerGame.bgmStep
        : (_frogBgmStep = (_frogBgmStep + 1) % 32);
      const frogMelody = [
        523, 523, 587, 659, 659, 587, 523, 0,
        659, 659, 698, 784, 784, 698, 659, 0,
        784, 784, 880, 784, 698, 659, 587, 0,
        523, 587, 659, 698, 784, 587, 523, 0
      ];
      const frogBass = [
        262, 196, 262, 196, 330, 262, 330, 262,
        330, 262, 330, 262, 392, 262, 392, 262,
        392, 262, 392, 262, 349, 262, 294, 196,
        262, 294, 330, 349, 392, 294, 262, 196
      ];
      const mNote = frogMelody[Math.abs(step) % 32];
      const bNote = frogBass[Math.abs(step) % 32];
      if (mNote > 0) {
        const oscM = audioCtx.createOscillator(), gM = audioCtx.createGain();
        oscM.type = 'square'; oscM.frequency.setValueAtTime(mNote, now);
        gM.gain.setValueAtTime(0.55, now);
        gM.gain.exponentialRampToValueAtTime(0.01, now + 0.082);
        oscM.connect(gM); gM.connect(filterNode);
        oscM.start(now); oscM.stop(now + 0.088);
      }
      if (bNote > 0) {
        const oscB = audioCtx.createOscillator(), gB = audioCtx.createGain();
        oscB.type = 'square'; oscB.frequency.setValueAtTime(bNote, now);
        gB.gain.setValueAtTime(0.42, now);
        gB.gain.exponentialRampToValueAtTime(0.01, now + 0.082);
        oscB.connect(gB); gB.connect(filterNode);
        oscB.start(now); oscB.stop(now + 0.088);
      }
      break;
    }

    case 'CLIMB-BGM': {
      // Crazy Climber (1980 Nichibutsu): Authentic Henry Mancini "Baby Elephant Walk" Swing Strut
      if (typeof _climbBgmStep === 'undefined') _climbBgmStep = 0;
      const step = (typeof climberState !== 'undefined' && climberState.bgmStep !== undefined)
        ? climberState.bgmStep
        : (_climbBgmStep = (_climbBgmStep + 1) % 28);
      const climbMelody = [
        294, 330, 349, 370, 392, 0, 392, 0,
        440, 392, 349, 294, 330, 0, 294, 330,
        349, 370, 392, 440, 523, 440, 392, 349,
        330, 294, 262, 0
      ];
      const climbBass = [
        147, 220, 147, 220, 196, 262, 196, 262,
        220, 196, 175, 147, 165, 220, 147, 220,
        147, 220, 196, 220, 262, 220, 196, 175,
        165, 147, 131, 196
      ];
      const mNote = climbMelody[Math.abs(step) % 28];
      const bNote = climbBass[Math.abs(step) % 28];
      if (mNote > 0) {
        const oscM = audioCtx.createOscillator(), gM = audioCtx.createGain();
        oscM.type = 'square'; oscM.frequency.setValueAtTime(mNote, now);
        gM.gain.setValueAtTime(0.50, now);
        gM.gain.exponentialRampToValueAtTime(0.01, now + 0.088);
        oscM.connect(gM); gM.connect(filterNode);
        oscM.start(now); oscM.stop(now + 0.095);
      }
      if (bNote > 0) {
        const oscB = audioCtx.createOscillator(), gB = audioCtx.createGain();
        oscB.type = 'square'; oscB.frequency.setValueAtTime(bNote, now);
        gB.gain.setValueAtTime(0.45, now);
        gB.gain.exponentialRampToValueAtTime(0.01, now + 0.088);
        oscB.connect(gB); gB.connect(filterNode);
        oscB.start(now); oscB.stop(now + 0.095);
      }
      break;
    }

    case 'GALAGA-BGM': {
      // Galaga (1981 Namco): Authentic WSG Space Fleet Formation Hum (8-step cycle)
      if (typeof _galagaBgmStep === 'undefined') _galagaBgmStep = 0;
      const step = (typeof galagaGame !== 'undefined' && galagaGame.bgmStep !== undefined)
        ? galagaGame.bgmStep
        : (_galagaBgmStep = (_galagaBgmStep + 1) % 8);
      const fleetPitches = [110, 110, 147, 147, 131, 131, 123, 123];
      const pitch = fleetPitches[Math.abs(step) % 8];
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(pitch, now);
      g.gain.setValueAtTime(0.55, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.11);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.12);

      const oscSub = audioCtx.createOscillator(), gSub = audioCtx.createGain();
      oscSub.type = 'triangle'; oscSub.frequency.setValueAtTime(55, now);
      gSub.gain.setValueAtTime(0.35, now);
      gSub.gain.exponentialRampToValueAtTime(0.01, now + 0.11);
      oscSub.connect(gSub); gSub.connect(filterNode);
      oscSub.start(now); oscSub.stop(now + 0.12);
      break;
    }

    case 'GALAGA-CHALLENGE-BGM': {
      // Galaga (1981 Namco): Authentic Challenging Stage BGM (28 steps)
      if (typeof _galagaChallStep === 'undefined') _galagaChallStep = 0;
      const step = (typeof galagaGame !== 'undefined' && galagaGame.bgmStep !== undefined)
        ? galagaGame.bgmStep
        : (_galagaChallStep = (_galagaChallStep + 1) % 28);
      const challMelody = [
        587, 587, 784, 587, 880, 784, 587, 659,
        587, 523, 587, 659, 784, 880, 988, 880,
        784, 659, 784, 880, 988, 1046, 988, 880,
        784, 659, 587, 523
      ];
      const note = challMelody[Math.abs(step) % 28];
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'square'; osc.frequency.setValueAtTime(note, now);
      g.gain.setValueAtTime(0.55, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.082);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.088);
      break;
    }

    case 'TEM-BGM': {
      // Tempest (1981 Atari): Authentic Atari POKEY Polyphonic Vector Pulse Arpeggio
      if (typeof _temBgmStep === 'undefined') _temBgmStep = 0;
      const step = (typeof tempestGame !== 'undefined' && tempestGame.bgmStep !== undefined)
        ? tempestGame.bgmStep
        : (_temBgmStep = (_temBgmStep + 1) % 8);
      const temPitches = [165, 220, 277, 330, 440, 554, 659, 880];
      const pitch = temPitches[Math.abs(step) % 8];
      const osc1 = audioCtx.createOscillator(), osc2 = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc1.type = 'sawtooth'; osc1.frequency.setValueAtTime(pitch, now);
      osc2.type = 'square'; osc2.frequency.setValueAtTime(pitch * 1.5, now);
      g.gain.setValueAtTime(0.48, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.082);
      osc1.connect(g); osc2.connect(g); g.connect(filterNode);
      osc1.start(now); osc2.start(now);
      osc1.stop(now + 0.088); osc2.stop(now + 0.088);
      break;
    }

    default: {
      // Clean fallback beep if unknown
      const osc = audioCtx.createOscillator(), g = audioCtx.createGain();
      osc.type = 'triangle'; osc.frequency.setValueAtTime(440, now);
      g.gain.setValueAtTime(0.40, now);
      g.gain.exponentialRampToValueAtTime(0.01, now + 0.10);
      osc.connect(g); g.connect(filterNode);
      osc.start(now); osc.stop(now + 0.12);
      break;
    }
  }
}
'''

if __name__ == "__main__":
    print(f"Generated {len(get_sfx_banks_js())} bytes of SFX Banks JS.")
    print(f"Generated {len(get_play_arcade_sfx_js())} bytes of playArcadeSfx JS.")
