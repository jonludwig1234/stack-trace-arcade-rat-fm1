const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const port = 9345;
const url = 'http://localhost:8085/fm1_pacman_preview.html';
const outDir = '/tmp/fm1_crt_frames';

if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

console.log("Launching headless Chrome to capture live 240x240 CRT gameplay animation loops...");

const chrome = spawn('google-chrome', [
  '--headless=new',
  `--remote-debugging-port=${port}`,
  '--disable-gpu',
  '--no-sandbox',
  url
]);

setTimeout(() => {
  http.get(`http://127.0.0.1:${port}/json`, (res) => {
    let d = ''; res.on('data', c => d += c);
    res.on('end', () => {
      const target = JSON.parse(d).find(t => t.type === 'page');
      const ws = new WebSocket(target.webSocketDebuggerUrl);

      ws.onopen = () => {
        const captureScript = `
          (async () => {
            const canvas = document.getElementById('tftCanvas');
            if (typeof splashState !== 'undefined') splashState.active = false;
            const games = ['pacman', 'galaga', 'dkong', 'frogger', 'asteroids', 'tempest', 'cclimber', 'gyruss'];
            const result = {};

            for (const g of games) {
              result[g] = [];
              if (typeof switchActiveGame === 'function') switchActiveGame(g);
              
              // Warm up game state so action is mid-screen
              for (let w = 0; w < 25; w++) {
                if (g === 'pacman' && typeof stepPacManFrame === 'function') stepPacManFrame();
                else if (g === 'galaga' && typeof updateGalagaGame === 'function') updateGalagaGame();
                else if (g === 'dkong' && typeof updateDonkeyKongGame === 'function') updateDonkeyKongGame();
                else if (g === 'frogger' && typeof updateFroggerGame === 'function') updateFroggerGame();
                else if (g === 'asteroids' && typeof updateAsteroidsGame === 'function') updateAsteroidsGame();
                else if (g === 'tempest' && typeof updateTempestGame === 'function') updateTempestGame();
                else if (g === 'cclimber' && typeof updateCrazyClimberGame === 'function') updateCrazyClimberGame();
                else if (g === 'gyruss' && typeof updateGyrussGame === 'function') updateGyrussGame();
              }

              for (let f = 0; f < 24; f++) {
                // Inject simulated player movement & firing for exciting action!
                if (g === 'galaga' && typeof galagaGame !== 'undefined') {
                  galagaGame.shipX = 120 + Math.sin(f * 0.35) * 65;
                  if (f % 4 === 0 && galagaGame.bullets) galagaGame.bullets.push({ x: galagaGame.shipX, y: 200 });
                } else if (g === 'dkong' && typeof dkongGame !== 'undefined' && dkongGame.mario) {
                  dkongGame.mario.x = 40 + (f * 4) % 140;
                  if (f % 6 === 0) dkongGame.mario.vy = -4.5;
                } else if (g === 'frogger' && typeof froggerGame !== 'undefined') {
                  if (f % 5 === 0 && froggerGame.frogY > 40) froggerGame.frogY -= 16;
                  if (froggerGame.frogY <= 40) froggerGame.frogY = 216;
                } else if (g === 'asteroids' && typeof asteroidsGame !== 'undefined' && asteroidsGame.ship) {
                  asteroidsGame.ship.angle += 0.22;
                  asteroidsGame.ship.thrusting = (f % 2 === 0);
                  if (f % 4 === 0 && asteroidsGame.bullets) {
                    asteroidsGame.bullets.push({
                      x: asteroidsGame.ship.x, y: asteroidsGame.ship.y,
                      vx: Math.cos(asteroidsGame.ship.angle) * 5, vy: Math.sin(asteroidsGame.ship.angle) * 5, life: 40
                    });
                  }
                } else if (g === 'tempest' && typeof tempestGame !== 'undefined') {
                  tempestGame.playerSeg = f % 16;
                  if (f % 3 === 0 && tempestGame.shots) tempestGame.shots.push({ seg: tempestGame.playerSeg, z: 0.1 });
                } else if (g === 'cclimber' && typeof cclimberGame !== 'undefined') {
                  cclimberGame.scrollY = (cclimberGame.scrollY || 0) + 3;
                  cclimberGame.leftArm = (f % 2 === 0) ? -1 : 1;
                  cclimberGame.rightArm = (f % 2 === 0) ? 1 : -1;
                } else if (g === 'gyruss' && typeof gyrussGame !== 'undefined') {
                  gyrussGame.angle = (gyrussGame.angle || 0) + 0.18;
                  if (f % 3 === 0 && gyrussGame.bullets) {
                    gyrussGame.bullets.push({ angle: gyrussGame.angle, r: 95 });
                  }
                }

                // Step 3 game ticks per captured frame for brisk arcade motion
                for (let s = 0; s < 3; s++) {
                  if (g === 'pacman') {
                    if (typeof stepPacManFrame === 'function') stepPacManFrame();
                    if (typeof renderScreen === 'function') renderScreen();
                  } else if (g === 'galaga') {
                    if (typeof updateGalagaGame === 'function') updateGalagaGame();
                    if (typeof renderGalagaGame === 'function') renderGalagaGame();
                  } else if (g === 'dkong') {
                    if (typeof updateDonkeyKongGame === 'function') updateDonkeyKongGame();
                    if (typeof renderDonkeyKongGame === 'function') renderDonkeyKongGame();
                  } else if (g === 'frogger') {
                    if (typeof updateFroggerGame === 'function') updateFroggerGame();
                    if (typeof renderFroggerGame === 'function') renderFroggerGame();
                  } else if (g === 'asteroids') {
                    if (typeof updateAsteroidsGame === 'function') updateAsteroidsGame();
                    if (typeof renderAsteroidsGame === 'function') renderAsteroidsGame();
                  } else if (g === 'tempest') {
                    if (typeof updateTempestGame === 'function') updateTempestGame();
                    if (typeof renderTempestGame === 'function') renderTempestGame();
                  } else if (g === 'cclimber') {
                    if (typeof updateCrazyClimberGame === 'function') updateCrazyClimberGame();
                    if (typeof renderCrazyClimberGame === 'function') renderCrazyClimberGame();
                  } else if (g === 'gyruss') {
                    if (typeof updateGyrussGame === 'function') updateGyrussGame();
                    if (typeof renderGyrussGame === 'function') renderGyrussGame();
                  }
                }

                result[g].push(canvas.toDataURL('image/png'));
              }
            }
            return result;
          })()
        `;

        ws.send(JSON.stringify({
          id: 1,
          method: 'Runtime.evaluate',
          params: { expression: captureScript, awaitPromise: true, returnByValue: true }
        }));
      };

      ws.onmessage = (msg) => {
        const resp = JSON.parse(msg.data);
        if (resp.id === 1) {
          const data = resp.result.result.value;
          let count = 0;
          for (const [game, frames] of Object.entries(data)) {
            frames.forEach((dataUrl, idx) => {
              const b64 = dataUrl.replace(/^data:image\/png;base64,/, '');
              const filePath = path.join(outDir, `${game}_${String(idx).padStart(2, '0')}.png`);
              fs.writeFileSync(filePath, Buffer.from(b64, 'base64'));
              count++;
            });
          }
          console.log(`Successfully captured ${count} live 240x240 CRT gameplay frames across 8 games in ${outDir}!`);
          ws.close();
          chrome.kill();
          process.exit(0);
        }
      };
    });
  });
}, 1200);
