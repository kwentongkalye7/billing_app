from django.contrib import admin

from .models import BillingItem, BillingStatement


class BillingItemInline(admin.TabularInline):
    model = BillingItem
    extra = 0


@admin.register(BillingStatement)
class BillingStatementAdmin(admin.ModelAdmin):
    list_display = ("number", "client", "engagement", "status", "period", "sub_total", "balance")
    search_fields = ("number", "client__name", "engagement__title")
    list_filter = ("status", "period")
    inlines = [BillingItemInline]


@admin.register(BillingItem)
class BillingItemAdmin(admin.ModelAdmin):
    list_display = ("billing_statement", "description", "qty", "unit_price", "line_total")
    search_fields = ("description",)
