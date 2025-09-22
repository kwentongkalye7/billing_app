from __future__ import annotations

from datetime import date
from typing import List

from django.conf import settings
from django.db import transaction
from rest_framework import serializers

from .models import BillingItem, BillingStatement


class BillingItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingItem
        fields = [
            "id",
            "billing_statement",
            "description",
            "qty",
            "unit",
            "unit_price",
            "line_total",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "billing_statement", "line_total", "created_at", "updated_at"]


class BillingStatementSerializer(serializers.ModelSerializer):
    items = BillingItemSerializer(many=True, required=False)
    client_name = serializers.CharField(source="client.name", read_only=True)
    engagement_title = serializers.CharField(source="engagement.title", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = BillingStatement
        fields = [
            "id",
            "number",
            "client",
            "client_name",
            "engagement",
            "engagement_title",
            "period",
            "issue_date",
            "due_date",
            "currency",
            "notes",
            "status",
            "status_display",
            "pdf_path",
            "pdf_url",
            "sub_total",
            "paid_to_date",
            "balance",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "number",
            "status",
            "status_display",
            "pdf_path",
            "pdf_url",
            "sub_total",
            "paid_to_date",
            "balance",
            "created_at",
            "updated_at",
        ]

    def get_pdf_url(self, obj: BillingStatement) -> str | None:
        if not obj.pdf_path:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(settings.MEDIA_URL + obj.pdf_path)
        return settings.MEDIA_URL + obj.pdf_path

    @transaction.atomic
    def create(self, validated_data):
        items_data: List[dict] = validated_data.pop("items", [])
        statement = BillingStatement.objects.create(**validated_data)
        for item in items_data:
            BillingItem.objects.create(billing_statement=statement, **item)
        statement.recalculate_totals(save=True)
        return statement

    @transaction.atomic
    def update(self, instance: BillingStatement, validated_data):
        if instance.status == BillingStatement.Status.ISSUED and self.partial is False:
            raise serializers.ValidationError("Issued statements cannot be edited; void and reissue instead.")
        items_data = validated_data.pop("items", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_data is not None:
            instance.items.all().delete()
            for item in items_data:
                BillingItem.objects.create(billing_statement=instance, **item)
        instance.recalculate_totals(save=True)
        return instance


class IssueStatementSerializer(serializers.Serializer):
    issue_date = serializers.DateField(default=date.today)
    due_date = serializers.DateField()
    number = serializers.CharField(required=False)

    def validate(self, attrs):
        issue_date = attrs["issue_date"]
        due_date = attrs["due_date"]
        if due_date < issue_date:
            raise serializers.ValidationError("Due date cannot be earlier than issue date")
        return attrs


class VoidStatementSerializer(serializers.Serializer):
    reason = serializers.CharField()

    def validate_reason(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Reason must be at least 5 characters")
        return value
