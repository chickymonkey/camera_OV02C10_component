# esphome-ov02c10

OV02C10 MIPI-CSI camera support for `esp_video_camera` (Psix-anp/esphome-esp-video-camera),
the camera component the esphome-intercom P4 video packages use. This is the sensor
on the Guition JC8012P4A1 (ESP32-P4, 10.1").

The driver comes from Guition's `video_lcd_display` demo
(`components/esp_cam_sensor/sensors/ov02c10`). Here it's a standard ESPHome external
component: the `.c`, `.cpp` and `.h` files sit directly in `components/ov02c10/` and
ESPHome compiles them like any other component. `ov02c10.c` registers itself in
`esp_cam_sensor`'s auto-detect table, so you don't have to fork `esp_cam_sensor` or
`esp_video_camera`.

## Layout

```
components/ov02c10/
  __init__.py                 ESPHome glue: YAML options, defines, IPA JSON hookup
  ov02c10_driver.h / .cpp     small ESPHome component: keeps the driver linked, logs config
  ov02c10_config.h            replaces Guition's Kconfig (lanes, gain limit, format index)
  ov02c10.c                   Guition sensor driver
  ov02c10.h, ov02c10_types.h
  ov02c10_regs.h, ov02c10_settings.h
  ov02c10_mipi_*.h            3 register tables (1-lane 1080p, 2-lane 1080p, 1288x728)
  ov02c10_default_p4_eco5.json   Guition IPA tuning
```

### How it hooks in

- **Build options.** The `lanes:` and `gain_limit:` YAML options become
  `OV02C10_LANES` / `OV02C10_GAIN_LIMIT` in `esphome/core/defines.h`.
  `ov02c10_config.h` turns them into the `CONFIG_CAMERA_OV02C10_*` names the driver
  was written against. Only the register table for the selected mode is compiled in.
- **Linking.** `OV02C10Driver::setup()` takes the address of `ov02c10_detect`. That
  forces the linker to keep `ov02c10.c` and its `.esp_cam_sensor_detect_fn` entry,
  which `esp_video_init()` scans when `esp_video_camera` starts.
- **IPA tuning.** `esp_ipa` only picks up JSON files through `esp_cam_sensor`'s
  per-sensor Kconfig options, and there isn't one for OV02C10. The JSON is therefore
  routed through the OV5647 "customized IPA file" slot. The file's top-level key
  (`"OV02C10"`) is what `esp_ipa` matches on, so it applies to the OV02C10. The only
  side effect is that an OV5647 would lose its tuning, and there isn't one on this board.

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
  # gain_limit: 66016     # x1000; lower = less noise in low light
  # ipa_json: my_tuning.json

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

At boot, `dump_config` should show `Detect hook: linked`. It's working when the log
shows `ov02c10: Detected Camera sensor PID=0x5602`, then
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
