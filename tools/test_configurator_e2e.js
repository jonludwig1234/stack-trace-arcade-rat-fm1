const http = require('http');
const fs = require('fs');
const path = require('path');
const assert = require('assert');
const { spawn } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.png': 'image/png',
  '.json': 'application/json',
  '.fwsc': 'application/octet-stream',
};

function startServer(port) {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      const urlPath = req.url.split('?')[0];
      const filePath = path.join(ROOT, urlPath === '/' ? 'index.html' : urlPath);
      if (!filePath.startsWith(ROOT) || !fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
        res.writeHead(404); res.end('404'); return;
      }
      res.writeHead(200, { 'Content-Type': MIME[path.extname(filePath)] || 'application/octet-stream' });
      fs.createReadStream(filePath).pipe(res);
    });
    server.listen(port, '127.0.0.1', () => resolve(server));
  });
}

(async () => {
  const port = 8096;
  const chromePort = 9396;
  const server = await startServer(port);
  const chrome = spawn('google-chrome', [
    '--headless=new',
    `--remote-debugging-port=${chromePort}`,
    '--disable-gpu', '--no-sandbox', '--disable-extensions',
    `http://127.0.0.1:${port}/web/configurator.html`,
  ], { stdio: 'ignore' });

  let wsUrl = null;
  for (let i = 0; i < 40; i++) {
    try {
      const list = await (await fetch(`http://127.0.0.1:${chromePort}/json/list`)).json();
      if (list?.[0]?.webSocketDebuggerUrl) { wsUrl = list[0].webSocketDebuggerUrl; break; }
    } catch {}
    await new Promise(r => setTimeout(r, 150));
  }
  assert(wsUrl, 'Failed to connect to Chrome DevTools');

  const ws = new WebSocket(wsUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  let msgId = 1;
  const pending = new Map();
  const errors = [];
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
    else if (msg.method === 'Runtime.exceptionThrown') errors.push(msg.params.exceptionDetails.text);
  };
  const send = (method, params = {}) => new Promise((resolve) => {
    const id = msgId++; pending.set(id, resolve);
    ws.send(JSON.stringify({ id, method, params }));
  });

  await send('Runtime.enable');
  await new Promise(r => setTimeout(r, 600));

  const res = await send('Runtime.evaluate', {
    awaitPromise: true,
    returnByValue: true,
    expression: `(async () => {
      // 1. Test real SHA-256 ROM drop & zero-byte file handling
      await handleRomFile(new File(['ARCADE_TEST_ROM'], 'test_rom.bin'));
      const subText = document.querySelector('#dropZone .drop-sub').textContent;
      await handleRomFile(new File([], 'empty.bin'));
      const emptyText = document.querySelector('#dropZone .drop-sub').textContent;

      // 2. Test 12-slot budget gauge update with 48KB games
      for (let i = 0; i < 12; i++) { selectSlot(i); equipGame('gyruss'); }
      const flashText = document.getElementById('flashText').textContent;

      // 3. Test C header & JSON config export blob payloads
      let capturedBlobs = [];
      const origCreate = URL.createObjectURL;
      URL.createObjectURL = (b) => { capturedBlobs.push(b); return 'blob:mock'; };
      document.getElementById('mapClimber').value = 'knobs';
      document.getElementById('btnExportHeader').click();
      document.getElementById('btnSaveConfig').click();
      URL.createObjectURL = origCreate;

      const headerStr = await capturedBlobs[0].text();
      const jsonCfg = JSON.parse(await capturedBlobs[1].text());
      return { subText, emptyText, flashText, headerStr, jsonCfg };
    })()`
  });

  ws.close();
  chrome.kill('SIGKILL');
  server.close();

  const val = res.result.result.value;
  assert.strictEqual(errors.length, 0, 'Unexpected runtime errors: ' + errors.join('; '));
  assert(val.subText.includes('test_rom.bin') && val.subText.includes('SHA-256:'), 'Missing SHA-256 in dropzone');
  assert(val.emptyText.includes('empty.bin') && val.emptyText.includes('SHA-256:'), 'Empty file SHA-256 failed');
  assert(val.flashText.includes('686.0 KB / 1,024 KB'), 'Unexpected flash gauge: ' + val.flashText);
  assert(val.headerStr.includes('#define FM1_SLOT_1_GAME "gyruss"'), 'Header macro missing');
  assert.strictEqual(val.jsonCfg.climber, 'knobs', 'climber mapping missing in arcade_config.json');
  assert.strictEqual(val.jsonCfg.slots.length, 12, 'Expected 12 slots in arcade_config.json');
  console.log('✓ Configurator E2E (SHA-256 drop, 0-byte, 12-slot gauge, C header & JSON export) passed!');
})();
