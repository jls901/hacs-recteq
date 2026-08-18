"""The Recteq integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_HOST
from homeassistant.exceptions import ConfigEntryNotReady

from .api import RecteqGrill
from .const import (
    CONF_DEVICE_ID,
    CONF_LOCAL_KEY,
    CONF_PROTOCOL,
    PLATFORMS,
)
from .coordinator import RecteqCoordinator
from .data import RecteqData

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Recteq from a config entry."""
    try:
        grill = RecteqGrill(
            entry.data[CONF_DEVICE_ID],
            entry.data[CONF_HOST],
            entry.data[CONF_LOCAL_KEY],
            entry.data[CONF_PROTOCOL],
        )
    except ConnectionError as err:
        raise ConfigEntryNotReady from err

    coordinator = RecteqCoordinator(hass, entry, grill)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = RecteqData(grill=grill, coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False

    entry.runtime_data.coordinator.shutdown()
    return True
