###Version 1.3.5
from homeassistant.components.switch import SwitchEntity
import json
import logging
import asyncio

from .const import DOMAIN
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN]
    i = 0
    for device in coordinator.data:
        if device['type'].find("Switch") >= 0:
            async_add_entities([xcSwitch(coordinator, i, device['id'], device['name'])])
        i += 1

class xcSwitch(SwitchEntity):

    def __init__(self, coordinator, id, unique_name, name ):
        self.id = id
        self._name = name
        self._unique_id = unique_name
        self.coordinator = coordinator
        self.last_message_time = ''
        self.messages_per_day = ''
        _LOGGER.debug("xcSwitch.init() %s", self.name)

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def extra_state_attributes(self):
        stats_id = str(self._unique_id).replace('xCo','hdm:xComfort Adapter')
        #_LOGGER.debug("xcSwitch.state_attributes() stats_id=%s", stats_id)
        try:
            self.last_message_time = self.coordinator.xc.log_stats[stats_id]['lastMsgTimeStamp']
        except:
            self.last_message_time = ''
            self.messages_per_day = ''
        else:
            self.messages_per_day = self.coordinator.xc.log_stats[stats_id]['msgsPerDay']
        #_LOGGER.debug("xcSwitch.state_attributes() self.messages_per_day=%s", self.messages_per_day)
        return {"Messeges per day": self.messages_per_day, "Last message": self.last_message_time}


    @property
    def should_poll(self):
        return False

    @property
    def is_on(self):
        return bool(self.coordinator.data[self.id]['value'] == "ON")

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))

    async def async_turn_on(self, **kwargs):
        if await self.coordinator.xc.switch(self._unique_id,"on"):
            self.coordinator.data[self.id]['value']="ON"
            await self.async_update_ha_state()
            _LOGGER.debug("xcSwitch.turn_on %s success",self.name)
        else:
            _LOGGER.debug("xcSwitch.turn_on %s unsucessful",self.name)

    async def async_turn_off(self, **kwargs):
        if await self.coordinator.xc.switch(self._unique_id,"off"):
            self.coordinator.data[self.id]['value']="OFF"
            await self.async_update_ha_state()
            _LOGGER.debug("xcSwitch.turn_off %s success",self.name)
        else:
            _LOGGER.debug("xcSwitch.turn_off %s unsucessful",self.name)
