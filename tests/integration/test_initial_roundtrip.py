import pytest
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch

from tests.factories import (
    ApplicationFactory, ApplicationPermissionFactory, ApplicationUserFactory, UserFactory)


User = get_user_model()


@pytest.mark.skip(reason='TODO: Fix me')
@pytest.mark.django_db
def test_initial_roundtrip(client, settings):
    user = UserFactory(username='foo', is_staff=True)
    user.set_password('bar')
    user.save()
    app = ApplicationFactory(
        client_id=settings.CENTRALAUTH_CLIENT_ID,
        client_secret=settings.CENTRALAUTH_CLIENT_SECRET,
        redirect_uris='https://testserver/client/login/callback/')
    perm = ApplicationPermissionFactory(
        application=app, codename='add_group', app_label='auth')
    app_user = ApplicationUserFactory(application=app, user=user)
    app_user.permissions.add(perm)

    # Start login process on client side. Expects redirect to provider.
    response = client.get('/client/login/?next=/foo/', secure=True)
    redirect = response['Location']
    assert '/provider/o/authorize/' in redirect

    # Authorize with provider. Expects redirect to login on provider.
    response = client.get(redirect, secure=True)
    redirect = response['Location']
    assert settings.LOGIN_URL in redirect

    # Login with provider. Expects redirect back to authorization endpoint
    data = {'username': user.username, 'password': 'bar'}
    response = client.post(redirect, data=data, secure=True)
    redirect = response['Location']
    assert '/provider/o/authorize/' in redirect

    # Authorize with provider and loggin in user.
    response = client.get(redirect, secure=True)
    redirect = response['Location']
    assert '/client/login/callback/' in redirect

    # Patch the request method in requests_oauthlib to use
    # the test client instead of doing a real request.
    def patched_oauthlib_request(method, url, **kwargs):
        client_method = getattr(client, method.lower())
        extra = {}
        data = kwargs.pop('data', '')
        headers = kwargs.pop('headers', {})
        headers.pop('Content-Type', None)
        for header, value in headers.items():
            extra[f'HTTP_{header.upper().replace("-", "_")}'] = value
        response = client_method(
            path=url, data=data,
            secure=True, **extra)
        response.request = Mock()
        response.text = response.content
        response.headers = {}
        response.raise_for_status = lambda: None
        return response

    # Finish login with client callback. Expects the client to fetch
    # an access_token, get the user details and update the user.
    redirect = redirect[redirect.index('/client/login/callback'):]
    with patch('requests_oauthlib.oauth2_session.requests.Session.request') as mock:
        mock.side_effect = patched_oauthlib_request
        response = client.get(redirect, secure=True)
        redirect = response['Location']
    user = User.objects.get(username='foo')
    assert user.get_all_permissions() == {'auth.add_group'}
    assert redirect == '/foo/'
    assert 'centralauth_token' in client.session
