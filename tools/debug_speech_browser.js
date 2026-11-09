const http = require('http');
const { spawn } = require('child_process');

async function debugSpeech() {
  const port = 9334;
  const chrome = spawn('google-chrome', [
    '--headless=new',
    `--remote-debugging-port=${port}`,
    '--disable-gpu',
    '--no-sandbox',
    '--disable-extensions',
    'http://localhost:8085/fm1_pacman_preview.html?tab=speech'
  ]);

  await new Promise(r => setTimeout(r, 1500));

  http.get(`http://127.0.0.1:${port}/json`, (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', async () => {
      const tabs = JSON.parse(data);
      const target = tabs.find(t => t.type === 'page');
      if (!target || !target.webSocketDebuggerUrl) {
        console.error('No target found');
        chrome.kill();
        return;
      }
      const ws = new WebSocket(target.webSocketDebuggerUrl);
      ws.onopen = () => {
        ws.send(JSON.stringify({ id: 1, method: 'Console.enable' }));
        ws.send(JSON.stringify({ id: 2, method: 'Runtime.enable' }));
        
        // Evaluate clicking each speech card and checking for errors
        setTimeout(() => {
          ws.send(JSON.stringify({
            id: 3,
            method: 'Runtime.evaluate',
            params: {
              expression: `(() => {
                const results = [];
                // Test initAudio
                initAudio();
                results.push({ audioCtxState: audioCtx ? audioCtx.state : 'null', filterNode: !!filterNode });
                
                // Test triggerSpeechRom
                const testIds = ['VOX_INTRUDER', 'VOX_COIN', 'VOX_QBERT', 'VOX_SINISTAR', 'VOX_HUNGER', 'VOX_WIZARD', 'VOX_DANGER', 'VOX_ARCADE_RAT'];
                for (const id of testIds) {
                  try {
                    triggerSpeechRom(id);
                    results.push({ id, status: 'ok' });
                  } catch (e) {
                    results.push({ id, error: e.message, stack: e.stack });
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
        if (m.method === 'Console.messageAdded') {
          console.log('[BROWSER CONSOLE]', m.params.message);
        }
        if (m.method === 'Runtime.consoleAPICalled') {
          console.log('[BROWSER LOG]', m.params);
        }
        if (m.method === 'Runtime.exceptionThrown') {
          console.error('[BROWSER EXCEPTION]', m.params);
        }
        if (m.id === 3) {
          console.log('[TEST EVAL RESULT]', JSON.stringify(m.result, null, 2));
          setTimeout(() => {
            chrome.kill();
            process.exit(0);
          }, 500);
        }
      };
    });
  });
}

debugSpeech();
