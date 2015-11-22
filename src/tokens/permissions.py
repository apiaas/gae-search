from collections import namedtuple

from rest_framework.permissions import BasePermission

roles = namedtuple('Roles', 'create, delete, admin')(
    'create', 'delete', 'admin'
)


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        authenticated = request.user and request.user.is_authenticated()
        if not authenticated:
            return False

        permissions = request.auth and request.auth.permissions
        if permissions and roles.admin in permissions:
            return True
