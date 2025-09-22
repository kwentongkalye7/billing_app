from __future__ import annotations

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdmin, IsAdminOrReviewer
from .models import Client, Contact
from .serializers import ClientSerializer, ContactSerializer


class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    queryset = Client.objects.prefetch_related("contacts").all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "tags"]
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
