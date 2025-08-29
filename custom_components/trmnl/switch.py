"""Support for TRMNL switches."""
import logging
from typing import Any, Dict, Optional

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import TRMNLDataUpdateCoordinator
from .const import (
    DOMAIN,
    SWITCH_TYPES,
    MANUFACTURER,
    MODEL,
    CONF_DEVICE_ID,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up TRMNL switches from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    device_id = config_entry.data[CONF_DEVICE_ID]

    switches = []
    for switch_type in SWITCH_TYPES:
        switches.append(TRMNLSwitch(coordinator, device_id, switch_type))

    async_add_entities(switches)


class TRMNLSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a TRMNL switch."""

    def __init__(
        self,
        coordinator: TRMNLDataUpdateCoordinator,
        device_id: str,
        switch_type: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._switch_type = switch_type
        self._attr_name = f"TRMNL {SWITCH_TYPES[switch_type]['name']}"
        self._attr_unique_id = f"{device_id}_{switch_type}"
        self._attr_icon = SWITCH_TYPES[switch_type].get("icon")
        self._is_on = False

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": f"TRMNL {self._device_id}",
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "sw_version": self.coordinator.data.get("firmware_version", "Unknown") if self.coordinator.data else "Unknown",
        }

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        if not self.coordinator.data:
            return self._is_on

        data = self.coordinator.data

        if self._switch_type == "auto_refresh":
            # Check if auto refresh is enabled based on device status
            return data.get("auto_refresh", True)

        return self._is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        _LOGGER.debug(f"Turning on {self._switch_type} for device {self._device_id}")
        
        if self._switch_type == "auto_refresh":
            # Enable auto refresh on the device
            success = await self._enable_auto_refresh()
            if success:
                self._is_on = True
                self.async_write_ha_state()
                await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        _LOGGER.debug(f"Turning off {self._switch_type} for device {self._device_id}")
        
        if self._switch_type == "auto_refresh":
            # Disable auto refresh on the device
            success = await self._disable_auto_refresh()
            if success:
                self._is_on = False
                self.async_write_ha_state()
                await self.coordinator.async_request_refresh()

    async def _enable_auto_refresh(self) -> bool:
        """Enable auto refresh on the device."""
        try:
            # This would be a custom API call to enable auto refresh
            # For now, we'll simulate success
            _LOGGER.info(f"Auto refresh enabled for device {self._device_id}")
            return True
        except Exception as err:
            _LOGGER.error(f"Failed to enable auto refresh: {err}")
            return False

    async def _disable_auto_refresh(self) -> bool:
        """Disable auto refresh on the device."""
        try:
            # This would be a custom API call to disable auto refresh
            # For now, we'll simulate success
            _LOGGER.info(f"Auto refresh disabled for device {self._device_id}")
            return True
        except Exception as err:
            _LOGGER.error(f"Failed to disable auto refresh: {err}")
            return False

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success