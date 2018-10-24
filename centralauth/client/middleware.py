from time import time

from django.conf import settings
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from . import services


class CentralAuthSyncMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if not request.user.is_authenticated:
            return
        backend = request.session.get('_auth_user_backend')
        if not backend == 'centralauth.client.backends.OAuthBackend':
            return
        token = services.load_token(request.session) or {}
        if token.get('expires_at', 0) > time():
            return
        client = services.oauth2_client(token, request.session)
        ok = services.sync_user(request.user, client)
        if not ok or not request.user.is_active:
            return redirect('{0}?next={1}'.format(settings.LOGIN_URL, request.path))
        return None
