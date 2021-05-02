from time import time

from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from oauthlib.oauth2.rfc6749.errors import OAuth2Error

from centralauth.compat import MiddlewareMixin, is_authenticated

from . import services


class CentralAuthSyncMiddleware(MiddlewareMixin):
    def process_request(self, request, retries=0):
        if not is_authenticated(request.user):
            return

        backend = request.session.get('_auth_user_backend')
        if not backend == 'centralauth.client.backends.OAuthBackend':
            return

        if retries > 0:
            # We might have triggered a race condition (two refreshes in parallel).
            # We check if we have a "newer" token in the session.
            request.session['centralauth_token'] = request.session.load().get(
                'centralauth_token'
            )

        token = services.load_token(request.session) or {}
        if token.get('expires_at', 0) > time():
            return

        client = services.oauth2_client(token, request.session)
        try:
            ok = services.sync_user(request.user, client)
        except OAuth2Error:
            # An oauth error is raised if the refresh token was already used.
            # This might happen if the refresh is triggered twice.
            # We then retry 2 times.
            if retries < 2:
                return self.process_request(request, retries + 1)

            ok = False

        if not ok or not request.user.is_active:
            logout(request)
            return redirect('{0}?next={1}'.format(settings.LOGIN_URL, request.path))

        return None
