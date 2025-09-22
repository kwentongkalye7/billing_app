from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models, transaction

from common.models import TimeStampedUserModel
from statements.models import BillingStatement


class Payment(TimeStampedUserModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        POSTED = "posted", "Posted"
        VERIFIED = "verified", "Verified"
        VOID = "void", "Void"

    class Method(models.TextChoices):
        CASH = "cash", "Cash"
        CHECK = "check", "Check"
        BPI = "bpi_transfer", "BPI Bank Transfer"
        BDO = "bdo_transfer", "BDO Bank Transfer"
        LBP = "lbp_transfer", "LBP Bank Transfer"
        GCASH = "gcash", "GCash"

    client = models.ForeignKey("clients.Client", on_delete=models.PROTECT, related_name="payments")
    payment_date = models.DateField()
    amount_received = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="PHP")
    method = models.CharField(max_length=20, choices=Method.choices)
    manual_invoice_no = models.CharField(max_length=50)
    reference_no = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    recorded_by = models.ForeignKey("accounts.User", related_name="payments_recorded", on_delete=models.PROTECT)
    verified_by = models.ForeignKey("accounts.User", related_name="payments_verified", on_delete=models.PROTECT, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-payment_date", "-created_at")

    def __str__(self):  # pragma: no cover
        return f"Payment {self.pk} — {self.client.name}"

    @property
    def allocated_amount(self) -> Decimal:
        return self.allocations.aggregate(total=models.Sum("amount_applied"))["total"] or Decimal("0.00")

    @property
    def delete(self, using=None, keep_parents=False):
        # Manually delete allocations so their hooks update statements
        for allocation in list(self.allocations.all()):
            allocation.delete()
        # Remove any related unapplied credits before deleting the payment
        self.unapplied_credits.all().delete()
        return super().delete(using=using, keep_parents=keep_parents)

    def clean(self):
        if self.currency != "PHP":
            raise ValidationError({"currency": "Only PHP currency is supported."})
        if self.amount_received <= 0:
            raise ValidationError({"amount_received": "Amount must be positive."})

    def mark_verified(self, actor):
        if self.status == self.Status.VERIFIED:
            return
        self.status = self.Status.VERIFIED
        self.verified_by = actor
        from django.utils import timezone

        self.verified_at = timezone.now()
        self.updated_by = actor
        self.save(update_fields=["status", "verified_by", "verified_at", "updated_by", "updated_at"])

    def void(self, actor, reason: str):
        if self.status == self.Status.VOID:
            return
        self.status = self.Status.VOID
        self.updated_by = actor
        self.notes = f"{self.notes}\nVoided: {reason}" if self.notes else f"Voided: {reason}"
        self.save(update_fields=["status", "notes", "updated_by", "updated_at"])
        # Rollback allocations
        for allocation in self.allocations.all():
            allocation.rollback(actor)


class PaymentAllocation(TimeStampedUserModel):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="allocations")
    billing_statement = models.ForeignKey(BillingStatement, on_delete=models.PROTECT, related_name="allocations")
    amount_applied = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ("payment", "billing_statement")

    def clean(self):
        if self.amount_applied <= 0:
            raise ValidationError({"amount_applied": "Allocation must be positive."})
        if self.payment.status == Payment.Status.VOID:
            raise ValidationError("Cannot allocate a void payment")
        if self.amount_applied > self.payment.remaining_unallocated + self._existing_amount():
            raise ValidationError("Allocation exceeds remaining payment amount")

    def _existing_amount(self) -> Decimal:
        if self.pk:
            return PaymentAllocation.objects.filter(pk=self.pk).values_list("amount_applied", flat=True).first() or Decimal("0.00")
        return Decimal("0.00")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.billing_statement.recalculate_totals(save=True)
        self.billing_statement.mark_settled_if_zero_balance(save=True)

    def delete(self, *args, **kwargs):
        statement = self.billing_statement
        super().delete(*args, **kwargs)
        statement.recalculate_totals(save=True)
        statement.mark_settled_if_zero_balance(save=True)

    def rollback(self, actor):
        statement = self.billing_statement
        self.delete()
        statement.updated_by = actor
        statement.save(update_fields=["updated_by", "updated_at"])


class UnappliedCredit(TimeStampedUserModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        APPLIED = "applied", "Applied"
        REFUNDED = "refunded", "Refunded"

    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE, related_name="unapplied_credits")
    source_payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="unapplied_credits")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)

    def mark_applied(self, actor):
        self.status = self.Status.APPLIED
        self.updated_by = actor
        self.save(update_fields=["status", "updated_by", "updated_at"])

    def mark_refunded(self, actor):
        self.status = self.Status.REFUNDED
        self.updated_by = actor
        self.save(update_fields=["status", "updated_by", "updated_at"])
