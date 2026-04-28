from django.urls import path

from observability.views import ServiceStatusHistoryView, ServiceStatusView

urlpatterns = [
    path("status/", ServiceStatusView.as_view(), name="service-status"),
    path("status/history/", ServiceStatusHistoryView.as_view(), name="service-status-history"),
]
