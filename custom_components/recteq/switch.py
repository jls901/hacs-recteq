"""Recteq Switch Component."""
import logging

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchDeviceClass
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity
)

from homeassistant.const import (
    CONF_NAME,
    CONF_HOST,
)

import homeassistant.helpers.config_validation as cv
from homeassistant.core import callback

from custom_components.recteq.device import RecteqCoordinator, RecteqGrill

from .const import (
    __version__,
    CONF_DEVICE_ID,
    CONF_LOCAL_KEY,
    CONF_PROTOCOL,
    DOMAIN,
    DPS_ACTUAL,
    DPS_POWER,
    DPS_TARGET,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config, add, discovery_info=None):
    entity = RecteqPowerSwitchEntity(
            hass.data[DOMAIN][config.entry_id],
            config.data.get(CONF_NAME, DOMAIN + '_' + config.data.get(CONF_LOCAL_KEY))
        )
    add([entity])

class RecteqPowerSwitchEntity(CoordinatorEntity, SwitchEntity):
    """The Recteq switch to turn the unit on and off."""

    def __init__(self, coordinator, name):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._device = coordinator.grill_device
        self._name = f"{self._device.name} Power"
        self._grill_data = self._coordinator.data
        self._state = self._grill_data['dps'][DPS_POWER] if self._grill_data else None
        self._device_class = SwitchDeviceClass.OUTLET

    @property
    def device_class(self):
         return self._device_class

    @property
    def unique_id(self):
         return f"{self._device.unique_id}.power"

    @property
    def device_info(self) -> {}:
        """Return the device info."""
        return {
            "identifiers": {
                (DOMAIN, self._device.unique_id)
            },
            "name": self.name,
        }

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._state

    async def async_turn_on(self, **kwargs):
        _LOGGER.debug("Switching %s ON", self._name)
        self._device.set_status(True, DPS_POWER)
        self._coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        _LOGGER.debug("Switching %s OFF", self._name)
        self._device.set_status(False, DPS_POWER)
        self._coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self):
        self._grill_data = self._coordinator.data
        self._state = self._grill_data['dps'][DPS_POWER]
        self.async_write_ha_state()