from rest_framework.permissions import BasePermission, SAFE_METHODS
from tokens.permissions import roles

CREATE_METHODS = ('POST', )
DELETE_METHODS = ('DELETE', )


class StartsWithPathPermission(BasePermission):

    def has_permission(self, request, view):
        auth_path = request.auth and request.auth.endpoint_path
        if not auth_path:
            return False

        if auth_path == '/':
            return True

        path = view.kwargs.get('path')
        if not path:
            return False

        if str(path).startswith(auth_path.strip('/')):
            return True

        return False


class MethodPermission(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        permissions = request.auth and request.auth.permissions
        if not permissions:
            return False

        if request.method in CREATE_METHODS and roles.create in permissions:
            return True

        if request.method in DELETE_METHODS and roles.delete in permissions:
            return True
