import time

from django.db import transaction
from django.core.management.base import BaseCommand
from django.utils import timezone

from observability.checks import DBCheck, HTTPCheck, RedisCheck
from observability.checks.message_normalizer import normalize_check_message
from observability.models import Incident, Service, ServiceStatus, ServiceStatusHistory


class Command(BaseCommand):
    help = "Run service checks continuously every 60 seconds."

    CHECKS_MAP = {
        Service.SERVICE_TYPE_HTTP: HTTPCheck,
        Service.SERVICE_TYPE_REDIS: RedisCheck,
        Service.SERVICE_TYPE_POSTGRES: DBCheck,
    }

    def _compute_next_status(
        self,
        current_status: str,
        is_success: bool,
        consecutive_failures: int,
        consecutive_success: int,
    ) -> str:
        if is_success:
            if current_status in (
                ServiceStatus.STATUS_OUTAGE,
                ServiceStatus.STATUS_DEGRADED,
            ) and consecutive_success < 2:
                return current_status
            if consecutive_success >= 2:
                return ServiceStatus.STATUS_OPERATIONAL
            return current_status

        if consecutive_failures >= 2:
            return ServiceStatus.STATUS_OUTAGE
        return ServiceStatus.STATUS_DEGRADED

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting observability checks loop..."))
        while True:
            try:
                services = Service.objects.filter(is_active=True)
                current_outage_services = []
                for service in services:
                    check_class = self.CHECKS_MAP.get(service.service_type)
                    if not check_class:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Skipping {service.name}: unknown service_type={service.service_type}"
                            )
                        )
                        continue

                    try:
                        check = (
                            check_class(service.endpoint)
                            if service.service_type
                            in (
                                Service.SERVICE_TYPE_HTTP,
                                Service.SERVICE_TYPE_POSTGRES,
                            )
                            else check_class()
                        )
                        check_status, latency_ms, message = check.run()
                    except Exception as exc:  # noqa: BLE001
                        check_status, latency_ms, message = (
                            "outage",
                            None,
                            normalize_check_message(str(exc)),
                        )

                    is_success = check_status == ServiceStatus.STATUS_OPERATIONAL
                    with transaction.atomic():
                        service_status, created = ServiceStatus.objects.select_for_update().get_or_create(
                            service=service,
                            defaults={
                                "status": ServiceStatus.STATUS_OPERATIONAL,
                                "response_time_ms": None,
                                "message": "No checks yet",
                                "consecutive_failures": 0,
                                "consecutive_success": 0,
                            },
                        )
                        previous_status = (
                            ServiceStatus.STATUS_OPERATIONAL if created else service_status.status
                        )

                        consecutive_failures = (
                            0 if is_success else service_status.consecutive_failures + 1
                        )
                        consecutive_success = (
                            service_status.consecutive_success + 1 if is_success else 0
                        )
                        next_status = self._compute_next_status(
                            current_status=previous_status,
                            is_success=is_success,
                            consecutive_failures=consecutive_failures,
                            consecutive_success=consecutive_success,
                        )

                        service_status.status = next_status
                        service_status.response_time_ms = latency_ms
                        service_status.message = message
                        service_status.consecutive_failures = consecutive_failures
                        service_status.consecutive_success = consecutive_success
                        service_status.save()

                        ServiceStatusHistory.objects.create(
                            service=service,
                            status=next_status,
                            response_time_ms=latency_ms,
                            message=message,
                        )

                        if previous_status != ServiceStatus.STATUS_OUTAGE and next_status == ServiceStatus.STATUS_OUTAGE:
                            open_incident = (
                                Incident.objects.select_for_update()
                                .filter(end_time__isnull=True)
                                .order_by("-start_time")
                                .first()
                            )
                            if open_incident is None:
                                open_incident = Incident.objects.create()
                            open_incident.affected_services.add(service)

                    if next_status == ServiceStatus.STATUS_OUTAGE:
                        current_outage_services.append(service.id)

                    self.stdout.write(
                        f"[{service.name}] raw={check_status} status={next_status} "
                        f"failures={consecutive_failures} successes={consecutive_success} "
                        f"latency_ms={latency_ms} message={message}"
                    )

                with transaction.atomic():
                    open_incident = (
                        Incident.objects.select_for_update()
                        .filter(end_time__isnull=True)
                        .order_by("-start_time")
                        .first()
                    )
                    if current_outage_services:
                        if open_incident is None:
                            open_incident = Incident.objects.create()
                        open_incident.affected_services.add(*current_outage_services)
                    elif open_incident is not None:
                        open_incident.end_time = timezone.now()
                        open_incident.save(update_fields=["end_time"])
            except Exception as exc:  # noqa: BLE001
                self.stderr.write(self.style.ERROR(f"Checks loop iteration failed: {exc}"))
            time.sleep(60)
