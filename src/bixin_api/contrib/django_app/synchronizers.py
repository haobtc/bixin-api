import decimal
import logging
import time
from threading import Thread

from bixin_api.contrib.django_app.config import get_client
from django.db import transaction

from .models import Deposit, BixinUser, Withdraw
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
        send_event(deposit.order_id, deposit.order_type, deposit.status)


def execute_withdraw():
    pending_ids = Withdraw.get_pending_ids()

    for order_id, user_id in pending_ids:
        with transaction.atomic():
            try:
                withdraw = Withdraw.objects.select_for_update().get(
                    order_id=order_id,
                    user__id=user_id,
                )
            except Withdraw.DoesNotExist:
                continue

            if withdraw.status != 'PENDING':
                continue
            # TODO(winkidney): user may withdraw twice if the worker killed
            # This known issue should be fixed.
            try:
                client.send_withdraw(
                    withdraw.save()
                )
            except Exception:
                logging.exception(
                    "Failed to do withdraw (transfer-out) operation for %s" % withdraw,
                )
                withdraw.mark_as_failed()
            else:
                withdraw.mark_as_succeed()
        send_event(withdraw.order_id, withdraw.order_type, withdraw.status)


class StoppableThread(Thread):
    def __init__(self):
        super(StoppableThread, self).__init__()
        self._stopped = False
        self.setDaemon(True)

    def stop(self):
        self._stopped = True


class TransferSync(StoppableThread):

    def run(self):
        while not self._stopped:
            time.sleep(0.05)
            try:
                sync_transfer_to_deposit()
            except Exception:
                logging.exception(
                    "Failed to sync deposit orders:"
                )


class WithdrawExecutor(StoppableThread):

    def run(self):
        while not self._stopped:
            time.sleep(0.2)
            try:
                execute_withdraw()
            except Exception:
                logging.exception(
                    "Failed to sync deposit orders:"
                )
