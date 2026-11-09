/* SPDX-License-Identifier: GPL-3.0-only WITH GPL-3.0-linking-exception
 * Namco WSG (Waveform Sound Generator) for M-VAVE FM-1 (44.1 kHz stereo output).
 */
#ifndef PAC_WSG_H
#define PAC_WSG_H

#include <stdint.h>
#include <stdbool.h>

#define WSG_VOICES 3
#define WSG_NATIVE_RATE 96000
#define FM1_AUDIO_RATE 44100

typedef struct {
    uint32_t frequency;   /* 20-bit frequency value */
    uint32_t accumulator; /* 20-bit phase accumulator */
    uint8_t waveform_no;  /* 3-bit waveform (0..7) */
    uint8_t volume;       /* 4-bit volume (0..15) */
    int8_t pan;           /* -64 (L) .. 0 (C) .. +64 (R) */
} wsg_voice_t;

typedef struct {
    wsg_voice_t voices[WSG_VOICES];
    const uint8_t *sound_rom; /* 256 bytes (8 waveforms x 32 steps) */
    int gain;                 /* Master volume scaling */
    bool enabled;
} wsg_chip_t;

void wsg_init(wsg_chip_t *w, const uint8_t *sound_rom);
void wsg_write(wsg_chip_t *w, uint8_t address, uint8_t value);
void wsg_render_stereo(wsg_chip_t *w, int32_t *out_stereo, unsigned frames);

#endif /* PAC_WSG_H */
