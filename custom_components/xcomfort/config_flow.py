###Version 1.1
from homeassistant.const import CONF_NAME
from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN


DATA_SCHEMA = vol.Schema(
    {
        vol.Required("name", default="XComfort"): str,
        vol.Required("url", default="http://10.0.0.20"): str,
        vol.Required("username", default="admin"): str,
        vol.Required("password",default=""): str,
        vol.Required("zone",default="hz_3"): str,
        vol.Required("scan_interval", default=5): int,
        vol.Optional("heating_zone0",default="hz_4"): str,
        vol.Optional("heating_zone0_radiator",default="4895915"): str,
        vol.Optional("heating_zone1",default="hz_10"): str,
        vol.Optional("heating_zone1_radiator",default="5152101"): str,
        vol.Optional("heating_zone2",default="hz_9"): str,
        vol.Optional("heating_zone2_radiator",default="5151991"): str,
        vol.Optional("heating_zone3",default="hz_6"): str,
        vol.Optional("heating_zone3_radiator",default="5149819"): str,
        vol.Optional("heating_zone4",default="hz_8"): str, 
        vol.Optional("heating_zone4_radiator",default="5149417"): str,
        vol.Optional("heating_zone5",default="hz_7"): str,  
        vol.Optional("heating_zone5_radiator",default="5151919"): str
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(
                    user_input["url"], raise_on_progress=False
                )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                    title=user_input["name"], data=user_input,
                )
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors,
        )
