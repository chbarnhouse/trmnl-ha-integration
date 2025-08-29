# TRMNL Home Assistant Integration

A custom Home Assistant integration that allows you to control and monitor TRMNL devices from your Home Assistant instance.

## Features

- **Device Discovery**: Automatically discover TRMNL devices on your network
- **Device Control**: Control display content, refresh intervals, and device settings
- **Status Monitoring**: Monitor battery level, WiFi signal strength, and device status
- **Plugin Management**: Switch between different plugins and manage display content
- **Service Calls**: Trigger display updates and control device functions from automations

## Installation

### HACS Installation (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the "+" button and search for "TRMNL"
4. Install the integration
5. Restart Home Assistant
6. Go to Configuration > Integrations
7. Click "Add Integration" and search for "TRMNL"
8. Follow the configuration steps

### Manual Installation

1. Copy the `custom_components/trmnl` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Configuration > Integrations
4. Click "Add Integration" and search for "TRMNL"
5. Follow the configuration steps

## Configuration

The integration requires:

- **API Token**: Your TRMNL API token from the TRMNL dashboard
- **Device ID**: The unique identifier for your TRMNL device
- **Base URL**: TRMNL API base URL (usually https://api.usetrmnl.com)

## Entities

This integration provides the following entities:

### Sensors
- **Battery Level**: Current battery percentage
- **WiFi Signal**: WiFi signal strength
- **Device Status**: Current device status (online/offline/sleeping)
- **Firmware Version**: Current firmware version
- **Last Update**: Timestamp of last device communication

### Switches
- **Display Power**: Turn the display on/off
- **Auto Refresh**: Enable/disable automatic content refresh

### Services

- `trmnl.refresh_display`: Manually trigger a display refresh
- `trmnl.update_plugin`: Change the active plugin
- `trmnl.send_notification`: Send a notification to the device

## Usage Examples

### Automation Example
```yaml
automation:
  - alias: "Update TRMNL at sunrise"
    trigger:
      platform: sun
      event: sunrise
    action:
      service: trmnl.refresh_display
      data:
        entity_id: sensor.trmnl_device_status
```

### Service Call Example
```yaml
service: trmnl.send_notification
data:
  entity_id: sensor.trmnl_device
  message: "Good morning! Today's weather is sunny."
  duration: 300
```

## Troubleshooting

1. **Device Not Found**: Ensure your TRMNL device is online and the API token is correct
2. **Connection Issues**: Check your Home Assistant network configuration and firewall settings
3. **Authentication Errors**: Verify your API token in the TRMNL dashboard

## Support

For issues and feature requests, please create an issue on the GitHub repository.

## License

MIT License