from bixin_api import Client
from bixin_api.client import GraphQLClient

_BASE_KEYS = {
    'client',
    'graphql_client',
}

_CLIENT_REQUIRED_KEYS = {
    'vendor_name',
    'secret',
    'aes_key',
}

_GRAPHQL_REQUIRED_KEYS = {}


def get_client_config():
    from django.conf import settings

    if not hasattr(settings, 'BIXIN_CONFIG'):
        raise ValueError("BIXIN_CONFIG should be set in django settings.")
    if 'client' not in settings.BIXIN_CONFIG:
        raise ValueError("client config is required")
    bixin_config = settings.BIXIN_CONFIG['client']
    for key in _CLIENT_REQUIRED_KEYS:
        if key not in bixin_config:
            raise ValueError(
                "config <%s> should be set in client config"
            )
    return bixin_config


def get_gql_config():
    from django.conf import settings

    if not hasattr(settings, 'BIXIN_CONFIG'):
        raise ValueError("BIXIN_CONFIG should be set in django settings.")
    if 'client' not in settings.BIXIN_CONFIG:
        raise ValueError("client config is required")
    bixin_config = settings.BIXIN_CONFIG['graphql_client']
    for key in _GRAPHQL_REQUIRED_KEYS:
        if key not in bixin_config:
            raise ValueError(
                "config <%s> should be set in graphql_client config"
            )
    return bixin_config


def get_client():
    config = get_client_config()
    return Client(config['vendor_name'], config['secret'], server_url=config.get('server_url'))


def get_gql_client():
    gql_config = get_gql_config()
    client_config = get_client_config()
    return GraphQLClient(
        client_config['vendor_name'],
        client_config['secret'],
        server_url=client_config.get('server_url'),
        gql_server_url=gql_config.get('server_url')
    )
