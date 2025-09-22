from __future__ import annotations

from rest_framework import serializers

from .models import Client, Contact


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            "id",
            "client",
            "name",
            "email",
            "phone",
            "role",
            "is_billing_recipient",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ClientSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = [
            "id",
            "name",
            "normalized_name",
            "status",
            "billing_address",
            "tin",
            "tags",
            "aliases",
            "group",
            "branding_logo",
            "branding_header_note",
            "contacts",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "normalized_name",
            "contacts",
            "created_at",
            "updated_at",
        ]
