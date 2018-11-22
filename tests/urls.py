import os

from django.contrib import admin


try:
    from django.urls import include, url
except ImportError:
    from django.conf.urls import include, url


urlpatterns = [
    url('^admin/', admin.site.urls),
    url('^client/', include('centralauth.client.urls')),
]

if 'provider' in os.environ.get('TOX_ENV_NAME', 'provider'):
    urlpatterns.append(url('^provider/', include('centralauth.provider.urls')))
