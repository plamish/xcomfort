
## Eaton xComfort SHC integration for Home Assistance 


#### Installation:
  1. Copy all files to /custom_components/xcomfort and restart your HA
  2. In Configuration->Integrations add "XComfort SHC"
  3. Lights, switches, shutters and temperature sensors should appear in your HA

or use [HACS](https://hacs.xyz/docs/setup/download "HACS") and add as custom repo.

<b>Warning</b>: This integration is not finshed and work is still in progress. All comments and feedback is welcomed

#### Configuration

Please note only devices from one SHC zone will be added to HA. For zone 1 use hz_1, for 2 use hz_2, etc.

To find zone number log into SHC via web console using this address http://ip_address_of_your_integration/system/console/config, go to Configuration Status -> Home Devices and use search function to search for 'hz_'. Number following hz_ is the zone number.

#### Limitations

The integration supports today:
- Switch actuators
- Light actuators 
- Shutter actuators
- Scenes
- Temperature sensor
- Binary sensors
- Radiator thermostats

The integration polls updates from xComfort SHC to Home Assistant with user defined frequency. Work on push based status updates is in progress.


#### xComfort to MQTT broker
For instant, push based updates from xComfort SHC to Home Assistant you can try AppDaemon based [xcomfort2mqtt](https://github.com/plamish/xcomfort2mqtt "xcomfort2mqtt") . This can be useful if you want to trigger  Home Assistant automations from your xComfort devices

#### Help and new ideas
For help or question open an issue. For new ideas or comments open an discussion


