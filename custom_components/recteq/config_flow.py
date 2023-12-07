"""Config flow for the Recteq integration."""
import logging
import socket
import uuid
import voluptuous as vol
from .const import (
    CONF_DEVICE_ID,
    CONF_FORCE_FAHRENHEIT,
    CONF_IP_ADDRESS,
    CONF_LOCAL_KEY,
    CONF_NAME,
    CONF_PROTOCOL,
    DEFAULT_PROTOCOL,
    DOMAIN,
    LEN_DEVICE_ID,
    LEN_LOCAL_KEY,
    PROTOCOLS,
    STR_INVALID_PREFIX,
    STR_PLEASE_CORRECT,
)
from homeassistant.const import (
    CONF_HOST,
)
from collections import OrderedDict
from homeassistant import config_entries
from homeassistant.core import callback

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class RecteqFlowHandler(config_entries.ConfigFlow):
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        self._errors = {}
        self._data = {}
        self._data["unique_id"] = str(uuid.uuid4())

    async def async_step_user(self, user_input=None):
        self._errors = {}

        if user_input is not None:
            self._data.update(user_input)

            try:
                socket.inet_aton(user_input[CONF_HOST])
            except OSError:
                self._errors[CONF_HOST] = STR_INVALID_PREFIX + CONF_IP_ADDRESS

            user_input[CONF_DEVICE_ID] = user_input[CONF_DEVICE_ID].replace(" ", " ")
            if len(user_input[CONF_DEVICE_ID]) != LEN_DEVICE_ID:
                # not all(c in string.hexdigits for c in user_input[CONF_DEVICE_ID])):
                self._errors[CONF_DEVICE_ID] = STR_INVALID_PREFIX + CONF_DEVICE_ID

            user_input[CONF_LOCAL_KEY] = user_input[CONF_LOCAL_KEY].replace(" ", " ")
            if len(user_input[CONF_LOCAL_KEY]) != LEN_LOCAL_KEY:
                # not all(c in string.hexdigits for c in user_input[CONF_LOCAL_KEY])):
                self._errors[CONF_LOCAL_KEY] = STR_INVALID_PREFIX + CONF_LOCAL_KEY

            user_input[CONF_PROTOCOL] = user_input[CONF_PROTOCOL].strip()
            if user_input[CONF_PROTOCOL] not in PROTOCOLS:
                self._errors[CONF_PROTOCOL] = STR_INVALID_PREFIX + CONF_PROTOCOL

            if self._errors == {}:
                self.init_info = user_input
                return self.async_create_entry(
                    title=self._data[CONF_NAME], data=self._data
                )
            else:
                self._errors["base"] = STR_PLEASE_CORRECT

            await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
            self._abort_if_unique_id_configured()

        return await self._show_user_form(user_input)

    async def _show_user_form(self, user_input):
        name = ""
        host = ""
        device_id = ""
        local_key = ""
        protocol = DEFAULT_PROTOCOL

        if user_input is not None:
            if CONF_NAME in user_input:
                name = user_input[CONF_NAME]
            if CONF_HOST in user_input:
                host = user_input[CONF_HOST]
            if CONF_DEVICE_ID in user_input:
                device_id = user_input[CONF_DEVICE_ID]
            if CONF_LOCAL_KEY in user_input:
                local_key = user_input[CONF_LOCAL_KEY]
            if CONF_PROTOCOL in user_input:
                protocol = user_input[CONF_PROTOCOL]
            # if CONF_FORCE_FAHRENHEIT in user_input:
            #     force_fahrenheit = user_input[CONF_FORCE_FAHRENHEIT]

        data_schema = OrderedDict()
        data_schema[vol.Required(CONF_NAME, default=name)] = str
        data_schema[vol.Required(CONF_HOST, default=host)] = str
        data_schema[vol.Required(CONF_DEVICE_ID, default=device_id)] = str
        data_schema[vol.Required(CONF_LOCAL_KEY, default=local_key)] = str
        data_schema[vol.Optional(CONF_PROTOCOL, default=protocol)] = str

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=self._errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=self.config_entry.data[CONF_NAME], data=user_input
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_FORCE_FAHRENHEIT,
                        default=self.config_entry.options.get(CONF_FORCE_FAHRENHEIT),
                    ): bool
                }
            ),
        )
