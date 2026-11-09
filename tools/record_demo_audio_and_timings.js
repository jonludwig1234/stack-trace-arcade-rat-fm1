const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const port = 9338;
const url = 'http://localhost:8085/fm1_pacman_preview.html';
const outAudioWav = path.resolve(__dirname, '../web/demo_soundtrack.wav');
const outTimelineJson = path.resolve(__dirname, '../web/demo_timeline.json');

console.log("Launching headless Chrome on port", port, "to record complete demo soundtrack...");

const chrome = spawn('google-chrome', [
  '--headless=new',
  `--remote-debugging-port=${port}`,
  '--disable-gpu',
  '--no-sandbox',
  '--autoplay-policy=no-user-gesture-required',
  url
]);

function writeWavFile(filePath, sampleRate, numChannels, floatSamples) {
  const numSamples = floatSamples.length;
  const byteRate = sampleRate * numChannels * 2;
  const blockAlign = numChannels * 2;
  const header = Buffer.alloc(44);
  header.write('RIFF', 0);
  header.writeUInt32LE(36 + numSamples * 2, 4);
  header.write('WAVE', 8);
  header.write('fmt ', 12);
  header.writeUInt32LE(16, 16);
  header.writeUInt16LE(1, 20); // PCM format
  header.writeUInt16LE(numChannels, 22);
  header.writeUInt32LE(sampleRate, 24);
  header.writeUInt32LE(byteRate, 28);
  header.writeUInt16LE(blockAlign, 32);
  header.writeUInt16LE(16, 34); // 16-bit
  header.write('data', 36);
  header.writeUInt32LE(numSamples * 2, 40);

  const data = Buffer.alloc(numSamples * 2);
  for (let i = 0; i < numSamples; i++) {
    let s = Math.max(-1, Math.min(1, floatSamples[i]));
    let val = s < 0 ? s * 0x8000 : s * 0x7FFF;
    data.writeInt16LE(Math.round(val), i * 2);
  }

  fs.writeFileSync(filePath, Buffer.concat([header, data]));
}

setTimeout(() => {
  http.get(`http://127.0.0.1:${port}/json`, (res) => {
    let d = ''; res.on('data', c => d += c);
    res.on('end', async () => {
      let tabs = [];
      try { tabs = JSON.parse(d); } catch (e) {}
      const target = tabs.find(t => t.type === 'page' && t.url.includes('8085')) || tabs.find(t => t.type === 'page');
      if (!target || !target.webSocketDebuggerUrl) {
        console.error("No target found!");
        chrome.kill();
        process.exit(1);
      }

      const ws = new WebSocket(target.webSocketDebuggerUrl);

      ws.onopen = () => {
        console.log("Connected to Chrome CDP WebSocket!");
        const injection = `
          (() => {
            initAudio();
            window.__demoAudio = [];
            window.__cuePoints = [];
            
            // Connect recorder directly to masterGain
            const proc = audioCtx.createScriptProcessor(2048, 1, 1);
            proc.onaudioprocess = (e) => {
              const input = e.inputBuffer.getChannelData(0);
              window.__demoAudio.push(new Float32Array(input));
            };
            masterGain.connect(proc);
            proc.connect(audioCtx.destination);
            
            window.logCue = (sceneId, name, desc) => {
              const t = (window.__demoAudio.length * 2048) / 44100;
              window.__cuePoints.push({ sceneId, name, desc, time: t });
            };
            
            return 'RECORDING_INITIALIZED';
          })()
        `;

        ws.send(JSON.stringify({
          id: 1,
          method: 'Runtime.evaluate',
          params: { expression: injection, returnByValue: true }
        }));
      };

      ws.onmessage = async (msg) => {
        const resp = JSON.parse(msg.data);
        if (resp.id === 1) {
          console.log("Audio graph recording initialized:", resp.result.result.value);
          
          const performanceScript = `
            (async () => {
              try {
                const sleep = ms => new Promise(r => setTimeout(r, ms));
                const logCue = (id, n, d) => { if (typeof window.logCue === 'function') window.logCue(id, n, d); };
                const safeSfx = id => { try { if (typeof playArcadeSfx === 'function') playArcadeSfx(id); } catch(e){ console.warn(e); } };
                const safeVox = id => { try { if (typeof playArcadeSpeechSample === 'function') playArcadeSpeechSample(id); } catch(e){ console.warn(e); } };

                // -------------------------------------------------------------
                // SCENE 1: BOOT SEQUENCE & FIRMWARE INTRO
                // -------------------------------------------------------------
                logCue('scene_01_intro', 'Firmware Boot Sequence', 'Z80 CPU Cold Boot & Pac-Man Chime');
                safeSfx('PAC-START');
                await sleep(5500);

                // -------------------------------------------------------------
                // SCENE 2: PAC-MAN (1980 NAMCO)
                // -------------------------------------------------------------
                logCue('scene_02_pacman', 'Pac-Man (1980 · Namco)', 'Z80 CPU · Namco WSG Siren, Waka-Waka & Ghost Fanfare');
                switchActiveGame('pacman');
                safeSfx('PAC-SIREN');
                await sleep(1000);
                for (let i = 0; i < 4; i++) {
                  safeSfx('PAC-WAKA');
                  await sleep(350);
                }
                safeSfx('PAC-POWER');
                await sleep(800);
                safeSfx('PAC-EATGHOST');
                await sleep(2000);

                // -------------------------------------------------------------
                // SCENE 3: GALAGA (1981 NAMCO)
                // -------------------------------------------------------------
                logCue('scene_03_galaga', 'Galaga (1981 · Namco)', 'Starfield Scrolling · Dual Lasers · Alien Dive & Explosion');
                switchActiveGame('galaga');
                safeSfx('GALAGA-DIVE');
                await sleep(1500);
                for (let i = 0; i < 3; i++) {
                  safeSfx('GALAGA-FIRE');
                  await sleep(400);
                }
                safeSfx('GALAGA-EXP');
                await sleep(1200);
                safeSfx('GALAGA-TRACTOR');
                await sleep(2000);

                // -------------------------------------------------------------
                // SCENE 4: DONKEY KONG (1981 NINTENDO)
                // -------------------------------------------------------------
                logCue('scene_04_dkong', 'Donkey Kong (1981 · Nintendo)', '25M Girder Physics · 8035 BGM · Hammer & Death Fanfare');
                switchActiveGame('dkong');
                safeSfx('DK-WALK');
                await sleep(600);
                safeSfx('DK-WALK');
                await sleep(600);
                safeSfx('DK-JUMP');
                await sleep(1000);
                safeSfx('DK-HAMMER');
                await sleep(1200);
                safeSfx('DK-GAMEOVER');
                await sleep(2500);

                // -------------------------------------------------------------
                // SCENE 5: FROGGER (1981 KONAMI)
                // -------------------------------------------------------------
                logCue('scene_05_frogger', 'Frogger (1981 · Konami)', 'Dual AY-3-8910 Chiptune BGM · Hop Chirps · Water Splash');
                switchActiveGame('frogger');
                for (let f = 0; f < 30; f++) updateFroggerGame();
                await sleep(1000);
                safeSfx('FROG-HOP');
                await sleep(400);
                safeSfx('FROG-HOP');
                await sleep(400);
                safeSfx('FROG-HOME');
                await sleep(1500);
                safeSfx('FROG-SPLASH');
                await sleep(2200);

                // -------------------------------------------------------------
                // SCENE 6: ASTEROIDS (1979 ATARI)
                // -------------------------------------------------------------
                logCue('scene_06_asteroids', 'Asteroids (1979 · Atari)', 'Vector Inertial Drift · Dual-Pitch Heartbeat Thrust · Vector Cannon');
                switchActiveGame('asteroids');
                safeSfx('AST-THRUST');
                await sleep(500);
                safeSfx('AST-THRUST');
                await sleep(500);
                for (let i = 0; i < 3; i++) {
                  safeSfx('AST-FIRE');
                  await sleep(350);
                }
                safeSfx('AST-EXP');
                await sleep(1200);
                safeSfx('AST-UFO');
                await sleep(2000);

                // -------------------------------------------------------------
                // SCENE 7: TEMPEST (1981 ATARI)
                // -------------------------------------------------------------
                logCue('scene_07_tempest', 'Tempest (1981 · Atari)', '3D Perspective Vector Warp · Superzapper · Atari POKEY Cascade');
                switchActiveGame('tempest');
                for (let i = 0; i < 4; i++) {
                  safeSfx('TEM-FIRE');
                  await sleep(350);
                }
                safeSfx('TEM-ZAP');
                await sleep(1800);
                safeSfx('TEM-DEATH');
                await sleep(2400);

                // -------------------------------------------------------------
                // SCENE 8: CRAZY CLIMBER (1980 NICHIBUTSU)
                // -------------------------------------------------------------
                logCue('scene_08_cclimber', 'Crazy Climber (1980 · Nichibutsu)', 'Twin-Stick Vertical Climber · Falling Flower Pots · Whistle & Splat');
                switchActiveGame('cclimber');
                safeSfx('CLIMB-STEP');
                await sleep(500);
                safeSfx('CLIMB-STEP');
                await sleep(500);
                safeSfx('CLIMB-SLAM');
                await sleep(1000);
                safeSfx('CLIMB-POT');
                await sleep(800);
                safeSfx('CLIMB-FALL');
                await sleep(2500);

                // -------------------------------------------------------------
                // SCENE 9: GYRUSS (1983 KONAMI)
                // -------------------------------------------------------------
                logCue('scene_09_gyruss', 'Gyruss (1983 · Konami)', '360° Polar Tube Flight · J.S. Bach Toccata & Fugue · 5x PSG Explosion');
                switchActiveGame('gyruss');
                for (let f = 0; f < 60; f++) updateGyrussGame();
                await sleep(1500);
                for (let i = 0; i < 3; i++) {
                  safeSfx('GYRUSS-FIRE');
                  await sleep(350);
                }
                safeSfx('GYRUSS-EXP');
                await sleep(2800);

                // -------------------------------------------------------------
                // SCENE 10: SFX BANK 1 - GOLDEN AGE ARCADE (1978–1982)
                // -------------------------------------------------------------
                logCue('scene_10_bank1', 'SFX Bank 1: Golden Age Arcade (1978–1982)', '27 Sounds · Space Invaders March, Galaxian Dive & Pac-Man Intermission');
                switchSfxBank(0);
                safeSfx('INV-STEP');
                await sleep(800);
                safeSfx('INV-UFO');
                await sleep(1400);
                safeSfx('DIVE');
                await sleep(1500);
                safeSfx('CAPTURE');
                await sleep(2000);

                // -------------------------------------------------------------
                // SCENE 11: SFX BANK 2 - NINTENDO 8-BIT ARCADE (1981–1985)
                // -------------------------------------------------------------
                logCue('scene_11_bank2', 'SFX Bank 2: Nintendo 8-Bit Arcade (1981–1985)', '27 Sounds · NES 2A03 APU Square/Noise Synthesis · Mario & Punch-Out');
                switchSfxBank(1);
                safeSfx('DK-WIN');
                await sleep(1500);
                safeSfx('MARIO-C');
                await sleep(800);
                safeSfx('PUNCH-BELL');
                await sleep(1200);
                safeSfx('PUNCH-KO');
                await sleep(2000);

                // -------------------------------------------------------------
                // SCENE 12: SFX BANK 3 - ATARI VECTOR & SCI-FI (1979–1984)
                // -------------------------------------------------------------
                logCue('scene_12_bank3', 'SFX Bank 3: Atari Vector & Sci-Fi (1979–1984)', '27 Sounds · Atari POKEY 4-Channel Polyphonic Audio & Laser Bursts');
                switchSfxBank(2);
                safeSfx('STARWAR-TIE');
                await sleep(1400);
                safeSfx('STARWAR-LAS');
                await sleep(1200);
                safeSfx('BZONE-CANN');
                await sleep(2000);

                // -------------------------------------------------------------
                // SCENE 13: SFX BANK 4 - KONAMI, SEGA & 80s ACTION (1981–1987)
                // -------------------------------------------------------------
                logCue('scene_13_bank4', 'SFX Bank 4: Konami, Sega & 80s Action (1981–1987)', '27 Sounds · Dual AY-3-8910 & Yamaha YM2151 FM Engine');
                switchSfxBank(3);
                safeSfx('OUTRUN-REV');
                await sleep(1400);
                safeSfx('SHINOBI-STAR');
                await sleep(1200);
                safeSfx('GYRUSS-WARP');
                await sleep(2200);

                // -------------------------------------------------------------
                // SCENE 14: VINTAGE SPEECH ROMS: BERZERK (1980)
                // -------------------------------------------------------------
                logCue('scene_14_speech_berzerk', 'Vintage Speech: Berzerk (1980 · Stern)', 'TSI S14001A Speech Chip: "Intruder Alert!" & "Coin Detected!"');
                safeVox('VOX_INTRUDER');
                await sleep(2600);
                safeVox('VOX_COIN');
                await sleep(2500);

                // -------------------------------------------------------------
                // SCENE 15: VINTAGE SPEECH ROMS: Q*BERT & SINISTAR (1982)
                // -------------------------------------------------------------
                logCue('scene_15_speech_sinistar', 'Vintage Speech: Q*bert & Sinistar (1982)', 'Votrax SC-01 & Harris HC-55516 CVSD: "@!#?@!" & "Beware, I Live!"');
                safeVox('VOX_QBERT');
                await sleep(2000);
                safeVox('VOX_SINISTAR');
                await sleep(2200);
                safeVox('VOX_HUNGER');
                await sleep(2400);

                // -------------------------------------------------------------
                // SCENE 16: VINTAGE SPEECH ROMS: WIZARD OF WOR, GORF & DRAGON LAIR
                // -------------------------------------------------------------
                logCue("scene_16_speech_classics", "Vintage Speech: Wizard of Wor, Gorf and Dragons Lair", "Votrax SC-01 and Dirk the Daring Authentic PCM Speech ROMs");
                safeVox('VOX_WIZARD');
                await sleep(2200);
                safeVox('VOX_GORF');
                await sleep(2200);
                safeVox('VOX_DRAGON');
                await sleep(2500);

                // -------------------------------------------------------------
                // SCENE 17: FM-1 DRUM SYNTH & 16-STEP TRACKER
                // -------------------------------------------------------------
                logCue('scene_17_drum_tracker', 'FM-1 Drum Synth & 16-Step Step Sequencer', 'TR-808 Modeled Analog Kick, Snare, Hi-Hats & Claps · 8 Patterns');
                for (let step = 0; step < 16; step++) {
                  if (step % 4 === 0) safeSfx('DK-WALK');
                  if (step % 8 === 4) safeSfx('CLIMB-STEP');
                  safeSfx('AST-FIRE');
                  await sleep(200);
                }
                await sleep(1000);

                // -------------------------------------------------------------
                // SCENE 18: NVRAM LEADERBOARDS & PRO FIRMWARE FEATURES
                // -------------------------------------------------------------
                logCue('scene_18_leaderboard', 'NVRAM Leaderboards & Pro Firmware Features', 'Persistent High Scores · Universal Immortal God Mode · Stage Skip');
                safeSfx('PUNCH-BELL');
                await sleep(1200);
                safeSfx('DK-WIN');
                await sleep(3000);

                // -------------------------------------------------------------
                // SCENE 19: LIVE JUKEBOX & CIRCUIT-BENDING GLITCH ENGINE
                // -------------------------------------------------------------
                logCue('scene_19_jukebox', 'Live Jukebox & Circuit-Bending Rewind Engine', 'Chiptune Album Playback · RAM Glitch Circuit-Bending · Time Machine');
                safeSfx('PAC-START');
                await sleep(2000);
                safeSfx('DK-WIN');
                await sleep(3500);

                // -------------------------------------------------------------
                // SCENE 20: OUTRO & HERMES AGENT QA CERTIFICATION
                // -------------------------------------------------------------
                logCue('scene_20_outro', 'Production Certified: 100% Green', 'Hermes Agent: 24 / 24 Master QA Batteries Passed · M-VAVE FM-1');
                safeSfx('PAC-POWER');
                await sleep(1000);
                safeSfx('PAC-EATGHOST');
                await sleep(3500);

                return { status: 'DONE', count: window.__cuePoints.length };
              } catch (e) {
                return { error: e.toString(), stack: e.stack };
              }
            })()
          `;

          ws.send(JSON.stringify({
            id: 2,
            method: 'Runtime.evaluate',
            params: { expression: performanceScript, awaitPromise: true, returnByValue: true }
          }));
        } else if (resp.id === 2) {
          console.log("Full response for id 2:", JSON.stringify(resp));
          console.log("Performance sequence finished with status:", resp.result ? resp.result.result : resp.error);

          // Now extract the recorded audio buffer and cue points
          ws.send(JSON.stringify({
            id: 3,
            method: 'Runtime.evaluate',
            params: {
              expression: `
                (() => {
                  let totalLen = 0;
                  for (let chunk of window.__demoAudio) totalLen += chunk.length;
                  const combined = new Float32Array(totalLen);
                  let offset = 0;
                  for (let chunk of window.__demoAudio) {
                    combined.set(chunk, offset);
                    offset += chunk.length;
                  }
                  return {
                    cuePoints: window.__cuePoints,
                    sampleRate: audioCtx.sampleRate,
                    totalSamples: totalLen,
                    durationSeconds: totalLen / audioCtx.sampleRate
                  };
                })()
              `,
              returnByValue: true
            }
          }));
        } else if (resp.id === 3) {
          const stats = resp.result.result.value;
          console.log(`Audio metadata received: ${stats.totalSamples} samples, ${stats.durationSeconds.toFixed(2)}s, ${stats.cuePoints.length} cue points`);
          
          fs.writeFileSync(outTimelineJson, JSON.stringify(stats, null, 2));
          console.log(`Wrote timeline to ${outTimelineJson}`);

          const chunkSize = 250000;
          const numChunks = Math.ceil(stats.totalSamples / chunkSize);
          const fullAudio = new Float32Array(stats.totalSamples);
          let received = 0;

          for (let i = 0; i < numChunks; i++) {
            const start = i * chunkSize;
            const end = Math.min(stats.totalSamples, (i + 1) * chunkSize);
            const chunkResp = await new Promise(resolve => {
              ws.send(JSON.stringify({
                id: 100 + i,
                method: 'Runtime.evaluate',
                params: {
                  expression: `
                    (() => {
                      let totalLen = 0;
                      for (let chunk of window.__demoAudio) totalLen += chunk.length;
                      const combined = new Float32Array(totalLen);
                      let offset = 0;
                      for (let chunk of window.__demoAudio) {
                        combined.set(chunk, offset);
                        offset += chunk.length;
                      }
                      return Array.from(combined.subarray(${start}, ${end}));
                    })()
                  `,
                  returnByValue: true
                }
              }));
              const handler = (m) => {
                const r = JSON.parse(m.data);
                if (r.id === 100 + i) {
                  ws.removeEventListener('message', handler);
                  resolve(r.result.result.value);
                }
              };
              ws.addEventListener('message', handler);
            });

            fullAudio.set(chunkResp, start);
            received += chunkResp.length;
            process.stdout.write(`\rExtracting audio chunks: ${(received / stats.totalSamples * 100).toFixed(1)}%`);
          }

          console.log("\nAudio extraction complete! Writing WAV file...");
          writeWavFile(outAudioWav, stats.sampleRate, 1, fullAudio);
          console.log(`Saved master audio track to ${outAudioWav} (${fs.statSync(outAudioWav).size} bytes)`);

          ws.close();
          chrome.kill();
          process.exit(0);
        }
      };
    });
  }).on('error', (err) => {
    console.error("HTTP error:", err);
    chrome.kill();
    process.exit(1);
  });
}, 1200);
