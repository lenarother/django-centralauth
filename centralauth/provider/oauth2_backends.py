from django.utils.translation import ugettext
from oauth2_provider.exceptions import FatalClientError
from oauth2_provider.oauth2_backends import OAuthLibCore
from oauthlib.oauth2 import AccessDeniedError


class CentralauthOAuthBackend(OAuthLibCore):

    def create_authorization_response(self, request, scopes, credentials, allow):
        if not credentials['request'].client.applicationuser_set.filter(
            user=request.user
        ).exists():
            raise FatalClientError(error=AccessDeniedError(ugettext(
                'Your user account is not configured for the requested application.')))

        return super().create_authorization_response(request, scopes, credentials, allow)
