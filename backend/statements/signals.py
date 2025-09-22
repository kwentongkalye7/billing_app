from __future__ import annotations

import hashlib

from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import BillingStatement


@receiver(pre_save, sender=BillingStatement)
def set_idempotency_hash(sender, instance: BillingStatement, **kwargs):
    raw = f"{instance.client_id}:{instance.engagement_id}:{instance.period}:{instance.sub_total}"
    instance.idempotency_hash = hashlib.sha256(raw.encode()).hexdigest()
