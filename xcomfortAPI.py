import logging
import json
import aiohttp

_LOGGER = logging.getLogger(__name__)


class xcomfortAPI:
    def __init__(self, session: aiohttp.ClientSession ,url, zone, username, password, stat_interval):
        self.sessionID = ''
        self.session = session
        self.devices = {}
        self.log_stats = {}
        self.username = username
        self.url = url
        self.zone = zone
        self.password = password
        self.update_counter = 0
        self.stat_interval = stat_interval
        try:
            file = open("xcomfort_session","r")
            self.sessionID = file.read()
        except IOError:
            self.is_connected = False
        else:
            file.close()
            self.is_connected = True

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
        _LOGGER.debug("xcomfort.query(%s)",method)
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

    async def get_statuses(self):
        self.update_counter +=1
        _LOGGER.debug("get_statuses() counter=%d, stat_interval=%d",self.update_counter,self.stat_interval)
        self.devices = await self.query('StatusControlFunction/getDevices', params=[self.zone, ''])
        if self.update_counter >= self.stat_interval:
            self.update_counter = 0
            self.log_stats = await self.query('Diagnostics/getPhysicalDevicesWithLogStats')
        return True

    async def switch(self, dev_id, state):
        result = await self.query('StatusControlFunction/controlDevice', params=[self.zone, dev_id, state])
        if not result['status'] == 'ok':
            return False
        else:
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
        """Return True is data is available."""
        return bool(self.devices)
