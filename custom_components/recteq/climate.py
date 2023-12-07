"""The Recteq climate component."""

import logging

from .const import (
    CONF_LOCAL_KEY,
    CONF_NAME,
    DOMAIN,
    DPS_ACTUAL,
    DPS_POWER,
    DPS_TARGET,
)

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.components import climate
from homeassistant.components.climate.const import (
    ATTR_HVAC_MODE,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_WHOLE, UnitOfTemperature
from homeassistant.util.unit_system import IMPERIAL_SYSTEM

_LOGGER = logging.getLogger(__name__)

ICON = "mdi:grill"

TEMP_MIN = 200
TEMP_MAX = 700


async def async_setup_entry(hass, entry, add):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    add(
        [
            RecteqClimate(
                coordinator,
                hass,
                entry.data.get(
                    CONF_NAME, DOMAIN + "_" + entry.data.get(CONF_LOCAL_KEY)
                ),
            )
        ]
    )


class RecteqClimate(CoordinatorEntity, climate.ClimateEntity):
    def __init__(self, coordinator, hass, name):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._device = coordinator.grill_device
        self._name = f"{self._device.name} Climate"
        self._units = hass.config.units
        self._hass = hass
        self._grill_data = self._coordinator.data
        self._attr_available = bool(self._grill_data) or False

    @property
    def unique_id(self):
        return f"{self._device.unique_id}.climate"

    @property
    def device_info(self) -> {}:
        return {
            "identifiers": {(DOMAIN, self._device.unique_id)},
            "name": self._device.name,
        }

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return ICON

    @property
    def precision(self):
        return PRECISION_WHOLE

    @property
    def temperature_unit(self):
        return self._units.temperature_unit

    @property
    def hvac_mode(self):
        if self.is_on:
            return HVAC_MODE_HEAT

        return HVAC_MODE_OFF

    @property
    def hvac_modes(self):
        return [HVAC_MODE_OFF, HVAC_MODE_HEAT]

    @property
    def current_temperature(self):
        if self._grill_data and "dps" in self._grill_data and self.is_on:
            temp = self._grill_data["dps"][DPS_ACTUAL]
            return round(float(self._units.temperature(temp, self.temperature_unit)), 1)

    @property
    def target_temperature(self):
        if self._grill_data and "dps" in self._grill_data:
            temp = self._grill_data["dps"][DPS_TARGET]
            return round(float(self._units.temperature(temp, self.temperature_unit)), 1)

    @property
    def target_temperature_step(self):
        if self.temperature_unit == UnitOfTemperature.FAHRENHEIT:
            return 5.0
        return 2.5

    @property
    def target_temperature_high(self):
        return self.max_temp

    @property
    def target_temperature_low(self):
        return self.min_temp

    @property
    def is_on(self):
        if self._grill_data:
            return self._grill_data.get("dps", {}).get(DPS_POWER) == True

    @property
    def is_off(self):
        if self._grill_data:
            return self._grill_data.get("dps", {}).get(DPS_POWER) == False

    @property
    def supported_features(self):
        return SUPPORT_TARGET_TEMPERATURE

    @property
    def min_temp(self):
        return round(float(self._units.temperature(TEMP_MIN, self.temperature_unit)), 1)

    @property
    def max_temp(self):
        return round(float(self._units.temperature(TEMP_MAX, self.temperature_unit)), 1)

    async def async_set_temperature(self, **kwargs):
        mode = kwargs.get(ATTR_HVAC_MODE)
        if mode is not None:
            await self.async_set_hvac_mode(mode)

        temp = kwargs.get(ATTR_TEMPERATURE)
        if self._units.temperature_unit != UnitOfTemperature.FAHRENHEIT:
            temp = IMPERIAL_SYSTEM.temperature(
                temp, self._device.units.temperature_unit
            )
        self._device.set_status(DPS_TARGET, int(temp + 0.5))
        await self._coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode):
        if hvac_mode == HVAC_MODE_HEAT:
            await self.async_turn_on()
        elif hvac_mode == HVAC_MODE_OFF:
            await self.async_turn_off()
        else:
            raise Exception(f'Invalid hvac_mode; "{hvac_mode}"')
        await self._coordinator.async_request_refresh()

    async def async_turn_on(self):
        self._device.set_status(DPS_POWER, True)
        await self._coordinator.async_request_refresh()

    async def async_turn_off(self):
        self._device.set_status(DPS_POWER, False)
        await self._coordinator.async_request_refresh()

    def _handle_coordinator_update(self):
        if self._coordinator.data:
            self._grill_data = self._coordinator.data
            self._attr_available = bool(self._grill_data) or False
            self.async_write_ha_state()
