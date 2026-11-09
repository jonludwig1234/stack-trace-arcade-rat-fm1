#!/usr/bin/env python3
"""
Upgrade all 6 remaining arcade engines (Crazy Climber, Galaga, Frogger, Asteroids, Tempest, Gyruss)
in tools/build_hardware_template.py to authentic arcade specifications, matching Donkey Kong's fidelity.
"""
import re

def build_crazy_climber_and_galaga():
    return '''// =========================================================================
// 8 AUTHENTIC PLAYABLE ARCADE ENGINES (High-Resolution CRT Graphics & Physics)
// Pac-Man, Crazy Climber, Galaga, Donkey Kong, Frogger, Asteroids, Tempest, Gyruss
// Integrated Autonomous Attract AI & High-Density Arcade Pixel Art / Vector CRT
// =========================================================================

// Global Keyboard Tracking for Smooth Multi-Key Response
var arcadeKeysDown = (typeof arcadeKeysDown !== 'undefined') ? arcadeKeysDown : {};
var dpadActiveDir = (typeof dpadActiveDir !== 'undefined') ? dpadActiveDir : null;

// -------------------------------------------------------------------------
// 0. CRAZY CLIMBER (1980 NICHIBUTSU Z80): FULLY PLAYABLE ARCADE ENGINE
// -------------------------------------------------------------------------
if (typeof climberState !== 'undefined') {
  climberState.floor = 1;
  climberState.leftArm = 'down';
  climberState.rightArm = 'down';
  climberState.col = 1;
  climberState.potY = -20;
  climberState.potCol = 2;
  climberState.dumbbells = [];
  climberState.score = 0;
  climberState.highScore = 18500;
  climberState.lives = 3;
  climberState.hanging = false;
  climberState.cleared = false;
  climberState.winTimer = 0;
  climberState.animTick = 0;
  climberState.stepCombo = 0;
  climberState.lastStepArm = null;
}

function initCrazyClimberGame() {
  climberState.floor = 1;
  climberState.leftArm = 'down';
  climberState.rightArm = 'down';
  climberState.col = 1;
  climberState.potY = -20;
  climberState.potCol = 2;
  climberState.dumbbells = [];
  climberState.score = 0;
  climberState.lives = 3;
  climberState.hanging = false;
  climberState.cleared = false;
  climberState.winTimer = 0;
  climberState.animTick = 0;
  climberState.stepCombo = 0;
  climberState.lastStepArm = null;
  playArcadeSfx('CLIMB-STEP');
}

function climberStep(arm, dir) {
  initAudio();
  if (climberState.cleared) return;
  const prevArmState = (arm === 'left') ? climberState.leftArm : climberState.rightArm;
  if (arm === 'left') climberState.leftArm = dir;
  else climberState.rightArm = dir;

  // Authentic Twin-Stick alternating pull:
  // Climber advances when left arm is up while right arm is down, or vice versa, alternating!
  if (climberState.leftArm !== climberState.rightArm && dir !== prevArmState) {
    climberState.floor++;
    climberState.score += 50;
    if (climberState.score > climberState.highScore) climberState.highScore = climberState.score;
    climberState.hanging = false;
    playArcadeSfx('CLIMB-STEP');

    // Roof Helicopter Rescue at Floor 50
    if (climberState.floor >= 50 && !climberState.cleared) {
      climberState.cleared = true;
      climberState.winTimer = 180;
      climberState.score += 10000;
      if (climberState.score > climberState.highScore) climberState.highScore = climberState.score;
      playArcadeSfx('CLIMB-WIN');
      if (typeof speakPhrase === 'function') speakPhrase('STEP IN');
    }
  }
}

function climberMove(dir) {
  initAudio();
  if (climberState.cleared || climberState.hanging) return;
  if (dir === 'left') climberState.col = Math.max(0, climberState.col - 1);
  else if (dir === 'right') climberState.col = Math.min(3, climberState.col + 1);
}

function updateCrazyClimberGame() {
  climberState.animTick++;
  const tick = climberState.animTick;

  // Autonomous Attract Tour AI
  if (currentMode === 'tour') {
    if (tick % 24 < 12) climberStep('left', 'up');
    else climberStep('right', 'up');
    if (climberState.potCol === climberState.col && climberState.potY > 50 && climberState.potY < 150) {
      climberState.col = (climberState.col + 1) % 4;
    }
  }

  // Falling Terracotta Flower Pot
  climberState.potY += 2.4;
  if (climberState.potY > 240) {
    climberState.potY = -15;
    climberState.potCol = Math.floor(Math.random() * 4);
  }

  const potY = climberState.potY;
  // Check Flowerpot Hit Climber
  if (climberState.potCol === climberState.col && potY > 110 && potY < 155 && currentMode !== 'tour') {
    climberState.potY = -20;
    climberState.floor = Math.max(1, climberState.floor - 2);
    climberState.lives--;
    playArcadeSfx('CLIMB-POT');
    if (typeof speakPhrase === 'function') speakPhrase('OUCH');
    if (climberState.lives <= 0) {
      initCrazyClimberGame();
    }
  }

  // Window Slam Hazard: if hands are raised when window closes, climber slips and hangs by one hand
  const currentWindowOpen = ((climberState.floor + climberState.col + (tick >> 6)) % 3 === 0);
  if (!currentWindowOpen && (climberState.leftArm === 'up' || climberState.rightArm === 'up') && tick % 140 === 0 && currentMode !== 'tour') {
    climberState.hanging = true;
    playArcadeSfx('CLIMB-SLIP');
  }

  // King Gorilla Ape on Left Pilaster (punches at columns 0 and 1)
  const kongY = 65 + Math.sin(tick * 0.08) * 12;
  const kongArmUp = (tick % 40 < 20);
  if (climberState.col <= 1 && Math.abs(kongY - 130) < 25 && kongArmUp && tick % 70 === 0 && currentMode !== 'tour') {
    playArcadeSfx('CLIMB-KONG');
    playArcadeSfx('DK-ROAR');
    climberState.floor = Math.max(1, climberState.floor - 3);
  }

  if (climberState.cleared && climberState.winTimer > 0) {
    climberState.winTimer--;
  }
}

function renderCrazyClimber() {
  updateCrazyClimberGame();
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

  // Alternating Arms or Hanging
  if (climberState.hanging) {
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(cx - 3, cy - 6, 5, 16);
    ctx.fillStyle = '#f8c291';
    ctx.fillRect(cx - 4, cy - 10, 7, 5);
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(cx + 20, cy + 16, 5, 14);
    ctx.fillStyle = '#f8c291';
    ctx.fillRect(cx + 19, cy + 28, 7, 5);
  } else {
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(cx - 3, leftArmUp ? cy - 4 : cy + 12, 5, 14);
    ctx.fillStyle = '#f8c291'; // White/Peach glove
    ctx.fillRect(cx - 4, leftArmUp ? cy - 8 : cy + 24, 7, 5);

    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(cx + 20, rightArmUp ? cy - 4 : cy + 12, 5, 14);
    ctx.fillStyle = '#f8c291';
    ctx.fillRect(cx + 19, rightArmUp ? cy - 8 : cy + 24, 7, 5);
  }

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
  isCapturing: false,
  captureAngle: 0,
  captureShipY: 220,
  tractorBeam: { active: false, x: 120, y: 75, height: 0, maxH: 140, state: 'off', boss: null, timer: 0 },
  capturedShip: null,
  isChallengingStage: false,
  hitsCount: 0,
  totalChallengingAliens: 40
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
  galagaGame.isCapturing = false;
  galagaGame.captureAngle = 0;
  galagaGame.captureShipY = 220;
  galagaGame.tractorBeam = { active: false, x: 120, y: 75, height: 0, maxH: 140, state: 'off', boss: null, timer: 0 };
  galagaGame.capturedShip = null;
  galagaGame.isChallengingStage = false;
  galagaGame.hitsCount = 0;
  spawnGalagaFleet();
  playArcadeSfx('GALAGA-INTRO');
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
  if (galagaGame.isCapturing) return;
  if (galagaGame.lasers.length < (galagaGame.dualFighter ? 8 : 4)) {
    if (galagaGame.dualFighter) {
      galagaGame.lasers.push({ x: galagaGame.shipX - 10, y: 214, vy: -6.0 });
      galagaGame.lasers.push({ x: galagaGame.shipX - 4,  y: 214, vy: -6.0 });
      galagaGame.lasers.push({ x: galagaGame.shipX + 4,  y: 214, vy: -6.0 });
      galagaGame.lasers.push({ x: galagaGame.shipX + 10, y: 214, vy: -6.0 });
    } else {
      galagaGame.lasers.push({ x: galagaGame.shipX - 4, y: 214, vy: -6.0 });
      galagaGame.lasers.push({ x: galagaGame.shipX + 4, y: 214, vy: -6.0 });
    }
    playArcadeSfx('GALAGA-FIRE');
  }
}

function updateGalagaGame() {
  galagaGame.tick++;
  const g = galagaGame;

  // Active Key Steer
  if (!g.isCapturing) {
    if (currentMode === 'tour') {
      let targetX = 120 + Math.sin(g.tick * 0.04) * 55;
      const diving = g.aliens.find(a => a.state === 'dive' || a.state === 'tractor');
      if (diving) targetX = diving.x;
      if (g.shipX < targetX - 3) g.shipX += 2.4;
      else if (g.shipX > targetX + 3) g.shipX -= 2.4;
      if (g.tick % 18 === 0) galagaFire();
    } else {
      if (arcadeKeysDown['a'] || arcadeKeysDown['arrowleft'] || (typeof dpadActiveDir !== 'undefined' && dpadActiveDir === 'left')) g.moveDir = -1;
      else if (arcadeKeysDown['d'] || arcadeKeysDown['arrowright'] || (typeof dpadActiveDir !== 'undefined' && dpadActiveDir === 'right')) g.moveDir = 1;
      else if (typeof dpadActiveDir === 'undefined' || !dpadActiveDir) g.moveDir = 0;
      g.shipX += g.moveDir * g.shipSpeed;
    }
    const maxBound = g.dualFighter ? 216 : 224;
    const minBound = g.dualFighter ? 24 : 16;
    g.shipX = Math.max(minBound, Math.min(maxBound, g.shipX));
  } else {
    // Player is being captured by tractor beam!
    g.captureAngle += 0.25;
    g.captureShipY -= 1.8;
    if (g.tractorBeam.boss && g.captureShipY <= g.tractorBeam.boss.y + 12) {
      // Reached Boss Galaga: dock as captive ship!
      g.capturedShip = { boss: g.tractorBeam.boss, x: g.tractorBeam.boss.x + 16, y: g.tractorBeam.boss.y };
      g.tractorBeam.active = false;
      g.tractorBeam.state = 'off';
      if (g.tractorBeam.boss) g.tractorBeam.boss.state = 'return';
      g.isCapturing = false;
      g.lives--;
      g.shipX = 120;
      g.captureShipY = 220;
      g.captureAngle = 0;
      if (g.lives <= 0) {
        g.lives = 3;
        g.score = 0;
        initGalagaGame();
      }
    }
  }

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
      if (Math.abs(l.x - al.x) < 14 && Math.abs(l.y - al.y) < 14) {
        al.hp--;
        g.lasers.splice(i, 1);
        if (g.isChallengingStage) g.hitsCount++;

        if (al.hp <= 0) {
          const isDiving = (al.state === 'dive' || al.state === 'tractor');
          const pts = isDiving ? (al.type === 'boss' ? 400 : 200) : (al.type === 'boss' ? 200 : 100);
          g.score += pts;
          if (g.score > g.highScore) g.highScore = g.score;
          g.scorePops.push({ x: al.x, y: al.y, text: String(pts), timer: 30 });
          g.explosions.push({ x: al.x, y: al.y, frame: 0 });
          if (al.type === 'boss') playArcadeSfx('BOSS');
          else playArcadeSfx('AST-EXP');
          if (pts >= 300) playArcadeSfx('BONUS');

          // If boss had tractor beam active, cancel it
          if (g.tractorBeam.active && g.tractorBeam.boss === al) {
            g.tractorBeam.active = false;
            g.tractorBeam.state = 'off';
            g.isCapturing = false;
          }

          // If boss had captured ship, release and create DUAL FIGHTER!
          if (g.capturedShip && g.capturedShip.boss === al) {
            g.dualFighter = true;
            g.capturedShip = null;
            playArcadeSfx('BONUS');
            g.score += 1000;
            g.scorePops.push({ x: 120, y: 180, text: 'DUAL FIGHTER! +1000', timer: 50 });
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

  // Aliens Sway, Dive, and Tractor Beam
  const sway = Math.sin(g.tick * 0.05) * 10;
  g.aliens.forEach(al => {
    if (al.state === 'grid') {
      al.x = al.homeX + sway;
      al.y = al.homeY + Math.sin(g.tick * 0.08 + al.homeX) * 2;
      if (Math.random() < 0.004 && g.aliens.filter(a => a.state === 'dive' || a.state === 'tractor').length < 3) {
        if (al.type === 'boss' && !g.tractorBeam.active && !g.dualFighter && !g.capturedShip && Math.random() < 0.45) {
          al.state = 'tractor_approach';
          al.diveTick = 0;
          playArcadeSfx('DIVE');
        } else {
          al.state = 'dive';
          al.diveTick = 0;
          playArcadeSfx('DIVE');
        }
      }
    } else if (al.state === 'tractor_approach') {
      al.diveTick++;
      al.y += 2.0;
      if (al.y >= 75) {
        al.state = 'tractor';
        al.y = 75;
        g.tractorBeam = {
          active: true,
          x: al.x,
          y: al.y + 12,
          height: 0,
          maxH: 135,
          state: 'expanding',
          boss: al,
          timer: 160
        };
        playArcadeSfx('TRACT');
      }
    } else if (al.state === 'tractor') {
      g.tractorBeam.timer--;
      if (g.tractorBeam.state === 'expanding') {
        g.tractorBeam.height += 4.5;
        if (g.tractorBeam.height >= g.tractorBeam.maxH) {
          g.tractorBeam.height = g.tractorBeam.maxH;
          g.tractorBeam.state = 'active';
        }
      }
      // Check capture collision if beam reaches bottom
      if (g.tractorBeam.state === 'active' && !g.isCapturing && !g.dualFighter) {
        if (Math.abs(g.shipX - g.tractorBeam.x) < 22) {
          g.isCapturing = true;
          g.captureShipY = 220;
          g.captureAngle = 0;
          playArcadeSfx('CAPTURE');
        }
      }
      if (g.tractorBeam.timer <= 0) {
        g.tractorBeam.active = false;
        g.tractorBeam.state = 'off';
        al.state = 'dive';
      }
    } else if (al.state === 'dive') {
      al.diveTick++;
      al.y += 2.4;
      al.x += Math.sin(al.diveTick * 0.12) * 3.2;
      al.angle = Math.sin(al.diveTick * 0.1) * 0.6;
      if (al.diveTick === 24 && g.bombs.length < 4 && !g.isChallengingStage) {
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
        al.angle = 0;
      }
    }
  });

  if (g.aliens.length === 0) {
    if (g.isChallengingStage) {
      if (g.hitsCount >= 40) {
        g.score += 10000;
        g.scorePops.push({ x: 120, y: 120, text: 'PERFECT! 10000 PTS', timer: 60 });
        playArcadeSfx('BONUS');
      }
      g.isChallengingStage = false;
    }
    g.stage++;
    playArcadeSfx('BONUS');
    if (g.stage % 4 === 3) {
      g.isChallengingStage = true;
      g.hitsCount = 0;
    }
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
    if (!g.isCapturing && Math.abs(bm.x - g.shipX) < (g.dualFighter ? 18 : 9) && Math.abs(bm.y - 220) < 9) {
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

  // Tractor Beam (Pulsating Blue-Cyan Conical Waves)
  if (galagaGame.tractorBeam.active) {
    const tb = galagaGame.tractorBeam;
    ctx.save();
    const beamGrad = ctx.createLinearGradient(tb.x, tb.y, tb.x, tb.y + tb.height);
    beamGrad.addColorStop(0, 'rgba(0, 229, 255, 0.55)');
    beamGrad.addColorStop(1, 'rgba(0, 210, 211, 0.15)');
    ctx.fillStyle = beamGrad;
    ctx.beginPath();
    ctx.moveTo(tb.x - 8, tb.y);
    ctx.lineTo(tb.x + 8, tb.y);
    const bottomW = 16 + (tb.height / tb.maxH) * 36;
    ctx.lineTo(tb.x + bottomW, tb.y + tb.height);
    ctx.lineTo(tb.x - bottomW, tb.y + tb.height);
    ctx.closePath();
    ctx.fill();

    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 1.0;
    for (let l = 10; l < tb.height; l += 14) {
      const lineW = 10 + (l / tb.maxH) * 32;
      const waveOff = Math.sin((tick * 0.2) + l * 0.1) * 3;
      ctx.beginPath();
      ctx.moveTo(tb.x - lineW + waveOff, tb.y + l);
      ctx.lineTo(tb.x + lineW + waveOff, tb.y + l);
      ctx.stroke();
    }
    ctx.restore();
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
  if (galagaGame.isChallengingStage) {
    ctx.fillText('CHALLENGING', 176, 12);
    ctx.fillText(`HITS: ${galagaGame.hitsCount}`, 176, 22);
  } else {
    ctx.fillText(`STAGE ${galagaGame.stage}`, 186, 12);
  }

  // Mini Ship Lives
  for (let l = 0; l < galagaGame.lives; l++) {
    const lx = 186 + l * 12;
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(lx, 26, 6, 6);
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(lx + 2, 25, 2, 2);
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

  // Captive Ship Docked to Boss Galaga
  if (galagaGame.capturedShip && galagaGame.capturedShip.boss) {
    const boss = galagaGame.capturedShip.boss;
    drawSingleFighter(boss.x + 16, boss.y - 2, '#eb2f06');
  }

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
  function drawSingleFighter(sx, sy, hullColor = '#ffffff') {
    ctx.save();
    ctx.translate(sx, sy);
    ctx.fillStyle = hullColor;
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

  // Draw Player or Capturing Fighter
  if (galagaGame.isCapturing) {
    ctx.save();
    ctx.translate(galagaGame.shipX, galagaGame.captureShipY);
    ctx.rotate(galagaGame.captureAngle);
    drawSingleFighter(0, 0, '#eb2f06');
    ctx.restore();
  } else {
    const shipY = 220;
    if (galagaGame.dualFighter) {
      ctx.fillStyle = '#718093';
      ctx.fillRect(galagaGame.shipX - 10, shipY + 2, 20, 2);
      drawSingleFighter(galagaGame.shipX - 8, shipY);
      drawSingleFighter(galagaGame.shipX + 8, shipY);
    } else {
      drawSingleFighter(galagaGame.shipX, shipY);
    }
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
'''

def build_frogger_asteroids_tempest_gyruss():
    return '''// -------------------------------------------------------------------------
// 3. FROGGER (1981 KONAMI DUAL Z80): FULLY PLAYABLE ARCADE ENGINE
// -------------------------------------------------------------------------
const froggerGame = {
  active: false,
  frog: {
    gridX: 7,
    gridY: 13,
    x: 112,
    y: 216,
    dir: 'up',
    hopTick: 0,
    hasLady: false
  },
  vehicles: [],
  logs: [],
  homeBays: [false, false, false, false, false],
  bayCrocodiles: [false, false, false, false, false],
  bayFlies: [false, false, false, false, false],
  score: 0,
  highScore: 12000,
  lives: 3,
  time: 60,
  tick: 0
};

function initFroggerGame() {
  froggerGame.active = true;
  froggerGame.frog.gridX = 7;
  froggerGame.frog.gridY = 13;
  froggerGame.frog.x = 112;
  froggerGame.frog.y = 216;
  froggerGame.frog.dir = 'up';
  froggerGame.frog.hopTick = 0;
  froggerGame.frog.hasLady = false;
  froggerGame.score = 0;
  froggerGame.lives = 3;
  froggerGame.time = 60;
  froggerGame.homeBays = [false, false, false, false, false];
  froggerGame.bayCrocodiles = [false, false, false, false, false];
  froggerGame.bayFlies = [false, false, false, false, false];
  froggerGame.tick = 0;
  spawnFroggerTraffic();
  spawnFroggerRiver();
  playArcadeSfx('FROG-H');
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
  // Row 1: Medium logs (moving right)
  for (let c = 0; c < 3; c++) froggerGame.logs.push({ x: c * 90, y: 102, w: 46, speed: 1.1, type: 'log', diving: false });
  // Row 2: Diving turtles (flotillas of 3, moving left)
  for (let c = 0; c < 4; c++) froggerGame.logs.push({ x: c * 65, y: 86, w: 34, speed: -1.3, type: 'turtle', diving: true, divePhase: c * 45 });
  // Row 3: Large logs and Crocodiles (moving right)
  for (let c = 0; c < 2; c++) froggerGame.logs.push({ x: c * 130, y: 70, w: 72, speed: 1.5, type: c === 0 ? 'crocodile' : 'log', diving: false });
  // Row 4: Small logs (moving right)
  for (let c = 0; c < 3; c++) froggerGame.logs.push({ x: c * 85, y: 54, w: 36, speed: 1.0, type: 'log', diving: false });
  // Row 5: Diving turtles (flotillas of 2, moving left)
  for (let c = 0; c < 4; c++) froggerGame.logs.push({ x: c * 70, y: 38, w: 28, speed: -1.6, type: 'turtle', diving: true, divePhase: c * 50 });
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

  // Random Crocodile in bay & Fly bonus update
  if (froggerGame.tick % 160 === 0) {
    const bay = Math.floor(Math.random() * 5);
    if (!froggerGame.homeBays[bay]) {
      froggerGame.bayCrocodiles[bay] = (Math.random() < 0.4);
      froggerGame.bayFlies[bay] = (!froggerGame.bayCrocodiles[bay] && Math.random() < 0.5);
    }
  }

  // Autonomous Tour AI
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

  // Vehicles update & squish collision
  froggerGame.vehicles.forEach(v => {
    v.x += v.speed;
    if (v.speed < 0 && v.x < -40) v.x = 240 + Math.random() * 20;
    else if (v.speed > 0 && v.x > 260) v.x = -40;

    if (Math.abs(v.y - fg.y) < 10 && Math.abs(v.x - fg.x) < (v.w / 2 + 4) && currentMode !== 'tour') {
      playArcadeSfx('FROG-SPLAT');
      fg.gridX = 7; fg.gridY = 13; fg.x = 112; fg.y = 216; fg.hasLady = false;
      froggerGame.lives--;
      if (froggerGame.lives <= 0) {
        froggerGame.lives = 3;
        froggerGame.score = 0;
        initFroggerGame();
      }
    }
  });

  // River logs, crocodiles & diving turtles
  let onRiverSupport = false;
  let submergedDrown = false;
  let crocodileSnap = false;

  froggerGame.logs.forEach(l => {
    l.x += l.speed;
    if (l.speed < 0 && l.x < -60) l.x = 240 + Math.random() * 20;
    else if (l.speed > 0 && l.x > 260) l.x = -60;

    if (l.diving) {
      l.divePhase = (l.divePhase + 1) % 180;
    }

    if (fg.gridY >= 2 && fg.gridY <= 6) {
      if (Math.abs(l.y - fg.y) < 8 && fg.x >= l.x - 4 && fg.x <= l.x + l.w + 4) {
        // If diving turtle is in submerged underwater phase (125..165), frog cannot stand on it!
        if (l.diving && l.divePhase >= 125 && l.divePhase <= 165) {
          submergedDrown = true;
        } else if (l.type === 'crocodile' && fg.x >= l.x + l.w - 16) {
          // If frog lands on crocodile mouth/snout, jaws snap!
          crocodileSnap = true;
        } else {
          onRiverSupport = true;
          fg.x += l.speed;
          fg.gridX = Math.round((fg.x - 8) / 16);
        }
      }
    }
  });

  // Drown in water or submerged turtle or crocodile bite
  if (fg.gridY >= 2 && fg.gridY <= 6 && (!onRiverSupport || submergedDrown || crocodileSnap) && currentMode !== 'tour') {
    if (crocodileSnap) playArcadeSfx('FROG-SPLAT');
    else playArcadeSfx('FROG-SPLASH');
    fg.gridX = 7; fg.gridY = 13; fg.x = 112; fg.y = 216; fg.hasLady = false;
    froggerGame.lives--;
    if (froggerGame.lives <= 0) {
      froggerGame.lives = 3;
      froggerGame.score = 0;
      initFroggerGame();
    }
  }

  // Home Bays Arrival
  if (fg.gridY === 1) {
    const bayIndex = Math.floor((fg.x - 10) / 48);
    if (bayIndex >= 0 && bayIndex < 5 && !froggerGame.homeBays[bayIndex]) {
      // Check if crocodile is in bay
      if (froggerGame.bayCrocodiles[bayIndex]) {
        // Eaten by crocodile in bay mouth
        playArcadeSfx('FROG-SPLAT');
        fg.gridX = 7; fg.gridY = 13; fg.x = 112; fg.y = 216; fg.hasLady = false;
        froggerGame.lives--;
        if (froggerGame.lives <= 0) {
          froggerGame.lives = 3;
          froggerGame.score = 0;
          initFroggerGame();
        }
      } else {
        froggerGame.homeBays[bayIndex] = true;
        let bonusPts = 500;
        if (froggerGame.bayFlies[bayIndex]) bonusPts += 200;
        if (fg.hasLady) bonusPts += 200;
        froggerGame.score += bonusPts;
        if (froggerGame.score > froggerGame.highScore) froggerGame.highScore = froggerGame.score;
        playArcadeSfx('FROG-HOME');
        fg.gridX = 7; fg.gridY = 13; fg.x = 112; fg.y = 216; fg.hasLady = false;

        // All 5 bays filled victory
        if (froggerGame.homeBays.every(b => b)) {
          froggerGame.score += 1000;
          if (froggerGame.score > froggerGame.highScore) froggerGame.highScore = froggerGame.score;
          playArcadeSfx('FROG-FANFARE');
          froggerGame.homeBays = [false, false, false, false, false];
          froggerGame.bayCrocodiles = [false, false, false, false, false];
          froggerGame.bayFlies = [false, false, false, false, false];
        }
      }
    } else {
      fg.gridX = 7; fg.gridY = 13; fg.x = 112; fg.y = 216; fg.hasLady = false;
      playArcadeSfx('FROG-SPLAT');
    }
  }
}

function renderFroggerGame() {
  if (!ctx) return;
  if (ctx.save) ctx.save();

  // Top Bank & Bays
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

    // Crocodile head in bay
    if (froggerGame.bayCrocodiles[idx]) {
      ctx.fillStyle = '#eb2f06';
      ctx.fillRect(bx - 4, 21, 8, 7);
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(bx - 3, 22, 2, 2); ctx.fillRect(bx + 1, 22, 2, 2);
    } else if (froggerGame.bayFlies[idx]) {
      // Fly bonus
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(bx - 2, 23, 4, 3);
      ctx.fillStyle = '#00d2d3';
      ctx.fillRect(bx - 1, 21, 2, 2);
    } else if (froggerGame.homeBays[idx]) {
      // Frog in home
      ctx.fillStyle = '#2ed573';
      ctx.fillRect(bx - 5, 20, 10, 8);
      ctx.fillStyle = '#ff4757';
      ctx.fillRect(bx - 3, 19, 2, 2); ctx.fillRect(bx + 1, 19, 2, 2);
    }
  });

  // River Blue Surface
  ctx.fillStyle = '#0652dd';
  ctx.fillRect(0, 34, 240, 82);

  // River Logs, Crocodiles, Diving Turtles
  froggerGame.logs.forEach(l => {
    if (l.type === 'turtle') {
      const isSubmerged = l.diving && l.divePhase >= 125 && l.divePhase <= 165;
      const isBubbling = l.diving && (l.divePhase >= 115 && l.divePhase <= 175);
      if (isSubmerged) {
        // Water ripples / bubbles
        ctx.fillStyle = 'rgba(255, 255, 255, 0.45)';
        ctx.fillRect(l.x + 4, l.y + 4, 3, 3);
        ctx.fillRect(l.x + 14, l.y + 2, 4, 4);
      } else {
        ctx.fillStyle = isBubbling ? '#1289a7' : '#009432';
        ctx.fillRect(l.x, l.y, l.w, 12);
        ctx.fillStyle = '#a3cb38';
        for (let t = 4; t < l.w; t += 10) {
          ctx.fillRect(l.x + t, l.y + 2, 6, 8);
        }
      }
    } else if (l.type === 'crocodile') {
      // Crocodile
      ctx.fillStyle = '#006266';
      ctx.fillRect(l.x, l.y + 1, l.w, 11);
      ctx.fillStyle = '#1b1464';
      ctx.fillRect(l.x + l.w - 14, l.y + 2, 12, 9); // Snout
      ctx.fillStyle = '#ff3838'; // Red eye
      ctx.fillRect(l.x + l.w - 10, l.y + 1, 3, 2);
      ctx.fillStyle = '#ffffff'; // White snapping teeth
      ctx.fillRect(l.x + l.w - 8, l.y + 5, 2, 2);
    } else {
      // Wood Log with bark
      ctx.fillStyle = '#795548';
      ctx.fillRect(l.x, l.y + 1, l.w, 11);
      ctx.fillStyle = '#5d4037';
      ctx.fillRect(l.x + 2, l.y + 2, l.w - 4, 9);
      ctx.fillStyle = '#8d6e63';
      ctx.fillRect(l.x + 6, l.y + 4, 8, 3);
      ctx.fillRect(l.x + 22, l.y + 3, 10, 3);
    }
  });

  // Middle Purple Sidewalk Strip
  ctx.fillStyle = '#4834d4';
  ctx.fillRect(0, 116, 240, 16);

  // Highway Asphalt
  ctx.fillStyle = '#130f40';
  ctx.fillRect(0, 132, 240, 82);

  // Road Lane Dashes
  ctx.fillStyle = 'rgba(255, 255, 255, 0.25)';
  for (let rw = 148; rw <= 196; rw += 16) {
    for (let d = 0; d < 240; d += 24) ctx.fillRect(d, rw, 12, 1);
  }

  // Vehicles
  froggerGame.vehicles.forEach(v => {
    ctx.fillStyle = v.color;
    ctx.fillRect(v.x, v.y - 2, v.w, 12);
    ctx.fillStyle = '#1e272e';
    ctx.fillRect(v.x + 2, v.y + 1, v.w - 4, 6);
    ctx.fillStyle = '#f1c40f';
    if (v.speed < 0) {
      ctx.fillRect(v.x + 1, v.y + 1, 2, 2);
      ctx.fillRect(v.x + 1, v.y + 5, 2, 2);
    } else {
      ctx.fillRect(v.x + v.w - 3, v.y + 1, 2, 2);
      ctx.fillRect(v.x + v.w - 3, v.y + 5, 2, 2);
    }
  });

  // Bottom Purple Starting Sidewalk
  ctx.fillStyle = '#4834d4';
  ctx.fillRect(0, 214, 240, 18);

  // Player Frog Sprite
  const fg = froggerGame.frog;
  ctx.save();
  ctx.translate(fg.x, fg.y);
  ctx.fillStyle = '#00ff66';
  ctx.fillRect(-5, -5, 10, 10);
  ctx.fillStyle = '#f5cd79';
  ctx.fillRect(-3, -3, 6, 6);
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(-4, -6, 3, 2); ctx.fillRect(1, -6, 3, 2);
  ctx.fillStyle = '#000000';
  ctx.fillRect(-3, -6, 1, 1); ctx.fillRect(2, -6, 1, 1);

  if (fg.hasLady) {
    ctx.fillStyle = '#ff3838'; // Pink/Red Lady Frog
    ctx.fillRect(-2, -2, 4, 4);
  }
  ctx.restore();

  // Header & HUD
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 8px monospace';
  ctx.fillText(`SCORE: ${froggerGame.score}`, 18, 12);
  ctx.fillStyle = '#f1c40f';
  ctx.fillText(`HI: ${froggerGame.highScore}`, 108, 12);
  ctx.fillStyle = '#00ff66';
  for (let l = 0; l < froggerGame.lives; l++) {
    ctx.fillText('🐸', 188 + l * 12, 12);
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
// 4. ASTEROIDS (1979 ATARI DVG VECTOR): FULLY PLAYABLE ARCADE ENGINE
// -------------------------------------------------------------------------
const asteroidsGame = {
  active: false,
  ship: { x: 120, y: 120, angle: -Math.PI / 2, vx: 0, vy: 0, thrust: false },
  rocks: [],
  bullets: [],
  saucerBullets: [],
  debris: [],
  saucer: { active: false, x: -20, y: 60, vx: 1.4, vy: 0, type: 'large', timer: 0 },
  score: 0,
  highScore: 30000,
  lives: 3,
  level: 1,
  tick: 0,
  heartbeatToggle: false
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
  asteroidsGame.saucerBullets = [];
  asteroidsGame.debris = [];
  asteroidsGame.saucer = { active: false, x: -20, y: 60, vx: 1.4, vy: 0, type: 'large', timer: 0 };
  asteroidsGame.score = 0;
  asteroidsGame.lives = 3;
  asteroidsGame.level = 1;
  asteroidsGame.tick = 0;
  asteroidsGame.heartbeatToggle = false;
  spawnAsteroidsField(4);
  playArcadeSfx('AST-FIRE');
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

  // Heartbeat dual-tone sound (accelerates as remaining asteroids decrease)
  const beatInterval = Math.max(14, Math.floor(asteroidsGame.rocks.length * 8 + 12));
  if (asteroidsGame.tick % beatInterval === 0) {
    asteroidsGame.heartbeatToggle = !asteroidsGame.heartbeatToggle;
    playArcadeSfx(asteroidsGame.heartbeatToggle ? 'AST-THUMP-LO' : 'AST-THUMP-HI');
  }

  // Autonomous Tour AI
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
    if (arcadeKeysDown['a'] || arcadeKeysDown['arrowleft'] || (typeof dpadActiveDir !== 'undefined' && dpadActiveDir === 'left')) s.angle -= 0.08;
    if (arcadeKeysDown['d'] || arcadeKeysDown['arrowright'] || (typeof dpadActiveDir !== 'undefined' && dpadActiveDir === 'right')) s.angle += 0.08;
    s.thrust = !!(arcadeKeysDown['w'] || arcadeKeysDown['arrowup'] || (typeof dpadActiveDir !== 'undefined' && dpadActiveDir === 'up'));
  }

  if (s.thrust) {
    s.vx += Math.cos(s.angle) * 0.14;
    s.vy += Math.sin(s.angle) * 0.14;
    if (asteroidsGame.tick % 10 === 0) playArcadeSfx('AST-THR');
  }
  s.vx *= 0.985;
  s.vy *= 0.985;
  s.x += s.vx;
  s.y += s.vy;

  if (s.x < 0) s.x += 240; else if (s.x > 240) s.x -= 240;
  if (s.y < 0) s.y += 240; else if (s.y > 240) s.y -= 240;

  // Bullets vs Rocks & Saucer
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

    // Bullet vs Saucer
    if (asteroidsGame.saucer.active) {
      const sc = asteroidsGame.saucer;
      if (Math.hypot(bl.x - sc.x, bl.y - sc.y) < (sc.type === 'large' ? 12 : 8)) {
        asteroidsGame.bullets.splice(b, 1);
        playArcadeSfx('AST-EXP');
        const pts = (sc.type === 'large') ? 200 : 1000;
        asteroidsGame.score += pts;
        if (asteroidsGame.score > asteroidsGame.highScore) asteroidsGame.highScore = asteroidsGame.score;
        sc.active = false;
        continue;
      }
    }

    // Bullet vs Rocks
    for (let r = asteroidsGame.rocks.length - 1; r >= 0; r--) {
      const rk = asteroidsGame.rocks[r];
      const dist = Math.hypot(bl.x - rk.x, bl.y - rk.y);
      if (dist < rk.radius) {
        asteroidsGame.bullets.splice(b, 1);
        playArcadeSfx('AST-EXP');
        const pts = (rk.size === 3) ? 20 : ((rk.size === 2) ? 50 : 100);
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
              radius: (rk.size === 3) ? 10 : 5,
              size: rk.size - 1
            });
          }
        }
        asteroidsGame.rocks.splice(r, 1);
        break;
      }
    }
  }

  // Debris
  for (let d = asteroidsGame.debris.length - 1; d >= 0; d--) {
    const db = asteroidsGame.debris[d];
    db.x += db.vx;
    db.y += db.vy;
    db.angle += db.vRot;
    db.life--;
    if (db.life <= 0) asteroidsGame.debris.splice(d, 1);
  }

  // Alien Saucer UFO (Large 200 PTS / Small 1000 PTS)
  if (!asteroidsGame.saucer.active && asteroidsGame.tick % 450 === 0) {
    const isSmall = (asteroidsGame.score > 10000 || Math.random() < 0.35);
    asteroidsGame.saucer = {
      active: true,
      x: 0,
      y: Math.random() * 160 + 30,
      vx: isSmall ? 1.8 : 1.2,
      vy: Math.sin(asteroidsGame.tick * 0.05) * 0.5,
      type: isSmall ? 'small' : 'large',
      timer: 0
    };
    playArcadeSfx('AST-SAU');
  }

  if (asteroidsGame.saucer.active) {
    const sc = asteroidsGame.saucer;
    sc.x += sc.vx;
    sc.y += sc.vy;
    sc.timer++;
    if (sc.timer % 65 === 0) {
      // Small saucer fires target-leading sniper torpedo!
      let fireAngle = Math.random() * Math.PI * 2;
      if (sc.type === 'small') {
        fireAngle = Math.atan2(s.y - sc.y, s.x - sc.x) + (Math.random() - 0.5) * 0.2;
      }
      asteroidsGame.saucerBullets.push({
        x: sc.x,
        y: sc.y,
        vx: Math.cos(fireAngle) * 3.5,
        vy: Math.sin(fireAngle) * 3.5,
        life: 55
      });
      playArcadeSfx('AST-FIRE');
    }
    if (sc.x > 240) sc.active = false;
  }

  // Saucer Bullets
  for (let sb = asteroidsGame.saucerBullets.length - 1; sb >= 0; sb--) {
    const sbl = asteroidsGame.saucerBullets[sb];
    sbl.x += sbl.vx;
    sbl.y += sbl.vy;
    sbl.life--;
    if (sbl.life <= 0) {
      asteroidsGame.saucerBullets.splice(sb, 1);
      continue;
    }
    // Saucer bullet vs ship
    if (Math.hypot(sbl.x - s.x, sbl.y - s.y) < 8 && currentMode !== 'tour') {
      asteroidsGame.saucerBullets.splice(sb, 1);
      playArcadeSfx('AST-EXP');
      asteroidsGame.lives--;
      s.x = 120; s.y = 120; s.vx = 0; s.vy = 0;
      if (asteroidsGame.lives <= 0) {
        asteroidsGame.lives = 3;
        asteroidsGame.score = 0;
        initAsteroidsGame();
      }
    }
  }

  // Rocks Collision with Ship
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

  // Vector CRT Phosphor Glow
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = 1.4;
  ctx.shadowColor = '#00ffcc';
  ctx.shadowBlur = 6;

  ctx.fillStyle = '#ffffff';
  asteroidsGame.bullets.forEach(bl => {
    ctx.fillRect(bl.x - 1, bl.y - 1, 2, 2);
  });

  ctx.fillStyle = '#ff4757';
  asteroidsGame.saucerBullets.forEach(sbl => {
    ctx.fillRect(sbl.x - 1, sbl.y - 1, 2, 2);
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

  // Alien Saucer UFO (Large / Small)
  if (asteroidsGame.saucer.active) {
    const sc = asteroidsGame.saucer;
    const sr = (sc.type === 'large') ? 10 : 6;
    ctx.save();
    ctx.translate(sc.x, sc.y);
    ctx.beginPath();
    ctx.moveTo(-sr * 1.5, 0);
    ctx.lineTo(sr * 1.5, 0);
    ctx.lineTo(sr * 0.8, -sr * 0.6);
    ctx.lineTo(-sr * 0.8, -sr * 0.6);
    ctx.closePath();
    ctx.moveTo(-sr * 0.8, -sr * 0.6);
    ctx.lineTo(-sr * 0.4, -sr * 1.1);
    ctx.lineTo(sr * 0.4, -sr * 1.1);
    ctx.lineTo(sr * 0.8, -sr * 0.6);
    ctx.moveTo(-sr * 1.5, 0);
    ctx.lineTo(-sr * 0.7, sr * 0.5);
    ctx.lineTo(sr * 0.7, sr * 0.5);
    ctx.lineTo(sr * 1.5, 0);
    ctx.stroke();
    ctx.restore();
  }

  // Player Vector Ship
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
  spikerTrails: [],
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
  tempestGame.spikerTrails = [];
  tempestGame.score = 0;
  tempestGame.lives = 3;
  tempestGame.superzapperUsed = false;
  tempestGame.superzapperFlash = 0;
  tempestGame.tube = 9;
  tempestGame.tick = 0;
  spawnTempestEnemies();
  playArcadeSfx('TEM-FIRE');
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
    tempestGame.superzapperFlash = 25;
    tempestGame.enemies.forEach(en => {
      tempestGame.score += 150;
    });
    tempestGame.enemies = [];
    playArcadeSfx('TEM-ZAP');
  }
}

function updateTempestGame() {
  tempestGame.tick++;

  // Autonomous Tour AI
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

  // Shots vs Enemies
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

  // Enemies crawl up tube, somersault between channels
  tempestGame.enemies.forEach(en => {
    en.dist += en.vDist;
    if (en.type === 'flipper' && tempestGame.tick % 45 === 0) {
      en.seg = (en.seg + (Math.random() < 0.5 ? 1 : 15)) % 16;
      playArcadeSfx('TEM-FLIP');
    } else if (en.type === 'spiker' && tempestGame.tick % 60 === 0) {
      playArcadeSfx('TEM-SPIKE');
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

  // Superzapper Full Tube Flash
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

  // Perspective 3D Vector Tube
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

  // Enemies (Flippers & Spikers)
  tempestGame.enemies.forEach(en => {
    const a = (en.seg + 0.5) / numSegs * Math.PI * 2;
    const r = rFar + (rNear - rFar) * en.dist;
    const ex = cx + Math.cos(a) * r;
    const ey = cy + Math.sin(a) * (r * 0.6);
    const scale = 0.8 + en.dist * 0.8;

    ctx.save();
    ctx.translate(ex, ey);
    if (en.type === 'flipper') {
      ctx.strokeStyle = '#eb2f06';
      ctx.beginPath();
      ctx.moveTo(-5 * scale, -5 * scale);
      ctx.lineTo(5 * scale, 5 * scale);
      ctx.lineTo(0, -6 * scale);
      ctx.closePath();
      ctx.stroke();
    } else {
      ctx.strokeStyle = '#2ed573';
      ctx.beginPath();
      ctx.arc(0, 0, 4 * scale, 0, Math.PI * 2);
      ctx.stroke();
    }
    ctx.restore();
  });

  // Particle Shots
  ctx.strokeStyle = '#f1c40f';
  ctx.lineWidth = 2.0;
  tempestGame.shots.forEach(sh => {
    const a = (sh.seg + 0.5) / numSegs * Math.PI * 2;
    const r = rFar + (rNear - rFar) * sh.dist;
    const sx = cx + Math.cos(a) * r;
    const sy = cy + Math.sin(a) * (r * 0.6);
    ctx.beginPath();
    ctx.moveTo(sx - 2, sy); ctx.lineTo(sx + 2, sy);
    ctx.stroke();
  });

  // Player Claw / Blaster on Rim
  const playerA = (tempestGame.segment + 0.5) / numSegs * Math.PI * 2;
  const px = cx + Math.cos(playerA) * rNear;
  const py = cy + Math.sin(playerA) * (rNear * 0.6);
  ctx.save();
  ctx.translate(px, py);
  ctx.rotate(playerA + Math.PI / 2);
  ctx.strokeStyle = '#f1c40f';
  ctx.lineWidth = 2.0;
  ctx.beginPath();
  ctx.moveTo(-7, -4);
  ctx.lineTo(0, 6);
  ctx.lineTo(7, -4);
  ctx.stroke();
  ctx.fillStyle = '#eb2f06';
  ctx.fillRect(-2, 2, 4, 3);
  ctx.restore();

  ctx.shadowBlur = 0;

  // Header & HUD
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 8px monospace';
  ctx.fillText(`SCORE: ${tempestGame.score}`, 18, 16);
  ctx.fillText(`TUBE ${tempestGame.tube}`, 108, 16);
  for (let l = 0; l < tempestGame.lives; l++) {
    ctx.fillText('⚡', 190 + l * 10, 16);
  }

  if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
  if (ctx.restore) ctx.restore();
}

function renderTempestTour(f) {
  if (!tempestGame.active) initTempestGame();
  updateTempestGame();
  renderTempestGame();
}

// -------------------------------------------------------------------------
// 6. GYRUSS (1983 KONAMI 5x PSG BAROQUE): FULLY PLAYABLE ARCADE ENGINE
// -------------------------------------------------------------------------
const gyrussGame = {
  active: false,
  angle: -Math.PI / 2,
  bankAngle: 0,
  shots: [],
  enemies: [],
  stars: [],
  score: 0,
  highScore: 35000,
  lives: 3,
  warp: 3,
  destPlanet: 'NEPTUNE',
  tick: 0
};

function initGyrussGame() {
  gyrussGame.active = true;
  gyrussGame.angle = -Math.PI / 2;
  gyrussGame.bankAngle = 0;
  gyrussGame.shots = [];
  gyrussGame.enemies = [];
  gyrussGame.stars = [];
  gyrussGame.score = 0;
  gyrussGame.lives = 3;
  gyrussGame.warp = 3;
  gyrussGame.destPlanet = 'NEPTUNE';
  gyrussGame.tick = 0;

  for (let i = 0; i < 48; i++) {
    gyrussGame.stars.push({
      angle: Math.random() * Math.PI * 2,
      dist: Math.random() * 110 + 6,
      speed: 1.2 + Math.random() * 2.2
    });
  }

  playArcadeSfx('GYRUSS-TUNE');
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

  // Starfield zoom
  g.stars.forEach(st => {
    st.dist += st.speed;
    if (st.dist > 115) {
      st.dist = 6;
      st.angle = Math.random() * Math.PI * 2;
    }
  });

  // Tour AI or Playable input
  if (currentMode === 'tour') {
    gyrussGame.angle += 0.055;
    gyrussGame.bankAngle = 0.25;
    if (gyrussGame.tick % 12 === 0) gyrussFire();
  } else {
    let rotating = false;
    if (arcadeKeysDown['a'] || arcadeKeysDown['arrowleft'] || (typeof dpadActiveDir !== 'undefined' && dpadActiveDir === 'left')) {
      gyrussGame.angle -= 0.07;
      gyrussGame.bankAngle = -0.35;
      rotating = true;
    }
    if (arcadeKeysDown['d'] || arcadeKeysDown['arrowright'] || (typeof dpadActiveDir !== 'undefined' && dpadActiveDir === 'right')) {
      gyrussGame.angle += 0.07;
      gyrussGame.bankAngle = 0.35;
      rotating = true;
    }
    if (!rotating) gyrussGame.bankAngle *= 0.8;
  }

  // Shots update
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
        if (g.score > g.highScore) g.highScore = g.score;
        playArcadeSfx('GYRUSS-EXP');
        break;
      }
    }
  }

  // Spiral entrance waves
  if (g.tick % 40 === 0) {
    g.enemies.push({
      angle: Math.random() * Math.PI * 2,
      dist: 10,
      vDist: 1.4,
      vAngle: (Math.random() - 0.5) * 0.05
    });
  }

  // Enemy movement & player collision
  for (let e = g.enemies.length - 1; e >= 0; e--) {
    const en = g.enemies[e];
    en.dist += en.vDist;
    en.angle += en.vAngle;

    if (en.dist >= 92 && en.dist <= 104 && currentMode !== 'tour') {
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

  if (g.tick % 600 === 0 && g.warp > 0) {
    g.warp--;
    playArcadeSfx('GYRUSS-WARP');
  }
}

function renderGyrussGame() {
  if (!ctx) return;
  if (ctx.save) ctx.save();

  ctx.fillStyle = '#05070a';
  ctx.fillRect(0, 0, 240, 240);

  const cx = 120, cy = 125;

  // Radial 3D Starfield
  ctx.fillStyle = '#ffffff';
  gyrussGame.stars.forEach(st => {
    const sx = cx + Math.cos(st.angle) * st.dist;
    const sy = cy + Math.sin(st.angle) * st.dist;
    const sz = (st.dist / 110) * 1.8;
    ctx.fillRect(sx, sy, sz, sz);
  });

  // Concentric Polar Warp Rings
  for (let r = 24; r <= 100; r += 24) {
    ctx.strokeStyle = `rgba(0, 229, 255, ${0.15 + (r / 100) * 0.35})`;
    ctx.lineWidth = 1.0;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();
  }

  // Lasers
  ctx.fillStyle = '#f1c40f';
  gyrussGame.shots.forEach(sh => {
    const lx = cx + Math.cos(sh.angle) * sh.dist;
    const ly = cy + Math.sin(sh.angle) * sh.dist;
    ctx.fillRect(lx - 1, ly - 1, 3, 3);
  });

  // Enemies
  gyrussGame.enemies.forEach(en => {
    const ex = cx + Math.cos(en.angle) * en.dist;
    const ey = cy + Math.sin(en.angle) * en.dist;
    const scale = 0.5 + (en.dist / 100) * 0.8;
    ctx.save();
    ctx.translate(ex, ey);
    ctx.rotate(en.angle + Math.PI / 2);
    ctx.fillStyle = '#eb2f06';
    ctx.fillRect(-6 * scale, -4 * scale, 12 * scale, 8 * scale);
    ctx.fillStyle = '#00e5ff';
    ctx.fillRect(-8 * scale, -2 * scale, 16 * scale, 4 * scale);
    ctx.restore();
  });

  // 360° Banked Player Starfighter
  const shipA = gyrussGame.angle;
  const shipDist = 96;
  const sx = cx + Math.cos(shipA) * shipDist;
  const sy = cy + Math.sin(shipA) * shipDist;
  ctx.save();
  ctx.translate(sx, sy);
  ctx.rotate(shipA + Math.PI / 2 + gyrussGame.bankAngle);
  ctx.fillStyle = '#0652dd';
  ctx.fillRect(-6, -4, 12, 8);
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(-2, -7, 4, 6);
  ctx.fillStyle = '#ff3838';
  ctx.fillRect(-8, 0, 3, 5); ctx.fillRect(5, 0, 3, 5);
  ctx.fillStyle = '#f1c40f';
  ctx.fillRect(-4, 3, 8, 2);
  ctx.restore();

  // Header & HUD
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 8px monospace';
  ctx.fillText(`SCORE: ${gyrussGame.score}`, 18, 16);
  ctx.fillStyle = '#f1c40f';
  ctx.fillText(`WARP ${gyrussGame.warp} TO ${gyrussGame.destPlanet}`, 80, 16);
  ctx.fillStyle = '#00e5ff';
  for (let l = 0; l < gyrussGame.lives; l++) {
    ctx.fillText('🚀', 190 + l * 10, 16);
  }

  if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
  if (ctx.restore) ctx.restore();
}

function renderGyrussTour(f) {
  if (!gyrussGame.active) initGyrussGame();
  updateGyrussGame();
  renderGyrussGame();
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
  const g = tourState.games[tourState.gameIdx];
  switchActiveGame(g.id);
  setMode('tour');
}

function prevTourGame() {
  initAudio();
  if (typeof stopCurrentGame === 'function') stopCurrentGame();
  tourState.frameInGame = 0;
  tourState.gameIdx = (tourState.gameIdx - 1 + tourState.games.length) % tourState.games.length;
  const g = tourState.games[tourState.gameIdx];
  switchActiveGame(g.id);
  setMode('tour');
}

function launchCurrentTourGame() {
  initAudio();
  const g = tourState.games[tourState.gameIdx];
  switchActiveGame(g.id);
  setMode('arcade');
}

function renderTourDemo() {
  if (!tourState.active) return;
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
'''

def main():
    target_file = "tools/build_hardware_template.py"
    with open(target_file, "r") as f:
        code = f.read()

    # 1. Replace Part A: Crazy Climber and Galaga (from idx_cc to idx_dk)
    idx_cc_header = code.find("// 0. CRAZY CLIMBER (1980 NICHIBUTSU Z80): FULLY PLAYABLE ARCADE ENGINE")
    idx_dk_header = code.find("// 2. DONKEY KONG 1981 NINTENDO 25M: HIGH-FIDELITY PLAYABLE ARCADE ENGINE")

    if idx_cc_header == -1 or idx_dk_header == -1:
        raise ValueError(f"Could not find Crazy Climber or Donkey Kong headers! idx_cc={idx_cc_header}, idx_dk={idx_dk_header}")

    # Back up to the comment banner
    idx_banner = code.rfind("// =========================================================================", 0, idx_cc_header)
    if idx_banner == -1:
        idx_banner = idx_cc_header

    part_a = build_crazy_climber_and_galaga()
    code = code[:idx_banner] + part_a + "\n" + code[idx_dk_header:]

    # 2. Replace Part B: Frogger, Asteroids, Tempest, Gyruss (from Frogger to Tour HUD)
    idx_frog_header = code.find("// -------------------------------------------------------------------------\n// 3. FROGGER (1981 KONAMI DUAL Z80): FULLY PLAYABLE ARCADE ENGINE")
    if idx_frog_header == -1:
        idx_frog_header = code.find("function initFroggerGame()")
        idx_frog_header = code.rfind("// -------------------------------------------------------------------------", 0, idx_frog_header)

    idx_tour_hud = code.find("function renderTourHud(game, f)")
    if idx_frog_header == -1 or idx_tour_hud == -1:
        raise ValueError(f"Could not find Frogger or Tour HUD headers! idx_frog={idx_frog_header}, idx_tour={idx_tour_hud}")

    part_b = build_frogger_asteroids_tempest_gyruss()
    code = code[:idx_frog_header] + part_b + "\n" + code[idx_tour_hud:]

    # Write back
    with open(target_file, "w") as f:
        f.write(code)

    print(f"Successfully updated {target_file} with authentic arcade specs across all engines!")

if __name__ == "__main__":
    main()
