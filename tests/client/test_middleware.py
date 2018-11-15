from importlib import import_module
from time import time
from unittest.mock import patch

import pytest
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from centralauth.client.middleware import CentralAuthSyncMiddleware
from tests.factories import UserFactory


session_engine = import_module(settings.SESSION_ENGINE)


@pytest.mark.django_db
class TestCentralAuthSyncMiddleware:

    def test_no_user(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        result = CentralAuthSyncMiddleware().process_request(request)
        assert result is None

    def test_user_different_auth_backend(self, rf):
        request = rf.get('/')
        request.user = UserFactory()
        request.session = session_engine.SessionStore()
        request.session['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
        with patch('centralauth.client.services.load_token') as mock:
            result = CentralAuthSyncMiddleware().process_request(request)
        mock.assert_not_called()
        assert result is None

    def test_user_not_expired(self, rf):
        request = rf.get('/')
        request.user = UserFactory()
        request.session = session_engine.SessionStore()
        request.session['_auth_user_backend'] = 'centralauth.client.backends.OAuthBackend'
        request.session['centralauth_token'] = {'expires_at': time() + 60}
        with patch('centralauth.client.services.oauth2_client') as mock:
            result = CentralAuthSyncMiddleware().process_request(request)
        mock.assert_not_called()
        assert result is None

    def test_user_expired_refresh_success(self, rf):
        request = rf.get('/')
        request.user = UserFactory()
        request.session = session_engine.SessionStore()
        request.session['_auth_user_backend'] = 'centralauth.client.backends.OAuthBackend'
        request.session['centralauth_token'] = {'expires_at': time() - 60}
        with patch('centralauth.client.services.sync_user') as mock:
            mock.return_value = True
            result = CentralAuthSyncMiddleware().process_request(request)
        mock.assert_called()
        assert result is None

    def test_user_expired_refresh_failed(self, rf, settings):
        request = rf.get('/foo/')
        request.user = UserFactory()
        request.session = session_engine.SessionStore()
        request.session['_auth_user_backend'] = 'centralauth.client.backends.OAuthBackend'
        request.session['centralauth_token'] = {'expires_at': time() - 60}
        with patch('centralauth.client.services.sync_user') as mock:
            mock.return_value = False
            result = CentralAuthSyncMiddleware().process_request(request)
        mock.assert_called()
        assert result['Location'].startswith(settings.LOGIN_URL)
        assert 'next=/foo/' in result['Location']
        assert request.user.is_authenticated is False
