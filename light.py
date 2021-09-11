###Version 1.1A
from homeassistant.components.light import (ATTR_BRIGHTNESS,ATTR_BRIGHTNESS_PCT, SUPPORT_BRIGHTNESS, LightEntity)
import json
import logging
import asyncio

from .const import DOMAIN
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN]
    i = 0
    for device in coordinator.data:
        if device['type'].find("DimAct") >= 0:
            async_add_entities([xcLight(coordinator, i, device['id'], device['name'], device['type'])])
        if device['type'].find("LightAct") >= 0:
            async_add_entities([xcLight(coordinator, i, device['id'], device['name'], device['type'])])
        i += 1


class xcLight(LightEntity):
    def __init__(self, coordinator, id, unique_name, name, type ):
        self.id = id
        self._name = name
        self.type = type
        self._unique_id = unique_name
        self.coordinator = coordinator
        self.last_message_time = ''
        self.messages_per_day = ''
        _LOGGER.debug("xcLight.init()  done %s", self.name)

    @property
    def icon(self):
        if self.available:
            if self.is_on:
                return "mdi:lightbulb-on"
            else:
                return "mdi:lightbulb-outline"
        else:
            return "mdi:exclamation-thick"

    @property
    def name(self):
        return self._name

    @property
    def should_poll(self):
        return False

    @property
    def is_on(self):
        if self.type == 'DimActuator':
            return bool(self.coordinator.data[self.id]['value'] != "0")
        else:
            return bool(self.coordinator.data[self.id]['value'] == 'ON')

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def brightness(self):
        return int(255 * float(self.coordinator.data[self.id]['value']) /100 )

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
    def supported_features(self):
        if self.type == 'DimActuator':
            return SUPPORT_BRIGHTNESS
        else:
            return 0

    async def async_update(self):
        _LOGGER.debug("sensor.async_update()")
        await self.coordinator.async_request_refresh()


    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )


    async def async_turn_on(self, **kwargs):
        if self.type == 'DimActuator':
            brightness = int(100 * kwargs.get(ATTR_BRIGHTNESS, 255) / 255)
            if await self.coordinator.xc.switch(self._unique_id,str(brightness)):
                self.coordinator.data[self.id]['value']=str(brightness)
                await self.async_update_ha_state()
                _LOGGER.debug("xcLight.turn_on dimm %s success",self.name)
            else:
                _LOGGER.debug("xcLight.turn_on dimm %s unsucessful",self.name)
        else:
            if await self.coordinator.xc.switch(self._unique_id,"on"):
                self.coordinator.data[self.id]['value']="ON"
                await self.async_update_ha_state()
                _LOGGER.debug("xcLight.turn_on %s success",self.name)
            else:
                _LOGGER.debug("xcLight.turn_on %s unsucessful",self.name)

    async def async_turn_off(self, **kwargs):
        if self.type == 'DimActuator':
            if await self.coordinator.xc.switch(self._unique_id,"0"):
                self.coordinator.data[self.id]['value']='0'
                await self.async_update_ha_state()
                _LOGGER.debug("xcLight.turn_off dimm %s success",self.name)
            else:
                _LOGGER.debug("xcLight.turn_on dimm %s unsucessful",self.name)
        else:
            if await self.coordinator.xc.switch(self._unique_id,"off"):
                self.coordinator.data[self.id]['value']="OFF"
                await self.async_update_ha_state()
                _LOGGER.debug("xcLight.turn_off %s success",self.name)
            else:
                _LOGGER.debug("xcLight.turn_off %s unsucessful",self.name)
