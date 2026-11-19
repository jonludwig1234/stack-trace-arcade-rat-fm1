/* SPDX-License-Identifier: GPL-3.0-only WITH GPL-3.0-linking-exception
 * Zero-allocation band-safe 240x240 RGB565 UI primitives for M-VAVE FM-1.
 */
#include "pac_ui.h"

/* Compact 5x7 font (5 columns x 7 rows, bit 0 = top row) stored in Flash (.rodata).
 * Covers space, A-Z, 0-9, and essential UI symbols. */
typedef struct {
    char ch;
    uint8_t cols[5];
} ui_glyph_t;

static const ui_glyph_t s_font5x7[] = {
    {' ', {0x00,0x00,0x00,0x00,0x00}},
    {'!', {0x00,0x00,0x5F,0x00,0x00}},
    {'%', {0x23,0x13,0x08,0x64,0x62}},
    {'+', {0x08,0x08,0x3E,0x08,0x08}},
    {'-', {0x08,0x08,0x08,0x08,0x08}},
    {'.', {0x00,0x60,0x60,0x00,0x00}},
    {'/', {0x20,0x10,0x08,0x04,0x02}},
    {':', {0x00,0x36,0x36,0x00,0x00}},
    {'<', {0x08,0x14,0x22,0x41,0x00}},
    {'>', {0x00,0x41,0x22,0x14,0x08}},
    {'?', {0x02,0x01,0x51,0x09,0x06}},
    {'[', {0x00,0x7F,0x41,0x41,0x00}},
    {']', {0x00,0x41,0x41,0x7F,0x00}},
    {'0', {0x3E,0x51,0x49,0x45,0x3E}},
    {'1', {0x00,0x42,0x7F,0x40,0x00}},
    {'2', {0x42,0x61,0x51,0x49,0x46}},
    {'3', {0x21,0x41,0x45,0x4B,0x31}},
    {'4', {0x18,0x14,0x12,0x7F,0x10}},
    {'5', {0x27,0x45,0x45,0x45,0x39}},
    {'6', {0x3C,0x4A,0x49,0x49,0x30}},
    {'7', {0x01,0x71,0x09,0x05,0x03}},
    {'8', {0x36,0x49,0x49,0x49,0x36}},
    {'9', {0x06,0x49,0x49,0x29,0x1E}},
    {'A', {0x7E,0x11,0x11,0x11,0x7E}},
    {'B', {0x7F,0x49,0x49,0x49,0x36}},
    {'C', {0x3E,0x41,0x41,0x41,0x22}},
    {'D', {0x7F,0x41,0x41,0x22,0x1C}},
    {'E', {0x7F,0x49,0x49,0x49,0x41}},
    {'F', {0x7F,0x09,0x09,0x09,0x01}},
    {'G', {0x3E,0x41,0x49,0x49,0x7A}},
    {'H', {0x7F,0x08,0x08,0x08,0x7F}},
    {'I', {0x00,0x41,0x7F,0x41,0x00}},
    {'J', {0x20,0x40,0x41,0x3F,0x01}},
    {'K', {0x7F,0x08,0x14,0x22,0x41}},
    {'L', {0x7F,0x40,0x40,0x40,0x40}},
    {'M', {0x7F,0x02,0x0C,0x02,0x7F}},
    {'N', {0x7F,0x04,0x08,0x10,0x7F}},
    {'O', {0x3E,0x41,0x41,0x41,0x3E}},
    {'P', {0x7F,0x09,0x09,0x09,0x06}},
    {'Q', {0x3E,0x41,0x51,0x21,0x5E}},
    {'R', {0x7F,0x09,0x19,0x29,0x46}},
    {'S', {0x46,0x49,0x49,0x49,0x31}},
    {'T', {0x01,0x01,0x7F,0x01,0x01}},
    {'U', {0x3F,0x40,0x40,0x40,0x3F}},
    {'V', {0x1F,0x20,0x40,0x20,0x1F}},
    {'W', {0x3F,0x40,0x38,0x40,0x3F}},
    {'X', {0x63,0x14,0x08,0x14,0x63}},
    {'Y', {0x07,0x08,0x70,0x08,0x07}},
    {'Z', {0x61,0x51,0x49,0x45,0x43}},
};

static const uint8_t *find_glyph(char ch)
{
    if (ch >= 'a' && ch <= 'z') ch = (char)(ch - 'a' + 'A');
    for (unsigned i = 0; i < (unsigned)(sizeof(s_font5x7) / sizeof(s_font5x7[0])); ++i) {
        if (s_font5x7[i].ch == ch) return s_font5x7[i].cols;
    }
    return s_font5x7[0].cols;
}

static inline void put_px(const ui_band_ctx_t *ctx, int x, int y, uint16_t color)
{
    if (!ctx || !ctx->band) return;
    if (x < 0 || x >= UI_SCREEN_W) return;
    if (y < ctx->y0 || y >= ctx->y0 + ctx->h) return;
    if (y < 0 || y >= UI_SCREEN_H) return;
    ctx->band[(y - ctx->y0) * UI_SCREEN_W + x] = color;
}

void ui_fill_rect(const ui_band_ctx_t *ctx, int x, int y, int w, int h, uint16_t color)
{
    if (!ctx || !ctx->band || w <= 0 || h <= 0) return;
    int x0 = x < 0 ? 0 : x;
    int x1 = (x + w) > UI_SCREEN_W ? UI_SCREEN_W : (x + w);
    int y0 = y < ctx->y0 ? ctx->y0 : y;
    int y1 = (y + h) > (ctx->y0 + ctx->h) ? (ctx->y0 + ctx->h) : (y + h);
    if (y0 < 0) y0 = 0;
    if (y1 > UI_SCREEN_H) y1 = UI_SCREEN_H;
    for (int py = y0; py < y1; ++py) {
        uint16_t *row = &ctx->band[(py - ctx->y0) * UI_SCREEN_W];
        for (int px = x0; px < x1; ++px) row[px] = color;
    }
}

void ui_draw_hline(const ui_band_ctx_t *ctx, int x, int y, int w, uint16_t color)
{
    ui_fill_rect(ctx, x, y, w, 1, color);
}

void ui_draw_rect_outline(const ui_band_ctx_t *ctx, int x, int y, int w, int h, uint16_t color)
{
    if (w <= 0 || h <= 0) return;
    ui_fill_rect(ctx, x, y, w, 1, color);
    ui_fill_rect(ctx, x, y + h - 1, w, 1, color);
    ui_fill_rect(ctx, x, y, 1, h, color);
    ui_fill_rect(ctx, x + w - 1, y, 1, h, color);
}

void ui_draw_char(const ui_band_ctx_t *ctx, int x, int y, char ch, uint16_t fg, uint16_t bg, bool opaque)
{
    if (!ctx || !ctx->band) return;
    if (y + 7 <= ctx->y0 || y >= ctx->y0 + ctx->h) return;
    const uint8_t *cols = find_glyph(ch);
    for (int c = 0; c < 5; ++c) {
        uint8_t bits = cols[c];
        for (int r = 0; r < 7; ++r) {
            bool on = (bits & (1U << r)) != 0;
            if (on) put_px(ctx, x + c, y + r, fg);
            else if (opaque) put_px(ctx, x + c, y + r, bg);
        }
    }
}

void ui_draw_text(const ui_band_ctx_t *ctx, int x, int y, const char *s, uint16_t fg, uint16_t bg, bool opaque)
{
    if (!ctx || !s) return;
    if (y + 7 <= ctx->y0 || y >= ctx->y0 + ctx->h) return;
    int cx = x;
    while (*s && cx < UI_SCREEN_W) {
        ui_draw_char(ctx, cx, y, *s, fg, bg, opaque);
        cx += 6;
        s++;
    }
}

void ui_draw_bar(const ui_band_ctx_t *ctx, int x, int y, int w, int h,
                 uint32_t value, uint32_t max_value, uint16_t fill_col, uint16_t bg_col)
{
    if (w < 4 || h < 4) return;
    ui_fill_rect(ctx, x, y, w, h, bg_col);
    ui_draw_rect_outline(ctx, x, y, w, h, UI_COL_GRID);
    if (max_value == 0) return;
    uint32_t clamped = value > max_value ? max_value : value;
    int inner_w = (int)(((uint64_t)(w - 2) * clamped) / max_value);
    if (inner_w > 0) {
        ui_fill_rect(ctx, x + 1, y + 1, inner_w, h - 2, fill_col);
    }
}

void ui_draw_toast(const ui_band_ctx_t *ctx, const char *msg, uint16_t border_col)
{
    if (!ctx || !msg || !*msg) return;
    ui_fill_rect(ctx, 12, 4, 216, 18, UI_COL_PANEL);
    ui_draw_rect_outline(ctx, 12, 4, 216, 18, border_col);
    ui_draw_text(ctx, 20, 9, msg, UI_COL_TEXT, UI_COL_PANEL, false);
}
