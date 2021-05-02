from unittest import mock
import pytest

from centralauth.client.services import register_perms
from tests.factories import ApplicationFactory


@pytest.mark.django_db
class TestPermissionsSync:

    @mock.patch('centralauth.client.services.requests.post')
    @mock.patch('centralauth.client.services.Permission.objects.all')
    def test_perms_sync(self, perm_manager_mock, post_mock, settings, client):
        app = ApplicationFactory(
            client_id=settings.CENTRALAUTH_CLIENT_ID,
            client_secret=settings.CENTRALAUTH_CLIENT_SECRET,
            redirect_uris='https://testserver/client/login/callback/')

        class MockContentType:
            app_label = 'TestApp'

        class MockPerm:
            codename = 'Foo Bar'
            content_type = MockContentType()

            def __str__(self):
                return 'TestApp | Foo | Bar'

        mock_perm = MockPerm()
        perm_manager_mock.return_value = [mock_perm]
        register_perms()

        data = post_mock.call_args_list[0][1]['data']
        client.post(
            '/provider/perms/',
            data=data,
            content_type='application/json',
            secure=True)

        synced_perm = app.applicationpermission_set.first()

        assert app.applicationpermission_set.count() == 1
        assert synced_perm.app_label == 'TestApp'
        assert synced_perm.codename == 'Foo Bar'
        assert synced_perm.repr == 'TestApp | Foo | Bar'
