# esphome-ov02c10

OV02C10 MIPI-CSI camera support for `esp_video_camera` (Psix-anp/esphome-esp-video-camera),
the camera component the esphome-intercom P4 video packages use. This is the sensor
on the Guition JC8012P4A1 (ESP32-P4, 10.1").

The driver comes from Guition's `video_lcd_display` demo. Here it's packaged as a
standalone ESP-IDF component that registers itself in `esp_cam_sensor`'s auto-detect
table, so you don't have to fork `esp_cam_sensor` or `esp_video_camera`.

## Layout

```
components/ov02c10/
  __init__.py                      ESPHome glue: copies the IDF component into the build, sets Kconfig
  idf/esp_cam_sensor_ov02c10/
    CMakeLists.txt                 links ov02c10_detect into the auto-detect table
    project_include.cmake          hands the IPA JSON to esp_ipa
    Kconfig                        fixed copy of Kconfig.ov02c10
    ov02c10.c                      Guition driver (AE logs moved to DEBUG)
    cfg/ov02c10_default_p4_eco5.json
    include/                       ov02c10.h, ov02c10_types.h
    private_include/               ov02c10_settings.h, ov02c10_regs.h, 3 register tables
```

All driver sources come from Guition's `video_lcd_display/components/esp_cam_sensor/sensors/ov02c10`.

## Changes from the Guition original

- Kconfig: the 1-lane and 2-lane 1080p "default format" entries both used the same
  symbol (`..._DEFAULT_FMT_RAW10_1920X1080_30FPS`). That made the 2-lane mode
  impossible to select. It's now two separate symbols.
- Kconfig: every format defaulted to `n`, which leaves an empty format table. The
  1-lane 1080p mode (the one the demo uses) is now on by default.
- The `CONFIG_CAMERA_OV02C10_MAX_SUPPORT` macro was removed. It pointed at a symbol
  that doesn't exist and nothing used it.
- The exposure, gain and ioctl logs fired on every frame at INFO level. They're now
  DEBUG, so they don't flood the ESPHome log and API.
- The detect registration is now gated on `..._AUTO_DETECT_MIPI_INTERFACE_SENSOR`,
  the same way upstream drivers do it.
- `ov02c10.h` declared `sc2336_detect` (a copy-paste slip). It now declares `ov02c10_detect`.
- `ov02c10_settings.h` pulled in all three register tables unconditionally, so unused
  `static const` arrays would trip IDF's warnings-as-errors. Each table is now
  included only when its mode is enabled.
- `ov02c10.c` now includes `<stdlib.h>`, `<inttypes.h>` and `esp_heap_caps.h`
  explicitly instead of relying on them coming in through other headers.
- Note: Guition's `ov02c10_regs.h` labels 0x3508/0x3509 as digital gain and 0x350a as
  analog gain. The Linux OV02C10 driver has those the other way round. The register
  writes themselves are left exactly as Guition ships them.

## Step 1: camera-only bring-up

```yaml
external_components:
  - source: github://Psix-anp/esphome-esp-video-camera@main
    components: [esp_video_camera]
  - source:
      type: local
      path: esphome-ov02c10/components
    components: [ov02c10]

esp_ldo:
  - channel: 3            # MIPI D-PHY supply (ESP_LDO_VO3 on the schematic)
    voltage: 2.5V

i2c:
  - id: internal_i2c
    sda: GPIO7
    scl: GPIO8
    frequency: 100kHz     # demo value; 400kHz once it's stable
    scan: true            # expect 0x18 ES8311, 0x32 RTC, 0x36 OV02C10, 0x40 ES7210

ov02c10:
  lanes: 1                # demo-validated; 2 is wired but untested

esp_video_camera:
  id: p4_camera
  name: P4 Camera
  i2c_id: internal_i2c
  device: jpeg
  resolution: 960x540     # exact 1/2 PPA downscale of 1920x1080
  max_framerate: 15
  enable_xclk: false      # module has its own 24 MHz oscillator

esphome:
  on_boot:
    priority: -100
    then:
      - lambda: 'id(p4_camera).set_runtime_hflip(true);'   # demo runs with hflip on
```

It's working when the log shows `ov02c10: Detected Camera sensor PID=0x5602`, then
`Capture resolution: 1920x1080`, then JPEG frames at 960x540. The camera entity in
Home Assistant should show a correctly coloured picture.

## Step 2: plug into esphome-intercom

Add the `external_components` entry and the `ov02c10:` block to your board package.
Then override the JPEG video substitutions:

```yaml
substitutions:
  p4_video_width: "960"
  p4_video_height: "540"
  p4_camera_rotation: "0"            # change once you know how the module is mounted
  p4_video_max_decode_width: "960"
  p4_video_max_decode_height: "960"
```

`esp_video_camera` only downscales by exact 1/16 steps. The intercom default of
800x800 isn't an exact step from 1920x1080, so it would fall back to full 1080p
JPEG, which is too big for the RTP path. Exact 16:9 sizes that work: 720x405,
960x540, 1200x675 and 1440x810. With a rotation of 90 or 270, the JPEG width and
height swap, so swap the voip_stack and source sizes to match.

## Caveats

- **IPA tuning is for ECO5, meaning P4 silicon v3.x.** If your chip is older than
  v3 (`CONFIG_ESP32P4_SELECTS_REV_LESS_V3`), check whether the Guition demo also
  ships an `..._eco4.json` and pass it in with `ov02c10: ipa_json: path/to/file.json`.
- `OV02C10_SENSOR_NAME` in `ov02c10.h` has to be `"OV02C10"` to match the JSON's
  top-level key. If it isn't, the IPA settings are ignored and the image comes out
  washed out or green.
- Auto-detect also tries SC202CS and OV5647 at address 0x36. Both fail harmlessly on
  the chip-ID check before OV02C10 matches.
