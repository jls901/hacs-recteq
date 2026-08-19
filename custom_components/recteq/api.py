"""Tinytuya wrapper for the Recteq integration."""

from __future__ import annotations

from threading import Lock
from time import time

import tinytuya

MAX_RETRIES = 3
CACHE_SECONDS = 20
ERR_STATUS_FETCH = "Failed to update status."


class RecteqGrill:
    """Wrap tinytuya.OutletDevice with a lock and cached status polls."""

    def __init__(
        self, device_id: str, ip_address: str, local_key: str, protocol: str
    ) -> None:
        """Initialize the grill."""
        self._device_id = device_id
        self._ip_address = ip_address
        self._local_key = local_key
        self._protocol = protocol
        self._device = tinytuya.OutletDevice(device_id, ip_address, local_key)
        self._device.set_version(float(protocol))
        self._cached_status: dict | None = None
        self._cached_status_time: float | None = None
        self._lock = Lock()

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the grill."""
        return self._device_id

    def _get_status(self) -> dict:
        """Fetch the status, retrying up to MAX_RETRIES times."""
        last_error: ConnectionError | None = None
        for _ in range(MAX_RETRIES):
            try:
                return self._device.status()
            except ConnectionError as err:
                last_error = err
        raise ConnectionError(ERR_STATUS_FETCH) from last_error

    def get_status(self) -> dict:
        """Return the cached status, refreshing it if stale."""
        with self._lock:
            now = time()
            if (
                self._cached_status is None
                or self._cached_status_time is None
                or now - self._cached_status_time > CACHE_SECONDS
            ):
                self._cached_status = self._get_status()
                self._cached_status_time = now
            return self._cached_status

    def set_status(self, dps: str, *, value: int | bool) -> None:
        """Set a DPS value and invalidate the cached status."""
        with self._lock:
            self._cached_status = None
            self._cached_status_time = None
            self._device.set_value(dps, value)

    def shutdown(self) -> None:
        """Close the underlying device."""
        self._device.close()
