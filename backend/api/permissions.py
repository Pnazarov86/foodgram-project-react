from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Права админа."""

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_staff)


class IsAuthorOrAdminReadOnly(permissions.BasePermission):
    """Права автора и админиа."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and (
                request.user.is_admin
                or obj.author == request.user or request.method == 'POST'):
            return True
        return request.method in permissions.SAFE_METHODS
