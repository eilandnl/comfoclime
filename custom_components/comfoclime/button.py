"""Button entities for write-only ComfoAir Q temperature profile commands."""

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN
from .comfoclime_api import ComfoClimeAPI

PROFILE_VALUES = {"warm": 2, "normal": 0, "cool": 1}
PROFILE_COMMANDS = (*PROFILE_VALUES, "automatic")


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create profile command buttons for each connected ComfoAir Q."""
    data = hass.data[DOMAIN][entry.entry_id]
    api: ComfoClimeAPI = data["api"]
    buttons = [
        ComfoAirQTemperatureProfileButton(api, device, profile, entry)
        for device in data["devices"]
        if device.get("modelTypeId") == 1 and device.get("uuid") not in (None, "NULL")
        for profile in PROFILE_COMMANDS
    ]
    async_add_entities(buttons)


class ComfoAirQTemperatureProfileButton(ButtonEntity):
    """Write a temporary temperature profile to a connected ComfoAir Q."""

    _attr_has_entity_name = True

    def __init__(
        self,
        api: ComfoClimeAPI,
        device: dict,
        profile: str,
        entry: ConfigEntry,
    ) -> None:
        self._api = api
        self._device = device
        self._profile = profile
        self._attr_config_entry_id = entry.entry_id
        self._attr_unique_id = (
            f"{entry.entry_id}_{device['uuid']}_temperature_profile_{profile}"
        )
        self._attr_translation_key = f"temperature_profile_{profile}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._device["uuid"])},
            name=self._device.get("displayName", "ComfoAir Q"),
            manufacturer="Zehnder",
            model=self._device.get("@modelType", "ComfoAir Q"),
            sw_version=self._device.get("version"),
        )

    async def async_press(self) -> None:
        """Apply the selected profile, or return to the unit schedule."""
        if self._profile == "automatic":
            method = 0x85  # DISABLETIMERENTRY
            data = [0x01]  # TIMER_DEFAULT
        else:
            method = 0x84  # ENABLETIMERENTRY
            value = PROFILE_VALUES[self._profile]
            data = [
                0x01,  # TIMER_DEFAULT
                0x00,
                0x00,
                0x00,
                0xFF,
                0xFF,
                0xFF,
                0xFF,  # duration=-1: keep active until cancelled
                value,
            ]

        try:
            await self._api.async_call_device_method(
                self.hass,
                device_uuid=self._device["uuid"],
                unit=0x15,  # SCHEDULE
                subunit=0x03,  # TEMPERATURE_PROFILE
                method=method,
                data=data,
            )
        except Exception as err:
            raise HomeAssistantError(
                f"Failed to set the ComfoAir Q temperature profile to {self._profile}"
            ) from err
