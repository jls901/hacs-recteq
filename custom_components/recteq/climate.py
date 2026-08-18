"""The Recteq climate component."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.climate import (
    ATTR_HVAC_MODE,
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_WHOLE, UnitOfTemperature
from homeassistant.util.unit_system import IMPERIAL_SYSTEM

from .const import DPS_ACTUAL, DPS_POWER, DPS_TARGET
from .entity import RecteqEntity

if TYPE_CHECKING:
    from typing import Any, ClassVar

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import RecteqCoordinator

TEMP_MIN = 200
TEMP_MAX = 700


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the climate platform."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities([RecteqClimate(hass, entry, coordinator)])


class RecteqClimate(RecteqEntity, ClimateEntity):
    """Recteq grill climate entity."""

    _attr_hvac_modes: ClassVar[list[HVACMode]] = [HVACMode.OFF, HVACMode.HEAT]
    _attr_icon = "mdi:grill"
    _attr_precision = PRECISION_WHOLE
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        coordinator: RecteqCoordinator,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(entry, coordinator, f"{coordinator.grill.unique_id}.climate")
        self._units = hass.config.units

    @property
    def _dps(self) -> dict | None:
        data = self.coordinator.data
        if not data:
            return None
        return data.get("dps")

    @property
    def temperature_unit(self) -> str:
        """Return the temperature unit."""
        return self._units.temperature_unit

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current HVAC mode."""
        dps = self._dps
        if dps is not None and dps.get(DPS_POWER) is True:
            return HVACMode.HEAT
        return HVACMode.OFF

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        if self.hvac_mode == HVACMode.OFF:
            return None
        dps = self._dps
        if dps is None:
            return None
        temp = dps.get(DPS_ACTUAL)
        if temp is None:
            return None
        return round(float(self._units.temperature(temp, self.temperature_unit)), 1)

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        dps = self._dps
        if dps is None:
            return None
        temp = dps.get(DPS_TARGET)
        if temp is None:
            return None
        return round(float(self._units.temperature(temp, self.temperature_unit)), 1)

    @property
    def target_temperature_step(self) -> float:
        """Return the target temperature step."""
        if self.temperature_unit == UnitOfTemperature.FAHRENHEIT:
            return 5.0
        return 2.5

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return round(float(self._units.temperature(TEMP_MIN, self.temperature_unit)), 1)

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return round(float(self._units.temperature(TEMP_MAX, self.temperature_unit)), 1)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set the target temperature."""
        if (mode := kwargs.get(ATTR_HVAC_MODE)) is not None:
            await self.async_set_hvac_mode(mode)

        temp = kwargs.get(ATTR_TEMPERATURE)
        if self.temperature_unit != UnitOfTemperature.FAHRENHEIT:
            temp = IMPERIAL_SYSTEM.temperature(temp, self.temperature_unit)
        self.coordinator.grill.set_status(DPS_TARGET, value=int(temp + 0.5))
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set the HVAC mode."""
        if hvac_mode == HVACMode.HEAT:
            self.coordinator.grill.set_status(DPS_POWER, value=True)
        elif hvac_mode == HVACMode.OFF:
            self.coordinator.grill.set_status(DPS_POWER, value=False)
        else:
            err = f'Invalid hvac_mode; "{hvac_mode}"'
            raise ValueError(err)
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        """Turn the grill on."""
        await self.async_set_hvac_mode(HVACMode.HEAT)

    async def async_turn_off(self) -> None:
        """Turn the grill off."""
        await self.async_set_hvac_mode(HVACMode.OFF)
