from django.conf.urls import url
from exchange.views import App, Docs, Register

app_name = 'exchange'

urlpatterns = [
    url(r'^$', App.as_view(), name='index'),
    url(r'^docs/', Docs.as_view(), name='docs'),
    url(r'^register/', Register.as_view(), name='register')
]