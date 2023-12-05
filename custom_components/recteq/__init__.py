"""The Recteq integration."""

import logging
import async_timeout
import asyncio

from .const import (
    DOMAIN,
    PROJECT,
    VERSION,
    ISSUE_LINK,
    PLATFORMS,
    CONF_DEVICE_ID,
    CONF_IP_ADDRESS,
    CONF_LOCAL_KEY,
    CONF_PROTOCOL
)

from .device import RecteqCoordinator, RecteqGrill

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from integrationhelper.const import CC_STARTUP_VERSION

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config):
    hass.data[DOMAIN] = {}

    _LOGGER.info(CC_STARTUP_VERSION.format(
        name=PROJECT,
        version=VERSION,
        issue_link=ISSUE_LINK
    ))

    return True

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    try:
        async with async_timeout.timeout(10):
            device = RecteqGrill(
                config_entry.data[CONF_DEVICE_ID],
                config_entry.data[CONF_HOST],
                config_entry.data[CONF_LOCAL_KEY],
                config_entry.data[CONF_PROTOCOL]
            )
    except ConnectionError as err:
        raise ConfigEntryNotReady from err

    recteq_coordinator = hass.data[DOMAIN][config_entry.entry_id] = RecteqCoordinator(
        hass, config_entry, device
    )
    #most likely need this
    #await recteq_coordinator.async_config_entry_first_refresh()

    for PLATFORM in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, PLATFORM)
        )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, PLATFORM)
                for PLATFORM in PLATFORMS
            ]
        )
    )
    if unload_ok:
        await hass.data[DOMAIN].pop(entry.entry_id).shutdown()

    return unload_ok

