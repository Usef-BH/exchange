from django.conf.urls import url
from api.views import Api, Latest

app_name = "api"

urlpatterns = [
    url(r'^$', Api.as_view(), name="api"),
    url(r'^latest/', Latest.as_view(), name="latest")
]