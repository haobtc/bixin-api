from bixin_api import Client

_REQUIRED_KEYS = {
    'vendor_name',
    'secret',
    'aes_key',
}


def get_config():
    from django.conf import settings

    if not hasattr(settings, 'BIXIN_CONFIG'):
        raise ValueError("BIXIN_CONFIG should be set in django settings.")
    bixin_config = settings.BIXIN_CONFIG
    for key in _REQUIRED_KEYS:
        if key not in bixin_config:
            raise ValueError(
                "config <%s> should be set in bixin-config"
            )
    return bixin_config


def get_client():
    config = get_config()
    return Client(config['vendor_name'], config['secret'])
