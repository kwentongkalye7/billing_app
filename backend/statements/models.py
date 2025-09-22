from __future__ import annotations

from decimal import Decimal
from typing import Optional

from django.db import models
from django.db.models import Sum

from common.models import TimeStampedUserModel


class BillingStatement(TimeStampedUserModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_REVIEW = "pending_review", "Pending Review"
        ISSUED = "issued", "Issued"
        VOID = "void", "Void"
        SETTLED = "settled", "Settled"

    number = models.CharField(max_length=50, unique=True, blank=True)
    client = models.ForeignKey("clients.Client", on_delete=models.PROTECT, related_name="billing_statements")
    engagement = models.ForeignKey("engagements.Engagement", on_delete=models.PROTECT, related_name="billing_statements")
    period = models.CharField(max_length=7, help_text="YYYY-MM")
    issue_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    currency = models.CharField(max_length=3, default="PHP")
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    pdf_path = models.CharField(max_length=255, blank=True)
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    paid_to_date = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    idempotency_hash = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("client", "engagement", "period")
        ordering = ("-issue_date", "-created_at")

    def __str__(self):  # pragma: no cover
        return self.number or f"Draft {self.client.name} {self.period}"

    @property
    def total_allocated(self) -> Decimal:
        from payments.models import PaymentAllocation  # Lazy import to avoid circular

        result = PaymentAllocation.objects.filter(billing_statement=self).aggregate(total=Sum("amount_applied"))
        return result["total"] or Decimal("0.00")

    def recalculate_totals(self, save: bool = False):
        subtotal = self.items.aggregate(total=Sum("line_total"))["total"] or Decimal("0.00")
        allocated = self.total_allocated
        self.sub_total = subtotal
        self.paid_to_date = allocated
        self.balance = subtotal - allocated
        if save:
            self.save(update_fields=["sub_total", "paid_to_date", "balance", "updated_at"])
        return self.balance

    def mark_settled_if_zero_balance(self, save: bool = True):
        self.recalculate_totals(save=False)
        if self.balance <= Decimal("0.00"):
            self.status = self.Status.SETTLED
        elif self.status == self.Status.SETTLED:
            self.status = self.Status.ISSUED
        if save:
            self.save(update_fields=["status", "sub_total", "paid_to_date", "balance", "updated_at"])

    def issue(self, actor, issue_date, due_date, number: Optional[str] = None):
        if self.status not in {self.Status.DRAFT, self.Status.PENDING_REVIEW}:
            raise ValueError("Only draft or pending statements can be issued")
        if not number:
            from sequences.models import Sequence

            number = Sequence.assign_next("SOA", actor=actor)
        self.number = number
        self.issue_date = issue_date
        self.due_date = due_date
        self.status = self.Status.ISSUED
        self.updated_by = actor
        self.save(update_fields=["number", "issue_date", "due_date", "status", "updated_by", "updated_at"])

    def void(self, actor, reason: str):
        if self.status == self.Status.VOID:
            return
        self.status = self.Status.VOID
        self.updated_by = actor
        self.notes = f"{self.notes}\nVoided: {reason}" if self.notes else f"Voided: {reason}"
        self.save(update_fields=["status", "updated_by", "notes", "updated_at"])


class BillingItem(TimeStampedUserModel):
    billing_statement = models.ForeignKey(BillingStatement, on_delete=models.CASCADE, related_name="items")
    description = models.TextField()
    qty = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("1.00"))
    unit = models.CharField(max_length=50, blank=True)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ("created_at",)

    def save(self, *args, **kwargs):
        self.line_total = (self.qty or Decimal("0.00")) * (self.unit_price or Decimal("0.00"))
        super().save(*args, **kwargs)
        self.billing_statement.recalculate_totals(save=True)

    def __str__(self):  # pragma: no cover
        return f"{self.description} — {self.line_total}"
