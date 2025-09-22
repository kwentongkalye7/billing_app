from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Role & Display", {"fields": ("role", "display_name")}),
    )
    list_display = ("username", "display_name", "role", "is_active", "email", "last_login")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "display_name", "email")
