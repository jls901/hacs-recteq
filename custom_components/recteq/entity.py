"""Base entity for the Recteq integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RecteqCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry


class RecteqEntity(CoordinatorEntity[RecteqCoordinator]):
    """Base entity for the Recteq integration."""

    config_entry: ConfigEntry

    def __init__(
        self, entry: ConfigEntry, coordinator: RecteqCoordinator, unique_id: str
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.config_entry = entry
        self._attr_unique_id = unique_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.grill.unique_id)},
        )
