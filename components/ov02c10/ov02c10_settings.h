/*
 * SPDX-FileCopyrightText: 2024-2025 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#pragma once

#include <stdio.h>
#include <stdint.h>
#include "ov02c10_config.h"
#include "ov02c10_regs.h"
#include "ov02c10_types.h"

#ifdef __cplusplus
extern "C" {
#endif

#if CONFIG_SOC_MIPI_CSI_SUPPORTED

#if CONFIG_CAMERA_OV02C10_MIPI_RAW10_1920X1080_30FPS_1_LANE
#include "ov02c10_mipi_1lane_24Minput_1920x1080_raw10_30fps.h"
#endif

#if CONFIG_CAMERA_OV02C10_MIPI_RAW10_1288X728_30FPS
#include "ov02c10_mipi_1lane_24Minput_1288x728_raw10_30fps.h"
#endif

#if CONFIG_CAMERA_OV02C10_MIPI_RAW10_1920X1080_30FPS_2_LANE
#include "ov02c10_mipi_2lane_24Minput_1920x1080_raw10_30fps.h"
#endif

#endif


#ifdef __cplusplus
}
#endif
