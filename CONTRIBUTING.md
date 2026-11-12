# Contributing to Arcade Rat

We welcome community additions, especially new retro engines and arcade cores! 

## Hooking a new retro engine into Arcade Rat

Below is boilerplate C code demonstrating how to plug your own Z80/Sound hardware emulations into our routing matrix.

```c
// Boilerplate: Hooking a new retro engine into Arcade Rat
#include "fm1_audio_engine.h"

// 1. Define your init function
void custom_arcade_core_init() {
    // Initialize emulated CPU / DAC here
    z80_reset();
    psg_init(AY8910_CLOCK_NTSC);
}

// 2. Define the per-sample audio generation loop
int16_t custom_arcade_core_process() {
    // Step the CPU
    z80_step();
    // Return standard 16-bit PCM for the M-VAVE DSP
    return psg_generate_sample();
}

// 3. Register it in the master engine array in main.c
// engine_registry[9] = { .init = custom_arcade_core_init, .process = custom_arcade_core_process };
```
