import uuid
from collections import OrderedDict

from google.appengine.ext import ndb
from google.appengine.api import search
from django.http import Http404
from rest_framework import generics, views, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param

from util.rest.mixins import DataStoreMixin, BaseMixin
from .models import Endpoint
from .serializers import EndpointSerializer
from .permissions import StartsWithPathPermission, MethodPermission


class EndpointView(DataStoreMixin, generics.GenericAPIView):
    model = Endpoint
    serializer_class = EndpointSerializer

    @property
    def client(self):
        return self.request.user

    def get_queryset(self):
        return Endpoint.query(ancestor=self.client.key)


class EndpointList(EndpointView, generics.ListCreateAPIView):
    pass


class EndpointDetails(EndpointView, generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'path'


class SearchDocs(object):

    doc_types = {
        'text': search.TextField,
        'html': search.HtmlField,
        'atom': search.AtomField,
        'date': search.DateField,
        'number': search.NumberField,
        'geo': search.GeoField,
    }

    def get(self, value, name, doc_type=None):
        doc_type = doc_type or 'text'
        search_type = getattr(self, '_' + doc_type, self._text)
        return search_type(value=value, name=name)

    def _text(self, **kwargs):
        return search.TextField(**kwargs)

    def _html(self, **kwargs):
        return search.HtmlField(**kwargs)

    def _atom(self, **kwargs):
        return search.AtomField(**kwargs)

    def _date(self, **kwargs):
        return search.DateField(**kwargs)

    def _number(self, **kwargs):
        return search.NumberField(**kwargs)

    def _geo(self, value, **kwargs):
        latitude, longitude = [float(v) for v in value.split(',')]
        return search.GeoField(
            value=search.GeoPoint(latitude, longitude), **kwargs
        )

search_docs = SearchDocs()


def search_to_representation(value):
    if isinstance(value, search.GeoPoint):
        return 'geopoint(lat={}, long={})'.format(
            value.latitude, value.longitude
        )

    return value


class ApplicationEndpoint(BaseMixin, views.APIView):

    default_result_size = 20
    max_result_size = 100
    result_size_param = 'results'
    cursor_query_param = 'cursor'
    permission_classes = (
        IsAuthenticated, StartsWithPathPermission, MethodPermission
    )

    @property
    def endpoint(self):
        return self.kwargs['endpoint']

    @property
    def client(self):
        return self.request.user

    def initial_hook(self, request, *args, **kwargs):
        super(ApplicationEndpoint, self).initial_hook(request, *args, **kwargs)
        path_id = self.kwargs.get('path')
        key = ndb.Key(Endpoint, str(path_id), parent=self.client.key)
        endpoint = key.get()
        if endpoint:
            self.kwargs['endpoint'] = endpoint
            return

        raise Http404('Endpoint not found.')

    def get_cursor(self):
        c_str = self.request.query_params.get(self.cursor_query_param)
        if c_str:
            return search.Cursor(web_safe_string=c_str)

        return search.Cursor()

    def get_next_page_linc(self, cursor):
        if not cursor:
            return ''

        return replace_query_param(
            self.request.build_absolute_uri(),
            self.cursor_query_param,
            cursor.web_safe_string
        )

    def get_query_limit(self):
        limit = self.request.query_params.get(
            self.result_size_param, self.default_result_size
        )
        try:
            limit = int(limit)
        except (ValueError, TypeError):
            limit = self.default_result_size

        if limit > self.max_result_size:
            limit = self.max_result_size
        return limit

    def get_queryset(self):
        q = self.request.query_params.get('q', '')

        options = search.QueryOptions(
            cursor=self.get_cursor(),
            limit=self.get_query_limit(),
        )
        return search.Query(query_string=q, options=options)

    def get_index(self):
        name = '{}-{}'.format(
            self.endpoint.key.parent().id(),
            self.endpoint.key.id()
        )
        return search.Index(name=name)

    def parse_docs(self, docs):
        res = []
        for result in docs:
            item = OrderedDict()
            for field in result.fields:
                item[field.name] = search_to_representation(field.value)
            res.append(item)
        return res

    def get(self, *args, **kwargs):
        response_dict = OrderedDict()
        index = self.get_index()
        result = index.search(self.get_queryset())
        response_dict['next'] = self.get_next_page_linc(result.cursor)
        response_dict['results'] = self.parse_docs(result)
        return Response(response_dict)

    def delete(self, *args, **kwargs):
        index = self.get_index()
        result = index.search(self.get_queryset())
        ids = [doc.doc_id for doc in result]
        index.delete(ids)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def gen_doc_id(self):
        return str(uuid.uuid1())

    def post(self, request, *args, **kwargs):
        index = self.get_index()
        docs = list()
        for item in request.data:
            doc_id = self.gen_doc_id()
            fields = [search.AtomField(name='id', value=doc_id)]
            for field in item:
                fields.append(search_docs.get(
                    name=field['name'],
                    value=field['value'],
                    doc_type=field.get('type'))
                )
            docs.append(search.Document(doc_id=doc_id, fields=fields))
        index.put(docs)

        return Response(self.parse_docs(docs))


endpoint_details = EndpointDetails().as_view()
endpoint_list = EndpointList.as_view()
application_endpoint = ApplicationEndpoint.as_view()
