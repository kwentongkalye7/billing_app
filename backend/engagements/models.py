from __future__ import annotations

from decimal import Decimal

from django.db import models

from common.models import TimeStampedUserModel


class Engagement(TimeStampedUserModel):
    class Types(models.TextChoices):
        RETAINER = "retainer", "Retainer"
        SPECIAL = "special", "Special"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        ENDED = "ended", "Ended"

    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE, related_name="engagements")
    type = models.CharField(max_length=20, choices=Types.choices)
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    recurrence = models.CharField(max_length=20, default="monthly")
    base_fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    default_description = models.TextField(blank=True)
    billing_day = models.PositiveSmallIntegerField(default=1, help_text="Day of month to issue retainer draft")
    tags = models.JSONField(default=list, blank=True)
    last_generated_period = models.CharField(max_length=7, blank=True, help_text="YYYY-MM of latest retainer draft")

    class Meta:
        unique_together = ("client", "title", "type")
        ordering = ("client__name", "title")

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.client.name} — {self.title}"

    @property
    def is_active(self) -> bool:
        return self.status == self.Status.ACTIVE

    @property
    def is_retainer(self) -> bool:
        return self.type == self.Types.RETAINER
