import mock
import pytest
from django.contrib.auth import get_user_model

from centralauth.client.backends import OAuthBackend

from .factories import UserFactory


User = get_user_model()


@pytest.mark.django_db
class TestOAuthBackend:

    def test_get_user(self):
        user = UserFactory.create()
        backend = OAuthBackend()
        assert backend.get_user(user.pk) == user

    def test_get_user_does_not_exist(self):
        user = UserFactory.create()
        user_pk = user.pk
        user.delete()
        backend = OAuthBackend()
        assert backend.get_user(user_pk) is None

    @mock.patch('centralauth.client.services.user_details')
    def test_authenticate_failur(self, user_details_mock, rf):
        user_details_mock.return_value = None
        request = rf.get('/')
        backend = OAuthBackend()
        user = backend.authenticate(request, '12345')
        assert user is None

    @mock.patch('centralauth.client.services.user_details')
    def test_authenticate_create_new_user(self, user_details_mock, rf):
        user_details_mock.return_value = {
            'username': 'test.foobar'
        }
        request = rf.get('/')
        backend = OAuthBackend()
        user = backend.authenticate(request, '12345')
        assert isinstance(user, User)
        assert user.username == 'test.foobar'

    @mock.patch('centralauth.client.services.user_details')
    def test_authenticate_update_existing_user(self, user_details_mock, rf):
        user = UserFactory.create(username='Foo', first_name='Old First Name')
        users_count = User.objects.count()
        user_details_mock.return_value = {
            'username': 'Foo',
            'first_name': 'New First Name'
        }
        request = rf.get('/')
        backend = OAuthBackend()
        user = backend.authenticate(request, '12345')

        assert isinstance(user, User)
        assert user.username == 'Foo'
        assert user.first_name == 'New First Name'
        assert User.objects.count() == users_count
