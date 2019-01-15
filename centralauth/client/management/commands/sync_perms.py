from django.core.management.base import BaseCommand, CommandError
from django.utils import translation
from requests.exceptions import ConnectionError

from centralauth.client.services import register_perms


class Command(BaseCommand):
    help = 'Synchronise project permissions with the centralauth-provider.'

    def handle(self, *args, **options):
        translation.activate('en-us')

        try:
            response = register_perms()
            if response.status_code == 403:
                raise CommandError(
                    'Permissions endpoint returned 403. '
                    'Ensure you have apllication cleint_id and client_secret '
                    'set in your settings and client application with these '
                    'credentials exists on your provider server.')
            response_json = response.json()
        except ConnectionError:
            raise CommandError(
                'Could not connect to the provider perms endpoint. '
                'Check whether your centralauth provider server is running.')

        if not response_json['success']:
            self.stdout.write('Operation failed.')
            return

        self.stdout.write(
            'Operation successful. {0} permissions synced, {1} permissions '
            'created, {2} permissions deleted. Permissions count: {3}.'.format(
                response_json['synced'],
                response_json['created'],
                response_json['deleted'],
                response_json['count'],
            )
        )
