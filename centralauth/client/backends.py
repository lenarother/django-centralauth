from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from . import services


User = get_user_model()


class OAuthBackend(ModelBackend):
    """Authenticate user with OAuth access token."""

    def authenticate(self, request, token):
        client = services.oauth2_client(token)
        details = services.user_details(client)
        if not details:
            return None
        try:
            user = User.objects.get(username=details['username'])
        except User.DoesNotExist:
            user = User(username=details['username'])
            user.save()
        services.update_user(user, **details)
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
