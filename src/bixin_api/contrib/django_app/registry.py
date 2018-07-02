import logging

import django.dispatch

order_done = django.dispatch.Signal(
    providing_args=['order_id', 'order_type', 'order_status'],
)


order_callback_registry = set()


def register_callback(callback):
    if callback in order_callback_registry:
        return
    order_callback_registry.add(callback)


def send_event(order_id, order_type, order_status):
    order_done.send(
        sender="order_manager",
        order_id=order_id,
        order_type=order_type,
        order_status=order_status,
    )


def _call(sender, order_id=None, order_type=None, order_status=None, **kwargs):
    for fn in order_callback_registry:
        try:
            fn(order_id, order_status)
        except Exception:
            logging.exception(
                "Failed to call callback %s" % fn.__name__
            )


order_done.connect(_call, dispatch_uid="order_status_update")


__all__ = (
    'register_callback',
    'send_event',
)
