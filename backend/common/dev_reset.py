from __future__ import annotations

from typing import Dict

from django.db import connection

from audit.models import AuditLog
from clients.models import Client, Contact
from engagements.models import Engagement
from payments.models import Payment, PaymentAllocation, UnappliedCredit
from sequences.models import Sequence
from statements.models import BillingItem, BillingStatement


BUSINESS_MODELS = {
    "payments": [PaymentAllocation, UnappliedCredit, Payment],
    "statements": [BillingItem, BillingStatement],
    "engagements": [Engagement],
    "clients": [Contact, Client],
    "audit": [AuditLog],
    "sequences": [Sequence],
}


TRUNCATE_TABLES = [
    "payments_paymentallocation",
    "payments_unappliedcredit",
    "payments_payment",
    "statements_billingitem",
    "statements_billingstatement",
    "engagements_engagement",
    "clients_contact",
    "clients_client",
    "audit_auditlog",
    "sequences_sequence",
]


def reset_business_data() -> Dict[str, int]:
    """Delete all business data while keeping auth/users intact."""

    counts = {}
    for label, models in BUSINESS_MODELS.items():
        counts[label] = sum(model.objects.count() for model in models)

    sql = "TRUNCATE TABLE {} RESTART IDENTITY CASCADE;".format(
        ", ".join(TRUNCATE_TABLES)
    )
    with connection.cursor() as cursor:
        cursor.execute(sql)

    return counts
