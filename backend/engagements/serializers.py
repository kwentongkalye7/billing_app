from __future__ import annotations

from rest_framework import serializers

from .models import Engagement


class EngagementSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", read_only=True)

    class Meta:
        model = Engagement
        fields = [
            "id",
            "client",
            "client_name",
            "type",
            "title",
            "summary",
            "status",
            "start_date",
            "end_date",
            "recurrence",
            "base_fee",
            "default_description",
            "billing_day",
            "tags",
            "last_generated_period",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["last_generated_period", "created_at", "updated_at"]

    def validate(self, attrs):
        if attrs.get("type") == Engagement.Types.RETAINER and attrs.get("base_fee") is None:
            raise serializers.ValidationError({"base_fee": "Retainer engagements require a base fee."})
        return attrs
