from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('client/', include('centralauth.client.urls')),
    path('provider/', include('centralauth.provider.urls'))
]
