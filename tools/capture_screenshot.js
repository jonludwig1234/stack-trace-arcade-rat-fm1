const http = require('http');
const fs = require('fs');
const { spawn } = require('child_process');

const url = process.argv[2] || 'http://localhost:8085/fm1_pacman_preview.html';
const outPath = process.argv[3] || 'screenshot.png';
const windowWidth = parseInt(process.argv[4]) || 1200;
const windowHeight = parseInt(process.argv[5]) || 1050;

async function main() {
  const port = 9333;
  const chrome = spawn('google-chrome', [
    '--headless=new',
    `--remote-debugging-port=${port}`,
    '--disable-gpu',
    '--no-sandbox',
    '--disable-extensions',
    `--window-size=${windowWidth},${windowHeight}`,
    url
  ]);

  // Wait for Chrome to initialize
  await new Promise(r => setTimeout(r, 1200));

  // Query /json to find page target
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

      // Connect via native WebSocket
      const ws = new WebSocket(target.webSocketDebuggerUrl);

      ws.onopen = () => {
        const u = new URL(url);
        const shelf = u.searchParams.get('shelf') || u.searchParams.get('tab');
        const bank = u.searchParams.get('bank');
        const game = u.searchParams.get('game');

        let evalCode = '';
        if (shelf) evalCode += `if (typeof setStudioTab === 'function') setStudioTab('${shelf}');`;
        if (bank) evalCode += `if (typeof switchSfxBank === 'function') switchSfxBank(${parseInt(bank) >= 1 ? parseInt(bank) - 1 : parseInt(bank)});`;
        if (game) evalCode += `if (typeof switchActiveGame === 'function') switchActiveGame('${game}');`;

        if (evalCode) {
          ws.send(JSON.stringify({
            id: 99,
            method: 'Runtime.evaluate',
            params: { expression: evalCode }
          }));
        }

        setTimeout(() => {
          ws.send(JSON.stringify({
            id: 1,
            method: 'Page.captureScreenshot',
            params: { format: 'png' }
          }));
        }, 1200);
      };

      ws.onmessage = (event) => {
        const resp = JSON.parse(event.data);
        if (resp.id === 1 && resp.result && resp.result.data) {
          const buf = Buffer.from(resp.result.data, 'base64');
          fs.writeFileSync(outPath, buf);
          console.log(`Successfully saved screenshot to ${outPath} (${buf.length} bytes)`);
          ws.close();
          chrome.kill();
          process.exit(0);
        }
      };
    });
  }).on('error', (err) => {
    console.error('HTTP error connecting to Chrome debugging port:', err);
    chrome.kill();
    process.exit(1);
  });
}

main();
