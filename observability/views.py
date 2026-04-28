from rest_framework.response import Response
from rest_framework.views import APIView

from observability.models import Service


class ServiceStatusView(APIView):
    def get(self, request):
        services = Service.objects.filter(is_active=True).select_related("service_status")
        payload = []
        critical_statuses = []
        non_critical_statuses = []

        for service in services:
            status_obj = getattr(service, "service_status", None)
            status = status_obj.status if status_obj else "outage"
            message = status_obj.message if status_obj else "No status yet"
            latency = status_obj.response_time_ms if status_obj else None
            if service.criticality == Service.CRITICALITY_CRITICAL:
                critical_statuses.append(status)
            else:
                non_critical_statuses.append(status)
            payload.append(
                {
                    "name": service.name,
                    "status": status,
                    "latency": latency,
                    "message": message,
                    "criticality": service.criticality,
                }
            )

        if "outage" in critical_statuses:
            overall_status = "outage"
        elif "degraded" in critical_statuses:
            overall_status = "degraded"
        elif "outage" in non_critical_statuses or "degraded" in non_critical_statuses:
            overall_status = "degraded"
        else:
            overall_status = "operational"

        return Response({"overall_status": overall_status, "services": payload})

# Create your views here.
