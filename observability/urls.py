from django.urls import path

from observability.views import ServiceStatusView

urlpatterns = [
    path("status/", ServiceStatusView.as_view(), name="service-status"),
]
