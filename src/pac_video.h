/* SPDX-License-Identifier: GPL-3.0-only WITH GPL-3.0-linking-exception
 * Pac-Man video pipeline for M-VAVE FM-1 (240x240 RGB565 ST7789 display).
 */
#ifndef PAC_VIDEO_H
#define PAC_VIDEO_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define PAC_NATIVE_WIDTH 224
#define PAC_NATIVE_HEIGHT 288
#define FM1_SCREEN_SIZE 240

typedef int (*pac_band_blit_fn)(unsigned x, unsigned y, unsigned w, unsigned h,
                                const uint16_t *pixels, size_t count);

typedef struct {
    uint16_t palette_rgb565[64][4]; /* Precomputed RGB565 lookup */
    uint8_t tiles_decoded[256 * 64];
    uint8_t sprites_decoded[64 * 256];
#ifndef __GCC_PI32V2__
    uint16_t arcade_frame[PAC_NATIVE_WIDTH * PAC_NATIVE_HEIGHT];
#endif
} pac_video_t;

void pac_video_init(pac_video_t *v,
                    const uint8_t *color_rom,
                    const uint8_t *palette_rom,
                    const uint8_t *tile_rom,
                    const uint8_t *sprite_rom);

#ifndef __GCC_PI32V2__
void pac_video_render(pac_video_t *v,
                      const uint8_t *vram,
                      const uint8_t *sprite_pos,
                      const uint8_t *sprite_info,
                      uint16_t *tft_output_240x240);
#else
void pac_video_render_bands(pac_video_t *v,
                            const uint8_t *vram,
                            const uint8_t *sprite_pos,
                            const uint8_t *sprite_info,
                            pac_band_blit_fn blit_fn);
#endif

#endif /* PAC_VIDEO_H */
