import time

from django.core.management.base import BaseCommand

from observability.checks import DBCheck, HTTPCheck, RedisCheck
from observability.checks.message_normalizer import normalize_check_message
from observability.models import Service, ServiceStatus


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
                            if service.service_type == Service.SERVICE_TYPE_HTTP
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
                    service_status, _ = ServiceStatus.objects.get_or_create(
                        service=service,
                        defaults={
                            "status": ServiceStatus.STATUS_OPERATIONAL,
                            "response_time_ms": None,
                            "message": "No checks yet",
                            "consecutive_failures": 0,
                            "consecutive_success": 0,
                        },
                    )

                    consecutive_failures = (
                        0 if is_success else service_status.consecutive_failures + 1
                    )
                    consecutive_success = (
                        service_status.consecutive_success + 1 if is_success else 0
                    )
                    next_status = self._compute_next_status(
                        current_status=service_status.status,
                        is_success=is_success,
                        consecutive_failures=consecutive_failures,
                        consecutive_success=consecutive_success,
                    )

                    ServiceStatus.objects.update_or_create(
                        service=service,
                        defaults={
                            "status": next_status,
                            "response_time_ms": latency_ms,
                            "message": message,
                            "consecutive_failures": consecutive_failures,
                            "consecutive_success": consecutive_success,
                        },
                    )

                    self.stdout.write(
                        f"[{service.name}] raw={check_status} status={next_status} "
                        f"failures={consecutive_failures} successes={consecutive_success} "
                        f"latency_ms={latency_ms} message={message}"
                    )
            except Exception as exc:  # noqa: BLE001
                self.stderr.write(self.style.ERROR(f"Checks loop iteration failed: {exc}"))
            time.sleep(60)
