###Version 1.1A
from homeassistant.components.cover import (
    SUPPORT_CLOSE,
    SUPPORT_OPEN,
    SUPPORT_STOP,
    CoverEntity,
)

import json
import logging
import asyncio

from .const import DOMAIN
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN]
    i = 0
    for device in coordinator.data:
        if device['type'].find("Shutt") >= 0:
            async_add_entities([xcShutter(coordinator, i, device['id'], device['name'])])
        i += 1

class xcShutter(CoverEntity):
    def __init__(self, coordinator, id, unique_name, name ):
        self.id = id
        self._name = name
        self._unique_id = unique_name
        self.coordinator = coordinator
        self._device_class = "shutter"
        self.last_message_time = ''
        self.messages_per_day = ''
        _LOGGER.debug("xcShutter.init() %s", self.name)

    @property
    def name(self):
        return self._name


    @property
    def icon(self):
        if self.available:
            if self.is_closed:
                return "mdi:window-shutter"
            else:
                return "mdi:window-shutter-open"
        else:
            return "mdi:exclamation-thick"

    @property
    def assumed_state(self):
        return True

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def device_state_attributes(self):
        stats_id = str(self._unique_id).replace('xCo','hdm:xComfort Adapter')
        try:
            self.last_message_time = self.coordinator.xc.log_stats[stats_id]['lastMsgTimeStamp']
        except:
            self.last_message_time = ''
            self.messages_per_day = ''
        else:
            self.messages_per_day = self.coordinator.xc.log_stats[stats_id]['msgsPerDay']
        return {"Messeges per day": self.messages_per_day, "Last message": self.last_message_time}


    @property
    def device_class(self):
        return self._device_class

    @property
    def is_closed(self):
        if self.coordinator.data[self.id]['value'] == "OPENED":
            return False
        elif self.coordinator.data[self.id]['value'] == "CLOSED":
            return True
        else:
            return None

    async def async_open_cover(self, **kwargs):
        if await self.coordinator.xc.switch(self._unique_id,"open"):
            #self.coordinator.xc.devices[self.id]['value']="OPENED"
            _LOGGER.debug("xcShutter.open %s success",self.name)
        else:
            _LOGGER.debug("xcShutter.open %s unsucessful",self.name)

    async def async_close_cover(self, **kwargs):
        if await self.coordinator.xc.switch(self._unique_id,"close"):
            #self.coordinator.xc.devices[self.id]['value']="CLOSED"
            _LOGGER.debug("xcShutter.open %s success",self.name)
        else:
            _LOGGER.debug("xcShutter.open %s unsucessful",self.name)

    async def async_stop_cover(self, **kwargs):
        if await self.coordinator.xc.switch(self._unique_id,"stop"):
            self.coordinator.xc.devices[self.id]['value']="?"
            _LOGGER.debug("xcShutter.stop %s success",self.name)
        else:
            _LOGGER.debug("xcShutter.stop %s unsucessful",self.name)

    async def async_update(self):
        await self.coordinator.async_request_refresh()
