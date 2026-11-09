import re

def get_upgraded_engines_code():
    return """
// =========================================================================
// 8 AUTHENTIC PLAYABLE ARCADE ENGINES (High-Resolution CRT Graphics & Physics)
// Pac-Man, Crazy Climber, Galaga, Donkey Kong, Frogger, Asteroids, Tempest, Gyruss
// Integrated Autonomous Attract AI & High-Density Arcade Pixel Art / Vector CRT
// =========================================================================

// -------------------------------------------------------------------------
// 1. GALAGA (1981 NAMCO DUAL Z80): FULLY PLAYABLE ARCADE ENGINE
// -------------------------------------------------------------------------
const galagaGame = {
  active: false,
  shipX: 120,
  shipSpeed: 2.6,
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
  tractorActive: false,
  tractorBeam: { active: false, x: 120, y: 60, height: 0, radius: 2 }
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
  galagaGame.tractorBeam = { active: false, x: 120, y: 60, height: 0, radius: 2 };
  spawnGalagaFleet();
}

function spawnGalagaFleet() {
  galagaGame.aliens = [];
  const alienTypes = ['boss', 'red', 'yellow'];
  for (let r = 0; r < 3; r++) {
    const type = alienTypes[r];
    for (let c = 0; c < 8; c++) {
      galagaGame.aliens.push({
        x: 44 + c * 22,
        y: 42 + r * 18,
        homeX: 44 + c * 22,
        homeY: 42 + r * 18,
        type: type,
        state: 'grid', // 'grid', 'dive', 'return'
        diveTick: 0,
        hp: type === 'boss' ? 2 : 1,
        angle: 0
      });
    }
  }
}

function galagaFire() {
  initAudio();
  if (galagaGame.lasers.length < 4) {
    if (galagaGame.dualFighter) {
      galagaGame.lasers.push({ x: galagaGame.shipX - 8, y: 214, vy: -5.8 });
      galagaGame.lasers.push({ x: galagaGame.shipX + 8, y: 214, vy: -5.8 });
    } else {
      galagaGame.lasers.push({ x: galagaGame.shipX, y: 214, vy: -5.8 });
    }
    playArcadeSfx('TRACT');
  }
}

function updateGalagaGame() {
  galagaGame.tick++;
  const g = galagaGame;

  // Autonomous Attract Tour AI
  if (currentMode === 'tour') {
    let targetX = 120 + Math.sin(g.tick * 0.04) * 55;
    const diving = g.aliens.find(a => a.state === 'dive');
    if (diving) targetX = diving.x;
    if (g.shipX < targetX - 3) g.shipX += 2.2;
    else if (g.shipX > targetX + 3) g.shipX -= 2.2;
    if (g.tick % 20 === 0) galagaFire();
  } else {
    // Player manual steering
    g.shipX += g.moveDir * g.shipSpeed;
  }
  g.shipX = Math.max(16, Math.min(224, g.shipX));

  // Move lasers
  for (let i = g.lasers.length - 1; i >= 0; i--) {
    const l = g.lasers[i];
    l.y += l.vy;
    if (l.y < 12) {
      g.lasers.splice(i, 1);
      continue;
    }
    // Check hit alien
    for (let a = g.aliens.length - 1; a >= 0; a--) {
      const al = g.aliens[a];
      if (Math.abs(l.x - al.x) < 11 && Math.abs(l.y - al.y) < 11) {
        al.hp--;
        g.lasers.splice(i, 1);
        if (al.hp <= 0) {
          const pts = al.state === 'dive' ? (al.type === 'boss' ? 400 : 200) : (al.type === 'boss' ? 200 : 100);
          g.score += pts;
          if (g.score > g.highScore) g.highScore = g.score;
          g.scorePops.push({ x: al.x, y: al.y, text: String(pts), timer: 30 });
          g.explosions.push({ x: al.x, y: al.y, frame: 0 });
          playArcadeSfx('AST-EXP');
          if (pts >= 300) playArcadeSfx('BONUS');
          g.aliens.splice(a, 1);
        } else {
          al.damaged = true;
          playArcadeSfx('TRACT');
        }
        break;
      }
    }
  }

  // Update aliens (Grid sway and dive bombing)
  const sway = Math.sin(g.tick * 0.05) * 8;
  g.aliens.forEach(al => {
    if (al.state === 'grid') {
      al.x = al.homeX + sway;
      al.y = al.homeY + Math.sin(g.tick * 0.08 + al.homeX) * 2;
      // Chance to initiate dive
      if (Math.random() < 0.003 && g.aliens.filter(a => a.state === 'dive').length < 2) {
        al.state = 'dive';
        al.diveTick = 0;
        playArcadeSfx('DIVE');
      }
    } else if (al.state === 'dive') {
      al.diveTick++;
      al.y += 2.2;
      al.x += Math.sin(al.diveTick * 0.12) * 2.8;
      al.angle = Math.sin(al.diveTick * 0.1) * 0.5;
      // Drop bomb towards player
      if (al.diveTick === 25 && g.bombs.length < 3) {
        g.bombs.push({ x: al.x, y: al.y + 6, vy: 2.6 });
      }
      if (al.y > 230) {
        al.state = 'return';
        al.y = 10;
        al.x = al.homeX;
      }
    } else if (al.state === 'return') {
      al.y += 1.8;
      if (al.y >= al.homeY) {
        al.state = 'grid';
        al.y = al.homeY;
      }
    }
  });

  // Respawn fleet if cleared
  if (g.aliens.length === 0) {
    g.stage++;
    playArcadeSfx('WARP');
    spawnGalagaFleet();
  }

  // Move bombs
  for (let b = g.bombs.length - 1; b >= 0; b--) {
    const bm = g.bombs[b];
    bm.y += bm.vy;
    if (bm.y > 240) {
      g.bombs.splice(b, 1);
      continue;
    }
    // Check hit ship
    if (Math.abs(bm.x - g.shipX) < 10 && Math.abs(bm.y - 220) < 10) {
      g.bombs.splice(b, 1);
      g.explosions.push({ x: g.shipX, y: 220, frame: 0 });
      playArcadeSfx('DEATH');
      if (currentMode !== 'tour') {
        g.lives--;
        if (g.lives <= 0) {
          g.lives = 3;
          g.score = 0;
          initGalagaGame();
        }
      }
    }
  }

  // Update explosions
  for (let e = g.explosions.length - 1; e >= 0; e--) {
    g.explosions[e].frame++;
    if (g.explosions[e].frame > 16) g.explosions.splice(e, 1);
  }

  // Update score pops
  for (let s = g.scorePops.length - 1; s >= 0; s--) {
    g.scorePops[s].timer--;
    if (g.scorePops[s].timer <= 0) g.scorePops.splice(s, 1);
  }
}

function renderGalagaGame() {
  if (!ctx) return;
  if (ctx.save) ctx.save();

  // Space Canvas Black
  ctx.fillStyle = '#05070a';
  ctx.fillRect(0, 0, 240, 240);

  // 3-Layer Parallax Starfield with Multi-Colored Stars
  const tick = galagaGame.tick;
  for (let st = 0; st < 36; st++) {
    // Layer 1: Slow dim blue stars
    const y1 = (st * 17 + tick * 0.4) % 240;
    const x1 = (st * 43) % 240;
    ctx.fillStyle = '#4b7bec';
    ctx.fillRect(x1, y1, 1, 1);

    // Layer 2: Medium amber stars
    const y2 = (st * 23 + tick * 1.1) % 240;
    const x2 = (st * 71 + 12) % 240;
    ctx.fillStyle = (st % 3 === 0) ? '#feca57' : '#ff4757';
    ctx.fillRect(x2, y2, 1, 1);

    // Layer 3: Fast sparkling white stars
    if (st % 2 === 0) {
      const y3 = (st * 31 + tick * 2.2) % 240;
      const x3 = (st * 97 + 34) % 240;
      ctx.fillStyle = (tick + st) % 12 < 6 ? '#ffffff' : '#a4b0be';
      ctx.fillRect(x3, y3, 2, 2);
    }
  }

  // Header Scores
  ctx.fillStyle = '#ff4757';
  ctx.font = 'bold 8px monospace';
  ctx.fillText('1UP', 22, 12);
  ctx.fillStyle = '#ffffff';
  ctx.fillText(String(galagaGame.score).padStart(6, '0'), 18, 22);

  ctx.fillStyle = '#00e5ff';
  ctx.fillText('HIGH SCORE', 92, 12);
  ctx.fillStyle = '#ffffff';
  ctx.fillText(String(galagaGame.highScore).padStart(6, '0'), 102, 22);

  ctx.fillStyle = '#fffa65';
  ctx.fillText(`STAGE ${galagaGame.stage}`, 186, 12);

  // Mini Ship Lives
  for (let l = 0; l < galagaGame.lives; l++) {
    const lx = 186 + l * 12;
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(lx, 18, 6, 6);
    ctx.fillStyle = '#ff4757';
    ctx.fillRect(lx + 2, 17, 2, 2);
  }

  // Dual Lasers
  galagaGame.lasers.forEach(l => {
    ctx.fillStyle = '#fffa65';
    ctx.fillRect(l.x - 1, l.y, 2, 7);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(l.x, l.y + 1, 1, 5);
  });

  // Enemy Bombs (pulsing torpedoes)
  galagaGame.bombs.forEach(b => {
    ctx.fillStyle = '#ff4757';
    ctx.fillRect(b.x - 1, b.y, 3, 5);
    ctx.fillStyle = '#fffa65';
    ctx.fillRect(b.x, b.y + 1, 1, 3);
  });

  // Aliens: Boss Galaga, Red Goei, Yellow Zako
  const flap = (tick >> 3) % 2;
  galagaGame.aliens.forEach(al => {
    ctx.save();
    ctx.translate(al.x, al.y);
    if (al.angle) ctx.rotate(al.angle);

    if (al.type === 'boss') {
      // Boss Galaga (Green / Cyan with flapping outer horns)
      ctx.fillStyle = al.hp === 2 ? '#10ac84' : '#0984e3'; // Turns blue on damage!
      ctx.fillRect(-6, -4, 12, 8);
      ctx.fillStyle = '#00e5ff';
      ctx.fillRect(-4, -6, 8, 3);
      // Yellow Horns (animated flap)
      ctx.fillStyle = '#fffa65';
      if (flap) {
        ctx.fillRect(-8, -8, 2, 4);
        ctx.fillRect(6, -8, 2, 4);
      } else {
        ctx.fillRect(-7, -7, 2, 4);
        ctx.fillRect(5, -7, 2, 4);
      }
      // Red Compound Eyes
      ctx.fillStyle = '#ff4757';
      ctx.fillRect(-3, -2, 2, 2);
      ctx.fillRect(1, -2, 2, 2);
    } else if (al.type === 'red') {
      // Red Goei (Red & Yellow Beetle)
      ctx.fillStyle = '#ee5253';
      ctx.fillRect(-5, -4, 10, 8);
      ctx.fillStyle = '#feca57';
      ctx.fillRect(-3, -5, 6, 2);
      // Pincer Wings (flapping)
      if (flap) {
        ctx.fillRect(-7, -2, 2, 4);
        ctx.fillRect(5, -2, 2, 4);
      } else {
        ctx.fillRect(-6, -1, 2, 4);
        ctx.fillRect(4, -1, 2, 4);
      }
    } else {
      // Yellow Zako (Yellow & Blue Butterfly)
      ctx.fillStyle = '#feca57';
      ctx.fillRect(-4, -3, 8, 6);
      ctx.fillStyle = '#0984e3';
      ctx.fillRect(-2, -4, 4, 2);
      // Fluttering Wings
      if (flap) {
        ctx.fillRect(-6, -3, 2, 5);
        ctx.fillRect(4, -3, 2, 5);
      } else {
        ctx.fillRect(-7, -2, 2, 4);
        ctx.fillRect(5, -2, 2, 4);
      }
    }
    ctx.restore();
  });

  // Explosions (Expanding retro particle ring)
  galagaGame.explosions.forEach(ex => {
    const r = ex.frame * 1.5;
    ctx.strokeStyle = ex.frame % 2 === 0 ? '#fffa65' : '#ff4757';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(ex.x, ex.y, r, 0, Math.PI * 2);
    ctx.stroke();
    for (let p = 0; p < 6; p++) {
      const pa = (p / 6) * Math.PI * 2;
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(ex.x + Math.cos(pa) * r * 1.2, ex.y + Math.sin(pa) * r * 1.2, 2, 2);
    }
  });

  // Player Fighter Ship (Authentic 1981 Namco Pixel Art)
  const shipX = galagaGame.shipX;
  const shipY = 220;
  ctx.save();
  ctx.translate(shipX, shipY);
  // White Fuselage
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(-6, -2, 12, 8);
  ctx.fillRect(-2, -8, 4, 7); // Nose cone
  ctx.fillRect(-1, -10, 2, 3); // Tip
  // Red Wing Accents & Twin Laser Cannons
  ctx.fillStyle = '#ee5253';
  ctx.fillRect(-8, -4, 2, 8);
  ctx.fillRect(6, -4, 2, 8);
  ctx.fillRect(-4, 0, 8, 2);
  // Cyan Cockpit
  ctx.fillStyle = '#00d2d3';
  ctx.fillRect(-2, -3, 4, 3);
  // Yellow Wingtip Highlights
  ctx.fillStyle = '#fffa65';
  ctx.fillRect(-8, -6, 2, 2);
  ctx.fillRect(6, -6, 2, 2);
  ctx.restore();

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

// =========================================================================
// 2. DONKEY KONG 1981 NINTENDO 25M: FULLY PLAYABLE ARCADE ENGINE
// High-Resolution CRT Pixel Art, Authentic Sloped Girders & Physics
// =========================================================================
const dkongGame = {
  active: false,
  mario: {
    x: 42,
    y: 202,
    vx: 0,
    vy: 0,
    w: 12,
    h: 16,
    facing: 'right',
    state: 'stand', // 'stand', 'run', 'jump', 'climb', 'hammer', 'dead', 'win'
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
  dk: {
    frame: 0,
    action: 'idle',
    actionTimer: 0
  },
  pauline: {
    frame: 0
  },
  barrels: [],
  scorePops: [],
  hammer: {
    x: 32,
    y: 104,
    available: true
  }
};

function getGirderY(x, tier) {
  if (tier === 0) { // Bottom
    if (x <= 80) return 218;
    return 218 - ((x - 80) / 142) * 4;
  } else if (tier === 1) { // Tier 2 (slopes down left to right)
    return 156 + ((x - 18) / 200) * 10;
  } else if (tier === 2) { // Tier 3 (slopes down right to left)
    return 118 - ((x - 24) / 198) * 10;
  } else if (tier === 3) { // Tier 4 (slopes down left to right)
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
  { id: 6, x: 106, top: 38,  bottom: 66,  fromTier: 3, toTier: 4, broken: false } // To Pauline
];

function initDonkeyKongGame() {
  dkongGame.active = true;
  dkongGame.mario.x = 42;
  dkongGame.mario.y = 202;
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

  const lad = DK_LADDERS.find(l => !l.broken && Math.abs(m.x - l.x) < 8 && m.y <= l.bottom + 4 && m.y >= l.top - 4);
  if (lad) {
    m.state = 'climb';
    m.ladder = lad;
    m.x = lad.x;
    m.y -= 1.6;
    m.climbFrame++;
    if (m.climbFrame % 6 === 0) playArcadeSfx('DK-WALK');
  }
}

function dkongClimbDown() {
  initAudio();
  const m = dkongGame.mario;
  if (m.state === 'dead' || m.hasHammer) return;

  const lad = DK_LADDERS.find(l => !l.broken && Math.abs(m.x - l.x) < 8 && m.y >= l.top - 6 && m.y < l.bottom);
  if (lad) {
    m.state = 'climb';
    m.ladder = lad;
    m.x = lad.x;
    m.y += 1.6;
    m.climbFrame++;
    if (m.climbFrame % 6 === 0) playArcadeSfx('DK-WALK');
  }
}

function updateDonkeyKongGame() {
  dkongGame.tick++;
  const m = dkongGame.mario;

  // Autonomous Attract Tour AI
  if (currentMode === 'tour') {
    if (!m.hasHammer) {
      if (m.currentGirder === 0) {
        if (m.x < 192) {
          m.vx = 1.4; m.facing = 'right'; m.state = 'run';
          const nearBarrel = dkongGame.barrels.find(b => b.tier === 0 && Math.abs(b.x - m.x) < 22 && b.x > m.x);
          if (nearBarrel && m.onGround) dkongJump();
        } else {
          m.vx = 0; dkongClimbUp();
        }
      } else if (m.currentGirder === 1) {
        if (m.x > 36) {
          m.vx = -1.4; m.facing = 'left'; m.state = 'run';
          const nearBarrel = dkongGame.barrels.find(b => b.tier === 1 && Math.abs(b.x - m.x) < 22 && b.x < m.x);
          if (nearBarrel && m.onGround) dkongJump();
        } else {
          m.vx = 1.2; m.facing = 'right';
        }
      }
    } else {
      m.vx = Math.sin(dkongGame.tick * 0.05) * 1.2;
      m.facing = m.vx > 0 ? 'right' : 'left';
    }
  }

  // Bonus Timer countdown
  dkongGame.bonusTick++;
  if (dkongGame.bonusTick % 50 === 0 && dkongGame.bonusTimer > 0) {
    dkongGame.bonusTimer = Math.max(0, dkongGame.bonusTimer - 100);
  }

  // Win condition: Rescue Pauline
  if (dkongGame.cleared) {
    dkongGame.winTimer--;
    if (dkongGame.winTimer <= 0) {
      dkongGame.level++;
      dkongGame.cleared = false;
      dkongGame.mario.x = 42;
      dkongGame.mario.y = 202;
      dkongGame.mario.currentGirder = 0;
      dkongGame.bonusTimer = 5000 + dkongGame.level * 500;
      dkongGame.barrels = [];
      dkongGame.hammer.available = true;
    }
    return;
  }

  // Death respawn
  if (m.state === 'dead') {
    dkongGame.deathTimer--;
    if (dkongGame.deathTimer <= 0) {
      if (dkongGame.lives > 0) {
        m.x = 42;
        m.y = 202;
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

  // Hammer timer
  if (m.hasHammer) {
    m.hammerTimer--;
    m.hammerFrame++;
    if (m.hammerFrame % 14 === 0) playArcadeSfx('DK-HAMR');
    if (m.hammerTimer <= 0) {
      m.hasHammer = false;
      m.state = 'stand';
    }
  }

  // Check hammer pickup
  if (dkongGame.hammer.available && !m.hasHammer) {
    if (Math.abs(m.x - dkongGame.hammer.x) < 12 && Math.abs(m.y - dkongGame.hammer.y) < 14) {
      dkongGame.hammer.available = false;
      m.hasHammer = true;
      m.hammerTimer = 300; // ~5 seconds of hammer time!
      m.state = 'hammer';
      playArcadeSfx('WARP');
    }
  }

  // Ladder Climbing Physics
  if (m.state === 'climb' && m.ladder) {
    m.y += m.vy;
    if (m.y <= m.ladder.top) {
      m.currentGirder = m.ladder.toTier;
      m.y = getGirderY(m.x, m.currentGirder) - 14;
      m.state = 'stand';
      m.onGround = true;
      m.ladder = null;
      m.vy = 0;
    } else if (m.y >= m.ladder.bottom) {
      m.currentGirder = m.ladder.fromTier;
      m.y = getGirderY(m.x, m.currentGirder) - 14;
      m.state = 'stand';
      m.onGround = true;
      m.ladder = null;
      m.vy = 0;
    }
    m.vy = 0;
  } else if (m.state === 'jump') {
    // Jump Arc
    m.x += m.vx;
    m.y += m.vy;
    m.vy += 0.28; // Gravity

    const floorY = getGirderY(m.x, m.currentGirder) - 14;
    if (m.vy > 0 && m.y >= floorY) {
      m.y = floorY;
      m.vy = 0;
      m.onGround = true;
      m.state = Math.abs(m.vx) > 0.1 ? 'run' : 'stand';
    }
  } else {
    // Running on Sloped Girder
    m.x += m.vx;
    m.x = Math.max(16, Math.min(224, m.x));
    const targetY = getGirderY(m.x, m.currentGirder) - 14;
    m.y = targetY;

    if (Math.abs(m.vx) > 0.1) {
      m.walkFrame++;
      m.state = m.hasHammer ? 'hammer' : 'run';
      if (m.walkFrame % 14 === 0) playArcadeSfx('DK-WALK');
    } else {
      m.state = m.hasHammer ? 'hammer' : 'stand';
    }
  }

  // Check top tier Pauline rescue
  if (m.y <= 44 && m.x >= 90 && m.x <= 138 && !dkongGame.cleared) {
    dkongGame.cleared = true;
    dkongGame.winTimer = 90;
    dkongGame.score += dkongGame.bonusTimer;
    if (dkongGame.score > dkongGame.highScore) dkongGame.highScore = dkongGame.score;
    playArcadeSfx('WARP');
    dkongGame.scorePops.push({ x: 110, y: 30, text: `+${dkongGame.bonusTimer}`, timer: 60 });
  }

  // Donkey Kong Barrel Toss Animation
  dkongGame.dk.frame++;
  if (dkongGame.dk.frame % 140 === 0) {
    dkongGame.barrels.push({
      x: 64,
      y: 60,
      tier: 3,
      vx: 1.4 + dkongGame.level * 0.15,
      rollFrame: 0,
      falling: false,
      scored: false
    });
  }

  // Update Barrels along sloped girders
  for (let i = dkongGame.barrels.length - 1; i >= 0; i--) {
    const b = dkongGame.barrels[i];
    b.rollFrame++;

    if (!b.falling) {
      b.x += b.vx;
      b.y = getGirderY(b.x, b.tier) - 8;

      // Transition to next girder when reaching edge
      if (b.tier === 3 && b.x >= 220) {
        b.tier = 2;
        b.vx = -(1.4 + dkongGame.level * 0.15);
      } else if (b.tier === 2 && b.x <= 20) {
        b.tier = 1;
        b.vx = (1.4 + dkongGame.level * 0.15);
      } else if (b.tier === 1 && b.x >= 220) {
        b.tier = 0;
        b.vx = -(1.4 + dkongGame.level * 0.15);
      } else if (b.tier === 0 && b.x <= 20) {
        // Oil drum incinerates barrel
        dkongGame.barrels.splice(i, 1);
        playArcadeSfx('AST-EXP');
        continue;
      }
    }

    // Mario jumps over barrel detection (+100 PTS)
    if (m.state === 'jump' && !b.scored && Math.abs(m.x - b.x) < 14 && m.y < b.y && (b.y - m.y) < 28) {
      b.scored = true;
      dkongGame.score += 100;
      if (dkongGame.score > dkongGame.highScore) dkongGame.highScore = dkongGame.score;
      dkongGame.scorePops.push({ x: m.x, y: m.y - 10, text: '100', timer: 30 });
      playArcadeSfx('BONUS');
    }

    // Hammer smashes barrel (+300 PTS)
    if (m.hasHammer && Math.abs(m.x - b.x) < 18 && Math.abs(m.y - b.y) < 16) {
      dkongGame.barrels.splice(i, 1);
      dkongGame.score += 300;
      if (dkongGame.score > dkongGame.highScore) dkongGame.highScore = dkongGame.score;
      dkongGame.scorePops.push({ x: b.x, y: b.y - 8, text: '300', timer: 35 });
      playArcadeSfx('DK-HAMR');
      continue;
    }

    // Barrel collision with Mario
    if (!m.hasHammer && m.state !== 'dead' && !dkongGame.cleared && currentMode !== 'tour') {
      if (Math.abs(m.x - b.x) < 9 && Math.abs(m.y - b.y) < 10) {
        m.state = 'dead';
        dkongGame.deathTimer = 60;
        dkongGame.lives--;
        playArcadeSfx('DK-FALL');
      }
    }
  }

  // Update floating score popups
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

  // CRT Arcade Black
  ctx.fillStyle = '#05070a';
  ctx.fillRect(0, 0, 240, 240);

  // 1. Draw 4 Sloped Magenta Steel Girders with cross-truss shading
  function drawGirder(startX, startY, endX, endY) {
    const dx = endX - startX;
    const dy = endY - startY;
    const len = Math.hypot(dx, dy);
    const steps = Math.floor(len / 8);

    // Top and bottom rail
    ctx.strokeStyle = '#e056fd'; // Authentic 1981 Magenta
    ctx.lineWidth = 2.0;
    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.lineTo(endX, endY);
    ctx.moveTo(startX, startY + 6);
    ctx.lineTo(endX, endY + 6);
    ctx.stroke();

    // Cross-truss diagonal rivets
    ctx.strokeStyle = '#be2edd';
    ctx.lineWidth = 1.0;
    ctx.beginPath();
    for (let i = 0; i < steps; i++) {
      const t1 = i / steps;
      const t2 = (i + 1) / steps;
      const x1 = startX + dx * t1, y1 = startY + dy * t1;
      const x2 = startX + dx * t2, y2 = startY + dy * t2;
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2 + 6);
    }
    ctx.stroke();

    // Specular rail highlights
    ctx.strokeStyle = '#f8a5c2';
    ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.lineTo(endX, endY);
    ctx.stroke();
  }

  // Tier 0: Bottom
  drawGirder(16, 218, 80, 218);
  drawGirder(80, 218, 224, 214);
  // Tier 1: Slopes down left to right
  drawGirder(18, 156, 222, 166);
  // Tier 2: Slopes down right to left
  drawGirder(222, 108, 24, 118);
  // Tier 3: Slopes down left to right
  drawGirder(24, 62, 88, 62);
  drawGirder(88, 66, 222, 70);
  // Top Girder (Pauline platform)
  drawGirder(90, 38, 138, 38);

  // 2. Cyan Steel Ladders
  DK_LADDERS.forEach(lad => {
    ctx.strokeStyle = lad.broken ? '#ff7675' : '#00d2d3'; // Cyan steel ladders
    ctx.lineWidth = 1.5;
    // Rungs
    for (let ly = lad.top; ly <= lad.bottom; ly += 5) {
      if (lad.broken && ly > lad.top + 10 && ly < lad.bottom - 10) continue;
      ctx.beginPath();
      ctx.moveTo(lad.x - 4, ly);
      ctx.lineTo(lad.x + 4, ly);
      ctx.stroke();
    }
    // Rails
    ctx.beginPath();
    ctx.moveTo(lad.x - 4, lad.top);
    ctx.lineTo(lad.x - 4, lad.bottom);
    ctx.moveTo(lad.x + 4, lad.top);
    ctx.lineTo(lad.x + 4, lad.bottom);
    ctx.stroke();
  });

  // 3. Living Oil Drum Flame at bottom left
  const drumX = 22, drumY = 202;
  ctx.fillStyle = '#2d3436';
  ctx.fillRect(drumX, drumY, 14, 16);
  ctx.strokeStyle = '#00d2d3';
  if (ctx.strokeRect) ctx.strokeRect(drumX, drumY, 14, 16);
  ctx.fillStyle = '#00d2d3';
  ctx.font = '6px monospace';
  ctx.fillText('OIL', drumX + 2, drumY + 11);

  // Dancing Multi-Colored Fire Tongues
  const fTick = dkongGame.tick;
  for (let f = 0; f < 3; f++) {
    const fx = drumX + 2 + f * 4;
    const fh = 6 + Math.sin(fTick * 0.2 + f) * 4;
    ctx.fillStyle = f === 1 ? '#fffa65' : '#ff4757';
    ctx.fillRect(fx, drumY - fh, 3, fh);
    ctx.fillStyle = '#00d2d3'; // Blue hot base
    ctx.fillRect(fx + 1, drumY - 2, 2, 2);
  }

  // 4. Animated Donkey Kong Sprite at top left
  const dkX = 40, dkY = 32;
  ctx.save();
  ctx.translate(dkX, dkY);
  // Gorilla Brown Body
  ctx.fillStyle = '#8c532b';
  ctx.fillRect(-14, 0, 28, 26);
  // Chest fur
  ctx.fillStyle = '#f5cd79';
  ctx.fillRect(-8, 6, 16, 14);
  // Angry Face & Teeth
  ctx.fillStyle = '#f5cd79';
  ctx.fillRect(-10, -8, 20, 10);
  ctx.fillStyle = '#e74c3c'; // Roaring mouth
  ctx.fillRect(-6, -2, 12, 4);
  ctx.fillStyle = '#ffffff'; // White fangs
  ctx.fillRect(-5, -2, 2, 2);
  ctx.fillRect(3, -2, 2, 2);
  // Eyes
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(-7, -7, 4, 4);
  ctx.fillRect(3, -7, 4, 4);
  ctx.fillStyle = '#000000';
  ctx.fillRect(-6, -6, 2, 2);
  ctx.fillRect(4, -6, 2, 2);

  // Pounding Chest Animation
  const dkChest = (fTick % 30 < 15);
  ctx.fillStyle = '#5d4037';
  if (dkChest) {
    ctx.fillRect(-18, 4, 6, 10); // Arm 1
    ctx.fillRect(12, 8, 8, 8);   // Arm 2 beating chest
  } else {
    ctx.fillRect(-14, 8, 8, 8);  // Arm 1 beating chest
    ctx.fillRect(12, 4, 6, 10);  // Arm 2
  }
  ctx.restore();

  // Stack of 4 waiting wooden barrels next to DK
  ctx.fillStyle = '#b7791f';
  ctx.fillRect(18, 38, 12, 9);
  ctx.fillRect(18, 48, 12, 9);
  ctx.strokeStyle = '#5d4037';
  if (ctx.strokeRect) ctx.strokeRect(18, 38, 12, 9);
  if (ctx.strokeRect) ctx.strokeRect(18, 48, 12, 9);

  // 5. Pauline on Top Platform
  const px = 114, py = 24;
  ctx.save();
  ctx.translate(px, py);
  // Fluttering Pink Dress
  ctx.fillStyle = '#ff9ff3';
  ctx.fillRect(-5, 0, 10, 14);
  // Blonde Hair
  ctx.fillStyle = '#feca57';
  ctx.fillRect(-6, -8, 12, 8);
  ctx.fillRect(-8, -4, 3, 10);
  // Face
  ctx.fillStyle = '#ffdd59';
  ctx.fillRect(-4, -6, 8, 6);
  ctx.fillStyle = '#000000';
  ctx.fillRect(-2, -5, 2, 2); // Eye

  // Animated HELP! Speech Bubble
  if (fTick % 40 < 25) {
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(8, -18, 28, 12);
    ctx.fillStyle = '#ff4757';
    ctx.font = 'bold 7px monospace';
    ctx.fillText('HELP!', 11, -9);
  }
  ctx.restore();

  // 6. Hammer Power-Up Pickup
  if (dkongGame.hammer.available) {
    ctx.fillStyle = '#5d4037';
    ctx.fillRect(dkongGame.hammer.x + 3, dkongGame.hammer.y - 6, 2, 12);
    ctx.fillStyle = '#f5cd79';
    ctx.fillRect(dkongGame.hammer.x, dkongGame.hammer.y - 10, 8, 5);
    ctx.strokeStyle = '#2d3436';
    if (ctx.strokeRect) ctx.strokeRect(dkongGame.hammer.x, dkongGame.hammer.y - 10, 8, 5);
  }

  // 7. Rolling Wood Barrels
  dkongGame.barrels.forEach(b => {
    ctx.save();
    ctx.translate(b.x, b.y);
    ctx.rotate((b.rollFrame * 0.15) * Math.sign(b.vx));
    // Barrel Body
    ctx.fillStyle = '#b7791f';
    ctx.beginPath();
    ctx.arc(0, 0, 6, 0, Math.PI * 2);
    ctx.fill();
    // Metal Hoop bands
    ctx.strokeStyle = '#2d3436';
    ctx.lineWidth = 1.2;
    ctx.stroke();
    // Wood cross planks
    ctx.strokeStyle = '#f5cd79';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(-5, 0); ctx.lineTo(5, 0);
    ctx.moveTo(0, -5); ctx.lineTo(0, 5);
    ctx.stroke();
    ctx.restore();
  });

  // 8. Player Mario / Jumpman (Detailed 12x16 Pixel Art)
  const m = dkongGame.mario;
  ctx.save();
  ctx.translate(m.x, m.y);
  if (m.facing === 'left') ctx.scale(-1, 1);

  if (m.state === 'dead') {
    // Mario Death Pose
    ctx.fillStyle = '#ee5253';
    ctx.fillRect(-7, 4, 14, 6);
    ctx.fillStyle = '#0abde3';
    ctx.fillRect(-4, 0, 8, 6);
    ctx.fillStyle = '#feca57';
    ctx.fillRect(-2, -4, 4, 4);
  } else {
    // Red Cap & Visor
    ctx.fillStyle = '#ee5253';
    ctx.fillRect(-5, -12, 10, 4);
    ctx.fillRect(0, -10, 8, 3); // Cap visor
    // Face & Nose
    ctx.fillStyle = '#ffdd59';
    ctx.fillRect(-4, -9, 8, 5);
    ctx.fillRect(2, -8, 4, 3); // Big Mario Nose
    // Mustache & Hair
    ctx.fillStyle = '#5d4037';
    ctx.fillRect(-5, -9, 3, 5); // Sideburn
    ctx.fillRect(0, -6, 6, 2);  // Mustache
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, -8, 2, 2);  // Eye

    // Blue Shirt
    ctx.fillStyle = '#0abde3';
    ctx.fillRect(-4, -6, 9, 5);
    // Red Dungarees / Overalls & Brass Button
    ctx.fillStyle = '#ee5253';
    ctx.fillRect(-3, -3, 7, 6);
    ctx.fillStyle = '#feca57';
    ctx.fillRect(1, -2, 2, 2);

    // Legs: Run Cycle vs Jump
    ctx.fillStyle = '#5d4037'; // Boots
    if (m.state === 'jump') {
      ctx.fillRect(-6, 0, 4, 3); // Left leg kicked out
      ctx.fillRect(2, -1, 4, 3);  // Right leg trailing
    } else if (m.state === 'run') {
      const step = (m.walkFrame >> 2) % 3;
      if (step === 0) { ctx.fillRect(-4, 2, 4, 3); ctx.fillRect(1, 2, 4, 3); }
      else if (step === 1) { ctx.fillRect(-6, 2, 4, 3); ctx.fillRect(2, 0, 4, 3); }
      else { ctx.fillRect(-2, 0, 4, 3); ctx.fillRect(3, 2, 4, 3); }
    } else {
      ctx.fillRect(-3, 2, 3, 3);
      ctx.fillRect(1, 2, 3, 3);
    }

    // Two-Handed Hammer Wielding
    if (m.hasHammer) {
      const hDown = (m.hammerFrame % 14 < 7);
      ctx.fillStyle = '#5d4037'; // Wood Handle
      ctx.fillRect(hDown ? 4 : -2, hDown ? -2 : -20, hDown ? 12 : 3, hDown ? 3 : 14);
      ctx.fillStyle = '#b7791f'; // Mallet Head
      ctx.fillRect(hDown ? 14 : -6, hDown ? -5 : -24, 8, 10);
      ctx.strokeStyle = '#2d3436';
      ctx.lineWidth = 1;
      if (ctx.strokeRect) ctx.strokeRect(hDown ? 14 : -6, hDown ? -5 : -24, 8, 10);
    }
  }
  ctx.restore();

  // 9. Floating Score Popups
  dkongGame.scorePops.forEach(sp => {
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 9px monospace';
    ctx.fillText(sp.text, sp.x - 6, sp.y);
  });

  // 10. Nintendo Score Header
  ctx.fillStyle = '#feca57'; // 1UP Yellow
  ctx.font = 'bold 8px monospace';
  ctx.fillText('1UP', 18, 12);
  ctx.fillStyle = '#ffffff';
  ctx.fillText(String(dkongGame.score).padStart(6, '0'), 18, 22);

  ctx.fillStyle = '#00e5ff'; // HIGH SCORE Cyan
  ctx.fillText('HIGH SCORE', 92, 12);
  ctx.fillStyle = '#ffffff';
  ctx.fillText(String(dkongGame.highScore).padStart(6, '0'), 102, 22);

  ctx.fillStyle = '#ff9f43'; // BONUS Orange
  ctx.fillText('BONUS', 184, 12);
  ctx.fillStyle = '#ffffff';
  ctx.fillText(String(dkongGame.bonusTimer).padStart(4, '0'), 188, 22);

  for (let l = 0; l < dkongGame.lives; l++) {
    ctx.fillStyle = '#ff4757';
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
  // Row 1 (y: 198): Yellow Taxi Sedans moving left
  for (let c = 0; c < 3; c++) froggerGame.vehicles.push({ x: c * 80, y: 198, w: 22, speed: -1.2, type: 'sedan', color: '#feca57' });
  // Row 2 (y: 182): Construction Bulldozers moving right
  for (let c = 0; c < 3; c++) froggerGame.vehicles.push({ x: c * 90, y: 182, w: 20, speed: 0.8, type: 'dozer', color: '#ffffff' });
  // Row 3 (y: 166): Red Sports Cars moving left
  for (let c = 0; c < 3; c++) froggerGame.vehicles.push({ x: c * 75, y: 166, w: 22, speed: -1.8, type: 'racer', color: '#ff4757' });
  // Row 4 (y: 150): Purple Formula Racers moving right
  for (let c = 0; c < 2; c++) froggerGame.vehicles.push({ x: c * 120, y: 150, w: 24, speed: 2.2, type: 'formula', color: '#a55eea' });
  // Row 5 (y: 134): Green Dump Trucks moving left
  for (let c = 0; c < 2; c++) froggerGame.vehicles.push({ x: c * 110, y: 134, w: 36, speed: -0.9, type: 'truck', color: '#10ac84' });
}

function spawnFroggerRiver() {
  froggerGame.logs = [];
  // Row 1 (y: 102): Medium Logs moving right
  for (let c = 0; c < 3; c++) froggerGame.logs.push({ x: c * 90, y: 102, w: 46, speed: 1.1, type: 'log' });
  // Row 2 (y: 86): Diving Turtles moving left
  for (let c = 0; c < 4; c++) froggerGame.logs.push({ x: c * 65, y: 86, w: 32, speed: -1.3, type: 'turtle' });
  // Row 3 (y: 70): Long Tree Logs moving right
  for (let c = 0; c < 2; c++) froggerGame.logs.push({ x: c * 130, y: 70, w: 72, speed: 1.5, type: 'log' });
  // Row 4 (y: 54): Small Logs moving right
  for (let c = 0; c < 3; c++) froggerGame.logs.push({ x: c * 85, y: 54, w: 36, speed: 1.0, type: 'log' });
  // Row 5 (y: 38): Fast Diving Turtles moving left
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

  // Autonomous Attract Tour AI
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

  // Move highway vehicles
  froggerGame.vehicles.forEach(v => {
    v.x += v.speed;
    if (v.speed < 0 && v.x < -40) v.x = 240 + Math.random() * 20;
    else if (v.speed > 0 && v.x > 260) v.x = -40;

    // Check hit frog
    if (Math.abs(v.y - fg.y) < 10 && Math.abs(v.x - fg.x) < (v.w / 2 + 4) && currentMode !== 'tour') {
      playArcadeSfx('DEATH');
      fg.gridX = 7; fg.gridY = 13; fg.x = 112; fg.y = 216;
      froggerGame.lives--;
      if (froggerGame.lives <= 0) {
        froggerGame.lives = 3;
        froggerGame.score = 0;
        initFroggerGame();
      }
    }
  });

  // Move river logs & turtles
  let onRiverSupport = false;
  froggerGame.logs.forEach(l => {
    l.x += l.speed;
    if (l.speed < 0 && l.x < -60) l.x = 240 + Math.random() * 20;
    else if (l.speed > 0 && l.x > 260) l.x = -60;

    // Carry frog if on log
    if (fg.gridY >= 2 && fg.gridY <= 6) {
      if (Math.abs(l.y - fg.y) < 8 && fg.x >= l.x - 4 && fg.x <= l.x + l.w + 4) {
        onRiverSupport = true;
        fg.x += l.speed;
        fg.gridX = Math.round((fg.x - 8) / 16);
      }
    }
  });

  // Drown in river if not on log
  if (fg.gridY >= 2 && fg.gridY <= 6 && !onRiverSupport && currentMode !== 'tour') {
    playArcadeSfx('DEATH');
    fg.gridX = 7; fg.gridY = 13; fg.x = 112; fg.y = 216;
    froggerGame.lives--;
    if (froggerGame.lives <= 0) {
      froggerGame.lives = 3;
      froggerGame.score = 0;
      initFroggerGame();
    }
  }

  // Home Bay Landing check (gridY === 1)
  if (fg.gridY === 1) {
    const bayIndex = Math.floor((fg.x - 10) / 48);
    if (bayIndex >= 0 && bayIndex < 5 && !froggerGame.homeBays[bayIndex]) {
      froggerGame.homeBays[bayIndex] = true;
      froggerGame.score += 500;
      if (froggerGame.score > froggerGame.highScore) froggerGame.highScore = froggerGame.score;
      playArcadeSfx('BONUS');
      fg.gridX = 7; fg.gridY = 13; fg.x = 112; fg.y = 216;

      // Cleared all 5 bays!
      if (froggerGame.homeBays.every(b => b)) {
        froggerGame.score += 1000;
        playArcadeSfx('WARP');
        froggerGame.homeBays = [false, false, false, false, false];
      }
    } else {
      // Missed bay or hit bush
      fg.gridX = 7; fg.gridY = 13; fg.x = 112; fg.y = 216;
      playArcadeSfx('DEATH');
    }
  }
}

function renderFroggerGame() {
  if (!ctx) return;
  if (ctx.save) ctx.save();

  // River Bank Top Shrubbery
  ctx.fillStyle = '#10ac84';
  ctx.fillRect(0, 16, 240, 18);
  const bayX = [20, 68, 116, 164, 212];
  bayX.forEach((bx, idx) => {
    ctx.fillStyle = '#0984e3'; // Water bay inlet
    ctx.fillRect(bx - 10, 16, 20, 18);
    // Green Lily Pad & Pink Lotus
    ctx.fillStyle = '#2ecc71';
    ctx.beginPath();
    ctx.arc(bx, 25, 7, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#ff7675';
    ctx.fillRect(bx - 1, 23, 3, 3);

    if (froggerGame.homeBays[idx]) {
      // Home Frog Saved
      ctx.fillStyle = '#00ff66';
      ctx.fillRect(bx - 4, 20, 8, 8);
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(bx - 3, 19, 2, 2);
      ctx.fillRect(bx + 1, 19, 2, 2);
    }
  });

  // Animated Shimmering Blue River
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
      ctx.moveTo(sx, wy);
      ctx.lineTo(sx + 8, wy);
    }
    ctx.stroke();
  }

  // Purple Median Safe Zone
  ctx.fillStyle = '#2f3542';
  ctx.fillRect(0, 118, 240, 16);
  ctx.fillStyle = '#57606f';
  ctx.fillRect(0, 118, 240, 2);
  ctx.fillRect(0, 132, 240, 2);

  // Asphalt Black Highway
  ctx.fillStyle = '#1e272e';
  ctx.fillRect(0, 134, 240, 80);
  for (let r = 1; r < 5; r++) {
    for (let c = 0; c < 240; c += 24) {
      ctx.fillStyle = '#dfe4ea';
      ctx.fillRect(c, 134 + r * 16, 12, 1);
    }
  }

  // Bottom Safe Grass
  ctx.fillStyle = '#2f3542';
  ctx.fillRect(0, 214, 240, 26);
  ctx.fillStyle = '#10ac84';
  ctx.fillRect(0, 214, 240, 3);

  // River Logs & Turtles
  froggerGame.logs.forEach(l => {
    if (l.type === 'log') {
      // Detailed Wood Log with Bark
      ctx.fillStyle = '#b36b2b';
      ctx.fillRect(l.x, l.y - 6, l.w, 12);
      ctx.fillStyle = '#d35400';
      ctx.fillRect(l.x + 4, l.y - 3, l.w - 8, 2);
      ctx.strokeStyle = '#5d4037';
      ctx.lineWidth = 1.0;
      if (ctx.strokeRect) ctx.strokeRect(l.x, l.y - 6, l.w, 12);
      // Tree end rings
      ctx.fillStyle = '#e58e26';
      ctx.beginPath();
      ctx.arc(l.x + 2, l.y, 4, 0, Math.PI * 2);
      ctx.fill();
    } else {
      // Swimming Turtles with Animated Flippers
      const swim = Math.sin(rTick * 0.18) * 2;
      for (let tx = l.x; tx < l.x + l.w; tx += 15) {
        // Red / Amber Shell
        ctx.fillStyle = '#e55039';
        ctx.beginPath();
        ctx.arc(tx + 6, l.y, 5, 0, Math.PI * 2);
        ctx.fill();
        // Shell scutes
        ctx.fillStyle = '#f6b93b';
        ctx.fillRect(tx + 4, l.y - 3, 4, 6);
        // Swimming flippers
        ctx.fillStyle = '#78e08f';
        ctx.fillRect(tx + 1, l.y - 6 + swim, 3, 3);
        ctx.fillRect(tx + 8, l.y - 6 + swim, 3, 3);
        ctx.fillRect(tx + 1, l.y + 4 - swim, 3, 3);
        ctx.fillRect(tx + 8, l.y + 4 - swim, 3, 3);
      }
    }
  });

  // Highway Vehicles (Detailed Retro Arcade Sprites)
  froggerGame.vehicles.forEach(v => {
    ctx.save();
    ctx.translate(v.x, v.y);
    if (v.speed < 0) ctx.scale(-1, 1);

    if (v.type === 'truck') {
      // Heavy Green Dump Truck
      ctx.fillStyle = '#10ac84'; // Cab
      ctx.fillRect(0, -6, 12, 12);
      ctx.fillStyle = '#2f3542'; // Cargo flatbed
      ctx.fillRect(-22, -6, 22, 12);
      ctx.fillStyle = '#dfe4ea'; // Windshield
      ctx.fillRect(6, -5, 4, 5);
      // Wheels
      ctx.fillStyle = '#000000';
      ctx.fillRect(-18, 6, 6, 2);
      ctx.fillRect(-6, 6, 6, 2);
      ctx.fillRect(4, 6, 6, 2);
      ctx.fillRect(-18, -8, 6, 2);
      ctx.fillRect(-6, -8, 6, 2);
      ctx.fillRect(4, -8, 6, 2);
    } else if (v.type === 'racer') {
      // Red Wedge Racecar with Rear Spoiler
      ctx.fillStyle = '#ee5253';
      ctx.beginPath();
      ctx.moveTo(12, 0);
      ctx.lineTo(-10, -6);
      ctx.lineTo(-10, 6);
      ctx.closePath();
      ctx.fill();
      // Rear spoiler
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(-12, -7, 3, 14);
      // Driver Helmet
      ctx.fillStyle = '#feca57';
      ctx.beginPath();
      ctx.arc(-2, 0, 3, 0, Math.PI * 2);
      ctx.fill();
    } else if (v.type === 'formula') {
      // Purple Open-Wheel Racer
      ctx.fillStyle = '#a55eea';
      ctx.fillRect(-8, -4, 18, 8);
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(-4, -6, 4, 12); // Front wing
      ctx.fillRect(8, -6, 3, 12);  // Rear wing
    } else {
      // Yellow Taxi Sedan with checkered roof
      ctx.fillStyle = '#feca57';
      ctx.fillRect(-10, -6, 20, 12);
      ctx.fillStyle = '#2d3436';
      ctx.fillRect(-2, -5, 8, 10); // Windows
      ctx.fillStyle = '#000000';
      ctx.fillRect(-4, -7, 6, 2); // Taxi sign
    }
    ctx.restore();
  });

  // Player Frog (Animated Leaping Legs & Eyes)
  const fg = froggerGame.frog;
  ctx.save();
  ctx.translate(fg.x, fg.y);
  if (fg.dir === 'down') ctx.rotate(Math.PI);
  else if (fg.dir === 'left') ctx.rotate(-Math.PI / 2);
  else if (fg.dir === 'right') ctx.rotate(Math.PI / 2);

  // Frog Body
  ctx.fillStyle = '#00ff66';
  ctx.fillRect(-5, -5, 10, 10);
  ctx.fillStyle = '#10ac84';
  ctx.fillRect(-3, -3, 6, 6);

  // Leaping extended legs vs landed
  if (fg.hopTick > 0) {
    ctx.fillStyle = '#00ff66';
    ctx.fillRect(-7, 4, 3, 6); // Left leg back
    ctx.fillRect(4, 4, 3, 6);  // Right leg back
  } else {
    ctx.fillStyle = '#10ac84';
    ctx.fillRect(-6, 3, 4, 3);
    ctx.fillRect(2, 3, 4, 3);
  }

  // Bulging 3D Eyes
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(-5, -7, 3, 3);
  ctx.fillRect(2, -7, 3, 3);
  ctx.fillStyle = '#000000';
  ctx.fillRect(-4, -6, 2, 2);
  ctx.fillRect(3, -6, 2, 2);
  ctx.restore();

  // Header
  ctx.fillStyle = '#fffa65';
  ctx.font = 'bold 8px monospace';
  ctx.fillText('1UP', 18, 12);
  ctx.fillStyle = '#ffffff';
  ctx.fillText(String(froggerGame.score).padStart(6, '0'), 18, 22);
  ctx.fillStyle = '#00e5ff';
  ctx.fillText('HIGH SCORE', 92, 12);
  ctx.fillStyle = '#ffffff';
  ctx.fillText(String(froggerGame.highScore).padStart(6, '0'), 102, 22);

  for (let l = 0; l < froggerGame.lives; l++) {
    ctx.fillStyle = '#00ff66';
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
      size: 3 // 3 = Large, 2 = Medium, 1 = Small
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
      vx: Math.cos(s.angle) * 5.5 + s.vx * 0.4,
      vy: Math.sin(s.angle) * 5.5 + s.vy * 0.4,
      life: 40
    });
    playArcadeSfx('TEM-ZAP');
  }
}

function asteroidsHyperspace() {
  initAudio();
  asteroidsGame.ship.x = Math.random() * 220 + 10;
  asteroidsGame.ship.y = Math.random() * 220 + 10;
  asteroidsGame.ship.vx = 0;
  asteroidsGame.ship.vy = 0;
  playArcadeSfx('WARP');
}

function updateAsteroidsGame() {
  asteroidsGame.tick++;
  const s = asteroidsGame.ship;

  // Autonomous Attract Tour AI
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
  }

  // Ship inertia & drag
  if (s.thrust) {
    s.vx += Math.cos(s.angle) * 0.12;
    s.vy += Math.sin(s.angle) * 0.12;
  }
  s.vx *= 0.985;
  s.vy *= 0.985;
  s.x += s.vx;
  s.y += s.vy;

  // Screen Wraparound
  if (s.x < 0) s.x += 240; else if (s.x > 240) s.x -= 240;
  if (s.y < 0) s.y += 240; else if (s.y > 240) s.y -= 240;

  // Bullets
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

    // Check hit rock
    for (let r = asteroidsGame.rocks.length - 1; r >= 0; r--) {
      const rk = asteroidsGame.rocks[r];
      const dist = Math.hypot(bl.x - rk.x, bl.y - rk.y);
      if (dist < rk.radius) {
        asteroidsGame.bullets.splice(b, 1);
        playArcadeSfx('AST-EXP');
        const pts = rk.size === 3 ? 50 : (rk.size === 2 ? 100 : 200);
        asteroidsGame.score += pts;
        if (asteroidsGame.score > asteroidsGame.highScore) asteroidsGame.highScore = asteroidsGame.score;

        // Spawn exploding debris lines
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

        // Split rock into smaller fragments
        if (rk.size > 1) {
          for (let sp = 0; sp < 2; sp++) {
            asteroidsGame.rocks.push({
              x: rk.x,
              y: rk.y,
              vx: (Math.random() - 0.5) * 2.2,
              vy: (Math.random() - 0.5) * 2.2,
              radius: rk.size === 3 ? 12 : 7,
              size: rk.size - 1
            });
          }
        }
        asteroidsGame.rocks.splice(r, 1);
        break;
      }
    }
  }

  // Update debris
  for (let d = asteroidsGame.debris.length - 1; d >= 0; d--) {
    const db = asteroidsGame.debris[d];
    db.x += db.vx;
    db.y += db.vy;
    db.angle += db.vRot;
    db.life--;
    if (db.life <= 0) asteroidsGame.debris.splice(d, 1);
  }

  // Update rocks
  asteroidsGame.rocks.forEach(rk => {
    rk.x += rk.vx;
    rk.y += rk.vy;
    if (rk.x < 0) rk.x += 240; else if (rk.x > 240) rk.x -= 240;
    if (rk.y < 0) rk.y += 240; else if (rk.y > 240) rk.y -= 240;

    // Check hit ship
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

  // Next level when all rocks cleared
  if (asteroidsGame.rocks.length === 0) {
    asteroidsGame.level++;
    playArcadeSfx('WARP');
    spawnAsteroidsField(4 + asteroidsGame.level);
  }
}

function renderAsteroidsGame() {
  if (!ctx) return;
  if (ctx.save) ctx.save();

  // CRT Vector Phosphor Black
  ctx.fillStyle = '#05070a';
  ctx.fillRect(0, 0, 240, 240);

  // Vector CRT Phosphor Beam: Bright Cyan / White with Glow
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = 1.4;
  ctx.shadowColor = '#00e5ff';
  ctx.shadowBlur = 4;

  // Bullets (Glowing photon torpedoes)
  ctx.fillStyle = '#ffffff';
  asteroidsGame.bullets.forEach(bl => {
    ctx.fillRect(bl.x - 1, bl.y - 1, 2, 2);
  });

  // Exploding Vector Debris Lines
  asteroidsGame.debris.forEach(db => {
    ctx.save();
    ctx.translate(db.x, db.y);
    ctx.rotate(db.angle);
    ctx.beginPath();
    ctx.moveTo(-db.len / 2, 0);
    ctx.lineTo(db.len / 2, 0);
    ctx.stroke();
    ctx.restore();
  });

  // Asteroid Vector Rocks (Multi-faceted geometric polygons with craters)
  asteroidsGame.rocks.forEach(rk => {
    ctx.beginPath();
    const pts = rk.size === 3 ? 10 : (rk.size === 2 ? 8 : 6);
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

  // Vector Ship
  const s = asteroidsGame.ship;
  ctx.save();
  ctx.translate(s.x, s.y);
  ctx.rotate(s.angle);
  ctx.beginPath();
  ctx.moveTo(9, 0);   // Nose tip
  ctx.lineTo(-7, -6); // Left wing
  ctx.lineTo(-4, 0);  // Inner engine notch
  ctx.lineTo(-7, 6);  // Right wing
  ctx.closePath();
  ctx.stroke();

  // Rocket Exhaust Flame (Flickering retro vector flame)
  if (s.thrust && animTick % 4 < 2) {
    ctx.strokeStyle = '#ff9f43';
    ctx.beginPath();
    ctx.moveTo(-4, 0);
    ctx.lineTo(-11, 0);
    ctx.stroke();
  }
  ctx.restore();

  ctx.shadowBlur = 0;

  // Header
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
      dist: 0.15 + i * 0.12, // 0 = far end, 1 = near rim (danger!)
      vDist: 0.0035,
      type: i % 2 === 0 ? 'flipper' : 'spiker'
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
    playArcadeSfx('TEM-ZAP');
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
    playArcadeSfx('WARP');
  }
}

function updateTempestGame() {
  tempestGame.tick++;

  // Autonomous Attract Tour AI
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

  // Update superzapper flash
  if (tempestGame.superzapperFlash > 0) tempestGame.superzapperFlash--;

  // Update shots
  for (let s = tempestGame.shots.length - 1; s >= 0; s--) {
    const sh = tempestGame.shots[s];
    sh.dist += sh.vDist;
    if (sh.dist <= 0) {
      tempestGame.shots.splice(s, 1);
      continue;
    }
    // Check hit enemy in same segment
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

  // Update enemies
  tempestGame.enemies.forEach(en => {
    en.dist += en.vDist;
    // Flippers flip between adjacent segments!
    if (en.type === 'flipper' && tempestGame.tick % 45 === 0) {
      en.seg = (en.seg + (Math.random() < 0.5 ? 1 : 15)) % 16;
    }
    // Enemy reached top rim (player danger)
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

  // Respawn enemies if cleared
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

  // CRT Vector Black
  ctx.fillStyle = '#05070a';
  ctx.fillRect(0, 0, 240, 240);

  const cx = 120, cy = 125;
  const numSegs = 16;
  const rNear = 95, rFar = 22;

  // Superzapper Lightning Arc Flash
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

  // 3D Color Vector Tube Wireframe
  ctx.strokeStyle = '#00d2d3';
  ctx.lineWidth = 1.6;
  ctx.shadowColor = '#00e5ff';
  ctx.shadowBlur = 4;

  // Far inner ring
  ctx.beginPath();
  for (let i = 0; i < numSegs; i++) {
    const a = (i / numSegs) * Math.PI * 2;
    const fx = cx + Math.cos(a) * rFar;
    const fy = cy + Math.sin(a) * (rFar * 0.6);
    if (i === 0) ctx.moveTo(fx, fy); else ctx.lineTo(fx, fy);
  }
  ctx.closePath();
  ctx.stroke();

  // Near rim outer ring
  ctx.beginPath();
  for (let i = 0; i < numSegs; i++) {
    const a = (i / numSegs) * Math.PI * 2;
    const nx = cx + Math.cos(a) * rNear;
    const ny = cy + Math.sin(a) * (rNear * 0.6);
    if (i === 0) ctx.moveTo(nx, ny); else ctx.lineTo(nx, ny);
  }
  ctx.closePath();
  ctx.stroke();

  // Connecting channel lines
  for (let i = 0; i < numSegs; i++) {
    const a = (i / numSegs) * Math.PI * 2;
    const nx = cx + Math.cos(a) * rNear;
    const ny = cy + Math.sin(a) * (rNear * 0.6);
    const fx = cx + Math.cos(a) * rFar;
    const fy = cy + Math.sin(a) * (rFar * 0.6);
    ctx.beginPath();
    ctx.moveTo(nx, ny);
    ctx.lineTo(fx, fy);
    ctx.stroke();
  }

  // Draw Enemies: Authentic 1981 Vector Flippers (Geometric Bowties with Perspective Scaling)
  tempestGame.enemies.forEach(en => {
    const a = (en.seg + 0.5) / numSegs * Math.PI * 2;
    const r = rFar + (rNear - rFar) * en.dist;
    const ex = cx + Math.cos(a) * r;
    const ey = cy + Math.sin(a) * (r * 0.6);
    const scale = 0.8 + en.dist * 0.8;

    ctx.save();
    ctx.translate(ex, ey);
    ctx.rotate(a + Math.PI / 2);
    ctx.strokeStyle = (animTick % 6 < 3) ? '#ff3838' : '#ff9f1a'; // Flashing Flipper Red/Gold
    ctx.lineWidth = 1.6;
    ctx.beginPath();
    // Left claw
    ctx.moveTo(-5 * scale, -4 * scale);
    ctx.lineTo(-2 * scale, 0);
    ctx.lineTo(-5 * scale, 4 * scale);
    // Waist
    ctx.lineTo(2 * scale, 0);
    // Right claw
    ctx.lineTo(5 * scale, -4 * scale);
    ctx.lineTo(2 * scale, 0);
    ctx.lineTo(5 * scale, 4 * scale);
    ctx.stroke();
    ctx.restore();
  });

  // Draw Shots flying down tube
  ctx.fillStyle = '#fffa65';
  tempestGame.shots.forEach(sh => {
    const a = (sh.seg + 0.5) / numSegs * Math.PI * 2;
    const r = rFar + (rNear - rFar) * sh.dist;
    const sx = cx + Math.cos(a) * r;
    const sy = cy + Math.sin(a) * (r * 0.6);
    ctx.fillRect(sx - 1, sy - 1, 3, 3);
  });

  // Player Rotary Blaster Claw on Near Rim (Authentic Yellow Vector Pincer)
  const aBlaster = (tempestGame.segment + 0.5) / numSegs * Math.PI * 2;
  const bx = cx + Math.cos(aBlaster) * rNear;
  const by = cy + Math.sin(aBlaster) * (rNear * 0.6);
  ctx.save();
  ctx.translate(bx, by);
  ctx.rotate(aBlaster + Math.PI / 2);
  ctx.strokeStyle = '#fff200'; // Yellow Blaster Claw
  ctx.lineWidth = 2.4;
  ctx.beginPath();
  ctx.moveTo(-7, -5);
  ctx.lineTo(-3, 1);
  ctx.lineTo(0, -2);
  ctx.lineTo(3, 1);
  ctx.lineTo(7, -5);
  ctx.stroke();
  // Dual Cyan Plasma Sparks on wingtips
  ctx.fillStyle = '#00f5d4';
  ctx.fillRect(-8, -6, 2, 2);
  ctx.fillRect(6, -6, 2, 2);
  ctx.restore();

  ctx.shadowBlur = 0;

  // Header
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
    playArcadeSfx('TRACT');
  }
}

function updateGyrussGame() {
  gyrussGame.tick++;
  const g = gyrussGame;

  // Autonomous Attract Tour AI
  if (currentMode === 'tour') {
    gyrussGame.angle += 0.055;
    if (gyrussGame.tick % 12 === 0) gyrussFire();
  }

  // Move shots towards central warp hole
  for (let s = g.shots.length - 1; s >= 0; s--) {
    const sh = g.shots[s];
    sh.dist += sh.vDist;
    if (sh.dist <= 8) {
      g.shots.splice(s, 1);
      continue;
    }
    // Check hit enemy
    for (let e = g.enemies.length - 1; e >= 0; e--) {
      const en = g.enemies[e];
      if (Math.abs(en.angle - sh.angle) < 0.28 && Math.abs(en.dist - sh.dist) < 12) {
        g.shots.splice(s, 1);
        g.enemies.splice(e, 1);
        g.score += 200;
        playArcadeSfx('AST-EXP');
        break;
      }
    }
  }

  // Spawn enemy spiral waves from center warp hole
  if (g.tick % 40 === 0) {
    g.enemies.push({
      angle: Math.random() * Math.PI * 2,
      dist: 10,
      vDist: 1.4,
      vAngle: (Math.random() - 0.5) * 0.05
    });
  }

  // Move enemies spiraling outward
  for (let e = g.enemies.length - 1; e >= 0; e--) {
    const en = g.enemies[e];
    en.dist += en.vDist;
    en.angle += en.vAngle;

    // Check hit player on orbital rim (dist ~98)
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

  // Cosmic Black
  ctx.fillStyle = '#05070a';
  ctx.fillRect(0, 0, 240, 240);

  const cx = 120, cy = 125;

  // Concentric Blue Warp Tunnel Rings
  for (let r = 24; r <= 100; r += 24) {
    ctx.strokeStyle = `rgba(0, 229, 255, ${0.15 + (r / 100) * 0.35})`;
    ctx.lineWidth = 1.0;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();
  }

  // 3D Perspective Radial Star Warp Spiraling Outward
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.45)';
  for (let st = 0; st < 24; st++) {
    const sa = (st / 24) * Math.PI * 2 + animTick * 0.015;
    ctx.beginPath();
    ctx.moveTo(cx + Math.cos(sa) * 20, cy + Math.sin(sa) * 20);
    ctx.lineTo(cx + Math.cos(sa) * 112, cy + Math.sin(sa) * 112);
    ctx.stroke();
  }

  // Central Planet / Warp Core
  ctx.fillStyle = '#0652dd';
  ctx.beginPath();
  ctx.arc(cx, cy, 20, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = '#00d2d3';
  ctx.beginPath();
  ctx.arc(cx - 4, cy - 4, 7, 0, Math.PI * 2);
  ctx.fill();

  // Inward Lasers (Twin Red/Yellow Pulse Bolts)
  gyrussGame.shots.forEach(sh => {
    const sx = cx + Math.cos(sh.angle) * sh.dist;
    const sy = cy + Math.sin(sh.angle) * sh.dist;
    ctx.fillStyle = '#fffa65';
    ctx.fillRect(sx - 1, sy - 1, 3, 3);
  });

  // Enemies: 3D Perspective Scaling Geometric Space Drones
  gyrussGame.enemies.forEach(en => {
    const ex = cx + Math.cos(en.angle) * en.dist;
    const ey = cy + Math.sin(en.angle) * en.dist;
    const scale = Math.max(0.4, (en.dist / 100));

    ctx.save();
    ctx.translate(ex, ey);
    ctx.rotate(en.angle + Math.PI / 2);
    // Delta solar wings
    ctx.fillStyle = (animTick % 8 < 4) ? '#ff3838' : '#e056fd';
    ctx.beginPath();
    ctx.moveTo(0, -6 * scale);
    ctx.lineTo(-8 * scale, 6 * scale);
    ctx.lineTo(-3 * scale, 4 * scale);
    ctx.lineTo(0, 5 * scale);
    ctx.lineTo(3 * scale, 4 * scale);
    ctx.lineTo(8 * scale, 6 * scale);
    ctx.closePath();
    ctx.fill();
    // Glowing core
    ctx.fillStyle = '#f9ca24';
    ctx.fillRect(-2 * scale, -2 * scale, 4 * scale, 4 * scale);
    ctx.restore();
  });

  // Player Starfighter in 360-Degree Orbital Rim
  const a = gyrussGame.angle;
  const sx = cx + Math.cos(a) * 98;
  const sy = cy + Math.sin(a) * 98;
  ctx.save();
  ctx.translate(sx, sy);
  ctx.rotate(a + Math.PI / 2);
  // Aerodynamic white fuselage
  ctx.fillStyle = '#f8f9fa';
  ctx.beginPath();
  ctx.moveTo(0, -10);
  ctx.lineTo(-9, 7);
  ctx.lineTo(-3, 5);
  ctx.lineTo(3, 5);
  ctx.lineTo(9, 7);
  ctx.closePath();
  ctx.fill();
  // Cyan cockpit canopy
  ctx.fillStyle = '#00d2d3';
  ctx.fillRect(-2, -6, 4, 6);
  // Red wing blasters
  ctx.fillStyle = '#ee5253';
  ctx.fillRect(-10, -1, 3, 7);
  ctx.fillRect(7, -1, 3, 7);
  // Pulsing blue ion engine exhaust trail
  ctx.fillStyle = (animTick % 4 < 2) ? '#54a0ff' : '#00d2d3';
  ctx.fillRect(-3, 6, 2, 4 + (animTick % 3));
  ctx.fillRect(1, 6, 2, 4 + (animTick % 3));
  ctx.restore();

  // Header
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
"""

if __name__ == '__main__':
    print("generate_upgraded_engines loaded successfully.")
