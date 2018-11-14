from django.conf.urls import url

from .views import CallbackView, LoginView


app_name = 'centralauth_client'
urlpatterns = [
    url('^login/$', LoginView.as_view(), name='login'),
    url('^login/callback/$', CallbackView.as_view(), name='login-callback'),
]
