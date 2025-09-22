from __future__ import annotations

from rest_framework import serializers

from .models import Sequence


class SequenceSerializer(serializers.ModelSerializer):
    sample_next = serializers.SerializerMethodField()

    class Meta:
        model = Sequence
        fields = [
            "id",
            "code",
            "name",
            "prefix",
            "padding",
            "current_value",
            "reset_rule",
            "last_reset_at",
            "sample_next",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "sample_next", "created_at", "updated_at"]

    def get_sample_next(self, obj: Sequence) -> str:
        preview = f"{obj.prefix}{obj.current_value + 1:0{obj.padding}}"
        return preview
