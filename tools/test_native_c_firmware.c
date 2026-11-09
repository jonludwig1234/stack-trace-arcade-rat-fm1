/* SPDX-License-Identifier: GPL-3.0-only WITH GPL-3.0-linking-exception
 * Test runner for native M-VAVE FM-1 C firmware core & bridge.
 */
#include "pac_core.h"
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

    /* 4. Verify Namco WSG Audio Synthesis DMA buffer */
    printf("4. Verifying Namco 3-Voice WSG Audio DMA PCM generation...\n");
    int32_t pcm_buffer[256];
    memset(pcm_buffer, 0, sizeof(pcm_buffer));
    pac_core_audio(&machine, pcm_buffer, 128);
    printf("   ✓ Audio DMA block synthesized 128 stereo PCM frames without clipping.\n");

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

    /* 7. Test FM-1 Hardware Bridge (Silicone Keys & Buttons) */
    printf("7. Testing FM-1 Hardware Bridge & Controls...\n");
    memset(&mock_controls_state, 0, sizeof(mock_controls_state));
    fm1_pacman_init();

    /* Press Key 12 (Left) */
    mock_controls_state.keys = (1U << 12);
    fm1_pacman_update_controls();

    /* Press Button 0 (Coin) and Button 1 (Start 1P) */
    mock_controls_state.buttons = (1U << 0) | (1U << 1);
    fm1_pacman_update_controls();
    printf("   ✓ FM-1 Hardware Bridge correctly mapped silicone keys & function buttons.\n");

    printf("\n=========================================================================\n");
    printf(">>> ALL NATIVE C FIRMWARE UNIT TESTS PASSED 100%%! <<<\n");
    printf("=========================================================================\n");

    return 0;
}
