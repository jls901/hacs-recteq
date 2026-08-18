"""The Recteq sensor component."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import UnitOfTemperature

from .const import (
    DPS_ACTUAL,
    DPS_PROBEA,
    DPS_PROBEB,
    DPS_TARGET,
    NAME_ACTUAL,
    NAME_PROBEA,
    NAME_PROBEB,
    NAME_TARGET,
)
from .entity import RecteqEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import RecteqCoordinator

SENSORS = [
    (DPS_TARGET, NAME_TARGET),
    (DPS_ACTUAL, NAME_ACTUAL),
    (DPS_PROBEA, NAME_PROBEA),
    (DPS_PROBEB, NAME_PROBEB),
]


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        RecteqTemperatureSensor(entry, coordinator, dps, name) for dps, name in SENSORS
    )


class RecteqTemperatureSensor(RecteqEntity, SensorEntity):
    """Temperature sensor for a Recteq grill DPS."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT

    def __init__(
        self,
        entry: ConfigEntry,
        coordinator: RecteqCoordinator,
        dps: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(entry, coordinator, f"{coordinator.grill.unique_id}.{dps}")
        self._attr_name = name
        self._dps = dps

    @property
    def native_value(self) -> int | float | None:
        """Return the sensor value."""
        data = self.coordinator.data
        if not data:
            return None
        return data.get("dps", {}).get(self._dps)
