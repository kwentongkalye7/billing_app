from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdminOrReviewer
from .models import Engagement
from .serializers import EngagementSerializer
from .services import run_retainer_cycle


class EngagementViewSet(viewsets.ModelViewSet):
    serializer_class = EngagementSerializer
    queryset = Engagement.objects.select_related("client").all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ["client", "type", "status"]
    search_fields = ["title", "summary", "client__name", "tags"]
    ordering_fields = ["title", "client__name", "start_date", "status", "updated_at"]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAdminOrReviewer()]
        if self.action == "run_cycle":
            return [IsAdminOrReviewer()]
        return super().get_permissions()

    @action(detail=False, methods=["post"], url_path="run-cycle")
    def run_cycle(self, request):
        period = request.data.get("period")
        if not period:
            return Response({"detail": "`period` (YYYY-MM) is required"}, status=status.HTTP_400_BAD_REQUEST)
        summary = run_retainer_cycle(period=period, actor=request.user)
        return Response(summary, status=status.HTTP_202_ACCEPTED)
