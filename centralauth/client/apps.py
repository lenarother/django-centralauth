from django.apps import AppConfig
from django.conf import settings
from django.contrib import admin


class ClientConfig(AppConfig):
    name = 'centralauth.client'

    def ready(self):
        login_template = getattr(settings, 'CENTRALAUTH_CUSTOM_LOGIN_TEMPLATE', False)
        if login_template:
            admin.site.login_template = (
                login_template
                if not isinstance(login_template, bool)
                else 'centralauth/client/client_login.html'
            )
