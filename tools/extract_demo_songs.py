#!/usr/bin/env python3
"""
Extract 4 multi-engine demo songs from src/pac_demo_songs.c into JSON.
"""
import re
import json

notes = {
    "REST": 0, "C2": 36, "D2": 38, "E2": 40, "F2": 41, "G2": 43, "A2": 45, "B2": 47,
    "C3": 48, "Cs3": 49, "D3": 50, "Ds3": 51, "E3": 52, "F3": 53, "Fs3": 54, "G3": 55, "Gs3": 56, "A3": 57, "As3": 58, "B3": 59,
    "C4": 60, "Cs4": 61, "D4": 62, "Ds4": 63, "E4": 64, "F4": 65, "Fs4": 66, "G4": 67, "Gs4": 68, "A4": 69, "As4": 70, "B4": 71,
    "C5": 72, "Cs5": 73, "D5": 74, "Ds5": 75, "E5": 76, "F5": 77, "Fs5": 78, "G5": 79, "Gs5": 80, "A5": 81, "As5": 82, "B5": 83,
    "C6": 84, "D6": 86, "E6": 88
}

def extract_songs():
    with open("src/pac_demo_songs.c", "r") as f:
        c_code = f.read()

    pattern = r"static const tracker_step_t (s_\w+)\[64\] = \{([\s\S]*?)\};"
    matches = re.findall(pattern, c_code)

    tracks_dict = {}
    for name, body in matches:
        step_pat = r"\{([A-Za-z0-9_]+),\s*(\d+),\s*(\d+),\s*(\d+)\}"
        steps = []
        for note_str, vol, inst, fx in re.findall(step_pat, body):
            n = notes.get(note_str, int(note_str) if note_str.isdigit() else 0)
            steps.append([n, int(vol), int(inst), int(fx)])
        tracks_dict[name] = steps

    songs = [
        {
            "id": "namco_neon",
            "title": "Namco Neon",
            "synth": "Namco WSG 3-Voice Wavetable",
            "chipType": "wsg",
            "bpm": 128,
            "trackNames": ["Slap Bass", "Arp Lead", "Chiptune Hook"],
            "tracks": [
                tracks_dict["s_namco_trk0_bass"],
                tracks_dict["s_namco_trk1_arp"],
                tracks_dict["s_namco_trk2_lead"]
            ]
        },
        {
            "id": "gyruss_odyssey",
            "title": "Gyruss Cosmic Odyssey",
            "synth": "5x AY-3-8910 (15-Ch Baroque Symphony)",
            "chipType": "ay8910",
            "bpm": 144,
            "trackNames": [
                "Lead Organ 1", "Lead Organ 2", "Lead Organ 3",
                "Chords Voicing 1", "Chords Voicing 2", "Chords Voicing 3",
                "Cosmic Arp 1", "Cosmic Arp 2", "Cosmic Arp 3",
                "Sub Bass Pedal 1", "Sub Bass Pedal 2", "Sub Bass Pedal 3",
                "Noise Drums", "Metallic Hi-Hat", "Laser Crash FX"
            ],
            "tracks": [
                tracks_dict["s_gyruss_trk0_lead1"],
                tracks_dict["s_gyruss_trk1_lead2"],
                tracks_dict["s_gyruss_trk2_lead3"],
                tracks_dict["s_gyruss_trk3_chord1"],
                tracks_dict["s_gyruss_trk4_chord2"],
                tracks_dict["s_gyruss_trk5_chord3"],
                tracks_dict["s_gyruss_trk6_arp1"],
                tracks_dict["s_gyruss_trk7_arp2"],
                tracks_dict["s_gyruss_trk8_arp3"],
                tracks_dict["s_gyruss_trk9_bass1"],
                tracks_dict["s_gyruss_trk10_bass2"],
                tracks_dict["s_gyruss_trk11_bass3"],
                tracks_dict["s_gyruss_trk12_drums"],
                tracks_dict["s_gyruss_trk13_hihat"],
                tracks_dict["s_gyruss_trk14_laser"]
            ]
        },
        {
            "id": "tempest_surge",
            "title": "Tempest Vector Surge",
            "synth": "Atari POKEY 4-Voice Distortion",
            "chipType": "pokey",
            "bpm": 140,
            "trackNames": ["Distortion Saw Lead", "POKEY Sub-Bass", "Poly-Noise Drums", "Vector Laser Sweeps"],
            "tracks": [
                tracks_dict["s_tempest_trk0_lead"],
                tracks_dict["s_tempest_trk1_bass"],
                tracks_dict["s_tempest_trk2_noise"],
                tracks_dict["s_tempest_trk3_laser"]
            ]
        },
        {
            "id": "plumbers_jump",
            "title": "Plumber's Jump",
            "synth": "Nintendo Arcade DAC 4-Track Ragtime",
            "chipType": "dac",
            "bpm": 132,
            "trackNames": ["Ragtime Square Lead", "Stride Triangle Bass", "Syncopated Chords", "Bouncy SFX Drums"],
            "tracks": [
                tracks_dict["s_plumber_trk0_lead"],
                tracks_dict["s_plumber_trk1_bass"],
                tracks_dict["s_plumber_trk2_chord"],
                tracks_dict["s_plumber_trk3_drums"]
            ]
        }
    ]

    with open("tools/demo_songs.json", "w") as out:
        json.dump(songs, out, indent=2)

    print(f"Successfully exported {len(songs)} songs to tools/demo_songs.json!")

if __name__ == "__main__":
    extract_songs()
