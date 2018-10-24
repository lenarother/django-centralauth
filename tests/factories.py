import factory
from django.contrib.auth import get_user_model

from centralauth.provider.models import (
    Application, ApplicationPermission, ApplicationPermissionGroup, ApplicationUser)


User = get_user_model()


class ApplicationFactory(factory.DjangoModelFactory):

    class Meta:
        model = Application


class UserFactory(factory.DjangoModelFactory):
    username = factory.Faker('user_name')

    class Meta:
        model = User


class ApplicationPermissionFactory(factory.DjangoModelFactory):
    application = factory.SubFactory(ApplicationFactory)
    app_label = 'foo'
    codename = factory.Sequence(lambda n: f'add_{n}')
    repr = factory.LazyAttribute(lambda o: f'{o.app_label} | add | {o.codename}')

    class Meta:
        model = ApplicationPermission


class ApplicationPermissionGroupFactory(factory.DjangoModelFactory):
    application = factory.SubFactory(ApplicationFactory)
    name = factory.Faker('text', max_nb_chars=255)

    class Meta:
        model = ApplicationPermissionGroup

    @factory.post_generation
    def permissions(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for permission in extracted:
                self.permissions.add(permission)


class ApplicationUserFactory(factory.DjangoModelFactory):
    application = factory.SubFactory(ApplicationFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = ApplicationUser

    @factory.post_generation
    def permissions(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for permission in extracted:
                self.permissions.add(permission)

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for group in extracted:
                self.groups.add(group)
