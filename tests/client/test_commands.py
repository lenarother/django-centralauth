from unittest import mock

import pytest
from django.core.management import call_command


@pytest.mark.django_db
class TestSyncPerms:

    @mock.patch('centralauth.client.services.register_perms')
    def test_register_perms_called(self, register_perms_mock):
        call_command('sync_perms')
        assert register_perms_mock.call_count == 1
