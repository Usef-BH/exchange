from django.conf.urls import url
from exchange.views import App

app_name = 'exchange'

urlpatterns = [
    url(r'^$', App.as_view(), name='index')
]