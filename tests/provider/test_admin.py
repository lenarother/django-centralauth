import pytest

from centralauth.compat import reverse

from ..factories import (
    ApplicationFactory,
    ApplicationPermissionFactory,
    ApplicationPermissionGroupFactory,
    ApplicationUserFactory,
)


@pytest.mark.django_db
class TestApplicationAdmin:
    def setup(self):
        self.application = ApplicationFactory.create()

    def test_change_view(self, admin_client):
        group = ApplicationPermissionGroupFactory.create(application=self.application)
        ApplicationUserFactory.create(application=self.application, groups=[group])
        url = reverse(
            'admin:{}_{}_change'.format(
                self.application._meta.app_label, self.application._meta.model_name
            ),
            args=(self.application.pk,),
        )
        response = admin_client.get(url)

        # test fields
        form = response.context['adminform'].form
        fields = [name for name in form.fields.keys()]
        assert fields == (['name', 'client_id', 'client_secret', 'redirect_uris'])

        # test inlines visible
        inlines = response.context['inline_admin_formsets']
        assert len(inlines) == 1

        # test groups qs
        inline_forms = inlines[0].formset.forms
        assert inline_forms[0].fields['groups'].queryset.count() == 1
        ApplicationPermissionGroupFactory.create(application=self.application)
        ApplicationPermissionGroupFactory.create()
        assert inline_forms[0].fields['groups'].queryset.count() == 2

    def test_add_view(self, admin_client):
        url = reverse(
            'admin:{}_{}_add'.format(
                self.application._meta.app_label, self.application._meta.model_name
            )
        )
        response = admin_client.get(url)

        # test fields
        form = response.context['adminform'].form
        fields = [name for name in form.fields.keys()]
        assert fields == (['name', 'client_id', 'client_secret', 'redirect_uris'])

        # test inlines empty
        inlines = response.context['inline_admin_formsets']
        assert len(inlines) == 0


@pytest.mark.django_db
class TestApplicationPermissionGroupAdmin:
    def setup(self):
        self.perms_group = ApplicationPermissionGroupFactory.create()

    def test_change_view(self, admin_client):
        ApplicationUserFactory.create(
            application=self.perms_group.application,
        )
        ApplicationUserFactory.create()
        ApplicationPermissionFactory.create_batch(
            size=2, application=self.perms_group.application
        )
        ApplicationPermissionFactory.create_batch(size=3)

        url = reverse(
            'admin:{}_{}_change'.format(
                self.perms_group._meta.app_label, self.perms_group._meta.model_name
            ),
            args=(self.perms_group.pk,),
        )
        response = admin_client.get(url)

        # test fields
        form = response.context['adminform'].form
        fields = [name for name in form.fields.keys()]
        assert fields == ['name', 'users', 'permissions']

        # test users qs
        assert form.fields['users'].queryset.count() == 1

        # test perms qs
        assert form.fields['permissions'].queryset.count() == 2

    def test_add_view(self, admin_client):
        url = reverse(
            'admin:{}_{}_add'.format(
                self.perms_group._meta.app_label, self.perms_group._meta.model_name
            )
        )
        response = admin_client.get(url)

        # test fields
        form = response.context['adminform'].form
        fields = [name for name in form.fields.keys()]
        assert fields == ['name', 'application', 'users']

        # test users qs empty
        assert form.fields['users'].queryset.count() == 0


@pytest.mark.django_db
class TestApplicationUserAdmin:
    def setup(self):
        self.user = ApplicationUserFactory.create()

    def test_change_view(self, admin_client):
        ApplicationPermissionGroupFactory.create()
        ApplicationPermissionGroupFactory.create(application=self.user.application)

        url = reverse(
            'admin:{}_{}_change'.format(self.user._meta.app_label, self.user._meta.model_name),
            args=(self.user.pk,),
        )
        response = admin_client.get(url)

        # test fields
        form = response.context['adminform'].form
        fields = [name for name in form.fields.keys()]
        assert fields == ['is_superuser', 'is_staff', 'is_active', 'groups']

        # test groups qs
        assert form.fields['groups'].queryset.count() == 1

    def test_add_view(self, admin_client):
        url = reverse(
            'admin:{}_{}_add'.format(self.user._meta.app_label, self.user._meta.model_name)
        )
        response = admin_client.get(url)

        # test fields
        form = response.context['adminform'].form
        fields = [name for name in form.fields.keys()]
        assert fields == (['user', 'application', 'is_superuser', 'is_staff', 'is_active'])
