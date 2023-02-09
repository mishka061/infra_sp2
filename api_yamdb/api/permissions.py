from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminModeratorAuthorOrReadOnly(BasePermission):
    """Права аутентификации админа, модератора, автора."""
    def has_permission(self, request, view):
        return (
                request.method in SAFE_METHODS
                or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
                request.method in SAFE_METHODS
                or obj.author == request.user
                or request.user.is_moderator
                or request.user.is_admin
        )


class IsAdminOrReadOnly(BasePermission):
    """Определяет права аутентификации админа и пользователя."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.is_admin
        return False


class IsAdmin(BasePermission):
    """Определяет права на изменение только администратору."""
    def has_permission(self, request, view):
        return (
                request.user.is_admin
                or request.user.is_superuser
        )


