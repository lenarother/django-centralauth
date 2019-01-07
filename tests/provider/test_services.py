import pytest

from centralauth.provider.services import get_perm_hash
from tests.factories import ApplicationPermissionFactory


@pytest.mark.django_db
class TestServices:

    def test_get_perm_hash(self):
        perm1 = ApplicationPermissionFactory.create(
            app_label='p1', codename='p1', repr='p1')
        perm2 = ApplicationPermissionFactory.create(
            application=perm1.application, app_label='p2', codename='p2',
            repr='p2')
        perm3 = ApplicationPermissionFactory.create(
            app_label='p1', codename='p1', repr='p1')

        assert get_perm_hash(perm1) == str(hash('p1-p1-p1'))
        assert get_perm_hash(perm1) == get_perm_hash(perm3)
        assert get_perm_hash(perm1) != get_perm_hash(perm2)
