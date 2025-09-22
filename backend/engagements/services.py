from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict

from django.db import transaction

from accounts.models import User
from clients.models import Client
from statements.models import BillingStatement, BillingItem
from .models import Engagement


@dataclass
class CycleSummary:
    created: int
    skipped_existing: int

    def as_dict(self) -> Dict[str, int]:
        return {"created": self.created, "skipped_existing": self.skipped_existing}


def last_day_of_month(period: str) -> date:
    year, month = map(int, period.split("-"))
    if month == 12:
        return date(year, month, 31)
    next_month = date(year, month + 1, 1)
    return next_month - timedelta(days=1)


def run_retainer_cycle(period: str, actor: User) -> Dict[str, int]:
    """Generate draft billing statements for active retainer engagements."""

    if len(period) != 7 or period[4] != "-":
        raise ValueError("Period must be in YYYY-MM format")

    created = 0
    skipped = 0
    due_date = last_day_of_month(period)

    engagements = Engagement.objects.select_related("client").filter(
        type=Engagement.Types.RETAINER,
        status=Engagement.Status.ACTIVE,
        client__status=Client.Status.ACTIVE,
    )

    for engagement in engagements:
        result = _create_retainer_statement_if_missing(engagement, period, due_date, actor)
        if result:
            created += 1
        else:
            skipped += 1

    return CycleSummary(created=created, skipped_existing=skipped).as_dict()


@transaction.atomic
def _create_retainer_statement_if_missing(engagement: Engagement, period: str, due_date: date, actor: User) -> bool:
    statement, created = BillingStatement.objects.get_or_create(
        client=engagement.client,
        engagement=engagement,
        period=period,
        defaults={
            "status": BillingStatement.Status.DRAFT,
            "currency": "PHP",
            "due_date": due_date,
            "created_by": actor,
            "updated_by": actor,
        },
    )
    if not created:
        return False

    description = engagement.default_description or f"Retainer services for {period}"
    BillingItem.objects.create(
        billing_statement=statement,
        description=description,
        qty=1,
        unit="month",
        unit_price=engagement.base_fee,
        line_total=engagement.base_fee,
        created_by=actor,
        updated_by=actor,
    )
    statement.recalculate_totals(save=True)
    engagement.last_generated_period = period
    engagement.updated_by = actor
    engagement.save(update_fields=["last_generated_period", "updated_by", "updated_at"])
    return True
