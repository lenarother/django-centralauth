from django.conf.urls import url
from oauth2_provider import views


app_name = 'oauth2_provider'

urlpatterns = [
    url(r'^authorize/$', views.AuthorizationView.as_view(), name='authorize'),
    url(r'^token/$', views.TokenView.as_view(), name='token'),
    url(r'^revoke_token/$', views.RevokeTokenView.as_view(), name='revoke-token'),
    url(r'^introspect/$', views.IntrospectTokenView.as_view(), name='introspect'),
]
