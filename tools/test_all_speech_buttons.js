const http = require('http');
const { spawn } = require('child_process');

async function testAllSpeechButtons() {
  const port = 9339;
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
              expression: `(() => {
                const results = [];
                const ids = ['VOX_INTRUDER', 'VOX_COIN', 'VOX_QBERT', 'VOX_SINISTAR', 'VOX_HUNGER', 'VOX_WIZARD', 'VOX_GORF', 'VOX_DRAGON'];
                for (const id of ids) {
                  const card = document.getElementById('card_' + id);
                  const btn = card ? card.querySelector('.speech-play-btn') : null;
                  if (!btn) {
                    results.push({ id, error: 'Button not found' });
                    continue;
                  }
                  try {
                    btn.click();
                    const statusText = document.getElementById('speechStatusDisplay').textContent;
                    const lastSfx = document.getElementById('sfxLastTriggered').textContent;
                    results.push({ id, statusText, lastSfx, success: true });
                  } catch (e) {
                    results.push({ id, error: e.message });
                  }
                }
                return results;
              })()`,
              returnByValue: true
            }
          }));
        }, 1000);
      };

      ws.onmessage = (msg) => {
        const m = JSON.parse(msg.data);
        if (m.id === 2) {
          console.log('[ALL BUTTONS TEST RESULT]', JSON.stringify(m.result, null, 2));
          chrome.kill();
          process.exit(0);
        }
      };
    });
  });
}

testAllSpeechButtons();
