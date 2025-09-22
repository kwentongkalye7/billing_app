from __future__ import annotations

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from .dev_reset import reset_business_data


class DevResetView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not settings.DEBUG:
            return Response({"detail": "Dev reset is disabled."}, status=status.HTTP_403_FORBIDDEN)
        if request.user.role != User.Roles.ADMIN:
            return Response({"detail": "Admin role required."}, status=status.HTTP_403_FORBIDDEN)

        counts = reset_business_data()
        return Response({"status": "ok", "cleared": counts})
