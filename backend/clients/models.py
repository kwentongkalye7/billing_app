from __future__ import annotations

from django.contrib.postgres.fields import ArrayField
from django.db import models

from common.models import TimeStampedUserModel


class Client(TimeStampedUserModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    name = models.CharField(max_length=255, unique=True)
    normalized_name = models.CharField(max_length=255, editable=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    billing_address = models.TextField(blank=True)
    tin = models.CharField(max_length=20, blank=True)
    tags = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    aliases = ArrayField(models.CharField(max_length=255), blank=True, default=list)
    group = models.CharField(max_length=255, blank=True)
    branding_logo = models.ImageField(upload_to="client_logos/", blank=True, null=True)
    branding_header_note = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.normalized_name = self.name.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):  # pragma: no cover - readability
        return self.name


class Contact(TimeStampedUserModel):
    class Roles(models.TextChoices):
        BILLING = "billing", "Billing"
        AP = "ap", "Accounts Payable"
        APPROVER = "approver", "Approver"
        OTHER = "other", "Other"

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="contacts")
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.OTHER)
    is_billing_recipient = models.BooleanField(default=False)

    class Meta:
        unique_together = ("client", "email", "phone")

    def __str__(self):  # pragma: no cover
        return f"{self.name} ({self.client.name})"
