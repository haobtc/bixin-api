from bixin_api.contrib.django_app.config import get_client
from bixin_api.contrib.django_app.models import Deposit, BixinUser


def get_vendor_address(symbol):
    client = get_client()
    address = client.get_first_vendor_address(currency=symbol)
    return address


def mk_transfer_in(user_id, symbol, amount, address=None, type='transfer_in'):
    if address is None:
        address = get_vendor_address(symbol)
    deposit = Deposit.objects.create(
        amount=amount,
        symbol=symbol,
        user=BixinUser.objects.get(id=user_id),
        address=address,
    )
    return deposit.order_id


def get_transfer_status(order_id):
    """
    :returns: 'SUCCESS' or 'PENDING'
    """
    deposit = Deposit.objects.get(order_id=order_id)
    return deposit.status


def subscribe_transfer_event(callback):
    """
    callback(order_id, order_status)
    order_status will be 'SUCCESS' or 'FAILED'
    """
    return
