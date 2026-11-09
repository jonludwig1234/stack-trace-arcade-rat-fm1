const http = require('http');
const { spawn } = require('child_process');

async function debugZeroAudio() {
  const port = 9336;
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
                const logs = [];
                const offCtx = new OfflineAudioContext(1, 44100, 44100);
                
                // Let's test VOX_INTRUDER step by step
                const now = offCtx.currentTime;
                logs.push('now is: ' + now);
                
                const words = [
                  { f1: 300, f2: 1800, dur: 0.12, pitch: 95 }
                ];
                let t = now;
                words.forEach(w => {
                  logs.push('word pitch: ' + w.pitch + ' at t: ' + t + ' dur: ' + w.dur);
                  const osc = offCtx.createOscillator(), g = offCtx.createGain();
                  const f1 = offCtx.createBiquadFilter(), f2 = offCtx.createBiquadFilter();
                  osc.type = 'sawtooth'; osc.frequency.setValueAtTime(w.pitch, t);
                  f1.type = 'bandpass'; f1.frequency.setValueAtTime(w.f1, t); f1.Q.setValueAtTime(5, t);
                  f2.type = 'bandpass'; f2.frequency.setValueAtTime(w.f2, t); f2.Q.setValueAtTime(5, t);
                  g.gain.setValueAtTime(0.65, t); g.gain.exponentialRampToValueAtTime(0.01, t + w.dur);
                  osc.connect(f1); osc.connect(f2);
                  f1.connect(g); f2.connect(g);
                  g.connect(offCtx.destination);
                  osc.start(t); osc.stop(t + w.dur);
                });
                
                const rendered = await offCtx.startRendering();
                const d = rendered.getChannelData(0);
                let max = 0;
                for (let i = 0; i < d.length; i++) if (Math.abs(d[i]) > max) max = Math.abs(d[i]);
                logs.push('Rendered max: ' + max);
                return logs;
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
          console.log('[DEBUG RESULT]', JSON.stringify(m.result, null, 2));
          chrome.kill();
          process.exit(0);
        }
      };
    });
  });
}

debugZeroAudio();
