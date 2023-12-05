"""The Recteq integration."""

import logging
import tinytuya
import async_timeout

from datetime import timedelta
from time import time
from threading import Lock

from .const import DOMAIN, CONF_NAME, DPS_ATTRS

from .const import (
    CONF_DEVICE_ID,
    CONF_FORCE_FAHRENHEIT,
    CONF_IP_ADDRESS,
    CONF_LOCAL_KEY,
    CONF_NAME,
    CONF_PROTOCOL,
    DOMAIN,
    DPS_POWER,
)
from homeassistant.helpers import update_coordinator

MAX_RETRIES = 3
CACHE_SECONDS = 20
UPDATE_INTERVAL = 30

_LOGGER = logging.getLogger(__name__)

class RecteqGrill:
    """Wrap tinytuya.OutletDevice to cache status lock around polls."""

    def __init__(self, device_id, ip_address, local_key, protocol):
        self._device_id  = device_id
        self._ip_address = ip_address
        self._local_key  = local_key
        self._protocol   = protocol
        self._device = tinytuya.OutletDevice(device_id, ip_address, local_key)
        self._device.set_version(float(protocol))
        self._cached_status = None
        self._cached_status_time = None
        self._lock = Lock()
        self.update()

    @property
    def available(self):
        return self._cached_status != None

    def _get_status(self):
        for i in range(MAX_RETRIES):
            try:
                status = self._device.status()
                return status
            except ConnectionError:
                if i+1 == MAX_RETRIES:
                    raise ConnectionError("Failed to update status.")


    def set_status(self, dps, value):
        self._cached_status = None
        self._cached_status_time = None
        return self._device.set_status(value, dps)

    def get_status(self):
        self._lock.acquire()
        try:
            now = time()
            if not self._cached_status or now - self._cached_status_time > 20:
                self._cached_status = self._get_status()
                self._cached_status_time = time()
            return self._cached_status
        finally:
            self._lock.release()


class RecteqCoordinator(update_coordinator.DataUpdateCoordinator):

    def __init__(self, hass, entry, grill: RecteqGrill):
        super().__init__(hass, _LOGGER,
            name = entry.data[CONF_NAME],
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        #self._name   = entry.data[CONF_NAME]
        self._entry  = entry
        self.grill_device = grill

    @property
    def available(self):
        return self.grill_device.available

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(5):
                return self.grill_device.status()
        except ConnectionError as err:
            raise update_coordinator.UpdateFailed("Error fetching data") from err