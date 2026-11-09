const http = require('http');
const fs = require('fs');
const { spawn } = require('child_process');

const url = 'http://localhost:8085/fm1_pacman_preview.html?mode=arcade&game=frogger';
const outPath = '/home/jon/.gemini/antigravity/brain/76628535-31d8-4f4a-baa3-a47a7f1798ab/snap_frogger_death_authentic.png';

async function main() {
  const port = 9335;
  const chrome = spawn('google-chrome', [
    '--headless=new',
    `--remote-debugging-port=${port}`,
    '--disable-gpu',
    '--no-sandbox',
    '--disable-extensions',
    '--window-size=1200,1050',
    url
  ]);

  await new Promise(r => setTimeout(r, 1500));

  http.get(`http://127.0.0.1:${port}/json`, (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', async () => {
      let tabs = [];
      try { tabs = JSON.parse(data); } catch(e) {}
      const target = tabs.find(t => t.type === 'page' && t.url.includes('8085')) || tabs.find(t => t.type === 'page');
      if (!target || !target.webSocketDebuggerUrl) {
        console.error('Could not find debugging target!');
        chrome.kill();
        process.exit(1);
      }

      const ws = new WebSocket(target.webSocketDebuggerUrl);

      ws.onopen = () => {
        // Trigger death animation at highway
        const evalCode = `
          setMode('arcade');
          switchActiveGame('frogger');
          initFroggerGame();
          froggerGame.frog.x = 104;
          froggerGame.frog.y = 160;
          killFrogger('splat');
          froggerGame.frog.deathTimer = 20; // Phase 2: Skull & Crossbones
          renderFroggerGame();
        `;
        ws.send(JSON.stringify({
          id: 1,
          method: 'Runtime.evaluate',
          params: { expression: evalCode }
        }));

        setTimeout(() => {
          ws.send(JSON.stringify({
            id: 2,
            method: 'Page.captureScreenshot',
            params: { format: 'png' }
          }));
        }, 600);
      };

      ws.onmessage = (msg) => {
        const payload = JSON.parse(msg.data);
        if (payload.id === 2 && payload.result && payload.result.data) {
          const buf = Buffer.from(payload.result.data, 'base64');
          fs.writeFileSync(outPath, buf);
          console.log(`Saved screenshot to ${outPath} (${buf.length} bytes)`);
          ws.close();
          chrome.kill();
          process.exit(0);
        }
      };
    });
  });
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
