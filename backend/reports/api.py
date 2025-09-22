from __future__ import annotations

from datetime import date, datetime, timedelta

from django.db import models
from django.db.models import Case, DecimalField, Sum, Value, When
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from statements.models import BillingStatement
from payments.models import Payment, UnappliedCredit
from audit.models import AuditLog
from audit.serializers import AuditLogSerializer


class AgingReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        as_of_param = request.query_params.get("as_of")
        as_of = datetime.strptime(as_of_param, "%Y-%m-%d").date() if as_of_param else date.today()
        qs = BillingStatement.objects.filter(balance__gt=0, status__in=[BillingStatement.Status.ISSUED, BillingStatement.Status.PENDING_REVIEW])

        aging_case = Case(
            When(due_date__gte=as_of, then=Value("0-30")),
            When(due_date__lt=as_of, due_date__gte=as_of - timedelta(days=30), then=Value("0-30")),
            When(due_date__lt=as_of - timedelta(days=30), due_date__gte=as_of - timedelta(days=60), then=Value("31-60")),
            When(due_date__lt=as_of - timedelta(days=60), due_date__gte=as_of - timedelta(days=90), then=Value("61-90")),
            default=Value("90+"),
            output_field=models.CharField(),
        )
        report = (
            qs.annotate(bucket=aging_case)
            .values("bucket")
            .annotate(total_balance=Sum("balance", output_field=DecimalField(max_digits=14, decimal_places=2)))
            .order_by("bucket")
        )
        data = {row["bucket"]: row["total_balance"] or 0 for row in report}
        return Response({"as_of": as_of, "buckets": data})


class CollectionsRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        qs = Payment.objects.filter(status__in=[Payment.Status.POSTED, Payment.Status.VERIFIED])
        if start:
            qs = qs.filter(payment_date__gte=start)
        if end:
            qs = qs.filter(payment_date__lte=end)
        report = (
            qs.values("payment_date", "method")
            .annotate(total_amount=Sum("amount_received"))
            .order_by("payment_date", "method")
        )
        return Response({"rows": list(report)})


class UnappliedCreditReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = UnappliedCredit.objects.filter(status=UnappliedCredit.Status.OPEN)
        report = (
            qs.values("client__name")
            .annotate(total_amount=Sum("amount"))
            .order_by("client__name")
        )
        return Response({"rows": list(report)})


class AuditLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = AuditLog.objects.select_related("actor")[:500]
        serializer = AuditLogSerializer(qs, many=True)
        return Response(serializer.data)
