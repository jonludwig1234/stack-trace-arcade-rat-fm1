/* SPDX-License-Identifier: GPL-3.0-only WITH GPL-3.0-linking-exception
 * Namco 3-voice synthesizer mode implementation with TFT oscilloscope visualizer.
 */
#include "pac_synth.h"
#include <string.h>

#ifndef __GCC_PI32V2__
#include <math.h>

static uint32_t note_freqs[128];
static bool tables_ready = false;

static void init_tables(void)
{
    if (tables_ready) return;
    for (int n = 0; n < 128; ++n) {
        /* A4 (MIDI 69) = 440 Hz */
        double hz = 440.0 * pow(2.0, (n - 69) / 12.0);
        /* Namco 20-bit frequency accumulator at 96kHz clock */
        note_freqs[n] = (uint32_t)((hz * 1048576.0) / 96000.0 + 0.5);
    }
    tables_ready = true;
}
#else
static const uint32_t note_freqs[128] = {
    89, 95, 100, 106, 113, 119, 126, 134, 142, 150, 159, 169,
    179, 189, 200, 212, 225, 238, 253, 268, 284, 300, 318, 337,
    357, 378, 401, 425, 450, 477, 505, 535, 567, 601, 636, 674,
    714, 757, 802, 850, 900, 954, 1010, 1070, 1134, 1201, 1273, 1349,
    1429, 1514, 1604, 1699, 1800, 1907, 2021, 2141, 2268, 2403, 2546, 2697,
    2858, 3028, 3208, 3398, 3600, 3815, 4041, 4282, 4536, 4806, 5092, 5395,
    5715, 6055, 6415, 6797, 7201, 7629, 8083, 8563, 9072, 9612, 10184, 10789,
    11431, 12110, 12830, 13593, 14402, 15258, 16165, 17127, 18145, 19224, 20367, 21578,
    22861, 24221, 25661, 27187, 28803, 30516, 32331, 34253, 36290, 38448, 40734, 43156,
    45722, 48441, 51322, 54373, 57607, 61032, 64661, 68506, 72580, 76896, 81468, 86312,
    91445, 96882, 102643, 108747, 115213, 122064, 129322, 137012
};

static inline void init_tables(void) {}
#endif

void pac_synth_init(pac_synth_t *s)
{
    init_tables();
    memset(s, 0, sizeof(*s));
    s->current_waveform = 0; /* Default sine */
    s->master_volume = 15;
    s->attack_rate = 12000;
    s->decay_rate = 1500;
    for (int i = 0; i < WSG_VOICES; ++i) {
        s->voices[i].note = -1;
    }
}

void pac_synth_key_event(pac_synth_t *s, wsg_chip_t *wsg, unsigned key_idx, bool pressed)
{
    if (key_idx >= 27) return;
    int midi_note = 48 + key_idx; /* C3 (48) to D5 (74) */

    if (pressed) {
        /* Allocate a voice: find idle voice or steal oldest */
        int chosen = -1;
        for (int v = 0; v < WSG_VOICES; ++v) {
            if (!s->voices[v].active) {
                chosen = v;
                break;
            }
        }
        if (chosen < 0) chosen = 0; /* Voice steal */

        s->voices[chosen].note = midi_note;
        s->voices[chosen].active = true;
        s->voices[chosen].env_level = 65535;

        /* Write to Namco hardware voice registers */
        wsg->voices[chosen].waveform_no = s->current_waveform;
        wsg->voices[chosen].frequency = note_freqs[midi_note];
        wsg->voices[chosen].volume = s->master_volume;
    } else {
        /* Release matching voice */
        for (int v = 0; v < WSG_VOICES; ++v) {
            if (s->voices[v].note == midi_note) {
                s->voices[v].active = false;
                wsg->voices[v].volume = 0;
                s->voices[v].note = -1;
            }
        }
    }
}

void pac_synth_tick(pac_synth_t *s, wsg_chip_t *wsg)
{
    for (int v = 0; v < WSG_VOICES; ++v) {
        if (s->voices[v].active) {
            if (s->voices[v].env_level > s->decay_rate) {
                s->voices[v].env_level -= s->decay_rate;
            }
            uint8_t vol = (s->voices[v].env_level * s->master_volume) >> 16;
            wsg->voices[v].volume = vol;
        }
    }
}

#ifndef __GCC_PI32V2__
void pac_synth_draw_ui(const pac_synth_t *s, const uint8_t *sound_rom, uint16_t *tft_output)
{
    /* Background dark navy */
    const uint16_t bg = 0x10A2;
    const uint16_t grid = 0x2124;
    const uint16_t wave_color = 0x07FF; /* Cyan */
    const uint16_t voice_active = 0x07E0; /* Green */
    const uint16_t voice_idle = 0x7BEF;   /* Dim gray */

    for (int i = 0; i < 240 * 240; ++i) tft_output[i] = bg;

    /* Draw oscilloscope grid lines */
    for (int g = 20; g < 240; g += 40) {
        for (int x = 0; x < 240; ++x) tft_output[g * 240 + x] = grid;
        for (int y = 0; y < 240; ++y) tft_output[y * 240 + g] = grid;
    }

    /* Draw active Namco waveform */
    const uint8_t *wave = &sound_rom[s->current_waveform * 32];
    for (int x = 0; x < 240; ++x) {
        int step = (x * 32) / 240;
        int val = (wave[step] & 0x0F) - 8;
        int y = 120 - val * 7;
        if (y >= 0 && y < 240) {
            tft_output[y * 240 + x] = wave_color;
            if (y + 1 < 240) tft_output[(y + 1) * 240 + x] = wave_color;
        }
    }

    /* Draw 3 voice indicator bars at the bottom */
    for (int v = 0; v < WSG_VOICES; ++v) {
        uint16_t col = s->voices[v].active ? voice_active : voice_idle;
        int start_x = 40 + v * 60;
        for (int by = 210; by < 225; ++by) {
            for (int bx = start_x; bx < start_x + 40; ++bx) {
                tft_output[by * 240 + bx] = col;
            }
        }
    }
}
#else
static uint16_t s_synth_band[16 * 240];

void pac_synth_draw_ui_bands(const pac_synth_t *s, const uint8_t *sound_rom, pac_band_blit_fn blit_fn)
{
    const uint16_t bg = 0x10A2;
    const uint16_t grid = 0x2124;
    const uint16_t wave_color = 0x07FF;
    const uint16_t voice_active = 0x07E0;
    const uint16_t voice_idle = 0x7BEF;
    const uint8_t *wave = &sound_rom[(s->current_waveform & 0x07U) * 32U];

    for (unsigned y0 = 0; y0 < 240U; y0 += 16U) {
        unsigned h = (y0 + 16U <= 240U) ? 16U : (240U - y0);
        for (unsigned i = 0; i < h * 240U; ++i) s_synth_band[i] = bg;

        for (unsigned r = 0; r < h; ++r) {
            unsigned y = y0 + r;
            uint16_t *row = &s_synth_band[r * 240U];

            if (y >= 20U && ((y - 20U) % 40U) == 0U) {
                for (int x = 0; x < 240; ++x) row[x] = grid;
            } else {
                for (int g = 20; g < 240; g += 40) row[g] = grid;
            }

            for (int x = 0; x < 240; ++x) {
                int step = (x * 32) / 240;
                int val = (wave[step] & 0x0F) - 8;
                int wy = 120 - val * 7;
                if ((int)y == wy || (int)y == wy + 1) {
                    row[x] = wave_color;
                }
            }

            if (y >= 210U && y < 225U) {
                for (int v = 0; v < WSG_VOICES; ++v) {
                    uint16_t col = s->voices[v].active ? voice_active : voice_idle;
                    int start_x = 40 + v * 60;
                    for (int bx = start_x; bx < start_x + 40; ++bx) {
                        row[bx] = col;
                    }
                }
            }
        }

        if (blit_fn) {
            blit_fn(0, y0, 240U, h, s_synth_band, (size_t)240U * h);
        }
    }
}
#endif
