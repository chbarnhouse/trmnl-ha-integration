"""TRMNL services for Home Assistant with external screenshot service."""
import logging
from typing import Dict, Any, Optional
import voluptuous as vol
from datetime import datetime
import aiohttp
import base64

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.exceptions import ServiceValidationError

from .const import DOMAIN
from .api import TRMNLApi

_LOGGER = logging.getLogger(__name__)

# Service schemas
DASHBOARD_CAPTURE_SCHEMA = vol.Schema({
    vol.Required("device_friendly_id"): cv.string,
    vol.Required("dashboard_path"): cv.string,
    vol.Optional("screenshot_service_url", default="http://localhost:3001"): cv.string,
    vol.Optional("theme"): cv.string,
    vol.Optional("width", default=800): vol.Coerce(int),
    vol.Optional("height", default=480): vol.Coerce(int),
    vol.Optional("wait_time", default=2000): vol.Coerce(int),
    vol.Optional("orientation", default="landscape"): vol.In(["landscape", "portrait"]),
    vol.Optional("center_x_offset", default=0): vol.Coerce(int),
    vol.Optional("center_y_offset", default=0): vol.Coerce(int),
    vol.Optional("margin_top", default=0): vol.Coerce(int),
    vol.Optional("margin_bottom", default=0): vol.Coerce(int),
    vol.Optional("margin_left", default=0): vol.Coerce(int),
    vol.Optional("margin_right", default=0): vol.Coerce(int),
    vol.Optional("rotation_angle", default=0.0): vol.Coerce(float),
})


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up TRMNL services."""
    
    async def handle_send_dashboard_to_device(call: ServiceCall) -> None:
        """Handle the send_dashboard_to_device service call."""
        device_friendly_id = call.data["device_friendly_id"]
        dashboard_path = call.data["dashboard_path"]
        screenshot_service_url = call.data["screenshot_service_url"]
        theme = call.data.get("theme")
        width = call.data["width"]
        height = call.data["height"]
        wait_time = call.data["wait_time"]
        orientation = call.data["orientation"]
        center_x_offset = call.data["center_x_offset"]
        center_y_offset = call.data["center_y_offset"]
        margin_top = call.data["margin_top"]
        margin_bottom = call.data["margin_bottom"]
        margin_left = call.data["margin_left"]
        margin_right = call.data["margin_right"]
        rotation_angle = call.data["rotation_angle"]
        
        try:
            # Get the TRMNL API instance
            api: TRMNLApi = hass.data[DOMAIN]["api"]
            
            # Get Home Assistant base URL
            ha_base_url = hass.config.external_url or hass.config.internal_url
            if not ha_base_url:
                ha_base_url = f"http://localhost:8123"
            
            # Construct full dashboard URL
            dashboard_url = f"{ha_base_url}{dashboard_path}"
            
            _LOGGER.info("Capturing dashboard %s via external screenshot service", dashboard_url)
            
            # Call external screenshot service
            screenshot_payload = {
                "url": dashboard_url,
                "width": width,
                "height": height,
                "theme": theme,
                "waitTime": wait_time,
                "orientation": orientation,
                "centerX": center_x_offset,
                "centerY": center_y_offset,
                "marginTop": margin_top,
                "marginBottom": margin_bottom,
                "marginLeft": margin_left,
                "marginRight": margin_right,
                "rotation": rotation_angle
            }
            
            async with aiohttp.ClientSession() as session:
                screenshot_endpoint = f"{screenshot_service_url.rstrip('/')}/screenshot"
                _LOGGER.info("Calling screenshot service: %s", screenshot_endpoint)
                
                try:
                    async with session.post(
                        screenshot_endpoint, 
                        json=screenshot_payload,
                        timeout=aiohttp.ClientTimeout(total=60)
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            if result.get('success'):
                                image_data = result['image']
                                _LOGGER.info("Screenshot captured successfully: %d characters", len(image_data))
                            else:
                                raise ServiceValidationError(f"Screenshot service failed: {result.get('message', 'Unknown error')}")
                        else:
                            error_text = await response.text()
                            raise ServiceValidationError(f"Screenshot service returned {response.status}: {error_text}")
                            
                except aiohttp.ClientError as e:
                    _LOGGER.error("Failed to connect to screenshot service at %s: %s", screenshot_endpoint, e)
                    raise ServiceValidationError(f"Cannot connect to screenshot service at {screenshot_service_url}. Please ensure the service is running.")
            
            # Create screen in TRMNL
            safe_path = dashboard_path.replace("/", "_").replace("\\", "_")
            timestamp = int(datetime.now().timestamp())
            unique_name = f"Dashboard_{safe_path}_{timestamp}"
            
            _LOGGER.info("Creating TRMNL screen with external screenshot data")
            
            # Try simple format first
            simple_screen_data = {
                "name": unique_name,
                "label": f"HA Dashboard {dashboard_path}",
                "image": {
                    "data": image_data
                }
            }
            
            screen_result = await api.create_screen(simple_screen_data)
            
            if not screen_result:
                _LOGGER.warning("Simple format failed, trying with model_id")
                # Try with model_id as we know this was required
                enhanced_screen_data = {
                    "model_id": 1,
                    "name": unique_name,
                    "label": f"HA Dashboard {dashboard_path}",
                    "image": {
                        "model_id": 1,
                        "name": unique_name,
                        "label": f"HA Dashboard {dashboard_path}",
                        "data": image_data
                    }
                }
                
                screen_result = await api.create_screen(enhanced_screen_data)
                
            if not screen_result:
                raise ServiceValidationError(f"Failed to create screen for dashboard {dashboard_path}")
            
            screen_id = screen_result.get('id')
            _LOGGER.info("Successfully created screen %s with external screenshot", screen_id)
            
            # Try to assign screen to device
            assignment_methods = [
                {"current_screen_id": screen_id},
                {"screen_id": screen_id}, 
                {"active_screen": screen_id},
                {"display_screen_id": screen_id},
                {"label": f"HA Dashboard {dashboard_path}", "active_screen_id": screen_id}
            ]
            
            assignment_success = False
            for i, assignment_data in enumerate(assignment_methods):
                try:
                    _LOGGER.info("Trying screen assignment method %d", i + 1)
                    result = await api.update_device(device_friendly_id, assignment_data)
                    if result:
                        _LOGGER.info("Screen assignment method %d succeeded!", i + 1)
                        assignment_success = True
                        break
                except Exception as assign_error:
                    _LOGGER.warning("Screen assignment method %d failed: %s", i + 1, assign_error)
                    continue
            
            if assignment_success:
                _LOGGER.info("Successfully assigned screen %s to device %s", screen_id, device_friendly_id)
                _LOGGER.info("Dashboard should now appear on TRMNL device!")
            else:
                _LOGGER.warning("Could not assign screen to device automatically")
                _LOGGER.info("Screen %s created successfully and available in TRMNL web interface", screen_id)
                _LOGGER.info("You can manually assign it to device %s", device_friendly_id)
            
            _LOGGER.info("Dashboard capture completed - screen %s created", screen_id)
            
        except ServiceValidationError:
            raise
        except Exception as e:
            _LOGGER.error("Error in send_dashboard_to_device service: %s", e, exc_info=True)
            raise ServiceValidationError(f"Failed to send dashboard to device: {e}")
    
    # Register services
    hass.services.async_register(
        DOMAIN,
        "send_dashboard_to_device", 
        handle_send_dashboard_to_device,
        schema=DASHBOARD_CAPTURE_SCHEMA
    )
    
    _LOGGER.info("TRMNL dashboard capture service registered (external screenshot version)")