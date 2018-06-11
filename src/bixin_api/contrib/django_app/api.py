from decimal import Decimal

from bixin_api.client import PubAPI

from .config import get_client


def get_vendor_address(symbol):
    client = get_client()
    address = client.get_first_vendor_address(currency=symbol)
    return address


def mk_transfer_in(user_id, symbol, amount, address=None):
    """
    数字货币还款/添加质押物
    """
    from bixin_api.contrib.django_app.models import Deposit
    from bixin_api.contrib.django_app.models import BixinUser

    if address is None:
        address = get_vendor_address(symbol)
    deposit = Deposit.objects.create(
        amount=amount,
        symbol=symbol,
        user=BixinUser.objects.get(openid=user_id),
        address=address,
    )
    return deposit.order_id, address


def mk_transfer_out(user_id, symbol, amount):
    from bixin_api.contrib.django_app.models import Withdraw
    from bixin_api.contrib.django_app.models import BixinUser

    withdraw = Withdraw.objects.create(
        address=None,
        symbol=symbol,
        amount=amount,
        user=BixinUser.objects.get(openid=user_id)
    )
    return withdraw.order_id


def get_transfer_status(order_id):
    """
    :returns: 'SUCCESS' or 'PENDING'
    """
    from bixin_api.contrib.django_app.models import Deposit
    deposit = Deposit.objects.get(order_id=order_id)
    return deposit.status


def subscribe_transfer_event(callback):
    """
    callback(order_id, order_type, order_status)
    order_status will be 'SUCCESS' or 'FAILED'
    order_type will be 'transfer_in' or 'transfer_out'
    """
    from .registry import register_callback
    assert callable(callback)
    register_callback(callback)


def get_exchange_rate(base_coin: str, quote: str) -> Decimal:
    api = PubAPI()
    ret = api.get_price(base_coin.upper(), quote.upper())
    return Decimal(ret)
