from django.urls import path
from configdev.views import DeviceView

urlpatterns = [
    path("", DeviceView.as_view(), name="device-page"),
]
