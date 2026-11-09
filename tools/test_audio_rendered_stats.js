const http = require('http');
const fs = require('fs');
const { spawn } = require('child_process');

async function testAudioOutput() {
  const port = 9335;
  const chrome = spawn('google-chrome', [
    '--headless=new',
    `--remote-debugging-port=${port}`,
    '--disable-gpu',
    '--no-sandbox',
    'http://localhost:8085/fm1_pacman_preview.html?tab=speech'
  ]);

  await new Promise(r => setTimeout(r, 1500));

  http.get(`http://127.0.0.1:${port}/json`, (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', async () => {
      const tabs = JSON.parse(data);
      const target = tabs.find(t => t.type === 'page');
      const ws = new WebSocket(target.webSocketDebuggerUrl);
      ws.onopen = () => {
        ws.send(JSON.stringify({ id: 1, method: 'Runtime.enable' }));
        setTimeout(() => {
          ws.send(JSON.stringify({
            id: 2,
            method: 'Runtime.evaluate',
            params: {
              expression: `(async () => {
                // Test speech synthesis and offline audio render
                const sampleIds = ['VOX_INTRUDER', 'VOX_COIN', 'VOX_QBERT', 'VOX_SINISTAR', 'VOX_HUNGER', 'VOX_WIZARD', 'VOX_DANGER', 'VOX_ARCADE_RAT'];
                const stats = {};
                for (const id of sampleIds) {
                  // Render in an OfflineAudioContext
                  const offCtx = new OfflineAudioContext(1, 44100 * 2, 44100);
                  const origCtx = window.audioCtx;
                  const origFilter = window.filterNode;
                  window.audioCtx = offCtx;
                  window.filterNode = offCtx.destination;
                  
                  playArcadeSpeechSample(id);
                  
                  const rendered = await offCtx.startRendering();
                  const chData = rendered.getChannelData(0);
                  let maxAmp = 0;
                  let nonZero = 0;
                  for (let i = 0; i < chData.length; i++) {
                    const abs = Math.abs(chData[i]);
                    if (abs > maxAmp) maxAmp = abs;
                    if (abs > 0.001) nonZero++;
                  }
                  stats[id] = { maxAmp, nonZeroDurationSec: (nonZero / 44100).toFixed(3) };
                  
                  window.audioCtx = origCtx;
                  window.filterNode = origFilter;
                }
                return stats;
              })()`,
              awaitPromise: true,
              returnByValue: true
            }
          }));
        }, 1000);
      };

      ws.onmessage = (msg) => {
        const m = JSON.parse(msg.data);
        if (m.id === 2) {
          console.log('[AUDIO STATS RESULT]', JSON.stringify(m.result, null, 2));
          chrome.kill();
          process.exit(0);
        }
      };
    });
  });
}

testAudioOutput();
