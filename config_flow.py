###Version 1.0
from homeassistant.const import CONF_NAME
from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN

DATA_SCHEMA = vol.Schema(
    {
        vol.Required("name", default="XComfort"): str,
        vol.Required("url", default="http://10.0.0.10"): str,
        vol.Required("username", default="admin"): str,
        vol.Required("password",default=""): str,
        vol.Required("zone",default="hz_1"): str,
        vol.Required("scan_interval", default=3): int,
    }
)


class ExampleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(
                    user_input["url"], raise_on_progress=False
                )
            self._abort_if_unique_id_configured()

            #websession = async_get_clientsession(self.hass)
            #with timeout(30):
            #    gios = Gios(user_input[CONF_STATION_ID], websession)
            #    await gios.update()

            return self.async_create_entry(
                    title=user_input["name"], data=user_input,
                )
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors,
        )
