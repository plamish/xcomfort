###Version 1.3.2
import logging
import json
import aiohttp

_LOGGER = logging.getLogger(__name__)


class xcomfortAPI:
    def __init__(self, session: aiohttp.ClientSession ,url, zone, username, password, stat_interval):
        self.sessionID = ''
        self.session = session
        self.devices = {}
        self.scenes = {}
        self.log_stats = {}
        self.zones_list = {}
        self.heating_zones = []
        self.heating_status = {}
        self.username = username
        self.url = url
        self.zone = zone
        self.password = password
        self.update_counter = 0
        self.stat_interval = stat_interval
        self.stat_scan_now = False
        self.is_connected = False
        #try:
        #    file = open("xcomfort_session","r")
        #    self.sessionID = file.read()
        #except IOError:
        #    self.is_connected = False
        #else:
        #    file.close()
        #    self.is_connected = True

    async def connect(self):
        _LOGGER.debug("connect()")
        if not self.is_connected:
            headers = {'User-Agent': 'Mozilla/5.0'}
            auth = aiohttp.BasicAuth(login=self.username, password=self.password)

            async with self.session.get(self.url, auth=auth) as response:
                _LOGGER.debug("connect() response.status=%d",response.status)
                if response.status != 200:
                    if response.status == 401:
                        _LOGGER.error('connect() Invalid username/password\nAborting...')
                        exit(1)
                    else:
                        _LOGGER.error('.connect() Server responded with status code %s', str(response.status_code))
                        exit(1)
                else:
                    _LOGGER.debug('connect() headers=%s',response.headers)
                    sID = response.headers.get("Set-Cookie")
                    x = sID.find("End")
                    self.sessionID = sID[0:x+3]
                    _LOGGER.debug('xcomfortAPI.connect() New sessionID = %s', self.sessionID)
            file = open("xcomfort_session", "w")
            file.write(self.sessionID)
            file.close()

    async def query(self, method, params=['', '']):
        #_LOGGER.debug("query(%s)",method)
        rpc_headers = {
            'Cookie':self.sessionID,
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
        }
        json_url = self.url + '/remote/json-rpc'
        rpc_data = {
            "jsonrpc": "2.0",
            'method': method,
            'params': params,
            'id': 1
        }

        try:
            async with self.session.post(json_url, data=json.dumps(rpc_data), headers=rpc_headers) as resp:
                response = await resp.json()
        except aiohttp.ClientConnectionError:
            _LOGGER.error('query() client connection error')

        if 'error' in response:
            _LOGGER.error("query() error, calling connect()")
            self.is_connected = False
            good = await self.connect()
            rpc_headers = {
                    'Cookie': self.sessionID,
                    'Accept-Encoding': 'gzip, deflate',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                }
            try:
                resp = await self.session.post(json_url, data=json.dumps(rpc_data), headers=rpc_headers)
                response = await resp.json()
            except aiohttp.ClientConnectionError:
                _LOGGER.error('query() client connection error after connect()')

        if 'result' not in response:
            response['result'] = [{}]
        return response['result']

    def add_heating_zone(self, zone):
        self.heating_zones.append(zone)
        self.stat_scan_now = True
        _LOGGER.debug("add_heating_zone zone=%s",zone)

    async def get_statuses(self):
        _LOGGER.debug("get_statuses() counter=%d, stat_interval=%d",self.update_counter,self.stat_interval)
        self.devices = await self.query('StatusControlFunction/getDevices', params=[self.zone, ''])
        self.scenes = await self.query('SceneFunction/getScenes', params=[self.zone, ''])
        #_LOGGER.debug("get_statuses() self.devices=%s", self.devices)
        #_LOGGER.debug("get_statuses() self.scenes=%s", self.scenes)
        if (self.update_counter <= 0) or self.stat_scan_now:
            _LOGGER.debug("get_statuses() update_counter <= 0")
            self.update_counter = self.stat_interval
            self.stat_scan_now = False
            self.log_stats = await self.query('Diagnostics/getPhysicalDevicesWithLogStats')
            for zone in self.heating_zones:
                #_LOGGER.debug("get_statuses() zone=%s", zone)
                results = await self.query('ClimateFunction/getZoneOverview',[zone])
                _target_temp = float(results[0]['overview'][0]['setpoint'])
                _heating = results[0]['overview'][0]['typeId']
                x = { zone:{'heating':_heating,"setpoint":_target_temp}}
                #_LOGGER.debug("get_statuses() x=%s", x)
                self.heating_status.update(x)
        self.update_counter -=1
        return True

    async def get_zones(self):
        _LOGGER.debug("get_zones()")
        self.zones_list = await self.query('HFM/getZones', params=[''])
        return True

    async def switch(self, dev_id, state):
        result = await self.query('StatusControlFunction/controlDevice', params=[self.zone, dev_id, state])
        if not result['status'] == 'ok':
            return False
        else:
            return True

    async def scene(self, scene_id):
        result = await self.query('SceneFunction/triggerScene', params=[self.zone, scene_id])
        if not result['status'] == 'ok':
            return False
        else:
            return True

    async def set_temperture(self, zone_id, temp):
        _LOGGER.debug("set_temperture %s %s ",zone_id,str(temp))
        result = await self.query('ClimateFunction/setSetpoint', [zone_id, str(temp)])
        if not result['status'] == 'ok':
            _LOGGER.debug("set_temperture %s UNsuccess",zone_id)
            return False
        else:
            _LOGGER.debug("set_temperture %s success",zone_id)
            self.heating_status[zone_id]['setpoint']=temp
            self.stat_scan_now = True
            return True

    async def set_heatingmode(self, zone_id, mode):
        if mode:
            _mode = 'heating'
        else:
            _mode = 'off'
        result = await self.query('ClimateFunction/setControlType', [zone_id, _mode])
        if not result['status'] == 'ok':
            _LOGGER.debug("set_heatingmode %s UNsuccess",zone_id)
            return False
        else:
            _LOGGER.debug("set_heatingmode %s success",zone_id)
            self.heating_status[zone_id]['heating']=mode
            self.stat_scan_now = True
            return True

    async def update(self):
        rpc_headers = {
            'Cookie':  self.sessionID,
            'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'application/json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
        }
        rpc_data = {
            "jsonrpc": "2.0",
            'method': 'StatusControlFunction/getDevices',
            'params': ['hz_9', ''],
            'id': 2}
        json_url = self.url + '/remote/json-rpc'

        try:
            resp = await self.session.post(json_url, data=json.dumps(rpc_data), headers=rpc_headers)
            resp_j = await resp.json()
            self.data = resp_j['result']
        except aiohttp.ClientConnectionError:
            _LOGGER.error('client connection error')
            self.data = None
        return True

    @property
    def available(self):
        """Return True if data is available."""
        return bool(self.devices)

    async def debug(self):
        file = open("xcomfort_devices", "w")
        file.write(json.dumps(self.devices, indent=4))
        file.close()
        file = open("xcomfort_log_stats", "w")
        file.write(json.dumps(self.log_stats, indent=4))
        file.close()
