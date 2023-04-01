[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs) 
# Eaton xComfort SHC integration for Home Assistance 
This is Eaton xComfort smart home and Home Assistance integration custom component


### Requirements :
- [xComfort Smart Home Controller](https://www.eaton.com/bg/en-gb/catalog/residential/xcomfort-smart-home-controller.html)
- [Home Assistant](https://www.home-assistant.io)

 > It is recommended to set the language of your Smart Home Controller to english as some state descriptions are language dependent and this integration only supports the english values

### Installation:
  Use [HACS](https://hacs.xyz/docs/setup/download "HACS") to install the integration

### Configuration

Please note only devices from one SHC zone will be added to HA. For zone 1 use hz_1, for 2 use hz_2, etc.

To find zone number log into SHC via web console using this address http://ip_address_of_your_integration/system/console/config, go to Configuration Status -> Home Devices and use search function to search for 'hz_'. Number following hz_ is the zone number.

 > You can create a root zone that will contain all your devices. Add this one in HA to get all devices!

### Supported devices

The integration supports today:
- Switch actuators
- Light actuators 
- Shutter actuators
- Scenes
- Temperature sensor
- Binary sensors
- Radiator thermostats

The integration polls updates from xComfort SHC to Home Assistant with user defined frequency. Work on push based status updates is in progress.


### xComfort to MQTT broker
For instant, push based updates from xComfort SHC to Home Assistant you can try AppDaemon based [xcomfort2mqtt](https://github.com/plamish/xcomfort2mqtt "xcomfort2mqtt") . This can be useful if you want to trigger  Home Assistant automations from your xComfort devices

### Help and new ideas
For help or question open an issue. For new ideas or comments open an discussion


