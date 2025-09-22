from __future__ import annotations

from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source="actor.display_name", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "actor",
            "actor_name",
            "action",
            "entity_type",
            "entity_id",
            "before",
            "after",
            "metadata",
            "created_at",
        ]
        read_only_fields = fields
