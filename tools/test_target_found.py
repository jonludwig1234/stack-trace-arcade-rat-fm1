with open('tools/simulator_template.html.bak', 'r') as f:
    s = f.read()

target = """  // During boot test (< frame 305), run CPU at 5x speed so game boots in < 0.6 seconds!
  if (animTick < 305) {
    for (let fast = 0; fast < 5 && animTick < 305; fast++) {
      stepCpuFrame();
    }
  } else {
    // Normal 60 Hz frame
    if (currentMode === 'arcade' || currentMode === 'glitch') {
      stepCpuFrame();

      // Save state to rewind ring buffer
      if (animTick % 2 === 0) {
        if (rewindBuffer.length >= 300) rewindBuffer.shift();
        rewindBuffer.push({
          ram: new Uint8Array(ram),
          spritePos: new Uint8Array(spritePos)
        });
      }
    } else if (isRewinding) {
      if (rewindBuffer.length > 0) {
        const snap = rewindBuffer.pop();
        ram.set(snap.ram);
        spritePos.set(snap.spritePos);
      }
    }
  }

  // Update HUD info
  const credits = ram[0x4e69 - 0x4000];
  document.getElementById('hudCredits').textContent = `CREDITS: ${credits}`;
  if (animTick < 305) {
    document.getElementById('hudStatus').className = 'hud-badge booting';
    document.getElementById('hudStatus').textContent = '● BOOTING TEST...';
  } else if (credits === 0) {
    document.getElementById('hudStatus').className = 'hud-badge attract';
    document.getElementById('hudStatus').textContent = '● ATTRACT (INSERT COIN)';
  } else {
    document.getElementById('hudStatus').className = 'hud-badge';
    document.getElementById('hudStatus').textContent = '● PLAYING: READY!';
  }"""

print("Found full mainLoop CPU block in bak:", target in s)
