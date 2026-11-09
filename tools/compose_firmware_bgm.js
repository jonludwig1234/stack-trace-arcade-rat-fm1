const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const port = 9342;
const url = 'http://localhost:8085/fm1_pacman_preview.html';
const foregroundWavPath = path.resolve(__dirname, '../web/demo_soundtrack.wav');
const masterWavPath = path.resolve(__dirname, '../web/demo_soundtrack.wav');
const musicOnlyWavPath = path.resolve(__dirname, '../web/demo_bgm_music.wav');

console.log("Composing background music using M-VAVE FM-1 firmware synthesis engines...");

function writeWavFile(filePath, sampleRate, numChannels, leftSamples, rightSamples) {
  const numSamples = leftSamples.length;
  const byteRate = sampleRate * numChannels * 2;
  const blockAlign = numChannels * 2;
  const header = Buffer.alloc(44);
  header.write('RIFF', 0);
  header.writeUInt32LE(36 + numSamples * numChannels * 2, 4);
  header.write('WAVE', 8);
  header.write('fmt ', 12);
  header.writeUInt32LE(16, 16);
  header.writeUInt16LE(1, 20); // PCM
  header.writeUInt16LE(numChannels, 22);
  header.writeUInt32LE(sampleRate, 24);
  header.writeUInt32LE(byteRate, 28);
  header.writeUInt16LE(blockAlign, 32);
  header.writeUInt16LE(16, 34); // 16-bit
  header.write('data', 36);
  header.writeUInt32LE(numSamples * numChannels * 2, 40);

  const data = Buffer.alloc(numSamples * numChannels * 2);
  for (let i = 0; i < numSamples; i++) {
    let l = Math.max(-1, Math.min(1, leftSamples[i]));
    let r = Math.max(-1, Math.min(1, (rightSamples ? rightSamples[i] : leftSamples[i])));
    let valL = Math.round(l < 0 ? l * 0x8000 : l * 0x7FFF);
    let valR = Math.round(r < 0 ? r * 0x8000 : r * 0x7FFF);
    if (numChannels === 1) {
      data.writeInt16LE(valL, i * 2);
    } else {
      data.writeInt16LE(valL, i * 4);
      data.writeInt16LE(valR, i * 4 + 2);
    }
  }

  fs.writeFileSync(filePath, Buffer.concat([header, data]));
}

function readWavSamples(filePath) {
  const buf = fs.readFileSync(filePath);
  const numChannels = buf.readUInt16LE(22);
  const sampleRate = buf.readUInt32LE(24);
  const bitsPerSample = buf.readUInt16LE(34);
  const dataOffset = buf.indexOf('data') + 8;
  const numSamples = (buf.length - dataOffset) / (numChannels * 2);

  const samples = new Float32Array(numSamples);
  for (let i = 0; i < numSamples; i++) {
    const raw = buf.readInt16LE(dataOffset + i * numChannels * 2);
    samples[i] = raw / 32768.0;
  }
  return { samples, sampleRate, numChannels };
}

const chrome = spawn('google-chrome', [
  '--headless=new',
  `--remote-debugging-port=${port}`,
  '--disable-gpu',
  '--no-sandbox',
  url
]);

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
        
        // This browser script composes and renders the complete 107-second background score
        // using the firmware's multi-engine chiptune and drum synthesis.
        const compositionCode = `
          (async () => {
            const sampleRate = 44100;
            const totalDuration = 107.0; // 107 seconds
            const totalSamples = Math.ceil(totalDuration * sampleRate);
            const offCtx = new OfflineAudioContext(2, totalSamples, sampleRate);

            // Master BGM Bus with warm arcade low-pass filtering and gentle compression
            const masterBgmGain = offCtx.createGain();
            masterBgmGain.gain.value = 0.42; // Tastefully mixed backing level

            const filter = offCtx.createBiquadFilter();
            filter.type = 'lowpass';
            filter.frequency.value = 9500;
            filter.Q.value = 0.7;

            masterBgmGain.connect(filter);
            filter.connect(offCtx.destination);

            // Synthesizer Helper Functions modeled on firmware's playTrackNote & drum synth
            const mtof = n => 440 * Math.pow(2, (n - 69) / 12);

            // 1. Kick Drum
            function triggerKick(t, vol = 1.0) {
              const osc = offCtx.createOscillator();
              const g = offCtx.createGain();
              osc.type = 'sine';
              osc.frequency.setValueAtTime(140, t);
              osc.frequency.exponentialRampToValueAtTime(45, t + 0.10);
              g.gain.setValueAtTime(0.7 * vol, t);
              g.gain.exponentialRampToValueAtTime(0.001, t + 0.12);
              osc.connect(g); g.connect(masterBgmGain);
              osc.start(t); osc.stop(t + 0.13);
            }

            // 2. Snare Drum
            function triggerSnare(t, vol = 1.0) {
              // Tone body
              const osc = offCtx.createOscillator();
              const oscG = offCtx.createGain();
              osc.type = 'triangle';
              osc.frequency.setValueAtTime(180, t);
              osc.frequency.exponentialRampToValueAtTime(70, t + 0.08);
              oscG.gain.setValueAtTime(0.35 * vol, t);
              oscG.gain.exponentialRampToValueAtTime(0.001, t + 0.09);
              osc.connect(oscG); oscG.connect(masterBgmGain);
              osc.start(t); osc.stop(t + 0.10);

              // Snare snap
              const oscNoise = offCtx.createOscillator();
              const nG = offCtx.createGain();
              oscNoise.type = 'sawtooth';
              oscNoise.frequency.setValueAtTime(1200, t);
              oscNoise.frequency.exponentialRampToValueAtTime(300, t + 0.12);
              nG.gain.setValueAtTime(0.30 * vol, t);
              nG.gain.exponentialRampToValueAtTime(0.001, t + 0.14);
              oscNoise.connect(nG); nG.connect(masterBgmGain);
              oscNoise.start(t); oscNoise.stop(t + 0.15);
            }

            // 3. Hi-Hat
            function triggerHiHat(t, open = false, vol = 1.0) {
              const osc = offCtx.createOscillator();
              const g = offCtx.createGain();
              osc.type = 'sawtooth';
              osc.frequency.setValueAtTime(7500, t);
              const dur = open ? 0.12 : 0.04;
              g.gain.setValueAtTime(0.18 * vol, t);
              g.gain.exponentialRampToValueAtTime(0.001, t + dur);
              osc.connect(g); g.connect(masterBgmGain);
              osc.start(t); osc.stop(t + dur + 0.01);
            }

            // 4. Synthesizer Tone (WSG, AY-3-8910, POKEY, 2A03)
            function playNote(chipType, note, t, dur, vol = 1.0, pan = 0.0) {
              if (note <= 0 || vol <= 0) return;
              const freq = mtof(note);
              const osc = offCtx.createOscillator();
              const g = offCtx.createGain();

              if (chipType === 'wsg') {
                osc.type = 'triangle'; // Smooth round Namco WSG wave
              } else if (chipType === 'ay8910') {
                osc.type = 'square';   // Pure 50% chiptune square wave
              } else if (chipType === 'pokey') {
                osc.type = 'sawtooth'; // Raw aggressive Atari POKEY wave
              } else {
                osc.type = 'square';   // NES 2A03 pulse wave
              }

              osc.frequency.setValueAtTime(freq, t);
              
              // Stereo Panner
              const panner = offCtx.createStereoPanner ? offCtx.createStereoPanner() : null;
              if (panner) panner.pan.value = pan;

              g.gain.setValueAtTime(0.20 * vol, t);
              g.gain.exponentialRampToValueAtTime(0.001, t + dur * 0.95);

              if (panner) {
                osc.connect(g); g.connect(panner); panner.connect(masterBgmGain);
              } else {
                osc.connect(g); g.connect(masterBgmGain);
              }
              osc.start(t); osc.stop(t + dur);
            }

            // =================================================================
            // THE 5-MOVEMENT ARCADE FIRMWARE SYMPHONY
            // =================================================================

            // -----------------------------------------------------------------
            // MOVEMENT 1: "The Golden Age Awakening" (0.0s - 25.0s, 128 BPM)
            // Pac-Man & Galaga themes, 2A03 Tri-Bass + WSG Melody
            // -----------------------------------------------------------------
            const bpm1 = 128;
            const step1 = 60 / bpm1 / 4; // 16th note
            const bassNotesM1 = [36, 36, 48, 36,  39, 39, 51, 39,  41, 41, 53, 41,  43, 43, 55, 43];
            const leadNotesM1 = [60,  0, 63,  0,  67,  0, 70,  0,  72, 70, 67, 65,  67,  0, 60,  0];
            const arpNotesM1  = [72, 75, 79, 84,  75, 79, 84, 87,  77, 80, 84, 89,  79, 82, 86, 91];

            for (let t = 0.5; t < 25.0; t += step1 * 16) {
              for (let s = 0; s < 16; s++) {
                const curT = t + s * step1;
                if (curT >= 25.0) break;

                // Drums
                if (s % 4 === 0) triggerKick(curT, 0.9);
                if (s % 8 === 4) triggerSnare(curT, 0.85);
                triggerHiHat(curT, s % 4 === 2, 0.7);

                // Bass (2A03)
                playNote('wsg', bassNotesM1[s], curT, step1 * 1.5, 1.1, -0.15);

                // Arp (WSG Triangle)
                if (s % 2 === 0) {
                  playNote('wsg', arpNotesM1[s], curT, step1 * 0.9, 0.6, 0.35);
                }

                // Lead (AY-3-8910 Square)
                if (leadNotesM1[s] > 0 && curT > 4.0) {
                  playNote('ay8910', leadNotesM1[s], curT, step1 * 2.0, 0.85, 0.1);
                }
              }
            }

            // -----------------------------------------------------------------
            // MOVEMENT 2: "Vector Space Flight" (25.0s - 57.0s, 138 BPM)
            // Donkey Kong, Frogger, Asteroids, Tempest, Gyruss
            // Referencing Bach Toccata & Fugue in D minor + High-Speed POKEY Arps
            // -----------------------------------------------------------------
            const bpm2 = 138;
            const step2 = 60 / bpm2 / 4;
            const bassNotesM2 = [38, 38, 50, 38,  41, 41, 53, 41,  45, 45, 57, 45,  43, 43, 55, 43];
            // Bach Toccata theme motifs in D minor: D5, C#5, D5, A4, F4, D4...
            const bachLeadM2  = [74, 73, 74,  0,  69,  0, 65,  0,  62,  0, 65,  0,  69,  0, 74,  0];
            const vectorArpM2 = [74, 77, 81, 86,  77, 81, 86, 89,  81, 84, 88, 93,  79, 82, 86, 91];

            for (let t = 25.0; t < 57.0; t += step2 * 16) {
              for (let s = 0; s < 16; s++) {
                const curT = t + s * step2;
                if (curT >= 57.0) break;

                // Driving 4-on-the-floor Kick + Upbeat Hi-hats
                if (s % 4 === 0) triggerKick(curT, 1.0);
                if (s % 8 === 4) triggerSnare(curT, 0.9);
                triggerHiHat(curT, s % 2 === 1, 0.75);

                // Heavy POKEY Sawtooth Bass
                playNote('pokey', bassNotesM2[s], curT, step2 * 1.8, 1.15, -0.2);

                // 16th-note Vector Arp
                playNote('ay8910', vectorArpM2[s], curT, step2 * 0.8, 0.65, 0.4);

                // Melodic Lead
                if (bachLeadM2[s] > 0) {
                  playNote('ay8910', bachLeadM2[s], curT, step2 * 1.5, 0.95, 0.0);
                }
              }
            }

            // -----------------------------------------------------------------
            // MOVEMENT 3: "The 108 Soundboard Dub" (57.0s - 78.0s, 126 BPM)
            // SFX Banks 1 to 4: Half-time groove, wide stereo delay chords
            // -----------------------------------------------------------------
            const bpm3 = 126;
            const step3 = 60 / bpm3 / 4;
            const bassNotesM3 = [31,  0, 31, 43,   0, 34,  0, 36,  31,  0, 31, 43,   0, 38, 36, 34];
            const chordM3     = [55, 58, 62, 67]; // G minor 7

            for (let t = 57.0; t < 78.0; t += step3 * 16) {
              for (let s = 0; s < 16; s++) {
                const curT = t + s * step3;
                if (curT >= 78.0) break;

                // Dub Half-Time Beats
                if (s === 0 || s === 10) triggerKick(curT, 1.0);
                if (s === 8) triggerSnare(curT, 1.0);
                if (s % 2 === 0) triggerHiHat(curT, s === 4 || s === 12, 0.6);

                // Deep Sub Bass
                if (bassNotesM3[s] > 0) {
                  playNote('wsg', bassNotesM3[s], curT, step3 * 2.2, 1.25, 0.0);
                }

                // Staccato Dub Chords on off-beats
                if (s === 4 || s === 12) {
                  chordM3.forEach((n, idx) => {
                    playNote('ay8910', n, curT, step3 * 1.2, 0.45, (idx - 1.5) * 0.3);
                  });
                }
              }
            }

            // -----------------------------------------------------------------
            // MOVEMENT 4: "Cybernetic Voices & Tracker Beat" (78.0s - 100.0s, 132 BPM)
            // Speech ROMs (Berzerk, Sinistar, etc.) + 16-Step Drum Tracker
            // Electro-synthwave groove leaving vocal band (500Hz-3.5kHz) open
            // -----------------------------------------------------------------
            const bpm4 = 132;
            const step4 = 60 / bpm4 / 4;
            const bassNotesM4 = [33, 33, 45, 33,  36, 36, 48, 36,  38, 38, 50, 38,  40, 40, 52, 40];
            const synthArpM4  = [69, 72, 76, 81,  72, 76, 81, 84,  74, 77, 81, 86,  76, 79, 83, 88];

            for (let t = 78.0; t < 100.0; t += step4 * 16) {
              for (let s = 0; s < 16; s++) {
                const curT = t + s * step4;
                if (curT >= 100.0) break;

                // Punchy TR-808 Electro Rhythm
                if (s % 4 === 0) triggerKick(curT, 0.95);
                if (s % 8 === 4) triggerSnare(curT, 0.85);
                if (s % 2 === 1) triggerHiHat(curT, false, 0.65);

                // Funky Syncopated Bass (A minor)
                playNote('wsg', bassNotesM4[s], curT, step4 * 1.6, 1.1, -0.25);

                // Shimmering High Arpeggios (above voice range)
                playNote('pokey', synthArpM4[s], curT, step4 * 0.75, 0.55, 0.35);
              }
            }

            // -----------------------------------------------------------------
            // MOVEMENT 5: "Grand Finale & Hermes Victory Climax" (100.0s - 107.0s, 132 BPM)
            // Glorious ascending arcade fanfare culminating in C major chord!
            // -----------------------------------------------------------------
            const bpm5 = 132;
            const step5 = 60 / bpm5 / 4;
            const victoryNotes = [60, 64, 67, 72,  65, 69, 72, 77,  67, 71, 74, 79,  72, 76, 79, 84];
            
            for (let s = 0; s < 16; s++) {
              const curT = 100.0 + s * step5;
              if (curT >= 107.0) break;

              triggerKick(curT, 1.0);
              if (s % 4 === 2) triggerSnare(curT, 1.0);
              triggerHiHat(curT, true, 0.8);

              // Ascending bass
              playNote('pokey', 36 + Math.floor(s / 4) * 2, curT, step5 * 2.0, 1.2, -0.2);

              // Triumphant double-lead
              playNote('ay8910', victoryNotes[s], curT, step5 * 1.8, 1.0, 0.0);
              playNote('wsg', victoryNotes[s] - 12, curT, step5 * 1.8, 0.9, 0.2);
            }

            // Final Climax Chord at 104.0s (C Major Grand Arcade Chord)
            const finalChord = [36, 48, 60, 64, 67, 72, 84];
            finalChord.forEach((note, idx) => {
              playNote(idx % 2 === 0 ? 'pokey' : 'wsg', note, 103.8, 3.0, 1.1, (idx - 3) * 0.2);
            });
            triggerKick(103.8, 1.2);
            triggerSnare(103.8, 1.2);

            console.log("Starting offline render of 107s background music...");
            const renderedBuffer = await offCtx.startRendering();
            console.log("Offline render finished successfully!");

            const left = Array.from(renderedBuffer.getChannelData(0));
            const right = Array.from(renderedBuffer.getChannelData(1));
            return {
              sampleRate: renderedBuffer.sampleRate,
              totalSamples: renderedBuffer.length,
              duration: renderedBuffer.duration,
              left,
              right
            };
          })()
        `;

        ws.send(JSON.stringify({
          id: 1,
          method: 'Runtime.evaluate',
          params: { expression: compositionCode, awaitPromise: true, returnByValue: true }
        }));
      };

      ws.onmessage = async (msg) => {
        const resp = JSON.parse(msg.data);
        if (resp.id === 1) {
          if (resp.result && resp.result.result && resp.result.result.value) {
            const resData = resp.result.result.value;
            console.log(`Rendered background score: ${resData.totalSamples} samples (${resData.duration.toFixed(2)}s)`);

            const leftSamples = new Float32Array(resData.left);
            const rightSamples = new Float32Array(resData.right);

            // Save the isolated music track
            writeWavFile(musicOnlyWavPath, resData.sampleRate, 2, leftSamples, rightSamples);
            console.log(`Saved isolated music track to ${musicOnlyWavPath} (${fs.statSync(musicOnlyWavPath).size} bytes)`);

            // Now perform master mix with the foreground SFX track!
            console.log("Loading foreground SFX & Speech track for broadcast mixing...");
            const fg = readWavSamples(foregroundWavPath);
            const totalLen = Math.max(leftSamples.length, fg.samples.length);

            const mixedLeft = new Float32Array(totalLen);
            const mixedRight = new Float32Array(totalLen);

            // Dynamic ducking & mastering pass
            for (let i = 0; i < totalLen; i++) {
              const bgmL = i < leftSamples.length ? leftSamples[i] : 0.0;
              const bgmR = i < rightSamples.length ? rightSamples[i] : 0.0;
              const fgSample = i < fg.samples.length ? fg.samples[i] : 0.0;

              // If foreground sound is active (> 0.05), apply gentle ducking (-3.5 dB)
              const fgEnergy = Math.abs(fgSample);
              const duckFactor = fgEnergy > 0.08 ? 0.65 : (fgEnergy > 0.02 ? 0.85 : 1.0);

              // Master mix: Background Music + Foreground SFX & Voices
              let mL = (bgmL * 0.82 * duckFactor) + (fgSample * 1.0);
              let mR = (bgmR * 0.82 * duckFactor) + (fgSample * 1.0);

              // Soft-clipping arcade limiter (tanh saturation)
              mixedLeft[i] = Math.tanh(mL);
              mixedRight[i] = Math.tanh(mR);
            }

            console.log("Master mix complete! Writing final master soundtrack...");
            writeWavFile(masterWavPath, resData.sampleRate, 2, mixedLeft, mixedRight);
            console.log(`Saved master mixed soundtrack to ${masterWavPath} (${fs.statSync(masterWavPath).size} bytes)`);

            ws.close();
            chrome.kill();
            process.exit(0);
          } else {
            console.error("Error in composition execution:", resp.result ? resp.result.result : resp.error);
            ws.close();
            chrome.kill();
            process.exit(1);
          }
        }
      };
    });
  }).on('error', (err) => {
    console.error("HTTP error:", err);
    chrome.kill();
    process.exit(1);
  });
}, 1200);
