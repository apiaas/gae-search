from google.appengine.ext import ndb
from rest_framework.authentication import TokenAuthentication as BaseTokenAuth
from rest_framework.authentication import (
    BaseAuthentication, CSRFCheck
)
from rest_framework import exceptions

from .models import Token


class TokenAuthentication(BaseTokenAuth):
    model = Token

    def authenticate_credentials(self, token_string):
        token = ndb.Key(Token, token_string).get()
        if not token:
            raise exceptions.AuthenticationFailed('Invalid token')

        user = token.user.get()
        if not user or not user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted')

        return user, token


class SessionAuthentication(BaseAuthentication):
    """
    Use Django's session framework for authentication.
    """

    def default_token(self):
        token = Token(
            key=ndb.Key(Token, 'session auth'),
            endpoint_path='/',
            permissions=['create', 'delete', 'admin']
        )
        return token

    def authenticate(self, request):
        """
        Returns a `User` if the request session currently has a logged in user.
        Otherwise returns `None`.
        """

        # Get the underlying HttpRequest object
        request = request._request
        user = getattr(request, 'user', None)

        # Unauthenticated, CSRF validation not required
        if not user or not user.is_active:
            return None

        self.enforce_csrf(request)

        # CSRF passed with authenticated user
        return user, self.default_token()

    def enforce_csrf(self, request):
        """
        Enforce CSRF validation for session based authentication.
        """
        reason = CSRFCheck().process_view(request, None, (), {})
        if reason:
            # CSRF failed, bail with explicit error message
            raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)
