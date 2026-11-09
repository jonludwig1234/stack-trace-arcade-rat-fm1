/* SPDX-License-Identifier: GPL-3.0-only WITH GPL-3.0-linking-exception
 * Pac-Man tile/sprite renderer with 5:6 vertical decimation for FM-1 ST7789 display.
 */
#include "pac_video.h"
#include <string.h>

static inline uint16_t rgb_to_565(uint8_t r, uint8_t g, uint8_t b)
{
    return (uint16_t)(((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3));
}

static void decode_strip(const uint8_t *rom, uint8_t *out, int bx, int by, int width)
{
    int base = by * width + bx;
    for (int x = 0; x < 8; ++x) {
        uint8_t strip = rom[x];
        for (int y = 0; y < 4; ++y) {
            int idx = base + (3 - y) * width + (7 - x);
            out[idx] = (strip >> y) & 1;
            out[idx] |= ((strip >> (y + 4)) & 1) << 1;
        }
    }
}

void pac_video_init(pac_video_t *v,
                    const uint8_t *color_rom,
                    const uint8_t *palette_rom,
                    const uint8_t *tile_rom,
                    const uint8_t *sprite_rom)
{
    memset(v, 0, sizeof(*v));

    /* 1. Decode 32-color PROM into RGB565 */
    uint16_t colors_565[32];
    for (int i = 0; i < 32; ++i) {
        uint8_t d = color_rom[i];
        uint8_t r = ((d >> 0) & 1) * 0x21 + ((d >> 1) & 1) * 0x47 + ((d >> 2) & 1) * 0x97;
        uint8_t g = ((d >> 3) & 1) * 0x21 + ((d >> 4) & 1) * 0x47 + ((d >> 5) & 1) * 0x97;
        uint8_t b = ((d >> 6) & 1) * 0x51 + ((d >> 7) & 1) * 0xAE;
        colors_565[i] = rgb_to_565(r, g, b);
    }

    /* 2. Precompute 64 palettes (4 colors each) */
    for (int p = 0; p < 64; ++p) {
        for (int c = 0; c < 4; ++c) {
            uint8_t color_idx = palette_rom[p * 4 + c] & 0x1F;
            v->palette_rgb565[p][c] = colors_565[color_idx];
        }
    }

    /* 3. Predecode 256 tiles (8x8 = 64 pixels each) */
    for (int t = 0; t < 256; ++t) {
        uint8_t *tile_dest = &v->tiles_decoded[t * 64];
        const uint8_t *rom = &tile_rom[t * 16];
        decode_strip(rom + 0, tile_dest, 0, 4, 8);
        decode_strip(rom + 8, tile_dest, 0, 0, 8);
    }

    /* 4. Predecode 64 sprites (16x16 = 256 pixels each) */
    for (int s = 0; s < 64; ++s) {
        uint8_t *sprite_dest = &v->sprites_decoded[s * 256];
        const uint8_t *rom = &sprite_rom[s * 64];
        decode_strip(rom + 0 * 8, sprite_dest, 8, 12, 16);
        decode_strip(rom + 1 * 8, sprite_dest, 8,  0, 16);
        decode_strip(rom + 2 * 8, sprite_dest, 8,  4, 16);
        decode_strip(rom + 3 * 8, sprite_dest, 8,  8, 16);
        decode_strip(rom + 4 * 8, sprite_dest, 0, 12, 16);
        decode_strip(rom + 5 * 8, sprite_dest, 0,  0, 16);
        decode_strip(rom + 6 * 8, sprite_dest, 0,  4, 16);
        decode_strip(rom + 7 * 8, sprite_dest, 0,  8, 16);
    }
}

static inline void draw_tile(pac_video_t *v, uint8_t tile_no, uint8_t pal_no, int bx, int by)
{
    const uint16_t *pal = v->palette_rgb565[pal_no & 0x3F];
    const uint8_t *tile = &v->tiles_decoded[tile_no * 64];

    for (int i = 0; i < 64; ++i) {
        int x = bx + (i % 8);
        int y = by + (i / 8);
        if (x >= 0 && x < PAC_NATIVE_WIDTH && y >= 0 && y < PAC_NATIVE_HEIGHT) {
            v->arcade_frame[y * PAC_NATIVE_WIDTH + x] = pal[tile[i]];
        }
    }
}

static inline void draw_sprite(pac_video_t *v, uint8_t sprite_no, uint8_t pal_no,
                               int sx, int sy, bool flip_x, bool flip_y)
{
    const uint16_t *pal = v->palette_rgb565[pal_no & 0x3F];
    const uint8_t *sprite = &v->sprites_decoded[sprite_no * 256];

    for (int i = 0; i < 256; ++i) {
        int spr_x = i % 16;
        int spr_y = i / 16;
        int px = flip_x ? (15 - spr_x) : spr_x;
        int py = flip_y ? (15 - spr_y) : spr_y;
        uint8_t color_idx = sprite[py * 16 + px];
        if (color_idx == 0) continue; /* 0 is transparent */

        int x = sx + spr_x;
        int y = sy + spr_y;
        if (x >= 0 && x < PAC_NATIVE_WIDTH && y >= 0 && y < PAC_NATIVE_HEIGHT) {
            v->arcade_frame[y * PAC_NATIVE_WIDTH + x] = pal[color_idx];
        }
    }
}

void pac_video_render(pac_video_t *v,
                      const uint8_t *vram,
                      const uint8_t *sprite_pos,
                      const uint8_t *sprite_info,
                      uint16_t *tft_output_240x240)
{
    /* Clear native frame to black */
    memset(v->arcade_frame, 0, sizeof(v->arcade_frame));

    /* 1. Background VRAM Tiles */
    /* Bottom row */
    int x = 31, y = 34, i = 0x000;
    while (x != 31 || y != 36) {
        draw_tile(v, vram[i], vram[i + 0x400], (x - 2) * 8, y * 8);
        ++i;
        if (x == 0) { x = 31; ++y; } else --x;
    }
    /* Middle playfield */
    x = 29; y = 2; i = 0x040;
    while (x != 1 || y != 2) {
        draw_tile(v, vram[i], vram[i + 0x400], (x - 2) * 8, y * 8);
        ++i;
        if (y == 33) { y = 2; --x; } else ++y;
    }
    /* Top score row */
    x = 31; y = 0; i = 0x3C0;
    while (x != 31 || y != 2) {
        draw_tile(v, vram[i], vram[i + 0x400], (x - 2) * 8, y * 8);
        ++i;
        if (x == 0) { x = 31; ++y; } else --x;
    }

    /* 2. Sprites (rendered 7 down to 0) */
    for (int s = 7; s >= 0; --s) {
        int sx = PAC_NATIVE_WIDTH - sprite_pos[s * 2] + 15;
        int sy = PAC_NATIVE_HEIGHT - sprite_pos[s * 2 + 1] - 16;
        uint8_t info = sprite_info[s * 2];
        uint8_t pal  = sprite_info[s * 2 + 1];
        draw_sprite(v, info >> 2, pal, sx, sy, (info >> 1) & 1, info & 1);
    }

    /* 3. Downsample 224x288 to 240x240 with centered 8px horizontal border.
     * Mathematical relationship: 288 * 5 / 6 = 240.
     * Every output line Y maps to source line floor(Y * 6 / 5). */
    const uint16_t border_color = 0x0842; /* Dark charcoal bezel line */

    for (unsigned out_y = 0; out_y < FM1_SCREEN_SIZE; ++out_y) {
        unsigned in_y = (out_y * 6U) / 5U;
        const uint16_t *src_row = &v->arcade_frame[in_y * PAC_NATIVE_WIDTH];
        uint16_t *dst_row = &tft_output_240x240[out_y * FM1_SCREEN_SIZE];

        /* Left 8px margin */
        for (int m = 0; m < 8; ++m) dst_row[m] = border_color;
        /* Centered 224 arcade pixels */
        memcpy(&dst_row[8], src_row, PAC_NATIVE_WIDTH * sizeof(uint16_t));
        /* Right 8px margin */
        for (int m = 232; m < 240; ++m) dst_row[m] = border_color;
    }
}
