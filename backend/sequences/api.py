from __future__ import annotations

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdmin
from .models import Sequence
from .serializers import SequenceSerializer


class SequenceViewSet(viewsets.ModelViewSet):
    serializer_class = SequenceSerializer
    queryset = Sequence.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ["code", "reset_rule"]
    ordering_fields = ["code", "updated_at"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy", "next_number"}:
            return [IsAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def next_number(self, request, pk=None):
        sequence = self.get_object()
        number = sequence.next()
        return Response({"number": number})
