import json
from unittest import mock

import pytest
import requests
from requests_oauthlib.oauth2_session import OAuth2Session

from centralauth.client.services import (
    load_token,
    oauth2_client,
    register_perms,
    save_token,
    serialize_perm,
    sync_user,
    update_user,
)

from .factories import UserFactory


@pytest.mark.django_db
class TestServicesPermissions:
    def test_serialize_perm(self):
        class MockContentType:
            app_label = 'TestApp'

        class MockPerm:
            codename = 'Foo Bar'
            content_type = MockContentType()

            def __str__(self):
                return 'TestApp | Foo | Bar'

        mock_perm = MockPerm()
        assert serialize_perm(mock_perm) == {
            'app_label': 'TestApp',
            'codename': 'Foo Bar',
            'repr': 'TestApp | Foo | Bar',
        }

    @mock.patch('centralauth.client.services.requests.post')
    @mock.patch('centralauth.client.services.serialize_perm')
    @mock.patch('centralauth.client.services.Permission.objects.all')
    def test_register_perms(self, perm_manager_mock, serialize_perm_mock, post_mock, settings):
        settings.CENTRALAUTH_CLIENT_ID = 'TEST_ID'
        settings.CENTRALAUTH_CLIENT_SECRET = 'TEST_SECRET'
        perm_manager_mock.return_value = [1, 2, 3]
        serialize_perm_mock.return_value = 'foo'

        register_perms()

        assert post_mock.call_args[0] == ('https://localhost:8000/provider/perms/',)
        assert json.loads(post_mock.call_args[1]['data']) == {
            'client_id': 'TEST_ID',
            'client_secret': 'TEST_SECRET',
            'perms': ['foo', 'foo', 'foo'],
        }
        assert post_mock.call_args[1]['headers'] == {
            'Content-type': 'application/json',
            'Accept': 'text/plain',
        }


@pytest.mark.django_db
class TestServicesClient:
    def test_oauth2_client_no_session(self, settings):
        settings.CENTRALAUTH_CLIENT_ID = 'FOOBAR'
        session = oauth2_client(token='abc')

        assert isinstance(session, OAuth2Session)
        assert session.token == 'abc'
        assert session.auto_refresh_url is None
        assert session.token_updater is None
        assert session.auto_refresh_kwargs == {}
        assert session.client_id == 'FOOBAR'

    @mock.patch(
        'centralauth.client.constants.REFRESH_ENDPOINT', 'https://provider.com/o/token/'
    )
    def test_oauth2_client_with_session(self, settings):
        settings.CENTRALAUTH_CLIENT_ID = 'FOOBAR'
        settings.CENTRALAUTH_CLIENT_SECRET = 'FOOBAR_SECRET'
        settings.CENTRALAUTH_PROVIDER_URL = 'https://provider.com'
        session = oauth2_client(token='cde', session='sth')

        assert isinstance(session, OAuth2Session)
        assert session.auto_refresh_url == 'https://provider.com/o/token/'
        assert callable(session.token_updater)
        assert session.auto_refresh_kwargs == {
            'client_id': 'FOOBAR',
            'client_secret': 'FOOBAR_SECRET',
        }
        assert session.client_id == 'FOOBAR'

    def test_save_token(self):
        session = {}
        save_token(session, '123')
        assert session['centralauth_token'] == '123'

    def test_load_token(self):
        session = {'centralauth_token': '567'}
        token = load_token(session)
        assert token == '567'

    def test_load_token_update_expires_in(self):
        session = {'centralauth_token': '567'}
        token = load_token(session)
        assert token == '567'

    @mock.patch('centralauth.client.services.time')
    def test_load_token_session_empty(self, time_mock):
        time_mock.return_value = 10
        session = {'centralauth_token': {'expires_at': 60}}
        token = load_token(session)
        assert token == {'expires_at': 60, 'expires_in': 50}


@pytest.mark.django_db
class TestServicesUser:
    @mock.patch('centralauth.client.services.user_details')
    @mock.patch('centralauth.client.services.update_user')
    def test_sync_user_success(self, update_user_mock, user_details_mock):
        user_details_mock.return_value = {'username': 'foo'}
        result = sync_user('user', 'client')
        assert update_user_mock.call_count == 1
        assert result is True

    @mock.patch('centralauth.client.services.update_user')
    def test_sync_user_failure(self, update_user_mock):
        client = mock.Mock()
        client.get.side_effect = requests.RequestException()
        result = sync_user('user', client)
        assert update_user_mock.call_count == 0
        assert result is False

    def test_user_details(self):
        pass

    def test_update_user_incorrect_attr_name(self):
        user = UserFactory.create()
        update_user(user, foo='foo')

    def test_update_user_clear_password(self):
        user = UserFactory.create()
        user.set_password('secret')
        assert user.check_password('secret') is True
        update_user(user)
        assert user.check_password('secret') is False

    def test_update_user_no_password(self):
        user = UserFactory.create()
        user.set_unusable_password()
        update_user(user)
        assert user.has_usable_password() is False
