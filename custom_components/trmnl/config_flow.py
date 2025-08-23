"""Config flow for TRMNL integration."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import TRMNLApiClient, TRMNLApiError, TRMNLAuthenticationError
from .const import (
    DOMAIN,
    CONF_API_TOKEN,
    CONF_DEVICE_ID,
    CONF_BASE_URL,
    DEFAULT_BASE_URL,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_TOKEN): str,
        vol.Required(CONF_DEVICE_ID): str,
        vol.Optional(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    api_client = TRMNLApiClient(
        session,
        data[CONF_API_TOKEN],
        data.get(CONF_BASE_URL, DEFAULT_BASE_URL),
    )

    # Test connection
    if not await api_client.test_connection():
        raise TRMNLAuthenticationError("Cannot connect to TRMNL API")

    # Test device access
    try:
        device_info = await api_client.get_device_info(data[CONF_DEVICE_ID])
        if not device_info:
            raise TRMNLApiError("Device not found or not accessible")
    except Exception as err:
        raise TRMNLApiError(f"Cannot access device: {err}")

    return {
        "title": f"TRMNL Device {data[CONF_DEVICE_ID]}",
        "device_info": device_info,
    }


class TRMNLConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TRMNL."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle the initial step."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except TRMNLAuthenticationError:
                errors["base"] = "invalid_auth"
            except TRMNLApiError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Create unique ID based on device ID
                await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_import(self, user_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle import."""
        return await self.async_step_user(user_input)