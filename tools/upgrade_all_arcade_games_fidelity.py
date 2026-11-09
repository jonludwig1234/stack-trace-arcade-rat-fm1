import re

def generate_upgraded_arcade_engines():
    return '''// =========================================================================
// 8 AUTHENTIC PLAYABLE ARCADE ENGINES (High-Resolution CRT Graphics & Physics)
// Pac-Man, Crazy Climber, Galaga, Donkey Kong, Frogger, Asteroids, Tempest, Gyruss
// Integrated Autonomous Attract AI & High-Density Arcade Pixel Art / Vector CRT
// =========================================================================

// Global Keyboard Tracking for Smooth Multi-Key Response
const arcadeKeysDown = {};

// -------------------------------------------------------------------------
// 0. CRAZY CLIMBER (1980 NICHIBUTSU Z80): FULLY PLAYABLE ARCADE ENGINE
// -------------------------------------------------------------------------
function renderCrazyClimber() {
  climberState.animTick++;
  const tick = climberState.animTick;

  // Dusk Sky gradient
  const skyGrad = ctx.createLinearGradient(0, 0, 0, 240);
  skyGrad.addColorStop(0, '#0c1020');
  skyGrad.addColorStop(1, '#1e272e');
  ctx.fillStyle = skyGrad;
  ctx.fillRect(0, 0, 240, 240);

  // Distant City Skyline with lit windows
  ctx.fillStyle = '#0a0d16';
  ctx.fillRect(4, 180, 22, 60);
  ctx.fillRect(14, 160, 10, 80);
  ctx.fillRect(218, 175, 18, 65);
  ctx.fillStyle = '#f1c40f';
  ctx.fillRect(8, 190, 2, 3);
  ctx.fillRect(16, 170, 2, 3);
  ctx.fillRect(224, 185, 2, 3);

  // Skyscraper Main Brick Facade (x: 26 to 214)
  const bldgGrad = ctx.createLinearGradient(26, 0, 214, 0);
  bldgGrad.addColorStop(0, '#8c532b');
  bldgGrad.addColorStop(0.5, '#a05c30');
  bldgGrad.addColorStop(1, '#6d3e1d');
  ctx.fillStyle = bldgGrad;
  ctx.fillRect(26, 0, 188, 240);

  // Autonomous Attract Tour AI
  if (currentMode === 'tour') {
    if (tick % 24 < 12) climberStep('left', 'up');
    else climberStep('right', 'up');
    if (climberState.potCol === climberState.col && climberState.potY > 50 && climberState.potY < 150) {
      climberState.col = (climberState.col + 1) % 4;
    }
  }

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
      ctx.fillRect(wx - 3, wy + 26, 34, 3);
      ctx.fillStyle = '#2f3542';
      ctx.fillRect(wx - 3, wy + 29, 34, 1);

      if (isOpen) {
        ctx.fillStyle = '#05070a';
        ctx.fillRect(wx, wy, 28, 26);
        ctx.fillStyle = '#e58e26'; // Interior warm lamp glow
        ctx.fillRect(wx + 8, wy + 4, 12, 10);
        ctx.fillStyle = '#f8c291'; // Fluttering curtain
        ctx.fillRect(wx + 2, wy, 5, 20);
      } else {
        ctx.fillStyle = '#1b76bc';
        ctx.fillRect(wx, wy, 28, 26);
        ctx.fillStyle = '#4bcffa';
        ctx.fillRect(wx + 2, wy + 2, 24, 10);
        ctx.fillRect(wx + 2, wy + 14, 24, 10);
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(wx + 4, wy + 3, 18, 2);
        ctx.fillRect(wx + 2, wy + 12, 24, 2);
        ctx.fillRect(wx + 13, wy + 2, 2, 22);
      }
    }
  }

  // King Kong / Giant Ape on Left Girder (x: 4 to 34)
  const kongY = 65 + Math.sin(tick * 0.08) * 12;
  const kongArmUp = (tick % 40 < 20);
  ctx.save();
  ctx.translate(2, kongY);
  ctx.fillStyle = '#2f3542';
  ctx.fillRect(6, 12, 24, 28);
  ctx.fillStyle = '#1e272e';
  ctx.fillRect(8, 14, 20, 24);
  ctx.fillStyle = '#2f3542';
  ctx.fillRect(10, 0, 18, 14);
  ctx.fillStyle = '#e74c3c';
  ctx.fillRect(14, 8, 10, 5);
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(15, 8, 2, 2); ctx.fillRect(21, 8, 2, 2);
  ctx.fillStyle = '#f1c40f';
  ctx.fillRect(13, 3, 3, 3); ctx.fillRect(20, 3, 3, 3);
  ctx.fillStyle = '#57606f';
  ctx.fillRect(kongArmUp ? 0 : 2, kongArmUp ? 2 : 24, 8, 10);
  ctx.fillRect(kongArmUp ? 24 : 26, kongArmUp ? 24 : 2, 8, 10);
  ctx.restore();

  // Falling Terracotta Flower Pot
  climberState.potY += 2.4;
  if (climberState.potY > 240) {
    climberState.potY = -15;
    climberState.potCol = Math.floor(Math.random() * 4);
  }
  const potX = windowCols[climberState.potCol] + 8;
  const potY = climberState.potY;
  if (potY >= 0 && potY < 235) {
    ctx.fillStyle = '#e84393';
    ctx.beginPath();
    ctx.arc(potX + 6, potY - 3, 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#2ecc71';
    ctx.fillRect(potX + 1, potY - 2, 10, 3);
    ctx.fillStyle = '#e17055';
    ctx.fillRect(potX, potY, 12, 3);
    ctx.fillRect(potX + 2, potY + 3, 8, 8);
  }

  // Check Flowerpot Hit Climber
  if (climberState.potCol === climberState.col && potY > 110 && potY < 155 && currentMode !== 'tour') {
    climberState.potY = -20;
    climberState.floor = Math.max(1, climberState.floor - 2);
    playArcadeSfx('DEATH');
  }

  // The Climber Character (16x16 Pixel Art)
  const cx = windowCols[climberState.col] + 3;
  const cy = 130;
  const leftArmUp = (climberState.leftArm === 'up');
  const rightArmUp = (climberState.rightArm === 'up');

  // Shadow
  ctx.fillStyle = 'rgba(0,0,0,0.45)';
  ctx.fillRect(cx - 2, cy + 32, 26, 4);

  // Boots
  ctx.fillStyle = '#795548';
  ctx.fillRect(cx + 2, cy + 28, 7, 4);
  ctx.fillRect(cx + 13, cy + 28, 7, 4);

  // Blue Overalls
  ctx.fillStyle = '#1e3799';
  ctx.fillRect(cx + 4, cy + 18, 14, 11);
  ctx.fillStyle = '#4a69bd';
  ctx.fillRect(cx + 5, cy + 13, 3, 7);
  ctx.fillRect(cx + 14, cy + 13, 3, 7);
  ctx.fillStyle = '#f1c40f'; // Brass buttons
  ctx.fillRect(cx + 5, cy + 19, 2, 2);
  ctx.fillRect(cx + 15, cy + 19, 2, 2);

  // Red Shirt
  ctx.fillStyle = '#eb2f06';
  ctx.fillRect(cx + 3, cy + 12, 16, 7);

  // Alternating Arms
  ctx.fillStyle = '#eb2f06';
  ctx.fillRect(cx - 3, leftArmUp ? cy - 4 : cy + 12, 5, 14);
  ctx.fillStyle = '#f8c291'; // White/Peach glove
  ctx.fillRect(cx - 4, leftArmUp ? cy - 8 : cy + 24, 7, 5);

  ctx.fillStyle = '#eb2f06';
  ctx.fillRect(cx + 20, rightArmUp ? cy - 4 : cy + 12, 5, 14);
  ctx.fillStyle = '#f8c291';
  ctx.fillRect(cx + 19, rightArmUp ? cy - 8 : cy + 24, 7, 5);

  // Head & Cap
  ctx.fillStyle = '#f8c291';
  ctx.fillRect(cx + 6, cy + 2, 10, 10);
  ctx.fillStyle = '#eb2f06';
  ctx.fillRect(cx + 4, cy - 2, 14, 5); // Red Cap
  ctx.fillRect(cx + 2, cy + 1, 5, 2);   // Visor
  ctx.fillStyle = '#000000';
  ctx.fillRect(cx + 7, cy + 5, 2, 2); // Eye

  // Floor 50 Rescue Chopper
  if (climberState.floor >= 50) {
    const chopX = 120, chopY = 25;
    ctx.fillStyle = '#f1c40f'; // Yellow chopper body
    ctx.fillRect(chopX - 16, chopY, 32, 12);
    ctx.fillStyle = '#0abde3'; // Cockpit glass
    ctx.fillRect(chopX - 12, chopY + 2, 10, 8);
    // Rotor blades spinning
    ctx.fillStyle = (tick % 4 < 2) ? '#ffffff' : '#718093';
    ctx.fillRect(chopX - 28, chopY - 4, 56, 2);
    // Rescue Rope Ladder
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 1.0;
    ctx.beginPath();
    ctx.moveTo(chopX, chopY + 12); ctx.lineTo(chopX, cy - 8);
    ctx.stroke();
  }

  // Header & HUD
  ctx.fillStyle = '#f1c40f';
  ctx.font = 'bold 8px monospace';
  ctx.fillText(`1UP: ${climberState.score}`, 10, 15);
  ctx.fillStyle = '#00d2d3';
  ctx.fillText(`${climberState.floor}F`, 198, 15);

  ctx.fillStyle = 'rgba(6, 9, 14, 0.88)';
  ctx.fillRect(0, 222, 240, 18);
  ctx.fillStyle = '#00e5ff';
  ctx.font = 'bold 8px monospace';
  ctx.fillText(`TWIN-STICK: L[${climberState.leftArm.toUpperCase()}] R[${climberState.rightArm.toUpperCase()}]  COL:${climberState.col + 1}/4`, 14, 234);

  if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
}


// -------------------------------------------------------------------------
// INSTALLED ROMS ATTRACT TOUR DEMO ENGINE
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
  if (typeof stopCurrentGame === 'function') stopCurrentGame();
  tourState.frameInGame = 0;
  tourState.gameIdx = (tourState.gameIdx + 1) % tourState.games.length;
  if (typeof currentGameIdx !== 'undefined') currentGameIdx = tourState.gameIdx;
  const enc = document.getElementById('encSelect');
  if (enc && enc.style && enc.style.setProperty) {
    enc.style.setProperty('--angle', ((tourState.gameIdx / tourState.games.length * 270) - 135) + 'deg');
  }
  if (typeof clearScreen === 'function') clearScreen(tourState.games[tourState.gameIdx].title);
  playArcadeSfx('WARP');
  renderTourDemo();
}

function prevTourGame() {
  initAudio();
  if (typeof stopCurrentGame === 'function') stopCurrentGame();
  tourState.frameInGame = 0;
  tourState.gameIdx = (tourState.gameIdx - 1 + tourState.games.length) % tourState.games.length;
  if (typeof currentGameIdx !== 'undefined') currentGameIdx = tourState.gameIdx;
  const enc = document.getElementById('encSelect');
  if (enc && enc.style && enc.style.setProperty) {
    enc.style.setProperty('--angle', ((tourState.gameIdx / tourState.games.length * 270) - 135) + 'deg');
  }
  if (typeof clearScreen === 'function') clearScreen(tourState.games[tourState.gameIdx].title);
  playArcadeSfx('WARP');
  renderTourDemo();
}

function launchCurrentTourGame() {
  const g = tourState.games[tourState.gameIdx];
  tourState.active = false;
  if (typeof stopCurrentGame === 'function') stopCurrentGame();
  if (typeof clearScreen === 'function') clearScreen(g.title);
  switchActiveGame(g.id);
  setMode('arcade');
  ensurePastBoot();
  insertCoin();
  setTimeout(start1P, 200);
}

function renderTourDemo() {
  const g = tourState.games[tourState.gameIdx];
  tourState.frameInGame++;
  if (tourState.frameInGame > 300) {
    nextTourGame();
    return;
  }

  switch (g.id) {
    case 'pacman':
      renderArcadeFrame();
      break;
    case 'cclimber':
      renderCrazyClimber();
      break;
    case 'galaga':
      renderGalagaTour(tourState.frameInGame);
      break;
    case 'dkong':
      renderDonkeyKongTour(tourState.frameInGame);
      break;
    case 'frogger':
      renderFroggerTour(tourState.frameInGame);
      break;
    case 'asteroids':
      renderAsteroidsTour(tourState.frameInGame);
      break;
    case 'tempest':
      renderTempestTour(tourState.frameInGame);
      break;
    case 'gyruss':
      renderGyrussTour(tourState.frameInGame);
      break;
    default:
      renderArcadeFrame();
  }

  renderTourHud(g, tourState.frameInGame);
}

// -------------------------------------------------------------------------
// 1. GALAGA (1981 NAMCO DUAL Z80): FULLY PLAYABLE ARCADE ENGINE
// -------------------------------------------------------------------------
const galagaGame = {
  active: false,
  shipX: 120,
  shipSpeed: 2.8,
  moveDir: 0,
  lasers: [],
  aliens: [],
  bombs: [],
  explosions: [],
  scorePops: [],
  score: 0,
  highScore: 20000,
  lives: 3,
  stage: 1,
  tick: 0,
  dualFighter: false,
  tractorBeam: { active: false, x: 120, y: 60, height: 0, maxH: 140, state: 'off' },
  capturedShip: null
};

function initGalagaGame() {
  galagaGame.active = true;
  galagaGame.shipX = 120;
  galagaGame.moveDir = 0;
  galagaGame.lasers = [];
  galagaGame.bombs = [];
  galagaGame.explosions = [];
  galagaGame.scorePops = [];
  galagaGame.score = 0;
  galagaGame.lives = 3;
  galagaGame.stage = 1;
  galagaGame.tick = 0;
  galagaGame.dualFighter = false;
  galagaGame.tractorBeam = { active: false, x: 120, y: 60, height: 0, maxH: 140, state: 'off' };
  galagaGame.capturedShip = null;
  spawnGalagaFleet();
}

function spawnGalagaFleet() {
  galagaGame.aliens = [];
  // Row 0: Boss Galaga (4 green/cyan commanders)
  for (let c = 0; c < 4; c++) {
    galagaGame.aliens.push({
      x: 64 + c * 36,
      y: 42,
      homeX: 64 + c * 36,
      homeY: 42,
      type: 'boss',
      state: 'grid',
      diveTick: 0,
      hp: 2,
      angle: 0
    });
  }
  // Rows 1 & 2: Red Goei (8 per row = 16 butterflies)
  for (let r = 1; r <= 2; r++) {
    for (let c = 0; c < 8; c++) {
      galagaGame.aliens.push({
        x: 42 + c * 22,
        y: 42 + r * 16,
        homeX: 42 + c * 22,
        homeY: 42 + r * 16,
        type: 'red',
        state: 'grid',
        diveTick: 0,
        hp: 1,
        angle: 0
      });
    }
  }
  // Rows 3 & 4: Yellow Zako (10 per row = 20 bees)
  for (let r = 3; r <= 4; r++) {
    for (let c = 0; c < 10; c++) {
      galagaGame.aliens.push({
        x: 32 + c * 20,
        y: 42 + r * 15,
        homeX: 32 + c * 20,
        homeY: 42 + r * 15,
        type: 'yellow',
        state: 'grid',
        diveTick: 0,
        hp: 1,
        angle: 0
      });
    }
  }
}

function galagaFire() {
  initAudio();
  if (galagaGame.lasers.length < 6) {
    if (galagaGame.dualFighter) {
      galagaGame.lasers.push({ x: galagaGame.shipX - 10, y: 214, vy: -6.0 });
      galagaGame.lasers.push({ x: galagaGame.shipX - 4,  y: 214, vy: -6.0 });
      galagaGame.lasers.push({ x: galagaGame.shipX + 4,  y: 214, vy: -6.0 });
      galagaGame.lasers.push({ x: galagaGame.shipX + 10, y: 214, vy: -6.0 });
    } else {
      galagaGame.lasers.push({ x: galagaGame.shipX - 4, y: 214, vy: -6.0 });
      galagaGame.lasers.push({ x: galagaGame.shipX + 4, y: 214, vy: -6.0 });
    }
    playArcadeSfx('INV-FIRE');
  }
}

function updateGalagaGame() {
  galagaGame.tick++;
  const g = galagaGame;

  // Active Key Steer
  if (currentMode === 'tour') {
    let targetX = 120 + Math.sin(g.tick * 0.04) * 55;
    const diving = g.aliens.find(a => a.state === 'dive');
    if (diving) targetX = diving.x;
    if (g.shipX < targetX - 3) g.shipX += 2.4;
    else if (g.shipX > targetX + 3) g.shipX -= 2.4;
    if (g.tick % 18 === 0) galagaFire();
  } else {
    if (arcadeKeysDown['a'] || arcadeKeysDown['arrowleft']) g.moveDir = -1;
    else if (arcadeKeysDown['d'] || arcadeKeysDown['arrowright']) g.moveDir = 1;
    else g.moveDir = 0;
    g.shipX += g.moveDir * g.shipSpeed;
  }
  g.shipX = Math.max(16, Math.min(224, g.shipX));

  // Lasers
  for (let i = g.lasers.length - 1; i >= 0; i--) {
    const l = g.lasers[i];
    l.y += l.vy;
    if (l.y < 12) {
      g.lasers.splice(i, 1);
      continue;
    }
    // Hit alien
    for (let a = g.aliens.length - 1; a >= 0; a--) {
      const al = g.aliens[a];
      if (Math.abs(l.x - al.x) < 12 && Math.abs(l.y - al.y) < 12) {
        al.hp--;
        g.lasers.splice(i, 1);
        if (al.hp <= 0) {
          const pts = al.state === 'dive' ? (al.type === 'boss' ? 400 : 200) : (al.type === 'boss' ? 200 : 100);
          g.score += pts;
          if (g.score > g.highScore) g.highScore = g.score;
          g.scorePops.push({ x: al.x, y: al.y, text: String(pts), timer: 30 });
          g.explosions.push({ x: al.x, y: al.y, frame: 0 });
          if (al.type === 'boss') playArcadeSfx('BOSS');
          else playArcadeSfx('AST-EXP');
          if (pts >= 300) playArcadeSfx('BONUS');

          if (al.type === 'boss' && g.capturedShip && g.capturedShip.boss === al) {
            g.dualFighter = true;
            g.capturedShip = null;
            playArcadeSfx('BONUS');
            g.scorePops.push({ x: 120, y: 180, text: 'DUAL FIGHTER!', timer: 45 });
          }

          g.aliens.splice(a, 1);
        } else {
          al.damaged = true;
          playArcadeSfx('TRACT');
        }
        break;
      }
    }
  }

  // Aliens Sway and Dive
  const sway = Math.sin(g.tick * 0.05) * 10;
  g.aliens.forEach(al => {
    if (al.state === 'grid') {
      al.x = al.homeX + sway;
      al.y = al.homeY + Math.sin(g.tick * 0.08 + al.homeX) * 2;
      if (Math.random() < 0.0035 && g.aliens.filter(a => a.state === 'dive').length < 3) {
        al.state = 'dive';
        al.diveTick = 0;
        playArcadeSfx('DIVE');
      }
    } else if (al.state === 'dive') {
      al.diveTick++;
      al.y += 2.4;
      al.x += Math.sin(al.diveTick * 0.12) * 3.2;
      al.angle = Math.sin(al.diveTick * 0.1) * 0.6;
      if (al.diveTick === 24 && g.bombs.length < 4) {
        g.bombs.push({ x: al.x, y: al.y + 6, vy: 2.8 });
      }
      if (al.y > 232) {
        al.state = 'return';
        al.y = 10;
        al.x = al.homeX;
      }
    } else if (al.state === 'return') {
      al.y += 2.0;
      if (al.y >= al.homeY) {
        al.state = 'grid';
        al.y = al.homeY;
      }
    }
  });

  if (g.aliens.length === 0) {
    g.stage++;
    playArcadeSfx('BONUS');
    spawnGalagaFleet();
  }

  // Bombs
  for (let b = g.bombs.length - 1; b >= 0; b--) {
    const bm = g.bombs[b];
    bm.y += bm.vy;
    if (bm.y > 240) {
      g.bombs.splice(b, 1);
      continue;
    }
    if (Math.abs(bm.x - g.shipX) < (g.dualFighter ? 16 : 9) && Math.abs(bm.y - 220) < 9) {
      g.bombs.splice(b, 1);
      g.explosions.push({ x: g.shipX, y: 220, frame: 0 });
      playArcadeSfx('DEATH');
      if (currentMode !== 'tour') {
        if (g.dualFighter) {
          g.dualFighter = false;
        } else {
          g.lives--;
          if (g.lives <= 0) {
            g.lives = 3;
            g.score = 0;
            initGalagaGame();
          }
        }
      }
    }
  }

  // Explosions
  for (let e = g.explosions.length - 1; e >= 0; e--) {
    g.explosions[e].frame++;
    if (g.explosions[e].frame > 16) g.explosions.splice(e, 1);
  }

  // Score Pops
  for (let s = g.scorePops.length - 1; s >= 0; s--) {
    g.scorePops[s].timer--;
    if (g.scorePops[s].timer <= 0) g.scorePops.splice(s, 1);
  }
}

function renderGalagaGame() {
  if (!ctx) return;
  if (ctx.save) ctx.save();

  // CRT Deep Space
  ctx.fillStyle = '#05070a';
  ctx.fillRect(0, 0, 240, 240);

  // Parallax Starfield with Blinking Namco Stars
  const tick = galagaGame.tick;
  for (let st = 0; st < 38; st++) {
    const y1 = (st * 17 + tick * 0.5) % 240;
    const x1 = (st * 43) % 240;
    ctx.fillStyle = '#3867d6';
    ctx.fillRect(x1, y1, 1, 1);

    const y2 = (st * 23 + tick * 1.2) % 240;
    const x2 = (st * 71 + 12) % 240;
    ctx.fillStyle = (st % 3 === 0) ? '#f7b731' : '#eb2f06';
    ctx.fillRect(x2, y2, 1, 1);

    if (st % 2 === 0) {
      const y3 = (st * 31 + tick * 2.2) % 240;
      const x3 = (st * 97 + 34) % 240;
      ctx.fillStyle = ((tick + st) % 12 < 6) ? '#ffffff' : '#778ca3';
      ctx.fillRect(x3, y3, 2, 2);
    }
  }

  // Header Scores
  ctx.fillStyle = '#eb2f06';
  ctx.font = 'bold 8px monospace';
  ctx.fillText('1UP', 22, 12);
  ctx.fillStyle = '#ffffff';
  ctx.fillText(String(galagaGame.score).padStart(6, '0'), 18, 22);

  ctx.fillStyle = '#00d2d3';
  ctx.fillText('HIGH SCORE', 92, 12);
  ctx.fillStyle = '#ffffff';
  ctx.fillText(String(galagaGame.highScore).padStart(6, '0'), 102, 22);

  ctx.fillStyle = '#f1c40f';
  ctx.fillText(`STAGE ${galagaGame.stage}`, 186, 12);

  // Mini Ship Lives
  for (let l = 0; l < galagaGame.lives; l++) {
    const lx = 186 + l * 12;
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(lx, 18, 6, 6);
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(lx + 2, 17, 2, 2);
  }

  // Dual / Quad Lasers
  galagaGame.lasers.forEach(l => {
    ctx.fillStyle = '#f1c40f';
    ctx.fillRect(l.x - 1, l.y, 2, 7);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(l.x, l.y + 1, 1, 5);
  });

  // Enemy Torpedo Bombs
  galagaGame.bombs.forEach(b => {
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(b.x - 1, b.y, 3, 5);
    ctx.fillStyle = '#f1c40f';
    ctx.fillRect(b.x, b.y + 1, 1, 3);
  });

  // Aliens Pixel Art (16x16 Namco Bitmaps)
  const flap = (tick >> 3) % 2;
  galagaGame.aliens.forEach(al => {
    ctx.save();
    ctx.translate(al.x, al.y);
    if (al.angle) ctx.rotate(al.angle);

    if (al.type === 'boss') {
      const bodyCol = (al.hp === 2) ? '#10ac84' : '#0652dd';
      ctx.fillStyle = bodyCol;
      ctx.fillRect(-7, -4, 14, 8);
      ctx.fillRect(-5, -6, 10, 3);
      ctx.fillStyle = '#00d2d3';
      ctx.fillRect(-3, -7, 6, 2);
      ctx.fillStyle = '#f1c40f';
      if (flap) {
        ctx.fillRect(-9, -8, 2, 5); ctx.fillRect(7, -8, 2, 5);
        ctx.fillRect(-7, -9, 2, 2); ctx.fillRect(5, -9, 2, 2);
      } else {
        ctx.fillRect(-8, -7, 2, 5); ctx.fillRect(6, -7, 2, 5);
        ctx.fillRect(-6, -8, 2, 2); ctx.fillRect(4, -8, 2, 2);
      }
      ctx.fillStyle = '#eb2f06';
      ctx.fillRect(-4, -2, 2, 3); ctx.fillRect(2, -2, 2, 3);
    } else if (al.type === 'red') {
      ctx.fillStyle = '#eb2f06';
      ctx.fillRect(-6, -4, 12, 8);
      ctx.fillRect(-3, -6, 6, 3);
      ctx.fillStyle = '#f1c40f';
      ctx.fillRect(-2, -3, 4, 6);
      ctx.fillRect(-1, -7, 2, 2);
      if (flap) {
        ctx.fillStyle = '#eb2f06';
        ctx.fillRect(-8, -2, 3, 5); ctx.fillRect(5, -2, 3, 5);
        ctx.fillStyle = '#f1c40f';
        ctx.fillRect(-8, 0, 2, 2); ctx.fillRect(6, 0, 2, 2);
      } else {
        ctx.fillStyle = '#eb2f06';
        ctx.fillRect(-7, -1, 3, 5); ctx.fillRect(4, -1, 3, 5);
        ctx.fillStyle = '#f1c40f';
        ctx.fillRect(-7, 1, 2, 2); ctx.fillRect(5, 1, 2, 2);
      }
    } else {
      ctx.fillStyle = '#f1c40f';
      ctx.fillRect(-5, -2, 10, 7);
      ctx.fillStyle = '#273c75';
      ctx.fillRect(-3, -5, 6, 4);
      ctx.fillStyle = '#05070a';
      ctx.fillRect(-4, 0, 8, 1);
      ctx.fillRect(-3, 2, 6, 1);
      ctx.fillStyle = flap ? '#dff9fb' : '#c7ecee';
      if (flap) {
        ctx.fillRect(-8, -4, 4, 6); ctx.fillRect(4, -4, 4, 6);
      } else {
        ctx.fillRect(-9, -3, 4, 5); ctx.fillRect(5, -3, 4, 5);
      }
    }
    ctx.restore();
  });

  // Explosions
  galagaGame.explosions.forEach(ex => {
    const r = ex.frame * 1.6;
    ctx.strokeStyle = (ex.frame % 2 === 0) ? '#f1c40f' : '#eb2f06';
    ctx.lineWidth = 1.6;
    ctx.beginPath();
    ctx.arc(ex.x, ex.y, r, 0, Math.PI * 2);
    ctx.stroke();
    for (let p = 0; p < 8; p++) {
      const pa = (p / 8) * Math.PI * 2;
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(ex.x + Math.cos(pa) * r * 1.2, ex.y + Math.sin(pa) * r * 1.2, 2, 2);
    }
  });

  // Player Fighter Sprite (Authentic 16x16 Namco Pixel Art)
  function drawSingleFighter(sx, sy) {
    ctx.save();
    ctx.translate(sx, sy);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(-6, -2, 12, 8);
    ctx.fillRect(-2, -8, 4, 7);
    ctx.fillRect(-1, -11, 2, 4);
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(-8, -4, 3, 8);
    ctx.fillRect(5, -4, 3, 8);
    ctx.fillRect(-5, 1, 10, 2);
    ctx.fillStyle = '#00d2d3';
    ctx.fillRect(-2, -4, 4, 4);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(-1, -4, 2, 1);
    ctx.fillStyle = '#f1c40f';
    ctx.fillRect(-8, -6, 2, 2);
    ctx.fillRect(6, -6, 2, 2);
    if (tick % 4 < 2) {
      ctx.fillRect(-3, 6, 2, 3);
      ctx.fillRect(1, 6, 2, 3);
    }
    ctx.restore();
  }

  const shipY = 220;
  if (galagaGame.dualFighter) {
    ctx.fillStyle = '#718093';
    ctx.fillRect(galagaGame.shipX - 10, shipY + 2, 20, 2);
    drawSingleFighter(galagaGame.shipX - 8, shipY);
    drawSingleFighter(galagaGame.shipX + 8, shipY);
  } else {
    drawSingleFighter(galagaGame.shipX, shipY);
  }

  // Score Popups
  galagaGame.scorePops.forEach(sp => {
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 8px monospace';
    ctx.fillText(sp.text, sp.x - 6, sp.y);
  });

  if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
  if (ctx.restore) ctx.restore();
}

function renderGalagaTour(f) {
  if (!galagaGame.active) initGalagaGame();
  updateGalagaGame();
  renderGalagaGame();
}

// -------------------------------------------------------------------------
// 2. DONKEY KONG 1981 NINTENDO 25M: FULLY PLAYABLE ARCADE ENGINE
// -------------------------------------------------------------------------
const dkongGame = {
  active: false,
  mario: {
    x: 42,
    y: 204,
    vx: 0,
    vy: 0,
    w: 12,
    h: 16,
    facing: 'right',
    state: 'stand',
    walkFrame: 0,
    climbFrame: 0,
    onGround: true,
    ladder: null,
    currentGirder: 0,
    hasHammer: false,
    hammerTimer: 0,
    hammerFrame: 0
  },
  score: 0,
  highScore: 7650,
  bonusTimer: 5000,
  bonusTick: 0,
  lives: 3,
  level: 1,
  cleared: false,
  winTimer: 0,
  deathTimer: 0,
  tick: 0,
  dk: { frame: 0, action: 'idle' },
  barrels: [],
  scorePops: [],
  hammer: { x: 34, y: 104, available: true }
};

function getGirderY(x, tier) {
  if (tier === 0) {
    if (x <= 80) return 218;
    return 218 - ((x - 80) / 142) * 4;
  } else if (tier === 1) {
    return 156 + ((x - 18) / 200) * 10;
  } else if (tier === 2) {
    return 118 - ((x - 24) / 198) * 10;
  } else if (tier === 3) {
    if (x < 88) return 62;
    return 66 + ((x - 88) / 134) * 4;
  }
  return 218;
}

const DK_LADDERS = [
  { id: 1, x: 194, top: 166, bottom: 214, fromTier: 0, toTier: 1, broken: false },
  { id: 2, x: 100, top: 194, bottom: 218, fromTier: 0, toTier: 1, broken: true },
  { id: 3, x: 46,  top: 118, bottom: 156, fromTier: 1, toTier: 2, broken: false },
  { id: 4, x: 130, top: 113, bottom: 161, fromTier: 1, toTier: 2, broken: false },
  { id: 5, x: 196, top: 69,  bottom: 109, fromTier: 2, toTier: 3, broken: false },
  { id: 6, x: 106, top: 38,  bottom: 66,  fromTier: 3, toTier: 4, broken: false }
];

function initDonkeyKongGame() {
  dkongGame.active = true;
  dkongGame.mario.x = 42;
  dkongGame.mario.y = 204;
  dkongGame.mario.vx = 0;
  dkongGame.mario.vy = 0;
  dkongGame.mario.facing = 'right';
  dkongGame.mario.state = 'stand';
  dkongGame.mario.onGround = true;
  dkongGame.mario.ladder = null;
  dkongGame.mario.currentGirder = 0;
  dkongGame.mario.hasHammer = false;
  dkongGame.mario.hammerTimer = 0;
  dkongGame.score = 0;
  dkongGame.bonusTimer = 5000;
  dkongGame.bonusTick = 0;
  dkongGame.lives = 3;
  dkongGame.cleared = false;
  dkongGame.winTimer = 0;
  dkongGame.deathTimer = 0;
  dkongGame.tick = 0;
  dkongGame.barrels = [];
  dkongGame.scorePops = [];
  dkongGame.hammer.available = true;
}

function dkongJump() {
  initAudio();
  const m = dkongGame.mario;
  if (m.onGround && m.state !== 'climb' && m.state !== 'dead') {
    m.vy = -4.0;
    m.onGround = false;
    m.state = 'jump';
    playArcadeSfx('DK-JUMP');
  }
}

function dkongClimbUp() {
  initAudio();
  const m = dkongGame.mario;
  if (m.state === 'dead' || m.hasHammer) return;
  const lad = DK_LADDERS.find(l => !l.broken && Math.abs(m.x - l.x) < 9 && m.y <= l.bottom + 6 && m.y >= l.top - 6);
  if (lad) {
    m.state = 'climb';
    m.ladder = lad;
    m.x = lad.x;
    m.y -= 1.8;
    m.climbFrame++;
    if (m.climbFrame % 6 === 0) playArcadeSfx('DK-WALK');
  }
}

function dkongClimbDown() {
  initAudio();
  const m = dkongGame.mario;
  if (m.state === 'dead' || m.hasHammer) return;
  const lad = DK_LADDERS.find(l => !l.broken && Math.abs(m.x - l.x) < 9 && m.y >= l.top - 8 && m.y < l.bottom);
  if (lad) {
    m.state = 'climb';
    m.ladder = lad;
    m.x = lad.x;
    m.y += 1.8;
    m.climbFrame++;
    if (m.climbFrame % 6 === 0) playArcadeSfx('DK-WALK');
  }
}

function updateDonkeyKongGame() {
  dkongGame.tick++;
  const m = dkongGame.mario;

  if (currentMode === 'tour') {
    if (!m.hasHammer) {
      if (m.currentGirder === 0) {
        if (m.x < 192) {
          m.vx = 1.4; m.facing = 'right'; m.state = 'run';
          const near = dkongGame.barrels.find(b => b.tier === 0 && Math.abs(b.x - m.x) < 22 && b.x > m.x);
          if (near && m.onGround) dkongJump();
        } else {
          m.vx = 0; dkongClimbUp();
        }
      } else if (m.currentGirder === 1) {
        if (m.x > 36) {
          m.vx = -1.4; m.facing = 'left'; m.state = 'run';
          const near = dkongGame.barrels.find(b => b.tier === 1 && Math.abs(b.x - m.x) < 22 && b.x < m.x);
          if (near && m.onGround) dkongJump();
        } else {
          m.vx = 1.2; m.facing = 'right';
        }
      }
    }
  } else {
    if (m.state !== 'climb' && m.state !== 'dead') {
      if (arcadeKeysDown['a'] || arcadeKeysDown['arrowleft']) {
        m.vx = -1.6; m.facing = 'left';
        if (m.onGround) m.state = m.hasHammer ? 'hammer' : 'run';
      } else if (arcadeKeysDown['d'] || arcadeKeysDown['arrowright']) {
        m.vx = 1.6; m.facing = 'right';
        if (m.onGround) m.state = m.hasHammer ? 'hammer' : 'run';
      } else {
        m.vx = 0;
        if (m.onGround && m.state === 'run') m.state = m.hasHammer ? 'hammer' : 'stand';
      }

      if (arcadeKeysDown['w'] || arcadeKeysDown['arrowup']) dkongClimbUp();
      else if (arcadeKeysDown['s'] || arcadeKeysDown['arrowdown']) dkongClimbDown();
    } else if (m.state === 'climb') {
      if (arcadeKeysDown['w'] || arcadeKeysDown['arrowup']) dkongClimbUp();
      else if (arcadeKeysDown['s'] || arcadeKeysDown['arrowdown']) dkongClimbDown();
    }
  }

  // Bonus Timer
  dkongGame.bonusTick++;
  if (dkongGame.bonusTick % 50 === 0 && dkongGame.bonusTimer > 0) {
    dkongGame.bonusTimer = Math.max(0, dkongGame.bonusTimer - 100);
  }

  if (dkongGame.cleared) {
    dkongGame.winTimer--;
    if (dkongGame.winTimer <= 0) {
      dkongGame.level++;
      dkongGame.cleared = false;
      dkongGame.mario.x = 42;
      dkongGame.mario.y = 204;
      dkongGame.mario.currentGirder = 0;
      dkongGame.bonusTimer = 5000 + dkongGame.level * 500;
      dkongGame.barrels = [];
      dkongGame.hammer.available = true;
    }
    return;
  }

  if (m.state === 'dead') {
    dkongGame.deathTimer--;
    if (dkongGame.deathTimer <= 0) {
      if (dkongGame.lives > 0) {
        m.x = 42;
        m.y = 204;
        m.vx = 0;
        m.vy = 0;
        m.currentGirder = 0;
        m.state = 'stand';
        m.onGround = true;
      } else {
        dkongGame.lives = 3;
        dkongGame.score = 0;
        initDonkeyKongGame();
      }
    }
    return;
  }

  if (m.hasHammer) {
    m.hammerTimer--;
    m.hammerFrame++;
    if (m.hammerFrame % 14 === 0) playArcadeSfx('DK-HAMR');
    if (m.hammerTimer <= 0) {
      m.hasHammer = false;
      m.state = 'stand';
    }
  }

  if (dkongGame.hammer.available && !m.hasHammer) {
    if (Math.abs(m.x - dkongGame.hammer.x) < 14 && Math.abs(m.y - dkongGame.hammer.y) < 14) {
      dkongGame.hammer.available = false;
      m.hasHammer = true;
      m.hammerTimer = 320;
      m.state = 'hammer';
      playArcadeSfx('WARP');
    }
  }

  if (m.state === 'climb' && m.ladder) {
    if (m.y <= m.ladder.top) {
      m.currentGirder = m.ladder.toTier;
      m.y = getGirderY(m.x, m.currentGirder) - 14;
      m.state = 'stand';
      m.onGround = true;
      m.ladder = null;
    } else if (m.y >= m.ladder.bottom) {
      m.currentGirder = m.ladder.fromTier;
      m.y = getGirderY(m.x, m.currentGirder) - 14;
      m.state = 'stand';
      m.onGround = true;
      m.ladder = null;
    }
  } else if (m.state === 'jump') {
    m.x += m.vx;
    m.y += m.vy;
    m.vy += 0.28;
    const floorY = getGirderY(m.x, m.currentGirder) - 14;
    if (m.vy > 0 && m.y >= floorY) {
      m.y = floorY;
      m.vy = 0;
      m.onGround = true;
      m.state = Math.abs(m.vx) > 0.1 ? (m.hasHammer ? 'hammer' : 'run') : (m.hasHammer ? 'hammer' : 'stand');
    }
  } else {
    m.x += m.vx;
    m.x = Math.max(16, Math.min(224, m.x));
    m.y = getGirderY(m.x, m.currentGirder) - 14;
    if (Math.abs(m.vx) > 0.1) {
      m.walkFrame++;
      if (m.walkFrame % 14 === 0) playArcadeSfx('DK-WALK');
    }
  }

  if (m.y <= 44 && m.x >= 90 && m.x <= 138 && !dkongGame.cleared) {
    dkongGame.cleared = true;
    dkongGame.winTimer = 90;
    dkongGame.score += dkongGame.bonusTimer;
    if (dkongGame.score > dkongGame.highScore) dkongGame.highScore = dkongGame.score;
    playArcadeSfx('DK-WIN');
    dkongGame.scorePops.push({ x: 110, y: 30, text: `+${dkongGame.bonusTimer}`, timer: 60 });
  }

  dkongGame.dk.frame++;
  if (dkongGame.dk.frame % 130 === 0) {
    playArcadeSfx('DK-ROAR');
    dkongGame.barrels.push({
      x: 64,
      y: 60,
      tier: 3,
      vx: 1.5 + dkongGame.level * 0.15,
      rollFrame: 0,
      scored: false
    });
  }

  for (let i = dkongGame.barrels.length - 1; i >= 0; i--) {
    const b = dkongGame.barrels[i];
    b.rollFrame++;
    b.x += b.vx;
    b.y = getGirderY(b.x, b.tier) - 8;

    if (b.tier === 3 && b.x >= 220) {
      b.tier = 2; b.vx = -(1.5 + dkongGame.level * 0.15);
    } else if (b.tier === 2 && b.x <= 20) {
      b.tier = 1; b.vx = (1.5 + dkongGame.level * 0.15);
    } else if (b.tier === 1 && b.x >= 220) {
      b.tier = 0; b.vx = -(1.5 + dkongGame.level * 0.15);
    } else if (b.tier === 0 && b.x <= 20) {
      dkongGame.barrels.splice(i, 1);
      playArcadeSfx('AST-EXP');
      continue;
    }

    if (m.state === 'jump' && !b.scored && Math.abs(m.x - b.x) < 14 && m.y < b.y && (b.y - m.y) < 28) {
      b.scored = true;
      dkongGame.score += 100;
      if (dkongGame.score > dkongGame.highScore) dkongGame.highScore = dkongGame.score;
      dkongGame.scorePops.push({ x: m.x, y: m.y - 10, text: '100', timer: 30 });
      playArcadeSfx('BONUS');
    }

    if (m.hasHammer && Math.abs(m.x - b.x) < 18 && Math.abs(m.y - b.y) < 16) {
      dkongGame.barrels.splice(i, 1);
      dkongGame.score += 300;
      if (dkongGame.score > dkongGame.highScore) dkongGame.highScore = dkongGame.score;
      dkongGame.scorePops.push({ x: b.x, y: b.y - 8, text: '300', timer: 35 });
      playArcadeSfx('DK-HAMR');
      continue;
    }

    if (!m.hasHammer && m.state !== 'dead' && !dkongGame.cleared && currentMode !== 'tour') {
      if (Math.abs(m.x - b.x) < 9 && Math.abs(m.y - b.y) < 10) {
        m.state = 'dead';
        dkongGame.deathTimer = 60;
        dkongGame.lives--;
        playArcadeSfx('DK-FALL');
      }
    }
  }

  for (let s = dkongGame.scorePops.length - 1; s >= 0; s--) {
    const sp = dkongGame.scorePops[s];
    sp.y -= 0.3;
    sp.timer--;
    if (sp.timer <= 0) dkongGame.scorePops.splice(s, 1);
  }
}

function renderDonkeyKongGame() {
  if (!ctx) return;
  if (ctx.save) ctx.save();

  ctx.fillStyle = '#05070a';
  ctx.fillRect(0, 0, 240, 240);

  function drawGirder(startX, startY, endX, endY) {
    const dx = endX - startX, dy = endY - startY;
    const len = Math.hypot(dx, dy);
    const steps = Math.floor(len / 8);

    ctx.strokeStyle = '#e056fd';
    ctx.lineWidth = 2.0;
    ctx.beginPath();
    ctx.moveTo(startX, startY); ctx.lineTo(endX, endY);
    ctx.moveTo(startX, startY + 6); ctx.lineTo(endX, endY + 6);
    ctx.stroke();

    ctx.strokeStyle = '#be2edd';
    ctx.lineWidth = 1.0;
    ctx.beginPath();
    for (let i = 0; i < steps; i++) {
      const t1 = i / steps, t2 = (i + 1) / steps;
      ctx.moveTo(startX + dx * t1, startY + dy * t1);
      ctx.lineTo(startX + dx * t2, startY + dy * t2 + 6);
    }
    ctx.stroke();
  }

  drawGirder(16, 218, 80, 218);
  drawGirder(80, 218, 224, 214);
  drawGirder(18, 156, 222, 166);
  drawGirder(222, 108, 24, 118);
  drawGirder(24, 62, 88, 62);
  drawGirder(88, 66, 222, 70);
  drawGirder(90, 38, 138, 38);

  DK_LADDERS.forEach(lad => {
    ctx.strokeStyle = lad.broken ? '#ff7675' : '#00d2d3';
    ctx.lineWidth = 1.5;
    for (let ly = lad.top; ly <= lad.bottom; ly += 5) {
      if (lad.broken && ly > lad.top + 8 && ly < lad.bottom - 8) continue;
      ctx.beginPath();
      ctx.moveTo(lad.x - 4, ly); ctx.lineTo(lad.x + 4, ly);
      ctx.stroke();
    }
    ctx.beginPath();
    ctx.moveTo(lad.x - 4, lad.top); ctx.lineTo(lad.x - 4, lad.bottom);
    ctx.moveTo(lad.x + 4, lad.top); ctx.lineTo(lad.x + 4, lad.bottom);
    ctx.stroke();
  });

  const drumX = 22, drumY = 202;
  ctx.fillStyle = '#2d3436';
  ctx.fillRect(drumX, drumY, 14, 16);
  ctx.strokeStyle = '#00d2d3';
  if (ctx.strokeRect) ctx.strokeRect(drumX, drumY, 14, 16);
  ctx.fillStyle = '#00d2d3';
  ctx.font = '6px monospace';
  ctx.fillText('OIL', drumX + 2, drumY + 11);

  const fTick = dkongGame.tick;
  for (let f = 0; f < 3; f++) {
    const fx = drumX + 2 + f * 4;
    const fh = 6 + Math.sin(fTick * 0.2 + f) * 4;
    ctx.fillStyle = (f === 1) ? '#f1c40f' : '#eb2f06';
    ctx.fillRect(fx, drumY - fh, 3, fh);
    ctx.fillStyle = '#00d2d3';
    ctx.fillRect(fx + 1, drumY - 2, 2, 2);
  }

  const dkX = 40, dkY = 32;
  ctx.save();
  ctx.translate(dkX, dkY);
  ctx.fillStyle = '#6d4c41';
  ctx.fillRect(-14, 0, 28, 26);
  ctx.fillStyle = '#f5cd79';
  ctx.fillRect(-8, 6, 16, 14);
  ctx.fillStyle = '#f5cd79';
  ctx.fillRect(-10, -8, 20, 10);
  ctx.fillStyle = '#eb2f06';
  ctx.fillRect(-6, -2, 12, 4);
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(-5, -2, 2, 2); ctx.fillRect(3, -2, 2, 2);
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(-7, -7, 4, 4); ctx.fillRect(3, -7, 4, 4);
  ctx.fillStyle = '#000000';
  ctx.fillRect(-6, -6, 2, 2); ctx.fillRect(4, -6, 2, 2);

  const dkChest = (fTick % 30 < 15);
  ctx.fillStyle = '#4e342e';
  if (dkChest) {
    ctx.fillRect(-18, 4, 6, 10);
    ctx.fillRect(12, 8, 8, 8);
  } else {
    ctx.fillRect(-14, 8, 8, 8);
    ctx.fillRect(12, 4, 6, 10);
  }
  ctx.restore();

  ctx.fillStyle = '#b7791f';
  ctx.fillRect(18, 38, 12, 9);
  ctx.fillRect(18, 48, 12, 9);
  ctx.strokeStyle = '#4e342e';
  if (ctx.strokeRect) ctx.strokeRect(18, 38, 12, 9);
  if (ctx.strokeRect) ctx.strokeRect(18, 48, 12, 9);

  const px = 114, py = 24;
  ctx.save();
  ctx.translate(px, py);
  ctx.fillStyle = '#ff9ff3';
  ctx.fillRect(-5, 0, 10, 14);
  ctx.fillStyle = '#feca57';
  ctx.fillRect(-6, -8, 12, 8);
  ctx.fillRect(-8, -4, 3, 10);
  ctx.fillStyle = '#ffdd59';
  ctx.fillRect(-4, -6, 8, 6);
  ctx.fillStyle = '#000000';
  ctx.fillRect(-2, -5, 2, 2);

  if (fTick % 40 < 25) {
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(8, -18, 28, 12);
    ctx.fillStyle = '#eb2f06';
    ctx.font = 'bold 7px monospace';
    ctx.fillText('HELP!', 11, -9);
  }
  ctx.restore();

  if (dkongGame.hammer.available) {
    ctx.fillStyle = '#5d4037';
    ctx.fillRect(dkongGame.hammer.x + 3, dkongGame.hammer.y - 6, 2, 12);
    ctx.fillStyle = '#f5cd79';
    ctx.fillRect(dkongGame.hammer.x, dkongGame.hammer.y - 10, 8, 5);
    ctx.strokeStyle = '#2d3436';
    if (ctx.strokeRect) ctx.strokeRect(dkongGame.hammer.x, dkongGame.hammer.y - 10, 8, 5);
  }

  dkongGame.barrels.forEach(b => {
    ctx.save();
    ctx.translate(b.x, b.y);
    ctx.rotate((b.rollFrame * 0.16) * Math.sign(b.vx));
    ctx.fillStyle = '#b7791f';
    ctx.beginPath();
    ctx.arc(0, 0, 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#2d3436';
    ctx.lineWidth = 1.2;
    ctx.stroke();
    ctx.strokeStyle = '#f5cd79';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(-5, 0); ctx.lineTo(5, 0);
    ctx.moveTo(0, -5); ctx.lineTo(0, 5);
    ctx.stroke();
    ctx.restore();
  });

  const m = dkongGame.mario;
  ctx.save();
  ctx.translate(m.x, m.y);
  if (m.facing === 'left') ctx.scale(-1, 1);

  if (m.state === 'dead') {
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(-7, 4, 14, 6);
    ctx.fillStyle = '#0abde3';
    ctx.fillRect(-4, 0, 8, 6);
    ctx.fillStyle = '#f5cd79';
    ctx.fillRect(-2, -4, 4, 4);
  } else {
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(-5, -12, 10, 4);
    ctx.fillRect(0, -10, 8, 3);
    ctx.fillStyle = '#ffdd59';
    ctx.fillRect(-4, -9, 8, 5);
    ctx.fillRect(2, -8, 4, 3);
    ctx.fillStyle = '#4e342e';
    ctx.fillRect(-5, -9, 3, 5);
    ctx.fillRect(0, -6, 6, 2);
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, -8, 2, 2);
    ctx.fillStyle = '#0abde3';
    ctx.fillRect(-4, -6, 9, 5);
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(-3, -3, 7, 6);
    ctx.fillStyle = '#f1c40f';
    ctx.fillRect(1, -2, 2, 2);

    ctx.fillStyle = '#4e342e';
    if (m.state === 'jump') {
      ctx.fillRect(-6, 0, 4, 3);
      ctx.fillRect(2, -1, 4, 3);
    } else if (m.state === 'run') {
      const step = (m.walkFrame >> 2) % 3;
      if (step === 0) { ctx.fillRect(-4, 2, 4, 3); ctx.fillRect(1, 2, 4, 3); }
      else if (step === 1) { ctx.fillRect(-6, 2, 4, 3); ctx.fillRect(2, 0, 4, 3); }
      else { ctx.fillRect(-2, 0, 4, 3); ctx.fillRect(3, 2, 4, 3); }
    } else {
      ctx.fillRect(-3, 2, 3, 3); ctx.fillRect(1, 2, 3, 3);
    }

    if (m.hasHammer) {
      const hDown = (m.hammerFrame % 14 < 7);
      ctx.fillStyle = '#5d4037';
      ctx.fillRect(hDown ? 4 : -2, hDown ? -2 : -20, hDown ? 12 : 3, hDown ? 3 : 14);
      ctx.fillStyle = '#b7791f';
      ctx.fillRect(hDown ? 14 : -6, hDown ? -5 : -24, 8, 10);
      ctx.strokeStyle = '#2d3436';
      ctx.lineWidth = 1;
      if (ctx.strokeRect) ctx.strokeRect(hDown ? 14 : -6, hDown ? -5 : -24, 8, 10);
    }
  }
  ctx.restore();

  dkongGame.scorePops.forEach(sp => {
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 9px monospace';
    ctx.fillText(sp.text, sp.x - 6, sp.y);
  });

  ctx.fillStyle = '#f1c40f';
  ctx.font = 'bold 8px monospace';
  ctx.fillText('1UP', 18, 12);
  ctx.fillStyle = '#ffffff';
  ctx.fillText(String(dkongGame.score).padStart(6, '0'), 18, 22);

  ctx.fillStyle = '#00d2d3';
  ctx.fillText('HIGH SCORE', 92, 12);
  ctx.fillStyle = '#ffffff';
  ctx.fillText(String(dkongGame.highScore).padStart(6, '0'), 102, 22);

  ctx.fillStyle = '#ff9f43';
  ctx.fillText('BONUS', 184, 12);
  ctx.fillStyle = '#ffffff';
  ctx.fillText(String(dkongGame.bonusTimer).padStart(4, '0'), 188, 22);

  for (let l = 0; l < dkongGame.lives; l++) {
    ctx.fillStyle = '#eb2f06';
    ctx.font = '8px monospace';
    ctx.fillText('♥', 188 + l * 10, 32);
  }

  if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
  if (ctx.restore) ctx.restore();
}

function renderDonkeyKongTour(f) {
  if (!dkongGame.active) initDonkeyKongGame();
  updateDonkeyKongGame();
  renderDonkeyKongGame();
}

// -------------------------------------------------------------------------
// 3. FROGGER (1981 KONAMI DUAL AY-3-8910): FULLY PLAYABLE ARCADE ENGINE
// -------------------------------------------------------------------------
const froggerGame = {
  active: false,
  frog: { gridX: 7, gridY: 13, x: 112, y: 216, dir: 'up', hopTick: 0 },
  score: 0,
  highScore: 10000,
  lives: 3,
  time: 60,
  homeBays: [false, false, false, false, false],
  vehicles: [],
  logs: [],
  tick: 0
};

function initFroggerGame() {
  froggerGame.active = true;
  froggerGame.frog.gridX = 7;
  froggerGame.frog.gridY = 13;
  froggerGame.frog.x = 112;
  froggerGame.frog.y = 216;
  froggerGame.frog.dir = 'up';
  froggerGame.score = 0;
  froggerGame.lives = 3;
  froggerGame.time = 60;
  froggerGame.homeBays = [false, false, false, false, false];
  froggerGame.tick = 0;
  spawnFroggerTraffic();
  spawnFroggerRiver();
}

function spawnFroggerTraffic() {
  froggerGame.vehicles = [];
  for (let c = 0; c < 3; c++) froggerGame.vehicles.push({ x: c * 80, y: 198, w: 22, speed: -1.2, type: 'sedan', color: '#feca57' });
  for (let c = 0; c < 3; c++) froggerGame.vehicles.push({ x: c * 90, y: 182, w: 20, speed: 0.8, type: 'dozer', color: '#ffffff' });
  for (let c = 0; c < 3; c++) froggerGame.vehicles.push({ x: c * 75, y: 166, w: 22, speed: -1.8, type: 'racer', color: '#eb2f06' });
  for (let c = 0; c < 2; c++) froggerGame.vehicles.push({ x: c * 120, y: 150, w: 24, speed: 2.2, type: 'formula', color: '#a55eea' });
  for (let c = 0; c < 2; c++) froggerGame.vehicles.push({ x: c * 110, y: 134, w: 36, speed: -0.9, type: 'truck', color: '#10ac84' });
}

function spawnFroggerRiver() {
  froggerGame.logs = [];
  for (let c = 0; c < 3; c++) froggerGame.logs.push({ x: c * 90, y: 102, w: 46, speed: 1.1, type: 'log' });
  for (let c = 0; c < 4; c++) froggerGame.logs.push({ x: c * 65, y: 86, w: 32, speed: -1.3, type: 'turtle' });
  for (let c = 0; c < 2; c++) froggerGame.logs.push({ x: c * 130, y: 70, w: 72, speed: 1.5, type: 'log' });
  for (let c = 0; c < 3; c++) froggerGame.logs.push({ x: c * 85, y: 54, w: 36, speed: 1.0, type: 'log' });
  for (let c = 0; c < 4; c++) froggerGame.logs.push({ x: c * 70, y: 38, w: 32, speed: -1.6, type: 'turtle' });
}

function froggerHop(dir) {
  initAudio();
  const fg = froggerGame.frog;
  fg.dir = dir;
  fg.hopTick = 8;
  if (dir === 'up') fg.gridY = Math.max(1, fg.gridY - 1);
  else if (dir === 'down') fg.gridY = Math.min(13, fg.gridY + 1);
  else if (dir === 'left') fg.gridX = Math.max(1, fg.gridX - 1);
  else if (dir === 'right') fg.gridX = Math.min(13, fg.gridX + 1);

  fg.x = 8 + fg.gridX * 16;
  fg.y = 16 + fg.gridY * 16;

  playArcadeSfx('FROG-H');
  froggerGame.score += 10;
  if (froggerGame.score > froggerGame.highScore) froggerGame.highScore = froggerGame.score;
}

function updateFroggerGame() {
  froggerGame.tick++;
  const fg = froggerGame.frog;
  if (fg.hopTick > 0) fg.hopTick--;

  if (currentMode === 'tour' && froggerGame.tick % 32 === 0) {
    if (fg.gridY > 1) {
      const nextY = 16 + (fg.gridY - 1) * 16;
      const danger = froggerGame.vehicles.some(v => Math.abs(v.y - nextY) < 10 && Math.abs(v.x - fg.x) < 20);
      if (!danger) froggerHop('up');
      else if (Math.random() < 0.4) froggerHop(Math.random() < 0.5 ? 'left' : 'right');
    } else {
      initFroggerGame();
    }
  }

  froggerGame.vehicles.forEach(v => {
    v.x += v.speed;
    if (v.speed < 0 && v.x < -40) v.x = 240 + Math.random() * 20;
    else if (v.speed > 0 && v.x > 260) v.x = -40;

    if (Math.abs(v.y - fg.y) < 10 && Math.abs(v.x - fg.x) < (v.w / 2 + 4) && currentMode !== 'tour') {
      playArcadeSfx('FROG-SPLAT');
      fg.gridX = 7; fg.gridY = 13; fg.x = 112; fg.y = 216;
      froggerGame.lives--;
      if (froggerGame.lives <= 0) {
        froggerGame.lives = 3;
        froggerGame.score = 0;
        initFroggerGame();
      }
    }
  });

  let onRiverSupport = false;
  froggerGame.logs.forEach(l => {
    l.x += l.speed;
    if (l.speed < 0 && l.x < -60) l.x = 240 + Math.random() * 20;
    else if (l.speed > 0 && l.x > 260) l.x = -60;

    if (fg.gridY >= 2 && fg.gridY <= 6) {
      if (Math.abs(l.y - fg.y) < 8 && fg.x >= l.x - 4 && fg.x <= l.x + l.w + 4) {
        onRiverSupport = true;
        fg.x += l.speed;
        fg.gridX = Math.round((fg.x - 8) / 16);
      }
    }
  });

  if (fg.gridY >= 2 && fg.gridY <= 6 && !onRiverSupport && currentMode !== 'tour') {
    playArcadeSfx('FROG-SPLASH');
    fg.gridX = 7; fg.gridY = 13; fg.x = 112; fg.y = 216;
    froggerGame.lives--;
    if (froggerGame.lives <= 0) {
      froggerGame.lives = 3;
      froggerGame.score = 0;
      initFroggerGame();
    }
  }

  if (fg.gridY === 1) {
    const bayIndex = Math.floor((fg.x - 10) / 48);
    if (bayIndex >= 0 && bayIndex < 5 && !froggerGame.homeBays[bayIndex]) {
      froggerGame.homeBays[bayIndex] = true;
      froggerGame.score += 500;
      if (froggerGame.score > froggerGame.highScore) froggerGame.highScore = froggerGame.score;
      playArcadeSfx('FROG-HOME');
      fg.gridX = 7; fg.gridY = 13; fg.x = 112; fg.y = 216;

      if (froggerGame.homeBays.every(b => b)) {
        froggerGame.score += 1000;
        playArcadeSfx('BONUS');
        froggerGame.homeBays = [false, false, false, false, false];
      }
    } else {
      fg.gridX = 7; fg.gridY = 13; fg.x = 112; fg.y = 216;
      playArcadeSfx('FROG-SPLAT');
    }
  }
}

function renderFroggerGame() {
  if (!ctx) return;
  if (ctx.save) ctx.save();

  ctx.fillStyle = '#10ac84';
  ctx.fillRect(0, 16, 240, 18);
  const bayX = [20, 68, 116, 164, 212];
  bayX.forEach((bx, idx) => {
    ctx.fillStyle = '#0984e3';
    ctx.fillRect(bx - 10, 16, 20, 18);
    ctx.fillStyle = '#2ecc71';
    ctx.beginPath();
    ctx.arc(bx, 25, 7, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(bx - 1, 23, 3, 3);

    if (froggerGame.homeBays[idx]) {
      ctx.fillStyle = '#2ed573';
      ctx.fillRect(bx - 4, 20, 8, 8);
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(bx - 3, 19, 2, 2);
      ctx.fillRect(bx + 1, 19, 2, 2);
    }
  });

  const rTick = froggerGame.tick;
  ctx.fillStyle = '#0652dd';
  ctx.fillRect(0, 34, 240, 84);
  ctx.strokeStyle = '#1e90ff';
  ctx.lineWidth = 1.0;
  for (let rw = 0; rw < 5; rw++) {
    const wy = 42 + rw * 16;
    ctx.beginPath();
    for (let wx = 0; wx < 240; wx += 20) {
      const sx = (wx + rTick * 0.8) % 240;
      ctx.moveTo(sx, wy); ctx.lineTo(sx + 8, wy);
    }
    ctx.stroke();
  }

  ctx.fillStyle = '#2f3542';
  ctx.fillRect(0, 118, 240, 16);
  ctx.fillStyle = '#57606f';
  ctx.fillRect(0, 118, 240, 2); ctx.fillRect(0, 132, 240, 2);

  ctx.fillStyle = '#1e272e';
  ctx.fillRect(0, 134, 240, 80);
  for (let r = 1; r < 5; r++) {
    for (let c = 0; c < 240; c += 24) {
      ctx.fillStyle = '#dfe4ea';
      ctx.fillRect(c, 134 + r * 16, 12, 1);
    }
  }

  ctx.fillStyle = '#2f3542';
  ctx.fillRect(0, 214, 240, 26);
  ctx.fillStyle = '#10ac84';
  ctx.fillRect(0, 214, 240, 3);

  froggerGame.logs.forEach(l => {
    if (l.type === 'log') {
      ctx.fillStyle = '#b36b2b';
      ctx.fillRect(l.x, l.y - 6, l.w, 12);
      ctx.fillStyle = '#d35400';
      ctx.fillRect(l.x + 4, l.y - 3, l.w - 8, 2);
      ctx.strokeStyle = '#5d4037';
      ctx.lineWidth = 1.0;
      if (ctx.strokeRect) ctx.strokeRect(l.x, l.y - 6, l.w, 12);
      ctx.fillStyle = '#e58e26';
      ctx.beginPath();
      ctx.arc(l.x + 2, l.y, 4, 0, Math.PI * 2);
      ctx.fill();
    } else {
      const swim = Math.sin(rTick * 0.18) * 2;
      for (let tx = l.x; tx < l.x + l.w; tx += 15) {
        ctx.fillStyle = '#e55039';
        ctx.beginPath();
        ctx.arc(tx + 6, l.y, 5, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#f6b93b';
        ctx.fillRect(tx + 4, l.y - 3, 4, 6);
        ctx.fillStyle = '#78e08f';
        ctx.fillRect(tx + 1, l.y - 6 + swim, 3, 3);
        ctx.fillRect(tx + 8, l.y - 6 + swim, 3, 3);
        ctx.fillRect(tx + 1, l.y + 4 - swim, 3, 3);
        ctx.fillRect(tx + 8, l.y + 4 - swim, 3, 3);
      }
    }
  });

  froggerGame.vehicles.forEach(v => {
    ctx.save();
    ctx.translate(v.x, v.y);
    if (v.speed < 0) ctx.scale(-1, 1);

    if (v.type === 'truck') {
      ctx.fillStyle = '#10ac84';
      ctx.fillRect(0, -6, 12, 12);
      ctx.fillStyle = '#2f3542';
      ctx.fillRect(-22, -6, 22, 12);
      ctx.fillStyle = '#dfe4ea';
      ctx.fillRect(6, -5, 4, 5);
      ctx.fillStyle = '#000000';
      ctx.fillRect(-18, 6, 6, 2); ctx.fillRect(-6, 6, 6, 2); ctx.fillRect(4, 6, 6, 2);
      ctx.fillRect(-18, -8, 6, 2); ctx.fillRect(-6, -8, 6, 2); ctx.fillRect(4, -8, 6, 2);
    } else if (v.type === 'racer') {
      ctx.fillStyle = '#eb2f06';
      ctx.beginPath();
      ctx.moveTo(12, 0); ctx.lineTo(-10, -6); ctx.lineTo(-10, 6);
      ctx.closePath();
      ctx.fill();
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(-12, -7, 3, 14);
      ctx.fillStyle = '#feca57';
      ctx.beginPath();
      ctx.arc(-2, 0, 3, 0, Math.PI * 2);
      ctx.fill();
    } else if (v.type === 'formula') {
      ctx.fillStyle = '#a55eea';
      ctx.fillRect(-8, -4, 18, 8);
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(-4, -6, 4, 12); ctx.fillRect(8, -6, 3, 12);
    } else {
      ctx.fillStyle = '#feca57';
      ctx.fillRect(-10, -6, 20, 12);
      ctx.fillStyle = '#2d3436';
      ctx.fillRect(-2, -5, 8, 10);
      ctx.fillStyle = '#000000';
      ctx.fillRect(-4, -7, 6, 2);
    }
    ctx.restore();
  });

  const fg = froggerGame.frog;
  ctx.save();
  ctx.translate(fg.x, fg.y);
  if (fg.dir === 'down') ctx.rotate(Math.PI);
  else if (fg.dir === 'left') ctx.rotate(-Math.PI / 2);
  else if (fg.dir === 'right') ctx.rotate(Math.PI / 2);

  ctx.fillStyle = '#2ed573';
  ctx.fillRect(-5, -5, 10, 10);
  ctx.fillStyle = '#10ac84';
  ctx.fillRect(-3, -3, 6, 6);

  if (fg.hopTick > 0) {
    ctx.fillStyle = '#2ed573';
    ctx.fillRect(-7, 4, 3, 6); ctx.fillRect(4, 4, 3, 6);
  } else {
    ctx.fillStyle = '#10ac84';
    ctx.fillRect(-6, 3, 4, 3); ctx.fillRect(2, 3, 4, 3);
  }

  ctx.fillStyle = '#ffffff';
  ctx.fillRect(-5, -7, 3, 3); ctx.fillRect(2, -7, 3, 3);
  ctx.fillStyle = '#000000';
  ctx.fillRect(-4, -6, 2, 2); ctx.fillRect(3, -6, 2, 2);
  ctx.restore();

  ctx.fillStyle = '#f1c40f';
  ctx.font = 'bold 8px monospace';
  ctx.fillText('1UP', 18, 12);
  ctx.fillStyle = '#ffffff';
  ctx.fillText(String(froggerGame.score).padStart(6, '0'), 18, 22);
  ctx.fillStyle = '#00d2d3';
  ctx.fillText('HIGH SCORE', 92, 12);
  ctx.fillStyle = '#ffffff';
  ctx.fillText(String(froggerGame.highScore).padStart(6, '0'), 102, 22);

  for (let l = 0; l < froggerGame.lives; l++) {
    ctx.fillStyle = '#2ed573';
    ctx.fillText('🐸', 188 + l * 10, 18);
  }

  if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
  if (ctx.restore) ctx.restore();
}

function renderFroggerTour(f) {
  if (!froggerGame.active) initFroggerGame();
  updateFroggerGame();
  renderFroggerGame();
}

// -------------------------------------------------------------------------
// 4. ASTEROIDS (1979 ATARI QUADRASCAN 6502): FULLY PLAYABLE ARCADE ENGINE
// -------------------------------------------------------------------------
const asteroidsGame = {
  active: false,
  ship: { x: 120, y: 120, angle: -Math.PI / 2, vx: 0, vy: 0, thrust: false },
  bullets: [],
  rocks: [],
  debris: [],
  saucer: { active: false, x: -20, y: 50, vx: 1.2, timer: 0 },
  score: 0,
  highScore: 15000,
  lives: 3,
  level: 1,
  tick: 0
};

function initAsteroidsGame() {
  asteroidsGame.active = true;
  asteroidsGame.ship.x = 120;
  asteroidsGame.ship.y = 120;
  asteroidsGame.ship.angle = -Math.PI / 2;
  asteroidsGame.ship.vx = 0;
  asteroidsGame.ship.vy = 0;
  asteroidsGame.ship.thrust = false;
  asteroidsGame.bullets = [];
  asteroidsGame.debris = [];
  asteroidsGame.saucer = { active: false, x: -20, y: 50, vx: 1.2, timer: 0 };
  asteroidsGame.score = 0;
  asteroidsGame.lives = 3;
  asteroidsGame.level = 1;
  asteroidsGame.tick = 0;
  spawnAsteroidsField(4);
}

function spawnAsteroidsField(count) {
  asteroidsGame.rocks = [];
  for (let i = 0; i < count; i++) {
    asteroidsGame.rocks.push({
      x: (i * 60 + 30) % 240,
      y: (i * 50 + 20) % 240,
      vx: (Math.random() - 0.5) * 1.6,
      vy: (Math.random() - 0.5) * 1.6,
      radius: 18,
      size: 3
    });
  }
}

function asteroidsFire() {
  initAudio();
  if (asteroidsGame.bullets.length < 5) {
    const s = asteroidsGame.ship;
    asteroidsGame.bullets.push({
      x: s.x + Math.cos(s.angle) * 8,
      y: s.y + Math.sin(s.angle) * 8,
      vx: Math.cos(s.angle) * 5.6 + s.vx * 0.4,
      vy: Math.sin(s.angle) * 5.6 + s.vy * 0.4,
      life: 40
    });
    playArcadeSfx('AST-FIRE');
  }
}

function asteroidsHyperspace() {
  initAudio();
  asteroidsGame.ship.x = Math.random() * 220 + 10;
  asteroidsGame.ship.y = Math.random() * 220 + 10;
  asteroidsGame.ship.vx = 0;
  asteroidsGame.ship.vy = 0;
  playArcadeSfx('DEF-HYPER');
}

function updateAsteroidsGame() {
  asteroidsGame.tick++;
  const s = asteroidsGame.ship;

  if (currentMode === 'tour') {
    let closest = null, minD = 9999;
    asteroidsGame.rocks.forEach(rk => {
      const d = Math.hypot(rk.x - s.x, rk.y - s.y);
      if (d < minD) { minD = d; closest = rk; }
    });
    if (closest) {
      const targetAngle = Math.atan2(closest.y - s.y, closest.x - s.x);
      let da = targetAngle - s.angle;
      while (da < -Math.PI) da += Math.PI * 2;
      while (da > Math.PI) da -= Math.PI * 2;
      s.angle += Math.sign(da) * Math.min(Math.abs(da), 0.08);
      if (Math.abs(da) < 0.35 && asteroidsGame.tick % 16 === 0) asteroidsFire();
      s.thrust = (minD > 65 && asteroidsGame.tick % 50 < 20);
    }
  } else {
    if (arcadeKeysDown['a'] || arcadeKeysDown['arrowleft']) s.angle -= 0.08;
    if (arcadeKeysDown['d'] || arcadeKeysDown['arrowright']) s.angle += 0.08;
    s.thrust = !!(arcadeKeysDown['w'] || arcadeKeysDown['arrowup']);
  }

  if (s.thrust) {
    s.vx += Math.cos(s.angle) * 0.12;
    s.vy += Math.sin(s.angle) * 0.12;
    if (asteroidsGame.tick % 10 === 0) playArcadeSfx('AST-THR');
  }
  s.vx *= 0.985;
  s.vy *= 0.985;
  s.x += s.vx;
  s.y += s.vy;

  if (s.x < 0) s.x += 240; else if (s.x > 240) s.x -= 240;
  if (s.y < 0) s.y += 240; else if (s.y > 240) s.y -= 240;

  for (let b = asteroidsGame.bullets.length - 1; b >= 0; b--) {
    const bl = asteroidsGame.bullets[b];
    bl.x += bl.vx;
    bl.y += bl.vy;
    if (bl.x < 0) bl.x += 240; else if (bl.x > 240) bl.x -= 240;
    if (bl.y < 0) bl.y += 240; else if (bl.y > 240) bl.y -= 240;
    bl.life--;
    if (bl.life <= 0) {
      asteroidsGame.bullets.splice(b, 1);
      continue;
    }

    for (let r = asteroidsGame.rocks.length - 1; r >= 0; r--) {
      const rk = asteroidsGame.rocks[r];
      const dist = Math.hypot(bl.x - rk.x, bl.y - rk.y);
      if (dist < rk.radius) {
        asteroidsGame.bullets.splice(b, 1);
        playArcadeSfx('AST-EXP');
        const pts = (rk.size === 3) ? 50 : ((rk.size === 2) ? 100 : 200);
        asteroidsGame.score += pts;
        if (asteroidsGame.score > asteroidsGame.highScore) asteroidsGame.highScore = asteroidsGame.score;

        for (let d = 0; d < 6; d++) {
          asteroidsGame.debris.push({
            x: rk.x, y: rk.y,
            vx: (Math.random() - 0.5) * 3,
            vy: (Math.random() - 0.5) * 3,
            len: 4 + Math.random() * 4,
            angle: Math.random() * Math.PI * 2,
            vRot: (Math.random() - 0.5) * 0.2,
            life: 25
          });
        }

        if (rk.size > 1) {
          for (let sp = 0; sp < 2; sp++) {
            asteroidsGame.rocks.push({
              x: rk.x,
              y: rk.y,
              vx: (Math.random() - 0.5) * 2.2,
              vy: (Math.random() - 0.5) * 2.2,
              radius: (rk.size === 3) ? 12 : 7,
              size: rk.size - 1
            });
          }
        }
        asteroidsGame.rocks.splice(r, 1);
        break;
      }
    }
  }

  for (let d = asteroidsGame.debris.length - 1; d >= 0; d--) {
    const db = asteroidsGame.debris[d];
    db.x += db.vx;
    db.y += db.vy;
    db.angle += db.vRot;
    db.life--;
    if (db.life <= 0) asteroidsGame.debris.splice(d, 1);
  }

  asteroidsGame.rocks.forEach(rk => {
    rk.x += rk.vx;
    rk.y += rk.vy;
    if (rk.x < 0) rk.x += 240; else if (rk.x > 240) rk.x -= 240;
    if (rk.y < 0) rk.y += 240; else if (rk.y > 240) rk.y -= 240;

    const dist = Math.hypot(s.x - rk.x, s.y - rk.y);
    if (dist < rk.radius + 5 && currentMode !== 'tour') {
      playArcadeSfx('AST-EXP');
      asteroidsGame.lives--;
      s.x = 120; s.y = 120; s.vx = 0; s.vy = 0;
      if (asteroidsGame.lives <= 0) {
        asteroidsGame.lives = 3;
        asteroidsGame.score = 0;
        initAsteroidsGame();
      }
    }
  });

  if (asteroidsGame.rocks.length === 0) {
    asteroidsGame.level++;
    playArcadeSfx('WARP');
    spawnAsteroidsField(4 + asteroidsGame.level);
  }
}

function renderAsteroidsGame() {
  if (!ctx) return;
  if (ctx.save) ctx.save();

  ctx.fillStyle = '#05070a';
  ctx.fillRect(0, 0, 240, 240);

  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = 1.4;
  ctx.shadowColor = '#00e5ff';
  ctx.shadowBlur = 4;

  ctx.fillStyle = '#ffffff';
  asteroidsGame.bullets.forEach(bl => {
    ctx.fillRect(bl.x - 1, bl.y - 1, 2, 2);
  });

  asteroidsGame.debris.forEach(db => {
    ctx.save();
    ctx.translate(db.x, db.y);
    ctx.rotate(db.angle);
    ctx.beginPath();
    ctx.moveTo(-db.len / 2, 0); ctx.lineTo(db.len / 2, 0);
    ctx.stroke();
    ctx.restore();
  });

  asteroidsGame.rocks.forEach(rk => {
    ctx.beginPath();
    const pts = (rk.size === 3) ? 10 : ((rk.size === 2) ? 8 : 6);
    for (let i = 0; i < pts; i++) {
      const a = (i / pts) * Math.PI * 2;
      const r = rk.radius * (1 + Math.sin(i * 2.3 + rk.size) * 0.22);
      const px = rk.x + Math.cos(a) * r;
      const py = rk.y + Math.sin(a) * r;
      if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.stroke();
  });

  const s = asteroidsGame.ship;
  ctx.save();
  ctx.translate(s.x, s.y);
  ctx.rotate(s.angle);
  ctx.beginPath();
  ctx.moveTo(9, 0);
  ctx.lineTo(-7, -6);
  ctx.lineTo(-4, 0);
  ctx.lineTo(-7, 6);
  ctx.closePath();
  ctx.stroke();

  if (s.thrust && (asteroidsGame.tick % 4 < 2)) {
    ctx.strokeStyle = '#ff9f43';
    ctx.beginPath();
    ctx.moveTo(-4, 0); ctx.lineTo(-11, 0);
    ctx.stroke();
  }
  ctx.restore();

  ctx.shadowBlur = 0;

  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 8px monospace';
  ctx.fillText(String(asteroidsGame.score).padStart(6, '0'), 18, 16);
  ctx.fillText(`SECTOR ${asteroidsGame.level}`, 100, 16);
  for (let l = 0; l < asteroidsGame.lives; l++) {
    ctx.fillText('▲', 190 + l * 10, 16);
  }

  if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
  if (ctx.restore) ctx.restore();
}

function renderAsteroidsTour(f) {
  if (!asteroidsGame.active) initAsteroidsGame();
  updateAsteroidsGame();
  renderAsteroidsGame();
}

// -------------------------------------------------------------------------
// 5. TEMPEST (1981 ATARI COLOR VECTOR): FULLY PLAYABLE ARCADE ENGINE
// -------------------------------------------------------------------------
const tempestGame = {
  active: false,
  segment: 0,
  shots: [],
  enemies: [],
  score: 0,
  highScore: 25000,
  lives: 3,
  superzapperUsed: false,
  superzapperFlash: 0,
  tube: 9,
  tick: 0
};

function initTempestGame() {
  tempestGame.active = true;
  tempestGame.segment = 0;
  tempestGame.shots = [];
  tempestGame.enemies = [];
  tempestGame.score = 0;
  tempestGame.lives = 3;
  tempestGame.superzapperUsed = false;
  tempestGame.superzapperFlash = 0;
  tempestGame.tube = 9;
  tempestGame.tick = 0;
  spawnTempestEnemies();
}

function spawnTempestEnemies() {
  tempestGame.enemies = [];
  for (let i = 0; i < 4; i++) {
    tempestGame.enemies.push({
      seg: (i * 4) % 16,
      dist: 0.15 + i * 0.12,
      vDist: 0.0035,
      type: (i % 2 === 0) ? 'flipper' : 'spiker'
    });
  }
}

function tempestFire() {
  initAudio();
  if (tempestGame.shots.length < 6) {
    tempestGame.shots.push({
      seg: tempestGame.segment,
      dist: 0.95,
      vDist: -0.055
    });
    playArcadeSfx('TEM-FIRE');
  }
}

function tempestSuperzapper() {
  initAudio();
  if (!tempestGame.superzapperUsed) {
    tempestGame.superzapperUsed = true;
    tempestGame.superzapperFlash = 20;
    tempestGame.enemies.forEach(en => {
      tempestGame.score += 150;
    });
    tempestGame.enemies = [];
    playArcadeSfx('TEM-ZAP');
  }
}

function updateTempestGame() {
  tempestGame.tick++;

  if (currentMode === 'tour') {
    let closest = null, minD = -1;
    tempestGame.enemies.forEach(en => {
      if (en.dist > minD) { minD = en.dist; closest = en; }
    });
    if (closest) {
      const targetSeg = closest.seg;
      let diff = (targetSeg - tempestGame.segment + 16) % 16;
      if (diff > 8) diff -= 16;
      if (tempestGame.tick % 4 === 0) {
        if (diff > 0) tempestGame.segment = (tempestGame.segment + 1) % 16;
        else if (diff < 0) tempestGame.segment = (tempestGame.segment - 1 + 16) % 16;
      }
      if (tempestGame.tick % 10 === 0) tempestFire();
      if (minD > 0.85 && tempestGame.tick % 100 === 0) tempestSuperzapper();
    } else {
      if (tempestGame.tick % 14 === 0) tempestGame.segment = (tempestGame.segment + 1) % 16;
      if (tempestGame.tick % 16 === 0) tempestFire();
    }
  }

  if (tempestGame.superzapperFlash > 0) tempestGame.superzapperFlash--;

  for (let s = tempestGame.shots.length - 1; s >= 0; s--) {
    const sh = tempestGame.shots[s];
    sh.dist += sh.vDist;
    if (sh.dist <= 0) {
      tempestGame.shots.splice(s, 1);
      continue;
    }
    for (let e = tempestGame.enemies.length - 1; e >= 0; e--) {
      const en = tempestGame.enemies[e];
      if (en.seg === sh.seg && Math.abs(en.dist - sh.dist) < 0.08) {
        tempestGame.shots.splice(s, 1);
        tempestGame.enemies.splice(e, 1);
        tempestGame.score += 150;
        if (tempestGame.score > tempestGame.highScore) tempestGame.highScore = tempestGame.score;
        playArcadeSfx('AST-EXP');
        break;
      }
    }
  }

  tempestGame.enemies.forEach(en => {
    en.dist += en.vDist;
    if (en.type === 'flipper' && tempestGame.tick % 45 === 0) {
      en.seg = (en.seg + (Math.random() < 0.5 ? 1 : 15)) % 16;
    }
    if (en.dist >= 1.0 && currentMode !== 'tour') {
      if (en.seg === tempestGame.segment) {
        playArcadeSfx('DEATH');
        tempestGame.lives--;
        tempestGame.enemies = [];
        spawnTempestEnemies();
        if (tempestGame.lives <= 0) {
          tempestGame.lives = 3;
          tempestGame.score = 0;
          initTempestGame();
        }
      }
    }
  });

  if (tempestGame.enemies.length === 0) {
    tempestGame.tube++;
    tempestGame.superzapperUsed = false;
    playArcadeSfx('WARP');
    spawnTempestEnemies();
  }
}

function renderTempestGame() {
  if (!ctx) return;
  if (ctx.save) ctx.save();

  ctx.fillStyle = '#05070a';
  ctx.fillRect(0, 0, 240, 240);

  const cx = 120, cy = 125;
  const numSegs = 16;
  const rNear = 95, rFar = 22;

  if (tempestGame.superzapperFlash > 0) {
    ctx.strokeStyle = '#00e5ff';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    for (let i = 0; i < numSegs; i++) {
      const a = (i / numSegs) * Math.PI * 2;
      const nx = cx + Math.cos(a) * rNear;
      const ny = cy + Math.sin(a) * (rNear * 0.6);
      if (i === 0) ctx.moveTo(nx, ny); else ctx.lineTo(nx, ny);
    }
    ctx.closePath();
    ctx.stroke();
  }

  ctx.strokeStyle = '#00d2d3';
  ctx.lineWidth = 1.6;
  ctx.shadowColor = '#00e5ff';
  ctx.shadowBlur = 4;

  ctx.beginPath();
  for (let i = 0; i < numSegs; i++) {
    const a = (i / numSegs) * Math.PI * 2;
    const fx = cx + Math.cos(a) * rFar;
    const fy = cy + Math.sin(a) * (rFar * 0.6);
    if (i === 0) ctx.moveTo(fx, fy); else ctx.lineTo(fx, fy);
  }
  ctx.closePath();
  ctx.stroke();

  ctx.beginPath();
  for (let i = 0; i < numSegs; i++) {
    const a = (i / numSegs) * Math.PI * 2;
    const nx = cx + Math.cos(a) * rNear;
    const ny = cy + Math.sin(a) * (rNear * 0.6);
    if (i === 0) ctx.moveTo(nx, ny); else ctx.lineTo(nx, ny);
  }
  ctx.closePath();
  ctx.stroke();

  for (let i = 0; i < numSegs; i++) {
    const a = (i / numSegs) * Math.PI * 2;
    const nx = cx + Math.cos(a) * rNear;
    const ny = cy + Math.sin(a) * (rNear * 0.6);
    const fx = cx + Math.cos(a) * rFar;
    const fy = cy + Math.sin(a) * (rFar * 0.6);
    ctx.beginPath();
    ctx.moveTo(nx, ny); ctx.lineTo(fx, fy);
    ctx.stroke();
  }

  tempestGame.enemies.forEach(en => {
    const a = (en.seg + 0.5) / numSegs * Math.PI * 2;
    const r = rFar + (rNear - rFar) * en.dist;
    const ex = cx + Math.cos(a) * r;
    const ey = cy + Math.sin(a) * (r * 0.6);
    const scale = 0.8 + en.dist * 0.8;

    ctx.save();
    ctx.translate(ex, ey);
    ctx.rotate(a + Math.PI / 2);
    ctx.strokeStyle = (tempestGame.tick % 6 < 3) ? '#eb2f06' : '#ff9f1a';
    ctx.lineWidth = 1.6;
    ctx.beginPath();
    ctx.moveTo(-5 * scale, -4 * scale); ctx.lineTo(-2 * scale, 0); ctx.lineTo(-5 * scale, 4 * scale);
    ctx.lineTo(2 * scale, 0);
    ctx.lineTo(5 * scale, -4 * scale); ctx.lineTo(2 * scale, 0); ctx.lineTo(5 * scale, 4 * scale);
    ctx.stroke();
    ctx.restore();
  });

  ctx.fillStyle = '#f1c40f';
  tempestGame.shots.forEach(sh => {
    const a = (sh.seg + 0.5) / numSegs * Math.PI * 2;
    const r = rFar + (rNear - rFar) * sh.dist;
    const sx = cx + Math.cos(a) * r;
    const sy = cy + Math.sin(a) * (r * 0.6);
    ctx.fillRect(sx - 1, sy - 1, 3, 3);
  });

  const aBlaster = (tempestGame.segment + 0.5) / numSegs * Math.PI * 2;
  const bx = cx + Math.cos(aBlaster) * rNear;
  const by = cy + Math.sin(aBlaster) * (rNear * 0.6);
  ctx.save();
  ctx.translate(bx, by);
  ctx.rotate(aBlaster + Math.PI / 2);
  ctx.strokeStyle = '#fff200';
  ctx.lineWidth = 2.4;
  ctx.beginPath();
  ctx.moveTo(-7, -5); ctx.lineTo(-3, 1); ctx.lineTo(0, -2); ctx.lineTo(3, 1); ctx.lineTo(7, -5);
  ctx.stroke();
  ctx.fillStyle = '#00f5d4';
  ctx.fillRect(-8, -6, 2, 2); ctx.fillRect(6, -6, 2, 2);
  ctx.restore();

  ctx.shadowBlur = 0;

  ctx.fillStyle = '#00e5ff';
  ctx.font = 'bold 8px monospace';
  ctx.fillText(`SCORE: ${tempestGame.score}`, 18, 16);
  ctx.fillText(`TUBE 09`, 105, 16);
  ctx.fillText(`LIVES: ${tempestGame.lives}`, 180, 16);

  if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
  if (ctx.restore) ctx.restore();
}

function renderTempestTour(f) {
  if (!tempestGame.active) initTempestGame();
  updateTempestGame();
  renderTempestGame();
}

// -------------------------------------------------------------------------
// 6. GYRUSS (1983 KONAMI 5x PSG): FULLY PLAYABLE ARCADE ENGINE
// -------------------------------------------------------------------------
const gyrussGame = {
  active: false,
  angle: -Math.PI / 2,
  shots: [],
  enemies: [],
  score: 0,
  highScore: 30000,
  lives: 3,
  warp: 3,
  tick: 0
};

function initGyrussGame() {
  gyrussGame.active = true;
  gyrussGame.angle = -Math.PI / 2;
  gyrussGame.shots = [];
  gyrussGame.enemies = [];
  gyrussGame.score = 0;
  gyrussGame.lives = 3;
  gyrussGame.warp = 3;
  gyrussGame.tick = 0;
}

function gyrussFire() {
  initAudio();
  if (gyrussGame.shots.length < 6) {
    const a = gyrussGame.angle;
    gyrussGame.shots.push({ angle: a - 0.05, dist: 96, vDist: -4.8 });
    gyrussGame.shots.push({ angle: a + 0.05, dist: 96, vDist: -4.8 });
    playArcadeSfx('GYRUSS-LAS');
  }
}

function updateGyrussGame() {
  gyrussGame.tick++;
  const g = gyrussGame;

  if (currentMode === 'tour') {
    gyrussGame.angle += 0.055;
    if (gyrussGame.tick % 12 === 0) gyrussFire();
  } else {
    if (arcadeKeysDown['a'] || arcadeKeysDown['arrowleft']) gyrussGame.angle -= 0.07;
    if (arcadeKeysDown['d'] || arcadeKeysDown['arrowright']) gyrussGame.angle += 0.07;
  }

  for (let s = g.shots.length - 1; s >= 0; s--) {
    const sh = g.shots[s];
    sh.dist += sh.vDist;
    if (sh.dist <= 8) {
      g.shots.splice(s, 1);
      continue;
    }
    for (let e = g.enemies.length - 1; e >= 0; e--) {
      const en = g.enemies[e];
      if (Math.abs(en.angle - sh.angle) < 0.28 && Math.abs(en.dist - sh.dist) < 12) {
        g.shots.splice(s, 1);
        g.enemies.splice(e, 1);
        g.score += 200;
        playArcadeSfx('GYRUSS-EXP');
        break;
      }
    }
  }

  if (g.tick % 40 === 0) {
    g.enemies.push({
      angle: Math.random() * Math.PI * 2,
      dist: 10,
      vDist: 1.4,
      vAngle: (Math.random() - 0.5) * 0.05
    });
  }

  for (let e = g.enemies.length - 1; e >= 0; e--) {
    const en = g.enemies[e];
    en.dist += en.vDist;
    en.angle += en.vAngle;

    if (en.dist >= 94 && en.dist <= 104 && currentMode !== 'tour') {
      if (Math.abs(en.angle - g.angle) < 0.25) {
        g.enemies.splice(e, 1);
        playArcadeSfx('DEATH');
        g.lives--;
        if (g.lives <= 0) {
          g.lives = 3;
          g.score = 0;
          initGyrussGame();
        }
        continue;
      }
    }
    if (en.dist > 115) {
      g.enemies.splice(e, 1);
    }
  }
}

function renderGyrussGame() {
  if (!ctx) return;
  if (ctx.save) ctx.save();

  ctx.fillStyle = '#05070a';
  ctx.fillRect(0, 0, 240, 240);

  const cx = 120, cy = 125;

  for (let r = 24; r <= 100; r += 24) {
    ctx.strokeStyle = `rgba(0, 229, 255, ${0.15 + (r / 100) * 0.35})`;
    ctx.lineWidth = 1.0;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();
  }

  ctx.strokeStyle = 'rgba(255, 255, 255, 0.45)';
  for (let st = 0; st < 24; st++) {
    const sa = (st / 24) * Math.PI * 2 + gyrussGame.tick * 0.015;
    ctx.beginPath();
    ctx.moveTo(cx + Math.cos(sa) * 20, cy + Math.sin(sa) * 20);
    ctx.lineTo(cx + Math.cos(sa) * 112, cy + Math.sin(sa) * 112);
    ctx.stroke();
  }

  ctx.fillStyle = '#0652dd';
  ctx.beginPath();
  ctx.arc(cx, cy, 20, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = '#00d2d3';
  ctx.beginPath();
  ctx.arc(cx - 4, cy - 4, 7, 0, Math.PI * 2);
  ctx.fill();

  gyrussGame.shots.forEach(sh => {
    const sx = cx + Math.cos(sh.angle) * sh.dist;
    const sy = cy + Math.sin(sh.angle) * sh.dist;
    ctx.fillStyle = '#f1c40f';
    ctx.fillRect(sx - 1, sy - 1, 3, 3);
  });

  gyrussGame.enemies.forEach(en => {
    const ex = cx + Math.cos(en.angle) * en.dist;
    const ey = cy + Math.sin(en.angle) * en.dist;
    const scale = Math.max(0.4, (en.dist / 100));

    ctx.save();
    ctx.translate(ex, ey);
    ctx.rotate(en.angle + Math.PI / 2);
    ctx.fillStyle = (gyrussGame.tick % 8 < 4) ? '#eb2f06' : '#e056fd';
    ctx.beginPath();
    ctx.moveTo(0, -6 * scale);
    ctx.lineTo(-8 * scale, 6 * scale);
    ctx.lineTo(-3 * scale, 4 * scale);
    ctx.lineTo(0, 5 * scale);
    ctx.lineTo(3 * scale, 4 * scale);
    ctx.lineTo(8 * scale, 6 * scale);
    ctx.closePath();
    ctx.fill();
    ctx.fillStyle = '#f9ca24';
    ctx.fillRect(-2 * scale, -2 * scale, 4 * scale, 4 * scale);
    ctx.restore();
  });

  const a = gyrussGame.angle;
  const sx = cx + Math.cos(a) * 98;
  const sy = cy + Math.sin(a) * 98;
  ctx.save();
  ctx.translate(sx, sy);
  ctx.rotate(a + Math.PI / 2);
  ctx.fillStyle = '#f8f9fa';
  ctx.beginPath();
  ctx.moveTo(0, -10); ctx.lineTo(-9, 7); ctx.lineTo(-3, 5); ctx.lineTo(3, 5); ctx.lineTo(9, 7);
  ctx.closePath();
  ctx.fill();
  ctx.fillStyle = '#00d2d3';
  ctx.fillRect(-2, -6, 4, 6);
  ctx.fillStyle = '#eb2f06';
  ctx.fillRect(-10, -1, 3, 7); ctx.fillRect(7, -1, 3, 7);
  ctx.fillStyle = (gyrussGame.tick % 4 < 2) ? '#54a0ff' : '#00d2d3';
  ctx.fillRect(-3, 6, 2, 4 + (gyrussGame.tick % 3));
  ctx.fillRect(1, 6, 2, 4 + (gyrussGame.tick % 3));
  ctx.restore();

  ctx.fillStyle = '#00e5ff';
  ctx.font = 'bold 8px monospace';
  ctx.fillText(`SCORE: ${gyrussGame.score}`, 18, 16);
  ctx.fillText(`WARP 3 TO NEPTUNE`, 84, 16);
  ctx.fillText(`LIVES: ${gyrussGame.lives}`, 190, 16);

  if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
  if (ctx.restore) ctx.restore();
}

function renderGyrussTour(f) {
  if (!gyrussGame.active) initGyrussGame();
  updateGyrussGame();
  renderGyrussGame();
}

function renderTourHud(game, f) {
  ctx.fillStyle = 'rgba(6, 9, 14, 0.92)';
  ctx.fillRect(0, 0, 240, 26);

  ctx.fillStyle = '#f5a623';
  ctx.font = 'bold 10px monospace';
  ctx.fillText(`★ TOUR: ${game.title}`, 8, 12);

  ctx.fillStyle = '#9aa0a6';
  ctx.font = '8px monospace';
  ctx.fillText(`${game.year} · ${game.badge}`, 8, 22);

  ctx.fillStyle = 'rgba(6, 9, 14, 0.92)';
  ctx.fillRect(0, 214, 240, 26);

  ctx.fillStyle = '#00e5ff';
  ctx.font = 'bold 8px monospace';
  ctx.fillText(`HW: ${game.cpu}`, 8, 225);

  const pulse = Math.sin(f * 0.15) > 0;
  ctx.fillStyle = pulse ? '#fffa65' : '#ffffff';
  ctx.font = 'bold 9px monospace';
  ctx.fillText('⚡ TAP / SPACE TO PLAY NOW!', 34, 236);
}'''

def update_build_hardware_template():
    with open('tools/build_hardware_template.py', 'r') as f:
        content = f.read()

    # 1. Replace the new_games_block in build_hardware_template.py
    # Lines 2081 to 4713 are between idx_cc check and script_body[:idx_cc]
    start_marker = '    if idx_cc != -1 and idx_td != -1:\n        new_games_block = """'
    end_marker = '        script_body = script_body[:idx_cc] + new_games_block + script_body[idx_td:]'
    
    idx_start = content.find(start_marker)
    idx_end = content.find(end_marker)
    assert idx_start != -1 and idx_end != -1, "Could not find new_games_block boundaries in build_hardware_template.py"

    upgraded_engines = generate_upgraded_arcade_engines()
    replacement = start_marker + upgraded_engines + '\n"""\n'
    content = content[:idx_start] + replacement + content[idx_end:]

    # 2. Update keyboard listener in additional_bindings to track keys in arcadeKeysDown and release velocities
    old_kbd_bindings = """// Keyboard button illumination
window.addEventListener('keydown', (e) => {
  const k = e.key.toLowerCase();
  if (k === 'a' || e.key === 'ArrowLeft') { if (cLeft) cLeft.classList.add('pressed'); }
  if (k === 'd' || e.key === 'ArrowRight') { if (cRight) cRight.classList.add('pressed'); }
  if (k === 'w' || e.key === 'ArrowUp') { if (cUp) cUp.classList.add('pressed'); }
  if (k === 's' || e.key === 'ArrowDown') { if (cDown) cDown.classList.add('pressed'); }
  if (e.key === ' ' || e.key === 'Enter') { if (cFire) cFire.classList.add('pressed'); }
  if (k === '1' || k === 'c') { if (cCoin) cCoin.classList.add('pressed'); }
  if (k === '5' || k === 'p') { if (cStart) cStart.classList.add('pressed'); }
  if (k === 'z') { toggleScreenZoom(); }
});

window.addEventListener('keyup', (e) => {
  const k = e.key.toLowerCase();
  if (k === 'a' || e.key === 'ArrowLeft') { if (cLeft) cLeft.classList.remove('pressed'); }
  if (k === 'd' || e.key === 'ArrowRight') { if (cRight) cRight.classList.remove('pressed'); }
  if (k === 'w' || e.key === 'ArrowUp') { if (cUp) cUp.classList.remove('pressed'); }
  if (k === 's' || e.key === 'ArrowDown') { if (cDown) cDown.classList.remove('pressed'); }
  if (e.key === ' ' || e.key === 'Enter') { if (cFire) cFire.classList.remove('pressed'); }
  if (k === '1' || k === 'c') { if (cCoin) cCoin.classList.remove('pressed'); }
  if (k === '5' || k === 'p') { if (cStart) cStart.classList.remove('pressed'); }
});"""

    new_kbd_bindings = """// Keyboard button illumination and continuous arcade physics tracking
window.addEventListener('keydown', (e) => {
  const k = e.key.toLowerCase();
  if (typeof arcadeKeysDown !== 'undefined') {
    arcadeKeysDown[k] = true;
    arcadeKeysDown[e.key] = true;
  }
  if (k === 'a' || e.key === 'ArrowLeft') { if (cLeft) cLeft.classList.add('pressed'); }
  if (k === 'd' || e.key === 'ArrowRight') { if (cRight) cRight.classList.add('pressed'); }
  if (k === 'w' || e.key === 'ArrowUp') { if (cUp) cUp.classList.add('pressed'); }
  if (k === 's' || e.key === 'ArrowDown') { if (cDown) cDown.classList.add('pressed'); }
  if (e.key === ' ' || e.key === 'Enter') { if (cFire) cFire.classList.add('pressed'); }
  if (k === '1' || k === 'c') { if (cCoin) cCoin.classList.add('pressed'); }
  if (k === '5' || k === 'p') { if (cStart) cStart.classList.add('pressed'); }
  if (k === 'z') { toggleScreenZoom(); }
});

window.addEventListener('keyup', (e) => {
  const k = e.key.toLowerCase();
  if (typeof arcadeKeysDown !== 'undefined') {
    delete arcadeKeysDown[k];
    delete arcadeKeysDown[e.key];
  }
  // Release physics velocity immediately so games never get stuck!
  if (typeof galagaGame !== 'undefined' && activeGame === 'galaga') {
    if ((k === 'a' || e.key === 'ArrowLeft') && galagaGame.moveDir === -1) galagaGame.moveDir = 0;
    if ((k === 'd' || e.key === 'ArrowRight') && galagaGame.moveDir === 1) galagaGame.moveDir = 0;
  }
  if (typeof dkongGame !== 'undefined' && activeGame === 'dkong') {
    if ((k === 'a' || e.key === 'ArrowLeft') && dkongGame.mario.vx < 0) {
      dkongGame.mario.vx = 0;
      if (dkongGame.mario.state === 'run') dkongGame.mario.state = dkongGame.mario.hasHammer ? 'hammer' : 'stand';
    }
    if ((k === 'd' || e.key === 'ArrowRight') && dkongGame.mario.vx > 0) {
      dkongGame.mario.vx = 0;
      if (dkongGame.mario.state === 'run') dkongGame.mario.state = dkongGame.mario.hasHammer ? 'hammer' : 'stand';
    }
  }
  if (typeof asteroidsGame !== 'undefined' && activeGame === 'asteroids') {
    if (k === 'w' || e.key === 'ArrowUp') asteroidsGame.ship.thrust = false;
  }
  if (k === 'a' || e.key === 'ArrowLeft') { if (cLeft) cLeft.classList.remove('pressed'); }
  if (k === 'd' || e.key === 'ArrowRight') { if (cRight) cRight.classList.remove('pressed'); }
  if (k === 'w' || e.key === 'ArrowUp') { if (cUp) cUp.classList.remove('pressed'); }
  if (k === 's' || e.key === 'ArrowDown') { if (cDown) cDown.classList.remove('pressed'); }
  if (e.key === ' ' || e.key === 'Enter') { if (cFire) cFire.classList.remove('pressed'); }
  if (k === '1' || k === 'c') { if (cCoin) cCoin.classList.remove('pressed'); }
  if (k === '5' || k === 'p') { if (cStart) cStart.classList.remove('pressed'); }
});"""

    if old_kbd_bindings in content:
        content = content.replace(old_kbd_bindings, new_kbd_bindings)

    # 3. Update handleUnifiedAction for D-Pad, screen quadrants, and silicone keys
    old_unified_action = """  } else if (activeGame === 'dkong') {
    if (act === 'up') dkongClimbUp();
    else if (act === 'down') dkongClimbDown();
    else if (act === 'left') { dkongGame.mario.x = Math.max(20, dkongGame.mario.x - 8); dkongGame.mario.facing = 'left'; }
    else if (act === 'right') { dkongGame.mario.x = Math.min(220, dkongGame.mario.x + 8); dkongGame.mario.facing = 'right'; }
    else if (act === 'action') dkongJump();"""

    new_unified_action = """  } else if (activeGame === 'dkong') {
    if (act === 'up') dkongClimbUp();
    else if (act === 'down') dkongClimbDown();
    else if (act === 'left') {
      dkongGame.mario.vx = -1.8;
      dkongGame.mario.facing = 'left';
      if (dkongGame.mario.onGround) dkongGame.mario.state = dkongGame.mario.hasHammer ? 'hammer' : 'run';
    } else if (act === 'right') {
      dkongGame.mario.vx = 1.8;
      dkongGame.mario.facing = 'right';
      if (dkongGame.mario.onGround) dkongGame.mario.state = dkongGame.mario.hasHammer ? 'hammer' : 'run';
    } else if (act === 'action') dkongJump();"""

    if old_unified_action in content:
        content = content.replace(old_unified_action, new_unified_action)

    with open('tools/build_hardware_template.py', 'w') as f:
        f.write(content)

    print("Successfully injected all upgraded authentic arcade engines into build_hardware_template.py!")

if __name__ == '__main__':
    update_build_hardware_template()
