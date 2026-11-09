import re

def main():
    print("=== UPGRADING DONKEY KONG TO FULLY PLAYABLE ARCADE ENGINE & HIGH-RES CRT GRAPHICS ===")
    
    with open("tools/build_hardware_template.py", "r") as f:
        content = f.read()

    # 1. Update canvas CSS for crisp, high-res rendering
    content = content.replace(
        "image-rendering: pixelated;",
        "image-rendering: auto; image-rendering: -webkit-optimize-contrast;"
    )

    # 2. Add complete Playable Donkey Kong 25M Engine to tools/build_hardware_template.py
    # We replace the static renderDonkeyKongTour function with the full playable engine + high-res renderer
    old_dkong_needle = """// 2. DONKEY KONG: True 1981 Nintendo Sloped Girders & Pixel Art
function renderDonkeyKongTour(f) {"""

    # Find where renderDonkeyKongTour ends
    idx_dk_start = content.find(old_dkong_needle)
    if idx_dk_start == -1:
        raise ValueError("Could not find renderDonkeyKongTour in tools/build_hardware_template.py")

    idx_dk_end = content.find("// 3. FROGGER:", idx_dk_start)
    if idx_dk_end == -1:
        raise ValueError("Could not find // 3. FROGGER: in tools/build_hardware_template.py")

    playable_dkong_code = """// =========================================================================
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
  for (const lad of DK_LADDERS) {
    if (lad.broken) continue;
    if (Math.abs(m.x - lad.x) <= 8 && m.y <= lad.bottom + 4 && m.y >= lad.top - 4) {
      m.x = lad.x;
      m.state = 'climb';
      m.ladder = lad;
      m.vy = -1.3;
      m.climbFrame++;
      if (m.climbFrame % 6 === 0) playArcadeSfx('DK-WALK');
      return;
    }
  }
}

function dkongClimbDown() {
  initAudio();
  const m = dkongGame.mario;
  if (m.state === 'dead' || m.hasHammer) return;
  for (const lad of DK_LADDERS) {
    if (lad.broken) continue;
    if (Math.abs(m.x - lad.x) <= 8 && m.y >= lad.top - 6 && m.y <= lad.bottom - 2) {
      m.x = lad.x;
      m.state = 'climb';
      m.ladder = lad;
      m.vy = 1.3;
      m.climbFrame++;
      if (m.climbFrame % 6 === 0) playArcadeSfx('DK-WALK');
      return;
    }
  }
}

function updateDonkeyKongGame() {
  const m = dkongGame.mario;

  // Bonus Countdown Timer
  dkongGame.bonusTick++;
  if (dkongGame.bonusTick % 50 === 0 && dkongGame.bonusTimer > 0) {
    dkongGame.bonusTimer = Math.max(0, dkongGame.bonusTimer - 100);
  }

  // Handle Win Animation
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

  // Handle Death Animation
  if (m.state === 'dead') {
    dkongGame.deathTimer--;
    if (dkongGame.deathTimer <= 0) {
      if (dkongGame.lives > 0) {
        m.x = 42;
        m.y = 202;
        m.vx = 0;
        m.vy = 0;
        m.state = 'stand';
        m.onGround = true;
        m.currentGirder = 0;
      } else {
        // Game Over -> Reset to Level 1
        dkongGame.lives = 3;
        dkongGame.score = 0;
        initDonkeyKongGame();
      }
    }
    return;
  }

  // Hammer Power-up Timer
  if (m.hasHammer) {
    m.hammerTimer--;
    m.hammerFrame++;
    if (m.hammerFrame % 14 === 0) playArcadeSfx('DK-HAMR');
    if (m.hammerTimer <= 0) {
      m.hasHammer = false;
      m.state = 'stand';
    }
  }

  // Hammer Collect Check
  if (dkongGame.hammer.available && !m.hasHammer) {
    if (Math.abs(m.x - dkongGame.hammer.x) < 12 && Math.abs(m.y - dkongGame.hammer.y) < 14) {
      dkongGame.hammer.available = false;
      m.hasHammer = true;
      m.hammerTimer = 260;
      m.state = 'hammer';
      playArcadeSfx('WARP');
    }
  }

  // Mario Movement: Climbing
  if (m.state === 'climb' && m.ladder) {
    m.y += m.vy;
    m.vx = 0;
    if (m.y <= m.ladder.top) {
      // Reached top of ladder
      m.currentGirder = m.ladder.toTier;
      m.y = getGirderY(m.x, m.currentGirder) - 14;
      m.state = 'stand';
      m.onGround = true;
      m.ladder = null;
      m.vy = 0;
    } else if (m.y >= m.ladder.bottom) {
      // Reached bottom of ladder
      m.currentGirder = m.ladder.fromTier;
      m.y = getGirderY(m.x, m.currentGirder) - 14;
      m.state = 'stand';
      m.onGround = true;
      m.ladder = null;
      m.vy = 0;
    }
    m.vy = 0; // Stop ladder slide unless key pressed
  } else if (m.state === 'jump') {
    // Mario In Air Jumping
    m.x += m.vx;
    m.y += m.vy;
    m.vy += 0.28; // Gravity

    // Landing check
    const floorY = getGirderY(m.x, m.currentGirder) - 14;
    if (m.vy > 0 && m.y >= floorY) {
      m.y = floorY;
      m.vy = 0;
      m.onGround = true;
      m.state = Math.abs(m.vx) > 0.1 ? 'run' : 'stand';
    }
  } else {
    // Mario On Ground
    m.x += m.vx;
    m.y = getGirderY(m.x, m.currentGirder) - 14;

    if (Math.abs(m.vx) > 0.1) {
      m.walkFrame++;
      m.state = m.hasHammer ? 'hammer' : 'run';
      if (m.walkFrame % 14 === 0) playArcadeSfx('DK-WALK');
    } else {
      m.state = m.hasHammer ? 'hammer' : 'stand';
    }
  }

  // Bounds limit
  m.x = Math.max(20, Math.min(220, m.x));

  // Check Win Condition (Pauline Platform: Tier 4 ladder top)
  if (m.y <= 44 && m.x >= 90 && m.x <= 138 && !dkongGame.cleared) {
    dkongGame.cleared = true;
    dkongGame.winTimer = 90;
    dkongGame.score += dkongGame.bonusTimer;
    if (dkongGame.score > dkongGame.highScore) dkongGame.highScore = dkongGame.score;
    playArcadeSfx('WARP');
    dkongGame.scorePops.push({ x: 110, y: 30, text: `+${dkongGame.bonusTimer}`, timer: 60 });
  }

  // Donkey Kong AI: Barrel Spawning & Chest Pound
  dkongGame.dk.frame++;
  if (dkongGame.dk.frame % 150 === 0) {
    // Roll new barrel down top tier
    dkongGame.barrels.push({
      x: 94,
      y: 58,
      vx: 1.4 + dkongGame.level * 0.15,
      tier: 3,
      rollAngle: 0,
      scored: false,
      dropping: false
    });
  }

  // Update Barrels
  for (let i = dkongGame.barrels.length - 1; i >= 0; i--) {
    const b = dkongGame.barrels[i];
    b.rollAngle += (b.vx > 0 ? 0.2 : -0.2);

    if (b.tier === 3) {
      b.x += b.vx;
      b.y = getGirderY(b.x, 3) - 6;
      if (b.x >= 218) {
        // Drop down to Tier 2
        b.tier = 2;
        b.vx = -(1.4 + dkongGame.level * 0.15);
        b.x = 216;
      }
    } else if (b.tier === 2) {
      b.x += b.vx;
      b.y = getGirderY(b.x, 2) - 6;
      if (b.x <= 26) {
        // Drop down to Tier 1
        b.tier = 1;
        b.vx = (1.4 + dkongGame.level * 0.15);
        b.x = 28;
      }
    } else if (b.tier === 1) {
      b.x += b.vx;
      b.y = getGirderY(b.x, 1) - 6;
      if (b.x >= 212) {
        // Drop down to Tier 0 (Bottom)
        b.tier = 0;
        b.vx = -(1.4 + dkongGame.level * 0.15);
        b.x = 210;
      }
    } else if (b.tier === 0) {
      b.x += b.vx;
      b.y = getGirderY(b.x, 0) - 6;
      if (b.x <= 34) {
        // Destroyed in Flaming Oil Drum
        dkongGame.barrels.splice(i, 1);
        playArcadeSfx('AST-EXP');
        continue;
      }
    }

    // Collision Check: Mario Jump Over Barrel (+100 PTS)
    if (m.state === 'jump' && !b.scored) {
      if (Math.abs(m.x - b.x) < 14 && m.y < b.y && (b.y - m.y) < 28) {
        b.scored = true;
        dkongGame.score += 100;
        if (dkongGame.score > dkongGame.highScore) dkongGame.highScore = dkongGame.score;
        dkongGame.scorePops.push({ x: m.x, y: m.y - 10, text: '100', timer: 30 });
        playArcadeSfx('BONUS');
      }
    }

    // Collision Check: Hammer Smash (+300 PTS)
    if (m.hasHammer && m.state !== 'dead') {
      if (Math.abs(m.x - b.x) < 20 && Math.abs(m.y - b.y) < 16) {
        dkongGame.barrels.splice(i, 1);
        dkongGame.score += 300;
        if (dkongGame.score > dkongGame.highScore) dkongGame.highScore = dkongGame.score;
        dkongGame.scorePops.push({ x: b.x, y: b.y - 8, text: '300', timer: 35 });
        playArcadeSfx('DK-HAMR');
        continue;
      }
    }

    // Collision Check: Barrel Hits Mario
    if (!m.hasHammer && m.state !== 'dead' && !dkongGame.cleared) {
      if (Math.abs(m.x - b.x) < 9 && Math.abs(m.y - b.y) < 10) {
        m.state = 'dead';
        dkongGame.deathTimer = 60;
        dkongGame.lives--;
        playArcadeSfx('DK-FALL');
      }
    }
  }

  // Update Floating Score Popups
  for (let s = dkongGame.scorePops.length - 1; s >= 0; s--) {
    const sp = dkongGame.scorePops[s];
    sp.y -= 0.5;
    sp.timer--;
    if (sp.timer <= 0) dkongGame.scorePops.splice(s, 1);
  }
}

// -------------------------------------------------------------------------
// HIGH-RESOLUTION 1981 ARCADE CRT RENDERER FOR DONKEY KONG
// -------------------------------------------------------------------------
function renderDonkeyKongGame() {
  if (!ctx) return;
  if (ctx.save) ctx.save();

  // 1. Deep Arcade Black CRT Background
  ctx.fillStyle = '#05070a';
  ctx.fillRect(0, 0, 240, 240);

  // 2. High-Definition Steel Girders with Specular Highlights & X-Truss Framework
  const girderSegments = [
    { tier: 3, x: 88, w: 136, slope: 4 },
    { tier: 3, x: 18, w: 70, slope: 0 }, // DK Platform
    { tier: 2, x: 24, w: 198, slope: -10 },
    { tier: 1, x: 18, w: 200, slope: 10 },
    { tier: 0, x: 18, w: 62, slope: 0 },  // Oil Can Platform
    { tier: 0, x: 80, w: 144, slope: -4 }
  ];

  girderSegments.forEach(g => {
    const yStart = getGirderY(g.x, g.tier);
    const yEnd = getGirderY(g.x + g.w, g.tier);

    // Double I-Beam Rails (Base & Highlight)
    ctx.strokeStyle = '#e84118';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(g.x, yStart);
    ctx.lineTo(g.x + g.w, yEnd);
    ctx.stroke();

    ctx.strokeStyle = '#ff6b81'; // Upper Specular Highlight
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(g.x, yStart - 1);
    ctx.lineTo(g.x + g.w, yEnd - 1);
    ctx.stroke();

    ctx.strokeStyle = '#990033'; // Lower Flange
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(g.x, yStart + 5);
    ctx.lineTo(g.x + g.w, yEnd + 5);
    ctx.stroke();

    // Steel Cross-Lattice X-Truss Pattern
    for (let gx = g.x + 6; gx < g.x + g.w - 6; gx += 12) {
      const gy = getGirderY(gx, g.tier);
      ctx.strokeStyle = '#d63031';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(gx - 4, gy + 1);
      ctx.lineTo(gx + 4, gy + 5);
      ctx.moveTo(gx - 4, gy + 5);
      ctx.lineTo(gx + 4, gy + 1);
      ctx.stroke();

      // Steel Joint Rivet
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(gx, gy + 3, 1, 1);
    }
  });

  // Pauline's Top Platform
  ctx.fillStyle = '#ff2a7a';
  ctx.fillRect(88, 38, 54, 4);
  ctx.fillStyle = '#ff99c8';
  ctx.fillRect(88, 38, 54, 1);

  // 3. Cobalt Blue Ladders with 3D Cylindrical Rungs
  DK_LADDERS.forEach(lad => {
    // Rails
    ctx.fillStyle = '#0984e3';
    ctx.fillRect(lad.x - 5, lad.top, 2, lad.bottom - lad.top);
    ctx.fillRect(lad.x + 5, lad.top, 2, lad.bottom - lad.top);
    ctx.fillStyle = '#74b9ff';
    ctx.fillRect(lad.x - 5, lad.top, 1, lad.bottom - lad.top);

    // Rungs
    const maxRung = lad.broken ? lad.top + 14 : lad.bottom;
    for (let ry = lad.bottom - 4; ry >= lad.top + 2; ry -= 6) {
      if (lad.broken && ry < lad.bottom - 16) continue; // Broken gap
      ctx.fillStyle = '#0984e3';
      ctx.fillRect(lad.x - 4, ry, 9, 2);
      ctx.fillStyle = '#dfe6e9';
      ctx.fillRect(lad.x - 4, ry, 9, 1);
    }
  });

  // 4. Flaming Oil Drum at Bottom Left
  const drumX = 22;
  const drumY = 202;
  ctx.fillStyle = '#0984e3'; // Blue Oil Can
  ctx.fillRect(drumX, drumY, 14, 16);
  ctx.strokeStyle = '#2d3436';
  ctx.lineWidth = 1;
  ctx.strokeRect(drumX, drumY, 14, 16);
  // Metal Ridges
  ctx.fillStyle = '#74b9ff';
  ctx.fillRect(drumX, drumY + 4, 14, 1);
  ctx.fillRect(drumX, drumY + 11, 14, 1);

  // Living Flickering Fire
  const fireF = (animTick >> 2);
  const flameH = 8 + (Math.sin(animTick * 0.4) * 4);
  // Outer Red Flame
  ctx.fillStyle = '#eb4d4b';
  ctx.beginPath();
  ctx.moveTo(drumX - 1, drumY);
  ctx.lineTo(drumX + 7, drumY - flameH);
  ctx.lineTo(drumX + 15, drumY);
  ctx.fill();
  // Mid Orange Flame
  ctx.fillStyle = '#f0932b';
  ctx.beginPath();
  ctx.moveTo(drumX + 2, drumY);
  ctx.lineTo(drumX + 7, drumY - flameH * 0.75);
  ctx.lineTo(drumX + 12, drumY);
  ctx.fill();
  // Inner Yellow Core
  ctx.fillStyle = '#ffbe76';
  ctx.beginPath();
  ctx.moveTo(drumX + 4, drumY);
  ctx.lineTo(drumX + 7, drumY - flameH * 0.45);
  ctx.lineTo(drumX + 10, drumY);
  ctx.fill();

  // 5. Donkey Kong (Detailed 42x32 Arcade Sprite)
  ctx.save();
  ctx.translate(34, 30);
  const dkPound = ((animTick >> 3) % 2 === 0);
  // Dark Brown Fur Body
  ctx.fillStyle = '#4b2810';
  ctx.fillRect(6, 8, 28, 22);
  ctx.fillStyle = '#6d4428'; // Shoulder muscles
  ctx.fillRect(4, 10, 32, 6);
  // Tan Chest Pecs
  ctx.fillStyle = '#ffb74d';
  ctx.fillRect(10, 12, 20, 14);
  ctx.fillStyle = '#f57c00';
  ctx.fillRect(19, 12, 2, 14); // Pec cleft
  // Head & Brow Ridge
  ctx.fillStyle = '#4b2810';
  ctx.fillRect(8, 0, 24, 10);
  ctx.fillStyle = '#6d4428';
  ctx.fillRect(10, 2, 20, 3); // Brow
  // Eyes
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(12, 4, 4, 3);
  ctx.fillRect(24, 4, 4, 3);
  ctx.fillStyle = '#000000';
  ctx.fillRect(14, 5, 2, 2);
  ctx.fillRect(24, 5, 2, 2);
  // Snarl Mouth with Teeth
  ctx.fillStyle = '#d63031';
  ctx.fillRect(13, 8, 14, 4);
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(14, 8, 3, 2);
  ctx.fillRect(23, 8, 3, 2);
  // Arms: Chest Thump Cycle
  ctx.fillStyle = '#4b2810';
  if (dkPound) {
    ctx.fillRect(0, 4, 8, 16);  // Left arm raised
    ctx.fillRect(32, 12, 8, 16); // Right arm low
  } else {
    ctx.fillRect(0, 12, 8, 16); // Left arm low
    ctx.fillRect(32, 4, 8, 16);  // Right arm raised
  }
  ctx.restore();

  // Stack of Barrels next to DK
  ctx.fillStyle = '#b36b2b';
  ctx.fillRect(18, 38, 12, 9);
  ctx.fillRect(18, 48, 12, 9);
  ctx.strokeStyle = '#2d3436';
  ctx.lineWidth = 1;
  ctx.strokeRect(18, 38, 12, 9);
  ctx.strokeRect(18, 48, 12, 9);

  // 6. Pauline / Lady in Pink Dress
  const p = dkongGame.pauline;
  const paulineX = 104;
  const paulineY = 20;
  // Blonde Flowing Hair
  ctx.fillStyle = '#f9ca24';
  ctx.fillRect(paulineX, paulineY, 10, 10);
  ctx.fillStyle = '#eb4d4b'; // Red Ribbon
  ctx.fillRect(paulineX + 2, paulineY + 1, 6, 2);
  // Face & Blue Eyes
  ctx.fillStyle = '#ffbe76';
  ctx.fillRect(paulineX + 2, paulineY + 4, 6, 6);
  ctx.fillStyle = '#0984e3';
  ctx.fillRect(paulineX + 6, paulineY + 5, 2, 2);
  // Pink Flared Dress
  ctx.fillStyle = '#ff4d94';
  ctx.fillRect(paulineX, paulineY + 10, 10, 8);
  ctx.fillRect(paulineX - 2, paulineY + 14, 14, 4);
  // Waving Arms
  const pWave = ((animTick >> 3) % 2 === 0);
  ctx.fillStyle = '#ffbe76';
  ctx.fillRect(paulineX - 4, pWave ? paulineY + 6 : paulineY + 10, 3, 5);
  ctx.fillRect(paulineX + 11, pWave ? paulineY + 10 : paulineY + 6, 3, 5);

  // "HELP!" Speech Bubble
  if (animTick % 60 < 45) {
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(paulineX + 16, paulineY - 6, 28, 12);
    ctx.fillStyle = '#d63031';
    ctx.font = 'bold 8px monospace';
    ctx.fillText('HELP!', paulineX + 18, paulineY + 3);
  }

  // 7. Collectible Hammer on Tier 3
  if (dkongGame.hammer.available) {
    ctx.fillStyle = '#5d4037'; // Wood handle
    ctx.fillRect(dkongGame.hammer.x + 3, dkongGame.hammer.y - 6, 2, 12);
    ctx.fillStyle = '#b7791f'; // Mallet head
    ctx.fillRect(dkongGame.hammer.x, dkongGame.hammer.y - 10, 8, 5);
    ctx.strokeStyle = '#2d3436';
    ctx.lineWidth = 1;
    ctx.strokeRect(dkongGame.hammer.x, dkongGame.hammer.y - 10, 8, 5);
  }

  // 8. Rolling Barrels with Spin Animation
  dkongGame.barrels.forEach(b => {
    ctx.save();
    ctx.translate(b.x, b.y);
    ctx.rotate(b.rollAngle);
    // Barrel Body
    ctx.fillStyle = '#b36b2b';
    ctx.beginPath();
    ctx.arc(0, 0, 5.5, 0, Math.PI * 2);
    ctx.fill();
    // Steel Hoops
    ctx.strokeStyle = '#2c3e50';
    ctx.lineWidth = 1.5;
    ctx.stroke();
    // Silver Rivets & Wood Plank Staves
    ctx.strokeStyle = '#e17055';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(-5, 0); ctx.lineTo(5, 0);
    ctx.moveTo(0, -5); ctx.lineTo(0, 5);
    ctx.stroke();
    ctx.restore();
  });

  // 9. Mario / Jumpman (Detailed 16x22 Arcade Sprite)
  const m = dkongGame.mario;
  ctx.save();
  ctx.translate(m.x, m.y);
  if (m.facing === 'left') {
    ctx.scale(-1, 1);
  }

  if (m.state === 'dead') {
    // Death spin animation
    ctx.rotate(animTick * 0.3);
    ctx.fillStyle = '#ee5253';
    ctx.fillRect(-6, -6, 12, 12);
    ctx.fillStyle = '#feca57';
    ctx.fillText('★', -4, -8);
  } else if (m.state === 'climb') {
    // Rear Climbing Stance
    const cHand = ((m.climbFrame >> 2) % 2 === 0);
    ctx.fillStyle = '#ee5253'; // Red Cap
    ctx.fillRect(-4, -13, 8, 4);
    ctx.fillStyle = '#0abde3'; // Blue Shirt & Overalls
    ctx.fillRect(-5, -9, 10, 8);
    ctx.fillStyle = '#ee5253';
    ctx.fillRect(-4, -5, 8, 6);
    // Hands reaching up
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(-6, cHand ? -14 : -9, 3, 3);
    ctx.fillRect(3, cHand ? -9 : -14, 3, 3);
    ctx.fillStyle = '#5d4037'; // Boots
    ctx.fillRect(-5, 1, 4, 3);
    ctx.fillRect(1, 1, 4, 3);
  } else {
    // Red Cap & Visor Brim
    ctx.fillStyle = '#ee5253';
    ctx.fillRect(-3, -13, 9, 3);
    ctx.fillRect(2, -12, 4, 2); // Brim
    // Face, Nose, Mustache
    ctx.fillStyle = '#ffbe76';
    ctx.fillRect(-2, -10, 7, 4);
    ctx.fillStyle = '#000000';
    ctx.fillRect(2, -8, 5, 2); // Mustache
    ctx.fillRect(1, -9, 2, 2); // Eye
    // Blue Shirt & Sleeves
    ctx.fillStyle = '#0abde3';
    ctx.fillRect(-4, -6, 9, 5);
    // Red Dungarees / Overalls & Brass Buttons
    ctx.fillStyle = '#ee5253';
    ctx.fillRect(-3, -3, 7, 6);
    ctx.fillStyle = '#feca57'; // Yellow Brass Button
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
      ctx.strokeRect(hDown ? 14 : -6, hDown ? -5 : -24, 8, 10);
    }
  }
  ctx.restore();

  // 10. Floating Score Popups
  dkongGame.scorePops.forEach(sp => {
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 9px monospace';
    ctx.fillText(sp.text, sp.x - 6, sp.y);
  });

  // 11. Authentic Nintendo Arcade Header (Scores & Bonus)
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

  // Lives Hearts
  for (let l = 0; l < dkongGame.lives; l++) {
    ctx.fillStyle = '#ff4757';
    ctx.font = '8px monospace';
    ctx.fillText('♥', 188 + l * 10, 32);
  }

  if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
  if (ctx.restore) ctx.restore();
}

function renderDonkeyKongTour(f) {
  updateDonkeyKongGame();
  renderDonkeyKongGame();
}
"""

    content = content[:idx_dk_start] + playable_dkong_code + "\n" + content[idx_dk_end:]

    # 3. Update switchActiveGame to initialize Donkey Kong game when selected
    content = content.replace(
        "renderDonkeyKongTour(0);",
        "initDonkeyKongGame(); renderDonkeyKongGame();"
    )

    # 4. Update mainLoop rendering dispatch for Donkey Kong
    old_loop_dispatch = """    } else if (activeGame === 'dkong') {
      renderDonkeyKongTour(animTick);"""
    
    new_loop_dispatch = """    } else if (activeGame === 'dkong') {
      updateDonkeyKongGame();
      renderDonkeyKongGame();"""
    content = content.replace(old_loop_dispatch, new_loop_dispatch)

    # 5. Add Donkey Kong controls into handleKey
    old_kbd_dk = """  // Pac-Man specific keyboard routing (strictly isolated to Pac-Man)
  if (activeGame === 'pacman') {"""

    new_kbd_dk = """  // Donkey Kong Full Interactive Controls
  if (activeGame === 'dkong') {
    const k = e.key.toLowerCase();
    if (k === 'a' || e.key === 'ArrowLeft') {
      dkongGame.mario.vx = -1.6;
      dkongGame.mario.facing = 'left';
      if (dkongGame.mario.onGround) dkongGame.mario.state = 'run';
      e.preventDefault();
      return;
    } else if (k === 'd' || e.key === 'ArrowRight') {
      dkongGame.mario.vx = 1.6;
      dkongGame.mario.facing = 'right';
      if (dkongGame.mario.onGround) dkongGame.mario.state = 'run';
      e.preventDefault();
      return;
    } else if (k === 'w' || e.key === 'ArrowUp') {
      dkongClimbUp();
      e.preventDefault();
      return;
    } else if (k === 's' || e.key === 'ArrowDown') {
      dkongClimbDown();
      e.preventDefault();
      return;
    } else if (e.key === ' ' || e.key === 'Enter' || k === '1' || k === 'c' || k === '5' || k === 'p') {
      dkongJump();
      e.preventDefault();
      return;
    }
    return;
  }

  // Pac-Man specific keyboard routing (strictly isolated to Pac-Man)
  if (activeGame === 'pacman') {"""

    content = content.replace(old_kbd_dk, new_kbd_dk)

    # 6. Add Keyup release handling for Donkey Kong
    old_keyup_target = """window.addEventListener('keyup', (e) => {
  const k = e.key.toLowerCase();"""

    new_keyup_target = """window.addEventListener('keyup', (e) => {
  const k = e.key.toLowerCase();
  if (activeGame === 'dkong') {
    if (k === 'a' || e.key === 'ArrowLeft') {
      if (dkongGame.mario.vx < 0) {
        dkongGame.mario.vx = 0;
        if (dkongGame.mario.onGround) dkongGame.mario.state = 'stand';
      }
    } else if (k === 'd' || e.key === 'ArrowRight') {
      if (dkongGame.mario.vx > 0) {
        dkongGame.mario.vx = 0;
        if (dkongGame.mario.onGround) dkongGame.mario.state = 'stand';
      }
    }
  }"""
    content = content.replace(old_keyup_target, new_keyup_target)

    # 7. Wire D-Pad & Quick Play for Donkey Kong
    old_dpad_bindings = """const dpadUp = document.getElementById('dpadUp');"""
    # Let's check how dpad buttons are bound in build_hardware_template.py
    
    with open("tools/build_hardware_template.py", "w") as f_out:
        f_out.write(content)
    
    print("Successfully updated tools/build_hardware_template.py with Playable Donkey Kong Engine!")

if __name__ == "__main__":
    main()
