from __future__ import annotations

from datetime import date
from rest_framework import status, viewsets
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdminOrReviewer
from audit.utils import log_action
from common.utils import diff_model
from .models import BillingItem, BillingStatement
from .serializers import (
    BillingItemSerializer,
    BillingStatementSerializer,
    IssueStatementSerializer,
    VoidStatementSerializer,
)
from .pdf import render_statement_pdf


class BatchIssueSerializer(serializers.Serializer):
    statement_ids = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=False)
    issue_date = serializers.DateField()
    due_date = serializers.DateField()

    def validate(self, attrs):
        if attrs['due_date'] < attrs['issue_date']:
            raise serializers.ValidationError('Due date cannot be earlier than issue date')
        return attrs


class BillingStatementViewSet(viewsets.ModelViewSet):
    serializer_class = BillingStatementSerializer
    queryset = BillingStatement.objects.select_related("client", "engagement").prefetch_related("items")
    permission_classes = [IsAuthenticated]
    filterset_fields = ["client", "engagement", "status", "period"]
    search_fields = ["number", "client__name", "engagement__title", "notes"]
    ordering_fields = ["issue_date", "due_date", "sub_total", "balance", "created_at"]

    def perform_create(self, serializer):
        statement = serializer.save(created_by=self.request.user, updated_by=self.request.user)
        log_action(actor=self.request.user, action="statement.create", instance=statement)

    def perform_update(self, serializer):
        statement = self.get_object()
        before = diff_model(statement)
        statement = serializer.save(updated_by=self.request.user)
        log_action(actor=self.request.user, action="statement.update", instance=statement, before=before)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrReviewer])
    def submit_for_review(self, request, pk=None):
        statement = self.get_object()
        if statement.status != BillingStatement.Status.DRAFT:
            return Response({"detail": "Only draft statements can be submitted."}, status=status.HTTP_400_BAD_REQUEST)
        statement.status = BillingStatement.Status.PENDING_REVIEW
        statement.updated_by = request.user
        statement.save(update_fields=["status", "updated_by", "updated_at"])
        log_action(actor=request.user, action="statement.submit_for_review", instance=statement)
        return Response(self.get_serializer(statement).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrReviewer])
    def issue(self, request, pk=None):
        statement = self.get_object()
        serializer = IssueStatementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data
        issue_date = payload.get("issue_date", date.today())
        due_date = payload["due_date"]
        number = payload.get("number")
        statement.issue(actor=request.user, issue_date=issue_date, due_date=due_date, number=number)
        pdf_path = render_statement_pdf(statement)
        statement.pdf_path = pdf_path
        statement.save(update_fields=["pdf_path", "updated_at"])
        log_action(actor=request.user, action="statement.issue", instance=statement, metadata={"pdf_path": pdf_path})
        return Response(self.get_serializer(statement).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrReviewer])
    def void(self, request, pk=None):
        statement = self.get_object()
        serializer = VoidStatementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        statement.void(actor=request.user, reason=serializer.validated_data["reason"])
        log_action(actor=request.user, action="statement.void", instance=statement, metadata={"reason": serializer.validated_data["reason"]})
        return Response(self.get_serializer(statement).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], permission_classes=[IsAdminOrReviewer], url_path="batch-issue")
    def batch_issue(self, request):
        serializer = BatchIssueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        statements = BillingStatement.objects.select_related("client", "engagement").filter(id__in=data["statement_ids"])

        issued: list[int] = []
        skipped: list[int] = []
        for statement in statements:
            if statement.status not in {BillingStatement.Status.DRAFT, BillingStatement.Status.PENDING_REVIEW}:
                skipped.append(statement.id)
                continue
            try:
                statement.issue(actor=request.user, issue_date=data["issue_date"], due_date=data["due_date"])
                pdf_path = render_statement_pdf(statement)
                statement.pdf_path = pdf_path
                statement.save(update_fields=["pdf_path", "updated_at"])
                log_action(actor=request.user, action="statement.batch_issue", instance=statement, metadata={"batch": True, "pdf_path": pdf_path})
                issued.append(statement.id)
            except Exception:  # pragma: no cover - defensive safety
                skipped.append(statement.id)

        if issued:
            BillingStatement.objects.filter(id__in=issued).update(status=BillingStatement.Status.ISSUED)
        return Response({"issued": issued, "skipped": skipped}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def refresh_pdf(self, request, pk=None):
        statement = self.get_object()
        if statement.status != BillingStatement.Status.ISSUED:
            return Response({"detail": "Only issued statements have PDFs."}, status=status.HTTP_400_BAD_REQUEST)
        pdf_path = render_statement_pdf(statement, force_refresh=True)
        statement.pdf_path = pdf_path
        statement.updated_by = request.user
        statement.save(update_fields=["pdf_path", "updated_by", "updated_at"])
        log_action(actor=request.user, action="statement.refresh_pdf", instance=statement, metadata={"pdf_path": pdf_path})
        return Response({"pdf_path": pdf_path})



class BillingItemViewSet(viewsets.ModelViewSet):
    serializer_class = BillingItemSerializer
    queryset = BillingItem.objects.select_related("billing_statement").all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ["billing_statement"]
    ordering_fields = ["created_at"]

    def perform_create(self, serializer):
        statement_id = self.request.data.get("billing_statement")
        if not statement_id:
            raise ValueError("billing_statement id is required")
        statement = BillingStatement.objects.get(pk=statement_id)
        serializer.save(billing_statement=statement, created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
