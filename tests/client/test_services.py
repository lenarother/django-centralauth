from unittest import mock

import pytest

from centralauth.client.services import register_perms, serialize_perm


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
    def test_register_perms(
            self, perm_manager_mock, serialize_perm_mock, post_mock, settings):
        settings.CENTRALAUTH_CLIENT_ID = 'TEST_ID'
        settings.CENTRALAUTH_CLIENT_SECRET = 'TEST_SECRET'
        perm_manager_mock.return_value = [1, 2, 3]
        serialize_perm_mock.return_value = 'foo'

        register_perms()

        post_mock.assert_called_with(
            'https://localhost:8000/provider/perms/',
            data=(
                '{"client_id": "TEST_ID", "client_secret": "TEST_SECRET", '
                '"perms": ["foo", "foo", "foo"]}'),
            headers={
                'Content-type': 'application/json',
                'Accept': 'text/plain'}
        )


@pytest.mark.django_db
class TestServicesClient:
    pass


@pytest.mark.django_db
class TestServicesUser:
    pass
