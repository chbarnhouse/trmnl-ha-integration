"""Constants for the TRMNL integration."""

DOMAIN = "trmnl"
CONF_API_TOKEN = "api_token"
CONF_DEVICE_ID = "device_id"
CONF_BASE_URL = "base_url"

DEFAULT_BASE_URL = "https://api.usetrmnl.com"
DEFAULT_SCAN_INTERVAL = 30  # seconds

# Entity types
SENSOR_TYPES = {
    "battery": {
        "name": "Battery",
        "device_class": "battery",
        "unit_of_measurement": "%",
        "icon": "mdi:battery",
    },
    "wifi_signal": {
        "name": "WiFi Signal",
        "device_class": "signal_strength",
        "unit_of_measurement": "dBm",
        "icon": "mdi:wifi",
    },
    "firmware_version": {
        "name": "Firmware Version",
        "icon": "mdi:chip",
    },
    "last_seen": {
        "name": "Last Seen",
        "device_class": "timestamp",
        "icon": "mdi:clock-outline",
    },
    "device_status": {
        "name": "Device Status",
        "icon": "mdi:monitor",
    },
}

# Switch types
SWITCH_TYPES = {
    "auto_refresh": {
        "name": "Auto Refresh",
        "icon": "mdi:refresh-auto",
    },
}

# Service names
SERVICE_REFRESH_DISPLAY = "refresh_display"
SERVICE_UPDATE_PLUGIN = "update_plugin"
SERVICE_SEND_NOTIFICATION = "send_notification"

# API endpoints
API_ENDPOINTS = {
    "display": "/api/display",
    "device_info": "/api/device/{device_id}",
    "plugins": "/api/plugins",
    "refresh": "/api/refresh/{device_id}",
}

# Device info
MANUFACTURER = "TRMNL"
MODEL = "E-Ink Display"