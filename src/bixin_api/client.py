from datetime import timedelta
from threading import Lock
import uuid
from urllib.parse import urljoin, urlencode

import pendulum
import requests

from .constants import PLATFORM_SERVER
from .exceptions import APIErrorCallFailed, normalize_network_error
from . import constants as csts


class Client:

    _bixin_ua = 'bixin_mac/2016122600 (Channel/bixin;Version/1.0.0)'

    def __init__(self, vendor_name, secret, access_token=None, server_url=None):
        self.vendor_name = vendor_name
        self.secret = secret
        self.server_url = server_url or PLATFORM_SERVER
        self.default_timeout = 15
        self.session = requests.session()
        self._token = access_token
        self._token_expired_at = pendulum.now()

    @property
    def access_token(self):
        with Lock():
            if self._token is not None:
                return self._token
            self._token, self._token_expired_at = self.fetch_access_token()
        return self._token

    def fetch_access_token(self):
        path = '/platform/token?vendor={vendor}&secret={secret}'.format(
            vendor=self.vendor_name,
            secret=self.secret
        )
        url = urljoin(self.server_url, path)
        resp = self.session.get(url, timeout=self.default_timeout)
        if resp.status_code == 200:
            a = resp.json()
            expired_at = pendulum.now() + timedelta(seconds=a['expire_in'])
            access_token = a['access_token']
        else:
            raise APIErrorCallFailed(
                code=resp.status_code, msg=resp.text
            )
        self._token = access_token
        self._token_expired_at = expired_at
        return access_token, expired_at

    def get_login_qr_code(self, qr_code_id, is_app=False):
        assert  isinstance(qr_code_id, str)
        base_url = csts.QR_LOGIN_URL
        protocol = "{}/qrcode/?uuid={}:{}".format(
            base_url,
            self.vendor_name,
            qr_code_id,
        )
        if is_app:
            protocol = "bixin://login/confirm?{}".format(urlencode({'url': protocol}))
        return protocol

    def request_platform(self, method, path, params=None, client_uuid=None):
        params = params or {}
        params['access_token'] = self.access_token
        url = urljoin(self.server_url, path)
        kw = dict(timeout=self.default_timeout)

        if method == 'GET':
            body = urlencode(params)
            if body:
                url = '%s?%s' % (url, body)
            r = requests.get(url, **kw)
        else:
            # POST
            cu = params.get('client_uuid', client_uuid) or uuid.uuid4().hex
            params['client_uuid'] = cu
            kw['data'] = params
            r = requests.post(url, **kw)

        if r.status_code == 200:
            return r.json()
        if r.status_code == 400:
            data = r.json()
            if 'access_token' in data:
                return self.request_platform(method, path, params=params)
            raise APIErrorCallFailed(code=r.status_code, msg=data)
        raise APIErrorCallFailed(code=r.status_code, msg=r.text)

    def get_user_of_vendor(self, user_token):
        url = '/platform/api/v1/user/im_token/{}/'.format(user_token)
        url = urljoin(self.server_url, url)
        resp = self.request_platform('GET', url, params={'ua': self._bixin_ua})
        return resp

    def get_user(self, user_id):
        user_info = self.request_platform('GET', '/platform/api/v1/user/%s' % user_id)
        return user_info

    def get_user_list(self, offset=0, limit=100):
        params = {
            'offset': offset,
            'limit': limit,
        }
        return self.request_platform('GET', '/platform/api/v1/user/list', params=params)

    def get_transfer(self, client_uuid):
        return self.request_platform(
            'GET', '/platform/api/v1/transfer/item',
            {'client_uuid': client_uuid},
        )

    def get_transfer_list(self, offset=0, limit=100, status=None, type=None, order='asc'):
        return self.request_platform(
            'GET', '/platform/api/v1/transfer/list',
            {
                'offset': offset,
                'limit': limit,
                'status': status,
                'type': type,
                'order': order
            }
        )

    def send_withdraw(self, withdraw):
        assert withdraw.status == 'PENDING'
        r = self.request_platform(
            'POST',
            '/platform/api/v1/withdraw/create',
            withdraw.get_payload()
        )
        withdraw.status = 'SENT'
        withdraw.save()
        return r

    def get_vendor_address_list(self, currency='BTC', offset=0, limit=20):
        params = {
            'offset': offset,
            'limit': limit,
            'currency': currency
        }
        return self.request_platform('GET', '/platform/api/v1/address/list', params)

    def get_jsapi_ticket(self):
        return self.request_platform('GET', '/platform/api/v1/ticket/jsapi')

    def pull_event(self, since_id, limit=20):
        payload = {'since_id': since_id, 'limit': limit}
        return self.request_platform('GET', '/platform/api/v1/event/list', payload)


class PubAPI:
    _price_path = '/currency/price?from={base}&to={quote}'

    def __init__(self):
        self.session = requests.session()
        self.server_url = PLATFORM_SERVER

    @normalize_network_error
    def get_price(self, base, quote):
        """
        :return:
        {
            'error':0,
            'err_msg':'success',
            'data':{
                'from'          :   BTC,
                'to'            :   USD,
                'price'         :   9350.6600,
                'exchange'      :   false,
                'intermediate'  :   None,
            }
        }
        or
        {
            'error'     :   1001,
            'err_msg'   :   'AVH is not supported',
            'data'      :   {}
        }
        :rtype: float
        """
        path = self._price_path.format(
            base=base.upper(),
            quote=quote.upper()
        )
        url = urljoin(
            self.server_url,
            path,
        )
        resp = self.session.get(url)
        data = resp.json()
        if data['error'] != 0:
            raise APIErrorCallFailed(
                msg="Failed to fetch given price for {} {}".format(
                    base, quote
                ),
                code=data['error'],
            )
        return data['data']['price']
