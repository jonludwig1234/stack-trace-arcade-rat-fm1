/* SPDX-License-Identifier: GPL-3.0-only WITH GPL-3.0-linking-exception
 * Test runner for native M-VAVE FM-1 C firmware core & bridge.
 */
#include "pac_core.h"
#include "fm1_flash_hw.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

/* Mock FM-1 SDK hooks required by fm1_pac_bridge.c */
struct fm1_controls {
    uint32_t keys;
    uint32_t buttons;
    int16_t  encoders[7];
    uint16_t knob;
    uint16_t battery;
};

static struct fm1_controls mock_controls_state;
static int screen_submit_count = 0;

void fm1_controls_read(struct fm1_controls *state) {
    *state = mock_controls_state;
}

int fm1_screen_submit(unsigned x, unsigned y, unsigned w, unsigned h, uint16_t *pixels, size_t count) {
    (void)x; (void)y; (void)w; (void)h; (void)pixels; (void)count;
    screen_submit_count++;
    return 0;
}

int fm1_screen_pending(void) {
    return 0;
}

void fm1_screen_fill(unsigned x, unsigned y, unsigned w, unsigned h, uint16_t color) {
    (void)x; (void)y; (void)w; (void)h; (void)color;
}

/* External bridge functions */
extern void fm1_pacman_init(void);
extern void fm1_pacman_update_controls(void);
extern void fm1_pacman_tick_frame(void);
extern int  fm1_pacman_poll_toggle(uint32_t buttons);
extern int  fm1_pacman_active(void);
extern void fm1_pacman_audio_mix(int32_t *rendered);
extern const pac_machine_t *fm1_pacman_get_machine(void);

int main(void) {
    printf("=========================================================================\n");
    printf("       NATIVE C FIRMWARE UNIT TEST & HARDWARE BRIDGE VALIDATION          \n");
    printf("=========================================================================\n\n");

    /* 1. Initialize Pac-Man Core directly */
    printf("1. Initializing pac_machine_t Core...\n");
    pac_machine_t machine;
    memset(&machine, 0, sizeof(machine));
    pac_core_init(&machine);
    assert(machine.mode == PAC_MODE_ARCADE);
    printf("   ✓ Pac-Man Core initialized cleanly in PAC_MODE_ARCADE.\n");

    /* 2. Run 300 CPU execution frames (emulating 5 seconds of arcade hardware) */
    printf("2. Running 300 native Z80 CPU execution & video render frames...\n");
    for (int frame = 0; frame < 300; frame++) {
        /* Emulate coin insert at frame 10 */
        if (frame == 10) machine.key_coin = true;
        if (frame == 15) machine.key_coin = false;

        /* Emulate 1P start at frame 30 */
        if (frame == 30) machine.key_start1 = true;
        if (frame == 35) machine.key_start1 = false;

        /* Emulate joystick movement */
        if (frame >= 40 && frame < 80) machine.key_left = true;
        else machine.key_left = false;

        pac_core_frame(&machine);
    }
    printf("   ✓ 300 frames executed! Z80 PC=0x%04X, SP=0x%04X\n", machine.cpu.pc, machine.cpu.sp);

    /* 3. Verify Video Framebuffer Output */
    printf("3. Verifying ST7789 Framebuffer (240x240 RGB565)...\n");
    int non_zero_pixels = 0;
    for (int p = 0; p < FM1_SCREEN_SIZE * FM1_SCREEN_SIZE; p++) {
        if (machine.screen_buffer[p] != 0) non_zero_pixels++;
    }
    printf("   ✓ Framebuffer active! Non-black pixels rendered: %d / %d\n", non_zero_pixels, FM1_SCREEN_SIZE * FM1_SCREEN_SIZE);
    assert(non_zero_pixels > 0);

    /* 4. Verify Namco WSG Audio Synthesis DMA buffer & bounds */
    printf("4. Verifying Namco 3-Voice WSG Audio DMA PCM generation & bounds...\n");
    int32_t pcm_buffer[256];
    memset(pcm_buffer, 0, sizeof(pcm_buffer));
    wsg_write(&machine.wsg, 0x05, 0xFF); /* Out-of-range waveform masked to 0..7 */
    wsg_write(&machine.wsg, 0x11, 0x04);
    wsg_write(&machine.wsg, 0x15, 0x0F);
    pac_core_audio(&machine, pcm_buffer, 128);
    int non_zero_audio = 0;
    for (int i = 0; i < 256; i++) {
        if (pcm_buffer[i] != 0) non_zero_audio++;
        assert(pcm_buffer[i] > -1000000 && pcm_buffer[i] < 1000000);
    }
    assert(non_zero_audio > 0);
    wsg_render_stereo(&machine.wsg, NULL, 128);
    wsg_render_stereo(&machine.wsg, pcm_buffer, 0);
    printf("   ✓ Audio DMA block synthesized %d non-zero PCM samples without clipping/OOB.\n", non_zero_audio);

    /* 5. Test God Mode Cheat Toggle */
    printf("5. Testing God Mode Invincibility Patching & Level Skip...\n");
    assert(machine.god_mode == false);
    pac_core_toggle_cheat(&machine);
    assert(machine.god_mode == true);
    pac_core_toggle_cheat(&machine);
    assert(machine.god_mode == false);
    
    /* Test Level Advance */
    uint8_t prev_lvl = machine.ram[0x4e13 - 0x4000];
    machine.ram[0x4e0e - 0x4000] = 120;
    pac_core_advance_level(&machine);
    assert(machine.ram[0x4e13 - 0x4000] == (uint8_t)(prev_lvl + 1)); /* Level advanced cleanly */
    assert(machine.ram[0x4e0e - 0x4000] == 0);    /* Dots eaten reset to 0 for fresh maze */
    assert(machine.ram[0x4e14 - 0x4000] == 1);    /* Energizer subsystem active for power pills */
    assert(machine.ram[98] == 0x10);              /* 240 pellets populated */
    assert(machine.ram[100] == 0x14);             /* Power pills (energizers) populated */
    assert(machine.key_rack_advance == 1);         /* Hardware rack advance active */
    printf("   ✓ God mode memory patch and full pellet/power-pill level skip verified.\n");

    /* 6. Test Namco Synth Mode Toggle */
    printf("6. Testing Namco Synth Groovebox Mode Toggle...\n");
    assert(machine.mode == PAC_MODE_ARCADE);
    pac_core_toggle_mode(&machine);
    assert(machine.mode == PAC_MODE_SYNTH);
    pac_core_toggle_mode(&machine);
    assert(machine.mode == PAC_MODE_ARCADE);
    printf("   ✓ Machine mode cleanly toggled between Arcade and Namco Synth.\n");

    /* 7. Test FM-1 Hardware Bridge (Silicone Keys, Buttons, Edges, Holds, Modes, Combos) */
    printf("7. Testing FM-1 Hardware Bridge & Controls...\n");
    memset(&mock_controls_state, 0, sizeof(mock_controls_state));
    fm1_pacman_init();
    const pac_machine_t *bm = fm1_pacman_get_machine();
    assert(bm != NULL);
    assert(fm1_pacman_active() == 1);

    /* 7a. Press & hold D-Pad keys (12=L, 14=U, 16=D, 17=R), then release */
    mock_controls_state.keys = (1U << 12) | (1U << 14);
    fm1_pacman_update_controls();
    assert(bm->key_left == true && bm->key_up == true && bm->key_down == false && bm->key_right == false);
    mock_controls_state.keys = (1U << 16) | (1U << 17);
    fm1_pacman_update_controls();
    assert(bm->key_left == false && bm->key_up == false && bm->key_down == true && bm->key_right == true);
    mock_controls_state.keys = 0;
    fm1_pacman_update_controls();
    assert(bm->key_down == false && bm->key_right == false);

    /* 7b. Stray non-D-Pad silicone keys in Arcade mode must NOT hijack WSG synth voices */
    mock_controls_state.keys = (1U << 0) | (1U << 5);
    fm1_pacman_update_controls();
    assert(bm->synth.voices[0].active == false && bm->synth.voices[1].active == false);
    mock_controls_state.keys = 0;
    fm1_pacman_update_controls();

    /* 7c. Coin & Start: rising edge latched across multiple control polls before frame tick, and held state */
    mock_controls_state.buttons = (1U << 0) | (1U << 1);
    fm1_pacman_update_controls();
    assert(bm->key_coin == true && bm->key_start1 == true);
    mock_controls_state.buttons = 0; /* rapid release before frame tick */
    fm1_pacman_update_controls();
    assert(bm->key_coin == true && bm->key_start1 == true); /* latched until frame consumes */
    fm1_pacman_tick_frame();
    fm1_pacman_update_controls();
    assert(bm->key_coin == false && bm->key_start1 == false);

    /* Rapid successive coin presses */
    mock_controls_state.buttons = (1U << 0);
    fm1_pacman_update_controls();
    assert(bm->key_coin == true);
    fm1_pacman_tick_frame();
    mock_controls_state.buttons = 0;
    fm1_pacman_update_controls();
    assert(bm->key_coin == false);
    mock_controls_state.buttons = (1U << 0);
    fm1_pacman_update_controls();
    assert(bm->key_coin == true);
    mock_controls_state.buttons = 0;
    fm1_pacman_tick_frame();

    /* 7d. God Mode toggle via Button 2 (STOP) */
    assert(bm->god_mode == false);
    mock_controls_state.buttons = (1U << 2);
    fm1_pacman_update_controls();
    assert(bm->god_mode == true);
    mock_controls_state.buttons = (1U << 2); /* hold does not re-toggle */
    fm1_pacman_update_controls();
    assert(bm->god_mode == true);
    mock_controls_state.buttons = 0;
    fm1_pacman_update_controls();
    mock_controls_state.buttons = (1U << 2);
    fm1_pacman_update_controls();
    assert(bm->god_mode == false);
    mock_controls_state.buttons = 0;
    fm1_pacman_update_controls();

    /* 7e. Mode toggle via Button 3 (MUTE) clears held Arcade D-Pad keys and enables Synth keys */
    mock_controls_state.keys = (1U << 12); /* hold Left */
    fm1_pacman_update_controls();
    assert(bm->key_left == true);
    mock_controls_state.buttons = (1U << 3);
    fm1_pacman_update_controls();
    assert(bm->mode == PAC_MODE_SYNTH);
    assert(bm->key_left == false); /* cleared on mode change */
    mock_controls_state.buttons = 0;
    mock_controls_state.keys = (1U << 0); /* play C3 in Synth mode */
    fm1_pacman_update_controls();
    assert(bm->synth.voices[0].active == true && bm->wsg.voices[0].volume > 0);
    mock_controls_state.keys = 0;
    fm1_pacman_update_controls();
    assert(bm->synth.voices[0].active == false && bm->wsg.voices[0].volume == 0);

    /* Encoder 1 waveform wrap-around 0..7 */
    mock_controls_state.encoders[1] = -1;
    fm1_pacman_update_controls();
    assert(bm->synth.current_waveform == 7);
    mock_controls_state.encoders[1] = 1;
    fm1_pacman_update_controls();
    assert(bm->synth.current_waveform == 0);
    mock_controls_state.encoders[1] = 0;

    /* 7f. REC+MUTE (0x09) combo toggles active state and silences audio_mix */
    assert(fm1_pacman_poll_toggle(0x09U) == 1);
    assert(fm1_pacman_active() == 0);
    memset(pcm_buffer, 0, sizeof(pcm_buffer));
    fm1_pacman_audio_mix(pcm_buffer);
    for (int i = 0; i < 256; i++) assert(pcm_buffer[i] == 0);
    fm1_pacman_audio_mix(NULL); /* null safety */
    assert(fm1_pacman_poll_toggle(0x09U) == 0); /* holding combo does not re-toggle */
    assert(fm1_pacman_poll_toggle(0x00U) == 0);
    assert(fm1_pacman_poll_toggle(0x09U) == 1);
    assert(fm1_pacman_active() == 1);
    printf("   ✓ FM-1 Hardware Bridge keys, edges, holds, modes, encoders & combos verified.\n");

    /* 8. Test Dual-Hardware Flash Identification & Driver Compatibility */
    printf("8. Testing Dual-Hardware Flash Identification (Old Rev 1 & New Rev 2)...\n");

    /* 8a. Test Old FM-1 Hardware (Puya P25Q80H, JEDEC ID 0x856014) */
    int ret_puya = fm1_flash_hw_init(FM1_JEDEC_PUYA_P25Q80H);
    assert(ret_puya == 0);
    const fm1_flash_hw_info_t *info_puya = fm1_flash_hw_get_info();
    assert(info_puya->rev == FM1_HW_REV1_PUYA);
    assert(info_puya->jedec_id == 0x856014U);
    assert(info_puya->status_register_unprotected == true);
    printf("   ✓ Old FM-1 verified: %s (JEDEC 0x%06X) - %s\n", info_puya->chip_name, info_puya->jedec_id, info_puya->batch_desc);

    /* 8b. Test New FM-1 Hardware (UCUN UC25HQ80, JEDEC ID 0xB36014) */
    int ret_ucun = fm1_flash_hw_init(FM1_JEDEC_UCUN_UC25HQ80);
    assert(ret_ucun == 0);
    const fm1_flash_hw_info_t *info_ucun = fm1_flash_hw_get_info();
    assert(info_ucun->rev == FM1_HW_REV2_UCUN);
    assert(info_ucun->jedec_id == 0xB36014U);
    assert(info_ucun->status_register_unprotected == true);
    printf("   ✓ New FM-1 verified: %s (JEDEC 0x%06X) - %s\n", info_ucun->chip_name, info_ucun->jedec_id, info_ucun->batch_desc);

    /* 8c. Test Generic JEDEC SPI NOR Compatibility (0xEF4014 / 0xC84014) */
    assert(fm1_flash_hw_is_supported_id(FM1_JEDEC_WINBOND_W25Q80) == true);
    assert(fm1_flash_hw_is_supported_id(FM1_JEDEC_GD_GD25Q80) == true);
    assert(fm1_flash_hw_is_supported_id(0x123456) == false); /* Unknown invalid chip rejected */
    printf("   ✓ Generic JEDEC 8Mbit SPI NOR fallback verified; invalid IDs rejected safely.\n");

    /* 9. Test NVRAM Persistence & CRC32 Integrity on Both Hardware Revisions */
    printf("9. Testing NVRAM High Score Persistence & CRC32 Verification...\n");

    /* Write test leaderboard payload on New Hardware (UCUN 0xB36014) */
    const char *test_leaderboard_payload = "PAC:BIL:3333360;DKG:ACE:1200000;GAL:KID:999990;";
    size_t payload_len = strlen(test_leaderboard_payload) + 1;
    int save_res = fm1_nvram_save(test_leaderboard_payload, payload_len);
    assert(save_res == 0);

    /* Read back and verify CRC */
    char readback_buf[256];
    size_t readback_size = 0;
    int load_res = fm1_nvram_load(readback_buf, sizeof(readback_buf), &readback_size);
    assert(load_res == 0);
    assert(readback_size == payload_len);
    assert(strcmp(readback_buf, test_leaderboard_payload) == 0);
    printf("   ✓ NVRAM save/load on New Hardware (0xB36014) matched 100%% byte-for-byte with valid CRC32.\n");

    /* Switch to Old Hardware (Puya 0x856014) and verify persistence across revision migration */
    ret_puya = fm1_flash_hw_init(FM1_JEDEC_PUYA_P25Q80H);
    assert(ret_puya == 0);
    const char *test_puya_payload = "FROG:HOP:884200;GYR:VEC:775000;AST:ROC:654300;";
    payload_len = strlen(test_puya_payload) + 1;
    save_res = fm1_nvram_save(test_puya_payload, payload_len);
    assert(save_res == 0);

    memset(readback_buf, 0, sizeof(readback_buf));
    load_res = fm1_nvram_load(readback_buf, sizeof(readback_buf), &readback_size);
    assert(load_res == 0);
    assert(readback_size == payload_len);
    assert(strcmp(readback_buf, test_puya_payload) == 0);
    printf("   ✓ NVRAM save/load on Old Hardware (0x856014) verified with zero data corruption.\n");

    /* Test Erase */
    int erase_res = fm1_nvram_erase();
    assert(erase_res == 0);
    load_res = fm1_nvram_load(readback_buf, sizeof(readback_buf), &readback_size);
    assert(load_res != 0); /* Empty / erased flash correctly reports uninitialized */
    printf("   ✓ Sector erase and clean uninitialized state verified.\n");

    /* 10. Flash Boundary & Fault-Injection Regression Tests */
    printf("10. Testing Flash Boundaries, Fault Injection & Atomic Save Recovery...\n");
    uint8_t small_buf[16];
    assert(fm1_flash_hw_read(FM1_NVRAM_OFFSET_DEFAULT, NULL, 8) == -1);
    assert(fm1_flash_hw_read(FM1_NVRAM_OFFSET_DEFAULT, small_buf, 0) == -1);
    assert(fm1_flash_hw_read(FM1_NVRAM_OFFSET_DEFAULT, small_buf, (size_t)0xFFFFFFFFU) == -1);
    assert(fm1_flash_hw_write(FM1_NVRAM_OFFSET_DEFAULT, NULL, 8) == -1);
    assert(fm1_flash_hw_write(FM1_NVRAM_OFFSET_DEFAULT, small_buf, 0) == -1);
    assert(fm1_flash_hw_write(FM1_NVRAM_OFFSET_DEFAULT, small_buf, (size_t)0xFFFFFFFFU) == -1);
    assert(fm1_flash_hw_erase_sector(FM1_NVRAM_OFFSET_DEFAULT + 1U) == -1); /* unaligned */
    assert(fm1_flash_hw_erase_sector(FM1_FLASH_TOTAL_BYTES) == -1);         /* OOB */
    assert(fm1_calc_crc32(NULL, 10) == 0);

    /* Oversized NVRAM save rejected */
    static uint8_t huge_payload[FM1_FLASH_SECTOR_SIZE];
    memset(huge_payload, 0xA5, sizeof(huge_payload));
    assert(fm1_nvram_save(huge_payload, sizeof(huge_payload)) == -1);

    /* Commit baseline record, then inject erase/write/read faults */
    const char *committed_v1 = "COMMITTED_V1_LEADERBOARD";
    assert(fm1_nvram_save(committed_v1, strlen(committed_v1) + 1) == 0);

    /* Fault 1: Erase failure preserves committed_v1 */
    fm1_flash_hw_set_mock_faults(-1, -1, 0);
    assert(fm1_nvram_save("ABORTED_ERASE", 14) == -2);
    fm1_flash_hw_set_mock_faults(-1, -1, -1);
    memset(readback_buf, 0, sizeof(readback_buf));
    assert(fm1_nvram_load(readback_buf, sizeof(readback_buf), &readback_size) == 0);
    assert(strcmp(readback_buf, committed_v1) == 0);

    /* Fault 2: Write failure mid-save preserves committed_v1 */
    fm1_flash_hw_set_mock_faults(-1, 0, -1);
    assert(fm1_nvram_save("ABORTED_WRITE", 14) == -4);
    fm1_flash_hw_set_mock_faults(-1, -1, -1);
    memset(readback_buf, 0, sizeof(readback_buf));
    assert(fm1_nvram_load(readback_buf, sizeof(readback_buf), &readback_size) == 0);
    assert(strcmp(readback_buf, committed_v1) == 0);

    /* Fault 3: Buffer too small for committed record returns -4 */
    assert(fm1_nvram_load(small_buf, 4, &readback_size) == -4);

    /* Fault 4: Read failure surfaces error */
    fm1_flash_hw_set_mock_faults(0, -1, -1);
    assert(fm1_nvram_load(readback_buf, sizeof(readback_buf), &readback_size) < 0);
    fm1_flash_hw_set_mock_faults(-1, -1, -1);

    /* Fault 5: Corrupt payload in active slot -> CRC mismatch detected */
    assert(fm1_nvram_erase() == 0);
    assert(fm1_nvram_save("CRC_CHECK_DATA", 15) == 0);
    uint8_t zero_byte = 0x00; /* 1->0 bit flip corrupts payload */
    assert(fm1_flash_hw_write(FM1_NVRAM_OFFSET_DEFAULT + sizeof(fm1_nvram_header_t), &zero_byte, 1) == 0);
    assert(fm1_nvram_load(readback_buf, sizeof(readback_buf), &readback_size) == -6);

    /* Video & Synth out-of-bounds / NULL safety */
    pac_synth_t bad_synth;
    pac_synth_init(&bad_synth);
    bad_synth.current_waveform = 255;
    pac_synth_draw_ui(&bad_synth, machine.wsg.sound_rom, machine.screen_buffer);
    pac_synth_draw_ui(NULL, machine.wsg.sound_rom, machine.screen_buffer);
    pac_video_render(NULL, machine.ram, machine.sprite_pos, machine.ram, machine.screen_buffer);
    printf("   ✓ Flash boundaries, fault-injection, CRC mismatch & atomic recovery verified.\n");

    /* 11. Firmware On-Device 240x240 ST7789 UI/UX Visual & Interactive Verification */
    printf("11. Testing Firmware On-Device 240x240 UI/UX (Bezel, Synth Oscilloscope & Voice Bars)...\n");
    memset(&mock_controls_state, 0, sizeof(mock_controls_state));
    fm1_pacman_init();
    const pac_machine_t *ui_m = fm1_pacman_get_machine();

    /* 11a. Arcade mode: run frames so VBLANK renders, verify 8px left/right bezel (0x0842) */
    for (int f = 0; f < 120; f++) fm1_pacman_tick_frame();
    assert(ui_m->vblank_enabled == true);
    assert(ui_m->screen_buffer[0] == 0x0842 && ui_m->screen_buffer[7] == 0x0842);
    assert(ui_m->screen_buffer[232] == 0x0842 && ui_m->screen_buffer[239] == 0x0842);

    /* 11b. Toggle to Synth Mode via Button 3 (MUTE) and render oscilloscope UI */
    mock_controls_state.buttons = (1U << 3);
    fm1_pacman_tick_frame();
    mock_controls_state.buttons = 0;
    assert(ui_m->mode == PAC_MODE_SYNTH);

    /* Verify voice 0 indicator bar (x=40..79, y=210..224) is idle gray (0x7BEF) */
    assert(ui_m->screen_buffer[215 * 240 + 50] == 0x7BEF);

    /* Hold key 0 -> voice 0 bar turns active green (0x07E0) */
    mock_controls_state.keys = (1U << 0);
    fm1_pacman_tick_frame();
    assert(ui_m->screen_buffer[215 * 240 + 50] == 0x07E0);

    /* Snapshot waveform pixels, rotate Encoder 1 -> waveform pixels visually change */
    uint16_t wave_snap[240];
    for (int x = 0; x < 240; x++) wave_snap[x] = ui_m->screen_buffer[120 * 240 + x];
    mock_controls_state.keys = 0;
    mock_controls_state.encoders[1] = 3; /* switch waveform 0 -> 3 */
    fm1_pacman_tick_frame();
    assert(ui_m->synth.current_waveform == 3);
    assert(ui_m->screen_buffer[215 * 240 + 50] == 0x7BEF); /* voice bar back to idle */
    int wave_diffs = 0;
    for (int x = 0; x < 240; x++) {
        for (int y = 60; y < 180; y++) {
            if (ui_m->screen_buffer[y * 240 + x] == 0x07FF && y == 120 && wave_snap[x] != 0x07FF) {
                wave_diffs++;
            }
        }
    }
    assert(wave_diffs > 0);
    printf("   ✓ On-device Arcade bezel, Synth oscilloscope waveform & voice indicator UI verified.\n");

    printf("\n=========================================================================\n");
    printf(">>> ALL NATIVE C FIRMWARE UNIT TESTS PASSED 100%%! <<<\n");
    printf("=========================================================================\n");

    return 0;
}
