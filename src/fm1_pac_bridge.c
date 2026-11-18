/* SPDX-License-Identifier: GPL-3.0-only WITH GPL-3.0-linking-exception
 * M-VAVE FM-1 Hardware Bridge for Pac-Man Arcade & Namco Synth Firmware.
 * Connects the Pac-Man core to FM-1's ST7789 LCD, Audio DMA, and 27 silicone keys.
 */
#include "pac_core.h"
#include "fm1_flash_hw.h"
#include <string.h>

/* FM1 SDK / Board structures */
#ifdef __GCC_PI32V2__
#include "fm1.h"
#else
#define FM1_AUDIO_CODE
#define FM1_NKEY 41
#define FM1_NENC 7
#define FM1_BLOCK_FRAMES 128
#define FM1_BLOCK_WORDS (FM1_BLOCK_FRAMES * 2)

struct fm1_controls {
    uint32_t keys;                  /* 27 notes bitmask */
    uint32_t buttons;               /* 14 function buttons bitmask */
    int16_t  encoders[FM1_NENC];    /* 7 rotary knobs delta */
    uint16_t knob;
    uint16_t battery;
};

/* FM-1 external SDK hooks */
extern void fm1_controls_read(struct fm1_controls *state);
extern int  fm1_screen_submit(unsigned x, unsigned y, unsigned w, unsigned h, uint16_t *pixels, size_t count);
extern int  fm1_screen_pending(void);
extern void fm1_screen_fill(unsigned x, unsigned y, unsigned w, unsigned h, uint16_t color);
#endif

/* Static global machine instance */
static pac_machine_t g_pac;
static uint32_t prev_keys = 0;
static uint32_t prev_buttons = 0;
static volatile int s_pac_active = 0;
static uint32_t prev_combo_btns = 0;
static bool pending_coin = false;
static bool pending_start1 = false;
#ifdef __GCC_PI32V2__
static uint32_t last_frame_ms = 0;
#endif

void fm1_pacman_init(void)
{
    /* Initialize dual-hardware flash detection (supports Old 0x856014 and New 0xB36014) */
    fm1_flash_hw_init(0);
    pac_core_init(&g_pac);
    prev_keys = 0;
    prev_buttons = 0;
    prev_combo_btns = 0;
    pending_coin = false;
    pending_start1 = false;
    s_pac_active = 1;
#ifdef __GCC_PI32V2__
    last_frame_ms = fm1_millis();
#endif
}

FM1_AUDIO_CODE int fm1_pacman_active(void)
{
    return s_pac_active;
}

#ifndef __GCC_PI32V2__
const pac_machine_t *fm1_pacman_get_machine(void)
{
    return &g_pac;
}
#endif

int fm1_pacman_poll_toggle(uint32_t buttons)
{
    int toggled = 0;
    if ((buttons & 0x09U) == 0x09U && (prev_combo_btns & 0x09U) != 0x09U) {
        s_pac_active = !s_pac_active;
        prev_buttons = buttons;
        pending_coin = false;
        pending_start1 = false;
        if (!s_pac_active) {
            for (int v = 0; v < WSG_VOICES; ++v) g_pac.wsg.voices[v].volume = 0;
        } else {
#ifdef __GCC_PI32V2__
            last_frame_ms = fm1_millis() - 16U;
#endif
        }
        toggled = 1;
    }
    prev_combo_btns = buttons;
    return toggled;
}

static void update_controls_from(const struct fm1_controls *ctrl)
{
    if (!ctrl) return;

    /* 1. Function Buttons (evaluated first so mode toggles apply immediately):
     * Button 0 (REC): Insert Coin (COIN 1)
     * Button 1 (PLAY): 1-Player Start
     * Button 2 (STOP): Toggle God Mode (Invincibility)
     * Button 3 (MUTE): Toggle Mode (Arcade <-> Namco Synth)
     */
    uint32_t btn_pressed = ctrl->buttons & ~prev_buttons;
    if ((ctrl->buttons & 0x09U) != 0x09U) {
        if (btn_pressed & (1U << 0)) pending_coin = true;
        if (btn_pressed & (1U << 1)) pending_start1 = true;
        if (btn_pressed & (1U << 2)) pac_core_toggle_cheat(&g_pac);
        if (btn_pressed & (1U << 3)) pac_core_toggle_mode(&g_pac);
    }
    g_pac.key_coin = pending_coin || ((ctrl->buttons & (1U << 0)) != 0);
    g_pac.key_start1 = pending_start1 || ((ctrl->buttons & (1U << 1)) != 0);

    prev_buttons = ctrl->buttons;

    /* 2. D-Pad Directional Controls on Silicone Keys:
     * Key 12 (C4): Left
     * Key 14 (D4): Up
     * Key 16 (E4): Down
     * Key 17 (F4): Right
     * Clear directional state when not in Arcade mode so keys never stick on mode toggle.
     */
    if (g_pac.mode == PAC_MODE_ARCADE) {
        g_pac.key_left  = (ctrl->keys & (1U << 12)) != 0;
        g_pac.key_up    = (ctrl->keys & (1U << 14)) != 0;
        g_pac.key_down  = (ctrl->keys & (1U << 16)) != 0;
        g_pac.key_right = (ctrl->keys & (1U << 17)) != 0;
    } else {
        g_pac.key_left  = false;
        g_pac.key_up    = false;
        g_pac.key_down  = false;
        g_pac.key_right = false;
    }

    /* 3. Rotary Encoders:
     * Knob 0: Master volume
     * Knob 1: Synth Waveform Selector (0..7)
     */
    if (ctrl->encoders[1] != 0) {
        int w = ((int)g_pac.synth.current_waveform + ctrl->encoders[1]) % 8;
        if (w < 0) w += 8;
        g_pac.synth.current_waveform = (uint8_t)w;
    }

    /* 4. Silicone Performance Keys in Synth Mode:
     * Only trigger synth notes in PAC_MODE_SYNTH so accidental key brushes
     * during Pac-Man arcade play do not hijack the Namco WSG audio voices.
     */
    if (g_pac.mode == PAC_MODE_SYNTH) {
        for (unsigned k = 0; k < 27; ++k) {
            uint32_t mask = 1U << k;
            bool was_down = (prev_keys & mask) != 0;
            bool is_down  = (ctrl->keys & mask) != 0;

            if (!was_down && is_down) {
                pac_synth_key_event(&g_pac.synth, &g_pac.wsg, k, true);
            } else if (was_down && !is_down) {
                pac_synth_key_event(&g_pac.synth, &g_pac.wsg, k, false);
            }
        }
    }
    prev_keys = ctrl->keys;
}

void fm1_pacman_update_controls(void)
{
    struct fm1_controls ctrl;
    fm1_controls_read(&ctrl);
    update_controls_from(&ctrl);
}

#ifdef __GCC_PI32V2__
void fm1_pacman_tick_controls(const struct fm1_controls *ctrl)
{
    update_controls_from(ctrl);

    uint32_t now = fm1_millis();
    if (now - last_frame_ms < 16U) return;
    last_frame_ms = now;

    g_pac.key_coin = pending_coin || ((ctrl->buttons & (1U << 0)) != 0);
    g_pac.key_start1 = pending_start1 || ((ctrl->buttons & (1U << 1)) != 0);
    pending_coin = false;
    pending_start1 = false;

    pac_core_frame(&g_pac);
    pac_core_render_bands(&g_pac, fm1_screen_blit);
}

void fm1_pacman_tick_frame(void)
{
    struct fm1_controls ctrl;
    fm1_controls_read(&ctrl);
    fm1_pacman_tick_controls(&ctrl);
}
#else
void fm1_pacman_tick_frame(void)
{
    /* Update keypad & encoders */
    fm1_pacman_update_controls();

    /* Emulate one 60Hz video frame */
    pac_core_frame(&g_pac);
    pending_coin = false;
    pending_start1 = false;

    /* Push 240x240 RGB565 frame to ST7789 display via DMA */
    if (!fm1_screen_pending()) {
        fm1_screen_submit(0, 0, 240, 240, g_pac.screen_buffer, 240 * 240);
    }
}
#endif

/* Audio DMA render callback (128 stereo frames at 44.1 kHz) */
FM1_AUDIO_CODE void fm1_pacman_audio_mix(int32_t *rendered)
{
    if (!s_pac_active || !rendered) return;
    pac_core_audio(&g_pac, rendered, FM1_BLOCK_FRAMES);
}
