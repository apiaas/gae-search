from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^gae-login/$', views.gae_login, name='gae_login'),
    url(r'^users/$', views.user_list, name='user_list'),
    url(r'^users/(?P<user_id>[0-9]+)/$', views.user_detail, name='user_detail'),
)
