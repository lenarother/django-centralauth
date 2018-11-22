import django
from django.utils.http import is_safe_url as django_is_safe_url


try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse  # noqa


try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    class MiddlewareMixin:
        pass


def is_authenticated(user):
    if django.VERSION[0:2] < (1, 10):
        return user.is_authenticated()

    return bool(user.is_authenticated)


def is_safe_url(url):
    if django.VERSION[0:2] < (1, 11):
        return django_is_safe_url(url)

    return django_is_safe_url(url, allowed_hosts=None)
