"""OV02C10 MIPI-CSI sensor driver for esp_video_camera (Guition JC8012P4A1).

The driver sources (ov02c10.c + headers) sit next to this file and are compiled
into the firmware like any other ESPHome component source. ov02c10.c registers
itself in esp_cam_sensor's auto-detect table, so esp_video_camera finds the
sensor during esp_video_init() without any changes to that component.
"""

from pathlib import Path

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components.esp32 import add_extra_build_file, add_idf_sdkconfig_option
from esphome.const import CONF_ID
from esphome.core import CORE

CODEOWNERS = []
DEPENDENCIES = ["esp32"]

CONF_LANES = "lanes"
CONF_GAIN_LIMIT = "gain_limit"
CONF_IPA_JSON = "ipa_json"

DEFAULT_IPA_JSON = Path(__file__).parent / "ov02c10_default_p4_eco5.json"
IPA_BUILD_FILE = "ov02c10_ipa.json"

ov02c10_ns = cg.esphome_ns.namespace("ov02c10")
OV02C10Driver = ov02c10_ns.class_("OV02C10Driver", cg.Component)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(OV02C10Driver),
        # The Guition demo runs 1 lane; both lanes are wired on the board.
        cv.Optional(CONF_LANES, default=1): cv.one_of(1, 2, int=True),
        cv.Optional(CONF_GAIN_LIMIT, default=66016): cv.int_range(min=4000, max=126016),
        cv.Optional(CONF_IPA_JSON): cv.file_,
    }
).extend(cv.COMPONENT_SCHEMA)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    # Read by ov02c10_config.h (via esphome/core/defines.h).
    cg.add_define("OV02C10_LANES", config[CONF_LANES])
    cg.add_define("OV02C10_GAIN_LIMIT", config[CONF_GAIN_LIMIT])

    # IPA (ISP auto-exposure / white-balance / colour) tuning.
    # esp_ipa collects JSON files from esp_cam_sensor's per-sensor Kconfig
    # options and keys them by the top-level sensor name inside the file
    # ("OV02C10"). esp_cam_sensor has no OV02C10 option, so the file is
    # routed through the OV5647 "customized IPA file" slot. That board has no
    # OV5647, so the only side effect is that an OV5647 would lose its tuning.
    json_path = (
        Path(CORE.relative_config_path(config[CONF_IPA_JSON]))
        if CONF_IPA_JSON in config
        else DEFAULT_IPA_JSON
    )
    add_extra_build_file(IPA_BUILD_FILE, json_path)
    add_idf_sdkconfig_option("CONFIG_CAMERA_OV5647", True)
    add_idf_sdkconfig_option("CONFIG_CAMERA_OV5647_DEFAULT_IPA_JSON_CONFIGURATION_FILE", False)
    add_idf_sdkconfig_option("CONFIG_CAMERA_OV5647_CUSTOMIZED_IPA_JSON_CONFIGURATION_FILE", True)
    add_idf_sdkconfig_option(
        "CONFIG_CAMERA_OV5647_CUSTOMIZED_IPA_JSON_CONFIGURATION_FILE_PATH",
        str(CORE.relative_build_path(IPA_BUILD_FILE)),
    )
