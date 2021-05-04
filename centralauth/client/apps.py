from django.apps import AppConfig
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured


class ClientConfig(AppConfig):
    name = 'centralauth.client'

    def ready(self):
        if 'centralauth.client.middleware.CentralAuthSyncMiddleware' not in (
            getattr(settings, 'MIDDLEWARE', ()) or getattr(settings, 'MIDDLEWARE_CLASSES', ())
        ):
            raise ImproperlyConfigured(
                'You cannot use CentralAuth without installing '
                'centralauth.client.middleware.CentralAuthSyncMiddleware'
            )

        login_template = getattr(settings, 'CENTRALAUTH_CUSTOM_LOGIN_TEMPLATE', False)
        if login_template:
            admin.site.login_template = (
                login_template
                if not isinstance(login_template, bool)
                else 'centralauth/client/client_login.html'
            )
