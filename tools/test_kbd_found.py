with open('tools/simulator_template.html.bak', 'r') as f:
    s = f.read()

target_kbd = """  if (activeGame === 'cclimber') {
    if (k === 'w') { climberStep('left', 'up'); e.preventDefault(); return; }
    else if (k === 's') { climberStep('left', 'down'); e.preventDefault(); return; }
    else if (e.key === 'ArrowUp') { climberStep('right', 'up'); e.preventDefault(); return; }
    else if (e.key === 'ArrowDown') { climberStep('right', 'down'); e.preventDefault(); return; }
    else if (k === 'a' || e.key === 'ArrowLeft') { climberState.col = Math.max(0, climberState.col - 1); e.preventDefault(); return; }
    else if (k === 'd' || e.key === 'ArrowRight') { climberState.col = Math.min(3, climberState.col + 1); e.preventDefault(); return; }
  }

  if (e.key === 'ArrowUp' || k === 'w') { keyUp = true; keyDown = false; e.preventDefault(); }
  else if (e.key === 'ArrowDown' || k === 's') { keyDown = true; keyUp = false; e.preventDefault(); }
  else if (e.key === 'ArrowLeft' || k === 'a') { keyLeft = true; keyRight = false; e.preventDefault(); }
  else if (e.key === 'ArrowRight' || k === 'd') { keyRight = true; keyLeft = false; e.preventDefault(); }
  else if (k === '1' || k === 'c') { insertCoin(); }
  else if (k === '5' || k === 'p' || e.key === 'Enter') { start1P(); }
  else if (e.key === ' ') { quickPlay(); e.preventDefault(); }"""

print("Found keyboard block in bak:", target_kbd in s)
