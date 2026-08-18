"""Config flow for the Recteq integration."""

from __future__ import annotations

import socket
import string
from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_DEVICE_ID,
    CONF_FORCE_FAHRENHEIT,
    CONF_LOCAL_KEY,
    CONF_PROTOCOL,
    DEFAULT_PROTOCOL,
    DOMAIN,
    LEN_DEVICE_ID,
    LEN_LOCAL_KEY,
    PROTOCOLS,
    STR_INVALID_PREFIX,
    STR_PLEASE_CORRECT,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry


def _is_hex(value: str, length: int) -> bool:
    """Return True if value is exactly length hex digits."""
    return len(value) == length and all(c in string.hexdigits for c in value)


class RecteqConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for the Recteq integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            user_input[CONF_DEVICE_ID] = user_input[CONF_DEVICE_ID].strip()
            user_input[CONF_LOCAL_KEY] = user_input[CONF_LOCAL_KEY].strip()

            try:
                socket.inet_aton(user_input[CONF_HOST])
            except OSError:
                errors[CONF_HOST] = f"{STR_INVALID_PREFIX}{CONF_HOST}"

            if not _is_hex(user_input[CONF_DEVICE_ID], LEN_DEVICE_ID):
                errors[CONF_DEVICE_ID] = f"{STR_INVALID_PREFIX}{CONF_DEVICE_ID}"

            if not _is_hex(user_input[CONF_LOCAL_KEY], LEN_LOCAL_KEY):
                errors[CONF_LOCAL_KEY] = f"{STR_INVALID_PREFIX}{CONF_LOCAL_KEY}"

            if user_input[CONF_PROTOCOL] not in PROTOCOLS:
                errors[CONF_PROTOCOL] = f"{STR_INVALID_PREFIX}{CONF_PROTOCOL}"

            if not errors:
                await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

            errors["base"] = STR_PLEASE_CORRECT

        return await self._show_form(user_input, errors)

    async def _show_form(
        self, user_input: dict | None, errors: dict[str, str]
    ) -> config_entries.ConfigFlowResult:
        """Show the form."""
        user_input = user_input or {}
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_NAME, default=user_input.get(CONF_NAME, "")
                ): selector.TextSelector(),
                vol.Required(
                    CONF_HOST, default=user_input.get(CONF_HOST, "")
                ): selector.TextSelector(),
                vol.Required(
                    CONF_DEVICE_ID, default=user_input.get(CONF_DEVICE_ID, "")
                ): selector.TextSelector(),
                vol.Required(
                    CONF_LOCAL_KEY,
                    default=user_input.get(CONF_LOCAL_KEY, ""),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
                vol.Optional(
                    CONF_PROTOCOL,
                    default=user_input.get(CONF_PROTOCOL, DEFAULT_PROTOCOL),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=PROTOCOLS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> RecteqOptionsFlowHandler:
        """Get the options flow for this handler."""
        return RecteqOptionsFlowHandler(config_entry)


class RecteqOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for the Recteq integration."""

    config_entry: ConfigEntry

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the options flow."""
        if user_input is not None:
            return self.async_create_entry(
                title=self.config_entry.title, data=user_input
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_FORCE_FAHRENHEIT,
                        default=self.config_entry.options.get(
                            CONF_FORCE_FAHRENHEIT, False
                        ),
                    ): selector.BooleanSelector()
                }
            ),
        )
