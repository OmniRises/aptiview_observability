from rest_framework.response import Response
from rest_framework.views import APIView

from observability.models import Service


class ServiceStatusView(APIView):
    def get(self, request):
        services = Service.objects.filter(is_active=True).select_related("service_status")
        payload = []
        statuses = []

        for service in services:
            status_obj = getattr(service, "service_status", None)
            status = status_obj.status if status_obj else "outage"
            message = status_obj.message if status_obj else "No status yet"
            latency = status_obj.response_time_ms if status_obj else None
            statuses.append(status)
            payload.append(
                {
                    "name": service.name,
                    "status": status,
                    "latency": latency,
                    "message": message,
                }
            )

        if "outage" in statuses:
            overall_status = "outage"
        elif "degraded" in statuses:
            overall_status = "degraded"
        else:
            overall_status = "operational"

        return Response({"overall_status": overall_status, "services": payload})

# Create your views here.
