from rest_framework.response import Response
from rest_framework.views import APIView

from observability.models import Incident, Service, ServiceStatusHistory
from observability.throttles import StatusPageRateThrottle


class ServiceStatusView(APIView):
    throttle_classes = [StatusPageRateThrottle]

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

        open_incident = Incident.objects.filter(end_time__isnull=True).order_by("-start_time").first()
        last_incident = Incident.objects.filter(end_time__isnull=False).order_by("-end_time").first()

        return Response(
            {
                "overall_status": overall_status,
                "services": payload,
                "incident": {
                    "open_incident_id": open_incident.id if open_incident else None,
                    "open_since": open_incident.start_time if open_incident else None,
                    "last_incident_end": last_incident.end_time if last_incident else None,
                },
            }
        )


class ServiceStatusHistoryView(APIView):
    throttle_classes = [StatusPageRateThrottle]

    def get(self, request):
        limit = int(request.query_params.get("limit", 100))
        history = ServiceStatusHistory.objects.select_related("service")[: max(1, min(limit, 500))]
        items = [
            {
                "service": entry.service.name,
                "status": entry.status,
                "response_time_ms": entry.response_time_ms,
                "message": entry.message,
                "checked_at": entry.checked_at,
            }
            for entry in history
        ]
        return Response({"count": len(items), "history": items})
