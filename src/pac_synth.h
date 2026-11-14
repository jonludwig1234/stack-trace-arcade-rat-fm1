/* SPDX-License-Identifier: GPL-3.0-only WITH GPL-3.0-linking-exception
 * Namco 3-Voice Performance Synthesizer for M-VAVE FM-1.
 */
#ifndef PAC_SYNTH_H
#define PAC_SYNTH_H

#include "pac_wsg.h"
#include "pac_video.h"
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef struct {
    uint8_t current_waveform; /* 0..7 */
    uint8_t master_volume;    /* 0..15 */
    uint16_t attack_rate;
    uint16_t decay_rate;
    struct {
        int note;             /* Active MIDI note or -1 */
        uint16_t env_level;   /* 0..65535 */
        bool active;
    } voices[WSG_VOICES];
} pac_synth_t;

void pac_synth_init(pac_synth_t *s);
void pac_synth_key_event(pac_synth_t *s, wsg_chip_t *wsg, unsigned key_idx, bool pressed);
void pac_synth_tick(pac_synth_t *s, wsg_chip_t *wsg);
#ifndef __GCC_PI32V2__
void pac_synth_draw_ui(const pac_synth_t *s, const uint8_t *sound_rom, uint16_t *tft_output);
#else
void pac_synth_draw_ui_bands(const pac_synth_t *s, const uint8_t *sound_rom, pac_band_blit_fn blit_fn);
#endif

#endif /* PAC_SYNTH_H */
