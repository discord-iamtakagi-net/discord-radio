import urllib.request
import urllib.error
import urllib.parse

import re
import base64
import json

from collections import OrderedDict

from http.cookiejar import FileCookieJar
import xml.etree.ElementTree as ET

from logger import logger

class Radiko():
    """ Radiko Api Client"""

    LOGIN_URL = "https://radiko.jp/ap/member/login/login"
    CHECK_URL = "https://radiko.jp/ap/member/webapi/member/login/check"
    LOGOUT_URL = "https://radiko.jp/ap/member/webapi/member/logout"
    CHANNEL_AREA_URL = "https://radiko.jp/v3/station/list/{}.xml"
    CHANNEL_FULL_URL = "https://radiko.jp/v3/station/region/full.xml"
    AUTH1_URL = "https://radiko.jp/v2/api/auth1"
    AUTH2_URL = "https://radiko.jp/v2/api/auth2"
    AUTH_KEY = "bcd151073c03b352e1ef2fd66c32209da9ca0afa"
    area_data = {}
    station_data = None
    stations = None
    area_id = None
    inst_ctr = 0
    opener = None
    token = None

    def __init__(
            self, acct={}, force_get_stations=False):
        Radiko.inst_ctr += 1
        if acct:
            if Radiko.opener:
                opener = Radiko.opener
                login_state = self.check_login(opener)
            if not Radiko.opener or not login_state:
                opener, cj = self.login(acct)
                login_state = self.check_login(opener)
                if login_state:
                    Radiko.opener = opener
            self.login_state = login_state
        else:
            self.login_state = None
        if self.login_state:
            self.opener = opener
            urllib.request.install_opener(opener)
        else:
            self.opener = None
        if force_get_stations or not Radiko.area_id:
            token, area_id = self.get_token()
            Radiko.token = token
            Radiko.area_id = area_id
            self.get_stations()

    def get_token(self):
        res = self.auth1()
        partialkey, token = self.get_partial_key(res)
        txt = self.auth2(partialkey, token)
        logger.debug(txt.strip())
        area_id, area_name, area_name_ascii = txt.strip().split(',')
        return token, area_id

    def login(self, acct):
        cj = FileCookieJar()
        opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(cj)
        )
        post = {
            'mail': acct['mail'],
            'pass': acct['pass']
        }
        data = urllib.parse.urlencode(post).encode('utf-8')
        res = opener.open(Radiko.LOGIN_URL, data)
        return opener, cj

    def check_login(self, opener):
        if not opener:
            logger.info('premium account not set')
            return None
        try:
            check = opener.open(Radiko.CHECK_URL)
            txt = check.read()
            logger.info('premium logged in')
            return json.loads(txt.decode())
        except urllib.request.HTTPError as e:
            logger.debug(e)
            if e.code == 400:
                logger.info('premium not logged in')
                return None
            else:
                raise e

    def logout(self):
        if self.login_state:
            logout = self.opener.open(Radiko.LOGOUT_URL)
            txt = logout.read()
            self.login_state = None
            logger.info('premium logout')
            return json.loads(txt.decode())

    def auth1(self):
        auth_response = {}

        headers = {
            "User-Agent": "curl/7.56.1",
            "Accept": "*/*",
            "X-Radiko-App": "pc_html5",
            "X-Radiko-App-Version": "0.0.1",
            "X-Radiko-User": "dummy_user",
            "X-Radiko-Device": "pc",
        }
        req = urllib.request.Request(Radiko.AUTH1_URL, None, headers)
        res = urllib.request.urlopen(req)
        auth_response["body"] = res.read()
        auth_response["headers"] = res.info()

        return auth_response

    def get_partial_key(self, auth_response):

        authtoken = auth_response["headers"]["x-radiko-authtoken"]
        offset = auth_response["headers"]["x-radiko-keyoffset"]
        length = auth_response["headers"]["x-radiko-keylength"]

        offset = int(offset)
        length = int(length)
        partialkey = Radiko.AUTH_KEY[offset:offset+length]
        partialkey = base64.b64encode(partialkey.encode())

        return partialkey, authtoken

    def auth2(self, partialkey, auth_token):

        headers = {
            "X-Radiko-AuthToken": auth_token,
            "X-Radiko-Partialkey": partialkey,
            "X-Radiko-User": "dummy_user",
            "X-Radiko-Device": 'pc'
        }

        req = urllib.request.Request(Radiko.AUTH2_URL, None, headers)
        res = urllib.request.urlopen(req)
        text = res.read().decode()

        return text

    def gen_temp_chunk_m3u8_url(self, url, auth_token):

        headers = {
            "X-Radiko-AuthToken": auth_token,
        }
        req = urllib.request.Request(url, None, headers)
        try:
            res = urllib.request.urlopen(req)
        except urllib.request.HTTPError as e:
            logger.error(e)
            if e.code == 403:
                return None
            else:
                raise e
        body = res.read().decode()
        lines = re.findall('^https?://.+m3u8$', body, flags=(re.MULTILINE))

        return lines[0]

    
    def get_stations(self):
        res = urllib.request.urlopen(Radiko.CHANNEL_FULL_URL)
        xml_string = res.read()
        root = ET.fromstring(xml_string)
        station_data = []
        for region in root:
            data = {}
            data['region'] = region.attrib
            data['stations'] = []
            for station in region:
                current_station = {}
                for e in station:
                    if e.tag in ['id', 'name',
                                 'ascii_name', 'areafree', 'timefree', 'area_id']:
                        value = e.itertext().__next__()
                        current_station[e.tag] = value
                data['stations'].append(current_station)
            station_data.append(data)
        Radiko.station_data = station_data
        areas = ['JP{}'.format(i+1) for i in range(47)]
        for area_id in areas:
            if area_id == Radiko.area_id or area_id not in Radiko.area_data:
                res = urllib.request.urlopen(
                    Radiko.CHANNEL_AREA_URL.format(area_id))
                xml_string = res.read()
                root = ET.fromstring(xml_string)
                area_name = root.attrib['area_name']
                stations = []
                for station in root:
                    for e in station:
                        if e.tag in ['id']:
                            stations.append(e.itertext().__next__())
                Radiko.area_data[area_id] = {
                    'area_name': area_name,
                    'stations': stations
                }
        stations = OrderedDict()
        for region in station_data:
            region_data = region['region']
            for s in region['stations']:
                station_id = s['id']
                region_name = region_data['region_name']
                area_id = s['area_id']
                area_name = re.sub(
                    '([^ ]+) JAPAN', '\\1',
                    Radiko.area_data[area_id]['area_name']
                )
                name = s['name']
                if (self.login_state or
                        station_id in Radiko.area_data[Radiko.area]['stations']):
                    stations[station_id] = (
                        name, region_name, area_id, area_name
                    )
        Radiko.stations = stations

    def __del__(self):
        Radiko.inst_ctr -= 1
        logger.debug('Radiko destructor: {}'.format(Radiko.inst_ctr))
        if Radiko.inst_ctr == 0:
            ret = self.logout()
            logger.debug(ret)
