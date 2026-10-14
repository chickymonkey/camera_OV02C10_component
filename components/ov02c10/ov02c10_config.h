/*
 * Build-time options for the OV02C10 driver.
 *
 * In Espressif's esp_cam_sensor these come from Kconfig. Here the driver is
 * compiled as part of the ESPHome component, so __init__.py writes
 * OV02C10_LANES / OV02C10_GAIN_LIMIT into esphome/core/defines.h and this
 * header turns them into the CONFIG_CAMERA_OV02C10_* names the driver expects.
 */
#pragma once

#include "sdkconfig.h"
#include "esphome/core/defines.h"

#ifndef OV02C10_LANES
#define OV02C10_LANES 1
#endif

#ifndef OV02C10_GAIN_LIMIT
#define OV02C10_GAIN_LIMIT 66016
#endif

#define CONFIG_CAMERA_OV02C10 1
#define CONFIG_CAMERA_OV02C10_AUTO_DETECT_MIPI_INTERFACE_SENSOR 1
#define CONFIG_CAMERA_OV02C10_ABSOLUTE_GAIN_LIMIT OV02C10_GAIN_LIMIT

/* Format indices match ov02c10_isp_info_mipi[] in ov02c10.c:
 * 0 = 1288x728 1-lane (untested), 1 = 1920x1080 1-lane, 2 = 1920x1080 2-lane */
#if OV02C10_LANES == 2
#define CONFIG_CAMERA_OV02C10_MIPI_RAW10_1920X1080_30FPS_2_LANE 1
#define CONFIG_CAMERA_OV02C10_MIPI_IF_FORMAT_INDEX_DEFAULT 2
#else
#define CONFIG_CAMERA_OV02C10_MIPI_RAW10_1920X1080_30FPS_1_LANE 1
#define CONFIG_CAMERA_OV02C10_MIPI_IF_FORMAT_INDEX_DEFAULT 1
#endif
