import sys


def get_access_token(vendor_name, secret_key):
    from bixin_api import Client
    client = Client(vendor_name=vendor_name, secret=secret_key)
    token = client.fetch_access_token()
    print(token)


if __name__ == '__main__':
    get_access_token(*sys.argv[1:])
