from __future__ import annotations

from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = AuditLogSerializer
    queryset = AuditLog.objects.select_related("actor").all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ["action", "entity_type", "actor"]
    search_fields = ["entity_id", "action", "metadata"]
    ordering_fields = ["created_at"]
