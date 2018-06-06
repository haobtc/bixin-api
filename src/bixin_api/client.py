from datetime import timedelta
from threading import Lock
import uuid
from urllib.parse import urljoin, urlencode

import pendulum
import requests
from bixin_api.models import BixinVendorUser

from gql import gql, Client as GQLClient
from gql.transport.requests import RequestsHTTPTransport

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
                if self._token_expired_at < pendulum.now():
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
        :param type: 'deposit' or None
        return
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
        return True

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
    _price_path = '/api/v1/currency/ticker?symbol={base}_{quote}'

    def __init__(self, server_base_url=None):
        self.session = requests.session()
        self.server_url = server_base_url or PLATFORM_SERVER

    @normalize_network_error
    def get_price(self, base, quote):
        """
        :return:
        {
            ok: true,
            data: {
                price: "13.06400384",
                is_converted: true
            }
        }
        :rtype: float
        """
        path = self._price_path.format(
            base=base.lower(),
            quote=quote.lower()
        )
        url = urljoin(
            self.server_url,
            path,
        )
        resp = self.session.get(url)
        data = resp.json()
        if not data['ok']:
            raise APIErrorCallFailed(
                msg="Failed to fetch given price for {} {}".format(
                    base, quote
                ),
            )
        return data['data']['price']


class GraphQLClient(Client):
    _gql_server_url = 'https://bixin.im/platform/graphql'
    _gql_ua = 'bixin_android/2018051401 (Channel/bixin; com.bixin.bixin_android; Version/3.1.3)'

    def __init__(self, vendor_name, secret, access_token=None, server_url=None, gql_server_url=None):
        super(GraphQLClient, self).__init__(
            vendor_name=vendor_name,
            secret=secret,
            access_token=access_token,
            server_url=server_url,
        )
        self.gql_server_url = gql_server_url or self._gql_server_url
        transport = RequestsHTTPTransport(
            url=self.gql_server_url,
            use_json=True,
        )
        self.gql = GQLClient(transport=transport, fetch_schema_from_transport=True)

    def get_user_by_im_token(self, user_token):
        """
        ret:
        {'userByImToken': {'avatar_url': None,
               'fullname': '',
               'is_locked': False,
               'openid': 'b97812328ead4d57b992f18d3f168ccb',
               'target_id': 'f2a7c018ed4a47b999e1c4893da42d79',
               'username': 'bx_u6962575070',
               'vendor_fund_balance': None,
               'verified': False,
               'verifiedInfo': {'bankcard': '{
                                    "verified": false,
                                    'card_number': '',  # should be exist if true
                                }',
                                'face': '{"verified": false}',
                                'idcard': '{
                                    "verified": false,
                                    'real_name': '',    # should be exist if true
                                    'card_number': '',  # should be exist if true
                                }',
                                'passport': '{
                                    "verified": false,
                                    'first_name': '',
                                    'last_name': '',
                                    'country': '',
                                    'card_number': '',
                                }',
                                'phone': '+8615650758818'},
               'wallet_balance': '{"DASH": "0", "AE": "0", "LTC": "0", '
                                 '"READ": "0", "DOGE": "0", "ELF": "0", '
                                 '"DAI": "0", "EOS": "0", "TRX": "0", '
                                 '"AVH": "0", "MKR": "0", "BTC": "0", '
                                 '"VEN": "0", "FGC": "0", "ETH": "0", '
                                 '"RDN": "0", "USDT": "0", "ENU": "0"}'}}

        """
        access_token = self.access_token
        query = """
        query {
            userByImToken(access_token: "%s", im_token: "%s", ua_str:"%s"){
                openid
                target_id
                username
                fullname
                avatar_url
                verified
                is_locked
                wallet_balance
                vendor_fund_balance
                verifiedInfo{
                    phone
                    idcard
                    passport
                    bankcard
                    face
                }
            }
        }
        """ % (access_token, user_token, self._gql_ua)
        query = gql(query)
        ret = self.gql.execute(query)
        return BixinVendorUser(
            **ret['userByImToken'],
        )

    def send_verification_sms(self, phone: str, code) -> bool:
        if not phone.startswith('+86'):
            phone = "+86" + phone
        query = """
        mutation {
            sendSmsByPhone(
                phone: "%s", 
                sms_data:{sms_args: "[('code', '%s')]", notify_type: "verify_code"}, 
                access_token: "%s"
            ){
                ok
          }
        }
        """ % (phone, code, self.access_token)
        query = gql(query)
        ret = self.gql.execute(query)
        return ret['sendSmsByPhone']['ok']

    def transfer2openid(self, currency, amount, openid, category=None, client_uuid=None):
        client_uuid = '"%s"' % client_uuid if client_uuid else 'null'
        category = '"%s"' % category if category else 'null'
        query = """
        mutation{
          withdrawByOpenid(
            withdraw_data: {
              currency: "%s",
              amount: "%s",
              category: %s,
              client_uuid: %s,
            },
            openid: "%s",
            access_token: "%s",
          ){
            transfer{
              status
            }
          }
        }
        """ % (
            currency, amount, category,
            client_uuid, openid, self.access_token
        )
        query = gql(query)
        ret = self.gql.execute(query)
        return ret['transfer']['status'] == 'SUCCESS'

    def get_transfer_list(self, offset=0, limit=100, status=None, type=None, order='desc'):
        """
        return
        [
            {'order_id': '237e3920c6f04923968d0a8ec096613d', 'status': 'SUCCESS'}
            {'order_id': None, 'status': 'SUCCESS'}
        ]
        """
        assert order in ('desc', 'asc')
        query = """
        query {
          transfers(
            access_token: "%s",
            limit: %s,
            offset: %s,
            order: %s,
          ){
            hasMore
            totalCount
            detail {
              order_id
              status
              created_at
            }
          }
        }
        """ % (self.access_token, limit, offset, '"%s"' % order)
        query = gql(query)
        ret = self.gql.execute(query)
        return ret['transfers']['detail']
