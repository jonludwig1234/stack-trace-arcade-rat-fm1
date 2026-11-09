/* SPDX-License-Identifier: GPL-3.0-only WITH GPL-3.0-linking-exception
 * Pac-Man video pipeline for M-VAVE FM-1 (240x240 RGB565 ST7789 display).
 */
#ifndef PAC_VIDEO_H
#define PAC_VIDEO_H

#include <stdint.h>
#include <stdbool.h>

#define PAC_NATIVE_WIDTH 224
#define PAC_NATIVE_HEIGHT 288
#define FM1_SCREEN_SIZE 240

typedef struct {
    uint16_t palette_rgb565[64][4]; /* Precomputed RGB565 lookup */
    uint8_t tiles_decoded[256 * 64];
    uint8_t sprites_decoded[64 * 256];
    uint16_t arcade_frame[PAC_NATIVE_WIDTH * PAC_NATIVE_HEIGHT];
} pac_video_t;

void pac_video_init(pac_video_t *v,
                    const uint8_t *color_rom,
                    const uint8_t *palette_rom,
                    const uint8_t *tile_rom,
                    const uint8_t *sprite_rom);

void pac_video_render(pac_video_t *v,
                      const uint8_t *vram,
                      const uint8_t *sprite_pos,
                      const uint8_t *sprite_info,
                      uint16_t *tft_output_240x240);

#endif /* PAC_VIDEO_H */
