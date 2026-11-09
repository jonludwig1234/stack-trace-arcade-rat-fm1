import re

with open("tools/build_hardware_template.py", "r") as f:
    code = f.read()

# 1. In new_arcade_frame, remove internal drawScanlines call (scanlines handled in mainLoop)
code = code.replace(
    "    ctx.drawImage(osCanvas, 0, 0, 224, 288, 8, 0, 224, 240);\n    if (crtScanlines) drawScanlines();",
    "    ctx.drawImage(osCanvas, 0, 0, 224, 288, 8, 0, 224, 240);"
)

# 2. In new_games_block, remove internal drawScanlines calls from individual games
code = code.replace(
    "  // CRT Scanlines\n  if (crtScanlines) drawScanlines();\n\n  // Nichibutsu Arcade HUD",
    "  // Nichibutsu Arcade HUD"
)
code = code.replace(
    "  if (crtScanlines) drawScanlines();\n  if (f % 90 === 30) playArcadeSfx('DIVE');",
    "  if (f % 90 === 30) playArcadeSfx('DIVE');"
)
code = code.replace(
    "  if (isJumping && f % 40 === 0) playArcadeSfx('DK-JUMP');\n  if (crtScanlines) drawScanlines();",
    "  if (isJumping && f % 40 === 0) playArcadeSfx('DK-JUMP');"
)
code = code.replace(
    "  ctx.fillRect(fx + 5, fy + 4, 3, 3);\n\n  if (crtScanlines) drawScanlines();",
    "  ctx.fillRect(fx + 5, fy + 4, 3, 3);"
)
code = code.replace(
    "    ctx.fillRect(ex - 2, ey - 2, 4, 4);\n  }\n\n  if (crtScanlines) drawScanlines();\n}",
    "    ctx.fillRect(ex - 2, ey - 2, 4, 4);\n  }\n}"
)

# 3. Add replacements for ensurePastBoot, renderTourDemo, mainLoop, switchActiveGame, and init
replacements_addition = '''
    # 4b. Ensure instant Pac-Man boot and crisp single scanline pass
    script_body = script_body.replace(
        """function ensurePastBoot() {
  let safety = 0;
  while (animTick < 305 && safety < 350) {
    stepCpuFrame();
    safety++;
  }
}""",
        """function ensurePastBoot() {
  let safety = 0;
  while (animTick < 320 && safety < 350) {
    stepCpuFrame();
    safety++;
  }
}"""
    )

    script_body = script_body.replace(
        """  switch (game.id) {
    case 'pacman':
      renderArcadeFrame();
      break;""",
        """  switch (game.id) {
    case 'pacman':
      ensurePastBoot();
      stepCpuFrame();
      renderArcadeFrame();
      break;"""
    )

    old_boot_loop = """  // During boot test (< frame 305), run CPU at 5x speed so game boots in < 0.6 seconds!
  if (animTick < 305) {
    for (let fast = 0; fast < 5 && animTick < 305; fast++) {
      stepCpuFrame();
    }
  } else {"""

    new_boot_loop = """  // Instant 0ms boot: fast-forward past memory self-test immediately
  if (animTick < 320) {
    ensurePastBoot();
  } else {"""
    script_body = script_body.replace(old_boot_loop, new_boot_loop)

    old_arcade_render_block = """    if (currentMode === 'rewind') {
      ctx.fillStyle = '#ff3344';
      ctx.font = 'bold 12px monospace';
      ctx.fillText('◄◄ REWINDING (HOLD KEY)', 12, 22);
    }
  } else if (currentMode === 'demo') {"""

    new_arcade_render_block = """    if (currentMode === 'rewind') {
      ctx.fillStyle = '#ff3344';
      ctx.font = 'bold 12px monospace';
      ctx.fillText('◄◄ REWINDING (HOLD KEY)', 12, 22);
    }
    if (crtScanlines) drawScanlines();
  } else if (currentMode === 'demo') {"""
    script_body = script_body.replace(old_arcade_render_block, new_arcade_render_block)

    old_switch_game = """    document.getElementById('hudStatus').textContent = '● PAC-MAN ACTIVE';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Controls: <b>WASD</b> or <b>Arrow Keys</b> or <b>On-Screen D-Pad</b>';
  }
}"""

    new_switch_game = """    document.getElementById('hudStatus').textContent = '● PAC-MAN ACTIVE';
    const hint = document.getElementById('controlsHint');
    if (hint) hint.innerHTML = 'Controls: <b>WASD</b> or <b>Arrow Keys</b> or <b>On-Screen D-Pad</b>';
    ensurePastBoot();
    renderArcadeFrame();
  }
}"""
    script_body = script_body.replace(old_switch_game, new_switch_game)

    old_init = """// Initialize Demo Songs UI
initDemoJukebox();

requestAnimationFrame(mainLoop);"""

    new_init = """// Initialize Demo Songs UI
initDemoJukebox();

// Instant Pac-Man maze & attract screen initialization (0ms wait)
ensurePastBoot();
renderArcadeFrame();

requestAnimationFrame(mainLoop);"""
    script_body = script_body.replace(old_init, new_init)
'''

# Insert replacements_addition before `script_body.replace(old_setupknob, new_setupknob)`
target_pos = code.find("script_body = script_body.replace(old_setupknob, new_setupknob)")
if target_pos != -1:
    code = code[:target_pos] + replacements_addition + "\n    " + code[target_pos:]
else:
    raise ValueError("Target position for replacements not found!")

# 4. Fix tourState.idx to tourState.gameIdx in additional_bindings
code = code.replace(
    "    if (currentMode !== 'tour') toggleTourDemo();\n    tourState.idx = currentGameIdx;",
    "    if (currentMode !== 'tour') toggleTourDemo();\n    tourState.gameIdx = currentGameIdx;\n    tourState.frameInGame = 0;"
)

# 5. Enhance URL query parameter handling for instant pacman render
code = code.replace(
    "    if (params.get('game')) {\n      switchActiveGame(params.get('game'));\n    }",
    "    if (params.get('game')) {\n      switchActiveGame(params.get('game'));\n      if (params.get('game') === 'pacman') { ensurePastBoot(); renderArcadeFrame(); }\n    }"
)

with open("tools/build_hardware_template.py", "w") as f:
    f.write(code)

print("Successfully updated tools/build_hardware_template.py!")
