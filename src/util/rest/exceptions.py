from rest_framework import exceptions


class ServiceUnavailable(exceptions.APIException):
    status_code = 503
    default_detail = 'Service temporarily unavailable, try again later.'
