from __future__ import annotations

from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Payment


@receiver(post_delete, sender=Payment)
def cleanup_unapplied(sender, instance: Payment, **kwargs):
    # Ensure dangling credits are removed if payment is deleted.
    instance.unapplied_credits.all().delete()
