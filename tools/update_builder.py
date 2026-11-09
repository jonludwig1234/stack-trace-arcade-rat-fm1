import re

def update():
    with open("tools/build_hardware_template.py", "r") as f:
        content = f.read()

    # 1. Update CSS
    old_css_needle = """  /* Quick Navigation / Modes Strip */
  .nav-strip {
    width: 100%;
    max-width: 960px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    flex-wrap: wrap;
    gap: 8px;
  }
  .game-toggle-group {
    display: flex;
    gap: 5px;
    background: #161c1e;
    padding: 3px 5px;
    border-radius: 8px;
    border: 1px solid #2e393b;
  }
  .game-btn {
    background: transparent;
    border: none;
    color: #8b9ea0;
    padding: 5px 12px;
    border-radius: 6px;
    font-size: 0.68rem;
    font-weight: 800;
    cursor: pointer;
    transition: all 0.12s ease;
    display: flex;
    align-items: center;
    gap: 5px;
  }
  .game-btn:hover { color: #fff; background: rgba(255,255,255,0.06); }
  .game-btn.active {
    background: var(--accent);
    color: #172e24;
    font-weight: 900;
    box-shadow: 0 0 10px var(--accent-glow);
  }
  .game-btn.tour-btn.active {
    background: #a55eea;
    color: #fff;
    box-shadow: 0 0 10px rgba(165, 94, 234, 0.6);
  }

  .mode-indicator {
    display: flex;
    gap: 3px;
    background: #161c1e;
    padding: 3px 5px;
    border-radius: 8px;
    border: 1px solid #2e393b;
    overflow-x: auto;
  }
  .mode-tag {
    font-size: 0.60rem;
    font-weight: 800;
    padding: 4px 8px;
    border-radius: 5px;
    color: #7d9193;
    cursor: pointer;
    transition: all 0.12s ease;
    letter-spacing: 0.3px;
    font-family: var(--font-mono);
  }
  .mode-tag:hover { color: #fff; background: rgba(255,255,255,0.06); }
  .mode-tag.active {
    background: #253632;
    color: var(--accent);
    border: 1px solid #3e5a52;
  }"""

    new_css = """  /* =========================================================================
     TWO-TIER CREATIVE WORKSPACE: STUDIO TABS & CONTEXT SHELVES
     Provides direct 1-click access to Arcade Vault, Synth Studio, Tracker, etc.
     ========================================================================= */
  .studio-nav-bar {
    width: 100%;
    max-width: 960px;
    display: flex;
    gap: 6px;
    background: #131a1d;
    padding: 5px;
    border-radius: 10px;
    border: 1px solid #2b3b3f;
    margin-bottom: 8px;
    overflow-x: auto;
  }
  .studio-tab {
    flex: 1;
    min-width: 120px;
    background: transparent;
    border: 1px solid transparent;
    color: #8fa59f;
    padding: 7px 10px;
    border-radius: 7px;
    font-size: 0.68rem;
    font-weight: 800;
    cursor: pointer;
    transition: all 0.15s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    white-space: nowrap;
    letter-spacing: 0.3px;
  }
  .studio-tab:hover {
    color: #fff;
    background: rgba(255, 255, 255, 0.05);
    border-color: #3d5156;
  }
  .studio-tab.active {
    background: #20352e;
    color: var(--accent);
    border: 1px solid #436d5f;
    box-shadow: 0 0 12px rgba(170, 228, 200, 0.25);
  }

  /* Context Shelves */
  .shelf-wrap {
    width: 100%;
    max-width: 960px;
    margin-bottom: 8px;
  }
  .context-shelf {
    display: none;
    background: #141c1f;
    border-radius: 10px;
    border: 1px solid #2d3e42;
    padding: 10px 14px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.5);
    flex-direction: column;
    gap: 8px;
  }
  .context-shelf.active {
    display: flex;
  }
  .shelf-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.70rem;
    font-weight: 800;
    color: var(--accent);
    letter-spacing: 0.5px;
    border-bottom: 1px solid #233135;
    padding-bottom: 6px;
  }
  .shelf-header span.tag {
    font-size: 0.60rem;
    color: #8fa5a0;
    font-weight: 600;
    font-family: var(--font-mono);
  }

  /* Arcade Vault Shelf (8 Playable Games Gallery) */
  .arcade-gallery-grid {
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    gap: 6px;
    width: 100%;
  }
  @media (max-width: 900px) {
    .arcade-gallery-grid { grid-template-columns: repeat(4, 1fr); }
  }
  @media (max-width: 540px) {
    .arcade-gallery-grid { grid-template-columns: repeat(2, 1fr); }
  }
  .arcade-card {
    background: #192327;
    border: 1px solid #33454a;
    border-radius: 8px;
    padding: 7px 5px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    cursor: pointer;
    transition: all 0.15s ease;
    gap: 2px;
  }
  .arcade-card:hover {
    border-color: var(--accent);
    transform: translateY(-2px);
    background: #212f34;
  }
  .arcade-card.active {
    background: linear-gradient(135deg, #1b382d 0%, #162a24 100%);
    border-color: var(--accent);
    box-shadow: 0 0 12px var(--accent-glow);
  }
  .arcade-card .card-emoji { font-size: 1.15rem; line-height: 1.2; }
  .arcade-card .card-name { font-size: 0.66rem; font-weight: 900; color: #e2ece8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }
  .arcade-card .card-meta { font-size: 0.53rem; color: #7f9994; font-family: var(--font-mono); }
  .arcade-card .card-badge {
    font-size: 0.48rem;
    padding: 1px 4px;
    border-radius: 3px;
    background: #253639;
    color: #a4bab5;
    font-weight: 800;
    text-transform: uppercase;
    margin-top: 2px;
  }
  .arcade-card.active .card-badge {
    background: var(--accent);
    color: #172e24;
  }

  /* Synth Studio Shelf (5 Soundchips + Envelopes + Modulators) */
  .synth-section {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .synth-row {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }
  .synth-label {
    font-size: 0.62rem;
    font-weight: 800;
    color: #92a8a4;
    letter-spacing: 0.6px;
    min-width: 110px;
    font-family: var(--font-mono);
  }
  .synth-btn-group {
    display: flex;
    gap: 5px;
    flex-wrap: wrap;
  }
  .synth-chip-btn {
    background: #1c262a;
    border: 1px solid #36494e;
    color: #adc4be;
    padding: 5px 10px;
    border-radius: 6px;
    font-size: 0.65rem;
    font-weight: 800;
    cursor: pointer;
    transition: all 0.12s ease;
    display: flex;
    align-items: center;
    gap: 5px;
  }
  .synth-chip-btn:hover {
    color: #fff;
    border-color: #00e5ff;
    background: #23343a;
  }
  .synth-chip-btn.active {
    background: #173836;
    color: #00e5ff;
    border-color: #00e5ff;
    box-shadow: 0 0 10px rgba(0, 229, 255, 0.4);
    font-weight: 900;
  }
  .synth-opt-btn {
    background: #1c262a;
    border: 1px solid #36494e;
    color: #9eb5af;
    padding: 4px 9px;
    border-radius: 5px;
    font-size: 0.62rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.1s ease;
  }
  .synth-opt-btn:hover { color: #fff; border-color: var(--accent); }
  .synth-opt-btn.active {
    background: var(--accent);
    color: #172e24;
    font-weight: 800;
    box-shadow: 0 0 8px var(--accent-glow);
  }
  .synth-hint-bar {
    font-size: 0.62rem;
    color: #8da49f;
    background: #172124;
    border-radius: 6px;
    padding: 6px 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-left: 3px solid #00e5ff;
  }

  /* Quick Navigation / Modes Strip */
  .nav-strip {
    width: 100%;
    max-width: 960px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    flex-wrap: wrap;
    gap: 8px;
  }
  .game-toggle-group {
    display: flex;
    gap: 5px;
    background: #161c1e;
    padding: 3px 5px;
    border-radius: 8px;
    border: 1px solid #2e393b;
  }
  .game-btn {
    background: transparent;
    border: none;
    color: #8b9ea0;
    padding: 5px 12px;
    border-radius: 6px;
    font-size: 0.68rem;
    font-weight: 800;
    cursor: pointer;
    transition: all 0.12s ease;
    display: flex;
    align-items: center;
    gap: 5px;
  }
  .game-btn:hover { color: #fff; background: rgba(255,255,255,0.06); }
  .game-btn.active {
    background: var(--accent);
    color: #172e24;
    font-weight: 900;
    box-shadow: 0 0 10px var(--accent-glow);
  }
  .game-btn.tour-btn.active {
    background: #a55eea;
    color: #fff;
    box-shadow: 0 0 10px rgba(165, 94, 234, 0.6);
  }

  .mode-indicator {
    display: flex;
    gap: 3px;
    background: #161c1e;
    padding: 3px 5px;
    border-radius: 8px;
    border: 1px solid #2e393b;
    overflow-x: auto;
  }
  .mode-tag {
    font-size: 0.60rem;
    font-weight: 800;
    padding: 4px 8px;
    border-radius: 5px;
    color: #7d9193;
    cursor: pointer;
    transition: all 0.12s ease;
    letter-spacing: 0.3px;
    font-family: var(--font-mono);
  }
  .mode-tag:hover { color: #fff; background: rgba(255,255,255,0.06); }
  .mode-tag.active {
    background: #253632;
    color: var(--accent);
    border: 1px solid #3e5a52;
  }"""

    if old_css_needle not in content:
        raise ValueError("Could not find old_css_needle in tools/build_hardware_template.py")
    content = content.replace(old_css_needle, new_css)

    # 2. Update HTML markup
    old_html_needle = """<!-- Quick Navigation / Game Switcher Strip -->
<div class="nav-strip">
  <div class="game-toggle-group">
    <button class="game-btn active" id="btnGamePacman" onclick="switchActiveGame('pacman')">🟡 PAC-MAN</button>
    <button class="game-btn" id="btnGameClimber" onclick="switchActiveGame('cclimber')">🧗 Crazy Climber</button>
    <button class="game-btn tour-btn" id="btnGameTour" onclick="toggleTourDemo()">🎡 TOUR ALL ROMS</button>
  </div>

  <!-- Mode Indicator Pills -->
  <div class="mode-indicator">
    <div class="mode-tag active" data-mode="arcade">ARCADE</div>
    <div class="mode-tag" data-mode="tour">TOUR DEMO</div>
    <div class="mode-tag" data-mode="demo">DEMO SONGS</div>
    <div class="mode-tag" data-mode="soundboard">SFX PADS (27)</div>
    <div class="mode-tag" data-mode="tracker">TRACKER</div>
    <div class="mode-tag" data-mode="rewind">REWIND</div>
    <div class="mode-tag" data-mode="vector">LISSAJOUS</div>
    <div class="mode-tag" data-mode="glitch">BENDER</div>
  </div>
</div>"""

    new_html = """<!-- Two-Tier Studio Workspace Navigation -->
<div class="studio-nav-bar">
  <button class="studio-tab active" id="tabArcade" data-tab="arcade" onclick="setStudioTab('arcade')">🕹️ ARCADE VAULT (8)</button>
  <button class="studio-tab" id="tabSynth" data-tab="synth" onclick="setStudioTab('synth')">🎹 SYNTH STUDIO (5)</button>
  <button class="studio-tab" id="tabTracker" data-tab="tracker" onclick="setStudioTab('tracker')">🎛️ TRACKER (16-STEP)</button>
  <button class="studio-tab" id="tabDemo" data-tab="demo" onclick="setStudioTab('demo')">🎵 DEMO JUKEBOX</button>
  <button class="studio-tab" id="tabSoundboard" data-tab="soundboard" onclick="setStudioTab('soundboard')">🔊 27 SFX PADS</button>
  <button class="studio-tab" id="tabTour" data-tab="tour" onclick="setStudioTab('tour')">🎡 TOUR DEMO</button>
</div>

<!-- Context Shelves -->
<div class="shelf-wrap">
  <!-- Shelf 1: Playable Arcade Vault (8 Games) -->
  <div class="context-shelf active" id="shelfArcade">
    <div class="shelf-header">
      <span>🕹️ PLAYABLE ARCADE VAULT · CLICK ANY GAME TO LAUNCH INSTANTLY</span>
      <span class="tag">8 ARCADE CLASSICS AVAILABLE</span>
    </div>
    <div class="arcade-gallery-grid">
      <div class="arcade-card active" id="btnGamePacman" data-game="pacman" onclick="switchActiveGame('pacman')">
        <div class="card-emoji">🟡</div>
        <div class="card-name">PAC-MAN</div>
        <div class="card-meta">1980 · Namco</div>
        <div class="card-badge">Z80 + WSG</div>
      </div>
      <div class="arcade-card" id="btnGameClimber" data-game="cclimber" onclick="switchActiveGame('cclimber')">
        <div class="card-emoji">🧗</div>
        <div class="card-name">Crazy Climber</div>
        <div class="card-meta">1980 · Nichibutsu</div>
        <div class="card-badge">Twin-Stick</div>
      </div>
      <div class="arcade-card" id="btnGameGalaga" data-game="galaga" onclick="switchActiveGame('galaga')">
        <div class="card-emoji">🚀</div>
        <div class="card-name">Galaga</div>
        <div class="card-meta">1981 · Namco</div>
        <div class="card-badge">Dual Z80</div>
      </div>
      <div class="arcade-card" id="btnGameDkong" data-game="dkong" onclick="switchActiveGame('dkong')">
        <div class="card-emoji">🦍</div>
        <div class="card-name">Donkey Kong</div>
        <div class="card-meta">1981 · Nintendo</div>
        <div class="card-badge">Platformer</div>
      </div>
      <div class="arcade-card" id="btnGameFrogger" data-game="frogger" onclick="switchActiveGame('frogger')">
        <div class="card-emoji">🐸</div>
        <div class="card-name">Frogger</div>
        <div class="card-meta">1981 · Konami</div>
        <div class="card-badge">Dual AY PSG</div>
      </div>
      <div class="arcade-card" id="btnGameAsteroids" data-game="asteroids" onclick="switchActiveGame('asteroids')">
        <div class="card-emoji">☄️</div>
        <div class="card-name">Asteroids</div>
        <div class="card-meta">1979 · Atari</div>
        <div class="card-badge">Vector CRT</div>
      </div>
      <div class="arcade-card" id="btnGameTempest" data-game="tempest" onclick="switchActiveGame('tempest')">
        <div class="card-emoji">🌀</div>
        <div class="card-name">Tempest</div>
        <div class="card-meta">1981 · Atari</div>
        <div class="card-badge">Color Vector</div>
      </div>
      <div class="arcade-card" id="btnGameGyruss" data-game="gyruss" onclick="switchActiveGame('gyruss')">
        <div class="card-emoji">🌌</div>
        <div class="card-name">Gyruss</div>
        <div class="card-meta">1983 · Konami</div>
        <div class="card-badge">5x PSG 3D</div>
      </div>
    </div>
  </div>

  <!-- Shelf 2: Synth Studio (5 Soundchips + Live Tweak) -->
  <div class="context-shelf" id="shelfSynth">
    <div class="shelf-header">
      <span>🎹 LIVE MULTI-ENGINE SYNTHESIZER · 5 SOUNDCHIPS & VECTOR OSC</span>
      <span class="tag" id="synthStatusTag">POLYPHONIC · 60Hz</span>
    </div>
    <div class="synth-section">
      <div class="synth-row">
        <span class="synth-label">SOUNDCHIP:</span>
        <div class="synth-btn-group">
          <button class="synth-chip-btn active" data-engine="wsg" onclick="setSynthEngine('wsg')">🟡 Namco WSG (3-Voice)</button>
          <button class="synth-chip-btn" data-engine="ay8910" onclick="setSynthEngine('ay8910')">🧗 AY-3-8910 (Chiptune PSG)</button>
          <button class="synth-chip-btn" data-engine="pokey" onclick="setSynthEngine('pokey')">☄️ Atari POKEY (Distortion)</button>
          <button class="synth-chip-btn" data-engine="dac" onclick="setSynthEngine('dac')">🦍 Nintendo DAC (7-bit APU)</button>
          <button class="synth-chip-btn" data-engine="fm" onclick="setSynthEngine('fm')">🎹 M-VAVE FM-1 (6-OP DX)</button>
        </div>
      </div>
      <div class="synth-row">
        <span class="synth-label">ENVELOPE:</span>
        <div class="synth-btn-group">
          <button class="synth-opt-btn synth-env-btn" data-env="pluck" onclick="setEnvelope('pluck')">Pluck</button>
          <button class="synth-opt-btn synth-env-btn active" data-env="lead" onclick="setEnvelope('lead')">Lead</button>
          <button class="synth-opt-btn synth-env-btn" data-env="organ" onclick="setEnvelope('organ')">Organ</button>
          <button class="synth-opt-btn synth-env-btn" data-env="pad" onclick="setEnvelope('pad')">Pad</button>
        </div>
        <span class="synth-label" style="min-width:70px; margin-left:10px;">OCTAVE:</span>
        <div class="synth-btn-group">
          <button class="synth-opt-btn synth-oct-btn" data-oct="-2" onclick="setSynthOctave(-2)">-2</button>
          <button class="synth-opt-btn synth-oct-btn" data-oct="-1" onclick="setSynthOctave(-1)">-1</button>
          <button class="synth-opt-btn synth-oct-btn active" data-oct="0" onclick="setSynthOctave(0)">0</button>
          <button class="synth-opt-btn synth-oct-btn" data-oct="1" onclick="setSynthOctave(1)">+1</button>
          <button class="synth-opt-btn synth-oct-btn" data-oct="2" onclick="setSynthOctave(2)">+2</button>
        </div>
        <div class="synth-btn-group" style="margin-left:auto;">
          <button class="synth-opt-btn" id="synthBtnArp" onclick="toggleArp()">ARP: OFF</button>
          <button class="synth-opt-btn" id="synthBtnLfo" onclick="toggleLfo()">LFO: OFF</button>
        </div>
      </div>
      <div class="synth-hint-bar">
        <span>⚡ <b>PLAY NOTES:</b> Click silicone keys 1-27 below or press QWERTY keys (A-K / W-U). Vector CRT shows real-time live oscilloscope.</span>
        <span><b>SCL</b>=Cycle Engine · <b>ENV</b>=Cycle Envelope</span>
      </div>
    </div>
  </div>

  <!-- Shelf 3: 16-Step Chiptune Tracker -->
  <div class="context-shelf" id="shelfTracker">
    <div class="shelf-header">
      <span>🎛️ 16-STEP CHIPTUNE TRACKER · 4 ARCHITECTURE PATTERNS</span>
      <span class="tag" id="trackerStatusTag">LOOP: STOPPED</span>
    </div>
    <div class="synth-section">
      <div class="synth-row">
        <span class="synth-label">PATTERNS:</span>
        <div class="synth-btn-group" id="trackerPatternList">
          <button class="synth-chip-btn active" data-pat="0" onclick="selectTrackerPattern(0)">01: ARCADE RAT (132 BPM)</button>
          <button class="synth-chip-btn" data-pat="1" onclick="selectTrackerPattern(1)">02: PAC-MANIA DUB (124 BPM)</button>
          <button class="synth-chip-btn" data-pat="2" onclick="selectTrackerPattern(2)">03: GYRUSS SPEED (144 BPM)</button>
          <button class="synth-chip-btn" data-pat="3" onclick="selectTrackerPattern(3)">04: CYBER LABYRINTH (138 BPM)</button>
        </div>
      </div>
      <div class="synth-row">
        <span class="synth-label">CONTROLS:</span>
        <div class="synth-btn-group">
          <button class="synth-opt-btn" id="btnTrackerPlay" onclick="toggleTracker()">▶ PLAY LOOP</button>
          <button class="synth-opt-btn" onclick="cycleTrackerPattern()">⏭ NEXT PATTERN</button>
          <button class="synth-opt-btn" onclick="stepTrackerStep()">⏩ STEP</button>
        </div>
        <span style="font-size:0.62rem; color:#8fa5a0; margin-left:auto; font-family:var(--font-mono);" id="trackerStepDisplay">STEP: <b>01/16</b></span>
      </div>
    </div>
  </div>

  <!-- Shelf 4: Demo Jukebox -->
  <div class="context-shelf" id="shelfDemo">
    <div class="shelf-header">
      <span>🎵 MULTI-ENGINE FULL DEMO SONGS JUKEBOX · 15-TRACK VU METERS</span>
      <span class="tag" id="shelfJukeStatus">STOPPED</span>
    </div>
    <div class="synth-section">
      <div class="synth-row">
        <span class="synth-label">SYMPHONIES:</span>
        <div class="synth-btn-group" id="shelfSongPills">
          <!-- Populated dynamically -->
        </div>
      </div>
      <div class="synth-row">
        <span class="synth-label">PLAYBACK:</span>
        <div class="synth-btn-group">
          <button class="synth-opt-btn" onclick="playDemoSong()">▶ PLAY</button>
          <button class="synth-opt-btn" onclick="pauseDemoSong()">⏹ STOP</button>
          <button class="synth-opt-btn" onclick="stepSong(1)">⏭ NEXT</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Shelf 5: 27 SFX Pads -->
  <div class="context-shelf" id="shelfSoundboard">
    <div class="shelf-header">
      <span>🔊 27 HARDWARE ARCADE SFX PADS · TOUCH SILICONE KEYS 1-27</span>
      <span class="tag">REAL-TIME CHIPTUNE FX</span>
    </div>
    <div class="synth-section">
      <div class="synth-row" style="font-size:0.63rem; color:#8fa5a0;">
        <span>🟡 <b>Keys 1-7:</b> Pac-Man (Waka, Siren, Fruit, Ghost, Death)</span> · 
        <span>🧗 <b>Keys 8-12:</b> Galaga & Climber (Tract, Dive, Capture)</span> · 
        <span>🦍 <b>Keys 13-20:</b> Donkey Kong & Mario</span> · 
        <span>☄️ <b>Keys 21-27:</b> Vector & Warp</span>
      </div>
    </div>
  </div>

  <!-- Shelf 6: Tour All ROMs -->
  <div class="context-shelf" id="shelfTour">
    <div class="shelf-header">
      <span>🎡 ATTRACT TOUR DEMO · CYCLING ALL 8 INSTALLED ARCADE ENGINES</span>
      <span class="tag">AUTO-ROTATING AT 60 FPS</span>
    </div>
    <div class="synth-section">
      <div class="synth-row">
        <span class="synth-label">CONTROLS:</span>
        <div class="synth-btn-group">
          <button class="synth-opt-btn" onclick="prevTourGame()">◀ PREV GAME (P)</button>
          <button class="synth-opt-btn" onclick="nextTourGame()">▶ NEXT GAME (N)</button>
          <button class="synth-opt-btn" style="background:var(--accent); color:#172e24; font-weight:900;" onclick="launchCurrentTourGame()">⚡ PLAY CURRENT GAME (SPACE)</button>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Secondary Navigation & Mode Indicators -->
<div class="nav-strip" style="margin-bottom: 8px;">
  <div class="mode-indicator" style="width: 100%; justify-content: center;">
    <div class="mode-tag active" data-mode="arcade">ARCADE</div>
    <div class="mode-tag" data-mode="synth">SYNTH STUDIO</div>
    <div class="mode-tag" data-mode="tracker">TRACKER</div>
    <div class="mode-tag" data-mode="demo">DEMO SONGS</div>
    <div class="mode-tag" data-mode="soundboard">SFX PADS (27)</div>
    <div class="mode-tag" data-mode="tour">TOUR DEMO</div>
    <div class="mode-tag" data-mode="rewind">REWIND</div>
    <div class="mode-tag" data-mode="vector">LISSAJOUS</div>
    <div class="mode-tag" data-mode="glitch">BENDER</div>
  </div>
</div>"""

    if old_html_needle not in content:
        raise ValueError("Could not find old_html_needle in tools/build_hardware_template.py")
    content = content.replace(old_html_needle, new_html)

    # 3. Update Arcade Render Block
    old_arcade_render_block = """    old_arcade_render_block = \"\"\"    if (currentMode === 'rewind') {
      ctx.fillStyle = '#ff3344';
      ctx.font = 'bold 12px monospace';
      ctx.fillText('◄◄ REWINDING (HOLD KEY)', 12, 22);
    }
  } else if (currentMode === 'demo') {\"\"\"

    new_arcade_render_block = \"\"\"    if (currentMode === 'rewind') {
      ctx.fillStyle = '#ff3344';
      ctx.font = 'bold 12px monospace';
      ctx.fillText('◄◄ REWINDING (HOLD KEY)', 12, 22);
    }
    if (crtScanlines) drawScanlines();
  } else if (currentMode === 'demo') {\"\"\"
    script_body = script_body.replace(old_arcade_render_block, new_arcade_render_block)"""

    new_arcade_render_block_code = """    old_arcade_render_block = \"\"\"  // Render Display
  if (currentMode === 'arcade' || currentMode === 'rewind' || currentMode === 'glitch') {
    if (activeGame === 'cclimber') {
      renderCrazyClimber();
    } else {
      renderArcadeFrame();
    }
    if (currentMode === 'rewind') {
      ctx.fillStyle = '#ff3344';
      ctx.font = 'bold 12px monospace';
      ctx.fillText('◄◄ REWINDING (HOLD KEY)', 12, 22);
    }
  } else if (currentMode === 'demo') {\"\"\"

    new_arcade_render_block = \"\"\"  // Render Display across all 8 arcade games, synth oscilloscope, tracker, etc.
  if (currentMode === 'arcade' || currentMode === 'rewind' || currentMode === 'glitch') {
    if (activeGame === 'pacman') {
      renderArcadeFrame();
    } else if (activeGame === 'cclimber') {
      renderCrazyClimber();
    } else if (activeGame === 'galaga') {
      renderGalagaTour(animTick);
    } else if (activeGame === 'dkong') {
      renderDonkeyKongTour(animTick);
    } else if (activeGame === 'frogger') {
      renderFroggerTour(animTick);
    } else if (activeGame === 'asteroids') {
      renderAsteroidsTour(animTick);
    } else if (activeGame === 'tempest') {
      renderTempestTour(animTick);
    } else if (activeGame === 'gyruss') {
      renderGyrussTour(animTick);
    } else {
      renderArcadeFrame();
    }
    if (currentMode === 'rewind') {
      ctx.fillStyle = '#ff3344';
      ctx.font = 'bold 12px monospace';
      ctx.fillText('◄◄ REWINDING (HOLD KEY)', 12, 22);
    }
    if (crtScanlines) drawScanlines();
  } else if (currentMode === 'synth') {
    renderSynthOscilloscope();
  } else if (currentMode === 'demo') {\"\"\"
    script_body = script_body.replace(old_arcade_render_block, new_arcade_render_block)"""

    if old_arcade_render_block not in content:
        raise ValueError("Could not find old_arcade_render_block in tools/build_hardware_template.py")
    content = content.replace(old_arcade_render_block, new_arcade_render_block_code)

    # 4. Update switchActiveGame implementation
    old_switch_target = """function switchActiveGame(gameId) {
  initAudio();
  // FIRST: stop current game and clear screen
  stopCurrentGame();

  activeGame = gameId;
  currentMode = 'arcade';
  document.querySelectorAll('.mode-tag').forEach(t => t.classList.toggle('active', t.dataset.mode === 'arcade'));
  const btnPac = document.getElementById('btnGamePacman');
  const btnClimb = document.getElementById('btnGameClimber');
  const btnTour = document.getElementById('btnGameTour') || document.getElementById('btnTourAllRoms');
  if (btnPac) btnPac.classList.toggle('active', gameId === 'pacman');
  if (btnClimb) btnClimb.classList.toggle('active', gameId === 'cclimber');
  if (btnTour) btnTour.classList.remove('active');

  // Sync Select encoder if in gameList
  if (typeof gameList !== 'undefined' && typeof currentGameIdx !== 'undefined') {
    const idx = gameList.indexOf(gameId);
    if (idx !== -1) {
      currentGameIdx = idx;
      const encSelect = document.getElementById('encSelect');
      if (encSelect && encSelect.style && encSelect.style.setProperty) {
        encSelect.style.setProperty('--angle', `${(currentGameIdx / gameList.length * 270) - 135}deg`);
      }
    }
  }

  if (gameId === 'cclimber') {
    document.getElementById('engineStatus').innerHTML = 'CRAZY CLIMBER: <b>1980 NICHIBUTSU Z80 + AY-3-8910</b> (Twin-Stick)';
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● CRAZY CLIMBER (TWIN-STICK)';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Twin-Stick: <b>W/S</b> (Left Arm) · <b>▲/▼</b> (Right Arm) · <b>A/D</b> (Col) · or Tap Screen Quadrants';
    climberState.floor = 42;
    climberState.score = 14850;
    climberState.animTick = 0;
    renderCrazyClimber();
  } else {
    document.getElementById('engineStatus').textContent = 'PAC-MAN (60 FPS Z80 + WSG)';
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● PAC-MAN ACTIVE';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Controls: <b>WASD</b> or <b>Arrow Keys</b> or <b>On-Screen D-Pad</b>';
    ensurePastBoot();
    renderArcadeFrame();
  }
}"""

    new_switch_impl = """function switchActiveGame(gameId) {
  initAudio();
  // FIRST: stop current game and clear screen
  stopCurrentGame();

  activeGame = gameId;
  currentMode = 'arcade';
  currentStudioTab = 'arcade';

  // Sync studio tabs & shelves
  document.querySelectorAll('.studio-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === 'arcade'));
  document.querySelectorAll('.context-shelf').forEach(s => s.classList.remove('active'));
  const shelfArcade = document.getElementById('shelfArcade');
  if (shelfArcade) shelfArcade.classList.add('active');

  // Sync mode tags
  document.querySelectorAll('.mode-tag').forEach(t => t.classList.toggle('active', t.dataset.mode === 'arcade'));

  // Sync arcade gallery cards
  document.querySelectorAll('.arcade-card').forEach(c => c.classList.toggle('active', c.dataset.game === gameId));
  const btnPac = document.getElementById('btnGamePacman');
  const btnClimb = document.getElementById('btnGameClimber');
  const btnTour = document.getElementById('btnGameTour');
  if (btnPac) btnPac.classList.toggle('active', gameId === 'pacman');
  if (btnClimb) btnClimb.classList.toggle('active', gameId === 'cclimber');
  if (btnTour) btnTour.classList.remove('active');

  // Sync Select encoder if in gameList
  if (typeof gameList !== 'undefined' && typeof currentGameIdx !== 'undefined') {
    const idx = gameList.indexOf(gameId);
    if (idx !== -1) {
      currentGameIdx = idx;
      const encSelect = document.getElementById('encSelect');
      if (encSelect && encSelect.style && encSelect.style.setProperty) {
        encSelect.style.setProperty('--angle', `${(currentGameIdx / gameList.length * 270) - 135}deg`);
      }
    }
  }

  if (gameId === 'cclimber') {
    document.getElementById('engineStatus').innerHTML = 'CRAZY CLIMBER: <b>1980 NICHIBUTSU Z80 + AY-3-8910</b> (Twin-Stick)';
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● CRAZY CLIMBER (TWIN-STICK)';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Twin-Stick: <b>W/S</b> (Left Arm) · <b>▲/▼</b> (Right Arm) · <b>A/D</b> (Col) · or Tap Screen Quadrants';
    climberState.floor = 42;
    climberState.score = 14850;
    climberState.animTick = 0;
    renderCrazyClimber();
  } else if (gameId === 'galaga') {
    document.getElementById('engineStatus').innerHTML = 'GALAGA: <b>1981 NAMCO DUAL Z80 + 3-VOICE WSG</b> (Space Shooter)';
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● GALAGA (STAGE 03)';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Fighter: <b>A/D</b> or <b>◀/▶</b> (Steer) · <b>Space / 1 / Start</b> (Dual Laser) · Tap Screen Sides';
    renderGalagaTour(0);
  } else if (gameId === 'dkong') {
    document.getElementById('engineStatus').innerHTML = 'DONKEY KONG: <b>1981 NINTENDO Z80 + 7-BIT DAC</b> (Platformer)';
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● DONKEY KONG (25M GIRDERS)';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Jumpman: <b>A/D</b> (Run) · <b>W / Space / Start</b> (Jump Barrels) · <b>S</b> (Hammer)';
    renderDonkeyKongTour(0);
  } else if (gameId === 'frogger') {
    document.getElementById('engineStatus').innerHTML = 'FROGGER: <b>1981 KONAMI Z80 + DUAL AY-3-8910</b> (Traffic Hop)';
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● FROGGER (RIVER & ROAD)';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Frog: <b>WASD</b> or <b>Arrow Keys</b> or <b>D-Pad</b> or <b>Screen Quadrants</b> to Hop';
    renderFroggerTour(0);
  } else if (gameId === 'asteroids') {
    document.getElementById('engineStatus').innerHTML = 'ASTEROIDS: <b>1979 ATARI QUADRASCAN 6502 + POKEY</b> (Vector CRT)';
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● ASTEROIDS (SECTOR 4)';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Ship: <b>A/D</b> (Rotate) · <b>W</b> (Thrust) · <b>Space / 1</b> (Fire) · <b>S</b> (Hyperspace)';
    renderAsteroidsTour(0);
  } else if (gameId === 'tempest') {
    document.getElementById('engineStatus').innerHTML = 'TEMPEST: <b>1981 ATARI COLOR VECTOR + POKEY</b> (Tube Shooter)';
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● TEMPEST (TUBE 09)';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Blaster: <b>A/D</b> (Rotary Spin) · <b>Space / 1</b> (Particle Fire) · <b>W</b> (Superzapper)';
    renderTempestTour(0);
  } else if (gameId === 'gyruss') {
    document.getElementById('engineStatus').innerHTML = 'GYRUSS: <b>1983 KONAMI 5x PSG BAROQUE SYMPHONY</b> (3D Warp)';
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● GYRUSS (WARP TO NEPTUNE)';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Starfighter: <b>A/D</b> or <b>◀/▶</b> (360° Orbit) · <b>Space / 1 / Start</b> (Twin Cannons)';
    renderGyrussTour(0);
  } else {
    activeGame = 'pacman';
    document.getElementById('engineStatus').textContent = 'PAC-MAN (60 FPS Z80 + WSG)';
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● PAC-MAN ACTIVE';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Controls: <b>WASD</b> or <b>Arrow Keys</b> or <b>On-Screen D-Pad</b>';
    ensurePastBoot();
    renderArcadeFrame();
  }
}"""

    if old_switch_target not in content:
        raise ValueError("Could not find old_switch_target in tools/build_hardware_template.py")
    content = content.replace(old_switch_target, new_switch_impl)

    # 5. In setMode, add full synchronization of studio tabs, synth UI, etc.
    old_set_mode_needle = """    script_body = script_body.replace(
        "function setMode(mode) {\\n  currentMode = mode;",
        "function setMode(mode) {\\n  if (currentMode !== mode) stopCurrentGame();\\n  currentMode = mode;"
    )"""

    new_set_mode_replacement = """    old_set_mode = \"\"\"function setMode(mode) {
  currentMode = mode;
  document.querySelectorAll('.mode-tag').forEach(t => t.classList.toggle('active', t.dataset.mode === mode));
  document.getElementById('jukeboxPanel').style.display = (mode === 'demo') ? 'flex' : 'none';
  const tourBtn = document.getElementById('btnGameTour');
  if (tourBtn) tourBtn.classList.toggle('active', mode === 'tour');
  updateKeyLabels();

  if (mode === 'tour') {
    tourState.active = true;
    tourState.frameInGame = 0;
    document.getElementById('engineStatus').innerHTML = 'ARCADE TOUR DEMO: <b>CYCLING ALL INSTALLED ROMS</b>';
    document.getElementById('hudStatus').textContent = '● TOUR DEMO ACTIVE';
  } else {
    tourState.active = false;
    document.getElementById('engineStatus').textContent = 'PAC-MAN (60 FPS Z80 + WSG)';
    document.getElementById('hudStatus').textContent = '● ATTRACT MODE';
  }
}\"\"\"

    new_set_mode = \"\"\"let currentStudioTab = 'arcade';

function setStudioTab(tab) {
  initAudio();
  currentStudioTab = tab;
  document.querySelectorAll('.studio-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
  document.querySelectorAll('.context-shelf').forEach(s => s.classList.remove('active'));
  const targetShelf = document.getElementById('shelf' + tab.charAt(0).toUpperCase() + tab.slice(1));
  if (targetShelf) targetShelf.classList.add('active');

  if (tab === 'arcade') {
    if (currentMode !== 'arcade') switchActiveGame(activeGame || 'pacman');
  } else if (tab === 'synth') {
    setMode('synth');
  } else if (tab === 'tracker') {
    setMode('tracker');
  } else if (tab === 'demo') {
    setMode('demo');
  } else if (tab === 'soundboard') {
    setMode('soundboard');
  } else if (tab === 'tour') {
    setMode('tour');
  }
}

function setMode(mode) {
  if (currentMode !== mode) stopCurrentGame();
  currentMode = mode;
  document.querySelectorAll('.mode-tag').forEach(t => t.classList.toggle('active', t.dataset.mode === mode));
  document.querySelectorAll('.studio-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === mode));
  document.querySelectorAll('.context-shelf').forEach(s => s.classList.remove('active'));
  const targetShelf = document.getElementById('shelf' + mode.charAt(0).toUpperCase() + mode.slice(1));
  if (targetShelf) targetShelf.classList.add('active');

  const jukePanel = document.getElementById('jukeboxPanel');
  if (jukePanel) jukePanel.style.display = (mode === 'demo') ? 'flex' : 'none';

  const tourBtn = document.getElementById('btnGameTour');
  if (tourBtn) tourBtn.classList.toggle('active', mode === 'tour');
  updateKeyLabels();

  if (mode === 'tour') {
    tourState.active = true;
    tourState.frameInGame = 0;
    document.getElementById('engineStatus').innerHTML = 'ARCADE TOUR DEMO: <b>CYCLING ALL INSTALLED ROMS</b>';
    document.getElementById('hudStatus').textContent = '● TOUR DEMO ACTIVE';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Tour: <b>Space/Enter</b>=Play Live · <b>N/D/▶</b>=Next Game · <b>P/A/◀</b>=Prev Game';
  } else if (mode === 'synth') {
    tourState.active = false;
    document.getElementById('engineStatus').innerHTML = `SYNTH STUDIO: <b>${liveSynth.engineNames[liveSynth.currentEngine]}</b>`;
    document.getElementById('hudStatus').textContent = `● SYNTH: ${liveSynth.currentEngine.toUpperCase()}`;
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Live Play: <b>Silicone Keys 1-27</b> or <b>QWERTY</b> · <b>SCL</b>=Chip · <b>ENV</b>=Envelope · <b>OCT-/+</b>';
    updateSynthUI();
  } else if (mode === 'tracker') {
    tourState.active = false;
    const pat = trackerEngine.patterns[trackerEngine.currentPatternIdx];
    document.getElementById('engineStatus').innerHTML = `16-STEP CHIPTUNE TRACKER: <b>${pat ? pat.name : 'ACTIVE'}</b>`;
    document.getElementById('hudStatus').textContent = '● TRACKER SEQUENCER';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Sequencer: <b>Space/PLAY</b>=Toggle Loop · <b>SCL</b>=Next Pattern · <b>Keys 1-16</b>=Audition';
    updateTrackerUI();
  } else if (mode === 'demo') {
    tourState.active = false;
    document.getElementById('engineStatus').innerHTML = 'DEMO JUKEBOX: <b>15-TRACK MULTI-VOICE SYMPHONIES</b>';
    document.getElementById('hudStatus').textContent = '● DEMO JUKEBOX';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Jukebox: <b>Space/PLAY</b>=Start/Stop Song · <b>PRESETS Knob</b>=Select Symphony';
  } else if (mode === 'soundboard') {
    tourState.active = false;
    document.getElementById('engineStatus').innerHTML = 'ARCADE SOUNDBOARD: <b>27 HARDWARE SFX PADS</b>';
    document.getElementById('hudStatus').textContent = '● SFX PADS ACTIVE';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Soundboard: <b>Click Any Silicone Key</b> to Trigger Chiptune FX';
  } else if (mode === 'arcade') {
    tourState.active = false;
    switchActiveGame(activeGame || 'pacman');
  } else {
    tourState.active = false;
  }
}\"\"\"
    script_body = script_body.replace(old_set_mode, new_set_mode)"""

    if old_set_mode_needle not in content:
        raise ValueError("Could not find old_set_mode_needle in tools/build_hardware_template.py")
    content = content.replace(old_set_mode_needle, new_set_mode_replacement)

    # 6. Update MODES list in script
    content = content.replace(
        "const MODES = ['arcade', 'tour', 'demo', 'soundboard', 'tracker', 'rewind', 'vector', 'glitch'];",
        "const MODES = ['arcade', 'synth', 'tracker', 'demo', 'soundboard', 'tour', 'rewind', 'vector', 'glitch'];"
    )

    # 7. Add renderSynthOscilloscope and helpers in additional_bindings
    synth_helpers = """
// =========================================================================
// SYNTH STUDIO: VECTOR CRT OSCILLOSCOPE & SOUNDCHIP CONTROLS
// =========================================================================
function renderSynthOscilloscope() {
  animTick++;
  if (!ctx) return;
  if (ctx.save) ctx.save();
  ctx.fillStyle = '#060a08';
  ctx.fillRect(0, 0, 240, 240);

  // CRT Phosphor Reticle Grid
  if (ctx.beginPath) {
    ctx.strokeStyle = 'rgba(0, 255, 102, 0.12)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let x = 20; x < 240; x += 20) { ctx.moveTo(x, 0); ctx.lineTo(x, 240); }
    for (let y = 20; y < 240; y += 20) { ctx.moveTo(0, y); ctx.lineTo(240, y); }
    ctx.stroke();

    // Center axes
    ctx.strokeStyle = 'rgba(0, 255, 102, 0.28)';
    ctx.beginPath();
    ctx.moveTo(120, 0); ctx.lineTo(120, 240);
    ctx.moveTo(0, 120); ctx.lineTo(240, 120);
    ctx.stroke();
  }

  // Header info
  if (ctx.fillText) {
    ctx.fillStyle = '#aae4c8';
    ctx.font = 'bold 11px monospace';
    ctx.fillText('SYNTH STUDIO · 60Hz', 12, 20);

    const engName = (liveSynth && liveSynth.engineNames) ? (liveSynth.engineNames[liveSynth.currentEngine] || 'WSG') : 'WSG';
    ctx.fillStyle = '#00ff66';
    ctx.font = 'bold 9px monospace';
    ctx.fillText('[' + (liveSynth ? liveSynth.currentEngine.toUpperCase() : 'WSG') + '] ' + engName.slice(0, 20), 12, 34);

    ctx.fillStyle = '#8fa59b';
    ctx.font = '8px monospace';
    const envStr = liveSynth ? liveSynth.envelope.toUpperCase() : 'LEAD';
    const octStr = (liveSynth && liveSynth.octaveOffset >= 0 ? '+' : '') + (liveSynth ? liveSynth.octaveOffset : 0);
    const lfoStr = (liveSynth && liveSynth.lfo && liveSynth.lfo.active) ? 'ON' : 'OFF';
    const arpStr = (liveSynth && liveSynth.arp && liveSynth.arp.active) ? 'ON' : 'OFF';
    ctx.fillText('ENV: ' + envStr + ' · OCT: ' + octStr + ' · LFO: ' + lfoStr + ' · ARP: ' + arpStr, 12, 47);
  }

  // Waveform rendering
  const isVoiceActive = (liveSynth && ((liveSynth.activeVoices && liveSynth.activeVoices.size > 0) || (liveSynth.arp && liveSynth.arp.active && liveSynth.arp.heldKeys.length > 0)));
  if (ctx.beginPath) {
    ctx.strokeStyle = isVoiceActive ? '#00ffaa' : 'rgba(0, 229, 255, 0.6)';
    ctx.shadowColor = isVoiceActive ? '#00ffaa' : '#00e5ff';
    ctx.shadowBlur = isVoiceActive ? 8 : 4;
    ctx.lineWidth = 2;
    ctx.beginPath();

    const numSamples = 216;
    const t = animTick * 0.08;
    const eng = liveSynth ? liveSynth.currentEngine : 'wsg';

    for (let i = 0; i < numSamples; i++) {
      const x = 12 + i;
      let y = 125;
      const progress = i / numSamples;

      if (!isVoiceActive) {
        y += Math.sin(progress * Math.PI * 4 + t) * 6 + Math.sin(progress * Math.PI * 12 + t * 2) * 2;
      } else {
        if (eng === 'wsg') {
          const step = Math.floor((i + animTick * 3) / 6) % 32;
          const waveVal = (typeof WSG_WAVETABLES !== 'undefined' && WSG_WAVETABLES[0]) ? (WSG_WAVETABLES[0][step] - 7.5) : Math.sin(i * 0.2) * 7;
          y += waveVal * 5.2;
        } else if (eng === 'ay8910') {
          const cycle = ((i * 4 + animTick * 8) % 64) < 32 ? 1 : -1;
          y += cycle * 38;
        } else if (eng === 'pokey') {
          const p1 = ((i * 5 + animTick * 6) % 48) < 24 ? 1 : -1;
          const p2 = ((i * 7 + animTick * 4) % 32) < 16 ? 0.7 : -0.7;
          y += (p1 + p2) * 24;
        } else if (eng === 'dac') {
          const raw = Math.sin(progress * Math.PI * 8 + t * 4);
          const quantized = Math.round(raw * 7) / 7;
          y += quantized * 40;
        } else {
          const mod = Math.sin(progress * Math.PI * 16 + t * 6);
          const carrier = Math.sin(progress * Math.PI * 6 + t * 3 + mod * 2.2);
          y += carrier * 42;
        }
      }

      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.shadowBlur = 0;
  }

  // Active Voices Indicators
  if (ctx.fillText && liveSynth) {
    ctx.fillStyle = '#667777';
    ctx.font = '8px monospace';
    ctx.fillText('VOICES: ', 12, 204);
    const voiceEntries = liveSynth.activeVoices ? Array.from(liveSynth.activeVoices.keys()) : [];
    for (let v = 0; v < 8; v++) {
      const vx = 56 + v * 20;
      const active = v < voiceEntries.length || (liveSynth.arp && liveSynth.arp.active && v < liveSynth.arp.heldKeys.length);
      ctx.fillStyle = active ? '#00ff66' : '#182420';
      ctx.fillRect(vx, 196, 14, 10);
      ctx.strokeStyle = '#324a40';
      ctx.strokeRect(vx, 196, 14, 10);
      if (active) {
        const k = voiceEntries[v] !== undefined ? voiceEntries[v] : (liveSynth.arp ? (liveSynth.arp.heldKeys[v] || 0) : 0);
        ctx.fillStyle = '#000';
        ctx.font = 'bold 7px monospace';
        ctx.fillText(noteNames[k % 12], vx + 2, 204);
      }
    }

    ctx.fillStyle = '#8fa5a0';
    ctx.font = '8px monospace';
    ctx.fillText('PLAY NOTES: SILICONE KEYS 1-27 OR QWERTY', 12, 226);
  }

  if (crtScanlines && typeof drawScanlines === 'function') drawScanlines();
  if (ctx.restore) ctx.restore();
}

function setSynthEngine(engineId) {
  initAudio();
  if (!liveSynth) return;
  if (liveSynth.engineOrder.includes(engineId)) {
    liveSynth.currentEngine = engineId;
    const name = liveSynth.engineNames[liveSynth.currentEngine];
    const status = document.getElementById('engineStatus');
    if (status) status.innerHTML = `SYNTH ENGINE: <b>${name}</b>`;
    const hud = document.getElementById('hudStatus');
    if (hud) hud.textContent = `● SYNTH: ${liveSynth.currentEngine.toUpperCase()}`;
    updateSynthUI();
    playStartupChimeMini();
    return name;
  }
}

function setEnvelope(envId) {
  initAudio();
  if (!liveSynth) return;
  liveSynth.envelope = envId;
  const status = document.getElementById('engineStatus');
  if (status) status.innerHTML = `ENVELOPE: <b>${liveSynth.envelope.toUpperCase()}</b>`;
  updateSynthUI();
}

function setSynthOctave(oct) {
  initAudio();
  if (!liveSynth) return;
  liveSynth.octaveOffset = Math.max(-2, Math.min(2, oct));
  const status = document.getElementById('engineStatus');
  if (status) status.innerHTML = `SYNTH OCTAVE: <b>${liveSynth.octaveOffset >= 0 ? '+' : ''}${liveSynth.octaveOffset}</b>`;
  updateSynthUI();
}

function updateSynthUI() {
  if (!liveSynth) return;
  document.querySelectorAll('.synth-chip-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.engine === liveSynth.currentEngine);
  });
  document.querySelectorAll('.synth-env-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.env === liveSynth.envelope);
  });
  document.querySelectorAll('.synth-oct-btn').forEach(btn => {
    btn.classList.toggle('active', parseInt(btn.dataset.oct) === liveSynth.octaveOffset);
  });
  const arpBtn = document.getElementById('synthBtnArp');
  if (arpBtn && liveSynth.arp) {
    arpBtn.classList.toggle('active', liveSynth.arp.active);
    arpBtn.textContent = liveSynth.arp.active ? 'ARP: ON (16th)' : 'ARP: OFF';
  }
  const lfoBtn = document.getElementById('synthBtnLfo');
  if (lfoBtn && liveSynth.lfo) {
    lfoBtn.classList.toggle('active', liveSynth.lfo.active);
    lfoBtn.textContent = liveSynth.lfo.active ? 'LFO: ON (6Hz)' : 'LFO: OFF';
  }
}

function selectTrackerPattern(idx) {
  initAudio();
  if (!trackerEngine || !trackerEngine.patterns) return;
  trackerEngine.currentPatternIdx = (idx + trackerEngine.patterns.length) % trackerEngine.patterns.length;
  updateTrackerUI();
}

function stepTrackerStep() {
  initAudio();
  if (!trackerEngine) return;
  stepTracker();
  updateTrackerUI();
}

function updateTrackerUI() {
  if (!trackerEngine || !trackerEngine.patterns) return;
  const pat = trackerEngine.patterns[trackerEngine.currentPatternIdx];
  const tag = document.getElementById('trackerStatusTag');
  if (tag) tag.textContent = trackerEngine.playing ? `PLAYING (${pat ? pat.bpm : 132} BPM)` : 'LOOP: STOPPED';
  const btn = document.getElementById('btnTrackerPlay');
  if (btn) btn.textContent = trackerEngine.playing ? '⏸ PAUSE LOOP' : '▶ PLAY LOOP';
  const disp = document.getElementById('trackerStepDisplay');
  if (disp) disp.innerHTML = `STEP: <b>${String(trackerEngine.step + 1).padStart(2, '0')}/16</b> · BPM: <b>${pat ? pat.bpm : 132}</b>`;
  document.querySelectorAll('#trackerPatternList .synth-chip-btn').forEach(b => {
    b.classList.toggle('active', parseInt(b.dataset.pat) === trackerEngine.currentPatternIdx);
  });
}
"""

    content = content.replace(
        "// Additional Authentic M-VAVE FM-1 Panel Button & Encoder Handlers",
        synth_helpers + "\n// Additional Authentic M-VAVE FM-1 Panel Button & Encoder Handlers"
    )

    with open("tools/build_hardware_template.py", "w") as f_out:
        f_out.write(content)
    print("Successfully updated tools/build_hardware_template.py!")

if __name__ == "__main__":
    update()
