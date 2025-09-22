from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Iterable, Optional

from django.db import models
from django.forms.models import model_to_dict


@dataclass
class Money:
    amount: Decimal
    currency: str = "PHP"

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:,.2f}"


def diff_model(instance: models.Model, fields: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    """Serialize model fields to a plain dict for audit logging."""

    opts = instance._meta
    field_names = fields or [f.name for f in opts.fields]
    data = model_to_dict(instance, field_names)
    data["id"] = getattr(instance, "id", None)
    return data
