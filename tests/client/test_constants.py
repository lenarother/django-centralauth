import pytest
from django.core.exceptions import ImproperlyConfigured

from centralauth.client.constants import provider_url


@pytest.mark.django_db
class TestConstants:
    def test_provider_url(self, settings):
        settings.CENTRALAUTH_PROVIDER_URL = 'http://provider.com/'
        assert provider_url() == 'http://provider.com'

    def test_no_provider_url(self, settings):
        settings.CENTRALAUTH_PROVIDER_URL = None
        with pytest.raises(ImproperlyConfigured):
            provider_url()
