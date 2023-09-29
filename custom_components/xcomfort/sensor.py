###Version 1.3.4
from homeassistant.helpers.entity import Entity
from homeassistant.const import TEMP_CELSIUS
import json
import logging
import asyncio


_LOGGER = logging.getLogger(__name__)
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN]
    i = 0
    for device in coordinator.data:
        if device['type'].find("Temp") >= 0:
            name = device['name'].replace("(temperature)","")
            async_add_entities([xcTemperature(coordinator, i, device['id'], name)])
        i += 1

class xcTemperature(Entity):

    def __init__(self, coordinator, id, unique_name, name ):
        self.id = id
        self._name = name
        self._unique_id = unique_name
        self._unit_of_measurement = TEMP_CELSIUS
        self.coordinator = coordinator
        self.last_message_time = ''
        self.messages_per_day = ''
        self.temp_set = ''
        self.temp_pos = ''
        _LOGGER.debug("xcTemperature.init() %s",name)

    @property
    def name(self):
        return self._name

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def state(self):
        try:
            return float(self.coordinator.data[self.id]['value'])
        except:
            return None

    @property
    def unit_of_measurement(self):
        return  self._unit_of_measurement

    @property
    def extra_state_attributes(self):
        stats_id = str(self._unique_id).replace('xCo','hdm:xComfort Adapter')
        try:
            self.last_message_time = self.coordinator.xc.log_stats[stats_id]['lastMsgTimeStamp']
        except:
            self.messages_per_day = '0'
        else:
            self.messages_per_day = self.coordinator.xc.log_stats[stats_id]['msgsPerDay']
            stats_id = stats_id.replace('_u0','_vp')
            try:
                self.temp_pos = self.coordinator.xc.log_stats[stats_id]['eventLog']
                stats_id = stats_id.replace('_vp','_ta')
                self.temp_set = self.coordinator.xc.log_stats[stats_id]['eventLog']
            except:
                self.temp_set = ''
                self.temp_pos = ''

        if self.temp_set == '':
            return {"Messeges per day": self.messages_per_day, "Last message": self.last_message_time}
        else:
            return {"Messeges per day": self.messages_per_day, "Last message": self.last_message_time, "Set Temperature": self.temp_set, "Position:": self.temp_pos}

    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    #async def async_update(self):
    #    await self.coordinator.async_request_refresh()
