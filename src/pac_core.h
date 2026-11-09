/* SPDX-License-Identifier: GPL-3.0-only WITH GPL-3.0-linking-exception
 * Pac-Man arcade machine core for M-VAVE FM-1.
 */
#ifndef PAC_CORE_H
#define PAC_CORE_H

#include "z80.h"
#include "pac_wsg.h"
#include "pac_video.h"
#include "pac_synth.h"
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    PAC_MODE_ARCADE,
    PAC_MODE_SYNTH
} pac_mode_t;

typedef struct {
    z80 cpu;
    uint8_t ram[0x1000];       /* 4KB working RAM (0x4000..0x4FFF) */
    uint8_t sprite_pos[0x10];  /* 0x5060..0x506F */

    wsg_chip_t wsg;
    pac_video_t video;
    pac_synth_t synth;

    pac_mode_t mode;
    bool vblank_enabled;
    bool sound_enabled;
    uint8_t int_vector;

    /* Inputs */
    bool key_up, key_left, key_right, key_down;
    bool key_coin, key_start1, key_start2, key_rack_advance;
    bool god_mode;

    /* Framebuffer for FM-1 ST7789 (240x240 RGB565) */
    uint16_t screen_buffer[FM1_SCREEN_SIZE * FM1_SCREEN_SIZE];
} pac_machine_t;

void pac_core_init(pac_machine_t *m);
void pac_core_frame(pac_machine_t *m);
void pac_core_audio(pac_machine_t *m, int32_t *pcm, unsigned frames);
void pac_core_toggle_cheat(pac_machine_t *m);
void pac_core_advance_level(pac_machine_t *m);
void pac_core_toggle_mode(pac_machine_t *m);

#endif /* PAC_CORE_H */
