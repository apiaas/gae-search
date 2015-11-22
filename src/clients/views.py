from collections import OrderedDict

from google.appengine.api import users
from django.contrib.auth import login, logout
from rest_framework import generics, status, views
from rest_framework.reverse import reverse
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from util.rest.mixins import DataStoreMixin, BaseMixin
from tokens.models import Token
from tokens.permissions import roles

from .models import User
from .serializers import UserSerializer, AuthViaEmailSerializer
from .permissions import IsGAEOrSuperAdmin


class UserView(DataStoreMixin, generics.GenericAPIView):
    permission_classes = (IsGAEOrSuperAdmin, )
    model = User
    serializer_class = UserSerializer
    queryset = User.query()


class UserList(UserView, generics.ListCreateAPIView):
    pass


class UserDetail(UserView, generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'user_id'


class UserLogin(BaseMixin, generics.GenericAPIView):
    serializer_class = AuthViaEmailSerializer
    permission_classes = (AllowAny, )

    def get_auth_string(self, request):
        return request.auth and ', '.join(request.auth.permissions) or ''

    def post(self, request, format=None):
        auth = self.get_serializer(data=request.data)
        if auth.is_valid():
            user = auth.validated_data['user']
            login(request, user)
            request.auth = Token(permissions=roles)
            return Response(
                OrderedDict(
                    [('user', unicode(request.user)),
                     ('auth', self.get_auth_string(request)),
                     ]
                )
            )

        return Response(auth.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        return Response(
            OrderedDict(
                [('user', unicode(request.user)),
                 ('auth', self.get_auth_string(request)),
                 ]
            )
        )


class UserLogout(views.APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, format=None):
        logout(request)
        return Response(status=status.HTTP_202_ACCEPTED)


class GAELogin(views.APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request, format=None):
        user = users.get_current_user()
        path = reverse('gae_login')
        logout_path = request.build_absolute_uri(
            users.create_logout_url(path)
        )
        if user:
            return Response(
                OrderedDict(
                    [('user', user.nickname()),
                     ('logout', logout_path),
                     ]
                )
            )

        login_path = request.build_absolute_uri(
            users.create_login_url(path)
        )
        return Response(
            OrderedDict(
                [('login', login_path)]
            )
        )


user_list = UserList.as_view()
user_detail = UserDetail.as_view()
user_login = UserLogin.as_view()
user_logout = UserLogout.as_view()
gae_login = GAELogin.as_view()
