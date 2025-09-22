from django.contrib import admin

from .models import Payment, PaymentAllocation, UnappliedCredit


class PaymentAllocationInline(admin.TabularInline):
    model = PaymentAllocation
    extra = 0


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "payment_date", "amount_received", "method", "status")
    list_filter = ("method", "status")
    search_fields = ("manual_invoice_no", "reference_no", "client__name")
    inlines = [PaymentAllocationInline]


@admin.register(UnappliedCredit)
class UnappliedCreditAdmin(admin.ModelAdmin):
    list_display = ("client", "amount", "status", "source_payment")
    list_filter = ("status",)
    search_fields = ("client__name",)


@admin.register(PaymentAllocation)
class PaymentAllocationAdmin(admin.ModelAdmin):
    list_display = ("payment", "billing_statement", "amount_applied")
    search_fields = ("payment__id", "billing_statement__number")
