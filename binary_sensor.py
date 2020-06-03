###Version 1.0
from homeassistant.helpers.entity import Entity
from homeassistant.const import STATE_ON, STATE_OFF
import json
import logging
import asyncio

from .const import DOMAIN
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN]
    async_add_entities([xcBinarySensor(coordinator, "hdm:xComfort Adapter:4003731_u0", "podlogowka_pompa")])
    async_add_entities([xcBinarySensor(coordinator, "hdm:xComfort Adapter:4003821_u0", "podlogowka_zawory")])


class xcBinarySensor(Entity):

    def __init__(self, coordinator, unique_name, name ):
        self._name = name
        self._unique_id = unique_name
        self.coordinator = coordinator
        self.last_message_time = ''
        self.messages_per_day = ''
        self.event_log = ''
        _LOGGER.debug("xcBinarySensor.init() %s",name)

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def is_on(self):
        return self._state == 1

    @property
    def state(self):
        try:
            self.event_log = self.coordinator.xc.log_stats[self._unique_id]['eventLog']
        except:
            self.event_log = ''
        return STATE_ON if (self.event_log == 'ON/OPEN') else STATE_OFF


    @property
    def device_state_attributes(self):
        try:
            self.last_message_time = self.coordinator.xc.log_stats[self._unique_id]['lastMsgTimeStamp']
            self.messages_per_day = self.coordinator.xc.log_stats[self._unique_id]['msgsPerDay']

        except:
            self.last_message_time = ''
            self.messages_per_day = ''
        return {"Messeges per day": self.messages_per_day, "Last message": self.last_message_time}

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        await self.coordinator.async_request_refresh()
