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


def m2m_set_objects(m2m_target, new_set):
    old_objects = set(m2m_target.all())
    new_objects = []
    for obj in new_set:
        if obj in old_objects:
            old_objects.remove(obj)
        else:
            new_objects.append(obj)

    m2m_target.remove(*old_objects)
    m2m_target.add(*new_objects)
