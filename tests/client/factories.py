import factory
from django.contrib.auth import get_user_model


User = get_user_model()


class UserFactory(factory.DjangoModelFactory):
    username = factory.Faker('user_name')

    class Meta:
        model = User
