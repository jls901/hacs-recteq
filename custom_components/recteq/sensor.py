"""The Recteq sensor component."""

import logging

from .const import (
    DOMAIN,
    DPS_POWER,
    DPS_TARGET,
    DPS_ACTUAL,
    DPS_PROBEA,
    DPS_PROBEB,
    NAME_TARGET,
    NAME_ACTUAL,
    NAME_PROBEA,
    NAME_PROBEB
)

from homeassistant.core import callback
from homeassistant.components import sensor
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, add):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    add(
        [
            RecteqTemperatureSensor(coordinator, DPS_TARGET, NAME_TARGET),
            RecteqTemperatureSensor(coordinator, DPS_ACTUAL, NAME_ACTUAL),
            RecteqTemperatureSensor(coordinator, DPS_PROBEA, NAME_PROBEA),
            RecteqTemperatureSensor(coordinator, DPS_PROBEB, NAME_PROBEB)
        ]
    )

class RecteqTemperatureSensor(CoordinatorEntity, sensor.SensorEntity):

    def __init__(self, coordinator, dps, sensor_name):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._device = coordinator.grill_device
        self._device_class = sensor.DEVICE_CLASS_TEMPERATURE
        self._grill_data = self.coordinator.data
        self._state = self._grill_data['dps'][DPS_POWER] if self._grill_data else None
        self._name = f"{self._device.name} {sensor_name}"
        self._dps_attr = dps

    @property
    def name(self):
        return self._name

    @property
    def device_class(self):
         return self._device_class

    @property
    def unique_id(self):
         return f"{self._device.unique_id}.{self._dps_attr}"

    @property
    def device_info(self) -> {}:
        """Return the device info."""
        return {
            "identifiers": {
                (DOMAIN, self._device.unique_id)
            },
            "name": self.name,
        }

    @callback
    def _handle_coordinator_update(self):
        self._grill_data = self.coordinator.data
        self._state = self._grill_data['dps'][self._dps_attr]
        self.async_write_ha_state()

