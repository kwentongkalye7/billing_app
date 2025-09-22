from __future__ import annotations

from django.db import models

from common.models import TimeStampedModel


class AuditLog(TimeStampedModel):
    actor = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50)
    entity_type = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=100)
    before = models.JSONField(null=True, blank=True)
    after = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):  # pragma: no cover
        return f"{self.action} {self.entity_type}#{self.entity_id}"
