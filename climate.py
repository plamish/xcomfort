###Version 1.1A
import json
import logging
import asyncio

from homeassistant.components.climate import PLATFORM_SCHEMA, ClimateEntity

from homeassistant.const import TEMP_CELSIUS

from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_TEMPERATURE,
    CONF_NAME,
    EVENT_HOMEASSISTANT_START,
    PRECISION_HALVES,
    PRECISION_TENTHS,
    PRECISION_WHOLE,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_ON,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)

from homeassistant.components.climate.const import (
    ATTR_PRESET_MODE,
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    CURRENT_HVAC_OFF,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    HVAC_MODE_AUTO,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    PRESET_AWAY,
    PRESET_NONE,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)

from .const import DOMAIN
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN]
    await coordinator.xc.get_zones()
    try:
        if config_entry.data["heating_zone0"]!='':
            zone_name = next(x for x in coordinator.xc.zones_list if x['zoneId']==config_entry.data["heating_zone0"])['zoneName']
            async_add_entities([xcThermostat(coordinator, config_entry.data["heating_zone0_radiator"], 
                zone_name, config_entry.data["heating_zone0"], True)])
    except:
        pass    

    try:
        if config_entry.data["heating_zone1"]!='':
            zone_name = next(x for x in coordinator.xc.zones_list if x['zoneId']==config_entry.data["heating_zone1"])['zoneName']
            async_add_entities([xcThermostat(coordinator, config_entry.data["heating_zone1_radiator"],  
                zone_name, config_entry.data["heating_zone1"], False)])
    except:
        pass
    try:
        if config_entry.data["heating_zone2"]!='':
            zone_name = next(x for x in coordinator.xc.zones_list if x['zoneId']==config_entry.data["heating_zone2"])['zoneName']
            async_add_entities([xcThermostat(coordinator, config_entry.data["heating_zone2_radiator"], 
                zone_name, config_entry.data["heating_zone2"], False)])

    except:
        pass

    try:
        if config_entry.data["heating_zone3"]!='':
            zone_name = next(x for x in coordinator.xc.zones_list if x['zoneId']==config_entry.data["heating_zone3"])['zoneName']
            async_add_entities([xcThermostat(coordinator, config_entry.data["heating_zone3_radiator"], 
                zone_name, config_entry.data["heating_zone3"], False)])
    except:
        pass
 
    try:
        if config_entry.data["heating_zone4"]!='':
            zone_name = next(x for x in coordinator.xc.zones_list if x['zoneId']==config_entry.data["heating_zone4"])['zoneName']
            async_add_entities([xcThermostat(coordinator, config_entry.data["heating_zone4_radiator"], 
                zone_name, config_entry.data["heating_zone4"], False)])
    except:
        pass

    try:
        if config_entry.data["heating_zone5"]!='':
            zone_name = next(x for x in coordinator.xc.zones_list if x['zoneId']==config_entry.data["heating_zone5"])['zoneName']
            async_add_entities([xcThermostat(coordinator, config_entry.data["heating_zone5_radiator"], 
                zone_name, config_entry.data["heating_zone5"], False)])
    except:
        pass

    try:
        if config_entry.data["heating_zone6"]!='':
            zone_name = next(x for x in coordinator.xc.zones_list if x['zoneId']==config_entry.data["heating_zone6"])['zoneName']
            async_add_entities([xcThermostat(coordinator, config_entry.data["heating_zone6_radiator"], 
                zone_name, config_entry.data["heating_zone6"], False)])
    except:
        pass
    
class xcThermostat(ClimateEntity):
    def __init__(self, coordinator, id, name, heating_zone, rm):
        self.id = id
        self._name = name
        self._unique_id = 'climate'+id
        self.coordinator = coordinator
        self.last_message_time = ''
        self.messages_per_day = ''
        self.temp_pos = 0
        self._hvac_mode = HVAC_MODE_HEAT
        self._active = False
        self._cur_temp = None
        self._heating_zone = heating_zone
        self._rm = rm
        coordinator.xc.add_heating_zone(heating_zone)
        
        #_LOGGER.debug("init()  id= %s", self.id)
        #_LOGGER.debug("init()  heating_zones= %s", self.coordinator.xc.heating_zones)
        



    @property
    def icon(self):
        if self.available:
            if self.is_on:
                return "mdi:thermometer-lines"
            else:
                return "mdi:thermometer-off"
        else:
            return "mdi:exclamation-thick"
            
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
    def is_on(self):
        return True

    
    @property
    def target_temperature_step(self):
        return PRECISION_HALVES

    @property
    def supported_features(self):
        """Return the supported features."""
        return SUPPORT_TARGET_TEMPERATURE
        
    @property
    def temperature_unit(self):
        return TEMP_CELSIUS


    @property
    def max_temp(self):
        return 24

    @property
    def min_temp(self):
        return 10        
  
  
    @property
    def _is_device_active(self):
        return bool(self.temp_pos>0)        
        
    @property
    def available(self):
        return True

    @property
    def target_temperature(self):
        _LOGGER.debug("target_temperature  heating_status=%s", self.coordinator.xc.heating_status)
        
        if self._hvac_mode == HVAC_MODE_HEAT:
            if self.coordinator.xc.heating_status!={}:
                _status = self.coordinator.xc.heating_status[self._heating_zone]
                if _status!={}:
                    return float(_status['setpoint'])
                else:
                    return None
            else:
                return None
                
    @property
    def current_temperature(self):
        if self._rm:
            try:
                dev = next(x for x in self.coordinator.data if x['id']=='xCo:'+self.id+'_u12')
                temp = float(dev['value'])
                return temp
            except:
                return None
        else:   
            try:
                dev = next(x for x in self.coordinator.data if x['id']=='xCo:'+self.id+'_u0')
                temp = float(dev['value'])
                return temp
            except:
                return None

    @property
    def hvac_modes(self):
        return [HVAC_MODE_HEAT, HVAC_MODE_OFF]
        
    @property
    def hvac_mode(self):
        return self._hvac_mode

    @property
    def hvac_action(self):
        if self._hvac_mode == HVAC_MODE_OFF:
            return CURRENT_HVAC_OFF
        if not self._is_device_active:
            return CURRENT_HVAC_IDLE


    @property
    def device_state_attributes(self):
        stats_id = str('xCo:'+self.id+'_vp').replace('xCo','hdm:xComfort Adapter')
        try:
            self.last_message_time = self.coordinator.xc.log_stats[stats_id]['lastMsgTimeStamp']
        except:
            self.messages_per_day = '0'
        else:
            self.messages_per_day = self.coordinator.xc.log_stats[stats_id]['msgsPerDay']
            try:
                self.temp_pos = float(self.coordinator.xc.log_stats[stats_id]['eventLog'])
            except:
                self.temp_pos = 0
        return {'Messeges per day': self.messages_per_day, 'Last message': self.last_message_time, 'Position:': self.temp_pos}


    async def async_set_temperature(self, **kwargs):
        await self.coordinator.xc.set_temperture(self._heating_zone, kwargs.get(ATTR_TEMPERATURE))
        self.async_write_ha_state()


    async def async_set_hvac_mode(self, hvac_mode):
        if hvac_mode == HVAC_MODE_HEAT:
            _hvac_mode = True
        else:
            _hvac_mode = False
            
        if await self.coordinator.xc.set_heatingmode(self._heating_zone, _hvac_mode):
            self._hvac_mode = hvac_mode
        else:
            LOGGER.error("Can't set hvac mode %s", self._heating_zone)
                
        #self.async_write_ha_state()
        


    async def async_added_to_hass(self):
        """Connect to dispatcher listening for entity data notifications."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )


