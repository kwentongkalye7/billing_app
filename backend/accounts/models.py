from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "admin", "Admin"
        BILLER = "biller", "Biller"
        REVIEWER = "reviewer", "Reviewer"
        VIEWER = "viewer", "Viewer"

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.VIEWER)
    display_name = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = self.get_full_name() or self.username
        super().save(*args, **kwargs)

    @property
    def permissions(self) -> dict[str, bool]:
        return {
            "can_issue": self.role in {self.Roles.ADMIN, self.Roles.REVIEWER},
            "can_void": self.role in {self.Roles.ADMIN, self.Roles.REVIEWER},
            "can_record_payments": self.role in {self.Roles.ADMIN, self.Roles.BILLER, self.Roles.REVIEWER},
            "is_admin": self.role == self.Roles.ADMIN,
        }

    def __str__(self) -> str:  # pragma: no cover - for readability
        return self.display_name or self.username
