/* SPDX-License-Identifier: GPL-3.0-only WITH GPL-3.0-linking-exception
 * Namco 3-voice synthesizer mode implementation with TFT oscilloscope visualizer.
 */
#include "pac_synth.h"
#include "fm1_flash_hw.h"
#include <stdio.h>
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
    s->ui_page = UI_PAGE_HOME;
    s->edit_cursor = 0;
    s->battery_pct = 100;
    for (int i = 0; i < WSG_VOICES; ++i) {
        s->voices[i].note = -1;
    }
}

void pac_synth_set_toast(pac_synth_t *s, const char *msg, uint16_t color)
{
    if (!s || !msg) return;
    snprintf(s->toast_msg, sizeof(s->toast_msg), "%s", msg);
    s->toast_color = color;
    s->toast_frames = 72; /* ~1.2s at 60Hz */
}

void pac_synth_adjust_param(pac_synth_t *s, int cursor, int delta)
{
    if (!s || delta == 0) return;
    switch (cursor) {
    case 0: {
        int w = ((int)s->current_waveform + delta) % 8;
        if (w < 0) w += 8;
        s->current_waveform = (uint8_t)w;
        break;
    }
    case 1: {
        int v = (int)s->master_volume + delta;
        if (v < 0) v = 0;
        if (v > 15) v = 15;
        s->master_volume = (uint8_t)v;
        break;
    }
    case 2: {
        int d = (int)s->decay_rate + delta * 150;
        if (d < 200) d = 200;
        if (d > 8000) d = 8000;
        s->decay_rate = (uint16_t)d;
        break;
    }
    case 3: {
        int a = (int)s->attack_rate + delta * 1000;
        if (a < 1000) a = 1000;
        if (a > 30000) a = 30000;
        s->attack_rate = (uint16_t)a;
        break;
    }
    default:
        break;
    }
}

void pac_synth_key_event(pac_synth_t *s, wsg_chip_t *wsg, unsigned key_idx, bool pressed)
{
    if (!s || !wsg || key_idx >= 27) return;
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
        wsg->voices[chosen].waveform_no = s->current_waveform & 0x07U;
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
    if (!s || !wsg) return;
    if (s->toast_frames > 0) s->toast_frames--;
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

static const char *const s_wsg_names[8] = {
    "SINE", "TRI", "SAW", "SQUARE", "PULSE", "ORGAN", "NOISE", "BUZZ"
};

static void render_synth_band(const pac_synth_t *s, const uint8_t *sound_rom, const ui_band_ctx_t *ctx)
{
    uint8_t active_w = s->current_waveform & 0x07U;
    ui_fill_rect(ctx, 0, 0, UI_SCREEN_W, UI_SCREEN_H, UI_COL_BG);

    if (s->ui_page == UI_PAGE_HOME) {
        char buf[32];
        /* 20px Header */
        ui_fill_rect(ctx, 0, 0, UI_SCREEN_W, 20, UI_COL_PANEL);
        ui_draw_hline(ctx, 0, 19, UI_SCREEN_W, UI_COL_GRID);
        ui_draw_text(ctx, 6, 6, "ARCADE RAT", UI_COL_TEXT, UI_COL_PANEL, false);
        snprintf(buf, sizeof(buf), "WSG:%u %s", (unsigned)active_w, s_wsg_names[active_w]);
        ui_draw_text(ctx, 84, 6, buf, UI_COL_ACCENT, UI_COL_PANEL, false);
        snprintf(buf, sizeof(buf), "%u%%", (unsigned)s->battery_pct);
        ui_draw_text(ctx, 206, 6, buf, UI_COL_NEON, UI_COL_PANEL, false);

        /* 8-segment WSG waveform strip (y=23..31) */
        for (int w = 0; w < 8; ++w) {
            uint16_t wcol = (w == (int)active_w) ? UI_COL_ACCENT : UI_COL_GRID;
            ui_fill_rect(ctx, 16 + w * 26, 23, 22, 7, wcol);
        }

        /* Split Canvas: Left = WSG Wave (x=8..134, y=36..162), Right = ADSR (x=140..232, y=36..162) */
        ui_fill_rect(ctx, 8, 36, 126, 126, UI_COL_PANEL);
        ui_draw_rect_outline(ctx, 8, 36, 126, 126, UI_COL_GRID);
        ui_draw_hline(ctx, 9, 99, 124, UI_COL_GRID);

        const uint8_t *wave = &sound_rom[active_w * 32U];
        for (int x = 0; x < 120; ++x) {
            int step = (x * 32) / 120;
            int val = (wave[step] & 0x0F) - 8;
            int wy = 99 - val * 6;
            ui_fill_rect(ctx, 11 + x, wy, 1, 2, UI_COL_ACCENT);
        }

        ui_fill_rect(ctx, 140, 36, 92, 126, UI_COL_PANEL);
        ui_draw_rect_outline(ctx, 140, 36, 92, 126, UI_COL_GRID);
        ui_draw_text(ctx, 148, 42, "ADSR", UI_COL_MUTED, UI_COL_PANEL, false);
        /* Proportional ADSR envelope preview */
        int atk_w = 8 + (int)(((uint32_t)(30000 - (s->attack_rate > 30000 ? 30000 : s->attack_rate)) * 22U) / 30000U);
        int dec_w = 18 + (int)(((uint32_t)(8000 - (s->decay_rate > 8000 ? 8000 : s->decay_rate)) * 42U) / 8000U);
        for (int i = 0; i < atk_w; ++i) {
            int ey = 148 - (i * 86) / (atk_w > 0 ? atk_w : 1);
            ui_fill_rect(ctx, 148 + i, ey, 2, 2, UI_COL_NEON);
        }
        for (int i = 0; i < dec_w && (148 + atk_w + i) < 228; ++i) {
            int ey = 62 + (i * 86) / (dec_w > 0 ? dec_w : 1);
            ui_fill_rect(ctx, 148 + atk_w + i, ey, 2, 2, UI_COL_AMBER);
        }

        /* 3 Voice Activity Bars (y=170..192) */
        for (int v = 0; v < WSG_VOICES; ++v) {
            int vx = 10 + v * 76;
            uint16_t vcol = s->voices[v].active ? UI_COL_NEON : UI_COL_GRID;
            uint32_t lvl = s->voices[v].active ? (uint32_t)s->voices[v].env_level : 0U;
            snprintf(buf, sizeof(buf), "V%d", v + 1);
            ui_draw_text(ctx, vx, 174, buf, s->voices[v].active ? UI_COL_TEXT : UI_COL_MUTED, UI_COL_BG, false);
            ui_draw_bar(ctx, vx + 16, 172, 52, 12, lvl, 65535U, vcol, UI_COL_PANEL);
        }

        /* Bottom Param Strip (y=198..236) */
        ui_fill_rect(ctx, 0, 198, UI_SCREEN_W, 42, UI_COL_PANEL);
        ui_draw_hline(ctx, 0, 198, UI_SCREEN_W, UI_COL_GRID);
        snprintf(buf, sizeof(buf), "VOL:%u", (unsigned)s->master_volume);
        ui_draw_text(ctx, 8, 206, buf, UI_COL_TEXT, UI_COL_PANEL, false);
        snprintf(buf, sizeof(buf), "DEC:%u", (unsigned)s->decay_rate);
        ui_draw_text(ctx, 64, 206, buf, UI_COL_AMBER, UI_COL_PANEL, false);
        snprintf(buf, sizeof(buf), "ATK:%uK", (unsigned)(s->attack_rate / 1000U));
        ui_draw_text(ctx, 136, 206, buf, UI_COL_NEON, UI_COL_PANEL, false);
        ui_draw_text(ctx, 8, 222, "[REC] EDIT  [MUTE] ARCADE", UI_COL_MUTED, UI_COL_PANEL, false);
    } else if (s->ui_page == UI_PAGE_EDIT) {
        char buf[32];
        ui_fill_rect(ctx, 0, 0, UI_SCREEN_W, 20, UI_COL_PANEL);
        ui_draw_hline(ctx, 0, 19, UI_SCREEN_W, UI_COL_GRID);
        ui_draw_text(ctx, 8, 6, "SYNTH EDIT", UI_COL_TEXT, UI_COL_PANEL, false);
        ui_draw_text(ctx, 168, 6, "PAGE 1/2", UI_COL_ACCENT, UI_COL_PANEL, false);

        const char *labels[4] = { "WAVE", "VOL ", "DEC ", "ATK " };
        uint32_t vals[4] = { active_w, s->master_volume, s->decay_rate, s->attack_rate };
        uint32_t maxs[4] = { 7U, 15U, 8000U, 30000U };
        for (int r = 0; r < 4; ++r) {
            int ry = 32 + r * 36;
            bool sel = ((int)s->edit_cursor == r);
            if (sel) {
                ui_fill_rect(ctx, 8, ry, 224, 28, UI_COL_ACCENT);
                ui_draw_text(ctx, 14, ry + 10, labels[r], UI_COL_INK, UI_COL_ACCENT, false);
                ui_draw_bar(ctx, 50, ry + 7, 114, 14, vals[r], maxs[r], UI_COL_INK, UI_COL_PANEL);
                snprintf(buf, sizeof(buf), "%u", (unsigned)vals[r]);
                ui_draw_text(ctx, 172, ry + 10, buf, UI_COL_INK, UI_COL_ACCENT, false);
            } else {
                ui_fill_rect(ctx, 8, ry, 224, 28, UI_COL_PANEL);
                ui_draw_rect_outline(ctx, 8, ry, 224, 28, UI_COL_GRID);
                ui_draw_text(ctx, 14, ry + 10, labels[r], UI_COL_TEXT, UI_COL_PANEL, false);
                ui_draw_bar(ctx, 50, ry + 7, 114, 14, vals[r], maxs[r], UI_COL_NEON, UI_COL_BG);
                snprintf(buf, sizeof(buf), "%u", (unsigned)vals[r]);
                ui_draw_text(ctx, 172, ry + 10, buf, UI_COL_MUTED, UI_COL_PANEL, false);
            }
        }
        ui_fill_rect(ctx, 0, 198, UI_SCREEN_W, 42, UI_COL_PANEL);
        ui_draw_hline(ctx, 0, 198, UI_SCREEN_W, UI_COL_GRID);
        ui_draw_text(ctx, 8, 206, "E3:CURSOR  E2:VALUE", UI_COL_TEXT, UI_COL_PANEL, false);
        ui_draw_text(ctx, 8, 222, "[REC] SYS 2/2  [STOP] HOME", UI_COL_MUTED, UI_COL_PANEL, false);
    } else if (s->ui_page == UI_PAGE_SYSTEM) {
        char buf[36];
        const fm1_flash_hw_info_t *hw = fm1_flash_hw_get_info();
        ui_fill_rect(ctx, 0, 0, UI_SCREEN_W, 20, UI_COL_PANEL);
        ui_draw_hline(ctx, 0, 19, UI_SCREEN_W, UI_COL_GRID);
        ui_draw_text(ctx, 8, 6, "SYSTEM / NVRAM", UI_COL_TEXT, UI_COL_PANEL, false);
        ui_draw_text(ctx, 168, 6, "PAGE 2/2", UI_COL_ACCENT, UI_COL_PANEL, false);

        ui_fill_rect(ctx, 10, 32, 220, 140, UI_COL_PANEL);
        ui_draw_rect_outline(ctx, 10, 32, 220, 140, UI_COL_GRID);
        snprintf(buf, sizeof(buf), "JEDEC: 0X%06X", (unsigned)hw->jedec_id);
        ui_draw_text(ctx, 18, 44, buf, UI_COL_ACCENT, UI_COL_PANEL, false);
        snprintf(buf, sizeof(buf), "REV: %s", hw->rev == FM1_HW_REV1_PUYA ? "REV1 PUYA" : "REV2 UCUN");
        ui_draw_text(ctx, 18, 64, buf, UI_COL_TEXT, UI_COL_PANEL, false);
        ui_draw_text(ctx, 18, 84, hw->status_register_unprotected ? "FLASH: UNLOCKED" : "FLASH: LOCKED",
                     UI_COL_NEON, UI_COL_PANEL, false);
        ui_draw_text(ctx, 18, 108, "NVRAM: A/B CRC32 SAFE", UI_COL_MUTED, UI_COL_PANEL, false);

        ui_fill_rect(ctx, 0, 198, UI_SCREEN_W, 42, UI_COL_PANEL);
        ui_draw_hline(ctx, 0, 198, UI_SCREEN_W, UI_COL_GRID);
        ui_draw_text(ctx, 8, 206, "[PLAY] SAVE   [STOP] CLEAR", UI_COL_AMBER, UI_COL_PANEL, false);
        ui_draw_text(ctx, 8, 222, "[REC] HOME    [MUTE] ARCADE", UI_COL_MUTED, UI_COL_PANEL, false);
    } else if (s->ui_page == UI_PAGE_CONFIRM) {
        ui_fill_rect(ctx, 16, 62, 208, 112, UI_COL_PANEL);
        ui_draw_rect_outline(ctx, 16, 62, 208, 112, UI_COL_DANGER);
        ui_draw_text(ctx, 42, 78, "ERASE ALL NVRAM?", UI_COL_DANGER, UI_COL_PANEL, false);
        ui_draw_text(ctx, 28, 102, "CLEARS SLOTS A+B FOREVER", UI_COL_MUTED, UI_COL_PANEL, false);
        ui_fill_rect(ctx, 28, 134, 82, 24, UI_COL_DANGER);
        ui_draw_text(ctx, 36, 142, "PLAY:YES", UI_COL_TEXT, UI_COL_DANGER, false);
        ui_fill_rect(ctx, 130, 134, 82, 24, UI_COL_GRID);
        ui_draw_text(ctx, 142, 142, "STOP:NO", UI_COL_TEXT, UI_COL_GRID, false);
    }

    if (s->toast_frames > 0) {
        ui_draw_toast(ctx, s->toast_msg, s->toast_color ? s->toast_color : UI_COL_ACCENT);
    }
}

#ifndef __GCC_PI32V2__
void pac_synth_draw_ui(const pac_synth_t *s, const uint8_t *sound_rom, uint16_t *tft_output)
{
    if (!s || !sound_rom || !tft_output) return;
    ui_band_ctx_t ctx = { .band = tft_output, .y0 = 0, .h = UI_SCREEN_H };
    render_synth_band(s, sound_rom, &ctx);
}
#endif
#if defined(__GCC_PI32V2__) || defined(FM1_ENABLE_BAND_RENDERER)
static uint16_t s_synth_band[16 * 240];

void pac_synth_draw_ui_bands(const pac_synth_t *s, const uint8_t *sound_rom, pac_band_blit_fn blit_fn)
{
    if (!s || !sound_rom) return;
    for (unsigned y0 = 0; y0 < 240U; y0 += 16U) {
        unsigned h = (y0 + 16U <= 240U) ? 16U : (240U - y0);
        ui_band_ctx_t ctx = { .band = s_synth_band, .y0 = (int)y0, .h = (int)h };
        render_synth_band(s, sound_rom, &ctx);
        if (blit_fn) {
            blit_fn(0, y0, 240U, h, s_synth_band, (size_t)240U * h);
        }
    }
}
#endif /* __GCC_PI32V2__ || FM1_ENABLE_BAND_RENDERER */
