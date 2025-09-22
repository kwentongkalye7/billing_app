from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from clients.models import Client
from engagements.models import Engagement
from engagements.services import run_retainer_cycle
from statements.models import BillingStatement


class RetainerCycleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="runner", password="password123", role=User.Roles.ADMIN)
        cls.client = Client.objects.create(name="Acme Corp", status=Client.Status.ACTIVE)
        cls.engagement = Engagement.objects.create(
            client=cls.client,
            type=Engagement.Types.RETAINER,
            title="Monthly Retainer",
            status=Engagement.Status.ACTIVE,
            start_date=timezone.now().date(),
            base_fee="10000.00",
        )

    def test_retainer_cycle_idempotent(self):
        period = "2025-09"
        summary = run_retainer_cycle(period=period, actor=self.user)
        self.assertEqual(summary["created"], 1)
        self.assertEqual(summary["skipped_existing"], 0)
        statement = BillingStatement.objects.get(engagement=self.engagement, period=period)
        self.assertEqual(statement.sub_total, statement.items.first().line_total)
        summary_second = run_retainer_cycle(period=period, actor=self.user)
        self.assertEqual(summary_second["created"], 0)
        self.assertEqual(summary_second["skipped_existing"], 1)
