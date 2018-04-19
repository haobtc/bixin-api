import json

from .crypto import PRPCrypt


SUB_LOGIN = 'vendor_qr_login'
SUB_USER_CREATED = 'user2vendor.created'

SUBJECT_CHOICES = {
    SUB_LOGIN,
    SUB_LOGIN,
}


class Event:
    """
    Example data:
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


def make(raw_text, aes_key=None):
    if aes_key is not None:
        raw_text = PRPCrypt(key=aes_key).decrypt(raw_text)
        # data json.loads(raw_data)
    data = json.loads(raw_text)
    assert data['subject'] in SUBJECT_CHOICES
    if data['subject'] == SUB_LOGIN:
        return LoginEvent(**data)
    return Event(**data)
