#include "ov02c10_driver.h"
#include "ov02c10_config.h"
#include "esphome/core/log.h"

namespace esphome {
namespace ov02c10 {

static const char *const TAG = "ov02c10";

// Taking the address of ov02c10_detect forces the linker to keep ov02c10.c,
// which carries the .esp_cam_sensor_detect_fn entry esp_video scans at init.
void OV02C10Driver::setup() { this->detect_fn_ = &ov02c10_detect; }

void OV02C10Driver::dump_config() {
  ESP_LOGCONFIG(TAG,
                "OV02C10 sensor driver:\n"
                "  SCCB address: 0x%02X\n"
                "  Expected PID: 0x%04X\n"
                "  MIPI lanes: %d (1920x1080 RAW10 30fps)\n"
                "  Gain limit: %d (x1000)\n"
                "  Detect hook: %s",
                OV02C10_SCCB_ADDR, OV02C10_PID, OV02C10_LANES, OV02C10_GAIN_LIMIT,
                this->detect_fn_ != nullptr ? "linked" : "MISSING");
}

}  // namespace ov02c10
}  // namespace esphome
