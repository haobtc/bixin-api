import logging

from .config import get_client
from .models import Deposit, BixinUser, Withdraw


def get_vendor_address(symbol):
    client = get_client()
    address = client.get_first_vendor_address(currency=symbol)
    return address


def mk_transfer_in(user_id, symbol, amount, address=None):
    """
    数字货币还款/添加质押物
    """
    if address is None:
        address = get_vendor_address(symbol)
    deposit = Deposit.objects.create(
        amount=amount,
        symbol=symbol,
        user=BixinUser.objects.get(id=user_id),
        address=address,
    )
    return deposit.order_id, address


def mk_transfer_out(user_id, symbol, amount):
    withdraw = Withdraw.objects.create(
        address=None,
        symbol=symbol,
        amount=amount,
        user=BixinUser.objects.get(id=user_id)
    )
    return withdraw.order_id


def get_transfer_status(order_id):
    """
    :returns: 'SUCCESS' or 'PENDING'
    """
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

