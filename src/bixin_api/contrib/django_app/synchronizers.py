import decimal

from bixin_api.contrib.django_app.config import get_client
from django.db import transaction

from .models import Deposit, BixinUser
from .registry import send_event


client = get_client()


def sync_transfer_to_deposit():
    resp = client.get_transfer_list(status='SUCCESS', limit=20, type='deposit', order='desc')
    for transfer in resp['items']:
        user_id = transfer['user.id']
        user = BixinUser.objects.filter(id=user_id).first()
        if user is None:
            raise ValueError(
                "Given user with user_id %s dost not exist" % user_id
            )
        deposit_id = transfer['args'].get('order_id')
        amount = decimal.Decimal(transfer['amount'])

        if not deposit_id:
            continue

        with transaction.atomic():
            try:
                deposit = Deposit.objects.select_for_update().get(
                    order_id=deposit_id,
                    user=user,
                )
            except Deposit.DoesNotExist:
                continue

            if deposit.status != 'PENDING':
                continue

            deposit.mark_as_succeed(amount=amount)
            deposit.save()
            send_event(deposit.order_id, "transfer_in", deposit.status)
