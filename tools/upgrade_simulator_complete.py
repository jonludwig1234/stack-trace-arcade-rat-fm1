import re

print("=== RUNNING FULL HARDWARE SIMULATOR UPGRADE ===")

with open("tools/build_hardware_template.py", "r") as f:
    content = f.read()

# --------------------------------------------------------------------------
# 1. ADD CSS FOR MISSION CARD, CONTROLLER DECK, AND 2X ZOOM
# --------------------------------------------------------------------------
extra_css = """
  /* 2X CRT Screen Zoom & Modal Focus */
  .screen-bezel.zoomed {
    position: fixed !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) scale(1.85) !important;
    z-index: 10000 !important;
    box-shadow: 0 0 60px rgba(0, 229, 255, 0.65), 0 30px 90px rgba(0,0,0,0.98) !important;
    border: 3px solid var(--cyan-oled) !important;
    transition: transform 0.22s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
  }
  .zoom-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(6, 9, 14, 0.88);
    backdrop-filter: blur(8px);
    z-index: 9999;
  }
  .zoom-overlay.active { display: block; }

  /* Interactive On-Screen Arcade Quick Controller Bar */
  .arcade-controller-deck {
    position: absolute;
    left: 31%;
    top: 42.4%;
    width: 27%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(14, 20, 26, 0.88);
    border: 1px solid rgba(0, 229, 255, 0.2);
    border-radius: 6px;
    padding: 3px 5px;
    gap: 3px;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.7), 0 2px 8px rgba(0,0,0,0.4);
    z-index: 20;
  }
  .ctrl-btn {
    flex: 1;
    background: #1b2329;
    color: #aae4c8;
    border: 1px solid #2e3d46;
    border-radius: 3px;
    font-family: var(--font-mono);
    font-size: 0.58rem;
    font-weight: 800;
    padding: 3px 2px;
    cursor: pointer;
    text-align: center;
    transition: all 0.08s ease-in-out;
    user-select: none;
  }
  .ctrl-btn:hover {
    background: #25333c;
    border-color: var(--cyan-oled);
    color: #fff;
  }
  .ctrl-btn:active, .ctrl-btn.pressed {
    background: var(--accent) !important;
    color: #0b1c14 !important;
    box-shadow: 0 0 10px var(--accent-glow) !important;
    transform: translateY(1px);
  }
  .ctrl-btn.ctrl-action {
    background: #3e1b22;
    color: #ff6b81;
    border-color: #632631;
  }
  .ctrl-btn.ctrl-action:active, .ctrl-btn.ctrl-action.pressed {
    background: #ff4757 !important;
    color: #fff !important;
    box-shadow: 0 0 12px rgba(255, 71, 87, 0.7) !important;
  }
  .ctrl-btn.ctrl-coin {
    background: #3a2e16;
    color: #feca57;
    border-color: #5c471e;
  }
  .ctrl-btn.ctrl-start {
    background: #153423;
    color: #2ed573;
    border-color: #1f5537;
  }
  .ctrl-btn.ctrl-zoom {
    background: #102a36;
    color: #00e5ff;
    border-color: #1b4b60;
  }

  /* Active Arcade Mission & How-To-Play Card */
  .arcade-mission-card {
    margin-top: 10px;
    background: linear-gradient(135deg, rgba(20, 26, 33, 0.95) 0%, rgba(13, 17, 23, 0.95) 100%);
    border: 1px solid rgba(0, 229, 255, 0.22);
    border-radius: 8px;
    padding: 9px 13px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.5);
  }
  .mission-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    padding-bottom: 4px;
  }
  .mission-title {
    color: #f5a623;
    font-weight: 800;
    font-size: 0.80rem;
    letter-spacing: 0.5px;
    font-family: var(--font-mono);
  }
  .mission-badge {
    background: rgba(0, 229, 255, 0.15);
    color: #00e5ff;
    font-size: 0.63rem;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 4px;
    border: 1px solid rgba(0, 229, 255, 0.3);
  }
  .mission-body {
    display: grid;
    grid-template-columns: 1.4fr 1.3fr 1.3fr;
    gap: 12px;
    font-size: 0.67rem;
  }
  .mission-label {
    color: #aae4c8;
    font-weight: 800;
    display: block;
    margin-bottom: 2px;
    font-size: 0.63rem;
  }
  .mission-text {
    color: #c8d6e5;
    line-height: 1.35;
  }
  .mission-text b {
    color: #ffffff;
  }

  /* Pulsing Tour Demo Play Button */
  .tour-play-btn {
    background: linear-gradient(135deg, #f5a623 0%, #ff4757 100%);
    color: #ffffff;
    border: none;
    border-radius: 5px;
    font-weight: 900;
    font-size: 0.75rem;
    padding: 6px 14px;
    cursor: pointer;
    box-shadow: 0 0 10px rgba(245, 166, 35, 0.5);
    transition: all 0.15s;
    animation: tourPulse 1.4s infinite alternate;
  }
  @keyframes tourPulse {
    0% { box-shadow: 0 0 6px rgba(245, 166, 35, 0.5); }
    100% { box-shadow: 0 0 18px rgba(255, 71, 87, 0.85); transform: scale(1.02); }
  }
"""

# Insert extra CSS right before </style>
if "</style>" in content and ".screen-bezel.zoomed" not in content:
    content = content.replace("</style>", extra_css + "\n</style>")
    print("Added CSS styling for Zoom, Mission Card, and Controller Deck.")

# --------------------------------------------------------------------------
# 2. INSERT MISSION CARD INTO SHELF ARCADE
# --------------------------------------------------------------------------
mission_card_html = """
    <!-- Active Arcade Mission & How-To-Play Card -->
    <div class="arcade-mission-card" id="arcadeMissionCard">
      <div class="mission-header">
        <span class="mission-title" id="missionTitle">PAC-MAN (1980 NAMCO)</span>
        <span class="mission-badge" id="missionBadge">MAZE CHASE · BARE-METAL Z80 + WSG</span>
      </div>
      <div class="mission-body">
        <div class="mission-col">
          <span class="mission-label">🎯 OBJECTIVE:</span>
          <span class="mission-text" id="missionObjective">Navigate the maze, eat all 244 dots and 4 energizers! Avoid Blinky, Pinky, Inky & Clyde.</span>
        </div>
        <div class="mission-col">
          <span class="mission-label">🕹️ CONTROLS:</span>
          <span class="mission-text" id="missionControls"><b>WASD</b> or <b>Arrow Keys</b> or <b>Screen Quadrants</b> to Turn · <b>1</b> (Coin) · <b>5</b> (1P Start) · <b>Space</b> (Quick Play)</span>
        </div>
        <div class="mission-col">
          <span class="mission-label">💡 PRO TIP:</span>
          <span class="mission-text" id="missionTip">Eat power pellets to turn ghosts blue and gobble them for 200, 400, 800, 1600 bonus points!</span>
        </div>
      </div>
    </div>
"""

old_end_shelf_arcade = """      <div class="arcade-card" id="btnGameGyruss" data-game="gyruss" onclick="switchActiveGame('gyruss')">
        <div class="card-emoji">🌌</div>
        <div class="card-name">Gyruss</div>
        <div class="card-meta">1983 · Konami</div>
        <div class="card-badge">5x PSG 3D</div>
      </div>
    </div>
  </div>"""

new_end_shelf_arcade = """      <div class="arcade-card" id="btnGameGyruss" data-game="gyruss" onclick="switchActiveGame('gyruss')">
        <div class="card-emoji">🌌</div>
        <div class="card-name">Gyruss</div>
        <div class="card-meta">1983 · Konami</div>
        <div class="card-badge">5x PSG 3D</div>
      </div>
    </div>
""" + mission_card_html + """  </div>"""

if old_end_shelf_arcade in content and "arcadeMissionCard" not in content:
    content = content.replace(old_end_shelf_arcade, new_end_shelf_arcade)
    print("Added arcadeMissionCard to shelfArcade.")

# --------------------------------------------------------------------------
# 3. UPGRADE SHELF DEMO PLAYBACK CONTROLS
# --------------------------------------------------------------------------
old_shelf_demo_playback = """      <div class="synth-row">
        <span class="synth-label">PLAYBACK:</span>
        <div class="synth-btn-group">
          <button class="synth-opt-btn" onclick="playDemoSong()">▶ PLAY</button>
          <button class="synth-opt-btn" onclick="pauseDemoSong()">⏹ STOP</button>
          <button class="synth-opt-btn" onclick="stepSong(1)">⏭ NEXT</button>
        </div>
      </div>"""

new_shelf_demo_playback = """      <div class="synth-row">
        <span class="synth-label">PLAYBACK:</span>
        <div class="synth-btn-group">
          <button class="synth-opt-btn" id="btnShelfPlay" onclick="playDemoSong()">▶ PLAY</button>
          <button class="synth-opt-btn" id="btnShelfPause" onclick="pauseDemoSong()">⏸ PAUSE</button>
          <button class="synth-opt-btn" id="btnShelfStop" onclick="stopDemoSong()">⏹ STOP</button>
          <button class="synth-opt-btn" onclick="stepSong(-1)">⏮ PREV</button>
          <button class="synth-opt-btn" onclick="stepSong(1)">⏭ NEXT</button>
        </div>
      </div>"""

if old_shelf_demo_playback in content:
    content = content.replace(old_shelf_demo_playback, new_shelf_demo_playback)
    print("Upgraded playback buttons in shelfDemo.")

# --------------------------------------------------------------------------
# 4. UPGRADE SHELF TOUR CONTROLS
# --------------------------------------------------------------------------
old_shelf_tour_controls = """      <div class="synth-row">
        <span class="synth-label">CONTROLS:</span>
        <div class="synth-btn-group">
          <button class="synth-opt-btn" onclick="prevTourGame()">◀ PREV GAME (P)</button>
          <button class="synth-opt-btn" onclick="nextTourGame()">▶ NEXT GAME (N)</button>
          <button class="synth-opt-btn" style="background:var(--accent); color:#172e24; font-weight:900;" onclick="launchCurrentTourGame()">⚡ PLAY CURRENT GAME (SPACE)</button>
        </div>
      </div>"""

new_shelf_tour_controls = """      <div class="synth-row">
        <span class="synth-label">TOUR CONTROLS:</span>
        <div class="synth-btn-group">
          <button class="synth-opt-btn" onclick="prevTourGame()">◀ PREV GAME (P)</button>
          <button class="synth-opt-btn" onclick="nextTourGame()">▶ NEXT GAME (N)</button>
          <button class="synth-opt-btn" id="btnTourPause" onclick="toggleTourDemo()">⏸ PAUSE TOUR</button>
          <button class="tour-play-btn" onclick="launchCurrentTourGame()">⚡ PLAY CURRENT GAME (SPACE)</button>
        </div>
      </div>"""

if old_shelf_tour_controls in content:
    content = content.replace(old_shelf_tour_controls, new_shelf_tour_controls)
    print("Upgraded tour controls in shelfTour.")

# --------------------------------------------------------------------------
# 5. INSERT CONTROLLER DECK & ZOOM OVERLAY BELOW SCREEN
# --------------------------------------------------------------------------
controller_deck_html = """
  <!-- On-Screen Arcade Quick Controller Bar (Mouse, Touch & Visual Key Feedback) -->
  <div class="arcade-controller-deck" id="arcadeControllerDeck">
    <button class="ctrl-btn" id="ctrlBtnLeft" title="Left (A / ◀)">◀ LEFT</button>
    <button class="ctrl-btn" id="ctrlBtnUp" title="Up / Jump (W / ▲)">▲ UP</button>
    <button class="ctrl-btn" id="ctrlBtnDown" title="Down / Climb (S / ▼)">▼ DOWN</button>
    <button class="ctrl-btn" id="ctrlBtnRight" title="Right (D / ▶)">▶ RIGHT</button>
    <button class="ctrl-btn ctrl-action" id="ctrlBtnFire" title="Action / Fire / Jump (Space)">🔴 ACTION</button>
    <button class="ctrl-btn ctrl-coin" id="ctrlBtnCoin" title="Insert Coin (1 / C)">🪙 COIN</button>
    <button class="ctrl-btn ctrl-start" id="ctrlBtnStart" title="Start Game (5 / Enter)">▶ START</button>
    <button class="ctrl-btn ctrl-zoom" id="ctrlBtnZoom" onclick="toggleScreenZoom()" title="Toggle 2X Screen Zoom (Z)">🔍 ZOOM</button>
  </div>
"""

old_caption = """  <div class="screen-caption">
    <span id="hudStatus">● ATTRACT MODE</span>
    <span id="hudCredits">CREDITS: 0</span>
    <span id="crtStatus" style="cursor:pointer;" title="Click or Press K to toggle scanlines">SCANLINES: ON</span>
  </div>"""

new_caption = """  <div class="screen-caption">
    <span id="hudStatus">● ATTRACT MODE</span>
    <span id="hudCredits">CREDITS: 0</span>
    <span id="crtStatus" style="cursor:pointer;" title="Click or Press K to toggle scanlines">SCANLINES: ON</span>
    <span id="btnZoomScreen" style="cursor:pointer; color:var(--cyan-oled); margin-left:6px; font-weight:800;" onclick="toggleScreenZoom()" title="Press Z or click to toggle 2X zoom">🔍 ZOOM 2X</span>
  </div>
""" + controller_deck_html

if old_caption in content and "arcadeControllerDeck" not in content:
    content = content.replace(old_caption, new_caption)
    print("Added arcadeControllerDeck and btnZoomScreen.")

# Add zoom overlay right before body close
if '<div class="zoom-overlay"' not in content:
    content = content.replace("</body>", '<div class="zoom-overlay" id="zoomOverlay" onclick="toggleScreenZoom()"></div>\n</body>')
    print("Added zoomOverlay element.")

with open("tools/build_hardware_template.py", "w") as f:
    f.write(content)

print("Template markup updated successfully.")
