const http = require('http');
const { spawn } = require('child_process');

async function testSpeechSynth() {
  const port = 9338;
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
                const hasSpeech = typeof window.speechSynthesis !== 'undefined';
                let speaking = false;
                if (hasSpeech) {
                  const utter = new SpeechSynthesisUtterance("Intruder alert! Intruder alert!");
                  utter.pitch = 0.5;
                  utter.rate = 0.85;
                  window.speechSynthesis.speak(utter);
                  speaking = window.speechSynthesis.speaking || window.speechSynthesis.pending;
                }
                return { hasSpeech, speaking };
              })()`,
              returnByValue: true
            }
          }));
        }, 1000);
      };

      ws.onmessage = (msg) => {
        const m = JSON.parse(msg.data);
        if (m.id === 2) {
          console.log('[SPEECH SYNTH TEST]', JSON.stringify(m.result, null, 2));
          chrome.kill();
          process.exit(0);
        }
      };
    });
  });
}

testSpeechSynth();
