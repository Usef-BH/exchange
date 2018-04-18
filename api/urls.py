from django.conf.urls import url
from api.views import Api, Latest, getHist

app_name = "api"

urlpatterns = [
    url(r'^$', Api.as_view(), name="api"),
    url(r'^latest/?$', Latest.as_view(), name="latest"),
    url(r'^([0-9]{4})-([0-9]{2})-([0-9]{2})/?', getHist.as_view(), name="historical")
    #url(r'^(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2})/?', getHist.as_view(), name="historical")
]