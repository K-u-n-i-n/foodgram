from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrAdmin(BasePermission):
    """
    Кастомный класс разрешений, предоставляющий доступ
    автору объекта или администратору.

    """

    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True

        return request.user.is_authenticated and (
            request.user == obj.author or request.user.is_staff
        )
