import json

import pytest

from centralauth.provider.models import ApplicationPermission

from ..factories import ApplicationFactory


@pytest.mark.django_db
class TestPermsEndpoint:

    def test_no_data(self, client):
        response = client.post(
            '/provider/perms/',
            content_type='application/json',
            secure=True)
        assert response.status_code == 403

    def test_incorrect_client_id(self, client):
        ApplicationFactory.create(
            client_id='app1', client_secret='secret1')
        response = client.post(
            '/provider/perms/',
            json.dumps({'client_id': 'foo', 'client_secret': 'secret1'}),
            content_type='application/json',
            secure=True)
        assert response.status_code == 403

    def test_incorrect_client_secret(self, client):
        ApplicationFactory.create(
            client_id='app1', client_secret='secret1')
        response = client.post(
            '/provider/perms/',
            json.dumps({'client_id': 'app1', 'client_secret': 'foo'}),
            content_type='application/json',
            secure=True)
        assert response.status_code == 403

    def test_permissions_synced(self, client):
        ApplicationFactory.create(
            client_id='app1', client_secret='secret1')

        # First permissions sync
        response = client.post(
            '/provider/perms/',
            json.dumps({
                'client_id': 'app1',
                'client_secret': 'secret1',
                'perms': [
                    {'app_label': 'label1', 'codename': 'codename1', 'repr': 'repr1'},
                    {'app_label': 'label2', 'codename': 'codename2', 'repr': 'repr2'},
                ],
            }),
            content_type='application/json',
            secure=True
        )

        assert response.status_code == 200
        response_json = response.json()
        assert response_json['success'] is True
        assert response_json['synced'] == 2
        assert response_json['created'] == 2
        assert response_json['count'] == ApplicationPermission.objects.count() == 2

        # Second permissions sync
        response = client.post(
            '/provider/perms/',
            json.dumps({
                'client_id': 'app1',
                'client_secret': 'secret1',
                'perms': [
                    {'app_label': 'label1', 'codename': 'codename1', 'repr': 'repr1'},
                    {'app_label': 'label2', 'codename': 'codename2', 'repr': 'repr2'},
                    {'app_label': 'label3', 'codename': 'codename3', 'repr': 'repr3'},
                ],
            }),
            content_type='application/json',
            secure=True)

        assert response.status_code == 200
        response_json = response.json()
        assert response_json['success'] is True
        assert response_json['synced'] == 3
        assert response_json['created'] == 1
        assert response_json['count'] == ApplicationPermission.objects.count() == 3
