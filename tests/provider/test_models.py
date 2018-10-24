import pytest

from ..factories import (
    ApplicationFactory, ApplicationPermissionFactory, ApplicationPermissionGroupFactory,
    ApplicationUserFactory)


@pytest.mark.django_db
class TestApplicationPermission:

    def test_str(self):
        permission = ApplicationPermissionFactory.create(
            application__name='App', repr='foo | bar | bazz')
        assert str(permission) == 'App: foo | bar | bazz'


@pytest.mark.django_db
class TestApplicationPermissionGroup:

    def test_str(self):
        group = ApplicationPermissionGroupFactory.create(name='foobar')
        assert str(group) == 'foobar'


@pytest.mark.django_db
class TestApplicationUser:

    def test_str(self):
        app_user = ApplicationUserFactory.create(
            application__name='MyTestApp', user__username='foobar')
        assert str(app_user) == 'foobar (MyTestApp)'

    def test_get_permissions(self):
        app = ApplicationFactory.create()
        p1 = ApplicationPermissionFactory(
            application=app, app_label='al1', codename='cn1')
        p2 = ApplicationPermissionFactory(
            application=app, app_label='al2', codename='cn2')
        p3 = ApplicationPermissionFactory(
            application=app, app_label='al3', codename='cn3')
        g1 = ApplicationPermissionGroupFactory.create(
            application=app, permissions=[p2, p3])
        app_user = ApplicationUserFactory.create(
            application=app,
            permissions=[p1, p2],
            groups=[g1]
        )
        assert sorted(app_user.get_permissions()) == sorted(
            [('al1', 'cn1'), ('al2', 'cn2'), ('al3', 'cn3')])
