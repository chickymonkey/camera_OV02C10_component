"""OV02C10 MIPI-CSI sensor driver for esp_video_camera (Guition JC8012P4A1).

This component has no runtime code. It copies a standalone ESP-IDF component
(idf/esp_cam_sensor_ov02c10) into the build's components/ directory and turns on
its Kconfig options. The driver registers itself in esp_cam_sensor's
auto-detect table, so esp_video_camera finds it with no changes.
"""

from pathlib import Path

import esphome.config_validation as cv
from esphome.components.esp32 import add_extra_build_file, add_idf_sdkconfig_option
from esphome.core import CORE

CODEOWNERS = []
DEPENDENCIES = ["esp32"]

CONF_LANES = "lanes"
CONF_GAIN_LIMIT = "gain_limit"
CONF_IPA_JSON = "ipa_json"

IDF_COMPONENT = "esp_cam_sensor_ov02c10"
IDF_DIR = Path(__file__).parent / "idf" / IDF_COMPONENT

REQUIRED_FILES = (
    "ov02c10.c",
    "include/ov02c10.h",
    "private_include/ov02c10_settings.h",
)

CONFIG_SCHEMA = cv.Schema(
    {
        # The Guition demo runs 1 lane; both lanes are wired on the board.
        cv.Optional(CONF_LANES, default=1): cv.one_of(1, 2, int=True),
        cv.Optional(CONF_GAIN_LIMIT, default=66016): cv.int_range(min=4000, max=126016),
        cv.Optional(CONF_IPA_JSON): cv.file_,
    }
)


def _check_sources():
    missing = [f for f in REQUIRED_FILES if not (IDF_DIR / f).is_file()]
    if missing:
        raise cv.Invalid(
            "ov02c10: driver sources incomplete, copy them from the Guition demo "
            f"(components/esp_cam_sensor/sensors/ov02c10): missing {', '.join(missing)}"
        )


async def to_code(config):
    _check_sources()

    for src in sorted(IDF_DIR.rglob("*")):
        if src.is_file():
            rel = src.relative_to(IDF_DIR).as_posix()
            add_extra_build_file(f"components/{IDF_COMPONENT}/{rel}", src)

    add_idf_sdkconfig_option("CONFIG_CAMERA_OV02C10", True)
    add_idf_sdkconfig_option("CONFIG_CAMERA_OV02C10_AUTO_DETECT_MIPI_INTERFACE_SENSOR", True)
    add_idf_sdkconfig_option("CONFIG_CAMERA_OV02C10_ABSOLUTE_GAIN_LIMIT", config[CONF_GAIN_LIMIT])

    one_lane = config[CONF_LANES] == 1
    add_idf_sdkconfig_option("CONFIG_CAMERA_OV02C10_MIPI_RAW10_1920X1080_30FPS_1_LANE", one_lane)
    add_idf_sdkconfig_option("CONFIG_CAMERA_OV02C10_MIPI_RAW10_1920X1080_30FPS_2_LANE", not one_lane)
    suffix = "1_LANE" if one_lane else "2_LANE"
    add_idf_sdkconfig_option(
        f"CONFIG_CAMERA_OV02C10_MIPI_DEFAULT_FMT_RAW10_1920X1080_30FPS_{suffix}", True
    )

    if CONF_IPA_JSON in config:
        ipa = f"{IDF_COMPONENT}_ipa.json"
        add_extra_build_file(ipa, Path(CORE.relative_config_path(config[CONF_IPA_JSON])))
        add_idf_sdkconfig_option("CONFIG_CAMERA_OV02C10_DEFAULT_IPA_JSON_CONFIGURATION_FILE", False)
        add_idf_sdkconfig_option("CONFIG_CAMERA_OV02C10_CUSTOMIZED_IPA_JSON_CONFIGURATION_FILE", True)
        add_idf_sdkconfig_option(
            "CONFIG_CAMERA_OV02C10_CUSTOMIZED_IPA_JSON_CONFIGURATION_FILE_PATH",
            str(CORE.relative_build_path(ipa)),
        )
