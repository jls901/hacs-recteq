"""Recteq Switch Component."""
import logging

from datetime import timedelta

import tinytuya

import voluptuous as vol

from homeassistant.components.switch import (
    SwitchEntity,
    PLATFORM_SCHEMA
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity
)

from homeassistant.const import (
    CONF_NAME,
    CONF_HOST,
    ATTR_ENTITY_ID,
    ATTR_TEMPERATURE
)

import homeassistant.helpers.config_validation as cv

from time import time
from threading import Lock

from .const import (
    __version__,

    ATTR_ACTUAL,
    ATTR_ERROR1,
    ATTR_ERROR2,
    ATTR_ERROR3,
    ATTR_POWER,
    ATTR_PROBEA,
    ATTR_PROBEB,
    ATTR_TARGET,

    CONF_DEVICE_ID,
    CONF_LOCAL_KEY,
    CONF_PROTOCOL,

    DOMAIN,

    DPS_ACTUAL,
    DPS_ERROR1,
    DPS_ERROR2,
    DPS_ERROR3,
    DPS_POWER,
    DPS_PROBEA,
    DPS_PROBEB,
    DPS_TARGET,
)

MAX_RETRIES = 2 # after the first failure

DPS_ATTRS = {
    DPS_POWER:  ATTR_POWER,
    DPS_TARGET: ATTR_TARGET,
    DPS_ACTUAL: ATTR_ACTUAL,
    DPS_PROBEA: ATTR_PROBEA,
    DPS_PROBEB: ATTR_PROBEB,
    DPS_ERROR1: ATTR_ERROR1,
    DPS_ERROR2: ATTR_ERROR2,
    DPS_ERROR3: ATTR_ERROR3,
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME): cv.string,
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_DEVICE_ID): cv.string,
    vol.Required(CONF_LOCAL_KEY): cv.string,
    vol.Optional(CONF_PROTOCOL, default='3.3'): cv.string,
})

SERVICE_TARGET_SET_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.string,
    vol.Required(ATTR_TEMPERATURE): cv.positive_int
})

SERVICE_TARGET_SET = "set_target"

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config, add, discovery_info=None):

    data = hass.data.setdefault(DOMAIN, {})
    devices = data.setdefault('devices', [])

    def handle_set_target_service(service):
        for device in devices:
            if device.entity_id == service.data[ATTR_ENTITY_ID]:
                device.set_target(service.data[ATTR_TEMPERATURE])

    # if not hass.services.has_service(DOMAIN, SERVICE_TARGET_SET):
    #     hass.services.register(
    #         DOMAIN,
    #         SERVICE_TARGET_SET,
    #         handle_set_target_service,
    #         schema=SERVICE_TARGET_SET_SCHEMA
    #     )

    device = RecteqEntity(
            CachedOutletDevice(
                config.data.get(CONF_DEVICE_ID),
                config.data.get(CONF_HOST),
                config.data.get(CONF_LOCAL_KEY),
                config.data.get(CONF_PROTOCOL)
            ),
            config.data.get(CONF_NAME, DOMAIN + '_' + config.data.get(CONF_LOCAL_KEY))
        )

    devices.append(device)

    add([device])

class CachedOutletDevice:
    """Wrapper for a Tuya OutletDevice that caches the status."""

    def __init__(self, device_id, host, local_key, protocol):
        self._device_id = device_id
        self.unique_id = self._device_id
        self._device = tinytuya.OutletDevice(device_id, host, local_key)
        self._device.set_version(float(protocol))

        self._cached_status = ''
        self._cached_status_time = 0

        self._lock = Lock()

    def __get_status(self):
        for i in range(MAX_RETRIES):
            try:
                status = self._device.status()
                return status
            except ConnectionError:
                if i+1 == MAX_RETRIES:
                    raise ConnectionError("Failed to update status.")

    def set_status(self, state, switchid):
        self._cached_status = ''
        self._cached_status_time = 0
        return self._device.set_status(state, switchid)

    def status(self):
        self._lock.acquire()
        try:
            now = time()
            if not self._cached_status or now - self._cached_status_time > 20:
                self._cached_status = self.__get_status()
                self._cached_status_time = time()
            return self._cached_status
        finally:
            self._lock.release()

class RecteqEntity(CoordinatorEntity, SwitchEntity):
    """The Recteq switch to turn the unit on and off and read attributes."""

    def __init__(self, device, name):
        self._device = device
        self._name = name
        self._state = None
        self._status = self._device.status()

    @property
    def unique_id(self):
         return self._device.unique_id + "-switch"

    @property
    def device_info(self) -> {}:
        """Return the device info."""
        return {
            "identifiers": {
                (DOMAIN, self._device.unique_id)
            },
            "name": self.name,
            "manufacturer": "Recteq",
            "model": "Deck Boss 590",
            "sw_version": "0.0.0.0",
        }

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._state

    @property
    def device_state_attributes(self):
        attrs = {}
        try:
            for dps, attr in DPS_ATTRS.items():
                attrs[attr] = "{}".format(self._status['dps'][dps])
        except KeyError:
            pass
        return attrs

    def turn_on(self, **kwargs):
        _LOGGER.debug("Switching %s ON", self._name)
        self._device.set_status(True, DPS_POWER)
        self.schedule_update_ha_state(force_refresh=True)

    def turn_off(self, **kwargs):
        _LOGGER.debug("Switching %s OFF", self._name)
        self._device.set_status(False, DPS_POWER)
        self.schedule_update_ha_state(force_refresh=True)

    def update(self):
        _LOGGER.debug("Polling status of %s", self._name)
        self._status= self._device.status()
        self._state = self._status['dps'][DPS_POWER]
        _LOGGER.debug(
            "%s is %s, target %s, actual %s",
            self._name,
            ('OFF', 'ON')[self._state],
            self._status['dps'][DPS_TARGET],
            self._status['dps'][DPS_ACTUAL]
        )

    def set_target(self, temperature):
        _LOGGER.debug("Setting target of %s to %d", self._name, temperature)
        self._device.set_status(temperature, DPS_TARGET)
        self.schedule_update_ha_state(force_refresh=True)