import json
import logging
from functools import partial
from time import time

import requests
from django.conf import settings
from django.contrib.auth.models import Permission
from requests_oauthlib import OAuth2Session

from . import constants


log = logging.getLogger('centralauth')


def serialize_perm(perm):
    """Serialize given permission object.

    Returns:
        dict: keys: app_lable, codename, repr.
    """
    return {
        'app_label': perm.content_type.app_label,
        'codename': perm.codename,
        'repr': str(perm),
    }


def register_perms():
    """Register permissions available in the project to the provider."""
    url = constants.REGISTER_PERMS_ENDPOINT
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = {
        'client_id': settings.CENTRALAUTH_CLIENT_ID,
        'client_secret': settings.CENTRALAUTH_CLIENT_SECRET,
        'perms': [serialize_perm(perm) for perm in Permission.objects.all()]
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response


def oauth2_client(token, session=None):
    kwargs = {}
    if session:
        kwargs.update({
            'auto_refresh_url': constants.REFRESH_ENDPOINT,
            'token_updater': partial(save_token, session=session),
            'auto_refresh_kwargs': {
                'client_id': settings.CENTRALAUTH_CLIENT_ID,
                'client_secret': settings.CENTRALAUTH_CLIENT_SECRET
            },
        })
    return OAuth2Session(client_id=settings.CENTRALAUTH_CLIENT_ID, token=token, **kwargs)


def save_token(session, token):
    session['centralauth_token'] = token


def load_token(session):
    token = session.get('centralauth_token', None)
    if token and 'expires_at' in token:
        token['expires_in'] = token['expires_at'] - time()
    return token


def sync_user(user, client):
    details = user_details(client)
    if not details:
        return False
    update_user(user, **details)
    return True


def user_details(client):
    try:
        response = client.get(constants.USER_ENDPOINT)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        log.exception('Failed to fetch user details')
        return None
    return response.json()


def update_user(user, **kwargs):
    """Update user attributes and permissions """
    permissions = kwargs.pop('permissions', [])
    allowed_attributes = (
        'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser'
    )
    for attr, value in kwargs.items():
        if attr in allowed_attributes and hasattr(user, attr):
            setattr(user, attr, value)
    user.save()

    updated_permissions = []
    for permission in permissions:
        updated_permissions.append(Permission.objects.get(
            content_type__app_label=permission[0], codename=permission[1]))
    user.user_permissions.clear()
    user.user_permissions.set(updated_permissions)
