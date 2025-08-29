# TRMNL Home Assistant Integration Installation

This integration allows you to control and monitor TRMNL devices directly from Home Assistant.

## Installation Methods

### Method 1: HACS (Recommended)

1. **Open HACS** in your Home Assistant instance
2. **Navigate to Integrations**
3. **Click the menu** (three dots) in the top right corner
4. **Select "Custom repositories"**
5. **Add this repository**:
   - URL: `https://github.com/chbarnhouse/trmnl-ha-integration`
   - Category: Integration
6. **Click "Add"**
7. **Find "TRMNL"** in the integrations list
8. **Click "Download"**
9. **Restart Home Assistant**
10. **Add the integration** through the UI

### Method 2: Manual Installation

1. **Download** the latest release from GitHub
2. **Extract** the `custom_components/trmnl` folder
3. **Copy** it to your Home Assistant `custom_components` directory:
   ```
   config/
     custom_components/
       trmnl/
         __init__.py
         api.py
         config_flow.py
         const.py
         manifest.json
         sensor.py
         strings.json
         switch.py
   ```
4. **Restart Home Assistant**
5. **Add the integration** through the UI

## Configuration

### Step 1: Get TRMNL API Credentials

1. **Log in** to your TRMNL account
2. **Navigate** to the Developer section
3. **Generate** an API token
4. **Note** your device ID (found in device settings)

### Step 2: Add Integration

1. **Go to** Settings → Devices & Services
2. **Click** "Add Integration"
3. **Search** for "TRMNL"
4. **Enter** your credentials:
   - **API Token**: Your TRMNL API token
   - **Device ID**: Your TRMNL device ID
   - **Base URL**: (Optional) Custom TRMNL API URL

### Step 3: Verify Installation

After setup, you should see:

#### Sensors
- `sensor.trmnl_battery` - Battery percentage
- `sensor.trmnl_wifi_signal` - WiFi signal strength
- `sensor.trmnl_device_status` - Online/offline status
- `sensor.trmnl_firmware_version` - Current firmware version
- `sensor.trmnl_last_seen` - Last communication timestamp

#### Switches
- `switch.trmnl_auto_refresh` - Enable/disable automatic refreshing

#### Services
- `trmnl.refresh_display` - Manually refresh the display
- `trmnl.update_plugin` - Change the active plugin
- `trmnl.send_notification` - Send a notification to the device

## Usage Examples

### Automation Examples

#### Refresh Display at Sunrise
```yaml
automation:
  - alias: "TRMNL Morning Refresh"
    trigger:
      platform: sun
      event: sunrise
    action:
      service: trmnl.refresh_display
      data:
        entity_id: sensor.trmnl_device_status
```

#### Send Weather Alert
```yaml
automation:
  - alias: "TRMNL Weather Alert"
    trigger:
      platform: state
      entity_id: weather.home
      attribute: weather_warnings
    condition:
      condition: template
      value_template: "{{ trigger.to_state.attributes.weather_warnings | length > 0 }}"
    action:
      service: trmnl.send_notification
      data:
        entity_id: sensor.trmnl_device_status
        message: "Weather Alert: {{ trigger.to_state.attributes.weather_warnings[0] }}"
        duration: 600
```

#### Auto-refresh Control Based on Presence
```yaml
automation:
  - alias: "TRMNL Auto Refresh Control"
    trigger:
      - platform: state
        entity_id: binary_sensor.someone_home
        to: 'on'
      - platform: state
        entity_id: binary_sensor.someone_home
        to: 'off'
    action:
      service: >
        {% if trigger.to_state.state == 'on' %}
          switch.turn_on
        {% else %}
          switch.turn_off
        {% endif %}
      entity_id: switch.trmnl_auto_refresh
```

### Dashboard Card Example

```yaml
type: entities
title: TRMNL Device
entities:
  - entity: sensor.trmnl_device_status
    name: Status
  - entity: sensor.trmnl_battery
    name: Battery
  - entity: sensor.trmnl_wifi_signal
    name: WiFi Signal
  - entity: switch.trmnl_auto_refresh
    name: Auto Refresh
  - entity: sensor.trmnl_last_seen
    name: Last Seen
```

### Service Call Examples

#### Manual Display Refresh
```yaml
service: trmnl.refresh_display
data:
  entity_id: sensor.trmnl_device_status
```

#### Change Active Plugin
```yaml
service: trmnl.update_plugin
data:
  entity_id: sensor.trmnl_device_status
  plugin_id: "weather-dashboard"
```

#### Send Notification
```yaml
service: trmnl.send_notification
data:
  entity_id: sensor.trmnl_device_status
  message: "Door left open for 5 minutes"
  duration: 300
```

## Troubleshooting

### Common Issues

1. **Integration Not Found**
   - Ensure you've restarted Home Assistant after installation
   - Check that files are in the correct directory

2. **Authentication Errors**
   - Verify your API token is correct and active
   - Check that your device ID matches exactly

3. **Device Shows Offline**
   - Ensure your TRMNL device is connected to WiFi
   - Check if the API base URL is correct
   - Verify network connectivity between HA and TRMNL API

4. **Services Not Working**
   - Check Home Assistant logs for detailed error messages
   - Verify the entity IDs are correct in service calls

### Debug Information

Enable debug logging by adding to `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.trmnl: debug
```

### Getting Help

1. **Check the logs** in Settings → System → Logs
2. **Search existing issues** on GitHub
3. **Create a new issue** with:
   - Home Assistant version
   - Integration version
   - Complete error logs
   - Steps to reproduce

## Uninstallation

### HACS Method
1. Go to HACS → Integrations
2. Find "TRMNL" and click the menu
3. Select "Remove"
4. Restart Home Assistant
5. Remove the integration from Settings → Devices & Services

### Manual Method
1. Delete the `custom_components/trmnl` folder
2. Restart Home Assistant
3. Remove the integration from Settings → Devices & Services