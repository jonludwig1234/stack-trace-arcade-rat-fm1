/* SPDX-License-Identifier: GPL-3.0-only WITH GPL-3.0-linking-exception
 * Namco WSG 3-voice 4-bit wavetable synthesis engine running at 44.1 kHz.
 */
#include "pac_wsg.h"
#include <string.h>

#ifdef __GCC_PI32V2__
#include "fm1.h"
static uint8_t s_wsg_sound_rom[256] FM1_AUDIO_DATA;
#else
#define FM1_AUDIO_CODE
#endif

void wsg_init(wsg_chip_t *w, const uint8_t *sound_rom)
{
    memset(w, 0, sizeof(*w));
#ifdef __GCC_PI32V2__
    if (sound_rom) {
        memcpy(s_wsg_sound_rom, sound_rom, 256);
    }
    w->sound_rom = s_wsg_sound_rom;
    w->gain = 8192; /* 24-bit PCM headroom on FM-1 hardware */
#else
    w->sound_rom = sound_rom;
    w->gain = 512; /* Q8 scaling for FM-1 32-bit audio pipeline */
#endif
    w->enabled = true;

    /* Stereo separation across the 3 arcade voices */
    w->voices[0].pan = -24; /* Slightly left */
    w->voices[1].pan = 0;   /* Center */
    w->voices[2].pan = 24;  /* Slightly right */
}

void wsg_write(wsg_chip_t *w, uint8_t address, uint8_t value)
{
    /* Voice 0 (addresses 0x00..0x05, 0x10..0x15) */
    if (address == 0x05) {
        w->voices[0].waveform_no = value & 0x07;
    } else if (address >= 0x10 && address <= 0x14) {
        uint8_t shift = (address - 0x10) * 4;
        w->voices[0].frequency &= ~(0x0Fu << shift);
        w->voices[0].frequency |= ((uint32_t)(value & 0x0F)) << shift;
    } else if (address == 0x15) {
        w->voices[0].volume = value & 0x0F;
    } else if (address <= 0x04) {
        uint8_t shift = address * 4;
        w->voices[0].accumulator &= ~(0x0Fu << shift);
        w->voices[0].accumulator |= ((uint32_t)(value & 0x0F)) << shift;
    }
    /* Voice 1 (addresses 0x06..0x0A, 0x16..0x1A) */
    else if (address == 0x0A) {
        w->voices[1].waveform_no = value & 0x07;
    } else if (address >= 0x16 && address <= 0x19) {
        uint8_t shift = (address - 0x16 + 1) * 4;
        w->voices[1].frequency &= ~(0x0Fu << shift);
        w->voices[1].frequency |= ((uint32_t)(value & 0x0F)) << shift;
    } else if (address == 0x1A) {
        w->voices[1].volume = value & 0x0F;
    } else if (address >= 0x06 && address <= 0x09) {
        uint8_t shift = (address - 0x06 + 1) * 4;
        w->voices[1].accumulator &= ~(0x0Fu << shift);
        w->voices[1].accumulator |= ((uint32_t)(value & 0x0F)) << shift;
    }
    /* Voice 2 (addresses 0x0B..0x0F, 0x1B..0x1F) */
    else if (address == 0x0F) {
        w->voices[2].waveform_no = value & 0x07;
    } else if (address >= 0x1B && address <= 0x1E) {
        uint8_t shift = (address - 0x1B + 1) * 4;
        w->voices[2].frequency &= ~(0x0Fu << shift);
        w->voices[2].frequency |= ((uint32_t)(value & 0x0F)) << shift;
    } else if (address == 0x1F) {
        w->voices[2].volume = value & 0x0F;
    } else if (address >= 0x0B && address <= 0x0E) {
        uint8_t shift = (address - 0x0B + 1) * 4;
        w->voices[2].accumulator &= ~(0x0Fu << shift);
        w->voices[2].accumulator |= ((uint32_t)(value & 0x0F)) << shift;
    }
}

FM1_AUDIO_CODE void wsg_render_stereo(wsg_chip_t *w, int32_t *out_stereo, unsigned frames)
{
    if (!w->enabled || !w->sound_rom) return;

    /* Pitch ratio conversion from 96kHz arcade clock to 44.1kHz:
     * step = frequency * 96000 / 44100 = frequency * 320 / 147 */
    for (unsigned i = 0; i < frames; ++i) {
        int32_t mix_l = 0;
        int32_t mix_r = 0;

        for (int v = 0; v < WSG_VOICES; ++v) {
            wsg_voice_t *voice = &w->voices[v];
            if (!voice->frequency || !voice->volume) continue;

#ifdef __GCC_PI32V2__
            uint32_t step = (voice->frequency << 1) + ((voice->frequency * 2898U) >> 14);
#else
            uint32_t step = (uint32_t)(((uint64_t)voice->frequency * 320U) / 147U);
#endif
            voice->accumulator = (voice->accumulator + step) & 0xFFFFF;

            /* Highest 5 bits of the 20-bit accumulator index the 32 samples */
            uint32_t sample_idx = (voice->waveform_no * 32U) + (voice->accumulator >> 15);
            int16_t raw_nibble = (int16_t)(w->sound_rom[sample_idx] & 0x0F) - 8;
            int32_t samp = raw_nibble * (int32_t)voice->volume;

            /* Stereo panning */
            int32_t gain_l = 64 - voice->pan;
            int32_t gain_r = 64 + voice->pan;

            mix_l += (samp * gain_l) >> 6;
            mix_r += (samp * gain_r) >> 6;
        }

        /* Mix into output buffer with master gain */
        out_stereo[i * 2 + 0] += mix_l * w->gain;
        out_stereo[i * 2 + 1] += mix_r * w->gain;
    }
}
