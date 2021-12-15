# xComfort
Home Assistant Eaton xComfort SHC integration


Installation:
  1. Copy all files to /custom_components/xcomfort and restart your HA
  2. In Configuration->Integrations add "XComfort SHC"
  3. Lights, switches, shutters and temperature sensors should appear in your HA

or use HACS and add as custom repo.

Please note only devices from one SHC zone will be added to HA. For zone 1 use hz_1, for 2 use hz_2, etc.

To find zone number log into SHC via web console using this address http://ip_address_of_your_integration/system/console/config, go to Configuration Status -> Home Devices and use search function to search for 'hz_'. Number following hz_ is the zone number.

The integration supports some of xComfort thermostats. Configuration is not straight forward and if you want to give try configure open an issue and I'll provide more guidline.

<b>Warning</b>: This integration is not finshed and work is still in progress. All comments and feedback is welcomed
