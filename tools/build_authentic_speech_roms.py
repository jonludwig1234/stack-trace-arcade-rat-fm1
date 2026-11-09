#!/usr/bin/env python3
"""
Build Authentic 1980s Vintage Arcade Speech ROM Engine.
Encodes authentic digitized audio from Berzerk, Q*bert, Sinistar,
Wizard of Wor, Gorf, and Dragon's Lair into base64 data URIs.
"""
import os
import base64
import subprocess

SAMPLES = [
    {
        "id": "VOX_INTRUDER",
        "name": "Intruder Alert!",
        "game": "Berzerk (1980 · Stern)",
        "chip": "TSI S14001A",
        "icon": "🤖",
        "text": "IN-TRU-DER A-LERT! IN-TRU-DER A-LERT!",
        "path": "/home/jon/.gemini/antigravity/scratch/fm1-pacman/web/audio/speech/berzerk_intruder.wav"
    },
    {
        "id": "VOX_COIN",
        "name": "Coin Detected!",
        "game": "Berzerk (1980 · Stern)",
        "chip": "TSI S14001A",
        "icon": "🪙",
        "text": "COIN DE-TEC-TED IN POCK-ET!",
        "path": "/home/jon/.gemini/antigravity/scratch/fm1-pacman/web/audio/speech/berzerk_coin.wav"
    },
    {
        "id": "VOX_QBERT",
        "name": "@!#?@! Swear",
        "game": "Q*bert (1982 · Gottlieb)",
        "chip": "VOTRAX SC-01",
        "icon": "🤬",
        "text": "@!#?@! VOTRAX SPEECH SYNTH",
        "path": "/home/jon/.gemini/antigravity/scratch/fm1-pacman/web/audio/speech/qbert_swear.wav"
    },
    {
        "id": "VOX_SINISTAR",
        "name": "Beware, I Live!",
        "game": "Sinistar (1982 · Williams)",
        "chip": "HC-55516 CVSD",
        "icon": "👹",
        "text": "BE-WARE, I LIVE!",
        "path": "/home/jon/.gemini/antigravity/scratch/fm1-pacman/web/audio/speech/bewareil.wav"
    },
    {
        "id": "VOX_HUNGER",
        "name": "I Hunger, Coward!",
        "game": "Sinistar (1982 · Williams)",
        "chip": "HC-55516 CVSD",
        "icon": "💀",
        "text": "I HUN-GER, CO-WARD!",
        "path": "/home/jon/.gemini/antigravity/scratch/fm1-pacman/web/audio/speech/ihungerc.wav"
    },
    {
        "id": "VOX_WIZARD",
        "name": "Wizard of Wor",
        "game": "Wizard of Wor (1980 · Midway)",
        "chip": "VOTRAX SC-01",
        "icon": "🧙",
        "text": "I AM THE WIZ-ARD OF WOR!",
        "path": "/home/jon/.gemini/antigravity/scratch/fm1-pacman/web/audio/speech/wizard_of_wor.wav"
    },
    {
        "id": "VOX_GORF",
        "name": "Long Live Gorf!",
        "game": "GORF (1981 · Midway)",
        "chip": "VOTRAX SC-01",
        "icon": "🛸",
        "text": "LONG LIVE GORF! HA-HA-HA-HA!",
        "path": "/home/jon/.gemini/antigravity/scratch/fm1-pacman/web/audio/speech/gorf_long_live.wav"
    },
    {
        "id": "VOX_DRAGON",
        "name": "Lead On Adventurer!",
        "game": "Dragon's Lair (1983 · Cinematronics)",
        "chip": "8-BIT LINEAR PCM",
        "icon": "🗡️",
        "text": "LEAD ON, AD-VEN-TUR-ER!",
        "path": "/home/jon/.gemini/antigravity/scratch/fm1-pacman/web/audio/speech/lead_on_adventurer.wav"
    }
]

def main():
    encoded_samples = []
    for item in SAMPLES:
        mp3_out = f"/tmp/final_{item['id']}.mp3"
        subprocess.run([
            "/home/jon/.local/bin/ffmpeg", "-y", "-i", item["path"],
            "-codec:a", "libmp3lame", "-b:a", "48k", "-ar", "22050", "-ac", "1",
            mp3_out
        ], stderr=subprocess.DEVNULL, check=True)
        with open(mp3_out, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        data_uri = f"data:audio/mp3;base64,{b64}"
        encoded_samples.append({
            "id": item["id"],
            "name": item["name"],
            "game": item["game"],
            "chip": item["chip"],
            "icon": item["icon"],
            "text": item["text"],
            "dataUri": data_uri
        })
        print(f"Encoded {item['id']}: {len(data_uri)} chars URI")

    import json
    # Generate speech_sample_engine.py
    js_samples = "[\n"
    for s in encoded_samples:
        js_samples += f"  {{\n    id: {json.dumps(s['id'])},\n    name: {json.dumps(s['name'])},\n    game: {json.dumps(s['game'])},\n    chip: {json.dumps(s['chip'])},\n    icon: {json.dumps(s['icon'])},\n    text: {json.dumps(s['text'])},\n    dataUri: {json.dumps(s['dataUri'])}\n  }},\n"
    js_samples += "]"

    engine_py_content = f'''#!/usr/bin/env python3
"""
Vintage Arcade Speech & PCM Sample-ROM Synthesizer for M-VAVE FM-1.
Authentic 1980s digitized arcade voice samples (Berzerk, Q*bert, Sinistar,
Wizard of Wor, Gorf, Dragon's Lair) embedded as base64 audio and decoded
via Web Audio API with direct mixer integration.
"""

def get_speech_sample_engine_js():
    return \'\'\'
// =========================================================================
// AUTHENTIC VINTAGE ARCADE SPEECH & PCM SAMPLE-ROM SYNTHESIZER
// =========================================================================
const ARCADE_SPEECH_SAMPLES = {js_samples};

const decodedSpeechBuffers = {{}};

function playArcadeSpeechSample(id) {{
  initAudio();
  if (typeof audioCtx !== 'undefined' && audioCtx && audioCtx.state === 'suspended') {{
    audioCtx.resume();
  }}

  // Handle aliases
  if (id === 'VOX_DANGER') id = 'VOX_DRAGON';
  if (id === 'VOX_ARCADE_RAT') id = 'VOX_GORF';

  const sample = ARCADE_SPEECH_SAMPLES.find(s => s.id === id);
  if (!sample) return;

  // 1. Update UI telemetry and visual badge
  const el = document.getElementById('sfxLastTriggered');
  if (el) el.innerHTML = `VOX: <b style="color:#00ff66;">${{sample.name}}</b> (${{sample.game}}) · "${{sample.text}}"`;
  const voxStatus = document.getElementById('speechStatusDisplay');
  if (voxStatus) voxStatus.innerHTML = `NOW SPEAKING: <b style="color:#00e5ff;">${{sample.name}}</b> [${{sample.chip}} · ${{sample.game}}] · <em>"${{sample.text}}"</em>`;

  const card = document.getElementById('card_' + id);
  if (card) {{
    card.classList.add('speech-card-active');
    setTimeout(() => card.classList.remove('speech-card-active'), 500);
  }}

  // 2. Play authentic digitized voice sample via Web Audio API BufferSource
  if (typeof audioCtx !== 'undefined' && audioCtx) {{
    if (decodedSpeechBuffers[id]) {{
      playBuffer(decodedSpeechBuffers[id]);
    }} else {{
      // Fetch and decode data URI into AudioBuffer
      fetch(sample.dataUri)
        .then(res => res.arrayBuffer())
        .then(ab => audioCtx.decodeAudioData(ab))
        .then(audioBuffer => {{
          decodedSpeechBuffers[id] = audioBuffer;
          playBuffer(audioBuffer);
        }})
        .catch(err => {{
          console.warn('Web Audio decode fallback, using HTML5 Audio:', err);
          playHtmlAudio(sample.dataUri);
        }});
    }}
  }} else {{
    playHtmlAudio(sample.dataUri);
  }}

  function playBuffer(buf) {{
    try {{
      const src = audioCtx.createBufferSource();
      src.buffer = buf;
      const gain = audioCtx.createGain();
      gain.gain.value = 1.0;
      src.connect(gain);
      if (typeof filterNode !== 'undefined' && filterNode) {{
        gain.connect(filterNode);
      }} else if (typeof masterGain !== 'undefined' && masterGain) {{
        gain.connect(masterGain);
      }} else {{
        gain.connect(audioCtx.destination);
      }}
      src.start(0);
    }} catch (e) {{
      playHtmlAudio(sample.dataUri);
    }}
  }}

  function playHtmlAudio(uri) {{
    try {{
      const a = new Audio(uri);
      a.volume = 1.0;
      a.play().catch(e => console.warn('HTML5 Audio playback prevented:', e));
    }} catch (e) {{}}
  }}
}}

// Global aliases for compatibility
const playSpeechSample = playArcadeSpeechSample;
function speakArcadePhrase(id) {{
  // Legacy alias redirects to authentic sample playback
  playArcadeSpeechSample(id);
}}
\'\'\'

if __name__ == "__main__":
    print(f"Generated {{len(get_speech_sample_engine_js())}} bytes of Speech Synthesizer JS.")
'''

    with open("tools/speech_sample_engine.py", "w", encoding="utf-8") as f:
        f.write(engine_py_content)
    print("Successfully generated tools/speech_sample_engine.py!")

if __name__ == "__main__":
    main()
