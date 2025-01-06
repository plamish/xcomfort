###Version 1.3.6
import async_timeout
import logging

from datetime import timedelta
from homeassistant.helpers import entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

#from xcomfortshc import xcomfortAPI
from .xcomfortAPI import xcomfortAPI

from .const import DOMAIN, VERSION
_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    return True

async def async_setup_entry(hass, config_entry):

    websession = async_get_clientsession(hass)
    coordinator = XCDataUpdateCoordinator(hass, websession, config_entry.data["url"],config_entry.data["zone"],
        config_entry.data["username"], config_entry.data["password"], config_entry.data["scan_interval"])
    await coordinator.xc.connect()
    await coordinator.async_refresh()
    hass.data[DOMAIN] = coordinator

    await hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, "sensor"))
    await hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, "light"))
    await hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, "switch"))
    await hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, "button"))
    await hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, "cover"))
    await hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, "climate"))

    async def async_service1(service_call):
        await coordinator.xc.debug()

    hass.services.async_register(DOMAIN,"save_status_files",async_service1,)
    return True

class XCDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, session, url, zone, username, password, scan_interval,  ):
        stat_interval = 60 // scan_interval
        if stat_interval == 0:
            stat_interval = 1
        self.xc = xcomfortAPI(session, url, zone, username, password, stat_interval)
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=scan_interval))

    async def _async_update_data(self):
        try:
            await self.xc.get_statuses()
        except:
            raise UpdateFailed("Error API")
        if not self.xc.devices:
            raise UpdateFailed("Invalid sensors data")
        return self.xc.devices
