from __future__ import annotations

from decimal import Decimal

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdmin, IsAdminOrBiller, IsAdminOrReviewer
from audit.utils import log_action
from common.utils import diff_model
from .models import Payment, PaymentAllocation, UnappliedCredit
from .serializers import (
    PaymentAllocationInputSerializer,
    PaymentAllocationSerializer,
    PaymentSerializer,
    UnappliedCreditSerializer,
)


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.select_related("client", "recorded_by", "verified_by").prefetch_related("allocations")
    permission_classes = [IsAuthenticated]
    filterset_fields = ["client", "status", "method", "payment_date"]
    search_fields = ["manual_invoice_no", "reference_no", "client__name"]
    ordering_fields = ["payment_date", "amount_received", "created_at"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update"}:
            return [IsAdminOrBiller()]
        if self.action in {"verify", "void"}:
            return [IsAdminOrReviewer()]
        if self.action in {"allocate"}:
            return [IsAdminOrBiller()]
        if self.action in {"destroy"}:
            return [IsAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        user = self.request.user
        payment = serializer.save(recorded_by=user, created_by=user, updated_by=user)
        log_action(actor=user, action="payment.create", instance=payment)

    def perform_update(self, serializer):
        payment = self.get_object()
        before = diff_model(payment)
        payment = serializer.save(updated_by=self.request.user)
        log_action(actor=self.request.user, action="payment.update", instance=payment, before=before)

    def perform_destroy(self, instance):
        snapshot = diff_model(instance)
        instance.delete()
        log_action(actor=self.request.user, action="payment.delete", instance=instance, before=snapshot)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrReviewer])
    def verify(self, request, pk=None):
        payment = self.get_object()
        payment.mark_verified(actor=request.user)
        log_action(actor=request.user, action="payment.verify", instance=payment)
        return Response(self.get_serializer(payment).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrReviewer])
    def void(self, request, pk=None):
        payment = self.get_object()
        reason = request.data.get("reason")
        if not reason:
            return Response({"detail": "Reason is required"}, status=status.HTTP_400_BAD_REQUEST)
        payment.void(actor=request.user, reason=reason)
        log_action(actor=request.user, action="payment.void", instance=payment, metadata={"reason": reason})
        return Response(self.get_serializer(payment).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrBiller], url_path="allocate")
    def allocate(self, request, pk=None):
        payment = self.get_object()
        payload = request.data.get("allocations", [])
        serializer = PaymentAllocationInputSerializer(data=payload, many=True)
        serializer.is_valid(raise_exception=True)
        payment.allocations.all().delete()
        for allocation in serializer.validated_data:
            PaymentAllocation.objects.create(
                payment=payment,
                billing_statement=allocation["billing_statement"],
                amount_applied=allocation["amount_applied"],
                created_by=request.user,
                updated_by=request.user,
            )
        payment.refresh_from_db()
        payment.unapplied_credits.all().delete()
        remaining = payment.remaining_unallocated
        if remaining > Decimal("0.00"):
            UnappliedCredit.objects.create(
                client=payment.client,
                source_payment=payment,
                amount=remaining,
                reason="Unallocated remainder",
                created_by=request.user,
                updated_by=request.user,
            )
        log_action(actor=request.user, action="payment.allocate", instance=payment, metadata={"remaining": str(remaining)})
        refreshed = PaymentSerializer(payment, context={"request": request})
        return Response(refreshed.data)


class PaymentAllocationViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentAllocationSerializer
    queryset = PaymentAllocation.objects.select_related("payment", "billing_statement")
    permission_classes = [IsAuthenticated]
    filterset_fields = ["payment", "billing_statement"]
    ordering_fields = ["created_at"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAdminOrBiller()]
        return super().get_permissions()

    def perform_create(self, serializer):
        allocation = serializer.save(created_by=self.request.user, updated_by=self.request.user)
        log_action(actor=self.request.user, action="allocation.create", instance=allocation)

    def perform_update(self, serializer):
        allocation = self.get_object()
        before = diff_model(allocation)
        allocation = serializer.save(updated_by=self.request.user)
        log_action(actor=self.request.user, action="allocation.update", instance=allocation, before=before)

    def perform_destroy(self, instance):
        log_action(actor=self.request.user, action="allocation.delete", instance=instance)
        super().perform_destroy(instance)


class UnappliedCreditViewSet(viewsets.ModelViewSet):
    serializer_class = UnappliedCreditSerializer
    queryset = UnappliedCredit.objects.select_related("client", "source_payment")
    permission_classes = [IsAuthenticated]
    filterset_fields = ["client", "status"]
    ordering_fields = ["created_at", "amount"]

    def get_permissions(self):
        if self.action in {"update", "partial_update", "destroy", "mark_applied", "mark_refunded"}:
            return [IsAdminOrReviewer()]
        return super().get_permissions()

    def perform_update(self, serializer):
        credit = serializer.save(updated_by=self.request.user)
        log_action(actor=self.request.user, action="unapplied.update", instance=credit)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrReviewer])
    def mark_applied(self, request, pk=None):
        credit = self.get_object()
        credit.mark_applied(actor=request.user)
        log_action(actor=request.user, action="unapplied.mark_applied", instance=credit)
        return Response(self.get_serializer(credit).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrReviewer])
    def mark_refunded(self, request, pk=None):
        credit = self.get_object()
        credit.mark_refunded(actor=request.user)
        log_action(actor=request.user, action="unapplied.mark_refunded", instance=credit)
        return Response(self.get_serializer(credit).data)
