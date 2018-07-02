# BixinAPI

A python wrapper for `bixin-api`

## Feature

+ `BixinClient` for qr-code login
+ User info access
+ Basic data model for events/user-data
+ `Login` implementation with Redis backend

## install

`pip install bixin-api`

## Examples

Please view `examples/flask/app.py`

## ChangeLog

+ [ChangeLog](./ChangeLog.md)


## How to subscribe to deposit and withdraw order status change

Refer:

```
from bixin_api.contrib.django_app.api import (
    subscribe_transfer_event,
)

def fn(order_id, status):
    """
    :param status: 'SUCCESS' or 'FAILED'
    """
    pass

subscribe_transfer_event(fn)
```

