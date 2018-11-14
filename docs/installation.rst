Installation
============

* Install with pip::

    pip install django-centralauth


Provider side
-------------

You need to update some of your Django settings.

* Your ``INSTALLED_APPS`` setting::

    INSTALLED_APPS = (
        # ...
        'oauth2_provider',
        'centralauth.provider',
    )

* Your ``MIDDLEWARE`` setting::

    MIDDLEWARE = [
        'oauth2_provider.middleware.OAuth2TokenMiddleware',
        # ...
    ]

* Your ``AUTHENTICATION_BACKENDS`` setting::

    AUTHENTICATION_BACKENDS = (
        'oauth2_provider.backends.OAuth2Backend',
        # ...
    )


* Add the following settings in addition::

    OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL = 'oauth2_provider.AccessToken'
    OAUTH2_PROVIDER_APPLICATION_MODEL = 'provider.Application'

* Configure the OAuth2 provider backend class::

    OAUTH2_PROVIDER = {
        'OAUTH2_BACKEND_CLASS': 'centralauth.provider.oauth2_backends.CentralauthOAuthBackend',
    }

If you want to re-validate the access more often, you might redurce the lifetime
of the generated access tokens::

    OAUTH2_PROVIDER = {
        # ...
        'ACCESS_TOKEN_EXPIRE_SECONDS': 5 * 60,
    }

After you updated your settings, add the ``centralauth.provider`` urls to your
url configuration::

    urlpatterns = [
        # ...
        path('provider/', include('centralauth.provider.urls'))
    ]

.. note::

    Make sure that you configure a sane ``LOGIN_URL``. django-oauth-toolkit will
    redirect users to this url to ensure the requesting user is logged in.


Client side
-----------

You need to update some of your Django settings.

* Your ``INSTALLED_APPS`` setting::

    INSTALLED_APPS = (
        # ...
        'centralauth.client',
    )

* Your ``AUTHENTICATION_BACKENDS`` setting::

    # Disable regular logins using local users and enforce centralauth logins.
    AUTHENTICATION_BACKENDS = (
        'centralauth.client.backends.OAuthBackend'
    )


* Add the following settings in addition::

    # The full uri to the provider side urls.
    CENTRALAUTH_PROVIDER_URL = 'http://localhost:8000/provider'

    # The application credentials generated on the provider side using the Django admin.
    CENTRALAUTH_CLIENT_ID = 'ADD-YOUR-CLIENT-ID'
    CENTRALAUTH_CLIENT_SECRET = 'ADD-YOUR-CLIENT-SECRET'


After you updated your settings, add the ``centralauth.client`` urls to your
url configuration::

    urlpatterns = [
        # ...
        path('centralauth/', include('centralauth.client.urls'))
    ]

.. note::

    Centralauth provides an option to hijack the admin login interface to make sure
    that the users go through the Centralauth oauth login flow.

    You might set ``CENTRALAUTH_CUSTOM_LOGIN_TEMPLATE`` to True or provide a
    Django template path to your custom template.
