# -*- coding: utf-8 -*-
import qrcode as qrcode
from bixin_api.contrib.django_app.decorators import require_debug
from bixin_api.event import make
from django.db import transaction

from .config import get_client_config, get_client
from django.http import HttpResponseNotAllowed, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from . import models


@csrf_exempt
def events_view(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(("POST",))
    aes_key = get_client_config()['aes_key']
    event = make(request.body, aes_key=aes_key)
    data = event.as_dict()
    event_id = data.pop('event_id')
    models.Event.objects.get_or_create(
        event_id=event_id,
        defaults=data,
    )
    return JsonResponse({})


def mk_qrcode(url):
    from io import BytesIO
    f = BytesIO()
    qrcode.make(url).save(f)
    f.seek(0)
    return f


@csrf_exempt
@transaction.atomic
@require_debug
def transfer_debug_qr_code(request):
    """
    Only work for debug.
    """
    from bixin_api.contrib.django_app.models import Deposit, BixinUser
    deposit = Deposit.objects.create(
        amount="0.001",
        symbol='ETH',
        user=BixinUser.objects.first(),
    )
    client = get_client()
    url = client.get_deposit_protocol(
        currency='ETH',
        amount='0.001',
        order_id=deposit.order_id,
    )
    image = mk_qrcode(url)
    resp = HttpResponse(
        content=image,
        content_type="image/png"
    )
    return resp


@require_debug
def transfer_out(request):
    from bixin_api.contrib.django_app.api import mk_transfer_out
    mk_transfer_out(
        user_id="1111111",
        symbol='BTC',
        amount=0.001,
    )
    return HttpResponse('done')
