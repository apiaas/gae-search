from django.conf.urls import patterns, url
from . import views


urlpatterns = patterns('',
    url(r'^tokens/$', views.token_list, name='tokens_list'),
    url(r'^tokens/(?P<token>[a-f0-9]{60})/$', views.token_detail, name='tokens_detail'),
)
