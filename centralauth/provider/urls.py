from django.urls import include, path

from .views import PermsEndpoint, UserEndpoint


urlpatterns = [
    path('o/', include('centralauth.provider.oauth_urls', namespace='oauth2_provider')),
    path('user/', UserEndpoint.as_view(), name='user'),
    path('perms/', PermsEndpoint.as_view(), name='perms'),
]
