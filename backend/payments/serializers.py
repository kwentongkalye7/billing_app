from __future__ import annotations

from decimal import Decimal
from typing import List

from django.db import transaction
from rest_framework import serializers

from statements.models import BillingStatement
from .models import Payment, PaymentAllocation, UnappliedCredit


class PaymentAllocationInputSerializer(serializers.Serializer):
    billing_statement = serializers.PrimaryKeyRelatedField(queryset=BillingStatement.objects.all())
    amount_applied = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate(self, attrs):
        statement: BillingStatement = attrs["billing_statement"]
        if statement.status == BillingStatement.Status.VOID:
            raise serializers.ValidationError("Cannot allocate to a void statement")
        return attrs


class PaymentSerializer(serializers.ModelSerializer):
    allocations = PaymentAllocationInputSerializer(many=True, required=False)
    client_name = serializers.CharField(source="client.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    remaining_unallocated = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "client",
            "client_name",
            "payment_date",
            "amount_received",
            "currency",
            "method",
            "manual_invoice_no",
            "reference_no",
            "notes",
            "status",
            "status_display",
            "recorded_by",
            "verified_by",
            "verified_at",
            "allocations",
            "remaining_unallocated",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status_display",
            "verified_by",
            "verified_at",
            "remaining_unallocated",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "recorded_by": {"read_only": True},
        }

    def validate_method(self, value):
        allowed = {choice[0] for choice in Payment.Method.choices}
        if value not in allowed:
            raise serializers.ValidationError("Unsupported payment method")
        return value

    def validate_currency(self, value):
        if value != "PHP":
            raise serializers.ValidationError("Currency must be PHP")
        return value

    @transaction.atomic
    def create(self, validated_data):
        allocations: List[dict] = validated_data.pop("allocations", [])
        payment: Payment = Payment.objects.create(**validated_data)
        self._replace_allocations(payment, allocations)
        self._create_unapplied_credit_if_needed(payment)
        return payment

    @transaction.atomic
    def update(self, instance: Payment, validated_data):
        allocations = validated_data.pop("allocations", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if allocations is not None:
            instance.allocations.all().delete()
            self._replace_allocations(instance, allocations)
        self._create_unapplied_credit_if_needed(instance, replace_existing=True)
        return instance

    def _replace_allocations(self, payment: Payment, allocations_payload: List[dict]):
        actor = self.context["request"].user if "request" in self.context else None
        total_allocation = Decimal("0.00")
        for allocation in allocations_payload:
            statement: BillingStatement = allocation["billing_statement"]
            amount = allocation["amount_applied"]
            if amount <= 0:
                raise serializers.ValidationError("Allocation amount must be positive")
            PaymentAllocation.objects.create(
                payment=payment,
                billing_statement=statement,
                amount_applied=amount,
                created_by=actor,
                updated_by=actor,
            )
            total_allocation += amount
        if total_allocation > payment.amount_received:
            raise serializers.ValidationError("Total allocations exceed payment amount")

    def _create_unapplied_credit_if_needed(self, payment: Payment, replace_existing: bool = False):
        remaining = payment.remaining_unallocated
        if replace_existing:
            payment.unapplied_credits.all().delete()
        if remaining > Decimal("0.00"):
            actor = self.context["request"].user if "request" in self.context else None
            UnappliedCredit.objects.create(
                client=payment.client,
                source_payment=payment,
                amount=remaining,
                reason="Unallocated remainder",
                created_by=actor,
                updated_by=actor,
            )


class PaymentAllocationSerializer(serializers.ModelSerializer):
    billing_statement_number = serializers.CharField(source='billing_statement.number', read_only=True)

    class Meta:
        model = PaymentAllocation
        fields = [
            'id',
            'payment',
            'billing_statement',
            'billing_statement_number',
            'amount_applied',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'payment', 'billing_statement_number', 'created_at', 'updated_at']


class UnappliedCreditSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = UnappliedCredit
        fields = [
            'id',
            'client',
            'client_name',
            'source_payment',
            'amount',
            'reason',
            'status',
            'status_display',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'client_name', 'status_display', 'created_at', 'updated_at']
