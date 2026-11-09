const http = require('http');
const { spawn } = require('child_process');
const assert = require('assert');

console.log("=========================================================================");
console.log("TEST: HEADLESS CHROME E2E BROWSER DOM & CANVAS PIXEL AUDIT BATTERY");
console.log("=========================================================================");

const port = 9334;
const url = `http://localhost:8085/fm1_pacman_preview.html?nosplash=1`;

async function runE2E() {
  const chrome = spawn('google-chrome', [
    '--headless=new',
    `--remote-debugging-port=${port}`,
    '--disable-gpu',
    '--no-sandbox',
    '--disable-extensions',
    '--window-size=1200,900',
    url
  ]);

  let killed = false;
  function cleanup() {
    if (!killed) {
      killed = true;
      try { chrome.kill(); } catch (e) {}
    }
  }

  process.on('exit', cleanup);
  process.on('SIGINT', cleanup);

  // Wait for Chrome to boot
  await new Promise(r => setTimeout(r, 1500));

  // Query CDP targets
  http.get(`http://127.0.0.1:${port}/json`, (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', async () => {
      let targets = [];
      try { targets = JSON.parse(data); } catch(e) {}
      const pageTarget = targets.find(t => t.type === 'page' && t.url.includes('8085')) || targets.find(t => t.type === 'page');
      if (!pageTarget || !pageTarget.webSocketDebuggerUrl) {
        console.error("❌ Could not connect to Chrome CDP WebSocket target!");
        cleanup();
        process.exit(1);
      }

      const ws = new WebSocket(pageTarget.webSocketDebuggerUrl);
      let msgId = 1;
      const callbacks = {};
      const consoleErrors = [];

      function sendCmd(method, params = {}) {
        return new Promise((resolve) => {
          const id = msgId++;
          callbacks[id] = resolve;
          ws.send(JSON.stringify({ id, method, params }));
        });
      }

      function evaluate(expr) {
        return sendCmd('Runtime.evaluate', { expression: expr, returnByValue: true }).then(r => {
          if (r && r.result && r.result.result) return r.result.result.value;
          return (r && r.result) ? r.result.value : r;
        });
      }

      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.id && callbacks[msg.id]) {
          callbacks[msg.id](msg);
          delete callbacks[msg.id];
        }
        if (msg.method === 'Runtime.exceptionThrown') {
          consoleErrors.push(msg.params.exceptionDetails.text);
        }
      };

      ws.onopen = async () => {
        try {
          await sendCmd('Runtime.enable');
          await sendCmd('Console.enable');

          console.log("\n1. Verifying Zero Console Errors & Page Initialization...");
          assert.strictEqual(consoleErrors.length, 0, `Page loaded with console errors: ${consoleErrors.join(', ')}`);
          console.log("   ✓ Zero console errors on initial load!");

          console.log("\n2. Checking Canvas Geometry & Hardware Cockpit Layout in Live DOM...");
          const canvasCheck = await evaluate(`
            const c = document.getElementById('tftCanvas');
            ({ width: c.width, height: c.height, id: c.id, hasCtx: !!c.getContext('2d') })
          `);
          assert(canvasCheck && canvasCheck.width === 240 && canvasCheck.height === 240, `Canvas must be 240x240, got: ${JSON.stringify(canvasCheck)}`);
          console.log(`   ✓ #tftCanvas verified in DOM: 240x240 pixels with 2D rendering context!`);

          console.log("\n3. Testing Real Pixel Rendering Across All 8 Arcade Games...");
          const games = ['pacman', 'cclimber', 'galaga', 'dkong', 'frogger', 'asteroids', 'tempest', 'gyruss'];
          for (const g of games) {
            // Switch game and render 3 frames
            await evaluate(`
              switchActiveGame('${g}');
              if ('${g}' === 'pacman') ensurePastBoot();
              renderArcadeFrame();
              renderArcadeFrame();
              renderArcadeFrame();
            `);
            await new Promise(r => setTimeout(r, 80));

            // Extract pixel buffer
            const resVal = await evaluate(`
              (() => {
                const c = document.getElementById('tftCanvas');
                const ctx = c.getContext('2d');
                const img = ctx.getImageData(0, 0, 240, 240);
                let nonZero = 0;
                for (let i = 0; i < img.data.length; i += 4) {
                  if (img.data[i] > 0 || img.data[i+1] > 0 || img.data[i+2] > 0) nonZero++;
                }
                return { total: img.data.length / 4, coloredPixels: nonZero, active: activeGame };
              })()
            `);

            assert(resVal && resVal.coloredPixels > 100, `Game ${g} rendered blank screen! Colored pixels: ${resVal ? resVal.coloredPixels : 'null'}`);
            console.log(`   ✓ ${g.padEnd(10)}: activeGame='${resVal.active}' -> ${resVal.coloredPixels} active colored pixels rendered to hardware frame!`);
          }

          console.log("\n4. Testing Real DOM Keyboard Events (Coin & 1P Start)...");
          await evaluate(`
            window.dispatchEvent(new KeyboardEvent('keydown', { key: '5', code: 'Digit5', bubbles: true }));
            window.dispatchEvent(new KeyboardEvent('keyup', { key: '5', code: 'Digit5', bubbles: true }));
            window.dispatchEvent(new KeyboardEvent('keydown', { key: '1', code: 'Digit1', bubbles: true }));
            window.dispatchEvent(new KeyboardEvent('keyup', { key: '1', code: 'Digit1', bubbles: true }));
          `);
          console.log("   ✓ Dispatched Coin (<kbd>5</kbd>) and 1P Start (<kbd>1</kbd>) to window cleanly!");

          console.log("\n5. Testing WebMIDI Handler & Rotary Encoder in Live Browser...");
          const midiResult = await evaluate(`
            (() => {
              handleMidiMessage({ data: [0xB0, 74, 96] }); // CC 74 LPF Knob 1
              return document.getElementById('valKnob1').textContent;
            })()
          `);
          assert(midiResult && midiResult.includes('kHz'), `WebMIDI message must update Knob 1 in live DOM, got: ${midiResult}`);
          console.log(`   ✓ WebMIDI CC 74 updated Knob 1 in live browser: ${midiResult}`);

          console.log("\n6. Testing High Score NVRAM Persistence in Live Browser...");
          const nvramCheck = await evaluate(`
            (() => {
              submitHighScore('pacman', 'E2E', 999990);
              return localStorage.getItem('fm1_arcade_nvram_leaderboard');
            })()
          `);
          assert(nvramCheck && nvramCheck.includes('999990'), `NVRAM localStorage must record new high score, got: ${nvramCheck}`);
          console.log("   ✓ Live browser localStorage saved NVRAM high score record intact!");

          console.log("\n7. Full DOM Click Sweep Across All Studio Tabs, Encoders, Jukebox, Tracker & Speech Cards...");
          const clickSweep = await evaluate(`
            (() => {
              const idsToClick = [
                'btnVolDown', 'btnVolUp', 'btnPrevGame', 'btnNextGame',
                'btnPrevSong', 'btnNextSong', 'btnPrevMode', 'btnNextMode',
                'btnShelfPlay', 'btnShelfPause', 'btnShelfStop',
                'btnTrackerPlay', 'btnScl', 'btnEnv', 'btnLfo', 'btnArp',
                'btnOctMinus', 'btnOctPlus', 'btnFxScanlines',
                'ctrlBtnCoin', 'ctrlBtnStart', 'ctrlBtnImmortal', 'ctrlBtnLevelSkip'
              ];
              let clicked = 0;
              for (const id of idsToClick) {
                const el = document.getElementById(id);
                if (el && typeof el.click === 'function') {
                  el.click();
                  clicked++;
                }
              }
              // Click through all 7 Studio Tabs
              document.querySelectorAll('.studio-tab').forEach(t => { t.click(); clicked++; });
              // Test Speech ROM tab & cards
              setStudioTab('speech');
              document.querySelectorAll('.speech-card').forEach(c => { c.click(); clicked++; });
              // Test Synth QWERTY keydown/keyup in live DOM
              setMode('synth');
              if (liveSynth.arp && liveSynth.arp.active) toggleArp();
              window.dispatchEvent(new KeyboardEvent('keydown', { key: 'z', bubbles: true }));
              const synthActive = liveSynth.activeVoices.size;
              window.dispatchEvent(new KeyboardEvent('keyup', { key: 'z', bubbles: true }));
              const synthReleased = liveSynth.activeVoices.size;
              return { clicked, synthActive, synthReleased, masterGainVal: masterGain ? masterGain.gain.value : -1 };
            })()
          `);
          assert(clickSweep && clickSweep.clicked >= 35, `Expected >= 35 DOM controls clicked, got: ${JSON.stringify(clickSweep)}`);
          assert.strictEqual(clickSweep.synthActive, 1, "Live DOM QWERTY keydown 'z' in synth mode must activate 1 voice");
          assert.strictEqual(clickSweep.synthReleased, 0, "Live DOM QWERTY keyup 'z' in synth mode must release voice");
          assert(clickSweep.masterGainVal > 0, "Live Web Audio masterGain must be active and > 0");
          console.log(`   ✓ Clicked ${clickSweep.clicked} live DOM controls, tabs & cards + verified live Web Audio Synth & MasterGain!`);

          console.log("\n8. Final Console Stability Check...");
          assert.strictEqual(consoleErrors.length, 0, `Errors occurred during run: ${consoleErrors.join('; ')}`);
          console.log("   ✓ 0 runtime exceptions or uncaught promise rejections observed throughout entire E2E session!");

          console.log("\n=========================================================================");
          console.log(">>> ALL HEADLESS CHROME E2E BROWSER & PIXEL TESTS PASSED 100%! <<<");
          console.log("=========================================================================");

          ws.close();
          cleanup();
          process.exit(0);
        } catch (err) {
          console.error("❌ E2E Test Assertion Error:", err);
          cleanup();
          process.exit(1);
        }
      };
    });
  }).on('error', (err) => {
    console.error("❌ HTTP error connecting to Chrome debugging port:", err);
    cleanup();
    process.exit(1);
  });
}

runE2E();
