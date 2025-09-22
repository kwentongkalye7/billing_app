from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from clients.models import Client
from engagements.models import Engagement
from statements.models import BillingStatement, BillingItem
from payments.models import Payment, PaymentAllocation, UnappliedCredit


class PaymentAllocationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="biller", password="password123", role=User.Roles.BILLER)
        self.client = Client.objects.create(name="Globex", status=Client.Status.ACTIVE)
        self.engagement = Engagement.objects.create(
            client=self.client,
            type=Engagement.Types.SPECIAL,
            title="Special Project",
            status=Engagement.Status.ACTIVE,
            start_date=timezone.now().date(),
        )
        self.statement = BillingStatement.objects.create(
            client=self.client,
            engagement=self.engagement,
            period="2025-08",
            status=BillingStatement.Status.ISSUED,
            currency="PHP",
            created_by=self.user,
            updated_by=self.user,
        )
        BillingItem.objects.create(
            billing_statement=self.statement,
            description="Services",
            qty=1,
            unit_price=Decimal("5000.00"),
            created_by=self.user,
            updated_by=self.user,
        )
        self.statement.refresh_from_db()

    def test_manual_allocation_and_unapplied_credit(self):
        payment = Payment.objects.create(
            client=self.client,
            payment_date=timezone.now().date(),
            amount_received=Decimal("6000.00"),
            currency="PHP",
            method=Payment.Method.CASH,
            manual_invoice_no="INV-001",
            recorded_by=self.user,
            created_by=self.user,
            updated_by=self.user,
        )
        PaymentAllocation.objects.create(
            payment=payment,
            billing_statement=self.statement,
            amount_applied=Decimal("5000.00"),
            created_by=self.user,
            updated_by=self.user,
        )
        self.statement.refresh_from_db()
        self.assertEqual(self.statement.balance, Decimal("0.00"))
        self.assertEqual(payment.remaining_unallocated, Decimal("1000.00"))
        credit = UnappliedCredit.objects.create(
            client=self.client,
            source_payment=payment,
            amount=payment.remaining_unallocated,
            reason="Overpayment",
            created_by=self.user,
            updated_by=self.user,
        )
        self.assertEqual(credit.amount, Decimal("1000.00"))
