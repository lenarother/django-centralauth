import re

import pytest
from django.test.client import Client

from ..factories import ApplicationFactory, ApplicationUserFactory


@pytest.mark.django_db
class TestAuthorizeRefresh:
    def get_token(self, client):
        app = ApplicationFactory.create(
            client_id='app1',
            client_secret='secret1',
            redirect_uris='http://localhost:9000/client/login/callback/',
        )
        app_user = ApplicationUserFactory.create(application=app)
        user = app_user.user

        assert client.login(username=user.username, password='secret') is True

        response = client.get(
            '/provider/o/authorize/',
            {
                'client_id': 'app1',
                'redirect_uri': 'http://localhost:9000/client/login/callback/',
                'response_type': 'code',
                'state': 'state123',
            },
        )
        code = re.match('.*code=([^&]+)', response['Location']).group(1)

        response = Client().post(
            '/provider/o/token/',
            {
                'client_id': 'app1',
                'client_secret': 'secret1',
                'redirect_uri': 'http://localhost:9000/client/login/callback/',
                'grant_type': 'authorization_code',
                'code': code,
            },
        )

        return (app, app_user, response.json())

    def test_authorize(self, client):
        app, app_user, token = self.get_token(client)
        user = app_user.user
        assert app.accesstoken_set.get(token=token['access_token']).user == user

    def test_refresh(self, client):
        app, app_user, token = self.get_token(client)
        user = app_user.user

        response = Client().post(
            '/provider/o/token/',
            {
                'client_id': 'app1',
                'client_secret': 'secret1',
                'grant_type': 'refresh_token',
                'refresh_token': token['refresh_token'],
            },
        )

        new_token = response.json()

        # Old token
        assert app.accesstoken_set.filter(token=token['access_token']).exists() is False
        assert app.refreshtoken_set.get(token=token['refresh_token']).revoked is not None

        # New token
        assert app.accesstoken_set.get(token=new_token['access_token']).user == user
        assert app.refreshtoken_set.get(token=new_token['refresh_token']).revoked is None

    def test_double_refresh(self, client):
        app, app_user, token = self.get_token(client)
        user = app_user.user

        # First refresh
        response = Client().post(
            '/provider/o/token/',
            {
                'client_id': 'app1',
                'client_secret': 'secret1',
                'grant_type': 'refresh_token',
                'refresh_token': token['refresh_token'],
            },
        )
        new_token1 = response.json()

        response = Client().post(
            '/provider/o/token/',
            {
                'client_id': 'app1',
                'client_secret': 'secret1',
                'grant_type': 'refresh_token',
                'refresh_token': token['refresh_token'],
            },
        )
        new_token2 = response.json()

        # New token 1
        assert app.accesstoken_set.get(token=new_token1['access_token']).user == user
        assert app.refreshtoken_set.get(token=new_token1['refresh_token']).revoked is None

        # New token 2 cannot be fetched
        assert new_token2['error'] == 'invalid_grant'
