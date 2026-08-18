"""Data for the Recteq integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .api import RecteqGrill
    from .coordinator import RecteqCoordinator


@dataclass
class RecteqData:
    """Class for storing Recteq integration data."""

    grill: RecteqGrill
    coordinator: RecteqCoordinator
