DEBUG = True

SECRET_KEY = 'test'

ROOT_URLCONF = 'tests.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

MIDDLEWARE_CLASSES = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',

    'oauth2_provider',  # provider
    'centralauth.client',  # client
    'centralauth.provider',  # provider
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'centralauth.client.middleware.CentralAuthSyncMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'centralauth.client.backends.OAuthBackend',
]

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
}]

LOGIN_URL = '/admin/login/'

OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL = 'oauth2_provider.AccessToken'  # provider
OAUTH2_PROVIDER_APPLICATION_MODEL = 'provider.Application'  # provider

CENTRALAUTH_PROVIDER_URL = 'https://localhost:8000/provider'  # client

CENTRALAUTH_CLIENT_ID = 'TEST-CLIENT-ID'  # client
CENTRALAUTH_CLIENT_SECRET = 'TEST-CLIENT-SECRET'  # client
