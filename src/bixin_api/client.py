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

    # _bixin_ua = 'bixin_android/2016122600 (Channel/bixin;Version/1.0.0)'
    _bixin_ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'

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

    def request_platform(self, method, path, params=None, client_uuid=None, kwargs=None):
        params = params or {}
        params['access_token'] = self.access_token
        url = urljoin(self.server_url, path)
        if kwargs is None:
            kwargs = {}
        kwargs.update(dict(timeout=self.default_timeout))

        if method == 'GET':
            body = urlencode(params)
            if body:
                url = '%s?%s' % (url, body)
            r = requests.get(url, **kwargs)
        else:
            # POST
            cu = params.get('client_uuid', client_uuid) or uuid.uuid4().hex
            params['client_uuid'] = cu
            kwargs['data'] = params
            r = requests.post(url, **kwargs)

        if r.status_code == 200:
            return r.json()
        if r.status_code == 400:
            data = r.json()
            if 'access_token' in data:
                return self.request_platform(method, path, params=params)
            raise APIErrorCallFailed(code=r.status_code, msg=data)
        raise APIErrorCallFailed(code=r.status_code, msg=r.text)

    def get_user_by_im_token(self, user_token):
        url = '/platform/api/v1/user/im_token/{}/'.format(user_token)
        url = urljoin(self.server_url, url)
        headers = {
            'User-Agent': self._bixin_ua
        }
        resp = self.request_platform(
            'GET',
            url,
            params={'ua': self._bixin_ua},
            kwargs={'headers': headers}
        )
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

    def get_transfer_list(self, offset=0, limit=100, status=None, type=None, order='desc'):
        """
        {
            'has_more': False,
            'items': [
                {
                    'amount': '0.001',
                    'args': {'order_id': 'f99cbe34a3064bb398d0c49c1eb02120',
                             'outside_transfer_type': 'SINGLE',
                             'transfer_type': ''},
                    'category': '',
                    'client_uuid': '5aa055014cbe4edbbae70432ea912cab',
                    'currency': 'ETH',
                    'id': 1169842,
                    'note': '',
                    'reply_transfer_id': 0,
                    'status': 'SUCCESS',
                    'user.id': 125103,
                    'vendor': 'bitexpressbeta'
                },
               {
                    'amount': '0.001',
                    'args': {'order_id': '0bd811cea8c041b992264d1950a2b8b7',
                             'outside_transfer_type': 'SINGLE',
                             'transfer_type': ''},
                    'category': '',
                    'client_uuid': '88fd4f0888044043be01ed05d479921c',
                    'currency': 'ETH',
                    'id': 1169807,
                    'note': '',
                    'reply_transfer_id': 0,
                    'status': 'SUCCESS',
                    'user.id': 125103,
                    'vendor': 'bitexpressbeta'
               },
            ]
        }
        """
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

    def send_withdraw(self, currency, amount, user_id, category=None, client_uuid=None):
        data = dict(
            currency=currency,
            category=category,
            amount=amount,
            user=user_id,
            client_uuid=client_uuid,
        )
        r = self.request_platform(
            'POST',
            '/platform/api/v1/withdraw/create',
            params=data,
        )
        return r.status_code == 200

    def get_deposit_protocol(self, currency, amount, order_id):
        url = 'bixin://currency_transfer/' \
              '?target_addr={address}' \
              '&amount={amount}' \
              '&currency={currency}' \
              '&order_id={order_id}' \
              '&category=deposit'
        address = self.get_first_vendor_address(currency=currency)
        url = url.format(
            order_id=order_id,
            address=address,
            currency=currency,
            amount=amount,
        )
        return url

    def get_first_vendor_address(self, currency='BTC'):
        resp = self.get_vendor_address_list(
            currency=currency,
        )
        assert len(resp['items']) > 0
        address = resp['items'][0]
        return address

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
