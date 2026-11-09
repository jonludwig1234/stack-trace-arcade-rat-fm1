#!/usr/bin/env python3
"""
Arcade Hall of Fame & High Score Leaderboard Engine for M-VAVE FM-1.
Maintains persistent Top-5 record books across all 8 arcade classics
with interactive initial entry, ranking, and live HUD telemetry.
"""

def get_leaderboard_engine_js():
    return '''
// =========================================================================
// ARCADE HALL OF FAME & HIGH SCORE LEADERBOARD SYSTEM (8 GAMES)
// =========================================================================
const DEFAULT_LEADERBOARDS = {
  pacman: [
    { rank: 1, initials: 'BIL', score: 3333360, name: 'Billy Mitchell' },
    { rank: 2, initials: 'AYR', score: 3250000, name: 'Chris Ayra' },
    { rank: 3, initials: 'RAT', score: 1850400, name: 'Arcade Rat' },
    { rank: 4, initials: 'STK', score: 980200, name: 'Stack Trace' },
    { rank: 5, initials: 'JON', score: 450000, name: 'Jon Doe' }
  ],
  cclimber: [
    { rank: 1, initials: 'NIC', score: 254800, name: 'Nichibutsu Pro' },
    { rank: 2, initials: 'CLB', score: 189400, name: 'Crazy Climber' },
    { rank: 3, initials: 'RAT', score: 149000, name: 'Arcade Rat' },
    { rank: 4, initials: 'STK', score: 95000, name: 'Stack Trace' },
    { rank: 5, initials: 'JON', score: 54000, name: 'Jon Doe' }
  ],
  galaga: [
    { rank: 1, initials: 'ARM', score: 4522800, name: 'Armando G' },
    { rank: 2, initials: 'NAM', score: 3200000, name: 'Namco Dual' },
    { rank: 3, initials: 'RAT', score: 1840000, name: 'Arcade Rat' },
    { rank: 4, initials: 'STK', score: 850000, name: 'Stack Trace' },
    { rank: 5, initials: 'JON', score: 420000, name: 'Jon Doe' }
  ],
  dkong: [
    { rank: 1, initials: 'WIE', score: 1068000, name: 'Steve Wiebe' },
    { rank: 2, initials: 'BIL', score: 1050200, name: 'Billy Mitchell' },
    { rank: 3, initials: 'RAT', score: 650000, name: 'Arcade Rat' },
    { rank: 4, initials: 'STK', score: 420000, name: 'Stack Trace' },
    { rank: 5, initials: 'JON', score: 280000, name: 'Jon Doe' }
  ],
  frogger: [
    { rank: 1, initials: 'LAF', score: 896980, name: 'Pat Laffaye' },
    { rank: 2, initials: 'HOP', score: 540000, name: 'River Hopper' },
    { rank: 3, initials: 'RAT', score: 320000, name: 'Arcade Rat' },
    { rank: 4, initials: 'STK', score: 180000, name: 'Stack Trace' },
    { rank: 5, initials: 'JON', score: 95000, name: 'Jon Doe' }
  ],
  asteroids: [
    { rank: 1, initials: 'SAF', score: 41336440, name: 'Scott Safran' },
    { rank: 2, initials: 'VEC', score: 15400000, name: 'Vector King' },
    { rank: 3, initials: 'RAT', score: 5800000, name: 'Arcade Rat' },
    { rank: 4, initials: 'STK', score: 2400000, name: 'Stack Trace' },
    { rank: 5, initials: 'JON', score: 980000, name: 'Jon Doe' }
  ],
  tempest: [
    { rank: 1, initials: 'VEC', score: 2450000, name: 'Tube Runner' },
    { rank: 2, initials: 'POK', score: 1850000, name: 'POKEY Master' },
    { rank: 3, initials: 'RAT', score: 950000, name: 'Arcade Rat' },
    { rank: 4, initials: 'STK', score: 620000, name: 'Stack Trace' },
    { rank: 5, initials: 'JON', score: 340000, name: 'Jon Doe' }
  ],
  gyruss: [
    { rank: 1, initials: 'BAR', score: 1850000, name: 'Baroque Ace' },
    { rank: 2, initials: 'NEP', score: 1240000, name: 'Neptune Star' },
    { rank: 3, initials: 'RAT', score: 850000, name: 'Arcade Rat' },
    { rank: 4, initials: 'STK', score: 520000, name: 'Stack Trace' },
    { rank: 5, initials: 'JON', score: 290000, name: 'Jon Doe' }
  ]
};

let arcadeLeaderboards = JSON.parse(JSON.stringify(DEFAULT_LEADERBOARDS));

function getGameHighScore(gameId) {
  const list = arcadeLeaderboards[gameId] || arcadeLeaderboards.pacman;
  return list && list.length ? list[0].score : 10000;
}

function checkHighScoreSubmit(gameId, score) {
  if (!score || score <= 0) return false;
  const list = arcadeLeaderboards[gameId] || [];
  const minScore = list.length >= 5 ? list[list.length - 1].score : 0;
  if (score > minScore) {
    promptInitialsEntry(gameId, score);
    return true;
  }
  return false;
}

function promptInitialsEntry(gameId, score) {
  const raw = (typeof prompt === 'function')
    ? prompt(`CONGRATULATIONS! High score of ${score} pts! Enter your 3 initials:`, 'RAT')
    : 'RAT';
  if (raw !== null && raw !== undefined) {
    const cleanInitials = String(raw).trim().toUpperCase().slice(0, 3) || 'RAT';
    submitHighScore(gameId, cleanInitials, score, true);
  }
}

function submitHighScore(gameId, initials, score, forceTop5 = false) {
  if (!arcadeLeaderboards[gameId]) arcadeLeaderboards[gameId] = [];
  const cleanInitials = String(initials || 'AAA').trim().toUpperCase().slice(0, 3) || 'AAA';
  const numScore = Number(score) || 0;
  const newEntry = {
    rank: 0,
    initials: cleanInitials,
    score: numScore,
    name: 'Player ' + cleanInitials,
    _justSubmitted: true
  };
  arcadeLeaderboards[gameId].push(newEntry);
  arcadeLeaderboards[gameId].sort((a, b) => b.score - a.score);
  arcadeLeaderboards[gameId] = arcadeLeaderboards[gameId].slice(0, 5);
  if (forceTop5 && !arcadeLeaderboards[gameId].some(e => e._justSubmitted)) {
    arcadeLeaderboards[gameId][4] = newEntry;
  }
  arcadeLeaderboards[gameId].forEach((entry, idx) => {
    delete entry._justSubmitted;
    entry.rank = idx + 1;
  });

  saveLeaderboardsToNVRAM();

  if (typeof updateMissionCard === 'function') updateMissionCard(gameId);
  if (typeof renderLeaderboardUI === 'function') renderLeaderboardUI(gameId);
}

function saveLeaderboardsToNVRAM() {
  try {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('fm1_arcade_nvram_leaderboard', JSON.stringify(arcadeLeaderboards));
    }
  } catch (e) {
    console.warn('NVRAM write failed:', e);
  }
}

function loadLeaderboardsFromNVRAM() {
  try {
    if (typeof localStorage !== 'undefined') {
      const data = localStorage.getItem('fm1_arcade_nvram_leaderboard');
      if (data) {
        const parsed = JSON.parse(data);
        if (parsed && typeof parsed === 'object') {
          for (const k in DEFAULT_LEADERBOARDS) {
            if (Array.isArray(parsed[k]) && parsed[k].length > 0) {
              arcadeLeaderboards[k] = parsed[k];
            }
          }
        }
      }
    }
  } catch (e) {
    console.warn('NVRAM restore failed, using factory defaults:', e);
    arcadeLeaderboards = JSON.parse(JSON.stringify(DEFAULT_LEADERBOARDS));
  }
}

function resetLeaderboardsToDefaults() {
  arcadeLeaderboards = JSON.parse(JSON.stringify(DEFAULT_LEADERBOARDS));
  saveLeaderboardsToNVRAM();
  if (typeof renderLeaderboardUI === 'function') {
    renderLeaderboardUI(typeof activeGame !== 'undefined' ? activeGame : 'pacman');
  }
}

// Auto-load NVRAM on startup
loadLeaderboardsFromNVRAM();
'''

if __name__ == "__main__":
    print(f"Generated {len(get_leaderboard_engine_js())} bytes of Leaderboard Engine JS.")
