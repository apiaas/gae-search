from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^endpoints/$', views.endpoint_list, name='endpoint_list'),
    url(r'^endpoints/(?P<path>[^?#]+)/$', views.endpoint_details, name='endpoint_details'),
    url(r'^api/(?P<path>[^?#]+)/$', views.application_endpoint, name='application_endpoint'),
)
