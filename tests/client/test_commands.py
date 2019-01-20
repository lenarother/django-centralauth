import sys

import mock
import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from requests.exceptions import ConnectionError


if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO


@pytest.mark.django_db
class TestSyncPerms:

    @mock.patch('centralauth.client.services.register_perms')
    def test_register_perms_called(self, register_perms_mock):
        class ResponseMock:
            status_code = 200
            result = {
                'success': True,
                'synced': 'foo',
                'created': 'bar',
                'deleted': 'fizz',
                'count': 'buzz',
            }

            def json(self):
                return self.result
        response = ResponseMock()

        out = StringIO()
        register_perms_mock.return_value = response
        call_command('sync_perms', stdout=out)
        assert register_perms_mock.call_count == 1
        message = out.getvalue()
        for expected in ['foo', 'bar', 'fizz', 'buzz']:
            assert expected in message

        out = StringIO()
        response.result['success'] = False
        register_perms_mock.return_value = response
        call_command('sync_perms', stdout=out)
        assert register_perms_mock.call_count == 2
        assert 'Operation failed.' in out.getvalue()

        response.status_code = 403
        register_perms_mock.return_value = response
        with pytest.raises(CommandError):
            call_command('sync_perms')
        assert register_perms_mock.call_count == 3

        register_perms_mock.side_effect = ConnectionError()
        with pytest.raises(CommandError):
            call_command('sync_perms')
        assert register_perms_mock.call_count == 4
