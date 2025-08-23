"""API client for TRMNL integration."""
import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import aiohttp

from .const import DEFAULT_BASE_URL, API_ENDPOINTS

_LOGGER = logging.getLogger(__name__)


class TRMNLApiClient:
    """TRMNL API client."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_token: str,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._api_token = api_token
        self._base_url = base_url.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

    async def _async_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an API request."""
        url = f"{self._base_url}{endpoint}"
        
        _LOGGER.debug(f"Making {method} request to {url}")
        
        try:
            async with self._session.request(
                method,
                url,
                headers=self._headers,
                json=data,
                params=params,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                response_text = await response.text()
                _LOGGER.debug(f"Response status: {response.status}")
                
                if response.status == 401:
                    raise TRMNLAuthenticationError("Invalid API token")
                elif response.status == 404:
                    raise TRMNLDeviceNotFoundError("Device not found")
                elif response.status >= 400:
                    raise TRMNLApiError(f"API error {response.status}: {response_text}")
                
                if not response_text:
                    return {}
                
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    _LOGGER.error(f"Invalid JSON response: {response_text}")
                    return {}
                    
        except asyncio.TimeoutError:
            raise TRMNLConnectionError("Request timeout")
        except aiohttp.ClientError as err:
            raise TRMNLConnectionError(f"Connection error: {err}")

    async def test_connection(self) -> bool:
        """Test the API connection."""
        try:
            await self._async_request("GET", "/api/user")
            return True
        except Exception as err:
            _LOGGER.error(f"Connection test failed: {err}")
            return False

    async def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """Get device information."""
        endpoint = API_ENDPOINTS["device_info"].format(device_id=device_id)
        response = await self._async_request("GET", endpoint)
        
        # Parse and standardize the response
        parsed_data = {
            "device_id": device_id,
            "battery": response.get("battery_voltage", 0),
            "wifi_signal": response.get("wifi_signal", 0),
            "firmware_version": response.get("firmware_version", "Unknown"),
            "last_seen": datetime.now().isoformat(),
            "device_status": "online" if response.get("online", False) else "offline",
            "mac_address": response.get("mac_address", ""),
            "uptime": response.get("uptime", 0),
        }
        
        return parsed_data

    async def refresh_display(self, device_id: str) -> bool:
        """Trigger a display refresh."""
        endpoint = API_ENDPOINTS["refresh"].format(device_id=device_id)
        try:
            await self._async_request("POST", endpoint)
            return True
        except Exception as err:
            _LOGGER.error(f"Failed to refresh display: {err}")
            return False

    async def get_display_content(self, device_id: str) -> Dict[str, Any]:
        """Get current display content."""
        endpoint = API_ENDPOINTS["display"]
        params = {"device_id": device_id}
        response = await self._async_request("GET", endpoint, params=params)
        
        return {
            "image_url": response.get("image_url", ""),
            "filename": response.get("filename", ""),
            "update_firmware": response.get("update_firmware", False),
            "next_refresh": response.get("next_refresh", 300),  # Default 5 minutes
        }

    async def update_plugin(self, device_id: str, plugin_id: str) -> bool:
        """Update the active plugin for a device."""
        data = {
            "device_id": device_id,
            "plugin_id": plugin_id,
        }
        
        try:
            await self._async_request("POST", "/api/device/plugin", data=data)
            return True
        except Exception as err:
            _LOGGER.error(f"Failed to update plugin: {err}")
            return False

    async def send_notification(self, device_id: str, message: str, duration: int = 60) -> bool:
        """Send a notification to the device."""
        data = {
            "device_id": device_id,
            "message": message,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
        }
        
        try:
            await self._async_request("POST", "/api/device/notification", data=data)
            return True
        except Exception as err:
            _LOGGER.error(f"Failed to send notification: {err}")
            return False

    async def get_available_plugins(self) -> list[Dict[str, Any]]:
        """Get list of available plugins."""
        try:
            response = await self._async_request("GET", API_ENDPOINTS["plugins"])
            return response.get("plugins", [])
        except Exception as err:
            _LOGGER.error(f"Failed to get plugins: {err}")
            return []


class TRMNLApiError(Exception):
    """Base TRMNL API exception."""


class TRMNLConnectionError(TRMNLApiError):
    """TRMNL connection exception."""


class TRMNLAuthenticationError(TRMNLApiError):
    """TRMNL authentication exception."""


class TRMNLDeviceNotFoundError(TRMNLApiError):
    """TRMNL device not found exception."""