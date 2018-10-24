from django.urls import path

from .views import CallbackView, LoginView


app_name = 'centralauth_client'
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('login/callback/', CallbackView.as_view(), name='login-callback'),
]
