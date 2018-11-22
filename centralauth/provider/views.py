import json

from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from oauth2_provider.views.generic import ProtectedResourceView

from .models import Application, ApplicationPermission, ApplicationUser


class UserEndpoint(ProtectedResourceView):
    """Endpoint for accessing user data.

    This endpoint can be accessed only with valid access token in header.
    """

    def get(self, request, *args, **kwargs):
        user = request.user
        token = request.META['HTTP_AUTHORIZATION'].split(' ')[1]
        application = user.oauth2_provider_accesstoken.get(token=token).application
        try:
            app_user = ApplicationUser.objects.get(
                user=user, application=application)
        except ApplicationUser.DoesNotExist:
            raise PermissionDenied

        return JsonResponse({
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_superuser': app_user.is_superuser,
            'is_staff': app_user.is_staff,
            'is_active': app_user.is_active,
            'permissions': app_user.get_permissions()
        })


class PermsEndpoint(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(PermsEndpoint, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        if not data.get('client_id', None) or not data.get('client_secret', None):
            raise PermissionDenied

        application = Application.objects.filter(
            client_id=data['client_id']).first()
        if not application or application.client_secret != data['client_secret']:
            raise PermissionDenied

        perms_data = data.get('perms', [])
        counter_created = 0
        for perm in perms_data:
            _, created = ApplicationPermission.objects.get_or_create(
                application=application,
                app_label=perm['app_label'],
                codename=perm['codename'],
                repr=perm['repr']
            )
            if created:
                counter_created += 1

        return JsonResponse({
            'success': True,
            'synced': len(perms_data),
            'created': counter_created,
            'count': application.applicationpermission_set.count(),
        })
