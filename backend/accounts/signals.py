from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import User


ROLE_GROUP_MAP = {
    User.Roles.ADMIN: "Admin",
    User.Roles.BILLER: "Biller",
    User.Roles.REVIEWER: "Reviewer",
    User.Roles.VIEWER: "Viewer",
}


@receiver(post_migrate)
def ensure_role_groups(sender, **kwargs):
    if sender.label != "accounts":
        return
    for role, label in ROLE_GROUP_MAP.items():
        Group.objects.get_or_create(name=label)
