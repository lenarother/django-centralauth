from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.views.generic.base import View
from requests_oauthlib import OAuth2Session

from . import constants, services
from ..compat import is_safe_url, reverse


OAUTH_STATE_KEY = 'oauth_state'


def get_oauth_redirect_url(request, next_url=None):
    path = reverse('centralauth_client:login-callback')
    if next_url and is_safe_url(next_url):
        path += '?next={}'.format(next_url)
    return request.build_absolute_uri(path)


class LoginView(View):
    """Request authorization code from provider.

    Set next url in session.
    Build authorization code request and redirect to provider server.
    """

    def get(self, *args, **kwargs):
        next_url = self.request.GET.get('next', None)

        oauth = OAuth2Session(
            client_id=settings.CENTRALAUTH_CLIENT_ID,
            redirect_uri=get_oauth_redirect_url(self.request, next_url),
        )
        authorization_url, state = oauth.authorization_url(
            constants.AUTHORISATION_ENDPOINT)

        self.request.session[OAUTH_STATE_KEY] = state

        return redirect(authorization_url)


class CallbackView(View):
    """Exchange authorization code for access token and authenticate user.

    Authenticate user with access token.
    Redirect to next_url or admin page.
    """

    def get(self, *args, **kwargs):
        grant_code = self.request.GET.get('code', None)
        state = self.request.GET.get('state', None)
        next_url = self.request.GET.get('next', None)

        state_ok = (state == self.request.session.get(OAUTH_STATE_KEY, ''))
        if not grant_code or not state or not state_ok:
            raise PermissionDenied

        oauth = OAuth2Session(
            client_id=settings.CENTRALAUTH_CLIENT_ID,
            redirect_uri=get_oauth_redirect_url(self.request, next_url),
            state=state,
        )
        token = oauth.fetch_token(
            token_url=constants.TOKEN_ENDPOINT,
            include_client_id=True,
            code=grant_code,
            client_secret=settings.CENTRALAUTH_CLIENT_SECRET,
        )

        user = authenticate(request=self.request, token=token)
        if user is None:
            raise PermissionDenied
        login(self.request, user)
        services.save_token(self.request.session, token)

        if next_url and is_safe_url(next_url):
            return redirect(next_url)
        return redirect(reverse('admin:index'))
