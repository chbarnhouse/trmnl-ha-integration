"""The TRMNL integration."""
import asyncio
import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TRMNLApiClient
from . import services
from .const import (
    DOMAIN,
    CONF_API_TOKEN,
    CONF_DEVICE_ID,
    CONF_BASE_URL,
    DEFAULT_SCAN_INTERVAL,
    SERVICE_REFRESH_DISPLAY,
    SERVICE_UPDATE_PLUGIN,
    SERVICE_SEND_NOTIFICATION,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH]

# Service schemas
REFRESH_DISPLAY_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): str,
    }
)

UPDATE_PLUGIN_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): str,
        vol.Required("plugin_id"): str,
    }
)

SEND_NOTIFICATION_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): str,
        vol.Required("message"): str,
        vol.Optional("duration", default=60): int,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up TRMNL from a config entry."""
    api_token = entry.data[CONF_API_TOKEN]
    device_id = entry.data[CONF_DEVICE_ID]
    base_url = entry.data.get(CONF_BASE_URL)

    session = async_get_clientsession(hass)
    api_client = TRMNLApiClient(session, api_token, base_url, device_id)

    coordinator = TRMNLDataUpdateCoordinator(hass, api_client, device_id)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    hass.data.setdefault(DOMAIN, {})["api"] = api_client  # Make API available to services

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Setup dashboard capture services
    await services.async_setup_services(hass)

    # Register services
    async def async_refresh_display(call):
        """Handle refresh display service call."""
        entity_id = call.data.get("entity_id")
        _LOGGER.debug(f"Refreshing display for entity: {entity_id}")
        try:
            await coordinator.api_client.refresh_display(coordinator.device_id)
            await coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(f"Failed to refresh display: {err}")

    async def async_update_plugin(call):
        """Handle update plugin service call."""
        entity_id = call.data.get("entity_id")
        plugin_id = call.data.get("plugin_id")
        _LOGGER.debug(f"Updating plugin to {plugin_id} for entity: {entity_id}")
        try:
            await coordinator.api_client.update_plugin(coordinator.device_id, plugin_id)
            await coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(f"Failed to update plugin: {err}")

    async def async_send_notification(call):
        """Handle send notification service call."""
        entity_id = call.data.get("entity_id")
        message = call.data.get("message")
        duration = call.data.get("duration", 60)
        _LOGGER.debug(f"Sending notification '{message}' for {duration}s to entity: {entity_id}")
        try:
            await coordinator.api_client.send_notification(coordinator.device_id, message, duration)
            await coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(f"Failed to send notification: {err}")

    hass.services.async_register(
        DOMAIN, SERVICE_REFRESH_DISPLAY, async_refresh_display, schema=REFRESH_DISPLAY_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE_PLUGIN, async_update_plugin, schema=UPDATE_PLUGIN_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SEND_NOTIFICATION, async_send_notification, schema=SEND_NOTIFICATION_SCHEMA
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # Remove services if this is the last entry
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_REFRESH_DISPLAY)
            hass.services.async_remove(DOMAIN, SERVICE_UPDATE_PLUGIN)
            hass.services.async_remove(DOMAIN, SERVICE_SEND_NOTIFICATION)

    return unload_ok


class TRMNLDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, api_client: TRMNLApiClient, device_id: str) -> None:
        """Initialize the coordinator."""
        self.api_client = api_client
        self.device_id = device_id
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.api_client.get_device_info(self.device_id)
        except Exception as exception:
            raise UpdateFailed(f"Error communicating with API: {exception}")