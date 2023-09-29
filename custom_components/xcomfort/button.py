###Version 1.3.4
from homeassistant.components.button import ButtonEntity
import json
import logging
import asyncio

from .const import DOMAIN
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN]
    i = 0
    for scene in coordinator.xc.scenes:
        async_add_entities([xcScene(coordinator, i, scene['id'], scene['name'])])
        i += 1

class xcScene(ButtonEntity):

    def __init__(self, coordinator, id, unique_name, name ):
        self.id = id
        self._name = name
        self._unique_id = unique_name
        self.coordinator = coordinator
        _LOGGER.debug("xcScene.init() %s", self.name)

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    async def async_press(self) -> None:
        _LOGGER.debug("Scene %s activation called", self.name)
        if await self.coordinator.xc.scene(self._unique_id):
            _LOGGER.debug("Scene %s activation success",self.name)
        else:
            _LOGGER.debug("Scene %s activation unsucessful",self.name)
