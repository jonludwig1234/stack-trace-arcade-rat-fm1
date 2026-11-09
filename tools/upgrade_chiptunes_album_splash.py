import re
import os

print("=== UPGRADING SPLASH SCREEN FOR STACK TRACE'S CHIPTUNES ALBUM ===")

# 1. Update tools/generate_final_simulator.py to embed __STACK_TRACE_ALBUM_B64__
with open("tools/generate_final_simulator.py", "r") as f:
    gen_code = f.read()

if "__STACK_TRACE_ALBUM_B64__" not in gen_code:
    old_avatar_block = """    # 4. Read Stack Trace Avatar Base64
    with open("web/images/stack_trace_avatar_b64.txt", "r") as f:
        avatar_b64 = f.read().strip()"""

    new_avatar_block = """    # 4. Read Stack Trace Avatar Base64
    with open("web/images/stack_trace_avatar_b64.txt", "r") as f:
        avatar_b64 = f.read().strip()

    # 5. Read Stack Trace Chiptunes Album Cover Base64
    with open("web/images/stack_trace_chiptunes_album_b64.txt", "r") as f:
        album_b64 = f.read().strip()"""

    assert old_avatar_block in gen_code, "Cannot find avatar block in generate_final_simulator.py"
    gen_code = gen_code.replace(old_avatar_block, new_avatar_block)
    gen_code = gen_code.replace(
        'html = html.replace("__STACK_TRACE_AVATAR_B64__", avatar_b64)',
        'html = html.replace("__STACK_TRACE_AVATAR_B64__", avatar_b64)\n    html = html.replace("__STACK_TRACE_ALBUM_B64__", album_b64)'
    )
    with open("tools/generate_final_simulator.py", "w") as f:
        f.write(gen_code)
    print("Updated tools/generate_final_simulator.py with album base64 injector!")

# 2. Update tools/build_hardware_template.py
with open("tools/build_hardware_template.py", "r") as f:
    bht = f.read()

# Add Album Splash button in header next to btnReplaySplash
old_header_btn = '<button class="splash-trigger-btn" id="btnReplaySplash" onclick="triggerSplashScreen()">⚡ SPLASH SCREEN</button>'
new_header_btn = '<button class="splash-trigger-btn album-btn" id="btnAlbumSplash" style="background:#2d1738; border-color:#9b59b6; color:#f5cd79; font-weight:800;" onclick="triggerAlbumSplashScreen()" title="View Stack Trace\'s Chiptunes Album Splash Screen">💿 CHIPTUNES ALBUM</button>\n    <button class="splash-trigger-btn" id="btnReplaySplash" onclick="triggerSplashScreen()" title="View Arcade Rat Firmware Boot Splash">⚡ ARCADE SPLASH</button>'

if old_header_btn in bht:
    bht = bht.replace(old_header_btn, new_header_btn, 1)
    print("Added [💿 CHIPTUNES ALBUM] button in header.")

# Add Album Showcase hero card in #shelfDemo
old_shelf_demo_header = """  <!-- Shelf 4: Demo Jukebox -->
  <div class="context-shelf" id="shelfDemo">
    <div class="shelf-header">
      <span>🎵 MULTI-ENGINE FULL DEMO SONGS JUKEBOX · 15-TRACK VU METERS</span>
      <span class="tag" id="shelfJukeStatus">STOPPED</span>
    </div>"""

new_shelf_demo_header = """  <!-- Shelf 4: Demo Jukebox -->
  <div class="context-shelf" id="shelfDemo">
    <div class="shelf-header">
      <span>🎵 MULTI-ENGINE FULL DEMO SONGS JUKEBOX · 15-TRACK VU METERS</span>
      <span class="tag" id="shelfJukeStatus">STOPPED</span>
    </div>

    <!-- Official Chiptunes Album Feature Card -->
    <div class="album-hero-card" style="display:flex; align-items:center; gap:14px; background:linear-gradient(135deg, rgba(29,18,38,0.92) 0%, rgba(14,20,26,0.95) 100%); border:1px solid rgba(155,89,182,0.35); border-radius:6px; padding:8px 12px; margin-bottom:10px;">
      <img src="images/stack_trace_chiptunes_album.jpg" onerror="this.src='data:image/jpeg;base64,__STACK_TRACE_ALBUM_B64__'" style="width:54px; height:54px; border-radius:4px; object-fit:cover; border:1px solid rgba(0,255,102,0.4); cursor:pointer;" onclick="triggerAlbumSplashScreen()" alt="Chiptunes Album Cover" title="Click to view full CRT splash screen!">
      <div style="flex:1;">
        <div style="font-size:0.62rem; color:#aae4c8; font-weight:800; font-family:var(--font-mono); letter-spacing:1.5px;">OFFICIAL ALBUM RELEASE · STACK TRACE_</div>
        <div style="font-size:0.88rem; font-weight:900; color:#f5cd79; letter-spacing:0.8px;">CHIPTUNES YOU DIDN'T KNOW YOU NEEDED TO HEAR</div>
        <div style="font-size:0.62rem; color:#8fa59b; font-family:var(--font-mono); margin-top:2px;">4 Multi-Voice Retro Symphonies · 15 Hardware Chiptune Channels · Z80/POKEY/AY-3-8910</div>
      </div>
      <button class="synth-opt-btn" style="background:#4b2354; border-color:#9b59b6; color:#fff;" onclick="triggerAlbumSplashScreen()">💿 VIEW ALBUM SPLASH</button>
    </div>"""

if old_shelf_demo_header in bht and "album-hero-card" not in bht:
    bht = bht.replace(old_shelf_demo_header, new_shelf_demo_header, 1)
    print("Added Album Showcase card in #shelfDemo.")

# Replace splash screen engine in build_hardware_template.py
old_splash_code = """// -------------------------------------------------------------------------
// STACK TRACE PRESENTS: ARCADE RAT v1.0 - ANIMATED STARTUP SPLASH SCREEN
// -------------------------------------------------------------------------
const splashState = {
  active: true,
  frame: 0,
  maxFrames: 240,
  chimePlayed: false,
  stars: Array.from({length: 28}, () => ({
    x: Math.random() * 240,
    y: Math.random() * 240,
    spd: 0.4 + Math.random() * 1.6,
    size: Math.random() > 0.75 ? 2 : 1
  }))
};

const stackTraceAvatarImg = new Image();
stackTraceAvatarImg.src = "data:image/png;base64,__STACK_TRACE_AVATAR_B64__";
let avatarLoaded = false;
stackTraceAvatarImg.onload = () => { avatarLoaded = true; };

function triggerSplashScreen() {
  initAudio();
  splashState.active = true;
  splashState.frame = 0;
  splashState.chimePlayed = false;
  setMode('arcade');
  playStartupChime();
}

function skipSplashScreen() {
  if (splashState.active) {
    splashState.active = false;
    initAudio();
  }
}

function renderSplashScreen() {
  splashState.frame++;
  const f = splashState.frame;

  if (f === 2 && !splashState.chimePlayed) {
    splashState.chimePlayed = true;
    playStartupChime();
  }

  // Update HUD status banner
  const hud = document.getElementById('hudStatus');
  if (hud) {
    hud.className = 'hud-badge booting';
    hud.textContent = '● STACK TRACE SPLASH';
  }

  // 1. Deep retro CRT dark background
  ctx.fillStyle = '#060a08';
  ctx.fillRect(0, 0, 240, 240);

  // 2. Animated floating cyber stars
  ctx.fillStyle = '#00ff66';
  for (let s of splashState.stars) {
    s.y += s.spd;
    if (s.y > 240) { s.y = 0; s.x = Math.random() * 240; }
    ctx.fillRect(Math.floor(s.x), Math.floor(s.y), s.size, s.size);
  }

  // Stage 1: CRT Electron Beam Ignition (Frames 0 - 25)
  if (f < 25) {
    const beamW = Math.min(240, f * 12);
    const beamH = Math.max(2, 24 - f);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(120 - beamW / 2, 120 - beamH / 2, beamW, beamH);
    ctx.fillStyle = 'rgba(0, 255, 102, 0.4)';
    ctx.fillRect(120 - beamW / 2, 110, beamW, 20);
    return;
  }

  // Stage 2: Avatar Reveal (Frames 25+)
  const cx = 120, cy = 76;
  const avatarR = 34;

  // Draw Stack Trace Avatar - cleanly framed, NO border or artificial rings
  ctx.save();
  ctx.beginPath();
  ctx.arc(cx, cy, avatarR, 0, Math.PI * 2);
  ctx.closePath();
  ctx.clip();
  if (avatarLoaded) {
    ctx.drawImage(stackTraceAvatarImg, cx - avatarR, cy - avatarR, avatarR * 2, avatarR * 2);
  } else {
    ctx.fillStyle = '#0f2415';
    ctx.fillRect(cx - avatarR, cy - avatarR, avatarR * 2, avatarR * 2);
    ctx.fillStyle = '#00ff66';
    ctx.font = 'bold 20px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('ST', cx, cy + 7);
  }
  ctx.restore();

  // Stage 3: Typography Stagger & Branding Reveal
  ctx.textAlign = 'center';

  if (f >= 45) {
    // STACK TRACE
    ctx.save();
    ctx.font = 'bold 12px monospace';
    ctx.fillStyle = '#00ff66';
    ctx.shadowColor = '#00ff66';
    ctx.shadowBlur = 8;
    ctx.fillText('STACK TRACE', cx, 132);
    ctx.restore();
  }

  if (f >= 70) {
    // PRESENTS
    ctx.font = '800 8px monospace';
    ctx.fillStyle = '#a0ffc8';
    ctx.fillText('— PRESENTS —', cx, 146);
  }

  if (f >= 95) {
    // ARCADE RAT
    ctx.save();
    ctx.font = '900 20px -apple-system, monospace';
    ctx.fillStyle = '#f5a623';
    ctx.shadowColor = '#ff6600';
    ctx.shadowBlur = 12;
    ctx.fillText('ARCADE RAT', cx, 172);
    ctx.restore();

    // v 1.0 Badge
    ctx.fillStyle = '#e74c3c';
    ctx.fillRect(cx - 24, 180, 48, 14);
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 9px monospace';
    ctx.fillText('v 1.0', cx, 191);
  }

  // Stage 4: System Diagnostic Readouts (Frames 125+)
  if (f >= 125) {
    ctx.font = '8px monospace';
    ctx.textAlign = 'left';

    const diag = [
      '[OK] Z80 CORE @ 3.072MHz',
      '[OK] 4-CHIP SYNTH STACK',
      '[OK] 12-GAME FLASH VAULT',
      '>> PRESS ANY KEY TO PLAY <<'
    ];
    const linesToShow = Math.min(4, Math.floor((f - 125) / 18) + 1);
    for (let i = 0; i < linesToShow; i++) {
      if (i === 3) {
        if (Math.floor(f / 15) % 2 === 0) {
          ctx.fillStyle = '#f5a623';
          ctx.fillText(diag[i], 36, 208 + i * 10);
        }
      } else {
        ctx.fillStyle = '#00ff88';
        ctx.fillText(diag[i], 36, 208 + i * 10);
      }
    }
  }

  // Stage 5: Transition to Game (Frame 240+)
  if (f >= splashState.maxFrames) {
    splashState.active = false;
    currentMode = 'arcade';
  }
}"""

new_splash_code = """// -------------------------------------------------------------------------
// STACK TRACE: CHIPTUNES ALBUM & ARCADE RAT DUAL-MODE SPLASH SCREEN ENGINE
// -------------------------------------------------------------------------
const splashState = {
  active: true,
  mode: 'album', // 'album' (Stack Trace Chiptunes Album) or 'arcade' (Arcade Rat)
  frame: 0,
  maxFrames: 300,
  chimePlayed: false,
  stars: Array.from({length: 32}, () => ({
    x: Math.random() * 240,
    y: Math.random() * 240,
    spd: 0.5 + Math.random() * 1.8,
    size: Math.random() > 0.7 ? 2 : 1
  }))
};

const stackTraceAvatarImg = new Image();
stackTraceAvatarImg.src = "data:image/png;base64,__STACK_TRACE_AVATAR_B64__";
let avatarLoaded = false;
stackTraceAvatarImg.onload = () => { avatarLoaded = true; };

const stackTraceAlbumImg = new Image();
stackTraceAlbumImg.src = "data:image/jpeg;base64,__STACK_TRACE_ALBUM_B64__";
let albumCoverLoaded = false;
stackTraceAlbumImg.onload = () => { albumCoverLoaded = true; };

function playAlbumStartupChime() {
  if (!audioCtx) return;
  const now = audioCtx.currentTime;

  // Punchy retro 8-bit kick drum
  const kick = audioCtx.createOscillator();
  const kickG = audioCtx.createGain();
  kick.frequency.setValueAtTime(140, now);
  kick.frequency.exponentialRampToValueAtTime(32, now + 0.15);
  kickG.gain.setValueAtTime(0.4, now);
  kickG.gain.exponentialRampToValueAtTime(0.001, now + 0.18);
  kick.connect(kickG);
  kickG.connect(masterGain);
  kick.start(now);
  kick.stop(now + 0.2);

  // Soaring Chiptune Fanfare: C4, G4, C5, E5, G5, B5, C6 (Major 7th Power Arp)
  const arpNotes = [261.63, 392.00, 523.25, 659.25, 783.99, 987.77, 1046.50, 1318.51, 1567.98];
  arpNotes.forEach((freq, idx) => {
    const t = now + 0.08 + idx * 0.045;
    const osc = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    osc.type = idx % 2 === 0 ? 'square' : 'sawtooth';
    osc.frequency.setValueAtTime(freq, t);

    const flt = audioCtx.createBiquadFilter();
    flt.type = 'lowpass';
    flt.frequency.setValueAtTime(3400, t);

    g.gain.setValueAtTime(0.18, t);
    g.gain.exponentialRampToValueAtTime(0.001, t + 0.16);

    osc.connect(flt);
    flt.connect(g);
    g.connect(masterGain);
    osc.start(t);
    osc.stop(t + 0.18);
  });
}

function triggerAlbumSplashScreen() {
  initAudio();
  stopCurrentGame();
  splashState.active = true;
  splashState.mode = 'album';
  splashState.frame = 0;
  splashState.chimePlayed = false;
  playAlbumStartupChime();
}

function triggerSplashScreen() {
  initAudio();
  stopCurrentGame();
  splashState.active = true;
  splashState.mode = 'arcade';
  splashState.frame = 0;
  splashState.chimePlayed = false;
  setMode('arcade');
  playStartupChime();
}

function skipSplashScreen() {
  if (splashState.active) {
    const wasAlbum = (splashState.mode === 'album');
    splashState.active = false;
    initAudio();
    if (wasAlbum) {
      if (typeof setStudioTab === 'function') setStudioTab('demo');
      else setMode('demo');
      playDemoSong();
    }
  }
}

function renderSplashScreen() {
  splashState.frame++;
  const f = splashState.frame;

  if (splashState.mode === 'album') {
    renderAlbumSplashScreen(f);
  } else {
    renderArcadeSplashScreen(f);
  }
}

// -------------------------------------------------------------------------
// STACK TRACE: CHIPTUNES ALBUM SPLASH SCREEN (OFFICIAL ARTWORK & EQUALIZER)
// -------------------------------------------------------------------------
function renderAlbumSplashScreen(f) {
  if (f === 2 && !splashState.chimePlayed) {
    splashState.chimePlayed = true;
    playAlbumStartupChime();
  }

  // Update HUD status banner
  const hud = document.getElementById('hudStatus');
  if (hud) {
    hud.className = 'hud-badge booting';
    hud.textContent = '● STACK TRACE · CHIPTUNES ALBUM';
  }

  // 1. Deep retro CRT dark background
  ctx.fillStyle = '#050807';
  ctx.fillRect(0, 0, 240, 240);

  // Stage 1: CRT Raster Beam Ignition (Frames 0 - 18)
  if (f < 18) {
    const beamW = Math.min(240, f * 14);
    const beamH = Math.max(2, 22 - f);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(120 - beamW / 2, 120 - beamH / 2, beamW, beamH);
    ctx.fillStyle = 'rgba(0, 255, 102, 0.45)';
    ctx.fillRect(120 - beamW / 2, 110, beamW, 20);
    return;
  }

  // Stage 2: Draw Full Square High-Res Album Cover Artwork (Frames 18+)
  if (albumCoverLoaded && stackTraceAlbumImg.complete && stackTraceAlbumImg.naturalWidth > 0) {
    ctx.save();
    // Subtle breathing pulse / zoom on reveal
    let scale = 1.0;
    if (f < 45) {
      scale = 0.94 + (f - 18) / 27 * 0.06;
    }
    const drawW = 240 * scale;
    const drawH = 240 * scale;
    const offX = (240 - drawW) / 2;
    const offY = (240 - drawH) / 2;
    ctx.drawImage(stackTraceAlbumImg, offX, offY, drawW, drawH);
    ctx.restore();
  } else {
    // Vector fallback if image loading
    renderAlbumVectorFallback(f);
  }

  // Stage 3: Live Equalizer Visualizer & Phosphor Shimmer (Frames 35+)
  if (f >= 35) {
    // Bottom translucent cyber telemetry bar
    const barAlpha = Math.min(0.88, (f - 35) / 25 * 0.88);
    ctx.fillStyle = `rgba(6, 10, 12, ${barAlpha})`;
    ctx.fillRect(0, 194, 240, 46);

    // Phosphor green border line
    ctx.strokeStyle = 'rgba(0, 255, 102, 0.6)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, 194);
    ctx.lineTo(240, 194);
    ctx.stroke();

    // 16 Bouncing Equalizer Bars
    for (let b = 0; b < 16; b++) {
      const bx = 10 + b * 14;
      const h = Math.abs(Math.sin((f * 0.14) + b * 0.65)) * 14 + (b % 3 === 0 ? 4 : 2);
      ctx.fillStyle = b < 5 ? '#00ff66' : (b < 11 ? '#00e5ff' : '#ff4757');
      ctx.fillRect(bx, 208 - h, 10, h);
    }

    // Glowing Album Callout Typography
    ctx.save();
    ctx.textAlign = 'center';
    ctx.font = 'bold 8px monospace';
    ctx.fillStyle = '#00ff66';
    ctx.shadowColor = '#00ff66';
    ctx.shadowBlur = 6;
    ctx.fillText('STACK TRACE_ · CHIPTUNES LP', 120, 218);
    ctx.restore();

    // Flashing Action Prompt
    const pulse = Math.floor(f / 16) % 2 === 0;
    ctx.fillStyle = pulse ? '#fffa65' : '#ffffff';
    ctx.font = 'bold 8px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('⚡ PRESS SPACE / ANY KEY TO PLAY', 120, 232);
    ctx.textAlign = 'left';
  }

  // Auto-transition after maxFrames (300 frames = ~5s)
  if (f >= splashState.maxFrames) {
    splashState.active = false;
    if (typeof setStudioTab === 'function') setStudioTab('demo');
    else setMode('demo');
    playDemoSong();
  }
}

function renderAlbumVectorFallback(f) {
  ctx.fillStyle = '#0c1015';
  ctx.fillRect(0, 0, 240, 240);
  ctx.fillStyle = '#00ff66';
  ctx.textAlign = 'center';
  ctx.font = 'bold 16px monospace';
  ctx.fillText('CHIPTUNES', 120, 70);
  ctx.font = 'bold 9px monospace';
  ctx.fillStyle = '#a0ffc8';
  ctx.fillText('YOU DIDN\\'T KNOW YOU NEEDED TO HEAR', 120, 90);
  ctx.fillStyle = '#00e5ff';
  ctx.font = 'bold 10px monospace';
  ctx.fillText('STACK TRACE_', 120, 150);
}

// -------------------------------------------------------------------------
// STACK TRACE: ARCADE RAT FIRMWARE BOOT SPLASH SCREEN
// -------------------------------------------------------------------------
function renderArcadeSplashScreen(f) {
  if (f === 2 && !splashState.chimePlayed) {
    splashState.chimePlayed = true;
    playStartupChime();
  }

  // Update HUD status banner
  const hud = document.getElementById('hudStatus');
  if (hud) {
    hud.className = 'hud-badge booting';
    hud.textContent = '● STACK TRACE SPLASH';
  }

  // 1. Deep retro CRT dark background
  ctx.fillStyle = '#060a08';
  ctx.fillRect(0, 0, 240, 240);

  // 2. Animated floating cyber stars
  ctx.fillStyle = '#00ff66';
  for (let s of splashState.stars) {
    s.y += s.spd;
    if (s.y > 240) { s.y = 0; s.x = Math.random() * 240; }
    ctx.fillRect(Math.floor(s.x), Math.floor(s.y), s.size, s.size);
  }

  // Stage 1: CRT Electron Beam Ignition (Frames 0 - 25)
  if (f < 25) {
    const beamW = Math.min(240, f * 12);
    const beamH = Math.max(2, 24 - f);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(120 - beamW / 2, 120 - beamH / 2, beamW, beamH);
    ctx.fillStyle = 'rgba(0, 255, 102, 0.4)';
    ctx.fillRect(120 - beamW / 2, 110, beamW, 20);
    return;
  }

  // Stage 2: Avatar Reveal (Frames 25+)
  const cx = 120, cy = 76;
  const avatarR = 34;

  // Draw Stack Trace Avatar - cleanly framed, NO border or artificial rings
  ctx.save();
  ctx.beginPath();
  ctx.arc(cx, cy, avatarR, 0, Math.PI * 2);
  ctx.closePath();
  ctx.clip();
  if (avatarLoaded) {
    ctx.drawImage(stackTraceAvatarImg, cx - avatarR, cy - avatarR, avatarR * 2, avatarR * 2);
  } else {
    ctx.fillStyle = '#0f2415';
    ctx.fillRect(cx - avatarR, cy - avatarR, avatarR * 2, avatarR * 2);
    ctx.fillStyle = '#00ff66';
    ctx.font = 'bold 20px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('ST', cx, cy + 7);
  }
  ctx.restore();

  // Stage 3: Typography Stagger & Branding Reveal
  ctx.textAlign = 'center';

  if (f >= 45) {
    ctx.save();
    ctx.font = 'bold 12px monospace';
    ctx.fillStyle = '#00ff66';
    ctx.shadowColor = '#00ff66';
    ctx.shadowBlur = 8;
    ctx.fillText('STACK TRACE', cx, 132);
    ctx.restore();
  }

  if (f >= 70) {
    ctx.font = '800 8px monospace';
    ctx.fillStyle = '#a0ffc8';
    ctx.fillText('— PRESENTS —', cx, 146);
  }

  if (f >= 95) {
    ctx.save();
    ctx.font = '900 20px -apple-system, monospace';
    ctx.fillStyle = '#f5a623';
    ctx.shadowColor = '#ff6600';
    ctx.shadowBlur = 12;
    ctx.fillText('ARCADE RAT', cx, 172);
    ctx.restore();

    ctx.fillStyle = '#e74c3c';
    ctx.fillRect(cx - 24, 180, 48, 14);
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 9px monospace';
    ctx.fillText('v 1.0', cx, 191);
  }

  // Stage 4: System Diagnostic Readouts (Frames 125+)
  if (f >= 125) {
    ctx.font = '8px monospace';
    ctx.textAlign = 'left';

    const diag = [
      '[OK] Z80 CORE @ 3.072MHz',
      '[OK] 4-CHIP SYNTH STACK',
      '[OK] 12-GAME FLASH VAULT',
      '>> PRESS ANY KEY TO PLAY <<'
    ];
    const linesToShow = Math.min(4, Math.floor((f - 125) / 18) + 1);
    for (let i = 0; i < linesToShow; i++) {
      if (i === 3) {
        if (Math.floor(f / 15) % 2 === 0) {
          ctx.fillStyle = '#f5a623';
          ctx.fillText(diag[i], 36, 208 + i * 10);
        }
      } else {
        ctx.fillStyle = '#00ff88';
        ctx.fillText(diag[i], 36, 208 + i * 10);
      }
    }
  }

  // Stage 5: Transition to Game (Frame 240+)
  if (f >= splashState.maxFrames) {
    splashState.active = false;
    currentMode = 'arcade';
  }
}"""

# Check for query param overrides to support ?album=1 or ?splash=album
old_query_param = """    if (params.get('nosplash') === '1') {
      splashState.active = false;
    }"""

new_query_param = """    if (params.get('nosplash') === '1') {
      splashState.active = false;
    }
    if (params.get('album') === '1' || params.get('splash') === 'album') {
      triggerAlbumSplashScreen();
    }
    if (params.get('splash') === 'arcade') {
      triggerSplashScreen();
    }"""

# Replace in bht
s_spl = bht.find("const splashState = {")
e_spl = bht.find("// -------------------------------------------------------------------------\n// ACTIVE ARCADE GAME & CRAZY CLIMBER ENGINE")

assert s_spl != -1 and e_spl != -1 and s_spl < e_spl, f"Splash block not found in build_hardware_template.py (s={s_spl}, e={e_spl})"
bht = bht[:s_spl] + new_splash_code + "\n\n" + bht[e_spl:]
print("Replaced splash screen engine with Dual-Mode (Chiptunes Album + Arcade Rat).")

if old_query_param in bht:
    bht = bht.replace(old_query_param, new_query_param, 1)
    print("Added URL parameter support for ?album=1 and ?splash=album.")

with open("tools/build_hardware_template.py", "w") as f:
    f.write(bht)

print("Saved updated tools/build_hardware_template.py!")
