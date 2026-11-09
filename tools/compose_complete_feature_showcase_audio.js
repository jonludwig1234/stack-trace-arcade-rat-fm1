#!/usr/bin/env node
/**
 * M-VAVE FM-1: Complete Feature-by-Feature & Sound-by-Sound Audio Producer (120.0s Stereo 44.1kHz)
 *
 * 1. Renders the 100% authentic Foreground Firmware Audio directly inside Headless Chrome's
 *    OfflineAudioContext using the actual `fm1_pacman_preview.html` Web Audio functions:
 *    - `playAlbumStartupChime()` & `playStartupChime()`
 *    - `playArcadeSfx()` (all 8 arcade games' authentic BGMs & SFX + 32 highlighted soundboard pads across all 4 banks)
 *    - `triggerSynthVoice()` (all 5 Synth Studio sound chips, 4 envelopes, ARP, LFO & filter sweeps)
 *    - `playTrackerVoice()` & `playArcadeDrum()` (all 8 built-in 16-Step Tracker Patterns)
 *    - `playTrackNote()` (all 4 multi-track Demo Jukebox songs)
 * 2. Decodes all 8 authentic 1980s Vintage Speech ROM samples (`SPEECH_SAMPLES_B64`).
 * 3. Synthesizes a lush, multi-movement Stereo Synthwave & Chiptune Background Soundtrack (`demo_bgm_music.wav`)
 *    featuring polyphonic 6-Op FM & warm analog supersaw chords, soaring dual-chip melodies with vibrato & portamento,
 *    60Hz chiptune chord arpeggiators, resonant 24dB/oct SVF slap bass, and punchy studio drums with fills.
 * 4. Mixes the Background Soundtrack (`demo_bgm_music.wav`) with the Foreground Firmware Showcase using a
 *    studio Sidechain Ducking Compressor so the background music carries the energy while automatically ducking
 *    whenever an individual SFX pad, Speech ROM, Synth solo, Tracker pattern, or Jukebox song is showcased.
 */

const { spawn, execFileSync } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');
const { composeMasterpieceBgm } = require('./bgm_studio_engine');

const PROJECT_ROOT = path.resolve(__dirname, '..');
const WEB_DIR = path.join(PROJECT_ROOT, 'web');
const SPEECH_PY = path.join(__dirname, 'speech_sample_engine.py');
const FFMPEG = '/home/jon/.local/bin/ffmpeg';

const SR = 44100;
const DURATION = 120.0;
const TOTAL_SAMPLES = Math.floor(SR * DURATION);

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function getWsUrl(port) {
  return new Promise((resolve, reject) => {
    const req = http.get(`http://127.0.0.1:${port}/json/version`, (res) => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => {
        try {
          const j = JSON.parse(d);
          if (j.webSocketDebuggerUrl) resolve(j.webSocketDebuggerUrl);
          else reject(new Error('No ws'));
        } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
  });
}

// ============================================================================
// 1. MASTER 48-FEATURE & 85-SOUND TIMELINE DEFINITION (120.0s)
// ============================================================================
const SCENES = [
  // CHAPTER 1: BOOT & ARCHITECTURE (0.0s - 6.0s)
  { id: 1, start: 0.0, end: 2.2, chapter: 'CH 1 · BOOT & ROM ARCHITECTURE', stateImg: 'state_01_album_splash.png', crtGame: 'pacman', title: 'FEATURE 01/48 · CHIPTUNES ALBUM SPLASH SCREEN', sub: 'Polyphonic Major-7th Chiptune Fanfare & Neon CRT Album Cover Art', chip: 'NAMCO WSG + 6-OP FM' },
  { id: 2, start: 2.2, end: 4.2, chapter: 'CH 1 · BOOT & ROM ARCHITECTURE', stateImg: 'state_02_arcade_splash.png', crtGame: 'pacman', title: 'FEATURE 02/48 · ARCADE RAT VECTOR BOOT SPLASH', sub: 'Analog Sub Drop + 8-Bit Power-Up Arpeggio & Hardware Diagnostics', chip: 'Z80 BUS + WSG' },
  { id: 3, start: 4.2, end: 6.0, chapter: 'CH 1 · BOOT & ROM ARCHITECTURE', stateImg: 'state_03_configurator.png', crtGame: 'galaga', title: 'FEATURE 03/48 · 93-GAME MAME ROM CONFIGURATOR', sub: 'Custom C Firmware Builder Supporting 93 Golden-Age Arcade ROM Sets', chip: 'ROM COMPILER' },

  // CHAPTER 2: PLAYABLE ARCADE VAULT — ALL 8 GAMES (6.0s - 30.0s)
  { id: 4, start: 6.0, end: 9.0, chapter: 'CH 2 · 8 PLAYABLE ARCADE CLASSICS', stateImg: 'state_04_game_pacman.png', crtGame: 'pacman', title: 'FEATURE 04/48 · PAC-MAN (1980 NAMCO · Z80 + WSG)', sub: 'Showcasing: Alternating Waka Chomp, Ghost Siren, Bonus Fruit & Ghost Eat', chip: 'NAMCO 3-VOICE WSG' },
  { id: 5, start: 9.0, end: 12.0, chapter: 'CH 2 · 8 PLAYABLE ARCADE CLASSICS', stateImg: 'state_05_game_cclimber.png', crtGame: 'cclimber', title: 'FEATURE 05/48 · CRAZY CLIMBER (1980 NICHIBUTSU)', sub: 'Showcasing: Skyscraper BGM, Window Step, Flowerpot Smash, Kong Roar & Chopper Win', chip: 'DUAL AY-3-8910 PSG' },
  { id: 6, start: 12.0, end: 15.0, chapter: 'CH 2 · 8 PLAYABLE ARCADE CLASSICS', stateImg: 'state_06_game_galaga.png', crtGame: 'galaga', title: 'FEATURE 06/48 · GALAGA (1981 NAMCO · DUAL Z80)', sub: 'Showcasing: Galaga Intro Fanfare, Dual Fighter Lasers, Tractor Beam & Stage Clear', chip: 'NAMCO WSG + NOISE' },
  { id: 7, start: 15.0, end: 18.0, chapter: 'CH 2 · 8 PLAYABLE ARCADE CLASSICS', stateImg: 'state_07_game_dkong.png', crtGame: 'dkong', title: 'FEATURE 07/48 · DONKEY KONG (1981 NINTENDO)', sub: 'Showcasing: Jumpman Walk, Spring Boing, Mallet Theme, Kong Roar & 25m Clear', chip: 'I8035 7-BIT DAC' },
  { id: 8, start: 18.0, end: 21.0, chapter: 'CH 2 · 8 PLAYABLE ARCADE CLASSICS', stateImg: 'state_08_game_frogger.png', crtGame: 'frogger', title: 'FEATURE 08/48 · FROGGER (1981 KONAMI · DUAL PSG)', sub: 'Showcasing: Frogger Theme Fanfare, Highway Hop, River Splash, Timer & Home Safe', chip: 'DUAL AY-3-8910 PSG' },
  { id: 9, start: 21.0, end: 24.0, chapter: 'CH 2 · 8 PLAYABLE ARCADE CLASSICS', stateImg: 'state_09_game_asteroids.png', crtGame: 'asteroids', title: 'FEATURE 09/48 · ASTEROIDS (1979 ATARI VECTOR)', sub: 'Showcasing: Low-Pass Ship Thrust, Photon Torpedo, Saucer Warble & Vector Bang', chip: 'ATARI POKEY / DISCRETE' },
  { id: 10, start: 24.0, end: 27.0, chapter: 'CH 2 · 8 PLAYABLE ARCADE CLASSICS', stateImg: 'state_10_game_tempest.png', crtGame: 'tempest', title: 'FEATURE 10/48 · TEMPEST (1981 ATARI COLOR VECTOR)', sub: 'Showcasing: Particle Gun, Flipper Trill, Spike Drill & Superzapper Filter Sweep', chip: 'DUAL ATARI POKEY' },
  { id: 11, start: 27.0, end: 30.0, chapter: 'CH 2 · 8 PLAYABLE ARCADE CLASSICS', stateImg: 'state_11_game_gyruss.png', crtGame: 'gyruss', title: 'FEATURE 11/48 · GYRUSS (1983 KONAMI · 5X PSG)', sub: 'Showcasing: J.S. Bach Toccata & Fugue in D Minor, Twin Cannon & Hyper Warp', chip: '5X AY-3-8910 STEREO' },

  // CHAPTER 3: HARDWARE DECK & SPECIAL MODES (30.0s - 39.0s)
  { id: 12, start: 30.0, end: 31.5, chapter: 'CH 3 · TACTICAL HARDWARE DECK', stateImg: 'state_12_hw_immortal.png', crtGame: 'pacman', title: 'FEATURE 12/48 · IMMORTAL INVINCIBILITY & LEVEL SKIP', sub: 'Hardware Deck Toggle for God-Mode Practice & Instant Stage Advancement', chip: 'Z80 RAM PATCHER' },
  { id: 13, start: 31.5, end: 33.0, chapter: 'CH 3 · TACTICAL HARDWARE DECK', stateImg: 'state_13_hw_zoom2x.png', crtGame: 'galaga', title: 'FEATURE 13/48 · 2X HARDWARE CRT SCREEN EXPANSION', sub: 'Instantaneous 2X CRT Bezel Zoom with Authentic Scanline Emulation', chip: '240x240 IPS ENGINE' },
  { id: 14, start: 33.0, end: 34.5, chapter: 'CH 3 · TACTICAL HARDWARE DECK', stateImg: 'state_14_hw_leaderboard.png', crtGame: 'dkong', title: 'FEATURE 14/48 · NVRAM ARCADE HALL OF FAME', sub: 'Persistent Top-5 High Score Leaderboards & 3-Letter Operator Initials Entry', chip: 'NVRAM STORAGE' },
  { id: 15, start: 34.5, end: 36.0, chapter: 'CH 3 · TACTICAL HARDWARE DECK', stateImg: 'state_15_hw_rewind.png', crtGame: 'frogger', title: 'FEATURE 15/48 · CIRCULAR FRAME-BUFFER TIME MACHINE', sub: 'Real-Time State Rewind Engine Stepping Backwards Through Z80 CPU Snapshots', chip: 'STATE RING BUFFER' },
  { id: 16, start: 36.0, end: 37.5, chapter: 'CH 3 · TACTICAL HARDWARE DECK', stateImg: 'state_16_hw_lissajous.png', crtGame: 'tempest', title: 'FEATURE 16/48 · X-Y LISSAJOUS VECTOR OSCILLOSCOPE', sub: 'Real-Time Stereo Phase & Harmonic Vector Visualizer on the 240x240 CRT', chip: 'VECTOR CRT SCOPE' },
  { id: 17, start: 37.5, end: 39.0, chapter: 'CH 3 · TACTICAL HARDWARE DECK', stateImg: 'state_17_hw_bender.png', crtGame: 'asteroids', title: 'FEATURE 17/48 · LIVE Z80 RAM CIRCUIT-BENDING', sub: 'Hardware Glitch Button Injecting Controlled Entropy into Video & Audio Registers', chip: 'CIRCUIT BENDER' },

  // CHAPTER 4: SYNTH STUDIO — ALL 5 SOUND CHIPS, ENVELOPES, ARP, LFO & KNOBS (39.0s - 54.0s)
  { id: 18, start: 39.0, end: 41.5, chapter: 'CH 4 · 5-CHIP SYNTHESIS STUDIO', stateImg: 'state_18_synth_wsg.png', crtGame: 'pacman', title: 'FEATURE 18/48 · SYNTH CHIP 1: NAMCO 3-VOICE WSG', sub: '32-Step 4-Bit PROM Wavetable Lead + Sub-Oscillator (Envelope: PLUCK)', chip: 'NAMCO WSG WAVETABLE' },
  { id: 19, start: 41.5, end: 44.0, chapter: 'CH 4 · 5-CHIP SYNTHESIS STUDIO', stateImg: 'state_19_synth_ay8910.png', crtGame: 'frogger', title: 'FEATURE 19/48 · SYNTH CHIP 2: GI AY-3-8910 + 60Hz ARP', sub: 'Detuned Dual Square PSG + 60Hz Chiptune Chord Arpeggiator (Envelope: ORGAN)', chip: 'GI AY-3-8910 PSG' },
  { id: 20, start: 44.0, end: 46.5, chapter: 'CH 4 · 5-CHIP SYNTHESIS STUDIO', stateImg: 'state_20_synth_pokey.png', crtGame: 'tempest', title: 'FEATURE 20/48 · SYNTH CHIP 3: ATARI POKEY + 6Hz LFO', sub: 'Polynomial Counter FM Distortion Lead + 6Hz Pitch Vibrato (Envelope: LEAD)', chip: 'ATARI POKEY SYNTH' },
  { id: 21, start: 46.5, end: 49.0, chapter: 'CH 4 · 5-CHIP SYNTHESIS STUDIO', stateImg: 'state_21_synth_dac.png', crtGame: 'dkong', title: 'FEATURE 21/48 · SYNTH CHIP 4: NINTENDO 2A03 7-BIT APU', sub: 'Sub-Octave Triangle Bass & Punchy Pulse Lead (Octave: -1 / +0)', chip: 'NINTENDO 2A03 DAC' },
  { id: 22, start: 49.0, end: 51.5, chapter: 'CH 4 · 5-CHIP SYNTHESIS STUDIO', stateImg: 'state_22_synth_fm.png', crtGame: 'gyruss', title: 'FEATURE 22/48 · SYNTH CHIP 5: M-VAVE 6-OPERATOR FM', sub: 'DX-Style Harmonic Ratio FM Synthesis with Shimmering Polyphony (Envelope: PAD)', chip: 'M-VAVE 6-OP FM' },
  { id: 23, start: 51.5, end: 54.0, chapter: 'CH 4 · 5-CHIP SYNTHESIS STUDIO', stateImg: 'state_23_synth_knobs.png', crtGame: 'asteroids', title: 'FEATURE 23/48 · 4 ENDLESS HARDWARE ROTARY ENCODERS', sub: 'Live 24dB/oct Low-Pass Filter Sweep, Tape Dub Delay (340ms), Feedback & Wave Morph', chip: 'STUDIO DSP FX RACK' },

  // CHAPTER 5: 16-STEP MULTI-CHIP TRACKER — ALL 8 PATTERNS (54.0s - 70.0s)
  { id: 24, start: 54.0, end: 56.0, chapter: 'CH 5 · 16-STEP TRACKER (8 PATTERNS)', stateImg: 'state_24_tracker_pat0.png', crtGame: 'pacman', title: 'FEATURE 24/48 · TRACKER PAT 1: ARCADE RAT THEME', sub: '132 BPM · 4-Channel Multi-Chip Sequence (WSG Bass + AY Lead + POKEY Arp + Drums)', chip: 'WSG+AY+POK+DAC' },
  { id: 25, start: 56.0, end: 58.0, chapter: 'CH 5 · 16-STEP TRACKER (8 PATTERNS)', stateImg: 'state_25_tracker_pat1.png', crtGame: 'frogger', title: 'FEATURE 25/48 · TRACKER PAT 2: PAC-MANIA DUB', sub: '124 BPM · Syncopated Reggae/Dub Chiptune Groove with Stereo Tape Echo', chip: 'WSG + TAPE DUB' },
  { id: 26, start: 58.0, end: 60.0, chapter: 'CH 5 · 16-STEP TRACKER (8 PATTERNS)', stateImg: 'state_26_tracker_pat2.png', crtGame: 'gyruss', title: 'FEATURE 26/48 · TRACKER PAT 3: GYRUSS SPEED RUN', sub: '144 BPM · High-Velocity Baroque Counterpoint & Driving 16th-Note Percussion', chip: 'AY-3-8910 BAROQUE' },
  { id: 27, start: 60.0, end: 62.0, chapter: 'CH 5 · 16-STEP TRACKER (8 PATTERNS)', stateImg: 'state_27_tracker_pat3.png', crtGame: 'asteroids', title: 'FEATURE 27/48 · TRACKER PAT 4: CYBER LABYRINTH', sub: '138 BPM · Dark Darksynth Arpeggio Matrix with 6-Op FM Bass & POKEY Leads', chip: '6-OP FM + POKEY' },
  { id: 28, start: 62.0, end: 64.0, chapter: 'CH 5 · 16-STEP TRACKER (8 PATTERNS)', stateImg: 'state_28_tracker_pat4.png', crtGame: 'dkong', title: 'FEATURE 28/48 · TRACKER PAT 5: DONKEY KONG 25M SWING', sub: '136 BPM · Upbeat Arcade Platformer Groove on 7-Bit DAC & WSG Wavetable', chip: '7-BIT DAC + WSG' },
  { id: 29, start: 64.0, end: 66.0, chapter: 'CH 5 · 16-STEP TRACKER (8 PATTERNS)', stateImg: 'state_29_tracker_pat5.png', crtGame: 'galaga', title: 'FEATURE 29/48 · TRACKER PAT 6: GALAGA SECTOR DIVE', sub: '140 BPM · Cosmic Starfighter Anthem with Dual Z80 WSG Harmonies', chip: 'DUAL Z80 WSG' },
  { id: 30, start: 66.0, end: 68.0, chapter: 'CH 5 · 16-STEP TRACKER (8 PATTERNS)', stateImg: 'state_30_tracker_pat6.png', crtGame: 'tempest', title: 'FEATURE 30/48 · TRACKER PAT 7: TEMPEST VECTOR SURGE', sub: '148 BPM · Relentless Acid Vector Techno Driven by Dual Atari POKEY Chips', chip: 'POKEY TECHNO' },
  { id: 31, start: 68.0, end: 70.0, chapter: 'CH 5 · 16-STEP TRACKER (8 PATTERNS)', stateImg: 'state_31_tracker_pat7.png', crtGame: 'gyruss', title: 'FEATURE 31/48 · TRACKER PAT 8: BACH TOCCATA IN D MINOR', sub: '134 BPM · Classical Pipe-Organ Chiptune Showpiece Across 5 PSG Voices', chip: '5-VOICE PSG' },

  // CHAPTER 6: DEMO JUKEBOX — ALL 4 MULTI-TRACK SONGS (70.0s - 80.0s)
  { id: 32, start: 70.0, end: 72.5, chapter: 'CH 6 · MULTI-TRACK DEMO JUKEBOX', stateImg: 'state_32_jukebox_0.png', crtGame: 'pacman', title: 'FEATURE 32/48 · JUKEBOX SONG 1: "NAMCO NEON"', sub: '128 BPM · 3-Channel Namco WSG Arrangement: Slap Bass, Arp Lead & Chiptune Hook', chip: 'NAMCO WSG 3-CH' },
  { id: 33, start: 72.5, end: 75.0, chapter: 'CH 6 · MULTI-TRACK DEMO JUKEBOX', stateImg: 'state_33_jukebox_1.png', crtGame: 'gyruss', title: 'FEATURE 33/48 · JUKEBOX SONG 2: "GYRUSS COSMIC ODYSSEY"', sub: '144 BPM · 5x AY-3-8910 Baroque Space Symphony with Stereo Counterpoint', chip: '5X AY-3-8910' },
  { id: 34, start: 75.0, end: 77.5, chapter: 'CH 6 · MULTI-TRACK DEMO JUKEBOX', stateImg: 'state_34_jukebox_2.png', crtGame: 'tempest', title: 'FEATURE 34/48 · JUKEBOX SONG 3: "TEMPEST VECTOR SURGE"', sub: '140 BPM · 4-Voice Atari POKEY Distortion & High-Energy Vector Electro', chip: 'ATARI POKEY 4-CH' },
  { id: 35, start: 77.5, end: 80.0, chapter: 'CH 6 · MULTI-TRACK DEMO JUKEBOX', stateImg: 'state_35_jukebox_3.png', crtGame: 'dkong', title: 'FEATURE 35/48 · JUKEBOX SONG 4: "PLUMBER\'S JUMP"', sub: '132 BPM · 4-Track Nintendo Arcade DAC Ragtime & Platformer Lead', chip: 'NINTENDO DAC 4-CH' },

  // CHAPTER 7: 108 ARCADE SFX SOUNDBOARD — ALL 4 BANKS (80.0s - 96.0s)
  { id: 36, start: 80.0, end: 84.0, chapter: 'CH 7 · 108 ARCADE SFX PADS (4 BANKS)', stateImg: 'state_36_sfx_bank0.png', crtGame: 'pacman', title: 'FEATURE 36/48 · SFX BANK 1: GOLDEN AGE (1978–1982)', sub: '27 Pads · Triggering: Waka, Siren, Ghost Eat, Pac Death, UFO, Tractor Beam, Superzapper & Flag', chip: 'WSG / POKEY / DISCRETE' },
  { id: 37, start: 84.0, end: 88.0, chapter: 'CH 7 · 108 ARCADE SFX PADS (4 BANKS)', stateImg: 'state_37_sfx_bank1.png', crtGame: 'dkong', title: 'FEATURE 37/48 · SFX BANK 2: NINTENDO 8-BIT (1981–1985)', sub: '27 Pads · Triggering: Spring Boing, Mallet, Kong Roar, Coin, Pipe Warp, 1-Up, KO & Zelda Chime', chip: '2A03 APU / 7-BIT DAC' },
  { id: 38, start: 88.0, end: 92.0, chapter: 'CH 7 · 108 ARCADE SFX PADS (4 BANKS)', stateImg: 'state_38_sfx_bank2.png', crtGame: 'asteroids', title: 'FEATURE 38/48 · SFX BANK 3: ATARI VECTOR & WILLIAMS', sub: '27 Pads · Triggering: Defender Laser, Smart Bomb, Hyperspace, Joust, Robotron, Evil Otto & TIE', chip: 'WILLIAMS 6800 / QUAD POKEY' },
  { id: 39, start: 92.0, end: 96.0, chapter: 'CH 7 · 108 ARCADE SFX PADS (4 BANKS)', stateImg: 'state_39_sfx_bank3.png', crtGame: 'cclimber', title: 'FEATURE 39/48 · SFX BANK 4: KONAMI, GOTTLIEB & SEGA FM', sub: '27 Pads · Triggering: Frogger, Gyruss Warp, Q*bert Boing & Curse, OutRun Ferrari, Shinobi & Sega', chip: 'YM2151 FM / DUAL AY-3' },

  // CHAPTER 8: VINTAGE SPEECH ROM SHELF — ALL 8 VOICE CHIPS (96.0s - 116.8s)
  { id: 40, start: 96.0, end: 98.1, chapter: 'CH 8 · 8 VINTAGE SPEECH ROM CHIPS', stateImg: 'state_40_speech_0.png', crtGame: 'asteroids', title: 'FEATURE 40/48 · SPEECH ROM 1: BERZERK (1980 STERN)', sub: 'TSI S14001A Custom NMOS Speech Synth: "IN-TRU-DER A-LERT! IN-TRU-DER A-LERT!"', chip: 'TSI S14001A ROM', speechKey: 'VOX_INTRUDER' },
  { id: 41, start: 98.1, end: 100.0, chapter: 'CH 8 · 8 VINTAGE SPEECH ROM CHIPS', stateImg: 'state_41_speech_1.png', crtGame: 'pacman', title: 'FEATURE 41/48 · SPEECH ROM 2: BERZERK COIN DETECT', sub: 'TSI S14001A Custom NMOS Speech Synth: "COIN DE-TEC-TED IN POCK-ET!"', chip: 'TSI S14001A ROM', speechKey: 'VOX_COIN' },
  { id: 42, start: 100.0, end: 102.3, chapter: 'CH 8 · 8 VINTAGE SPEECH ROM CHIPS', stateImg: 'state_42_speech_2.png', crtGame: 'dkong', title: 'FEATURE 42/48 · SPEECH ROM 3: Q*BERT SWEAR SYNTH', sub: 'Votrax SC-01 Formant Phoneme Synthesizer: "@!#?@! VOTRAX SPEECH SYNTH"', chip: 'VOTRAX SC-01 ROM', speechKey: 'VOX_QBERT' },
  { id: 43, start: 102.3, end: 104.7, chapter: 'CH 8 · 8 VINTAGE SPEECH ROM CHIPS', stateImg: 'state_43_speech_3.png', crtGame: 'tempest', title: 'FEATURE 43/48 · SPEECH ROM 4: SINISTAR AWAKENS', sub: 'Harris HC-55516 CVSD Delta Modulation Decoder: "BE-WARE, I LIVE!"', chip: 'HC-55516 CVSD ROM', speechKey: 'VOX_SINISTAR' },
  { id: 44, start: 104.7, end: 107.2, chapter: 'CH 8 · 8 VINTAGE SPEECH ROM CHIPS', stateImg: 'state_44_speech_4.png', crtGame: 'galaga', title: 'FEATURE 44/48 · SPEECH ROM 5: SINISTAR ROAR', sub: 'Harris HC-55516 CVSD Delta Modulation Decoder: "I HUN-GER, CO-WARD!"', chip: 'HC-55516 CVSD ROM', speechKey: 'VOX_HUNGER' },
  { id: 45, start: 107.2, end: 109.6, chapter: 'CH 8 · 8 VINTAGE SPEECH ROM CHIPS', stateImg: 'state_45_speech_5.png', crtGame: 'cclimber', title: 'FEATURE 45/48 · SPEECH ROM 6: WIZARD OF WOR (1980)', sub: 'Midway Votrax SC-01 Dungeon Taunt: "I AM THE WIZ-ARD OF WOR!"', chip: 'VOTRAX SC-01 ROM', speechKey: 'VOX_WIZARD' },
  { id: 46, start: 109.6, end: 112.3, chapter: 'CH 8 · 8 VINTAGE SPEECH ROM CHIPS', stateImg: 'state_46_speech_6.png', crtGame: 'gyruss', title: 'FEATURE 46/48 · SPEECH ROM 7: GORF SPACE EMPEROR', sub: 'Midway Votrax SC-01 Space Laugh: "LONG LIVE GORF! HA-HA-HA-HA!"', chip: 'VOTRAX SC-01 ROM', speechKey: 'VOX_GORF' },
  { id: 47, start: 112.3, end: 116.8, chapter: 'CH 8 · 8 VINTAGE SPEECH ROM CHIPS', stateImg: 'state_47_speech_7.png', crtGame: 'frogger', title: 'FEATURE 47/48 · SPEECH ROM 8: DRAGON\'S LAIR (1983)', sub: 'Cinematronics 8-Bit Linear PCM Voice ROM: "LEAD ON, AD-VEN-TUR-ER! YOUR QUEST AWAITS!"', chip: '8-BIT LINEAR PCM', speechKey: 'VOX_DRAGON' },

  // CHAPTER 9: ATTRACT TOUR & FINALE (116.8s - 120.0s)
  { id: 48, start: 116.8, end: 120.0, chapter: 'CH 9 · ATTRACT TOUR & FINALE SPECS', stateImg: 'state_48_tour_demo.png', crtGame: 'gyruss', title: 'FEATURE 48/48 · AUTONOMOUS 8-GAME ATTRACT TOUR AI', sub: 'Hands-Free AI Bot Cycling All 8 Playable Arcade Engines + Full 5-Chip Symphony Finale', chip: 'ALL 5 SOUND CHIPS' }
];

// ============================================================================
// 2. FOREGROUND SOUND EVENTS SCHEDULE (85+ INDIVIDUAL SOUNDS!)
// ============================================================================
const FOREGROUND_EVENTS = [
  // Ch 1: Boot & Splash
  { time: 0.15, dur: 1.8, type: 'BOOT', fn: 'albumChime', label: 'CHIPTUNES ALBUM STARTUP FANFARE', chip: 'WSG + FM' },
  { time: 2.30, dur: 1.1, type: 'BOOT', fn: 'startupChime', label: 'ARCADE RAT Z80 COLD-BOOT CHIME', chip: 'NAMCO WSG' },
  { time: 3.45, dur: 0.6, type: 'SFX', sfxId: 'COIN', label: 'INSERT COIN (Z80 BUS INTERRUPT)', chip: 'WSG / DAC' },
  { time: 4.35, dur: 0.7, type: 'SFX', sfxId: 'MARIO-1UP', label: 'ROM CONFIGURATOR READY (93 GAMES)', chip: 'NES APU' },
  { time: 5.10, dur: 0.8, type: 'SFX', sfxId: 'ZELDA-SECR', label: 'FIRMWARE COMPILATION VERIFIED', chip: 'NES APU' },

  // Ch 2: 8 Playable Games (authentic game SFX + BGMs)
  // Game 1: Pac-Man (6.0 - 9.0)
  { time: 6.10, dur: 0.45, type: 'GAME', sfxId: 'WAKA', label: 'PAC-MAN: WAKA CHOMP A/B', chip: 'WSG 3-V' },
  { time: 6.45, dur: 0.45, type: 'GAME', sfxId: 'WAKA', label: 'PAC-MAN: WAKA CHOMP B/A', chip: 'WSG 3-V' },
  { time: 6.85, dur: 0.65, type: 'GAME', sfxId: 'SIREN', label: 'PAC-MAN: GHOST SIREN LFO', chip: 'WSG 3-V' },
  { time: 7.55, dur: 0.65, type: 'GAME', sfxId: 'FRUIT', label: 'PAC-MAN: BONUS CHERRY EAT', chip: 'WSG 3-V' },
  { time: 8.20, dur: 0.75, type: 'GAME', sfxId: 'GHOST', label: 'PAC-MAN: 1600 PT GHOST SWEEP', chip: 'WSG 3-V' },

  // Game 2: Crazy Climber (9.0 - 12.0)
  { time: 9.10, dur: 0.65, type: 'GAME', sfxId: 'CLIMB-STEP', label: 'CRAZY CLIMBER: SKYSCRAPER GRIP', chip: 'DUAL AY-3' },
  { time: 9.75, dur: 0.70, type: 'GAME', sfxId: 'CLIMB-POT', label: 'CRAZY CLIMBER: FLOWERPOT SMASH', chip: 'NOISE CRASH' },
  { time: 10.45, dur: 0.70, type: 'GAME', sfxId: 'CLIMB-KONG', label: 'CRAZY CLIMBER: GIANT APE PUNCH', chip: 'DUAL AY-3' },
  { time: 11.15, dur: 0.80, type: 'GAME', sfxId: 'CLIMB-WIN', label: 'CRAZY CLIMBER: ROOF CHOPPER RESCUE', chip: 'DUAL AY-3' },

  // Game 3: Galaga (12.0 - 15.0)
  { time: 12.05, dur: 0.90, type: 'GAME', sfxId: 'GALAGA-INTRO', label: 'GALAGA: STAGE 1 FANFARE', chip: 'NAMCO WSG' },
  { time: 13.00, dur: 0.65, type: 'GAME', sfxId: 'TRACT', label: 'GALAGA: BOSS TRACTOR BEAM', chip: 'WSG 3-V' },
  { time: 13.65, dur: 0.65, type: 'GAME', sfxId: 'CAPTURE', label: 'GALAGA: DUAL FIGHTER CAPTURE', chip: 'WSG 3-V' },
  { time: 14.30, dur: 0.65, type: 'GAME', sfxId: 'BONUS', label: 'GALAGA: CHALLENGING STAGE CLEAR', chip: 'WSG 3-V' },

  // Game 4: Donkey Kong (15.0 - 18.0)
  { time: 15.10, dur: 0.60, type: 'GAME', sfxId: 'DK-JUMP', label: 'DONKEY KONG: JUMP OVER BARREL', chip: '7-BIT DAC' },
  { time: 15.70, dur: 0.75, type: 'GAME', sfxId: 'DK-HAMR', label: 'DONKEY KONG: HAMMER POWER THEME', chip: '7-BIT DAC' },
  { time: 16.45, dur: 0.70, type: 'GAME', sfxId: 'DK-ROAR', label: 'DONKEY KONG: KONG GROWL ROAR', chip: 'NOISE / DAC' },
  { time: 17.15, dur: 0.80, type: 'GAME', sfxId: 'DK-WIN', label: 'DONKEY KONG: 25M GIRDER CLEAR', chip: '7-BIT DAC' },

  // Game 5: Frogger (18.0 - 21.0)
  { time: 18.05, dur: 0.80, type: 'GAME', sfxId: 'FROG-FANFARE', label: 'FROGGER: KONAMI STAGE THEME', chip: 'DUAL AY-3' },
  { time: 18.85, dur: 0.55, type: 'GAME', sfxId: 'FROG-H', label: 'FROGGER: HIGHWAY HOP', chip: 'DUAL AY-3' },
  { time: 19.45, dur: 0.65, type: 'GAME', sfxId: 'FROG-SPLASH', label: 'FROGGER: RIVER LOG SPLASH', chip: 'WATER BLOOP' },
  { time: 20.15, dur: 0.80, type: 'GAME', sfxId: 'FROG-HOME', label: 'FROGGER: SAFE LILYPAD LANDING', chip: 'DUAL AY-3' },

  // Game 6: Asteroids (21.0 - 24.0)
  { time: 21.10, dur: 0.65, type: 'GAME', sfxId: 'AST-THR', label: 'ASTEROIDS: SUB-BASS SHIP THRUST', chip: 'POKEY PBF' },
  { time: 21.75, dur: 0.60, type: 'GAME', sfxId: 'AST-FIRE', label: 'ASTEROIDS: VECTOR PHOTON TORPEDO', chip: 'POKEY PULSE' },
  { time: 22.40, dur: 0.70, type: 'GAME', sfxId: 'AST-SAU', label: 'ASTEROIDS: SMALL SAUCER SIREN', chip: 'POKEY SINE' },
  { time: 23.15, dur: 0.80, type: 'GAME', sfxId: 'AST-EXP', label: 'ASTEROIDS: BOULDER DETONATION', chip: 'POKEY LPF' },

  // Game 7: Tempest (24.0 - 27.0)
  { time: 24.10, dur: 0.60, type: 'GAME', sfxId: 'TEM-FIRE', label: 'TEMPEST: RAPID PARTICLE BLASTER', chip: 'POKEY PULSE' },
  { time: 24.75, dur: 0.65, type: 'GAME', sfxId: 'TEM-FLIP', label: 'TEMPEST: RIM FLIPPER TRILL', chip: 'POKEY TRILL' },
  { time: 25.40, dur: 0.65, type: 'GAME', sfxId: 'TEM-SPIKE', label: 'TEMPEST: SPIKER SPIRAL DRILL', chip: 'POKEY BUZZ' },
  { time: 26.10, dur: 0.85, type: 'GAME', sfxId: 'TEM-ZAP', label: 'TEMPEST: SUPERZAPPER TUBE SWEEP', chip: 'POKEY SWEEP' },

  // Game 8: Gyruss (27.0 - 30.0)
  { time: 27.05, dur: 1.00, type: 'GAME', sfxId: 'GYRUSS-TUNE', label: 'GYRUSS: BACH TOCCATA IN D MINOR', chip: '5X AY-3-8910' },
  { time: 28.10, dur: 0.60, type: 'GAME', sfxId: 'GYRUSS-LAS', label: 'GYRUSS: ORBITAL TWIN PHASER', chip: '5X PSG' },
  { time: 28.75, dur: 0.55, type: 'GAME', sfxId: 'GYRUSS-DIV', label: 'GYRUSS: SATELLITE SWARM DIVE', chip: '5X PSG' },
  { time: 29.30, dur: 0.65, type: 'GAME', sfxId: 'GYRUSS-WARP', label: 'GYRUSS: NEPTUNE TO URANUS WARP', chip: '5X PSG' },

  // Ch 3: Hardware Deck Modes (30.0 - 39.0)
  { time: 30.15, dur: 1.1, type: 'HW', sfxId: 'WARP', label: 'IMMORTAL MODE & STAGE SKIP ENGAGED', chip: 'Z80 DECK' },
  { time: 31.65, dur: 1.1, type: 'HW', sfxId: 'RALLY-FLG', label: '2X HARDWARE CRT BEZEL ZOOM', chip: 'IPS DISPLAY' },
  { time: 33.15, dur: 1.1, type: 'HW', sfxId: 'DEF-CATCH', label: 'NVRAM HALL OF FAME HIGH SCORE SAVED', chip: 'NVRAM' },
  { time: 34.65, dur: 1.1, type: 'HW', sfxId: 'DEF-HYPER', label: 'TIME-MACHINE Z80 STATE REWIND', chip: 'RING BUFFER' },
  { time: 36.15, dur: 1.1, type: 'HW', sfxId: 'STARWAR-TRB', label: 'X-Y LISSAJOUS VECTOR PHASE SCOPE', chip: 'VECTOR DSP' },
  { time: 37.65, dur: 1.1, type: 'HW', sfxId: 'ROBOT-ZAP', label: 'Z80 RAM CIRCUIT-BENDING GLITCH', chip: 'RAM BENDER' },

  // Ch 4: Synth Studio Solos (39.0 - 54.0)
  { time: 39.05, dur: 2.4, type: 'SYNTH', fn: 'synthWsg', label: 'SYNTH SOLO 1: NAMCO WSG 3-VOICE (PLUCK)', chip: 'NAMCO WSG' },
  { time: 41.55, dur: 2.4, type: 'SYNTH', fn: 'synthAy', label: 'SYNTH SOLO 2: AY-3-8910 + 60Hz ARP (ORGAN)', chip: 'AY-3-8910' },
  { time: 44.05, dur: 2.4, type: 'SYNTH', fn: 'synthPokey', label: 'SYNTH SOLO 3: ATARI POKEY + 6Hz LFO (LEAD)', chip: 'ATARI POKEY' },
  { time: 46.55, dur: 2.4, type: 'SYNTH', fn: 'synthDac', label: 'SYNTH SOLO 4: NINTENDO 2A03 APU (SUB OCTAVE)', chip: '2A03 DAC' },
  { time: 49.05, dur: 2.4, type: 'SYNTH', fn: 'synthFm', label: 'SYNTH SOLO 5: M-VAVE 6-OP FM CHORDS (PAD)', chip: '6-OP FM' },
  { time: 51.55, dur: 2.4, type: 'SYNTH', fn: 'synthKnobs', label: 'LIVE 24dB/OCT FILTER SWEEP & TAPE DUB DELAY', chip: '4 ENCODERS' },

  // Ch 5: 8 Tracker Patterns (54.0 - 70.0)
  { time: 54.0, dur: 1.95, type: 'TRACKER', patIdx: 0, label: 'PAT 1: ARCADE RAT THEME (132 BPM)', chip: 'WSG+AY+POK+DAC' },
  { time: 56.0, dur: 1.95, type: 'TRACKER', patIdx: 1, label: 'PAT 2: PAC-MANIA DUB (124 BPM)', chip: 'WSG+TAPE DUB' },
  { time: 58.0, dur: 1.95, type: 'TRACKER', patIdx: 2, label: 'PAT 3: GYRUSS SPEED RUN (144 BPM)', chip: 'AY-3-8910' },
  { time: 60.0, dur: 1.95, type: 'TRACKER', patIdx: 3, label: 'PAT 4: CYBER LABYRINTH (138 BPM)', chip: '6-OP FM + POKEY' },
  { time: 62.0, dur: 1.95, type: 'TRACKER', patIdx: 4, label: 'PAT 5: DONKEY KONG 25M SWING (136 BPM)', chip: '7-BIT DAC + WSG' },
  { time: 64.0, dur: 1.95, type: 'TRACKER', patIdx: 5, label: 'PAT 6: GALAGA SECTOR DIVE (140 BPM)', chip: 'DUAL Z80 WSG' },
  { time: 66.0, dur: 1.95, type: 'TRACKER', patIdx: 6, label: 'PAT 7: TEMPEST VECTOR SURGE (148 BPM)', chip: 'POKEY TECHNO' },
  { time: 68.0, dur: 1.95, type: 'TRACKER', patIdx: 7, label: 'PAT 8: BACH TOCCATA IN D MINOR (134 BPM)', chip: '5-VOICE PSG' },

  // Ch 6: 4 Demo Jukebox Songs (70.0 - 80.0)
  { time: 70.0, dur: 2.45, type: 'JUKEBOX', songIdx: 0, label: 'SONG 1: NAMCO NEON (3-CH WSG @ 128 BPM)', chip: 'NAMCO WSG' },
  { time: 72.5, dur: 2.45, type: 'JUKEBOX', songIdx: 1, label: 'SONG 2: GYRUSS COSMIC ODYSSEY (144 BPM)', chip: '5X AY-3-8910' },
  { time: 75.0, dur: 2.45, type: 'JUKEBOX', songIdx: 2, label: 'SONG 3: TEMPEST VECTOR SURGE (140 BPM)', chip: 'ATARI POKEY' },
  { time: 77.5, dur: 2.45, type: 'JUKEBOX', songIdx: 3, label: 'SONG 4: PLUMBER\'S JUMP (132 BPM)', chip: 'NINTENDO DAC' },

  // Ch 7: 108 SFX Soundboard — 32 Highlighted Pads Across All 4 Banks (80.0 - 96.0)
  // Bank 1 (80.0 - 84.0): 8 pads @ 0.50s each
  { time: 80.05, dur: 0.46, type: 'SFX_PAD', bank: 0, padIdx: 0, sfxId: 'WAKA', label: 'BANK 1 PAD 01: WAKA CHOMP (PAC-MAN)', chip: 'WSG 3-V' },
  { time: 80.55, dur: 0.46, type: 'SFX_PAD', bank: 0, padIdx: 1, sfxId: 'SIREN', label: 'BANK 1 PAD 02: GHOST SIREN (PAC-MAN)', chip: 'WSG 3-V' },
  { time: 81.05, dur: 0.46, type: 'SFX_PAD', bank: 0, padIdx: 3, sfxId: 'GHOST', label: 'BANK 1 PAD 04: GHOST EAT (PAC-MAN)', chip: 'WSG 3-V' },
  { time: 81.55, dur: 0.46, type: 'SFX_PAD', bank: 0, padIdx: 6, sfxId: 'DEATH', label: 'BANK 1 PAD 07: PAC DEATH (PAC-MAN)', chip: 'WSG 3-V' },
  { time: 82.05, dur: 0.46, type: 'SFX_PAD', bank: 0, padIdx: 8, sfxId: 'INV-UFO', label: 'BANK 1 PAD 09: UFO SIREN (SPACE INVADERS)', chip: 'DISCRETE' },
  { time: 82.55, dur: 0.46, type: 'SFX_PAD', bank: 0, padIdx: 11, sfxId: 'TRACT', label: 'BANK 1 PAD 12: TRACTOR BEAM (GALAGA)', chip: 'WSG 3-V' },
  { time: 83.05, dur: 0.46, type: 'SFX_PAD', bank: 0, padIdx: 19, sfxId: 'TEM-ZAP', label: 'BANK 1 PAD 20: SUPERZAPPER (TEMPEST)', chip: 'POKEY SWEEP' },
  { time: 83.55, dur: 0.44, type: 'SFX_PAD', bank: 0, padIdx: 24, sfxId: 'RALLY-FLG', label: 'BANK 1 PAD 25: SPECIAL FLAG (RALLY-X)', chip: 'WSG 3-V' },

  // Bank 2 (84.0 - 88.0): 8 pads @ 0.50s each
  { time: 84.05, dur: 0.46, type: 'SFX_PAD', bank: 1, padIdx: 1, sfxId: 'DK-JUMP', label: 'BANK 2 PAD 02: SPRING BOING (DONKEY KONG)', chip: '7-BIT DAC' },
  { time: 84.55, dur: 0.46, type: 'SFX_PAD', bank: 1, padIdx: 2, sfxId: 'DK-HAMR', label: 'BANK 2 PAD 03: MALLET POUND (DONKEY KONG)', chip: '7-BIT DAC' },
  { time: 85.05, dur: 0.46, type: 'SFX_PAD', bank: 1, padIdx: 4, sfxId: 'DK-ROAR', label: 'BANK 2 PAD 05: KONG ROAR (DONKEY KONG)', chip: 'NOISE/DAC' },
  { time: 85.55, dur: 0.46, type: 'SFX_PAD', bank: 1, padIdx: 7, sfxId: 'MARIO-C', label: 'BANK 2 PAD 08: MARIO COIN (MARIO BROS.)', chip: 'NES APU' },
  { time: 86.05, dur: 0.46, type: 'SFX_PAD', bank: 1, padIdx: 8, sfxId: 'PIPE', label: 'BANK 2 PAD 09: PIPE WARP (SUPER MARIO)', chip: 'NES APU' },
  { time: 86.55, dur: 0.46, type: 'SFX_PAD', bank: 1, padIdx: 11, sfxId: 'MARIO-1UP', label: 'BANK 2 PAD 12: 1-UP JINGLE (SUPER MARIO)', chip: 'NES APU' },
  { time: 87.05, dur: 0.46, type: 'SFX_PAD', bank: 1, padIdx: 17, sfxId: 'PUNCH-KO', label: 'BANK 2 PAD 18: KO BUZZER (PUNCH-OUT!!)', chip: 'SQUARE BUZ' },
  { time: 87.55, dur: 0.44, type: 'SFX_PAD', bank: 1, padIdx: 24, sfxId: 'ZELDA-SECR', label: 'BANK 2 PAD 25: SECRET CHIME (ZELDA ARCADE)', chip: 'NES APU' },

  // Bank 3 (88.0 - 92.0): 8 pads @ 0.50s each
  { time: 88.05, dur: 0.46, type: 'SFX_PAD', bank: 2, padIdx: 0, sfxId: 'DEF-FIRE', label: 'BANK 3 PAD 01: RAPID LASER (DEFENDER)', chip: 'WILLIAMS 6800' },
  { time: 88.55, dur: 0.46, type: 'SFX_PAD', bank: 2, padIdx: 1, sfxId: 'DEF-SMART', label: 'BANK 3 PAD 02: SMART BOMB (DEFENDER)', chip: 'NOISE FLASH' },
  { time: 89.05, dur: 0.46, type: 'SFX_PAD', bank: 2, padIdx: 4, sfxId: 'DEF-HYPER', label: 'BANK 3 PAD 05: HYPERSPACE (DEFENDER)', chip: 'PITCH SWEEP' },
  { time: 89.55, dur: 0.46, type: 'SFX_PAD', bank: 2, padIdx: 5, sfxId: 'JOUST-FLAP', label: 'BANK 3 PAD 06: OSTRICH FLAP (JOUST)', chip: 'LOW RESON' },
  { time: 90.05, dur: 0.46, type: 'SFX_PAD', bank: 2, padIdx: 9, sfxId: 'ROBOT-ZAP', label: 'BANK 3 PAD 10: DUAL LASER (ROBOTRON)', chip: 'WILLIAMS 6800' },
  { time: 90.55, dur: 0.46, type: 'SFX_PAD', bank: 2, padIdx: 12, sfxId: 'BERZERK-ROB', label: 'BANK 3 PAD 13: EVIL OTTO BOUNCE (BERZERK)', chip: 'SQUEAK LFO' },
  { time: 91.05, dur: 0.46, type: 'SFX_PAD', bank: 2, padIdx: 20, sfxId: 'STARWAR-TIE', label: 'BANK 3 PAD 21: TIE SCREAMER (STAR WARS)', chip: 'QUAD POKEY' },
  { time: 91.55, dur: 0.44, type: 'SFX_PAD', bank: 2, padIdx: 21, sfxId: 'STARWAR-LAS', label: 'BANK 3 PAD 22: X-WING QUAD LASER (STAR WARS)', chip: 'QUAD POKEY' },

  // Bank 4 (92.0 - 96.0): 8 pads @ 0.50s each
  { time: 92.05, dur: 0.46, type: 'SFX_PAD', bank: 3, padIdx: 0, sfxId: 'FROG-H', label: 'BANK 4 PAD 01: FROG HOP (FROGGER)', chip: 'DUAL AY-3' },
  { time: 92.55, dur: 0.46, type: 'SFX_PAD', bank: 3, padIdx: 5, sfxId: 'GYRUSS-WARP', label: 'BANK 4 PAD 06: HYPER WARP (GYRUSS)', chip: '5X PSG' },
  { time: 93.05, dur: 0.46, type: 'SFX_PAD', bank: 3, padIdx: 14, sfxId: 'QBERT-HOP', label: 'BANK 4 PAD 15: PYRAMID BOING (Q*BERT)', chip: 'GOTTLIEB DAC' },
  { time: 93.55, dur: 0.46, type: 'SFX_PAD', bank: 3, padIdx: 15, sfxId: 'QBERT-CURSE', label: 'BANK 4 PAD 16: @!#?@! CURSE (Q*BERT)', chip: 'VOTRAX VOICE' },
  { time: 94.05, dur: 0.46, type: 'SFX_PAD', bank: 3, padIdx: 18, sfxId: 'OUTRUN-REV', label: 'BANK 4 PAD 19: FERRARI TESTAROSSA REV (OUTRUN)', chip: 'YM2151 FM' },
  { time: 94.55, dur: 0.46, type: 'SFX_PAD', bank: 3, padIdx: 20, sfxId: 'OUTRUN-PASS', label: 'BANK 4 PAD 21: CHECKPOINT! (OUTRUN)', chip: 'YM2151 FM' },
  { time: 95.05, dur: 0.46, type: 'SFX_PAD', bank: 3, padIdx: 21, sfxId: 'SHINOBI-STAR', label: 'BANK 4 PAD 22: SHURIKEN THROW (SHINOBI)', chip: 'YM2151 FM' },
  { time: 95.55, dur: 0.44, type: 'SFX_PAD', bank: 3, padIdx: 25, sfxId: 'GONGA-COIN', label: 'BANK 4 PAD 26: SEGA FM COIN RING', chip: 'YM2151 FM' },

  // Ch 8: All 8 Vintage Speech ROMs (96.0 - 116.8) — Full unclipped phrase durations!
  { time: 96.10, dur: 1.85, type: 'SPEECH', speechKey: 'VOX_INTRUDER', label: 'BERZERK: "INTRUDER ALERT! INTRUDER ALERT!"', chip: 'TSI S14001A' },
  { time: 98.20, dur: 1.65, type: 'SPEECH', speechKey: 'VOX_COIN', label: 'BERZERK: "COIN DETECTED IN POCKET!"', chip: 'TSI S14001A' },
  { time: 100.10, dur: 2.05, type: 'SPEECH', speechKey: 'VOX_QBERT', label: 'Q*BERT: "@!#?@! VOTRAX SPEECH SYNTH"', chip: 'VOTRAX SC-01' },
  { time: 102.40, dur: 2.15, type: 'SPEECH', speechKey: 'VOX_SINISTAR', label: 'SINISTAR: "BEWARE, I LIVE!"', chip: 'HC-55516 CVSD' },
  { time: 104.80, dur: 2.25, type: 'SPEECH', speechKey: 'VOX_HUNGER', label: 'SINISTAR: "I HUNGER, COWARD!"', chip: 'HC-55516 CVSD' },
  { time: 107.30, dur: 2.18, type: 'SPEECH', speechKey: 'VOX_WIZARD', label: 'WIZARD OF WOR: "I AM THE WIZARD OF WOR!"', chip: 'VOTRAX SC-01' },
  { time: 109.70, dur: 2.50, type: 'SPEECH', speechKey: 'VOX_GORF', label: 'GORF: "LONG LIVE GORF! HA-HA-HA-HA!"', chip: 'VOTRAX SC-01' },
  { time: 112.40, dur: 4.30, type: 'SPEECH', speechKey: 'VOX_DRAGON', label: 'DRAGON\'S LAIR: "LEAD ON, ADVENTURER!"', chip: '8-BIT PCM' },

  // Ch 9: Tour & Finale
  { time: 117.00, dur: 1.4, type: 'SFX', sfxId: 'BONUS', label: 'ATTRACT TOUR AI & VICTORY FANFARE', chip: 'ALL 5 CHIPS' }
];

// ============================================================================
// 3. RENDER FOREGROUND FIRMWARE AUDIO IN HEADLESS CHROME OFFLINEAUDIOCONTEXT
// ============================================================================
async function renderFirmwareForegroundAudio() {
  const fgCachePath = '/tmp/fm1_fg_120s_v2.pcm';
  if (fs.existsSync(fgCachePath) && fs.statSync(fgCachePath).size === TOTAL_SAMPLES * 4) {
    console.log('1/4: Loading cached 120s Authentic Firmware Foreground Audio (' + fgCachePath + ')...');
    const rawPcmBuf = fs.readFileSync(fgCachePath);
    return new Int16Array(rawPcmBuf.buffer, rawPcmBuf.byteOffset, rawPcmBuf.byteLength / 2);
  }
  console.log('1/4: Rendering 120s Authentic Firmware Foreground Audio via Headless Chrome OfflineAudioContext...');

  let receivedBuffer = null;
  let resolveUpload = null;
  const uploadPromise = new Promise(r => { resolveUpload = r; });

  const server = http.createServer((req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    if (req.method === 'OPTIONS') { res.writeHead(200); res.end(); return; }
    const chunks = [];
    req.on('data', c => chunks.push(c));
    req.on('end', () => {
      receivedBuffer = Buffer.concat(chunks);
      res.writeHead(200);
      res.end('OK');
      resolveUpload(receivedBuffer);
    });
  });
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const srvPort = server.address().port;
  const dbgPort = 9300 + (process.pid % 600);

  const chrome = spawn('/usr/bin/google-chrome', [
    '--headless=new', '--no-sandbox', '--disable-gpu', '--autoplay-policy=no-user-gesture-required',
    `--user-data-dir=/tmp/chrome_fg_${process.pid}`,
    `--remote-debugging-port=${dbgPort}`, 'http://localhost:8085/fm1_pacman_preview.html'
  ], { stdio: 'ignore' });

  let wsUrl = null;
  for (let i = 0; i < 30; i++) {
    try { wsUrl = await getWsUrl(dbgPort); if (wsUrl) break; } catch (e) {}
    await sleep(250);
  }
  const targets = await new Promise((resolve, reject) => {
    http.get(`http://127.0.0.1:${dbgPort}/json/list`, res => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => resolve(JSON.parse(d)));
    }).on('error', reject);
  });
  const pageTarget = targets.find(t => t.type === 'page') || targets[0];
  const ws = new WebSocket(pageTarget.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });

  let msgId = 1;
  const pending = new Map();
  ws.onmessage = (ev) => {
    const data = JSON.parse(ev.data);
    if (data.id && pending.has(data.id)) {
      const { resolve, reject } = pending.get(data.id);
      pending.delete(data.id);
      if (data.error) reject(new Error(JSON.stringify(data.error)));
      else resolve(data.result);
    }
  };
  function send(method, params = {}) {
    const id = msgId++;
    return new Promise((resolve, reject) => {
      pending.set(id, { resolve, reject });
      ws.send(JSON.stringify({ id, method, params }));
    });
  }

  await send('Page.enable');
  await send('Runtime.enable');
  await sleep(1000);

  const fgEventsJson = JSON.stringify(FOREGROUND_EVENTS);

  const evalRes = await send('Runtime.evaluate', {
    awaitPromise: true,
    returnByValue: true,
    expression: `(async () => {
      try {
        const SR = 44100;
        const DUR = 120.0;
        const realOffline = new OfflineAudioContext(2, SR * DUR, SR);

        let simTime = 0;
        Object.defineProperty(realOffline, 'currentTime', {
          get: () => simTime,
          configurable: true
        });
        audioCtx = realOffline;

      // Set up firmware DSP chain on realOffline
      masterGain = realOffline.createGain();
      masterGain.gain.value = 0.85;
      masterGain.connect(realOffline.destination);

      filterNode = realOffline.createBiquadFilter();
      filterNode.type = 'lowpass';
      filterNode.frequency.value = 7500;
      filterNode.Q.value = 1.4;

      delayNode = realOffline.createDelay(2.0);
      delayNode.delayTime.value = 0.24;
      feedbackNode = realOffline.createGain();
      feedbackNode.gain.value = 0.28;
      delayWetNode = realOffline.createGain();
      delayWetNode.gain.value = 0.22;

      filterNode.connect(masterGain);
      filterNode.connect(delayNode);
      delayNode.connect(feedbackNode);
      feedbackNode.connect(delayNode);
      delayNode.connect(delayWetNode);
      delayWetNode.connect(masterGain);

      // Build deterministic noiseBuffer for percussion & arcade explosions
      noiseBuffer = realOffline.createBuffer(1, SR * 2, SR);
      const nd = noiseBuffer.getChannelData(0);
      let seed = 1337;
      for (let i = 0; i < nd.length; i++) {
        seed = (seed * 16807) % 2147483647;
        nd[i] = (seed / 1073741823.5) - 1.0;
      }

      // Override initAudio to no-op and force QBERT-CURSE formant synth in OfflineAudioContext
      window.initAudio = function() {};
      window.playArcadeSpeechSample = undefined;

      const events = ${fgEventsJson};
      const burstSfx = new Set(['TEM-FIRE', 'ROBOT-ZAP', 'DEF-FIRE', 'AST-FIRE', 'GYRUSS-LAS']);

      for (const ev of events) {
        simTime = ev.time;

        if (ev.fn === 'albumChime') {
          playAlbumStartupChime();
        } else if (ev.fn === 'startupChime') {
          playStartupChime();
        } else if (ev.sfxId) {
          if (burstSfx.has(ev.sfxId)) {
            [0, 0.11, 0.22].forEach(dt => { simTime = ev.time + dt; playArcadeSfx(ev.sfxId); });
          } else {
            playArcadeSfx(ev.sfxId);
          }
        } else if (ev.type === 'SYNTH') {
          if (ev.fn === 'synthWsg') {
            liveSynth.currentEngine = 'wsg'; liveSynth.envelope = 'pluck'; liveSynth.octaveOffset = 0; liveSynth.lfo.active = false;
            const mel = [14, 17, 21, 24, 26, 24, 21, 17, 14, 17, 21, 26];
            mel.forEach((k, idx) => { simTime = ev.time + idx * 0.19; triggerSynthVoice(k, 0.17); });
          } else if (ev.fn === 'synthAy') {
            liveSynth.currentEngine = 'ay8910'; liveSynth.envelope = 'organ'; liveSynth.octaveOffset = 0; liveSynth.lfo.active = false;
            const chords = [[14, 17, 21, 24], [10, 14, 17, 22], [7, 10, 14, 19], [9, 13, 16, 21]];
            for (let step = 0; step < 36; step++) {
              const ch = chords[Math.floor(step / 9) % chords.length];
              simTime = ev.time + step * 0.062;
              triggerSynthVoice(ch[step % 4], 0.058);
            }
          } else if (ev.fn === 'synthPokey') {
            liveSynth.currentEngine = 'pokey'; liveSynth.envelope = 'lead'; liveSynth.octaveOffset = 0; liveSynth.lfo.active = true;
            const mel = [2, 5, 9, 12, 14, 17, 16, 14, 12, 9, 7, 9];
            mel.forEach((k, idx) => { simTime = ev.time + idx * 0.19; triggerSynthVoice(k, 0.17); });
          } else if (ev.fn === 'synthDac') {
            liveSynth.currentEngine = 'dac'; liveSynth.envelope = 'pluck'; liveSynth.octaveOffset = -1; liveSynth.lfo.active = false;
            const bass = [2, 2, 14, 2, 5, 5, 17, 5, 7, 7, 19, 9];
            bass.forEach((k, idx) => { simTime = ev.time + idx * 0.19; triggerSynthVoice(k, 0.17); });
          } else if (ev.fn === 'synthFm') {
            liveSynth.currentEngine = 'fm'; liveSynth.envelope = 'pad'; liveSynth.octaveOffset = 0; liveSynth.lfo.active = true;
            const chords = [[14, 17, 21, 24], [10, 14, 17, 21], [9, 13, 16, 21]];
            chords.forEach((ch, cIdx) => {
              simTime = ev.time + cIdx * 0.78;
              ch.forEach(k => triggerSynthVoice(k, 0.72));
            });
          } else if (ev.fn === 'synthKnobs') {
            liveSynth.currentEngine = 'pokey'; liveSynth.envelope = 'lead'; liveSynth.octaveOffset = 0;
            filterNode.Q.setValueAtTime(5.5, ev.time);
            filterNode.frequency.setValueAtTime(320, ev.time);
            filterNode.frequency.exponentialRampToValueAtTime(7800, ev.time + 1.1);
            filterNode.frequency.exponentialRampToValueAtTime(420, ev.time + 2.0);
            filterNode.frequency.exponentialRampToValueAtTime(7500, ev.time + 2.4);
            filterNode.Q.setValueAtTime(1.4, ev.time + 2.42);
            const arp = [2, 9, 14, 17, 21, 26, 21, 17, 14, 9, 2, 9, 14, 17, 21, 26];
            arp.forEach((k, idx) => { simTime = ev.time + idx * 0.145; triggerSynthVoice(k, 0.13); });
          }
        } else if (ev.type === 'TRACKER') {
          const pat = trackerEngine.patterns[ev.patIdx];
          if (pat) {
            const stepSec = (60.0 / pat.bpm) / 4.0;
            for (let s = 0; s < 16; s++) {
              const tStep = ev.time + s * stepSec;
              if (tStep >= ev.time + ev.dur) break;
              const row = pat.steps[s % pat.steps.length];
              if (row[0] && row[0][0] > 0) playTrackerVoice('wsg', row[0][0], row[0][1], stepSec, tStep);
              if (row[1] && row[1][0] > 0) playTrackerVoice('ay8910', row[1][0], row[1][1], stepSec, tStep);
              if (row[2] && row[2][0] > 0) playTrackerVoice('pokey', row[2][0], row[2][1], stepSec, tStep);
              if (row[3] && row[3] !== '---') playArcadeDrum(row[3], 13, tStep);
            }
          }
        } else if (ev.type === 'JUKEBOX') {
          const song = DEMO_SONGS[ev.songIdx];
          if (song) {
            const stepSec = (60.0 / song.bpm) / 4.0;
            const maxSteps = Math.floor(ev.dur / stepSec);
            for (let s = 0; s < maxSteps; s++) {
              const tStep = ev.time + s * stepSec;
              song.tracks.forEach((trk, trkIdx) => {
                const cell = trk[s % trk.length];
                if (cell && cell[0] > 0 && cell[1] > 0) {
                  playTrackNote(song.chipType, trkIdx, cell[0], cell[1], cell[2], cell[3], stepSec * 1.6, tStep);
                }
              });
            }
          }
        }
      }

      const rendered = await realOffline.startRendering();
      const chL = rendered.getChannelData(0);
      const chR = rendered.getChannelData(1);
      const pcm = new Int16Array(chL.length * 2);
      for (let i = 0; i < chL.length; i++) {
        const l = Math.max(-1, Math.min(1, chL[i]));
        const r = Math.max(-1, Math.min(1, chR[i]));
        pcm[i * 2] = l < 0 ? l * 32768 : l * 32767;
        pcm[i * 2 + 1] = r < 0 ? r * 32768 : r * 32767;
      }
        await fetch('http://127.0.0.1:${srvPort}/upload', {
          method: 'POST',
          body: new Uint8Array(pcm.buffer)
        });
        return { ok: true };
      } catch (err) {
        return { ok: false, err: String(err && err.stack || err) };
      }
    })()`
  });

  if (evalRes.exceptionDetails || (evalRes.result && evalRes.result.value && !evalRes.result.value.ok)) {
    console.error('Chrome OfflineAudioContext error:', evalRes.exceptionDetails || evalRes.result.value);
    process.exit(1);
  }

  const rawPcmBuf = await uploadPromise;
  ws.close();
  chrome.kill();
  server.close();
  fs.writeFileSync(fgCachePath, rawPcmBuf);
  console.log(`   -> Rendered & cached ${rawPcmBuf.length} bytes of authentic stereo firmware foreground PCM!`);
  return new Int16Array(rawPcmBuf.buffer, rawPcmBuf.byteOffset, rawPcmBuf.byteLength / 2);
}

// ============================================================================
// 4. DECODE ALL 8 VINTAGE SPEECH ROM SAMPLES
// ============================================================================
function loadSpeechRomBuffers() {
  console.log('2/4: Decoding 8 authentic 1980s Vintage Speech ROMs...');
  const pyText = fs.readFileSync(SPEECH_PY, 'utf8');
  const regex = /id:\s*"([A-Z0-9_]+)"[\s\S]*?dataUri:\s*"data:audio\/mp3;base64,([A-Za-z0-9+/=]+)"/g;
  const speechBuffers = {};
  const tmpDir = '/tmp/fm1_speech_decode2';
  fs.mkdirSync(tmpDir, { recursive: true });

  let match;
  while ((match = regex.exec(pyText)) !== null) {
    const key = match[1];
    const b64 = match[2];
    const mp3Path = path.join(tmpDir, `${key}.mp3`);
    const pcmPath = path.join(tmpDir, `${key}.raw`);
    fs.writeFileSync(mp3Path, Buffer.from(b64, 'base64'));
    execFileSync(FFMPEG, ['-y', '-i', mp3Path, '-f', 'f32le', '-ac', '1', '-ar', String(SR), pcmPath], { stdio: 'ignore' });
    const rawBuf = fs.readFileSync(pcmPath);
    const f32 = new Float32Array(rawBuf.buffer, rawBuf.byteOffset, rawBuf.byteLength / 4);
    let peak = 0.01;
    for (let i = 0; i < f32.length; i++) if (Math.abs(f32[i]) > peak) peak = Math.abs(f32[i]);
    for (let i = 0; i < f32.length; i++) {
      // Normalize and apply gentle vintage broadcast compression so every syllable is loud and intelligible
      const norm = (f32[i] / peak);
      f32[i] = Math.tanh(norm * 1.55) * 0.96;
    }
    speechBuffers[key] = f32;
    console.log(`   -> Decoded Speech ROM [${key}]: ${(f32.length / SR).toFixed(2)}s (${f32.length} samples)`);
  }
  if (Object.keys(speechBuffers).length < 8) {
    throw new Error(`Expected 8 Speech ROMs, but only decoded ${Object.keys(speechBuffers).length}`);
  }
  return speechBuffers;
}

// ============================================================================
// 5. COMPOSE LUSH, STUDIO-MASTERED 4-MOVEMENT SYNTHWAVE & CHIPTUNE BGM
// ============================================================================
function composeRichBackgroundMusic() {
  console.log('3/4: Synthesizing 120s 4-Movement Stereo Chiptune & Synthwave Background Score...');
  const bgmL = new Float64Array(TOTAL_SAMPLES);
  const bgmR = new Float64Array(TOTAL_SAMPLES);
  const noteEvents = [];

  const m2f = (m) => 440.0 * Math.pow(2.0, (m - 69.0) / 12.0);

  // Polyblep band-limited saw & pulse helpers for warm, alias-free studio synthwave + crisp chiptune
  function polyblep(t, dt) {
    if (t < dt) { t /= dt; return t + t - t * t - 1.0; }
    else if (t > 1.0 - dt) { t = (t - 1.0) / dt; return t * t + t + t + 1.0; }
    return 0.0;
  }

  // 1) Lush Stereo 6-Op FM + Chorus Polysynth Pad Chord Voice
  function addStereoPadChord(startSec, durSec, midiNotes, gain = 0.11) {
    const s0 = Math.max(0, Math.floor(startSec * SR));
    const s1 = Math.min(TOTAL_SAMPLES, Math.floor((startSec + durSec) * SR));
    for (let nIdx = 0; nIdx < midiNotes.length; nIdx++) {
      const midi = midiNotes[nIdx];
      noteEvents.push({ t: Number(startSec.toFixed(3)), d: Number(durSec.toFixed(3)), ch: 5, m: midi });
      const freq = m2f(midi);
      const pan = (nIdx % 2 === 0 ? -0.45 : 0.45) * ((nIdx + 1) / midiNotes.length);
      const gL = gain * Math.cos((pan + 1) * Math.PI * 0.25);
      const gR = gain * Math.sin((pan + 1) * Math.PI * 0.25);

      let ph1 = (nIdx * 0.19) % 1.0;
      let ph2 = (nIdx * 0.47) % 1.0;
      let phMod = 0.0;
      const dt1 = (freq * 0.997) / SR;
      const dt2 = (freq * 1.003) / SR;
      const dtMod = (freq * 2.0) / SR;

      for (let i = s0; i < s1; i++) {
        const rel = (i - s0) / SR;
        const att = Math.min(1.0, rel / 0.14);
        const relEnv = Math.min(1.0, (durSec - rel) / 0.22);
        const env = att * Math.max(0.0, relEnv);

        phMod = (phMod + dtMod) % 1.0;
        const fmMod = Math.sin(2.0 * Math.PI * phMod) * 0.35 * Math.exp(-rel * 1.8);

        ph1 = (ph1 + dt1) % 1.0;
        ph2 = (ph2 + dt2) % 1.0;
        const saw1 = (2.0 * ph1 - 1.0) - polyblep(ph1, dt1);
        const saw2 = (2.0 * ph2 - 1.0) - polyblep(ph2, dt2);
        const fmCar = Math.sin(2.0 * Math.PI * ph1 + fmMod);

        const sigL = (saw1 * 0.45 + fmCar * 0.55) * env;
        const sigR = (saw2 * 0.45 + fmCar * 0.55) * env;
        bgmL[i] += sigL * gL;
        bgmR[i] += sigR * gR;
      }
    }
  }

  // 2) Expressive Dual-Chip Lead (Namco WSG + AY-3-8910) with Portamento & Delayed Vibrato
  function addExpressiveLead(startSec, durSec, midi, prevMidi, gain = 0.16, pan = 0.15) {
    if (midi <= 0) return;
    noteEvents.push({ t: Number(startSec.toFixed(3)), d: Number(durSec.toFixed(3)), ch: 1, m: midi });
    const s0 = Math.max(0, Math.floor(startSec * SR));
    const s1 = Math.min(TOTAL_SAMPLES, Math.floor((startSec + durSec) * SR));
    const targetFreq = m2f(midi);
    const startFreq = prevMidi > 0 ? m2f(prevMidi) : targetFreq;
    const gL = gain * Math.cos((pan + 1) * Math.PI * 0.25);
    const gR = gain * Math.sin((pan + 1) * Math.PI * 0.25);

    let phA = 0.0, phB = 0.25, phSub = 0.0;
    for (let i = s0; i < s1; i++) {
      const rel = (i - s0) / SR;
      const glide = Math.min(1.0, rel / 0.035);
      const baseF = startFreq + (targetFreq - startFreq) * glide;
      const vib = rel > 0.08 ? Math.sin(2.0 * Math.PI * 5.8 * (rel - 0.08)) * 0.0045 * Math.min(1.0, (rel - 0.08) / 0.1) : 0.0;
      const f = baseF * (1.0 + vib);
      const dt = f / SR;

      phA = (phA + dt) % 1.0;
      phB = (phB + dt * 1.0035) % 1.0;
      phSub = (phSub + dt * 0.5) % 1.0;

      // WSG custom harmonic wave + detuned pulse
      const sqA = (phA < 0.5 ? 1.0 : -1.0) + polyblep(phA, dt) - polyblep((phA + 0.5) % 1.0, dt);
      const sawB = (2.0 * phB - 1.0) - polyblep(phB, dt);
      const triSub = 1.0 - 4.0 * Math.abs(Math.round(phSub - 0.25) - (phSub - 0.25));

      const att = Math.min(1.0, rel / 0.006);
      const dec = 0.35 + 0.65 * Math.exp(-rel * 4.5);
      const relEnv = Math.min(1.0, (durSec - rel) / 0.02);
      const env = att * dec * Math.max(0.0, relEnv);

      bgmL[i] += (sqA * 0.55 + triSub * 0.35 + sawB * 0.20) * env * gL;
      bgmR[i] += (sawB * 0.55 + triSub * 0.35 + sqA * 0.20) * env * gR;
    }
  }

  // 3) 60Hz Chiptune Chord Arpeggiator (AY-3-8910 / SID style sparkling arps)
  function add60HzArp(startSec, durSec, chordNotes, gain = 0.095, pan = -0.35) {
    noteEvents.push({ t: Number(startSec.toFixed(3)), d: Number(durSec.toFixed(3)), ch: 2, m: chordNotes[0] });
    const s0 = Math.max(0, Math.floor(startSec * SR));
    const s1 = Math.min(TOTAL_SAMPLES, Math.floor((startSec + durSec) * SR));
    const gL = gain * Math.cos((pan + 1) * Math.PI * 0.25);
    const gR = gain * Math.sin((pan + 1) * Math.PI * 0.25);
    let ph = 0.0;
    for (let i = s0; i < s1; i++) {
      const rel = (i - s0) / SR;
      const step60 = Math.floor(rel * 60.0) % chordNotes.length;
      const f = m2f(chordNotes[step60]);
      const dt = f / SR;
      ph = (ph + dt) % 1.0;
      const pulse = (ph < 0.25 ? 1.0 : -1.0) + polyblep(ph, dt) - polyblep((ph + 0.75) % 1.0, dt);
      const env = Math.min(1.0, rel / 0.004) * Math.exp(-rel * 3.2) * Math.min(1.0, (durSec - rel) / 0.015);
      bgmL[i] += pulse * env * gL;
      bgmR[i] += pulse * env * gR;
    }
  }

  // 4) Driving Resonant SVF Synthwave + POKEY Bassline
  function addResonantBass(startSec, durSec, midi, gain = 0.24, accent = 1.0) {
    if (midi <= 0) return;
    noteEvents.push({ t: Number(startSec.toFixed(3)), d: Number(durSec.toFixed(3)), ch: 3, m: midi });
    const s0 = Math.max(0, Math.floor(startSec * SR));
    const s1 = Math.min(TOTAL_SAMPLES, Math.floor((startSec + durSec) * SR));
    const f = m2f(midi);
    const dt = f / SR;
    let phSaw = 0.0, phSub = 0.0;
    let ic1 = 0.0, ic2 = 0.0;

    for (let i = s0; i < s1; i++) {
      const rel = (i - s0) / SR;
      phSaw = (phSaw + dt) % 1.0;
      phSub = (phSub + dt * 0.5) % 1.0;

      const saw = (2.0 * phSaw - 1.0) - polyblep(phSaw, dt);
      const sub = Math.sin(2.0 * Math.PI * phSub);
      const raw = saw * 0.68 + sub * 0.55;

      // Per-note resonant filter envelope
      const cutoff = 180.0 + (1900.0 * accent) * Math.exp(-rel * 16.0);
      const g = Math.tan(Math.PI * Math.min(0.45, cutoff / SR));
      const k = 1.0 / (1.8 + 0.8 * accent);
      const a1 = 1.0 / (1.0 + g * (g + k));
      const a2 = g * a1;
      const a3 = g * a2;
      const v3 = raw - ic2;
      const v1 = a1 * ic1 + a2 * v3;
      const v2 = ic2 + a2 * ic1 + a3 * v3;
      ic1 = 2.0 * v1 - ic1;
      ic2 = 2.0 * v2 - ic2;

      const env = Math.min(1.0, rel / 0.003) * Math.exp(-rel * 6.5) * Math.min(1.0, (durSec - rel) / 0.012);
      const sig = Math.tanh(v2 * 1.4) * env * gain;
      bgmL[i] += sig;
      bgmR[i] += sig;
    }
  }

  // 5) Studio Drum Kit (Punchy Kick, Gated Snare, Stereo Hats, Tom Fills & Crash)
  function addDrum(startSec, type, vel = 1.0) {
    const midiMap = { KCK: 36, SNR: 38, HHC: 42, HHO: 46, TOM: 45, CRS: 49 };
    noteEvents.push({ t: Number(startSec.toFixed(3)), d: 0.14, ch: 4, m: midiMap[type] || 36 });
    const s0 = Math.max(0, Math.floor(startSec * SR));
    let rng = (s0 + 1234567) | 0;
    const rand = () => { rng = (rng * 1664525 + 1013904223) | 0; return ((rng >>> 0) / 2147483648.0) - 1.0; };

    if (type === 'KCK') {
      const s1 = Math.min(TOTAL_SAMPLES, s0 + Math.floor(0.28 * SR));
      let ph = 0.0;
      for (let i = s0; i < s1; i++) {
        const rel = (i - s0) / SR;
        const f = 46.0 + 135.0 * Math.exp(-rel * 48.0);
        ph += f / SR;
        const click = rand() * Math.exp(-rel * 180.0) * 0.25;
        const body = Math.sin(2.0 * Math.PI * ph) * Math.exp(-rel * 10.5);
        const sig = Math.tanh((body + click) * 1.5) * 0.38 * vel;
        bgmL[i] += sig;
        bgmR[i] += sig;
      }
    } else if (type === 'SNR') {
      const s1 = Math.min(TOTAL_SAMPLES, s0 + Math.floor(0.26 * SR));
      let ph = 0.0;
      for (let i = s0; i < s1; i++) {
        const rel = (i - s0) / SR;
        ph += (185.0 * Math.exp(-rel * 16.0) + 95.0) / SR;
        const tone = Math.sin(2.0 * Math.PI * ph) * Math.exp(-rel * 22.0) * 0.45;
        const snapL = rand() * Math.exp(-rel * 12.5) * 0.65;
        const snapR = rand() * Math.exp(-rel * 12.5) * 0.65;
        bgmL[i] += (tone + snapL) * 0.26 * vel;
        bgmR[i] += (tone + snapR) * 0.26 * vel;
      }
    } else if (type === 'HHC' || type === 'HHO') {
      const dur = type === 'HHO' ? 0.22 : 0.055;
      const dec = type === 'HHO' ? 14.0 : 58.0;
      const s1 = Math.min(TOTAL_SAMPLES, s0 + Math.floor(dur * SR));
      let prev = 0.0;
      for (let i = s0; i < s1; i++) {
        const rel = (i - s0) / SR;
        const n = rand();
        const hp = n - prev; prev = n * 0.85;
        const sig = hp * Math.exp(-rel * dec) * 0.11 * vel;
        bgmL[i] += sig * 0.85;
        bgmR[i] += sig * 1.15;
      }
    } else if (type === 'TOM') {
      const s1 = Math.min(TOTAL_SAMPLES, s0 + Math.floor(0.20 * SR));
      let ph = 0.0;
      for (let i = s0; i < s1; i++) {
        const rel = (i - s0) / SR;
        ph += (95.0 + 90.0 * Math.exp(-rel * 20.0)) / SR;
        const sig = Math.sin(2.0 * Math.PI * ph) * Math.exp(-rel * 14.0) * 0.26 * vel;
        bgmL[i] += sig;
        bgmR[i] += sig;
      }
    } else if (type === 'CRS') {
      const s1 = Math.min(TOTAL_SAMPLES, s0 + Math.floor(0.85 * SR));
      let prev = 0.0;
      for (let i = s0; i < s1; i++) {
        const rel = (i - s0) / SR;
        const n = rand();
        const hp = n - prev; prev = n * 0.82;
        const sig = hp * Math.exp(-rel * 4.2) * 0.14 * vel;
        bgmL[i] += sig * 1.1;
        bgmR[i] += sig * 0.9;
      }
    }
  }

  // ==========================================================================
  // COMPOSE THE 4 MOVEMENTS ACROSS 120.0 SECONDS (130 BPM = 0.4615s/beat, 1.846s/bar)
  // ==========================================================================
  const BPM = 130.0;
  const BEAT = 60.0 / BPM;
  const STEP = BEAT / 4.0;
  const BAR = BEAT * 4.0;
  const TOTAL_BARS = Math.ceil(DURATION / BAR);

  // Rich chord progressions & melodic hooks per movement
  const progressions = [
    // Mvt 1 (Bars 0..15): F Minor / Ab Major Neon Synthwave
    [
      { root: 41, chord: [65, 68, 72, 75], arp: [65, 68, 72, 77], mel: [77, 0, 75, 72, 68, 72, 75, 80, 79, 77, 75, 72, 68, 0, 72, 75] },
      { root: 37, chord: [61, 65, 68, 72], arp: [61, 65, 68, 75], mel: [73, 0, 72, 68, 65, 68, 72, 77, 75, 73, 72, 68, 65, 0, 68, 72] },
      { root: 39, chord: [63, 67, 70, 75], arp: [63, 67, 70, 77], mel: [75, 0, 77, 79, 80, 79, 77, 75, 79, 0, 77, 75, 72, 70, 68, 67] },
      { root: 36, chord: [60, 64, 67, 70], arp: [60, 64, 67, 72], mel: [72, 75, 77, 79, 80, 82, 84, 80, 79, 76, 72, 67, 64, 67, 70, 72] }
    ],
    // Mvt 2 (Bars 16..37): D Minor Baroque Chiptune Odyssey
    [
      { root: 38, chord: [62, 65, 69, 72], arp: [62, 65, 69, 74], mel: [74, 77, 81, 77, 74, 69, 74, 77, 81, 84, 81, 77, 74, 69, 65, 69] },
      { root: 34, chord: [58, 62, 65, 69], arp: [58, 62, 65, 72], mel: [70, 74, 77, 74, 70, 65, 70, 74, 77, 81, 77, 74, 70, 65, 62, 65] },
      { root: 31, chord: [55, 58, 62, 67], arp: [55, 58, 62, 69], mel: [67, 70, 74, 77, 79, 77, 74, 70, 74, 77, 79, 82, 81, 79, 77, 74] },
      { root: 33, chord: [57, 61, 64, 69], arp: [57, 61, 64, 73], mel: [73, 76, 81, 79, 76, 73, 69, 73, 76, 81, 85, 81, 79, 76, 73, 69] }
    ],
    // Mvt 3 (Bars 38..54): E Minor Electro-Funk (SFX & Speech Showcase Groove)
    [
      { root: 40, chord: [64, 67, 71, 74], arp: [64, 67, 71, 76], mel: [76, 0, 79, 76, 74, 0, 71, 67, 71, 74, 76, 79, 83, 79, 76, 74] },
      { root: 36, chord: [60, 64, 67, 71], arp: [60, 64, 67, 74], mel: [72, 0, 76, 72, 71, 0, 67, 64, 67, 71, 72, 76, 79, 76, 72, 71] },
      { root: 33, chord: [57, 60, 64, 69], arp: [57, 60, 64, 72], mel: [69, 72, 76, 81, 79, 76, 72, 69, 72, 76, 79, 81, 84, 81, 79, 76] },
      { root: 35, chord: [59, 63, 66, 71], arp: [59, 63, 66, 75], mel: [71, 75, 78, 83, 81, 78, 75, 71, 75, 78, 83, 87, 86, 83, 78, 75] }
    ],
    // Mvt 4 (Bars 55..end): D Minor -> D Major 9 Grand Finale
    [
      { root: 38, chord: [62, 66, 69, 73, 76], arp: [62, 66, 69, 74, 78, 81], mel: [74, 78, 81, 86, 85, 81, 78, 74, 78, 81, 85, 86, 90, 86, 85, 81] },
      { root: 35, chord: [59, 62, 66, 69, 74], arp: [59, 62, 66, 71, 74, 78], mel: [71, 74, 78, 83, 81, 78, 74, 71, 74, 78, 81, 83, 86, 83, 81, 78] },
      { root: 31, chord: [55, 59, 62, 66, 71], arp: [55, 59, 62, 67, 71, 74], mel: [67, 71, 74, 79, 78, 74, 71, 67, 71, 74, 78, 79, 83, 79, 78, 74] },
      { root: 33, chord: [57, 61, 64, 69, 74], arp: [57, 61, 64, 69, 73, 76], mel: [73, 76, 81, 85, 86, 85, 81, 76, 81, 85, 86, 88, 90, 88, 86, 85] }
    ]
  ];

  let prevLeadNote = 0;
  for (let bar = 0; bar < TOTAL_BARS; bar++) {
    const barStart = bar * BAR;
    if (barStart >= DURATION) break;

    const mvtIdx = bar < 16 ? 0 : (bar < 38 ? 1 : (bar < 55 ? 2 : 3));
    const prog = progressions[mvtIdx];
    const barData = prog[bar % prog.length];

    // 1. Lush Stereo Pad Chords
    addStereoPadChord(barStart, BAR * 0.98, barData.chord, 0.105);

    // 2. Crash on movement changes & every 8 bars
    if (bar % 8 === 0) addDrum(barStart, 'CRS', 0.95);

    // 3. 16 Steps per Bar
    for (let s = 0; s < 16; s++) {
      const tStep = barStart + s * STEP;
      if (tStep >= DURATION) break;

      // Driving Octave Synthwave / POKEY Bassline
      const bassOct = (s % 2 === 1) ? 12 : 0;
      const bassNote = (s === 14) ? barData.root + 7 : (s === 15 ? barData.root + 10 : barData.root + bassOct);
      const accent = (s % 4 === 0) ? 1.25 : 0.75;
      addResonantBass(tStep, STEP * 0.92, bassNote, 0.22, accent);

      // 60Hz Chiptune Arp on off-beats & arpeggio steps
      if (s % 2 === 0) {
        add60HzArp(tStep, STEP * 1.85, barData.arp, 0.085, (s % 4 === 0) ? -0.4 : 0.4);
      }

      // Expressive Dual-Chip Lead Melody
      const melNote = barData.mel[s];
      if (melNote > 0) {
        addExpressiveLead(tStep, STEP * 1.75, melNote, prevLeadNote, 0.145, 0.12 * Math.sin(s));
        prevLeadNote = melNote;
      }

      // Studio Drum Groove
      if (s === 0 || s === 8 || (s === 10 && bar % 2 === 1)) addDrum(tStep, 'KCK', 1.0);
      if (s === 4 || s === 12) addDrum(tStep, 'SNR', 1.0);
      if (s % 2 === 0) addDrum(tStep, 'HHC', 0.75);
      if (s % 4 === 2) addDrum(tStep, 'HHO', 0.85);

      // 4-Bar Drum Fill
      if (bar % 4 === 3 && s >= 12) {
        addDrum(tStep, s % 2 === 0 ? 'TOM' : 'SNR', 0.92);
      }
    }
  }

  // Apply Stereo Ping-Pong Tape Delay (3/16th dotted delay) to BGM
  const dSamples = Math.floor(STEP * 3.0 * SR);
  const delL = new Float64Array(TOTAL_SAMPLES);
  const delR = new Float64Array(TOTAL_SAMPLES);
  for (let i = 0; i < TOTAL_SAMPLES; i++) {
    const prevL = i >= dSamples ? delR[i - dSamples] : 0.0;
    const prevR = i >= dSamples ? delL[i - dSamples] : 0.0;
    delL[i] = bgmL[i] * 0.22 + prevL * 0.36;
    delR[i] = bgmR[i] * 0.22 + prevR * 0.36;
    bgmL[i] += delL[i] * 0.26;
    bgmR[i] += delR[i] * 0.26;
  }

  return { bgmL, bgmR, noteEvents };
}

// ============================================================================
// 6. SIDECHAIN MIXING & WAV EXPORT
// ============================================================================
function writeWavFile(filepath, chL, chR) {
  const numSamples = chL.length;
  const dataSize = numSamples * 4;
  const buf = Buffer.alloc(44 + dataSize);
  buf.write('RIFF', 0);
  buf.writeUInt32LE(36 + dataSize, 4);
  buf.write('WAVE', 8);
  buf.write('fmt ', 12);
  buf.writeUInt32LE(16, 16);
  buf.writeUInt16LE(1, 20);
  buf.writeUInt16LE(2, 22);
  buf.writeUInt32LE(SR, 24);
  buf.writeUInt32LE(SR * 4, 28);
  buf.writeUInt16LE(4, 32);
  buf.writeUInt16LE(16, 34);
  buf.write('data', 36);
  buf.writeUInt32LE(dataSize, 40);

  let offset = 44;
  for (let i = 0; i < numSamples; i++) {
    const sL = Math.max(-1.0, Math.min(1.0, Math.tanh(chL[i] * 1.15)));
    const sR = Math.max(-1.0, Math.min(1.0, Math.tanh(chR[i] * 1.15)));
    buf.writeInt16LE(Math.round(sL * 32767), offset);
    buf.writeInt16LE(Math.round(sR * 32767), offset + 2);
    offset += 4;
  }
  fs.writeFileSync(filepath, buf);
}

async function main() {
  const fgInt16 = await renderFirmwareForegroundAudio();
  const speechBuffers = loadSpeechRomBuffers();
  console.log('3/4: Synthesizing 120s 64-Bar (128 BPM) 4-Act Masterpiece Chiptune, Synthwave & Jazz-Funk Score...');
  const { bgmL, bgmR, noteEvents } = composeMasterpieceBgm(SR, TOTAL_SAMPLES);

  console.log('4/4: Mixing Foreground Firmware Sounds + 8 Speech ROMs + Musical Multi-Stage Sidechain BGM...');

  // Save standalone Background Music first (`demo_bgm_music.wav`)
  writeWavFile(path.join(WEB_DIR, 'demo_bgm_music.wav'), bgmL, bgmR);

  // Build complete foreground stereo buffers (fgL, fgR) combining Chrome OfflineAudioContext + Speech ROMs
  const fgL = new Float64Array(TOTAL_SAMPLES);
  const fgR = new Float64Array(TOTAL_SAMPLES);
  for (let i = 0; i < TOTAL_SAMPLES; i++) {
    fgL[i] = (fgInt16[i * 2] || 0) / 32768.0;
    fgR[i] = (fgInt16[i * 2 + 1] || 0) / 32768.0;
  }

  // Per-event peak normalization on rendered OfflineAudioContext SFX/Synth/Tracker/Jukebox events
  for (const ev of FOREGROUND_EVENTS) {
    if (ev.type === 'SPEECH') continue;
    const s0 = Math.max(0, Math.floor(ev.time * SR));
    const s1 = Math.min(TOTAL_SAMPLES, Math.floor((ev.time + ev.dur) * SR));
    if (ev.sfxId === 'QBERT-CURSE' && speechBuffers['VOX_QBERT']) {
      const sp = speechBuffers['VOX_QBERT'];
      const maxLen = Math.min(sp.length, s1 - s0);
      for (let i = 0; i < maxLen; i++) {
        fgL[s0 + i] = fgL[s0 + i] * 0.35 + sp[i] * 0.85;
        fgR[s0 + i] = fgR[s0 + i] * 0.35 + sp[i] * 0.85;
      }
    }
    let pk = 0.0;
    for (let i = s0; i < s1; i++) {
      const m = Math.max(Math.abs(fgL[i]), Math.abs(fgR[i]));
      if (m > pk) pk = m;
    }
    if (pk > 0.005 && pk < 0.82) {
      const boost = Math.min(6.0, 0.85 / pk);
      for (let i = s0; i < s1; i++) {
        fgL[i] = Math.tanh(fgL[i] * boost);
        fgR[i] = Math.tanh(fgR[i] * boost);
      }
    }
  }

  // Mix in all 8 Vintage Speech ROMs at their exact Chapter 8 timestamps
  for (const ev of FOREGROUND_EVENTS) {
    if (ev.type === 'SPEECH' && ev.speechKey && speechBuffers[ev.speechKey]) {
      const sp = speechBuffers[ev.speechKey];
      const s0 = Math.floor(ev.time * SR);
      const maxSamples = Math.min(sp.length, Math.floor(ev.dur * SR));
      for (let i = 0; i < maxSamples && (s0 + i) < TOTAL_SAMPLES; i++) {
        const fadeOut = (maxSamples - i) < Math.floor(0.06 * SR) ? (maxSamples - i) / Math.floor(0.06 * SR) : 1.0;
        fgL[s0 + i] = sp[i] * 0.98 * fadeOut;
        fgR[s0 + i] = sp[i] * 0.98 * fadeOut;
      }
    }
  }

  // Add subtle Haas stereo widening (11ms R-channel offset mix) to Tracker/Jukebox sections (54s..80s)
  const haasSamples = Math.floor(0.011 * SR);
  for (let i = Math.floor(54.0 * SR); i < Math.floor(80.0 * SR) && i < TOTAL_SAMPLES; i++) {
    const delayed = i >= haasSamples ? fgL[i - haasSamples] : 0.0;
    fgL[i] = fgL[i] * 0.90 + delayed * 0.18;
    fgR[i] = fgR[i] * 0.90 - delayed * 0.18;
  }

  // Musical Multi-Stage Sidechain Envelope:
  // - Keeps BGM loud, full, and front-and-center (0.80..0.95) during Chapters 1, 2, 3, 4, 7 & 9,
  //   dipping only briefly on instantaneous SFX transients so the music drives the video!
  // - Smoothly ducks BGM to 0.08 during Tracker & Jukebox chapters (54.0s..80.0s) so their native songs play cleanly without BPM clashes.
  // - Ducks BGM to a groovy 0.30 vocal-pocket during Speech ROMs (96.0s..116.8s) so both the voice and the F-Minor groove shine!
  const targetDuck = new Float32Array(TOTAL_SAMPLES);
  targetDuck.fill(0.92);
  for (const ev of FOREGROUND_EVENTS) {
    if (ev.type === 'SPEECH') {
      const s0 = Math.max(0, Math.floor((ev.time - 0.06) * SR));
      const s1 = Math.min(TOTAL_SAMPLES, Math.floor((ev.time + ev.dur + 0.08) * SR));
      for (let i = s0; i < s1; i++) targetDuck[i] = 0.28;
    } else if (ev.type === 'TRACKER' || ev.type === 'JUKEBOX') {
      const s0 = Math.max(0, Math.floor((ev.time - 0.05) * SR));
      const s1 = Math.min(TOTAL_SAMPLES, Math.floor((ev.time + ev.dur + 0.05) * SR));
      for (let i = s0; i < s1; i++) targetDuck[i] = 0.08;
    } else if (ev.type === 'SYNTH') {
      const s0 = Math.max(0, Math.floor((ev.time - 0.04) * SR));
      const s1 = Math.min(TOTAL_SAMPLES, Math.floor((ev.time + ev.dur + 0.04) * SR));
      for (let i = s0; i < s1; i++) targetDuck[i] = 0.52;
    }
  }

  const masterL = new Float64Array(TOTAL_SAMPLES);
  const masterR = new Float64Array(TOTAL_SAMPLES);
  let smoothDuck = 0.92;
  let transientEnv = 0.0;
  const duckAtt = Math.exp(-1.0 / (0.025 * SR));
  const duckRel = Math.exp(-1.0 / (0.160 * SR));
  const trAtt = Math.exp(-1.0 / (0.005 * SR));
  const trRel = Math.exp(-1.0 / (0.090 * SR));

  for (let i = 0; i < TOTAL_SAMPLES; i++) {
    const tgt = targetDuck[i];
    if (tgt < smoothDuck) {
      smoothDuck = duckAtt * smoothDuck + (1.0 - duckAtt) * tgt;
    } else {
      smoothDuck = duckRel * smoothDuck + (1.0 - duckRel) * tgt;
    }

    const fgPeak = Math.max(Math.abs(fgL[i]), Math.abs(fgR[i]));
    if (fgPeak > transientEnv) {
      transientEnv = trAtt * transientEnv + (1.0 - trAtt) * fgPeak;
    } else {
      transientEnv = trRel * transientEnv + (1.0 - trRel) * fgPeak;
    }

    // Fast transient dip (up to 35% dip only on the sharp peak of an SFX hit)
    const transientDip = 1.0 - Math.min(0.35, transientEnv * 0.42);
    const finalBgmGain = smoothDuck * transientDip * 0.95;

    // Smooth 1.8s fade-out at the very end (118.2s - 120.0s)
    const t = i / SR;
    const endFade = t > 118.2 ? Math.max(0.0, (120.0 - t) / 1.8) : 1.0;

    masterL[i] = (bgmL[i] * finalBgmGain + fgL[i] * 1.02) * endFade;
    masterR[i] = (bgmR[i] * finalBgmGain + fgR[i] * 1.02) * endFade;
  }

  writeWavFile(path.join(WEB_DIR, 'commercial_master_audio.wav'), masterL, masterR);
  writeWavFile(path.join(WEB_DIR, 'demo_soundtrack.wav'), masterL, masterR);

  const telemetry = {
    duration: DURATION,
    sampleRate: SR,
    scenes: SCENES,
    events: FOREGROUND_EVENTS,
    noteEvents
  };
  fs.writeFileSync(path.join(WEB_DIR, 'commercial_telemetry.json'), JSON.stringify(telemetry, null, 2));
  console.log(`Saved commercial_master_audio.wav, demo_bgm_music.wav, and commercial_telemetry.json (${SCENES.length} scenes, ${FOREGROUND_EVENTS.length} sound showcases)!`);
}

main().catch(err => { console.error(err); process.exit(1); });
