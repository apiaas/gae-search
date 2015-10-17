from django.conf.urls import include, patterns, url


urlpatterns = patterns('',
    url(r'', include('landing.urls')),
    url(r'', include('clients.urls')),
    url(r'', include('api.urls')),
    url(r'', include('tokens.urls')),
)
