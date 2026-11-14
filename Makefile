CC ?= gcc
CFLAGS ?= -O2 -Wall -I. -Isrc
BUILD_DIR := build
FWSC := arcade_rat_fm1.fwsc

.PHONY: all clean test package

all: package test
	@mkdir -p $(BUILD_DIR)
	cp -f $(FWSC) $(BUILD_DIR)/$(FWSC)
	cp -f firmware/SHA256SUMS.txt $(BUILD_DIR)/SHA256SUMS.txt
	@echo "✅ Build complete: $(BUILD_DIR)/$(FWSC)"

package:
	@if [ -d fm1_open/sdk ] && command -v wine >/dev/null 2>&1; then \
		if [ -f "$$HOME/.gemini/antigravity/scratch/jieli_pi32/bin/clang.exe" ] || [ -n "$$FM1_PI32_TOOLCHAIN" ]; then \
			echo "Building AC791N PI32v2 firmware package via Wine SDK..."; \
			python3 tools/build_firmware_package.py; \
		else \
			echo "Using precompiled $(FWSC) (PI32v2 compiler not configured)..."; \
		fi; \
	else \
		echo "Using precompiled $(FWSC) (PI32v2 Wine SDK not present in this environment)..."; \
	fi

test:
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) tools/test_native_c_firmware.c \
		src/z80.c src/pac_wsg.c src/pac_video.c src/pac_synth.c \
		src/pac_demo_songs.c src/pac_core.c src/fm1_pac_bridge.c src/fm1_flash_hw.c \
		-lm -o $(BUILD_DIR)/test_native_c_firmware
	./$(BUILD_DIR)/test_native_c_firmware
	python3 tools/verify_all.py

clean:
	rm -rf $(BUILD_DIR) tools/test_native_c_firmware
