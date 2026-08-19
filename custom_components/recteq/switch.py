"""The Recteq switch component."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity

from .const import DPS_POWER, LOGGER, NAME_POWER
from .entity import RecteqEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import RecteqCoordinator


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities([RecteqPowerSwitch(entry, coordinator)])


class RecteqPowerSwitch(RecteqEntity, SwitchEntity):
    """Switch to turn the Recteq grill on and off."""

    _attr_device_class = SwitchDeviceClass.OUTLET
    _attr_name = NAME_POWER

    def __init__(
        self,
        entry: ConfigEntry,
        coordinator: RecteqCoordinator,
    ) -> None:
        """Initialize the switch."""
        super().__init__(entry, coordinator, f"{coordinator.grill.unique_id}.power")

    @property
    def is_on(self) -> bool:
        """Return True if the grill is powered on."""
        data = self.coordinator.data
        if not data:
            return False
        return bool(data.get("dps", {}).get(DPS_POWER))

    async def async_turn_on(self) -> None:
        """Turn the grill on."""
        LOGGER.debug("Switching %s ON", self.config_entry.title)
        await self.hass.async_add_executor_job(
            partial(self.coordinator.grill.set_status, DPS_POWER, value=True)
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn the grill off."""
        LOGGER.debug("Switching %s OFF", self.config_entry.title)
        await self.hass.async_add_executor_job(
            partial(self.coordinator.grill.set_status, DPS_POWER, value=False)
        )
        await self.coordinator.async_request_refresh()
