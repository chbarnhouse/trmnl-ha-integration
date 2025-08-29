## TRMNL Home Assistant Integration

Control and monitor your TRMNL e-ink displays directly from Home Assistant.

### Features

- **Device Control**: Refresh display, switch plugins, send notifications
- **Monitoring**: Battery level, WiFi signal, device status, firmware version
- **Automation**: Integrate TRMNL devices into your Home Assistant automations
- **Easy Setup**: Simple configuration through the Home Assistant UI

### Installation

1. Add this repository to HACS as a custom repository
2. Install the "TRMNL Integration" 
3. Restart Home Assistant
4. Add the integration through Settings → Devices & Services

### Requirements

- Home Assistant 2024.1.0 or newer
- TRMNL device with API access
- TRMNL API token and device ID

### Configuration

You'll need:
- **API Token**: From your TRMNL developer dashboard
- **Device ID**: Your specific TRMNL device identifier
- **Base URL**: Usually the default TRMNL API URL

### Support

For issues and support, please visit the [GitHub repository](https://github.com/chbarnhouse/trmnl-ha-integration).