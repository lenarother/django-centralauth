import pytest
from django.apps import apps as django_apps
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured


@pytest.mark.django_db
class TestClientConfig:

    def test_ready(self):
        assert django_apps.get_app_config('client').ready() is None

    def test_ready_no_middleware(self, settings):
        if hasattr(settings, 'MIDDLEWARE'):
            settings.MIDDLEWARE = list(settings.MIDDLEWARE)
            settings.MIDDLEWARE.remove(
                'centralauth.client.middleware.CentralAuthSyncMiddleware')
        elif hasattr(settings, 'MIDDLEWARE_CLASSES'):
            settings.MIDDLEWARE_CLASSES = list(settings.MIDDLEWARE_CLASSES)
            settings.MIDDLEWARE_CLASSES.remove(
                'centralauth.client.middleware.CentralAuthSyncMiddleware')
        with pytest.raises(ImproperlyConfigured):
            django_apps.get_app_config('client').ready()

    def test_default_login_template(self, settings):
        settings.CENTRALAUTH_CUSTOM_LOGIN_TEMPLATE = True
        django_apps.get_app_config('client').ready()
        assert admin.site.login_template == (
            'centralauth/client/client_login.html')

    def test_custom_login_template(self, settings):
        settings.CENTRALAUTH_CUSTOM_LOGIN_TEMPLATE = 'foo/bar.html'
        django_apps.get_app_config('client').ready()
        assert admin.site.login_template == 'foo/bar.html'
