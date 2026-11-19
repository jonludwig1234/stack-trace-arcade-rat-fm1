/* SPDX-License-Identifier: GPL-3.0-only WITH GPL-3.0-linking-exception
 * Zero-allocation band-safe 240x240 RGB565 UI primitives for M-VAVE FM-1.
 */
#ifndef PAC_UI_H
#define PAC_UI_H

#include <stdint.h>
#include <stdbool.h>

#define UI_SCREEN_W 240
#define UI_SCREEN_H 240

/* Palette (RGB565) */
#define UI_COL_BG       0x0861 /* #0D1318 dark slate */
#define UI_COL_PANEL    0x10A2 /* #121720 card surface */
#define UI_COL_GRID     0x2124 /* #20262A subtle divider */
#define UI_COL_TEXT     0xE73C /* #E6E8EE crisp off-white */
#define UI_COL_MUTED    0x8C71 /* #8E949E muted label */
#define UI_COL_ACCENT   0x07FF /* #00E5FF cyan highlight */
#define UI_COL_NEON     0x07E0 /* #00FF66 active green */
#define UI_COL_AMBER    0xFD20 /* #F5A623 warning/amber */
#define UI_COL_DANGER   0xF800 /* #FF0000 danger red */
#define UI_COL_INK      0x0000 /* #000000 text on inverted pill */

typedef enum {
    UI_PAGE_HOME = 0,
    UI_PAGE_EDIT = 1,
    UI_PAGE_SYSTEM = 2,
    UI_PAGE_CONFIRM = 3
} ui_page_t;

typedef struct {
    uint16_t *band;      /* Pointer to band buffer (w * band_h) */
    int y0;              /* Top Y of this band in 0..239 */
    int h;               /* Height of this band (16 on device, 240 on host) */
} ui_band_ctx_t;

void ui_fill_rect(const ui_band_ctx_t *ctx, int x, int y, int w, int h, uint16_t color);
void ui_draw_hline(const ui_band_ctx_t *ctx, int x, int y, int w, uint16_t color);
void ui_draw_rect_outline(const ui_band_ctx_t *ctx, int x, int y, int w, int h, uint16_t color);
void ui_draw_char(const ui_band_ctx_t *ctx, int x, int y, char ch, uint16_t fg, uint16_t bg, bool opaque);
void ui_draw_text(const ui_band_ctx_t *ctx, int x, int y, const char *s, uint16_t fg, uint16_t bg, bool opaque);
void ui_draw_bar(const ui_band_ctx_t *ctx, int x, int y, int w, int h,
                 uint32_t value, uint32_t max_value, uint16_t fill_col, uint16_t bg_col);
void ui_draw_toast(const ui_band_ctx_t *ctx, const char *msg, uint16_t border_col);

#endif /* PAC_UI_H */
