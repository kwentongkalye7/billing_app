from __future__ import annotations

from typing import Any, Dict, Optional

from django.db import transaction

from common.utils import diff_model
from .models import AuditLog



def _to_serializable(value):
    from datetime import date, datetime

    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _to_serializable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_serializable(v) for v in value]
    return value


@transaction.atomic
def log_action(*, actor, action: str, instance, before: Optional[Dict[str, Any]] = None, after: Optional[Dict[str, Any]] = None, metadata: Optional[Dict[str, Any]] = None):
    """Persist an audit entry for the given instance."""

    after_payload = after or diff_model(instance)
    AuditLog.objects.create(
        actor=actor,
        action=action,
        entity_type=instance._meta.label,
        entity_id=str(instance.pk),
        before=_to_serializable(before) if before else None,
        after=_to_serializable(after_payload) if after_payload else None,
        metadata=_to_serializable(metadata) if metadata else {},
    )
