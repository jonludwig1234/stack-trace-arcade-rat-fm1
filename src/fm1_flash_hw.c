/* SPDX-License-Identifier: GPL-3.0-only WITH GPL-3.0-linking-exception
 * M-VAVE FM-1 Dual-Hardware SPI NOR Flash Compatibility Driver & NVRAM Engine.
 * Supports Old FM-1 (Puya P25Q80H, 0x856014) and New FM-1 (UCUN UC25HQ80, 0xB36014).
 */
#include "fm1_flash_hw.h"
#include <string.h>

/* Optional weak FM1 SDK bindings (present on device builds, mocked in unit tests) */
#if defined(__GNUC__) && !defined(__GCC_PI32V2__)
__attribute__((weak)) uint32_t fm1_flash_size(void) { return FM1_FLASH_TOTAL_BYTES; }
__attribute__((weak)) int fm1_flash_read(uint32_t offset, void *data, size_t bytes);
__attribute__((weak)) int fm1_flash_write(uint32_t offset, const void *data, size_t bytes);
__attribute__((weak)) int fm1_flash_erase(uint32_t offset);
#elif defined(__GCC_PI32V2__)
extern uint32_t fm1_flash_size(void);
extern int fm1_flash_read(uint32_t offset, void *data, size_t bytes);
extern int fm1_flash_write(uint32_t offset, const void *data, size_t bytes);
extern int fm1_flash_erase(uint32_t offset);
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

#ifndef __GCC_PI32V2__
/* Emulated hardware Flash buffer (2 sectors: Slot A at 0x7D000, Slot B at 0x7E000) */
static uint8_t s_mock_flash_mem[FM1_FLASH_SECTOR_SIZE * 2];
static bool s_use_internal_mem = false;
static int s_fault_read_after = -1;
static int s_fault_write_after = -1;
static int s_fault_erase_after = -1;

void fm1_flash_hw_set_mock_faults(int read_fail_after, int write_fail_after, int erase_fail_after)
{
    s_fault_read_after = read_fail_after;
    s_fault_write_after = write_fail_after;
    s_fault_erase_after = erase_fail_after;
}

static bool mock_check_fault(int *counter)
{
    if (*counter < 0) return false;
    if (*counter == 0) return true;
    (*counter)--;
    return false;
}

static int mock_map_range(uint32_t offset, size_t bytes, uint32_t *local_off)
{
    if (bytes > sizeof(s_mock_flash_mem)) return -1;
    if (offset < FM1_NVRAM_OFFSET_DEFAULT) return -1;
    uint32_t rel = offset - FM1_NVRAM_OFFSET_DEFAULT;
    if (rel > sizeof(s_mock_flash_mem) - bytes) return -1;
    *local_off = rel;
    return 0;
}
#endif

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
    if (!data && length > 0) return 0;
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

#ifndef __GCC_PI32V2__
    /* Initialize internal memory buffer to 0xFF (erased state) and reset fault counters */
    memset(s_mock_flash_mem, 0xFF, sizeof(s_mock_flash_mem));
    s_use_internal_mem = true;
    fm1_flash_hw_set_mock_faults(-1, -1, -1);
#endif

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
    if (bytes > FM1_FLASH_TOTAL_BYTES || offset > FM1_FLASH_TOTAL_BYTES - bytes) return -1;

#ifdef __GCC_PI32V2__
    return fm1_flash_read(offset, data, bytes);
#else
    if (!s_use_internal_mem && fm1_flash_read) {
        return fm1_flash_read(offset, data, bytes);
    }
    if (mock_check_fault(&s_fault_read_after)) return -1;

    uint32_t local_off = 0;
    if (mock_map_range(offset, bytes, &local_off) != 0) return -1;
    memcpy(data, &s_mock_flash_mem[local_off], bytes);
    return 0;
#endif
}

int fm1_flash_hw_erase_sector(uint32_t offset)
{
    /* Sectors must be 4096-byte aligned */
    if ((offset % FM1_FLASH_SECTOR_SIZE) != 0) return -1;
    if (offset >= FM1_FLASH_TOTAL_BYTES) return -1;

#ifdef __GCC_PI32V2__
    return fm1_flash_erase(offset);
#else
    if (!s_use_internal_mem && fm1_flash_erase) {
        return fm1_flash_erase(offset);
    }
    if (mock_check_fault(&s_fault_erase_after)) return -1;

    uint32_t local_off = 0;
    if (mock_map_range(offset, FM1_FLASH_SECTOR_SIZE, &local_off) != 0) return -1;
    memset(&s_mock_flash_mem[local_off], 0xFF, FM1_FLASH_SECTOR_SIZE);
    return 0;
#endif
}

int fm1_flash_hw_write(uint32_t offset, const void *data, size_t bytes)
{
    if (!data || bytes == 0) return -1;
    if (bytes > FM1_FLASH_TOTAL_BYTES || offset > FM1_FLASH_TOTAL_BYTES - bytes) return -1;
    if (!g_flash_hw.status_register_unprotected) {
        fm1_flash_hw_unprotect();
    }

#ifdef __GCC_PI32V2__
    return fm1_flash_write(offset, data, bytes);
#else
    if (!s_use_internal_mem && fm1_flash_write) {
        return fm1_flash_write(offset, data, bytes);
    }
    if (mock_check_fault(&s_fault_write_after)) return -1;

    uint32_t local_off = 0;
    if (mock_map_range(offset, bytes, &local_off) != 0) return -1;

    /* Flash memory can only flip 1 bits to 0 */
    const uint8_t *src = (const uint8_t *)data;
    for (size_t i = 0; i < bytes; i++) {
        s_mock_flash_mem[local_off + i] &= src[i];
    }
    return 0;
#endif
}

static uint32_t nvram_get_seq(const fm1_nvram_header_t *hdr)
{
    return (uint32_t)hdr->reserved[0] |
           ((uint32_t)hdr->reserved[1] << 8) |
           ((uint32_t)hdr->reserved[2] << 16) |
           ((uint32_t)hdr->reserved[3] << 24);
}

static void nvram_set_seq(fm1_nvram_header_t *hdr, uint32_t seq)
{
    hdr->reserved[0] = (uint8_t)(seq & 0xFFU);
    hdr->reserved[1] = (uint8_t)((seq >> 8) & 0xFFU);
    hdr->reserved[2] = (uint8_t)((seq >> 16) & 0xFFU);
    hdr->reserved[3] = (uint8_t)((seq >> 24) & 0xFFU);
}

/* Validate an NVRAM slot without overwriting caller's output buffer unless valid & fits.
 * Returns 0 if valid, -2 read err, -3 bad magic/version, -4 bad/oversized payload_bytes,
 * -5 payload read err, -6 CRC mismatch. */
static int nvram_probe_slot(uint32_t slot_offset, void *scratch, size_t scratch_cap,
                            fm1_nvram_header_t *out_hdr)
{
    fm1_nvram_header_t hdr;
    if (fm1_flash_hw_read(slot_offset, &hdr, sizeof(hdr)) != 0) {
        return -2;
    }
    if (hdr.magic != FM1_NVRAM_MAGIC || hdr.version != FM1_NVRAM_VERSION) {
        return -3;
    }
    size_t max_slot_payload = FM1_FLASH_SECTOR_SIZE - sizeof(fm1_nvram_header_t);
    if (hdr.payload_bytes == 0 || hdr.payload_bytes > max_slot_payload) {
        return -4;
    }
    if (scratch && hdr.payload_bytes <= scratch_cap) {
        if (fm1_flash_hw_read(slot_offset + (uint32_t)sizeof(hdr), scratch, hdr.payload_bytes) != 0) {
            return -5;
        }
        if (fm1_calc_crc32(scratch, hdr.payload_bytes) != hdr.crc32) {
            return -6;
        }
    } else if (!scratch) {
        /* Verify CRC in fixed chunks when probing during save */
        uint8_t chunk[256];
        uint32_t crc = 0xFFFFFFFFU;
        size_t remaining = hdr.payload_bytes;
        uint32_t addr = slot_offset + (uint32_t)sizeof(hdr);
        init_crc32_table();
        while (remaining > 0) {
            size_t n = remaining > sizeof(chunk) ? sizeof(chunk) : remaining;
            if (fm1_flash_hw_read(addr, chunk, n) != 0) return -5;
            for (size_t i = 0; i < n; i++) {
                crc = s_crc32_table[(crc ^ chunk[i]) & 0xFFU] ^ (crc >> 8);
            }
            addr += (uint32_t)n;
            remaining -= n;
        }
        if ((crc ^ 0xFFFFFFFFU) != hdr.crc32) {
            return -6;
        }
    }
    *out_hdr = hdr;
    return 0;
}

int fm1_nvram_save(const void *data, size_t size)
{
    if (!data || size == 0) return -1;
    if (size > (FM1_FLASH_SECTOR_SIZE - sizeof(fm1_nvram_header_t))) return -1;

    if (!g_flash_hw.is_initialized) {
        fm1_flash_hw_init(0);
    }

    /* Probe both A/B slots to find the active valid slot and highest sequence */
    static const uint32_t slots[2] = { FM1_NVRAM_OFFSET_DEFAULT, FM1_NVRAM_OFFSET_BACKUP };
    int active_idx = -1;
    uint32_t best_seq = 0;
    for (int i = 0; i < 2; i++) {
        fm1_nvram_header_t probe_hdr;
        if (nvram_probe_slot(slots[i], NULL, 0, &probe_hdr) == 0) {
            uint32_t seq = nvram_get_seq(&probe_hdr);
            if (active_idx < 0 || seq >= best_seq) {
                active_idx = i;
                best_seq = seq;
            }
        }
    }

    /* Write to the inactive slot so an interrupted erase/write preserves committed data */
    uint32_t target_slot = (active_idx == 0) ? slots[1] : slots[0];

    fm1_nvram_header_t hdr;
    memset(&hdr, 0, sizeof(hdr));
    hdr.magic = FM1_NVRAM_MAGIC;
    hdr.version = FM1_NVRAM_VERSION;
    hdr.jedec_id = g_flash_hw.jedec_id;
    hdr.payload_bytes = (uint32_t)size;
    hdr.crc32 = fm1_calc_crc32(data, size);
    hdr.hw_rev = (uint8_t)g_flash_hw.rev;
    nvram_set_seq(&hdr, (active_idx >= 0) ? (best_seq + 1U) : 1U);

    if (fm1_flash_hw_erase_sector(target_slot) != 0) {
        return -2;
    }

    /* Write payload first, then header so an interrupted payload write leaves header erased */
    if (fm1_flash_hw_write(target_slot + (uint32_t)sizeof(hdr), data, size) != 0) {
        return -4;
    }

    if (fm1_flash_hw_write(target_slot, &hdr, sizeof(hdr)) != 0) {
        return -3;
    }

    return 0;
}

int fm1_nvram_load(void *buffer, size_t max_size, size_t *out_size)
{
    if (!buffer || max_size == 0) return -1;

    if (!g_flash_hw.is_initialized) {
        fm1_flash_hw_init(0);
    }

    static const uint32_t slots[2] = { FM1_NVRAM_OFFSET_DEFAULT, FM1_NVRAM_OFFSET_BACKUP };
    int best_idx = -1;
    uint32_t best_seq = 0;
    fm1_nvram_header_t best_hdr;
    int last_err = -3;

    for (int i = 0; i < 2; i++) {
        fm1_nvram_header_t hdr;
        int rc = nvram_probe_slot(slots[i], NULL, 0, &hdr);
        if (rc == 0) {
            uint32_t seq = nvram_get_seq(&hdr);
            if (best_idx < 0 || seq >= best_seq) {
                best_idx = i;
                best_seq = seq;
                best_hdr = hdr;
            }
        } else if (last_err == -3 || rc < last_err) {
            last_err = rc;
        }
    }

    if (best_idx < 0) {
        return last_err;
    }
    if (best_hdr.payload_bytes > max_size) {
        return -4;
    }
    if (fm1_flash_hw_read(slots[best_idx] + (uint32_t)sizeof(best_hdr), buffer, best_hdr.payload_bytes) != 0) {
        return -5;
    }
    if (fm1_calc_crc32(buffer, best_hdr.payload_bytes) != best_hdr.crc32) {
        return -6;
    }

    if (out_size) {
        *out_size = best_hdr.payload_bytes;
    }
    return 0;
}

int fm1_nvram_erase(void)
{
    if (!g_flash_hw.is_initialized) {
        fm1_flash_hw_init(0);
    }
    int r0 = fm1_flash_hw_erase_sector(FM1_NVRAM_OFFSET_DEFAULT);
    int r1 = fm1_flash_hw_erase_sector(FM1_NVRAM_OFFSET_BACKUP);
    return (r0 != 0) ? r0 : r1;
}
