import re

# Read current build_hardware_template.py
with open("tools/build_hardware_template.py", "r") as f:
    bht = f.read()

# We want to replace the old renderArcadeFrame downsampling and the tour game renderers
# with the upgraded pixel-art and vector graphics engines.

arcade_frame_upgrade = '''// High-Fidelity Arcade Display Pipeline
const osCanvas = (typeof document !== 'undefined' && document.createElement) ? document.createElement('canvas') : null;
if (osCanvas) {
  osCanvas.width = 224;
  osCanvas.height = 288;
}
const osCtx = (osCanvas && osCanvas.getContext) ? osCanvas.getContext('2d') : null;
const osImgData = (osCtx && osCtx.createImageData) ? osCtx.createImageData(224, 288) : null;
const osBuf32 = osImgData ? new Uint32Array(osImgData.data.buffer) : null;

function renderArcadeFrame() {
  arcadeBuf.fill(0xff000000);
  
  // Tiles: Bottom 2 rows
  for (let i = 0x00; i <= 0x03f; i++) {
    drawTile(ram[i], ram[i + 0x400], (29 - (i % 0x20)) * 8, (i >= 0x20 ? 35 : 34) * 8);
  }
  // Tiles: Middle section
  for (let i = 0x40; i <= 0x3bf; i++) {
    drawTile(ram[i], ram[i + 0x400], (29 - Math.floor(i / 0x20)) * 8, (2 + (i % 0x20)) * 8);
  }
  // Tiles: Top 2 rows
  for (let i = 0x3c0; i <= 0x3ff; i++) {
    drawTile(ram[i], ram[i + 0x400], (29 - (i % 0x20)) * 8, (i >= 0x3e0 ? 1 : 0) * 8);
  }

  // 8 Hardware Sprites
  for (let s = 7; s >= 0; s--) {
    const sx = 239 - spritePos[s * 2];
    const sy = 272 - spritePos[s * 2 + 1];
    const info = ram[0x0ff0 + s * 2];
    const pal = ram[0x0ff0 + s * 2 + 1];
    drawSprite(info >> 2, pal, sx, sy, (info >> 1) & 1, info & 1);
  }

  // High-Fidelity Rendering:
  // In real browser, use hardware bilinear anti-aliased scaling
  // so NO scanlines are dropped, maze walls and text stay razor-sharp!
  if (osCtx && osBuf32 && ctx && ctx.drawImage) {
    osBuf32.set(arcadeBuf);
    osCtx.putImageData(osImgData, 0, 0);
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, 240, 240);
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(osCanvas, 0, 0, 224, 288, 8, 0, 224, 240);
    if (crtScanlines) drawScanlines();
  } else {
    // Fallback for headless environments
    buf32.fill(0xff08090c);
    for (let outY = 0; outY < 240; outY++) {
      const inY = Math.floor(outY * 6 / 5);
      const inRow = inY * 224;
      const outRow = outY * 240 + 8;
      for (let outX = 0; outX < 224; outX++) {
        buf32[outRow + outX] = arcadeBuf[inRow + outX];
      }
    }
    if (ctx && ctx.putImageData) ctx.putImageData(imgData, 0, 0);
  }
}'''

high_fidelity_games_code = '''// =========================================================================
// HIGH-FIDELITY ARCADE GAME RENDERERS (Pixel-Art, Vector CRT & 3D Shaders)
// =========================================================================

function renderCrazyClimber() {
  climberState.animTick++;
  const tick = climberState.animTick;

  // Dusk Sky gradient
  const skyGrad = ctx.createLinearGradient(0, 0, 0, 240);
  skyGrad.addColorStop(0, '#0c1020');
  skyGrad.addColorStop(1, '#1e272e');
  ctx.fillStyle = skyGrad;
  ctx.fillRect(0, 0, 240, 240);

  // Distant City Skyline
  ctx.fillStyle = '#0a0d16';
  ctx.fillRect(4, 180, 22, 60);
  ctx.fillRect(14, 160, 10, 80);
  ctx.fillRect(218, 175, 18, 65);

  // Skyscraper Main Facade (x: 26 to 214)
  const bldgGrad = ctx.createLinearGradient(26, 0, 214, 0);
  bldgGrad.addColorStop(0, '#8c532b');
  bldgGrad.addColorStop(0.5, '#a05c30');
  bldgGrad.addColorStop(1, '#6d3e1d');
  ctx.fillStyle = bldgGrad;
  ctx.fillRect(26, 0, 188, 240);

  // Left & Right Limestone Art-Deco Pilasters
  ctx.fillStyle = '#dcdde1';
  ctx.fillRect(26, 0, 10, 240);
  ctx.fillRect(204, 0, 10, 240);
  ctx.fillStyle = '#718093';
  ctx.fillRect(35, 0, 2, 240);
  ctx.fillRect(203, 0, 2, 240);

  // Horizontal Stone Floor Ledges
  for (let fl = 0; fl < 7; fl++) {
    const ly = (fl * 38 + (climberState.floor * 2) % 38) % 240;
    ctx.fillStyle = '#2f3542';
    ctx.fillRect(26, ly, 188, 3);
    ctx.fillStyle = '#f1f2f6';
    ctx.fillRect(26, ly + 3, 188, 1);
  }

  // 4 Columns of Authentic Double-Hung Windows
  const windowCols = [44, 84, 124, 164];
  for (let row = -1; row < 7; row++) {
    const wy = (row * 38 + (climberState.floor * 2) % 38);
    if (wy < -35 || wy > 240) continue;

    for (let c = 0; c < 4; c++) {
      const wx = windowCols[c];
      const isOpen = (row + c + (tick >> 6)) % 3 === 0;

      // Stone sill & frame
      ctx.fillStyle = '#1e272e';
      ctx.fillRect(wx - 2, wy - 2, 32, 30);
      ctx.fillStyle = '#dfe4ea';
      ctx.fillRect(wx - 3, wy + 26, 34, 3); // Lower stone sill
      ctx.fillStyle = '#2f3542';
      ctx.fillRect(wx - 3, wy + 29, 34, 1); // Sill shadow

      // Glass pane
      if (isOpen) {
        // Open window with dark room and curtain
        ctx.fillStyle = '#05070a';
        ctx.fillRect(wx, wy, 28, 26);
        ctx.fillStyle = '#e58e26'; // Interior warm lamp glow
        ctx.fillRect(wx + 8, wy + 4, 12, 10);
        ctx.fillStyle = '#f8c291'; // Silhouette curtain
        ctx.fillRect(wx + 2, wy, 5, 20);
      } else {
        // Closed double-hung glass with reflection glints
        ctx.fillStyle = '#1b76bc';
        ctx.fillRect(wx, wy, 28, 26);
        ctx.fillStyle = '#4bcffa';
        ctx.fillRect(wx + 2, wy + 2, 24, 10); // Upper pane
        ctx.fillRect(wx + 2, wy + 14, 24, 10); // Lower pane
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(wx + 4, wy + 3, 18, 2); // Glass shine
        ctx.fillRect(wx + 2, wy + 12, 24, 2); // Horizontal sash bar
        ctx.fillRect(wx + 13, wy + 2, 2, 22); // Vertical sash bar
      }
    }
  }

  // King Kong / Giant Ape on Left Girder (x: 4 to 34)
  const kongY = 65 + Math.sin(tick * 0.08) * 12;
  const kongArmUp = (tick % 40 < 20);
  ctx.save();
  ctx.translate(2, kongY);
  // Ape Body & Fur
  ctx.fillStyle = '#2f3542';
  ctx.fillRect(6, 12, 24, 28);
  ctx.fillStyle = '#1e272e';
  ctx.fillRect(8, 14, 20, 24);
  // Ape Head & Roar
  ctx.fillStyle = '#2f3542';
  ctx.fillRect(10, 0, 18, 14);
  ctx.fillStyle = '#e74c3c'; // Roaring mouth
  ctx.fillRect(14, 8, 10, 5);
  ctx.fillStyle = '#ffffff'; // Fangs
  ctx.fillRect(15, 8, 2, 2);
  ctx.fillRect(21, 8, 2, 2);
  ctx.fillStyle = '#f1c40f'; // Eyes
  ctx.fillRect(13, 3, 3, 3);
  ctx.fillRect(20, 3, 3, 3);
  // Pounding Fists
  ctx.fillStyle = '#57606f';
  ctx.fillRect(kongArmUp ? 0 : 2, kongArmUp ? 2 : 24, 8, 10);
  ctx.fillRect(kongArmUp ? 24 : 26, kongArmUp ? 24 : 2, 8, 10);
  ctx.restore();

  // Falling Terracotta Flower Pot
  climberState.potY += 2.2;
  if (climberState.potY > 240) {
    climberState.potY = -15;
    climberState.potCol = Math.floor(Math.random() * 4);
  }
  const potX = windowCols[climberState.potCol] + 8;
  const potY = climberState.potY;
  if (potY >= 0 && potY < 235) {
    // Flower blossoms
    ctx.fillStyle = '#e84393';
    ctx.beginPath();
    ctx.arc(potX + 6, potY - 3, 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#2ecc71'; // Leaves
    ctx.fillRect(potX + 1, potY - 2, 10, 3);
    // Terracotta Pot
    ctx.fillStyle = '#e17055';
    ctx.fillRect(potX, potY, 12, 3); // Rim
    ctx.fillRect(potX + 2, potY + 3, 8, 8); // Base
  }

  // The Climber Character (Nichibutsu Arcade Pixel Art)
  const cx = windowCols[climberState.col] + 3;
  const cy = 130;
  const leftArmUp = (climberState.leftArm === 'up');
  const rightArmUp = (climberState.rightArm === 'up');

  // Shadow under climber
  ctx.fillStyle = 'rgba(0,0,0,0.45)';
  ctx.fillRect(cx - 2, cy + 32, 26, 4);

  // Boots
  ctx.fillStyle = '#795548';
  ctx.fillRect(cx + 2, cy + 28, 7, 4);
  ctx.fillRect(cx + 13, cy + 28, 7, 4);

  // Blue Overalls / Dungarees
  ctx.fillStyle = '#1e3799';
  ctx.fillRect(cx + 4, cy + 18, 14, 11);
  ctx.fillStyle = '#4a69bd';
  ctx.fillRect(cx + 5, cy + 13, 3, 7); // Left suspender
  ctx.fillRect(cx + 14, cy + 13, 3, 7); // Right suspender
  ctx.fillStyle = '#f1c40f'; // Brass buttons
  ctx.fillRect(cx + 5, cy + 19, 2, 2);
  ctx.fillRect(cx + 15, cy + 19, 2, 2);

  // Red Shirt & Torso
  ctx.fillStyle = '#eb2f06';
  ctx.fillRect(cx + 3, cy + 12, 16, 7);

  // Dynamic Climbing Arms & Hands
  // Left Arm
  ctx.fillStyle = '#eb2f06';
  ctx.fillRect(cx - 3, leftArmUp ? cy - 4 : cy + 12, 5, 14);
  ctx.fillStyle = '#f8c291'; // Glove
  ctx.fillRect(cx - 4, leftArmUp ? cy - 8 : cy + 24, 6, 6);

  // Right Arm
  ctx.fillStyle = '#eb2f06';
  ctx.fillRect(cx + 20, rightArmUp ? cy - 4 : cy + 12, 5, 14);
  ctx.fillStyle = '#f8c291'; // Glove
  ctx.fillRect(cx + 20, rightArmUp ? cy - 8 : cy + 24, 6, 6);

  // Face
  ctx.fillStyle = '#f8c291';
  ctx.fillRect(cx + 5, cy + 4, 12, 9);
  ctx.fillStyle = '#000000'; // Eyes
  ctx.fillRect(cx + 8, cy + 6, 2, 3);
  ctx.fillRect(cx + 13, cy + 6, 2, 3);

  // Yellow Safety Helmet
  ctx.fillStyle = '#f1c40f';
  ctx.fillRect(cx + 3, cy - 2, 16, 7);
  ctx.fillStyle = '#f39c12';
  ctx.fillRect(cx + 1, cy + 3, 20, 2); // Brim

  // CRT Scanlines
  if (crtScanlines) drawScanlines();

  // Nichibutsu Arcade HUD
  ctx.fillStyle = 'rgba(10, 14, 20, 0.85)';
  ctx.fillRect(0, 0, 240, 22);
  ctx.fillStyle = '#f5a623';
  ctx.font = 'bold 10px monospace';
  ctx.fillText(`1UP: ${climberState.score}`, 10, 15);
  ctx.fillStyle = '#00e5ff';
  ctx.fillText(`HIGH: 050000`, 90, 15);
  ctx.fillStyle = '#2ecc71';
  ctx.fillText(`${climberState.floor}F`, 198, 15);

  // Twin-Stick Status Pill at bottom
  ctx.fillStyle = 'rgba(10, 14, 20, 0.9)';
  ctx.fillRect(0, 222, 240, 18);
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 9px monospace';
  ctx.fillText(`TWIN-STICK: L[${climberState.leftArm.toUpperCase()}] R[${climberState.rightArm.toUpperCase()}]  COL:${climberState.col + 1}/4`, 14, 234);
}

// -------------------------------------------------------------------------
// INSTALLED ROMS ATTRACT TOUR DEMO ENGINE (High-Fidelity Suite)
// -------------------------------------------------------------------------
const tourState = {
  active: false,
  gameIdx: 0,
  frameInGame: 0,
  framesPerGame: 540,
  games: [
    { id: 'pacman', title: 'PAC-MAN', year: '1980 NAMCO', cpu: 'Z80 @ 3.072 MHz', sound: 'Namco WSG (3-ch Wavetable)', badge: 'MAZE CHASE' },
    { id: 'cclimber', title: 'CRAZY CLIMBER', year: '1980 NICHIBUTSU', cpu: 'Z80 @ 3.072 MHz', sound: 'AY-3-8910 PSG (Twin-Stick)', badge: 'VERTICAL CLIMB' },
    { id: 'galaga', title: 'GALAGA', year: '1981 NAMCO', cpu: '3× Z80 Cores', sound: 'Namco WSG 3-Voice Soundchip', badge: 'SPACE SHOOTER' },
    { id: 'dkong', title: 'DONKEY KONG', year: '1981 NINTENDO', cpu: 'Z80 + I8035 Co-processor', sound: 'Discrete DAC & Jump FX', badge: 'PLATFORM ICON' },
    { id: 'frogger', title: 'FROGGER', year: '1981 KONAMI', cpu: '2× Z80 Processors', sound: 'AY-3-8910 Chiptune Jingles', badge: 'TRAFFIC & RIVER' },
    { id: 'asteroids', title: 'ASTEROIDS', year: '1979 ATARI', cpu: 'MOS 6502 @ 1.5 MHz', sound: 'Discrete Analog Thruster / Saucer', badge: 'VECTOR GLOW' },
    { id: 'tempest', title: 'TEMPEST', year: '1981 ATARI', cpu: 'MOS 6502 + Math Box', sound: 'Dual Atari POKEY Soundchips', badge: 'ROTARY TUBE' },
    { id: 'gyruss', title: 'GYRUSS', year: '1983 KONAMI', cpu: '2× Z80 + 6809 Sound CPU', sound: '5× AY-3-8910 (15-Ch Orchestral)', badge: '360° COSMIC ODYSSEY' }
  ]
};

function toggleTourDemo() {
  initAudio();
  if (currentMode === 'tour') setMode('arcade'); else setMode('tour');
}

function nextTourGame() {
  initAudio();
  tourState.frameInGame = 0;
  tourState.gameIdx = (tourState.gameIdx + 1) % tourState.games.length;
  playArcadeSfx('WARP');
}

function prevTourGame() {
  initAudio();
  tourState.frameInGame = 0;
  tourState.gameIdx = (tourState.gameIdx - 1 + tourState.games.length) % tourState.games.length;
  playArcadeSfx('WARP');
}

function launchCurrentTourGame() {
  const g = tourState.games[tourState.gameIdx];
  tourState.active = false;
  if (g.id === 'cclimber') switchActiveGame('cclimber'); else switchActiveGame('pacman');
  setMode('arcade');
  ensurePastBoot();
  insertCoin();
  setTimeout(start1P, 200);
}

// 1. GALAGA: True 1981 Namco Pixel Art & Starfield
function renderGalagaTour(f) {
  ctx.fillStyle = '#020408';
  ctx.fillRect(0, 0, 240, 240);

  // 3-Speed Multi-Color Starfield
  for (let i = 0; i < 42; i++) {
    const sx = (i * 47 + (i % 5) * 19) % 240;
    const spd = (i % 3 === 0) ? 2.5 : ((i % 2 === 0) ? 1.4 : 0.7);
    const sy = Math.floor((f * spd + i * 23) % 240);
    const col = (i % 6 === 0) ? '#ff5252' : ((i % 4 === 0) ? '#00e5ff' : ((i % 3 === 0) ? '#f1c40f' : '#ffffff'));
    ctx.fillStyle = col;
    ctx.fillRect(sx, sy, i % 5 === 0 ? 2 : 1, i % 5 === 0 ? 2 : 1);
  }

  // Dual Player Fighters (Docked)
  const px = 120 + Math.sin(f * 0.035) * 45;
  const py = 198;
  [-11, 5].forEach(ox => {
    const fx = px + ox;
    ctx.fillStyle = '#ffffff'; // White Fuselage
    ctx.fillRect(fx + 4, py, 4, 14);
    ctx.fillStyle = '#e74c3c'; // Red Wings
    ctx.fillRect(fx, py + 8, 12, 4);
    ctx.fillRect(fx + 2, py + 12, 2, 4);
    ctx.fillRect(fx + 8, py + 12, 2, 4);
    ctx.fillStyle = '#00a8ff'; // Cockpit
    ctx.fillRect(fx + 5, py + 4, 2, 4);
  });

  // Dual Laser Fire with Glow
  const ly = py - ((f * 10) % 175);
  ctx.fillStyle = '#00ffff';
  ctx.shadowColor = '#00ffff';
  ctx.shadowBlur = 6;
  ctx.fillRect(px - 7, ly, 2, 10);
  ctx.fillRect(px + 9, ly, 2, 10);
  ctx.shadowBlur = 0;

  // Fleet Formation (Bees, Butterflies, Bosses)
  const alienColors = ['#f1c40f', '#e74c3c', '#2ecc71'];
  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 6; c++) {
      const ax = 36 + c * 28 + Math.sin(f * 0.05 + r) * 7;
      const ay = 34 + r * 20;
      const wingOpen = (f + c * 10) % 30 < 15;
      
      // Alien Sprite Pixel Art
      ctx.fillStyle = alienColors[r];
      ctx.fillRect(ax - 5, ay - 3, 10, 6);
      ctx.fillStyle = '#ffffff'; // Eyes
      ctx.fillRect(ax - 3, ay - 2, 2, 2);
      ctx.fillRect(ax + 1, ay - 2, 2, 2);
      ctx.fillStyle = '#3498db'; // Wings
      if (wingOpen) {
        ctx.fillRect(ax - 7, ay - 4, 2, 4);
        ctx.fillRect(ax + 5, ay - 4, 2, 4);
      } else {
        ctx.fillRect(ax - 6, ay, 2, 4);
        ctx.fillRect(ax + 4, ay, 2, 4);
      }
    }
  }

  // Diving Boss Galaga with Tractor Beam
  const diveX = 120 + Math.sin(f * 0.05) * 60;
  const diveY = 40 + (f * 2.5) % 150;
  ctx.fillStyle = '#2ecc71'; // Green carapace
  ctx.fillRect(diveX - 7, diveY - 6, 14, 12);
  ctx.fillStyle = '#f1c40f'; // Horns
  ctx.fillRect(diveX - 5, diveY - 8, 3, 3);
  ctx.fillRect(diveX + 2, diveY - 8, 3, 3);
  ctx.fillStyle = '#3498db'; // Wings
  ctx.fillRect(diveX - 9, diveY - 3, 3, 6);
  ctx.fillRect(diveX + 6, diveY - 3, 3, 6);

  // Concentric Expanding Holographic Tractor Beam
  if (f % 180 > 40 && f % 180 < 120) {
    const beamProgress = ((f % 180) - 40) / 80;
    for (let ring = 0; ring < 6; ring++) {
      const ry = diveY + 8 + ring * 22;
      const rx = 12 + ring * 9;
      if (ry < 230) {
        ctx.strokeStyle = `rgba(0, 229, 255, ${0.7 - ring * 0.1})`;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.ellipse(diveX, ry, rx, rx * 0.35, 0, 0, Math.PI * 2);
        ctx.stroke();
      }
    }
    if (f % 45 === 0) playArcadeSfx('TRACT');
  }

  if (crtScanlines) drawScanlines();
  if (f % 90 === 30) playArcadeSfx('DIVE');
}

// 2. DONKEY KONG: True 1981 Nintendo Sloped Girders & Pixel Art
function renderDonkeyKongTour(f) {
  ctx.fillStyle = '#060608';
  ctx.fillRect(0, 0, 240, 240);

  // Sloped Pink Steel Girders with Truss Bracing
  const girders = [
    { x: 18, y: 70, w: 204, slope: 4 },
    { x: 18, y: 118, w: 204, slope: -4 },
    { x: 18, y: 166, w: 204, slope: 4 },
    { x: 18, y: 216, w: 204, slope: -2 }
  ];
  girders.forEach(g => {
    ctx.fillStyle = '#e84393';
    ctx.fillRect(g.x, g.y, g.w, 7);
    ctx.fillStyle = '#fd79a8';
    ctx.fillRect(g.x, g.y, g.w, 1); // Highlight
    // Diamond Cross Bracing
    for (let x = g.x + 8; x < g.x + g.w - 8; x += 16) {
      ctx.fillStyle = '#d63031';
      ctx.fillRect(x, g.y + 1, 2, 5);
      ctx.fillRect(x + 6, g.y + 1, 2, 5);
    }
  });

  // Blue Ladders with Broken Rungs
  const ladders = [
    { x: 194, y: 72, h: 48 },
    { x: 44, y: 116, h: 52 },
    { x: 182, y: 168, h: 48 }
  ];
  ladders.forEach(l => {
    ctx.fillStyle = '#0984e3';
    ctx.fillRect(l.x, l.y, 2, l.h);
    ctx.fillRect(l.x + 12, l.y, 2, l.h);
    for (let r = l.y + 4; r < l.y + l.h; r += 7) {
      ctx.fillRect(l.x, r, 14, 2);
    }
  });

  // Donkey Kong 32x28 Pixel Art
  ctx.save();
  ctx.translate(34, 42);
  const dkPound = (f % 40 < 20);
  ctx.fillStyle = '#6d4c41'; // Fur
  ctx.fillRect(4, 8, 24, 20);
  ctx.fillStyle = '#ffb74d'; // Chest
  ctx.fillRect(8, 12, 16, 14);
  // Brow & Face
  ctx.fillStyle = '#6d4c41';
  ctx.fillRect(6, 0, 20, 10);
  ctx.fillStyle = '#ffb74d';
  ctx.fillRect(8, 4, 16, 6);
  ctx.fillStyle = '#000000'; // Eyes
  ctx.fillRect(10, 4, 2, 2);
  ctx.fillRect(18, 4, 2, 2);
  ctx.fillStyle = '#d32f2f'; // Mouth
  ctx.fillRect(11, 7, 10, 3);
  // Arms
  ctx.fillStyle = '#5d4037';
  ctx.fillRect(dkPound ? 0 : 2, dkPound ? 2 : 16, 6, 12);
  ctx.fillRect(dkPound ? 26 : 24, dkPound ? 16 : 2, 6, 12);
  ctx.restore();

  // Pauline / Lady with "HELP!" Bubble
  ctx.fillStyle = '#ffeaa7';
  ctx.fillRect(114, 42, 6, 6); // Head
  ctx.fillStyle = '#fd79a8';
  ctx.fillRect(112, 48, 10, 18); // Pink dress
  // Speech bubble
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(128, 38, 32, 14);
  ctx.fillStyle = '#d63031';
  ctx.font = 'bold 8px monospace';
  ctx.fillText('HELP!', 132, 48);

  // Rolling Barrels with Metal Hoops
  const barrelX = 210 - (f * 1.8) % 180;
  ctx.save();
  ctx.translate(barrelX, 210);
  ctx.fillStyle = '#b7791f';
  ctx.beginPath();
  ctx.arc(0, 0, 6, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = '#2d3748';
  ctx.lineWidth = 1.5;
  ctx.stroke();
  ctx.restore();

  // Jumpman / Mario 16x16 Sprite
  const mx = 35 + (f * 1.4) % 155;
  const isJumping = (Math.abs(mx - barrelX) < 26);
  const my = isJumping ? 190 : 204;
  ctx.fillStyle = '#d63031'; // Red Cap
  ctx.fillRect(mx - 3, my - 13, 8, 3);
  ctx.fillStyle = '#ffb74d'; // Face & Nose
  ctx.fillRect(mx - 2, my - 10, 7, 4);
  ctx.fillStyle = '#000000'; // Mustache
  ctx.fillRect(mx, my - 7, 5, 2);
  ctx.fillStyle = '#0984e3'; // Blue Shirt
  ctx.fillRect(mx - 4, my - 6, 9, 5);
  ctx.fillStyle = '#d63031'; // Red Overalls
  ctx.fillRect(mx - 3, my - 2, 7, 6);

  if (isJumping && f % 40 === 0) playArcadeSfx('DK-JUMP');
  if (crtScanlines) drawScanlines();
}

// 3. FROGGER: True 1981 Konami River, Highway & Swimming Turtles
function renderFroggerTour(f) {
  ctx.fillStyle = '#05070e';
  ctx.fillRect(0, 0, 240, 240);

  // River Bank with 5 Home Bays
  ctx.fillStyle = '#009432';
  ctx.fillRect(0, 24, 240, 16);
  const bayX = [20, 68, 116, 164, 212];
  bayX.forEach(bx => {
    ctx.fillStyle = '#0652dd';
    ctx.fillRect(bx - 8, 24, 16, 16);
    ctx.fillStyle = '#2ed573'; // Lilypad
    ctx.beginPath();
    ctx.arc(bx, 32, 6, 0, Math.PI * 2);
    ctx.fill();
  });

  // River Water with Gentle Animated Ripples
  ctx.fillStyle = '#0652dd';
  ctx.fillRect(0, 40, 240, 75);
  ctx.fillStyle = 'rgba(255,255,255,0.18)';
  for (let r = 0; r < 5; r++) {
    const rx = (f * 1.2 + r * 55) % 240;
    ctx.fillRect(rx, 48 + r * 14, 20, 1);
  }

  // Floating Cedar Logs
  [0, 2].forEach(lane => {
    const spd = (lane === 0 ? 1.4 : 1.1);
    const lx = (f * spd + lane * 90) % 300 - 60;
    ctx.fillStyle = '#795548'; // Wood grain
    ctx.fillRect(lx, 44 + lane * 26, 64, 14);
    ctx.fillStyle = '#4e342e';
    ctx.fillRect(lx + 4, 46 + lane * 26, 56, 3);
    ctx.fillStyle = '#ffcc80'; // Tree rings on ends
    ctx.fillRect(lx + 1, 46 + lane * 26, 2, 10);
    ctx.fillRect(lx + 61, 46 + lane * 26, 2, 10);
  });

  // Diving Swimming Turtles in Lane 1
  const tx = (280 - (f * 1.5) % 320) - 40;
  for (let t = 0; t < 3; t++) {
    const singleTx = tx + t * 24;
    ctx.fillStyle = '#2ed573'; // Shell
    ctx.beginPath();
    ctx.ellipse(singleTx, 76, 8, 6, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#f1c40f'; // Flippers
    ctx.fillRect(singleTx - 10, 72, 3, 3);
    ctx.fillRect(singleTx + 7, 72, 3, 3);
    ctx.fillRect(singleTx - 10, 78, 3, 3);
    ctx.fillRect(singleTx + 7, 78, 3, 3);
  }

  // Median Sidewalk
  ctx.fillStyle = '#57606f';
  ctx.fillRect(0, 115, 240, 16);
  ctx.fillStyle = '#747d8c';
  ctx.fillRect(0, 115, 240, 2);

  // Asphalt Highway
  ctx.fillStyle = '#1e272e';
  ctx.fillRect(0, 131, 240, 76);
  // Dashed White Lane Dividers
  ctx.fillStyle = '#ffffff';
  for (let lx = 0; lx < 240; lx += 24) {
    ctx.fillRect(lx, 156, 12, 1.5);
    ctx.fillRect(lx, 181, 12, 1.5);
  }

  // Multi-Lane Highway Traffic (Sedans, Racecars, Trucks)
  // Lane 1: Yellow Sports Car
  const cx1 = (f * 2.4) % 280 - 40;
  ctx.fillStyle = '#f1c40f';
  ctx.fillRect(cx1, 138, 28, 12);
  ctx.fillStyle = '#000000'; // Wheels
  ctx.fillRect(cx1 + 4, 136, 6, 2);
  ctx.fillRect(cx1 + 18, 136, 6, 2);
  ctx.fillRect(cx1 + 4, 150, 6, 2);
  ctx.fillRect(cx1 + 18, 150, 6, 2);
  ctx.fillStyle = '#3498db'; // Windshield
  ctx.fillRect(cx1 + 10, 140, 8, 8);

  // Lane 2: Red Speedster (Opposite Direction)
  const cx2 = 280 - (f * 3.2) % 320;
  ctx.fillStyle = '#e74c3c';
  ctx.fillRect(cx2, 162, 26, 12);
  ctx.fillStyle = '#00ffff';
  ctx.fillRect(cx2 + 8, 164, 8, 8);

  // Lane 3: Long Delivery Truck
  const cx3 = (f * 1.6 + 60) % 290 - 50;
  ctx.fillStyle = '#9b59b6';
  ctx.fillRect(cx3, 188, 44, 14);
  ctx.fillStyle = '#ecf0f1';
  ctx.fillRect(cx3 + 32, 189, 11, 12); // Cab

  // Frogger 16x16 Sprite Hopping
  const hopCycle = Math.floor(f / 35) % 6;
  const fy = 196 - hopCycle * 28;
  const fx = 120 + Math.sin(f * 0.05) * 22;
  ctx.fillStyle = '#2ecc71'; // Skin
  ctx.fillRect(fx - 6, fy - 6, 12, 12);
  ctx.fillStyle = '#ffffff'; // Bulging eyes
  ctx.fillRect(fx - 5, fy - 8, 4, 3);
  ctx.fillRect(fx + 1, fy - 8, 4, 3);
  ctx.fillStyle = '#000000';
  ctx.fillRect(fx - 4, fy - 8, 2, 2);
  ctx.fillRect(fx + 2, fy - 8, 2, 2);
  ctx.fillStyle = '#27ae60'; // Webbed feet
  ctx.fillRect(fx - 8, fy + 4, 3, 3);
  ctx.fillRect(fx + 5, fy + 4, 3, 3);

  if (crtScanlines) drawScanlines();
  if (f % 70 === 0) playArcadeSfx('FROG-H');
}

// 4. ASTEROIDS: True Atari 1979 Vector CRT Phosphor Beam Engine
function renderAsteroidsTour(f) {
  ctx.fillStyle = '#000000';
  ctx.fillRect(0, 0, 240, 240);

  ctx.save();
  ctx.strokeStyle = '#00ffff';
  ctx.shadowColor = '#00ffff';
  ctx.shadowBlur = 9;
  ctx.lineWidth = 1.6;

  // 4 Atari Polygonal Vector Asteroid Models
  const roids = [
    { x: 50, y: 65, r: 24, pts: [-1,-0.8, -0.6,-1, 0.4,-0.9, 1,-0.4, 0.9,0.5, 0.2,1, -0.7,0.8, -1,0.1], rot: f * 0.012 },
    { x: 190, y: 75, r: 28, pts: [-0.9,-0.5, -0.4,-1, 0.7,-0.8, 1,-0.1, 0.6,0.9, -0.3,1, -1,0.6], rot: -f * 0.009 },
    { x: 65, y: 175, r: 20, pts: [-1,-0.6, -0.2,-1, 0.9,-0.6, 1,0.3, 0.4,1, -0.8,0.7], rot: f * 0.016 },
    { x: 180, y: 170, r: 22, pts: [-0.8,-0.9, 0.3,-1, 1,-0.3, 0.7,0.8, -0.4,1, -1,0.2], rot: -f * 0.014 }
  ];

  roids.forEach(r => {
    ctx.beginPath();
    for (let p = 0; p < r.pts.length; p += 2) {
      const px = r.pts[p], py = r.pts[p + 1];
      const cos = Math.cos(r.rot), sin = Math.sin(r.rot);
      const rx = (px * cos - py * sin) * r.r + r.x;
      const ry = (px * sin + py * cos) * r.r + r.y;
      if (p === 0) ctx.moveTo(rx, ry); else ctx.lineTo(rx, ry);
    }
    ctx.closePath();
    ctx.stroke();
  });

  // Center Vector Delta Ship with Phosphor Core
  const shipAngle = f * 0.038;
  const cx = 120, cy = 118;
  const tipX = cx + Math.cos(shipAngle) * 14;
  const tipY = cy + Math.sin(shipAngle) * 14;
  const lX = cx + Math.cos(shipAngle + 2.45) * 11;
  const lY = cy + Math.sin(shipAngle + 2.45) * 11;
  const rX = cx + Math.cos(shipAngle - 2.45) * 11;
  const rY = cy + Math.sin(shipAngle - 2.45) * 11;

  ctx.strokeStyle = '#ffffff';
  ctx.shadowColor = '#ffffff';
  ctx.shadowBlur = 11;
  ctx.beginPath();
  ctx.moveTo(tipX, tipY);
  ctx.lineTo(lX, lY);
  ctx.lineTo(cx, cy);
  ctx.lineTo(rX, rY);
  ctx.closePath();
  ctx.stroke();

  // Flickering Vector Thruster Flame
  if (f % 8 < 5) {
    ctx.strokeStyle = '#ff9f1a';
    ctx.shadowColor = '#ff9f1a';
    ctx.beginPath();
    ctx.moveTo(lX, lY);
    ctx.lineTo(cx - Math.cos(shipAngle) * 9, cy - Math.sin(shipAngle) * 9);
    ctx.lineTo(rX, rY);
    ctx.stroke();
  }

  // Vector Bullets with Glow
  const dist = (f * 7) % 95;
  const bx = cx + Math.cos(shipAngle) * dist;
  const by = cy + Math.sin(shipAngle) * dist;
  ctx.fillStyle = '#ffffff';
  ctx.shadowColor = '#ffffff';
  ctx.fillRect(bx - 1.5, by - 1.5, 3, 3);

  // Flying Alien Saucer (UFO)
  const ufoX = (f * 1.5) % 280 - 20;
  const ufoY = 32;
  ctx.strokeStyle = '#ff3838';
  ctx.shadowColor = '#ff3838';
  ctx.beginPath();
  ctx.ellipse(ufoX, ufoY, 14, 5, 0, 0, Math.PI * 2);
  ctx.moveTo(ufoX - 7, ufoY - 2);
  ctx.lineTo(ufoX - 4, ufoY - 6);
  ctx.lineTo(ufoX + 4, ufoY - 6);
  ctx.lineTo(ufoX + 7, ufoY - 2);
  ctx.stroke();

  ctx.restore();
  if (f % 140 === 0) playArcadeSfx('AST-THR');
  if (f % 260 === 180) playArcadeSfx('AST-EXP');
}

// 5. TEMPEST: True Atari 1981 Color QuadraScan 3D Vector Tube
function renderTempestTour(f) {
  ctx.fillStyle = '#010206';
  ctx.fillRect(0, 0, 240, 240);

  ctx.save();
  ctx.strokeStyle = '#00a8ff';
  ctx.shadowColor = '#00a8ff';
  ctx.shadowBlur = 10;
  ctx.lineWidth = 1.6;

  const cx = 120, cy = 112;
  const spokes = 16;

  // 3D Perspective Web Rings Receding into Cosmic Abyss
  [0.22, 0.45, 0.70, 0.96].forEach((depth, idx) => {
    ctx.beginPath();
    ctx.strokeStyle = idx === 3 ? '#00e5ff' : '#0066cc';
    for (let s = 0; s < spokes; s++) {
      const a = (s / spokes) * Math.PI * 2;
      const x = cx + Math.cos(a) * (94 * depth);
      const y = cy + Math.sin(a) * (68 * depth);
      if (s === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();
  });

  // Radial Channel Tracks with Depth Shading
  ctx.strokeStyle = '#0097e6';
  for (let s = 0; s < spokes; s++) {
    const a = (s / spokes) * Math.PI * 2;
    ctx.beginPath();
    ctx.moveTo(cx + Math.cos(a) * 20, cy + Math.sin(a) * 15);
    ctx.lineTo(cx + Math.cos(a) * 94, cy + Math.sin(a) * 68);
    ctx.stroke();
  }

  // Player 3D Yellow Blaster Claw on Rim
  const clawSeg = Math.floor(f * 0.07) % spokes;
  const a1 = (clawSeg / spokes) * Math.PI * 2;
  const a2 = ((clawSeg + 1) / spokes) * Math.PI * 2;
  const x1 = cx + Math.cos(a1) * 94, y1 = cy + Math.sin(a1) * 68;
  const x2 = cx + Math.cos(a2) * 94, y2 = cy + Math.sin(a2) * 68;

  ctx.strokeStyle = '#f1c40f';
  ctx.shadowColor = '#f1c40f';
  ctx.shadowBlur = 12;
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  // Prongs
  ctx.lineTo(x2 + Math.cos(a2) * 6, y2 + Math.sin(a2) * 6);
  ctx.moveTo(x1, y1);
  ctx.lineTo(x1 + Math.cos(a1) * 6, y1 + Math.sin(a1) * 6);
  ctx.stroke();

  // Particle Laser Shot Streaming Down Channel
  const lDepth = 1.0 - (f * 0.05) % 0.8;
  const midA = (a1 + a2) / 2;
  ctx.fillStyle = '#ffff00';
  ctx.shadowColor = '#ffff00';
  ctx.fillRect(cx + Math.cos(midA) * (94 * lDepth) - 2, cy + Math.sin(midA) * (68 * lDepth) - 2, 4, 4);

  // Incoming Flipper Enemy (Red Bowtie)
  const enemySeg = (clawSeg + 6) % spokes;
  const ea1 = (enemySeg / spokes) * Math.PI * 2;
  const ea2 = ((enemySeg + 1) / spokes) * Math.PI * 2;
  const eDepth = 0.35 + Math.sin(f * 0.04) * 0.35;
  ctx.strokeStyle = '#ff3838';
  ctx.shadowColor = '#ff3838';
  ctx.lineWidth = 2.2;
  ctx.beginPath();
  ctx.moveTo(cx + Math.cos(ea1) * (94 * eDepth), cy + Math.sin(ea1) * (68 * eDepth));
  ctx.lineTo(cx + Math.cos(ea2) * (94 * eDepth), cy + Math.sin(ea2) * (68 * eDepth));
  ctx.stroke();

  // Superzapper Screen Lightning Flash
  if (f % 160 === 80) {
    ctx.strokeStyle = '#ffffff';
    ctx.shadowColor = '#00ffff';
    ctx.lineWidth = 4;
    ctx.stroke();
    playArcadeSfx('TEM-ZAP');
  }

  ctx.restore();
}

// 6. GYRUSS: True 1983 Konami 360-Degree Cosmic Odyssey
function renderGyrussTour(f) {
  ctx.fillStyle = '#020106';
  ctx.fillRect(0, 0, 240, 240);

  const cx = 120, cy = 112;

  // 360-Degree Hyperspace Star Warp
  for (let i = 0; i < 48; i++) {
    const a = (i * 1.39) % (Math.PI * 2);
    const dist = (f * (2.2 + (i % 3)) + i * 16) % 125;
    const sx = cx + Math.cos(a) * dist;
    const sy = cy + Math.sin(a) * dist;
    const col = dist > 95 ? '#ffffff' : (dist > 55 ? '#00e5ff' : '#7158e2');
    ctx.fillStyle = col;
    ctx.fillRect(sx, sy, dist > 75 ? 2 : 1, dist > 75 ? 2 : 1);
  }

  // Central Spinning 3D Planet Neptune with Atmosphere Glow
  const planetGrad = ctx.createRadialGradient(cx - 5, cy - 5, 3, cx, cy, 26);
  planetGrad.addColorStop(0, '#4bcffa');
  planetGrad.addColorStop(0.6, '#1e3799');
  planetGrad.addColorStop(1, '#0c2461');
  ctx.fillStyle = planetGrad;
  ctx.beginPath();
  ctx.arc(cx, cy, 24, 0, Math.PI * 2);
  ctx.fill();

  // Atmospheric Glow Ring
  ctx.strokeStyle = 'rgba(75, 207, 250, 0.4)';
  ctx.lineWidth = 2;
  ctx.stroke();

  // Outer Orbit Track
  ctx.strokeStyle = 'rgba(0, 229, 255, 0.35)';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.arc(cx, cy, 84, 0, Math.PI * 2);
  ctx.stroke();

  // Player Starfighter Orbiting 360 Degrees
  const pa = f * 0.045;
  const px = cx + Math.cos(pa) * 84;
  const py = cy + Math.sin(pa) * 84;

  ctx.save();
  ctx.translate(px, py);
  ctx.rotate(pa + Math.PI / 2);
  // Fighter Fuselage
  ctx.fillStyle = '#3498db';
  ctx.fillRect(-3, -7, 6, 14);
  ctx.fillStyle = '#e74c3c'; // Red Wingtips
  ctx.fillRect(-7, 0, 14, 4);
  ctx.fillStyle = '#f1c40f'; // Cockpit
  ctx.fillRect(-1.5, -3, 3, 4);
  ctx.restore();

  // Inward Firing Plasma Bolts
  const pDist = 84 - (f * 6) % 65;
  const bx = cx + Math.cos(pa) * pDist;
  const by = cy + Math.sin(pa) * pDist;
  ctx.fillStyle = '#00ffff';
  ctx.beginPath();
  ctx.arc(bx, by, 2.5, 0, Math.PI * 2);
  ctx.fill();

  // Spiraling Enemy Alien Swarms in Lissajous Formations
  for (let e = 0; e < 4; e++) {
    const ea = pa + Math.PI + e * 0.45;
    const ed = ((f * 2.2 + e * 26) % 80);
    const ex = cx + Math.cos(ea) * ed;
    const ey = cy + Math.sin(ea) * ed;
    ctx.fillStyle = '#ff4757';
    ctx.fillRect(ex - 4, ey - 4, 8, 8);
    ctx.fillStyle = '#ffa502';
    ctx.fillRect(ex - 2, ey - 2, 4, 4);
  }

  if (crtScanlines) drawScanlines();
}

function renderTourHud(game, f) {
  // Semi-Transparent HUD Bar at top
  ctx.fillStyle = 'rgba(6, 9, 14, 0.88)';
  ctx.fillRect(0, 0, 240, 22);

  ctx.fillStyle = '#f5a623';
  ctx.font = 'bold 10px monospace';
  ctx.fillText(game.title, 8, 15);

  ctx.fillStyle = '#00ff66';
  ctx.font = '9px monospace';
  ctx.fillText(game.year, 150, 15);

  // Bottom Technical Telemetry & Arcade Hardware Badge
  ctx.fillStyle = 'rgba(6, 9, 14, 0.90)';
  ctx.fillRect(0, 220, 240, 20);

  ctx.fillStyle = '#00e5ff';
  ctx.font = 'bold 8px monospace';
  ctx.fillText(`HW: ${game.cpu} · ${game.sound}`, 8, 233);
}'''

# Replace in build_hardware_template.py
# First, let's find the old renderArcadeFrame downsampling in simulator_template.html.bak when build_hardware_template reads it
# We can tell build_hardware_template.py to replace:
# 1) renderArcadeFrame downsampling with arcade_frame_upgrade
# 2) renderCrazyClimber through renderTourHud with high_fidelity_games_code

with open("tools/build_hardware_template.py", "r") as f:
    text = f.read()

# Let's inspect where build_hardware_template.py applies replacements:
old_target = """    # 4. Update setupKnob to support needle and stepper buttons"""

replacement_hook = f"""    # Upgraded High-Fidelity Graphics Engines
    old_arcade_frame = \"\"\"function renderArcadeFrame() {{
  arcadeBuf.fill(0xff000000);
  
  // Tiles: Bottom 2 rows
  for (let i = 0x00; i <= 0x03f; i++) {{
    drawTile(ram[i], ram[i + 0x400], (29 - (i % 0x20)) * 8, (i >= 0x20 ? 35 : 34) * 8);
  }}
  // Tiles: Middle section
  for (let i = 0x40; i <= 0x3bf; i++) {{
    drawTile(ram[i], ram[i + 0x400], (29 - Math.floor(i / 0x20)) * 8, (2 + (i % 0x20)) * 8);
  }}
  // Tiles: Top 2 rows
  for (let i = 0x3c0; i <= 0x3ff; i++) {{
    drawTile(ram[i], ram[i + 0x400], (29 - (i % 0x20)) * 8, (i >= 0x3e0 ? 1 : 0) * 8);
  }}

  // 8 Hardware Sprites
  for (let s = 7; s >= 0; s--) {{
    const sx = 239 - spritePos[s * 2];
    const sy = 272 - spritePos[s * 2 + 1];
    const info = ram[0x0ff0 + s * 2];
    const pal = ram[0x0ff0 + s * 2 + 1];
    drawSprite(info >> 2, pal, sx, sy, (info >> 1) & 1, info & 1);
  }}

  // 5:6 Downsampling (288 -> 240) + Scanline Filter
  buf32.fill(0xff08090c);
  for (let outY = 0; outY < 240; outY++) {{
    const inY = Math.floor(outY * 6 / 5);
    const inRow = inY * 224;
    const outRow = outY * 240 + 8;
    const scanDim = (crtScanlines && (outY % 2 === 1)) ? 0.72 : 1.0;
    
    for (let outX = 0; outX < 224; outX++) {{
      const pix = arcadeBuf[inRow + outX];
      if (scanDim < 1.0) {{
        const r = Math.floor((pix & 0xff) * scanDim);
        const g = Math.floor(((pix >> 8) & 0xff) * scanDim);
        const b = Math.floor(((pix >> 16) & 0xff) * scanDim);
        buf32[outRow + outX] = 0xff000000 | (b << 16) | (g << 8) | r;
      }} else {{
        buf32[outRow + outX] = pix;
      }}
    }}
  }}

  ctx.putImageData(imgData, 0, 0);
}}\"\"\"

    new_arcade_frame = \"\"\"{arcade_frame_upgrade}\"\"\"
    script_body = script_body.replace(old_arcade_frame, new_arcade_frame)

    # Replace old tour renderers (from renderCrazyClimber to renderTourDemo)
    idx_cc = script_body.find("function renderCrazyClimber()")
    idx_td = script_body.find("function renderTourDemo()")
    if idx_cc != -1 and idx_td != -1:
        new_games_block = \"\"\"{high_fidelity_games_code}\\n\\n\"\"\"
        script_body = script_body[:idx_cc] + new_games_block + script_body[idx_td:]

    # 4. Update setupKnob to support needle and stepper buttons"""

text = text.replace(old_target, replacement_hook)

with open("tools/build_hardware_template.py", "w") as f:
    f.write(text)

print("Successfully injected high-fidelity graphics upgrades into build_hardware_template.py!")
