import pytest
from oauth2_provider.exceptions import FatalClientError

from centralauth.provider.oauth2_backends import CentralauthOAuthBackend

from ..factories import ApplicationFactory, ApplicationUserFactory


@pytest.mark.django_db
class TestCentralauthOAuthBackend:

    def test_user_can_access_app(self, rf):
        backend = CentralauthOAuthBackend()
        test_app = ApplicationFactory.create(
            client_id='app1',
            client_secret='secret1',
            redirect_uris='http://localhost:9000/client/login/callback/')
        test_user = ApplicationUserFactory.create(application=test_app)
        test_user_no_access = ApplicationUserFactory.create()

        class OAuthLibRequestMock:
            client = test_app

        request = rf.get(
            '/provider/o/authorize/',
            {
                'esponse_type': 'code',
                'client_id': 'app1',
                'redirect_uri': 'http://localhost:9000/client/login/callback/',
                'state': 'state123',
            }
        )
        request.user = test_user.user

        # create_authorization_response success
        backend.create_authorization_response(
            request=request,
            scopes=['read', 'write'],
            credentials={
                'request': OAuthLibRequestMock,
                'redirect_uri': 'http://localhost:9000/client/login/callback/',
                'state': 'state123',
                'client_id': 'app1',
                'response_type': 'code',
            },
            allow=True
        )

        # create_authorization_response user has no permissions for app
        request.user = test_user_no_access.user
        with pytest.raises(FatalClientError):
            backend.create_authorization_response(
                request=request,
                scopes=['read', 'write'],
                credentials={
                    'request': OAuthLibRequestMock,
                    'redirect_uri': 'http://localhost:9000/client/login/callback/',
                    'state': 'state123',
                    'client_id': 'app1',
                    'response_type': 'code',
                },
                allow=True
            )
