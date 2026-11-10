/* SPDX-License-Identifier: GPL-3.0-only WITH GPL-3.0-linking-exception
 * M-VAVE FM-1 Dual-Hardware SPI NOR Flash Compatibility Driver & NVRAM Engine.
 * Supports Old FM-1 (Puya P25Q80H, 0x856014) and New FM-1 (UCUN UC25HQ80, 0xB36014).
 * Ensures zero-bricking and 100% persistent save compatibility across all manufacturing batches.
 */
#ifndef FM1_FLASH_HW_H
#define FM1_FLASH_HW_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Known JEDEC Manufacturer & Device Identifiers */
#define FM1_JEDEC_PUYA_P25Q80H   0x856014U /* Old FM-1 (Rev 1 / Batch 1) */
#define FM1_JEDEC_UCUN_UC25HQ80  0xB36014U /* New FM-1 (Rev 2 / Autumn 2026 Batch with logo) */
#define FM1_JEDEC_WINBOND_W25Q80 0xEF4014U /* Generic compatible 1MiB */
#define FM1_JEDEC_GD_GD25Q80     0xC84014U /* Generic compatible 1MiB */

/* Geometry Constants */
#define FM1_FLASH_TOTAL_BYTES    (1024U * 1024U) /* 1 MiB / 8 Mbit */
#define FM1_FLASH_SECTOR_SIZE    4096U           /* 4 KiB sector erase */
#define FM1_FLASH_PAGE_SIZE      256U            /* 256 bytes page write */
#define FM1_NVRAM_MAGIC          0x41545346U     /* "FSTA" (FM1 STACK TRACE ARCADE) */

/* NVRAM storage allocation within user Flash:
 * In FM-1 SDK, user storage starts at FlashLimit - UserSize (0x7D000 = 512KB offset)
 */
#define FM1_NVRAM_OFFSET_DEFAULT 0x0007D000U

typedef enum {
    FM1_HW_REV_UNKNOWN = 0,
    FM1_HW_REV1_PUYA   = 1, /* Rev 1: Puya P25Q80H (0x856014) */
    FM1_HW_REV2_UCUN   = 2, /* Rev 2: UCUN UC25HQ80 (0xB36014) */
    FM1_HW_REV_COMPAT  = 3  /* Standard 1MiB JEDEC SPI NOR */
} fm1_hw_rev_t;

typedef struct {
    uint32_t     jedec_id;
    fm1_hw_rev_t rev;
    const char   *chip_name;
    const char   *batch_desc;
    uint32_t     flash_size_bytes;
    uint16_t     sector_size_bytes;
    uint16_t     page_size_bytes;
    bool         status_register_unprotected;
    bool         is_initialized;
} fm1_flash_hw_info_t;

#pragma pack(push, 1)
typedef struct {
    uint32_t magic;          /* FM1_NVRAM_MAGIC */
    uint32_t version;        /* Format version (1) */
    uint32_t jedec_id;       /* 0x856014 or 0xB36014 */
    uint32_t payload_bytes;  /* Number of valid user bytes */
    uint32_t crc32;          /* IEEE 802.3 CRC32 of payload */
    uint8_t  hw_rev;         /* fm1_hw_rev_t */
    uint8_t  reserved[11];   /* Alignment to 32 bytes */
} fm1_nvram_header_t;
#pragma pack(pop)

/* Hardware Flash API */
bool fm1_flash_hw_is_supported_id(uint32_t jedec_id);
int  fm1_flash_hw_init(uint32_t detected_jedec_id);
const fm1_flash_hw_info_t *fm1_flash_hw_get_info(void);
int  fm1_flash_hw_unprotect(void);

/* Low-level flash driver operations with dual-chip support */
int  fm1_flash_hw_read(uint32_t offset, void *data, size_t bytes);
int  fm1_flash_hw_write(uint32_t offset, const void *data, size_t bytes);
int  fm1_flash_hw_erase_sector(uint32_t offset);

/* High-level NVRAM persistence (Leaderboards & Settings) */
int  fm1_nvram_save(const void *data, size_t size);
int  fm1_nvram_load(void *buffer, size_t max_size, size_t *out_size);
int  fm1_nvram_erase(void);

/* CRC32 Utility */
uint32_t fm1_calc_crc32(const void *data, size_t length);

#ifdef __cplusplus
}
#endif

#endif /* FM1_FLASH_HW_H */
