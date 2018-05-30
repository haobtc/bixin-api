import json

from .crypto import PRPCrypt


SUB_LOGIN = 'vendor_qr_login'
SUB_DEPOSIT_CREATED = 'user2vendor.created'

SUBJECT_CHOICES = {
    SUB_LOGIN,
    SUB_DEPOSIT_CREATED,
}


class Event:
    """
    Example data:

    - login:

    {
        'event_id': 633776,
        'vendor_name': 'bitexpressbeta',
        'payload': {
            'qr_uuid': '8a129893-3196-4ccc-93fa-02a69d1b2d7e',
            'user_id': 125103
        },
        'uuid': '0db56cfd74984e2eb0c254d7e6b22160',
        'subject': 'vendor_qr_login',
    }

    - transfer:

    {'event_id': 1182650,
     'payload': {'amount': '0.001',
                 'currency': 'ETH',
                 'json_args': {'order_id': '9b1f084b85514ea3b90ab4073d9df088',
                               'outside_transfer_type': 'SINGLE',
                               'transfer_type': ''},
                 'note': '',
                 'transfer.id': 1169783,
                 'user.id': 125103},
     'subject': 'user2vendor.created',
     'uuid': 'b2208f6dc71c4a928060f8917c8b6441',
     'vendor_name': 'bitexpressbeta'
     }

    """
    def __init__(
            self,
            event_id,
            vendor_name,
            payload,
            uuid,
            subject,
    ):
        self.event_id = event_id
        self.vendor_name = vendor_name
        self.payload = payload
        self.uuid = uuid
        self.subject = subject

    def is_valid(self, vendor_name):
        return vendor_name == self.vendor_name

    def as_dict(self):
        return {
            'event_id': self.event_id,
            'vendor_name': self.vendor_name,
            'payload': self.payload,
            'uuid': self.uuid,
            'subject': self.subject,
        }


class LoginEvent(Event):

    @property
    def qr_code_id(self):
        return self.payload['qr_uuid']

    @property
    def user_id(self):
        return self.payload['user_id']


class DepositEvent(Event):

    @property
    def order_id(self):
        return self.payload['order_id']


_subject_event_map = {
    SUB_LOGIN: LoginEvent,
    SUB_DEPOSIT_CREATED: DepositEvent,
}


def instantiate_event(data):
    assert data['subject'] in SUBJECT_CHOICES
    event_cls = _subject_event_map.get(data['subject'], Event)
    return event_cls(**data)


def make(raw_text, aes_key=None):
    if aes_key is not None:
        raw_text = PRPCrypt(key=aes_key).decrypt(raw_text)
    data = json.loads(raw_text)
    return instantiate_event(data)
