/* SPDX-License-Identifier: GPL-3.0-only WITH GPL-3.0-linking-exception
 * M-VAVE FM-1 Hardware Bridge for Pac-Man Arcade & Namco Synth Firmware.
 * Connects the Pac-Man core to FM-1's ST7789 LCD, Audio DMA, and 27 silicone keys.
 */
#include "pac_core.h"
#include "fm1_flash_hw.h"
#include <string.h>

/* FM1 SDK / Board structures */
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

/* Static global machine instance */
static pac_machine_t g_pac;
static uint32_t prev_keys = 0;
static uint32_t prev_buttons = 0;

void fm1_pacman_init(void)
{
    /* Initialize dual-hardware flash detection (supports Old 0x856014 and New 0xB36014) */
    fm1_flash_hw_init(0);
    pac_core_init(&g_pac);
}

void fm1_pacman_update_controls(void)
{
    struct fm1_controls ctrl;
    fm1_controls_read(&ctrl);

    /* 1. D-Pad Directional Controls on Silicone Keys:
     * Key 12 (C4): Left
     * Key 14 (D4): Up
     * Key 16 (E4): Down
     * Key 17 (F4): Right
     */
    if (g_pac.mode == PAC_MODE_ARCADE) {
        g_pac.key_left  = (ctrl.keys & (1U << 12)) != 0;
        g_pac.key_up    = (ctrl.keys & (1U << 14)) != 0;
        g_pac.key_down  = (ctrl.keys & (1U << 16)) != 0;
        g_pac.key_right = (ctrl.keys & (1U << 17)) != 0;
    }

    /* 2. Function Buttons:
     * Button 0 (REC): Insert Coin (COIN 1)
     * Button 1 (PLAY): 1-Player Start
     * Button 2 (STOP): Toggle God Mode (Invincibility)
     * Button 3 (MUTE): Toggle Mode (Arcade <-> Namco Synth)
     */
    uint32_t btn_pressed = ctrl.buttons & ~prev_buttons;
    if (btn_pressed & (1U << 0)) g_pac.key_coin = true;
    else g_pac.key_coin = false;

    if (btn_pressed & (1U << 1)) g_pac.key_start1 = true;
    else g_pac.key_start1 = false;

    if (btn_pressed & (1U << 2)) pac_core_toggle_cheat(&g_pac);
    if (btn_pressed & (1U << 3)) pac_core_toggle_mode(&g_pac);

    prev_buttons = ctrl.buttons;

    /* 3. Rotary Encoders:
     * Knob 0: Master volume
     * Knob 1: Synth Waveform Selector (0..7)
     */
    if (ctrl.encoders[1] != 0) {
        int w = (int)g_pac.synth.current_waveform + ctrl.encoders[1];
        if (w < 0) w = 7;
        if (w > 7) w = 0;
        g_pac.synth.current_waveform = (uint8_t)w;
    }

    /* 4. Silicone Performance Keys in Synth Mode:
     * Detect rising/falling edges across all 27 keys */
    for (unsigned k = 0; k < 27; ++k) {
        uint32_t mask = 1U << k;
        bool was_down = (prev_keys & mask) != 0;
        bool is_down  = (ctrl.keys & mask) != 0;

        if (g_pac.mode == PAC_MODE_SYNTH || (k != 12 && k != 14 && k != 16 && k != 17)) {
            if (!was_down && is_down) {
                pac_synth_key_event(&g_pac.synth, &g_pac.wsg, k, true);
            } else if (was_down && !is_down) {
                pac_synth_key_event(&g_pac.synth, &g_pac.wsg, k, false);
            }
        }
    }
    prev_keys = ctrl.keys;
}

void fm1_pacman_tick_frame(void)
{
    /* Update keypad & encoders */
    fm1_pacman_update_controls();

    /* Emulate one 60Hz video frame */
    pac_core_frame(&g_pac);

    /* Push 240x240 RGB565 frame to ST7789 display via DMA */
    if (!fm1_screen_pending()) {
        fm1_screen_submit(0, 0, 240, 240, g_pac.screen_buffer, 240 * 240);
    }
}

/* Audio DMA render callback (128 stereo frames at 44.1 kHz) */
void fm1_pacman_audio_mix(int32_t *rendered)
{
    pac_core_audio(&g_pac, rendered, FM1_BLOCK_FRAMES);
}
