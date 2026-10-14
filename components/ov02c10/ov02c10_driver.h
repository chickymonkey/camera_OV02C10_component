#pragma once

#include <cstddef>
#include <cstdint>

#include "esphome/core/component.h"
#include "ov02c10.h"

namespace esphome {
namespace ov02c10 {

/// Link anchor + config logging for the OV02C10 esp_cam_sensor driver.
///
/// The sensor itself is probed by esp_video_init() (called from
/// esp_video_camera) through esp_cam_sensor's auto-detect table. This class
/// only makes sure ov02c10.c is linked so its table entry exists.
class OV02C10Driver : public Component {
 public:
  void setup() override;
  void dump_config() override;
  float get_setup_priority() const override { return setup_priority::HARDWARE; }

 protected:
  esp_cam_sensor_device_t *(*detect_fn_)(esp_cam_sensor_config_t *){nullptr};
};

}  // namespace ov02c10
}  // namespace esphome
