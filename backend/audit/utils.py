from __future__ import annotations

from typing import Any, Dict, Optional

from django.db import transaction

from common.utils import diff_model
from .models import AuditLog


@transaction.atomic
def log_action(*, actor, action: str, instance, before: Optional[Dict[str, Any]] = None, after: Optional[Dict[str, Any]] = None, metadata: Optional[Dict[str, Any]] = None):
    """Persist an audit entry for the given instance."""

    AuditLog.objects.create(
        actor=actor,
        action=action,
        entity_type=instance._meta.label,
        entity_id=str(instance.pk),
        before=before,
        after=after or diff_model(instance),
        metadata=metadata or {},
    )
