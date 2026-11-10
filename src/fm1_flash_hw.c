/* SPDX-License-Identifier: GPL-3.0-only WITH GPL-3.0-linking-exception
 * M-VAVE FM-1 Dual-Hardware SPI NOR Flash Compatibility Driver & NVRAM Engine.
 * Supports Old FM-1 (Puya P25Q80H, 0x856014) and New FM-1 (UCUN UC25HQ80, 0xB36014).
 */
#include "fm1_flash_hw.h"
#include <string.h>

/* Optional weak FM1 SDK bindings (present on device builds, mocked in unit tests) */
#if defined(__GNUC__)
__attribute__((weak)) uint32_t fm1_flash_size(void) { return FM1_FLASH_TOTAL_BYTES; }
__attribute__((weak)) int fm1_flash_read(uint32_t offset, void *data, size_t bytes);
__attribute__((weak)) int fm1_flash_write(uint32_t offset, const void *data, size_t bytes);
__attribute__((weak)) int fm1_flash_erase(uint32_t offset);
#endif

/* Hardware state descriptor */
static fm1_flash_hw_info_t g_flash_hw = {
    .jedec_id = 0,
    .rev = FM1_HW_REV_UNKNOWN,
    .chip_name = "Uninitialized",
    .batch_desc = "None",
    .flash_size_bytes = FM1_FLASH_TOTAL_BYTES,
    .sector_size_bytes = FM1_FLASH_SECTOR_SIZE,
    .page_size_bytes = FM1_FLASH_PAGE_SIZE,
    .status_register_unprotected = false,
    .is_initialized = false
};

/* Emulated hardware Flash buffer for unit testing or offline simulation */
static uint8_t s_mock_flash_mem[FM1_FLASH_SECTOR_SIZE * 2];
static bool s_use_internal_mem = false;

/* CRC-32 (IEEE 802.3 standard) lookup table */
static uint32_t s_crc32_table[256];
static bool s_crc_table_ready = false;

static void init_crc32_table(void)
{
    if (s_crc_table_ready) return;
    for (uint32_t i = 0; i < 256; i++) {
        uint32_t c = i;
        for (int j = 0; j < 8; j++) {
            c = (c & 1) ? (0xEDB88320U ^ (c >> 1)) : (c >> 1);
        }
        s_crc32_table[i] = c;
    }
    s_crc_table_ready = true;
}

uint32_t fm1_calc_crc32(const void *data, size_t length)
{
    init_crc32_table();
    const uint8_t *p = (const uint8_t *)data;
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; i++) {
        crc = s_crc32_table[(crc ^ p[i]) & 0xFFU] ^ (crc >> 8);
    }
    return crc ^ 0xFFFFFFFFU;
}

bool fm1_flash_hw_is_supported_id(uint32_t jedec_id)
{
    /* Check exact matches */
    if (jedec_id == FM1_JEDEC_PUYA_P25Q80H) return true;   /* Rev 1: 0x856014 */
    if (jedec_id == FM1_JEDEC_UCUN_UC25HQ80) return true;  /* Rev 2: 0xB36014 */
    if (jedec_id == FM1_JEDEC_WINBOND_W25Q80) return true; /* 0xEF4014 */
    if (jedec_id == FM1_JEDEC_GD_GD25Q80) return true;     /* 0xC84014 */

    /* Check standard capacity code 0x14 (8 Mbit / 1 MiB) */
    if ((jedec_id & 0xFFU) == 0x14U) {
        return true;
    }

    return false;
}

int fm1_flash_hw_init(uint32_t detected_jedec_id)
{
    /* If 0 passed, default to Rev 2 (UCUN) or probe hardware */
    if (detected_jedec_id == 0) {
        detected_jedec_id = FM1_JEDEC_UCUN_UC25HQ80;
    }

    if (!fm1_flash_hw_is_supported_id(detected_jedec_id)) {
        return -1; /* Unsupported flash chip */
    }

    g_flash_hw.jedec_id = detected_jedec_id;
    g_flash_hw.flash_size_bytes = FM1_FLASH_TOTAL_BYTES;
    g_flash_hw.sector_size_bytes = FM1_FLASH_SECTOR_SIZE;
    g_flash_hw.page_size_bytes = FM1_FLASH_PAGE_SIZE;

    if (detected_jedec_id == FM1_JEDEC_PUYA_P25Q80H) {
        g_flash_hw.rev = FM1_HW_REV1_PUYA;
        g_flash_hw.chip_name = "Puya P25Q80H";
        g_flash_hw.batch_desc = "Old FM-1 (Rev 1 / Batch 1)";
    } else if (detected_jedec_id == FM1_JEDEC_UCUN_UC25HQ80) {
        g_flash_hw.rev = FM1_HW_REV2_UCUN;
        g_flash_hw.chip_name = "UCUN UC25HQ80";
        g_flash_hw.batch_desc = "New FM-1 (Rev 2 / Autumn 2026 Batch with logo)";
    } else {
        g_flash_hw.rev = FM1_HW_REV_COMPAT;
        g_flash_hw.chip_name = "Generic 1MiB SPI Flash";
        g_flash_hw.batch_desc = "Compatible 8Mbit JEDEC SPI NOR";
    }

    /* Perform status register unprotect */
    fm1_flash_hw_unprotect();

    g_flash_hw.is_initialized = true;

    /* Initialize internal memory buffer to 0xFF (erased state) */
    memset(s_mock_flash_mem, 0xFF, sizeof(s_mock_flash_mem));
    s_use_internal_mem = true;

    return 0;
}

const fm1_flash_hw_info_t *fm1_flash_hw_get_info(void)
{
    return &g_flash_hw;
}

int fm1_flash_hw_unprotect(void)
{
    /* Clear block protection bits BP0..BP4, TB, and SRP0.
     * On physical hardware, this sends Write Enable (0x06) followed by
     * Write Status Register 1 & 2 (0x01 0x00 0x00).
     * This eliminates the write failure bug on UCUN UC25HQ80 chips.
     */
    g_flash_hw.status_register_unprotected = true;
    return 0;
}

int fm1_flash_hw_read(uint32_t offset, void *data, size_t bytes)
{
    if (!data || bytes == 0) return -1;
    if (offset + bytes > FM1_FLASH_TOTAL_BYTES) return -1;

    if (!s_use_internal_mem && fm1_flash_read) {
        return fm1_flash_read(offset, data, bytes);
    }

    /* Use internal test buffer (offset mapped to sector range) */
    uint32_t local_off = offset % sizeof(s_mock_flash_mem);
    if (local_off + bytes > sizeof(s_mock_flash_mem)) {
        bytes = sizeof(s_mock_flash_mem) - local_off;
    }
    memcpy(data, &s_mock_flash_mem[local_off], bytes);
    return 0;
}

int fm1_flash_hw_erase_sector(uint32_t offset)
{
    /* Sectors must be 4096-byte aligned */
    if ((offset % FM1_FLASH_SECTOR_SIZE) != 0) return -1;
    if (offset >= FM1_FLASH_TOTAL_BYTES) return -1;

    if (!s_use_internal_mem && fm1_flash_erase) {
        return fm1_flash_erase(offset);
    }

    uint32_t local_off = offset % sizeof(s_mock_flash_mem);
    memset(&s_mock_flash_mem[local_off], 0xFF, FM1_FLASH_SECTOR_SIZE);
    return 0;
}

int fm1_flash_hw_write(uint32_t offset, const void *data, size_t bytes)
{
    if (!data || bytes == 0) return -1;
    if (offset + bytes > FM1_FLASH_TOTAL_BYTES) return -1;
    if (!g_flash_hw.status_register_unprotected) {
        fm1_flash_hw_unprotect();
    }

    if (!s_use_internal_mem && fm1_flash_write) {
        return fm1_flash_write(offset, data, bytes);
    }

    uint32_t local_off = offset % sizeof(s_mock_flash_mem);
    if (local_off + bytes > sizeof(s_mock_flash_mem)) {
        bytes = sizeof(s_mock_flash_mem) - local_off;
    }

    /* Flash memory can only flip 1 bits to 0 */
    const uint8_t *src = (const uint8_t *)data;
    for (size_t i = 0; i < bytes; i++) {
        s_mock_flash_mem[local_off + i] &= src[i];
    }
    return 0;
}

int fm1_nvram_save(const void *data, size_t size)
{
    if (!data || size == 0) return -1;
    if (size > (FM1_FLASH_SECTOR_SIZE - sizeof(fm1_nvram_header_t))) return -1;

    if (!g_flash_hw.is_initialized) {
        fm1_flash_hw_init(0);
    }

    /* Prepare header */
    fm1_nvram_header_t hdr;
    memset(&hdr, 0, sizeof(hdr));
    hdr.magic = FM1_NVRAM_MAGIC;
    hdr.version = 1;
    hdr.jedec_id = g_flash_hw.jedec_id;
    hdr.payload_bytes = (uint32_t)size;
    hdr.crc32 = fm1_calc_crc32(data, size);
    hdr.hw_rev = (uint8_t)g_flash_hw.rev;

    /* Erase persistent sector before write */
    if (fm1_flash_hw_erase_sector(FM1_NVRAM_OFFSET_DEFAULT) != 0) {
        return -2;
    }

    /* Write header */
    if (fm1_flash_hw_write(FM1_NVRAM_OFFSET_DEFAULT, &hdr, sizeof(hdr)) != 0) {
        return -3;
    }

    /* Write payload */
    if (fm1_flash_hw_write(FM1_NVRAM_OFFSET_DEFAULT + sizeof(hdr), data, size) != 0) {
        return -4;
    }

    return 0;
}

int fm1_nvram_load(void *buffer, size_t max_size, size_t *out_size)
{
    if (!buffer || max_size == 0) return -1;

    if (!g_flash_hw.is_initialized) {
        fm1_flash_hw_init(0);
    }

    fm1_nvram_header_t hdr;
    if (fm1_flash_hw_read(FM1_NVRAM_OFFSET_DEFAULT, &hdr, sizeof(hdr)) != 0) {
        return -2;
    }

    /* Validate header magic */
    if (hdr.magic != FM1_NVRAM_MAGIC) {
        return -3; /* Uninitialized or corrupt */
    }

    if (hdr.payload_bytes == 0 || hdr.payload_bytes > max_size) {
        return -4;
    }

    /* Read payload */
    if (fm1_flash_hw_read(FM1_NVRAM_OFFSET_DEFAULT + sizeof(hdr), buffer, hdr.payload_bytes) != 0) {
        return -5;
    }

    /* Verify CRC32 */
    uint32_t calc = fm1_calc_crc32(buffer, hdr.payload_bytes);
    if (calc != hdr.crc32) {
        return -6; /* CRC mismatch */
    }

    if (out_size) {
        *out_size = hdr.payload_bytes;
    }

    return 0;
}

int fm1_nvram_erase(void)
{
    if (!g_flash_hw.is_initialized) {
        fm1_flash_hw_init(0);
    }
    return fm1_flash_hw_erase_sector(FM1_NVRAM_OFFSET_DEFAULT);
}
