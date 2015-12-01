from rest_framework import generics

from util.rest.mixins import DataStoreMixin, BaseMixin

from .models import Token
from .serializers import TokenSerializer


class TokenView(DataStoreMixin, generics.GenericAPIView):
    model = Token
    serializer_class = TokenSerializer

    @property
    def client(self):
        return self.request.user

    def set_model_id_type(self, id_string):
        return str(id_string)

    def get_queryset(self):
        return self.model.query(self.model.user == self.client.key)


class TokenList(TokenView, generics.ListCreateAPIView):
    pass


class TokenDetail(TokenView, generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'token'


token_list = TokenList.as_view()
token_detail = TokenDetail.as_view()
