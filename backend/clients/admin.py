from django.contrib import admin

from .models import Client, Contact


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "group", "tin")
    search_fields = ("name", "aliases", "group", "tin")
    list_filter = ("status", "group")


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "client", "role", "is_billing_recipient")
    search_fields = ("name", "email", "phone")
    list_filter = ("role", "is_billing_recipient")
