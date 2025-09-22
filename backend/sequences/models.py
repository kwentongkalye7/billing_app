from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from django.db import models, transaction

from common.models import TimeStampedUserModel


class Sequence(TimeStampedUserModel):
    class ResetRule(models.TextChoices):
        NONE = "none", "No Reset"
        ANNUAL = "annual", "Annual"

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    prefix = models.CharField(max_length=20, default="SOA-")
    padding = models.PositiveSmallIntegerField(default=4)
    current_value = models.PositiveIntegerField(default=0)
    reset_rule = models.CharField(max_length=10, choices=ResetRule.choices, default=ResetRule.ANNUAL)
    last_reset_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ("code",)

    def __str__(self):  # pragma: no cover
        return f"{self.name} ({self.code})"

    @transaction.atomic
    def next(self) -> str:
        today = datetime.utcnow().date()
        if self.reset_rule == self.ResetRule.ANNUAL and self.last_reset_at and self.last_reset_at.year != today.year:
            self.current_value = 0
            self.last_reset_at = today
        self.current_value += 1
        if not self.last_reset_at:
            self.last_reset_at = today
        self.save(update_fields=["current_value", "last_reset_at", "updated_at"])
        return f"{self.prefix}{today.year}-{str(self.current_value).zfill(self.padding)}"

    @classmethod
    def assign_next(cls, code: str, actor=None) -> str:
        sequence, _ = cls.objects.get_or_create(
            code=code,
            defaults={
                "name": f"{code} Sequence",
                "created_by": actor,
                "updated_by": actor,
            },
        )
        if actor and not sequence.created_by:
            sequence.created_by = actor
        sequence.updated_by = actor
        sequence.save(update_fields=["updated_by", "updated_at"])
        return sequence.next()


@dataclass
class NumberSample:
    code: str
    example: str
