"""Coordinator for the Recteq integration."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import LOGGER

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .api import RecteqGrill

UPDATE_INTERVAL = timedelta(seconds=30)
UPDATE_TIMEOUT = 5
ERR_DATA_FETCH = "Error fetching data"


class RecteqCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator that polls the Recteq grill."""

    config_entry: ConfigEntry

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, grill: RecteqGrill
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=entry.title,
            config_entry=entry,
            update_interval=UPDATE_INTERVAL,
        )
        self.grill = grill

    async def _async_update_data(self) -> dict:
        """Fetch the latest status from the grill."""
        try:
            async with asyncio.timeout(UPDATE_TIMEOUT):
                return await self.hass.async_add_executor_job(self.grill.get_status)
        except ConnectionError as err:
            raise UpdateFailed(ERR_DATA_FETCH) from err

    def shutdown(self) -> None:
        """Shut down the grill device."""
        self.grill.shutdown()
