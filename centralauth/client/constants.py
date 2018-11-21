from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def provider_url():
    url = getattr(settings, 'CENTRALAUTH_PROVIDER_URL', None)
    if not url:
        raise ImproperlyConfigured(
            'Centralauth requires CENTRALAUTH_PROVIDER_URL setting.')
    return url.rstrip('/')


PROVIDER_URL = provider_url()
USER_ENDPOINT = '{0}/user/'.format(PROVIDER_URL)
REGISTER_PERMS_ENDPOINT = '{0}/perms/'.format(PROVIDER_URL)
TOKEN_ENDPOINT = '{0}/o/token/'.format(PROVIDER_URL)
AUTHORISATION_ENDPOINT = '{0}/o/authorize/'.format(PROVIDER_URL)
REFRESH_ENDPOINT = '{0}/o/token/'.format(PROVIDER_URL)
