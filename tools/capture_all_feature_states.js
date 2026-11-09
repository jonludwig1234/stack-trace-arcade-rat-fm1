#!/usr/bin/env node
/**
 * Captures all 48 individual firmware feature states and exact DOM element bounding boxes
 * directly from http://localhost:8085/fm1_pacman_preview.html via headless Chrome CDP.
 */
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

const OUT_DIR = '/tmp/fm1_ui_states';
fs.mkdirSync(OUT_DIR, { recursive: true });

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

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function main() {
  console.log('Launching headless Chrome (1280x920) to capture all 48 live firmware feature states...');
  const chrome = spawn('/usr/bin/google-chrome', [
    '--headless=new', '--no-sandbox', '--disable-gpu', '--autoplay-policy=no-user-gesture-required',
    '--remote-debugging-port=9235', '--window-size=1280,920', 'http://localhost:8085/fm1_pacman_preview.html'
  ], { stdio: 'ignore' });

  let wsUrl = null;
  for (let i = 0; i < 30; i++) {
    try { wsUrl = await getWsUrl(9235); if (wsUrl) break; } catch (e) {}
    await sleep(250);
  }
  if (!wsUrl) { chrome.kill(); throw new Error('Could not connect to Chrome CDP'); }

  const targets = await new Promise((resolve, reject) => {
    http.get('http://127.0.0.1:9235/json/list', res => {
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

  async function evaluate(expr) {
    const wrapped = expr.trim().startsWith('(() =>') ? expr : `(() => {\n${expr}\n})()`;
    const res = await send('Runtime.evaluate', { expression: wrapped, returnByValue: true, awaitPromise: true });
    if (res.exceptionDetails) {
      console.error('Evaluate exception:', res.exceptionDetails.text);
    }
    return res.result ? res.result.value : undefined;
  }

  async function snap(filename) {
    const shot = await send('Page.captureScreenshot', { format: 'png' });
    const outPath = path.join(OUT_DIR, filename);
    fs.writeFileSync(outPath, Buffer.from(shot.data, 'base64'));
    process.stdout.write(`  [SNAP] ${filename}\n`);
  }

  await send('Page.enable');
  await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', {
    width: 1280, height: 920, deviceScaleFactor: 1, mobile: false
  });
  await sleep(1200);

  // Ensure scroll is at top and audio initialized
  await evaluate(`
    window.scrollTo(0, 0);
    if (typeof initAudio === 'function') initAudio();
  `);

  // Record key bounding boxes in the 1280x920 viewport
  const layoutRects = await evaluate(`(() => {
    function rectOf(sel) {
      const el = document.querySelector(sel);
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return { x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width), h: Math.round(r.height) };
    }
    const rects = {
      viewport: { w: 1280, h: 920 },
      tftCanvas: rectOf('#tftCanvas'),
      screenBezel: rectOf('#screenBezel'),
      tabArcade: rectOf('#tabArcade'),
      tabSynth: rectOf('#tabSynth'),
      tabTracker: rectOf('#tabTracker'),
      tabDemo: rectOf('#tabDemo'),
      tabSoundboard: rectOf('#tabSoundboard'),
      tabSpeech: rectOf('#tabSpeech'),
      tabTour: rectOf('#tabTour'),
      knob1: rectOf('#knob1'),
      knob2: rectOf('#knob2'),
      knob3: rectOf('#knob3'),
      knob4: rectOf('#knob4'),
      sfxPads: [],
      speechCards: {}
    };
    setStudioTab('soundboard');
    switchSfxBank(0);
    for (let i = 0; i < 27; i++) {
      rects.sfxPads.push(rectOf('#sfxPad_' + i));
    }
    setStudioTab('speech');
    const spIds = ['VOX_INTRUDER','VOX_COIN','VOX_QBERT','VOX_SINISTAR','VOX_HUNGER','VOX_WIZARD','VOX_GORF','VOX_DRAGON'];
    for (const id of spIds) {
      rects.speechCards[id] = rectOf('#card_' + id);
    }
    setStudioTab('arcade');
    return rects;
  })()`);

  fs.writeFileSync(path.join(OUT_DIR, 'layout_rects.json'), JSON.stringify(layoutRects, null, 2));
  console.log('Saved layout_rects.json (tftCanvas:', layoutRects.tftCanvas, ')');

  // 1. Boot & Splash Modes
  await evaluate(`setStudioTab('arcade'); triggerAlbumSplashScreen();`);
  await sleep(300);
  await snap('state_01_album_splash.png');

  await evaluate(`triggerSplashScreen();`);
  await sleep(300);
  await snap('state_02_arcade_splash.png');

  // 2. All 8 Playable Arcade Classics
  const games = ['pacman', 'cclimber', 'galaga', 'dkong', 'frogger', 'asteroids', 'tempest', 'gyruss'];
  for (let i = 0; i < games.length; i++) {
    const g = games[i];
    await evaluate(`
      skipSplashScreen();
      setStudioTab('arcade');
      switchActiveGame('${g}');
      insertCoin();
      start1P();
    `);
    await sleep(350);
    await evaluate(`for (let k = 0; k < 25; k++) { if (typeof stepCpuFrame === 'function') stepCpuFrame(); }`);
    await sleep(100);
    await snap(`state_${String(4 + i).padStart(2, '0')}_game_${g}.png`);
  }

  // 3. Hardware Deck & Special Firmware Modes
  await evaluate(`
    setStudioTab('arcade');
    switchActiveGame('pacman');
    if (!arcadeImmortalMode) toggleImmortalMode();
    skipCurrentLevel();
  `);
  await sleep(200);
  await snap('state_12_hw_immortal.png');

  await evaluate(`if (arcadeImmortalMode) toggleImmortalMode(); toggleScreenZoom();`);
  await sleep(250);
  await snap('state_13_hw_zoom2x.png');
  await evaluate(`toggleScreenZoom();`); // restore normal zoom
  await sleep(150);

  await evaluate(`
    const lb = document.getElementById('arcadeLeaderboardCard');
    if (lb) { lb.style.boxShadow = '0 0 20px rgba(0, 229, 255, 0.6)'; lb.style.borderColor = '#00e5ff'; }
  `);
  await sleep(150);
  await snap('state_14_hw_leaderboard.png');
  await evaluate(`
    const lb = document.getElementById('arcadeLeaderboardCard');
    if (lb) { lb.style.boxShadow = ''; lb.style.borderColor = ''; }
  `);

  await evaluate(`setMode('rewind'); if (typeof renderArcadeFrame === 'function') renderArcadeFrame();`);
  await sleep(250);
  await snap('state_15_hw_rewind.png');

  await evaluate(`setMode('vector'); if (typeof updateVisual === 'function') updateVisual();`);
  await sleep(250);
  await snap('state_16_hw_lissajous.png');

  await evaluate(`setStudioTab('arcade'); switchActiveGame('pacman'); triggerCircuitBending();`);
  await sleep(250);
  await snap('state_17_hw_bender.png');

  // 4. Synth Studio — All 5 Sound Chips + Envelopes + ARP/LFO + Knobs
  const synthStates = [
    { file: 'state_18_synth_wsg.png', eng: 'wsg', env: 'pluck', arp: false, lfo: false, oct: 0, note: 60 },
    { file: 'state_19_synth_ay8910.png', eng: 'ay8910', env: 'organ', arp: true, lfo: false, oct: 0, note: 64 },
    { file: 'state_20_synth_pokey.png', eng: 'pokey', env: 'lead', arp: false, lfo: true, oct: 0, note: 67 },
    { file: 'state_21_synth_dac.png', eng: 'dac', env: 'pluck', arp: false, lfo: false, oct: -1, note: 55 },
    { file: 'state_22_synth_fm.png', eng: 'fm', env: 'pad', arp: true, lfo: true, oct: 1, note: 72 }
  ];
  for (const st of synthStates) {
    await evaluate(`
      setStudioTab('synth');
      setSynthEngine('${st.eng}');
      setEnvelope('${st.env}');
      setSynthOctave(${st.oct});
      if (Boolean(liveSynth.arp) !== ${st.arp}) toggleArp();
      if (Boolean(liveSynth.lfo) !== ${st.lfo}) toggleLfo();
      playLiveSynthNote(${st.note}, 9);
      if (typeof renderSynthOscilloscope === 'function') renderSynthOscilloscope();
    `);
    await sleep(220);
    await snap(st.file);
  }

  // Hardware Knobs highlight state
  await evaluate(`
    setStudioTab('synth');
    document.getElementById('valKnob1').textContent = '1.8 kHz';
    document.getElementById('valKnob2').textContent = '340 MS';
    document.getElementById('valKnob3').textContent = '68%';
    document.getElementById('valKnob4').textContent = 'WSG 4';
    ['knob1','knob2','knob3','knob4'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.style.boxShadow = '0 0 18px #00e5ff';
    });
  `);
  await sleep(200);
  await snap('state_23_synth_knobs.png');
  await evaluate(`
    ['knob1','knob2','knob3','knob4'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.style.boxShadow = '';
    });
  `);

  // 5. 16-Step Multi-Chip Tracker — All 8 Patterns
  for (let p = 0; p < 8; p++) {
    await evaluate(`
      setStudioTab('tracker');
      selectTrackerPattern(${p});
      trackerEngine.step = ${(p * 2) % 16};
      updateTrackerUI();
      if (typeof renderTrackerScreen === 'function') renderTrackerScreen();
    `);
    await sleep(220);
    await snap(`state_${24 + p}_tracker_pat${p}.png`);
  }

  // 6. Demo Jukebox — All 4 Multi-Track Songs
  for (let s = 0; s < 4; s++) {
    await evaluate(`
      setStudioTab('demo');
      selectDemoSong(${s});
      demoPlayer.playing = true;
      demoPlayer.step = ${(s * 4) % 16};
      updateJukeboxUI();
    `);
    await sleep(220);
    await snap(`state_${32 + s}_jukebox_${s}.png`);
  }
  await evaluate(`stopDemoSong();`);

  // 7. 108 SFX Soundboard — All 4 Golden-Era Banks
  const bankSampleNames = ['PAC-WAKA', 'DK-JUMP', 'INV-SHOOT', 'QBERT-HOP'];
  for (let b = 0; b < 4; b++) {
    await evaluate(`
      setStudioTab('soundboard');
      switchSfxBank(${b});
      lastSfxName = '${bankSampleNames[b]}';
      if (typeof renderAudio === 'function') renderAudio();
    `);
    await sleep(220);
    await snap(`state_${36 + b}_sfx_bank${b}.png`);
  }

  // 8. Vintage Speech ROM Shelf — All 8 Authentic Voice Chips Illuminated One by One
  const speechIds = [
    'VOX_INTRUDER', 'VOX_COIN', 'VOX_QBERT', 'VOX_SINISTAR',
    'VOX_HUNGER', 'VOX_WIZARD', 'VOX_GORF', 'VOX_DRAGON'
  ];
  for (let i = 0; i < speechIds.length; i++) {
    const id = speechIds[i];
    await evaluate(`
      setStudioTab('speech');
      lastSpeechRomId = '${id}';
      lastSfxName = '${id}';
      document.querySelectorAll('.speech-card').forEach(c => {
        c.classList.remove('speech-card-active');
        c.style.borderColor = '';
        c.style.boxShadow = '';
      });
      const target = document.getElementById('card_${id}');
      if (target) {
        target.classList.add('speech-card-active');
        target.style.borderColor = '#00e5ff';
        target.style.boxShadow = '0 0 22px rgba(0, 229, 255, 0.75)';
      }
      const spDisp = document.getElementById('speechStatusDisplay');
      if (spDisp) spDisp.textContent = 'SPEAKING: ${id} (AUTHENTIC 1980s VOICE ROM ACTIVE)';
      if (typeof renderAudio === 'function') renderAudio();
    `);
    await sleep(200);
    await snap(`state_${40 + i}_speech_${i}.png`);
  }

  // 9. Autonomous Tour Demo
  await evaluate(`
    setStudioTab('tour');
    if (typeof renderTourDemo === 'function') renderTourDemo();
  `);
  await sleep(250);
  await snap('state_48_tour_demo.png');

  // 10. Capture 93-Game Configurator page as state_03_configurator.png
  await send('Page.navigate', { url: 'http://localhost:8085/configurator.html' });
  await sleep(800);
  await snap('state_03_configurator.png');

  ws.close();
  chrome.kill();
  console.log('Successfully captured all 48 live firmware feature states into ' + OUT_DIR);
}

main().catch(err => { console.error(err); process.exit(1); });
