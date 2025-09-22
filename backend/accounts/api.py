from __future__ import annotations

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import LoginSerializer, UserCreateSerializer, UserSerializer
from .permissions import IsAdmin


class UserViewSet(viewsets.ModelViewSet):
    """CRUD for application users with RBAC enforcement."""

    serializer_class = UserSerializer
    queryset = User.objects.all().order_by("username")
    permission_classes = [IsAuthenticated]
    search_fields = ["username", "display_name", "email", "first_name", "last_name"]
    ordering_fields = ["username", "date_joined", "last_login", "role"]

    def get_permissions(self):
        if self.action in {"create", "destroy", "set_password"}:
            return [IsAdmin()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def set_password(self, request, pk=None):
        user = self.get_object()
        password = request.data.get("password")
        if not password:
            return Response({"detail": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
        user.save(update_fields=["password"])
        return Response({"detail": "Password updated"})


class AuthViewSet(viewsets.ViewSet):
    """Session endpoints for login/logout/token rotation."""

    permission_classes = []

    def _build_response(self, payload):
        return Response(payload, status=status.HTTP_200_OK)

    def login(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        payload = serializer.save()
        return self._build_response(payload)

    def logout(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:  # pragma: no cover - best effort blacklist
                pass
        return Response({"detail": "Logged out"}, status=status.HTTP_205_RESET_CONTENT)
