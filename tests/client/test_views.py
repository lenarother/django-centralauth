import pytest

from centralauth.client import views


class TestGetOAuthRedirectUrl:

    def test_simple(self, rf):
        request = rf.get('/', secure=True)
        redirect = views.get_oauth_redirect_url(request)
        assert redirect == 'https://testserver/client/login/callback/'

    def test_with_next(self, rf):
        request = rf.get('/', secure=True)
        redirect = views.get_oauth_redirect_url(request, next_url='/foo/')
        assert redirect == 'https://testserver/client/login/callback/?next=/foo/'

    def test_with_unsafe_next(self, rf):
        request = rf.get('/', secure=True)
        redirect = views.get_oauth_redirect_url(request, next_url='http://evil.com')
        assert redirect == 'https://testserver/client/login/callback/'


@pytest.mark.django_db
class TestLoginView:

    def test_get(self, client, settings):
        response = client.get('/client/login/', secure=True)
        assert response.status_code == 302
        assert response['Location'].startswith(settings.CENTRALAUTH_PROVIDER_URL)


@pytest.mark.django_db
class TestCallbackView:

    def test_forbidden(self, client, settings):
        response = client.get('/client/login/callback/', secure=True)
        assert response.status_code == 403
