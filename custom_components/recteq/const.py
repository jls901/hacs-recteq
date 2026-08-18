"""Constants for the Recteq integration."""

from logging import getLogger
from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "recteq"

PLATFORMS: Final = [Platform.SWITCH, Platform.CLIMATE, Platform.SENSOR]

LOGGER: Final = getLogger(__package__)

DPS_POWER = "1"
DPS_TARGET = "101"
DPS_ACTUAL = "102"
DPS_PROBEA = "103"
DPS_PROBEB = "104"
DPS_MIN_FEED_RATE = "105"
DPS_TEMP_ADJUST = "106"
DPS_ERROR1 = "107"
DPS_ERROR2 = "108"
DPS_ERROR3 = "109"

NAME_POWER = "Power"
NAME_TARGET = "Target Temperature"
NAME_ACTUAL = "Actual Temperature"
NAME_PROBEA = "Probe A Temperature"
NAME_PROBEB = "Probe B Temperature"

PROTOCOL_3_1 = "3.1"
PROTOCOL_3_3 = "3.3"
PROTOCOL_3_4 = "3.4"

PROTOCOLS: Final = [PROTOCOL_3_1, PROTOCOL_3_3, PROTOCOL_3_4]

DEFAULT_PROTOCOL = PROTOCOL_3_4

LEN_DEVICE_ID = 22
LEN_LOCAL_KEY = 16

CONF_DEVICE_ID = "device_id"
CONF_LOCAL_KEY = "local_key"
CONF_PROTOCOL = "protocol"
CONF_FORCE_FAHRENHEIT = "force_fahrenheit"

STR_INVALID_PREFIX = "invalid_"
STR_PLEASE_CORRECT = "please_correct"
