from __future__ import annotations

from rest_framework import viewsets

import django_filters
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdmin, IsAdminOrReviewer
from .models import Client, Contact
from .serializers import ClientSerializer, ContactSerializer


class ClientFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(method="filter_tags")

    class Meta:
        model = Client
        fields = ["status", "tags"]

    def filter_tags(self, queryset, name, value):
        if not value:
            return queryset
        values = [v.strip() for v in value.split(",") if v.strip()]
        if not values:
            return queryset
        for val in values:
            queryset = queryset.filter(tags__contains=[val])
        return queryset


class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    queryset = Client.objects.prefetch_related("contacts").all()
    permission_classes = [IsAuthenticated]
    filterset_class = ClientFilter
    search_fields = ["name", "normalized_name", "aliases", "group", "tags"]
    ordering_fields = ["name", "status", "created_at", "updated_at"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAdminOrReviewer()]
        return super().get_permissions()


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    queryset = Contact.objects.select_related("client").all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ["client", "is_billing_recipient"]
    search_fields = ["name", "email", "phone"]
    ordering_fields = ["name", "client__name", "created_at"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAdminOrReviewer()]
        return super().get_permissions()
