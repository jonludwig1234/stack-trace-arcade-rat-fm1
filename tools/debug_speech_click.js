const http = require('http');
const { spawn } = require('child_process');

async function testClick() {
  const port = 9337;
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
        ws.send(JSON.stringify({ id: 2, method: 'Input.enable' }));
        
        setTimeout(() => {
          // Let's inspect the DOM element for card_VOX_INTRUDER
          ws.send(JSON.stringify({
            id: 3,
            method: 'Runtime.evaluate',
            params: {
              expression: `(() => {
                const el = document.getElementById('card_VOX_INTRUDER');
                const btn = el ? el.querySelector('button') : null;
                const tab = document.getElementById('tabSpeech');
                const shelf = document.getElementById('shelfSpeech');
                
                // Let's test calling button.click()
                let clicked = false;
                let sfxLast = '';
                if (btn) {
                  btn.click();
                  clicked = true;
                  sfxLast = document.getElementById('sfxLastTriggered').textContent;
                }
                
                return {
                  hasTab: !!tab,
                  hasShelf: !!shelf,
                  shelfClasses: shelf ? shelf.className : '',
                  hasCard: !!el,
                  hasBtn: !!btn,
                  clicked,
                  sfxLast,
                  audioCtxState: typeof audioCtx !== 'undefined' && audioCtx ? audioCtx.state : 'null',
                  audioCtxSampleRate: typeof audioCtx !== 'undefined' && audioCtx ? audioCtx.sampleRate : 'null'
                };
              })()`,
              returnByValue: true
            }
          }));
        }, 1000);
      };

      ws.onmessage = (msg) => {
        const m = JSON.parse(msg.data);
        if (m.id === 3) {
          console.log('[CLICK TEST RESULT]', JSON.stringify(m.result, null, 2));
          chrome.kill();
          process.exit(0);
        }
      };
    });
  });
}

testClick();
