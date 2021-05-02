from importlib import import_module
from time import time

import pytest
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from unittest.mock import patch
from oauthlib.oauth2.rfc6749.errors import FatalClientError

from centralauth.client.middleware import CentralAuthSyncMiddleware
from centralauth.compat import is_authenticated

from .factories import UserFactory


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

        with patch('centralauth.client.services.load_token') as load_token_mock:
            result = CentralAuthSyncMiddleware().process_request(request)

        assert load_token_mock.called is False
        assert result is None

    def test_user_not_expired(self, rf):
        request = rf.get('/')
        request.user = UserFactory()
        request.session = session_engine.SessionStore()
        request.session['_auth_user_backend'] = 'centralauth.client.backends.OAuthBackend'
        request.session['centralauth_token'] = {'expires_at': time() + 60}

        with patch('centralauth.client.services.oauth2_client') as oauth_mock:
            result = CentralAuthSyncMiddleware().process_request(request)

        assert oauth_mock.called is False
        assert result is None
        assert is_authenticated(request.user) is True

    def test_user_expired_refresh_success(self, rf):
        request = rf.get('/')
        request.user = UserFactory()
        request.session = session_engine.SessionStore()
        request.session['_auth_user_backend'] = 'centralauth.client.backends.OAuthBackend'
        request.session['centralauth_token'] = {'expires_at': time() - 60}

        with patch('centralauth.client.services.sync_user') as sync_mock:
            sync_mock.return_value = True
            result = CentralAuthSyncMiddleware().process_request(request)

        assert sync_mock.call_count == 1
        assert result is None
        assert is_authenticated(request.user) is True

    def test_user_expired_refresh_failed(self, rf, settings):
        request = rf.get('/foo/')
        request.user = UserFactory()
        request.session = session_engine.SessionStore()
        request.session['_auth_user_backend'] = 'centralauth.client.backends.OAuthBackend'
        request.session['centralauth_token'] = {'expires_at': time() - 60}

        with patch('centralauth.client.services.sync_user') as sync_mock:
            sync_mock.return_value = False
            result = CentralAuthSyncMiddleware().process_request(request)

        assert sync_mock.call_count == 1
        assert is_authenticated(request.user) is False
        assert result['Location'] == settings.LOGIN_URL + '?next=/foo/'

    def test_user_expired_refresh_exception_retry_success(self, rf):
        request = rf.get('/foo/')
        request.user = UserFactory()
        request.session = session_engine.SessionStore()
        request.session['_auth_user_backend'] = 'centralauth.client.backends.OAuthBackend'
        request.session['centralauth_token'] = {'expires_at': time() + 60}
        request.session.save()

        request.session = session_engine.SessionStore(request.session.session_key)
        request.session['centralauth_token'] = {'expires_at': time() - 60}

        with patch('centralauth.client.services.sync_user') as sync_mock:
            sync_mock.side_effect = FatalClientError('invalid_grant')
            result = CentralAuthSyncMiddleware().process_request(request)

        assert sync_mock.call_count == 1
        assert result is None
        assert is_authenticated(request.user) is True

    def test_user_expired_refresh_exception_retry_fail(self, rf):
        request = rf.get('/foo/')
        request.user = UserFactory()
        request.session = session_engine.SessionStore()
        request.session['_auth_user_backend'] = 'centralauth.client.backends.OAuthBackend'
        request.session['centralauth_token'] = {'expires_at': time() - 60}

        with patch('centralauth.client.services.sync_user') as sync_mock:
            sync_mock.side_effect = FatalClientError('invalid_grant')
            result = CentralAuthSyncMiddleware().process_request(request)

        assert sync_mock.call_count == 3
        assert result.status_code == 302
        assert is_authenticated(request.user) is False
