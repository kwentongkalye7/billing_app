from rest_framework.permissions import BasePermission, SAFE_METHODS


class RolePermission(BasePermission):
    """Base permission that checks a user's role string."""

    allowed_roles: set[str] = set()

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_superuser:
            return True
        return request.user.role in self.allowed_roles


class IsAdmin(RolePermission):
    allowed_roles = {"admin"}


class IsAdminOrReviewer(RolePermission):
    allowed_roles = {"admin", "reviewer"}


class IsAdminOrBiller(RolePermission):
    allowed_roles = {"admin", "biller"}
