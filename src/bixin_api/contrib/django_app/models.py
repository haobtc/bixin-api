import uuid

from .fields import BixinDecimalField, JsonField
from django.db import models


def hex_uuid():
    return uuid.uuid4().hex


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class BixinUser(BaseModel):
    """
    Only stable properties will be stored here.
    """
    id = models.IntegerField(unique=True, primary_key=True)
    username = models.CharField(max_length=200, blank=True, null=True, default='')
    target_id = models.CharField(max_length=32, unique=True, null=True)
    openid = models.CharField(max_length=32, unique=True, null=True)


class Deposit(BaseModel):
    STATUS_CHOICES = [(x, x) for x in ['PENDING', 'SUCCESS']]

    order_id = models.CharField(default=hex_uuid, max_length=64, db_index=True)
    nonce = models.CharField(default=hex_uuid, max_length=64)
    symbol = models.CharField(max_length=32)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='PENDING')
    amount = BixinDecimalField(default=0)
    user = models.ForeignKey(
        BixinUser,
        on_delete=models.CASCADE,
        related_name='deposit'
    )

    @property
    def is_pending(self):
        return self.status != 'PENDING'

    def mark_as_succeed(self, amount=None):
        self.status = 'SUCCESS'
        if amount is not None:
            self.amount = amount


class Event(models.Model):
    STATUS_CHOICES = [(x, x) for x in ['RECEIVED', 'PROCESSED']]
    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        default='RECEIVED',
    )
    event_id = models.IntegerField(db_index=True)
    vendor_name = models.CharField(max_length=50)
    subject = models.CharField(max_length=32, db_index=True)
    payload = JsonField(null=True, blank=True, max_length=5000)
    uuid = models.CharField(max_length=50)

    def __str__(self):
        return '{}'.format(self.event_id)
