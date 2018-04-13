from django.conf.urls import url
from exchange.views import App, Docs, Code

app_name = 'exchange'

urlpatterns = [
    url(r'^$', App.as_view(), name='index'),
    url(r'^docs/', Docs.as_view(), name='docs'),
    url(r'^code/', Code.as_view(), name='code')
]