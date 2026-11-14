/* SPDX-License-Identifier: GPL-3.0-only WITH GPL-3.0-linking-exception
 * Pac-Man arcade machine core implementation for M-VAVE FM-1.
 */
#include "pac_core.h"
#include "pacman_roms.h"
#include <string.h>

#ifdef __GCC_PI32V2__
#include "fm1.h"
#else
#define FM1_AUDIO_CODE
#endif

#define PAC_CLOCK_HZ 3072000
#define PAC_FPS 60
#define PAC_CYCLES_PER_FRAME (PAC_CLOCK_HZ / PAC_FPS)

#ifndef __GCC_PI32V2__
/* Static RAM copy of program ROM if god-mode cheats need patching,
 * or direct pointer access to flash */
static uint8_t prg_rom[0x4000];
#endif

static uint8_t mem_read(void *userdata, uint16_t addr)
{
    pac_machine_t *m = (pac_machine_t *)userdata;
    addr &= 0x7FFF;

    if (addr < 0x4000) {
#ifdef __GCC_PI32V2__
        if (m->god_mode && (addr == 0x0315 || addr == 0x0316)) {
            return 0x00;
        }
        if (addr < 0x1000) return pacman_rom_6e[addr];
        if (addr < 0x2000) return pacman_rom_6f[addr - 0x1000];
        if (addr < 0x3000) return pacman_rom_6h[addr - 0x2000];
        return pacman_rom_6j[addr - 0x3000];
#else
        return prg_rom[addr];
#endif
    } else if (addr < 0x5000) {
        return m->ram[addr - 0x4000];
    } else if (addr <= 0x50FF) {
        /* IN0 (0x5000..0x503F) */
        if (addr >= 0x5000 && addr <= 0x503F) {
            return (!m->key_up << 0) | (!m->key_left << 1) |
                   (!m->key_right << 2) | (!m->key_down << 3) |
                   (!m->key_rack_advance << 4) | /* rack advance */
                   (!m->key_coin << 5) | (1 << 6) | (1 << 7);
        }
        /* IN1 (0x5040..0x507F) */
        if (addr >= 0x5040 && addr <= 0x507F) {
            return (!m->key_up << 0) | (!m->key_left << 1) |
                   (!m->key_right << 2) | (!m->key_down << 3) |
                   (1 << 4) | /* test */
                   (!m->key_start1 << 5) | (!m->key_start2 << 6) | (1 << 7);
        }
        /* DIP Switches (0x5080..0x50BF) */
        if (addr >= 0x5080 && addr <= 0x50BF) {
            /* 1 Coin 1 Credit, 3 Pac-Men, 10000 bonus */
            return 0b11001001;
        }
    }
    return 0xFF;
}

static void mem_write(void *userdata, uint16_t addr, uint8_t val)
{
    pac_machine_t *m = (pac_machine_t *)userdata;
    addr &= 0x7FFF;

    if (addr < 0x4000) {
        /* ROM is read-only */
        return;
    } else if (addr < 0x5000) {
        m->ram[addr - 0x4000] = val;
    } else if (addr <= 0x50FF) {
        if (addr == 0x5000) {
            m->vblank_enabled = (val & 1) != 0;
        } else if (addr == 0x5001) {
            m->sound_enabled = (val & 1) != 0;
            m->wsg.enabled = m->sound_enabled;
        } else if (addr >= 0x5040 && addr <= 0x505F) {
            wsg_write(&m->wsg, addr - 0x5040, val);
        } else if (addr >= 0x5060 && addr <= 0x506F) {
            m->sprite_pos[addr - 0x5060] = val;
        }
    }
}

static uint8_t port_in(z80 *const z, uint8_t port)
{
    (void)z; (void)port;
    return 0;
}

static void port_out(z80 *const z, uint8_t port, uint8_t val)
{
    pac_machine_t *m = (pac_machine_t *)z->userdata;
    if (port == 0) {
        m->int_vector = val;
    }
}

void pac_core_init(pac_machine_t *m)
{
    memset(m, 0, sizeof(*m));

    /* Assemble program ROM into writable buffer */
#ifndef __GCC_PI32V2__
    memcpy(&prg_rom[0x0000], pacman_rom_6e, 0x1000);
    memcpy(&prg_rom[0x1000], pacman_rom_6f, 0x1000);
    memcpy(&prg_rom[0x2000], pacman_rom_6h, 0x1000);
    memcpy(&prg_rom[0x3000], pacman_rom_6j, 0x1000);
#endif

    /* Initialize CPU */
    z80_init(&m->cpu);
    m->cpu.userdata = m;
    m->cpu.read_byte = mem_read;
    m->cpu.write_byte = mem_write;
    m->cpu.port_in = port_in;
    m->cpu.port_out = port_out;

    /* Initialize audio & video subsystems */
    wsg_init(&m->wsg, pacman_sound_rom1);
    pac_video_init(&m->video, pacman_color_rom, pacman_palette_rom,
                   pacman_tile_rom, pacman_sprite_rom);
    pac_synth_init(&m->synth);

    m->mode = PAC_MODE_ARCADE;
    m->sound_enabled = true;
    m->vblank_enabled = false;
    m->int_vector = 0;
}

void pac_core_frame(pac_machine_t *m)
{
    if (m->mode == PAC_MODE_SYNTH) {
        /* In Synth Mode, bypass Z80 and draw the interactive oscilloscope UI */
        pac_synth_tick(&m->synth, &m->wsg);
#ifndef __GCC_PI32V2__
        pac_synth_draw_ui(&m->synth, pacman_sound_rom1, m->screen_buffer);
#endif
        return;
    }

    /* Emulate 1 frame (~51,200 Z80 clock cycles) */
    int cycles = 0;
    while (cycles < PAC_CYCLES_PER_FRAME) {
        int cyc_before = m->cpu.cyc;
        z80_step(&m->cpu);
        int elapsed = m->cpu.cyc - cyc_before;
        cycles += elapsed;
    }

    /* Trigger VBLANK interrupt & render video */
    if (m->vblank_enabled) {
        z80_gen_int(&m->cpu, m->int_vector);
#ifndef __GCC_PI32V2__
        pac_video_render(&m->video, m->ram, m->sprite_pos,
                         &m->ram[0x0FF0], m->screen_buffer);
#endif
    }

    if (m->god_mode) {
        /* Maintain unlimited lives in RAM */
        if (m->ram[0x4e6e - 0x4000] < 5) {
            m->ram[0x4e6e - 0x4000] = 99;
        }
    }
}

#ifdef __GCC_PI32V2__
void pac_core_render_bands(pac_machine_t *m, pac_band_blit_fn blit_fn)
{
    if (m->mode == PAC_MODE_SYNTH) {
        pac_synth_draw_ui_bands(&m->synth, pacman_sound_rom1, blit_fn);
    } else if (m->vblank_enabled) {
        pac_video_render_bands(&m->video, m->ram, m->sprite_pos,
                               &m->ram[0x0FF0], blit_fn);
    }
}
#endif

FM1_AUDIO_CODE void pac_core_audio(pac_machine_t *m, int32_t *pcm, unsigned frames)
{
    wsg_render_stereo(&m->wsg, pcm, frames);
}

void pac_core_toggle_cheat(pac_machine_t *m)
{
    m->god_mode = !m->god_mode;
    if (m->god_mode) {
        /* Unlimited lives patch: NOP out SUB 1 at 0x0315 so Pac-Man never loses a life on death */
#ifndef __GCC_PI32V2__
        prg_rom[0x0315] = 0x00;
        prg_rom[0x0316] = 0x00;
#endif
        m->ram[0x4e6e - 0x4000] = 99;
    } else {
        /* Restore original SUB 1 opcode (D6 01) */
#ifndef __GCC_PI32V2__
        prg_rom[0x0315] = 0xd6;
        prg_rom[0x0316] = 0x01;
#endif
        m->ram[0x4e6e - 0x4000] = 3;
    }
}

static const uint16_t pac_dot_indices[240] = {
    98,99,101,102,103,104,105,117,118,119,123,124,125,126,130,134,137,149,152,155,
    158,162,166,169,181,184,185,186,187,190,194,198,201,213,219,222,226,230,233,245,
    251,254,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,
    276,277,278,279,280,281,282,283,286,290,294,309,312,318,322,326,341,344,350,354,
    358,359,360,361,373,376,377,378,379,382,386,390,393,405,408,411,414,418,422,425,
    437,440,443,446,450,451,452,453,454,457,469,470,471,472,475,476,477,478,486,510,
    518,542,546,547,548,549,550,553,565,566,567,568,571,572,573,574,578,582,585,597,
    600,603,606,610,614,617,629,632,635,638,642,646,647,648,649,661,664,665,666,667,
    670,674,678,693,696,702,706,710,725,728,734,738,739,740,741,742,743,744,745,746,
    747,748,749,750,751,752,753,754,755,756,757,758,759,760,761,762,763,766,770,774,
    777,789,795,798,802,806,809,821,827,830,834,838,841,853,856,857,858,859,862,866,
    870,873,885,888,891,894,898,899,901,902,903,904,905,917,918,919,923,924,925,926
};

void pac_core_advance_level(pac_machine_t *m)
{
    /* Clean Level Skip (Stage Warp):
       Advance fruit/level counter, reset eaten dots counter to 0, and keep energizer subsystem active (1).
       Replenish all 240 pellets, 4 power pills, and reset dot bitmask array so the next maze
       never starts empty and power pills always function properly. */
    m->ram[0x4e13 - 0x4000] = (m->ram[0x4e13 - 0x4000] + 1) & 0xff;
    m->ram[0x4e0e - 0x4000] = 0;
    m->ram[0x4e14 - 0x4000] = 1;

    for (int b = 0x4e16; b <= 0x4e33; b++) {
        m->ram[b - 0x4000] = 0xff;
    }
    for (int b = 0x4e34; b <= 0x4e37; b++) {
        m->ram[b - 0x4000] = 0x14;
    }
    for (int i = 0; i < 240; i++) {
        m->ram[pac_dot_indices[i]] = 0x10;
    }
    m->ram[100] = 0x14;
    m->ram[120] = 0x14;
    m->ram[900] = 0x14;
    m->ram[920] = 0x14;

    m->key_rack_advance = 1;
}

void pac_core_toggle_mode(pac_machine_t *m)
{
    if (m->mode == PAC_MODE_ARCADE) {
        m->mode = PAC_MODE_SYNTH;
        /* Mute game sound, enable synth */
        for (int v = 0; v < WSG_VOICES; ++v) m->wsg.voices[v].volume = 0;
    } else {
        m->mode = PAC_MODE_ARCADE;
    }
}
