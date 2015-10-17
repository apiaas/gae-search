
from django.core.cache.backends.memcached import BaseMemcachedCache


class GaeMemcachedCache(BaseMemcachedCache):
    """
    An implementation of a cache binding using python-memcached
    """

    def __init__(self, server, params):
        from google.appengine.api import memcache
        super(GaeMemcachedCache, self).__init__(server, params,
                                                library=memcache,
                                                value_not_found_exception=ValueError)
