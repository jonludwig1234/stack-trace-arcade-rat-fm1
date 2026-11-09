/* SPDX-License-Identifier: GPL-3.0-only WITH GPL-3.0-linking-exception
 * Multi-Engine Full Demo Songs for M-VAVE FM-1.
 * Provides complete multi-track sequenced compositions for:
 * 1. Namco WSG (3 Tracks) - "Namco Neon"
 * 2. AY-3-8910 (15 Tracks Max) - "Gyruss Cosmic Odyssey"
 * 3. Atari POKEY (4 Tracks) - "Tempest Vector Surge"
 * 4. Nintendo DAC (4 Tracks) - "Plumber's Jump"
 */
#ifndef PAC_DEMO_SONGS_H
#define PAC_DEMO_SONGS_H

#include <stdint.h>
#include <stdbool.h>

#define MAX_DEMO_TRACKS 15
#define DEMO_PATTERN_STEPS 64

typedef enum {
    SONG_NAMCO_NEON,      /* 3 Tracks (Namco WSG 4-bit wavetable) */
    SONG_GYRUSS_ODYSSEY,  /* 15 Tracks (5x AY-3-8910 Chiptune Symphony) */
    SONG_TEMPEST_SURGE,   /* 4 Tracks (Atari POKEY Distortion & Laser) */
    SONG_PLUMBERS_JUMP,   /* 4 Tracks (Nintendo DAC Bouncy Ragtime) */
    SONG_COUNT
} demo_song_id_t;

typedef struct {
    uint8_t note;         /* MIDI note number (0 = rest) */
    uint8_t volume;       /* 0..15 */
    uint8_t instrument;   /* Waveform / timbre index */
    uint8_t effect;       /* Arp, glide, or noise flag */
} tracker_step_t;

typedef struct {
    const char *title;
    const char *synth_engine;
    uint8_t track_count;
    uint16_t bpm;
    uint16_t total_steps;
    const tracker_step_t *tracks[MAX_DEMO_TRACKS];
} demo_song_t;

extern const demo_song_t g_demo_songs[SONG_COUNT];

/* Sequencer state */
typedef struct {
    demo_song_id_t current_song;
    uint16_t current_step;
    uint16_t tick_counter;
    bool playing;
    bool loop;
} demo_player_t;

void demo_player_init(demo_player_t *player);
void demo_player_select(demo_player_t *player, demo_song_id_t song_id);
void demo_player_play(demo_player_t *player);
void demo_player_stop(demo_player_t *player);
void demo_player_tick(demo_player_t *player);

#endif /* PAC_DEMO_SONGS_H */
