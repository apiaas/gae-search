from rest_framework.permissions import BasePermission
from google.appengine.api import users


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        authenticated = request.user and request.user.is_authenticated()
        if authenticated and request.user.is_super_admin:
            return True


class IsGAEOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        if users.is_current_user_admin():
            return True

        if IsSuperAdmin().has_permission(request, view):
            return True

