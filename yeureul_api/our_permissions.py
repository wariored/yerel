from rest_framework import permissions
class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Read only permissions if user is not superuser .
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser
