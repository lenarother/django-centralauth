import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from centralauth.provider.models import (
    Application, ApplicationPermission, ApplicationPermissionGroup, ApplicationUser)


User = get_user_model()


class ApplicationFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Application


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker('user_name')

    class Meta:
        model = User

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        raw_password = kwargs.pop('raw_password', 'secret')
        if 'password' not in kwargs:
            kwargs['password'] = make_password(raw_password)
        return super()._adjust_kwargs(**kwargs)


class ApplicationPermissionFactory(factory.django.DjangoModelFactory):
    application = factory.SubFactory(ApplicationFactory)
    app_label = 'foo'
    codename = factory.Sequence(lambda n: f'add_{n}')
    repr = factory.LazyAttribute(lambda o: f'{o.app_label} | add | {o.codename}')

    class Meta:
        model = ApplicationPermission


class ApplicationPermissionGroupFactory(factory.django.DjangoModelFactory):
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


class ApplicationUserFactory(factory.django.DjangoModelFactory):
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
