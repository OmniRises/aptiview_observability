import os

from django.core.management.base import BaseCommand

from observability.models import Service


class Command(BaseCommand):
    help = "Seed initial services for observability monitoring."

    def handle(self, *args, **options):
        backend_endpoint = os.getenv(
            "SERVICE_BACKEND_ENDPOINT",
            "https://dev.aptiview.com/healthz",
        )
        redis_endpoint = os.getenv("SERVICE_REDIS_ENDPOINT") or None
        postgres_endpoint = os.getenv("SERVICE_POSTGRES_ENDPOINT") or None

        services = [
            {
                "name": "backend",
                "service_type": Service.SERVICE_TYPE_HTTP,
                "endpoint": backend_endpoint,
                "criticality": Service.CRITICALITY_CRITICAL,
            },
            {
                "name": "redis",
                "service_type": Service.SERVICE_TYPE_REDIS,
                "endpoint": redis_endpoint,
                "criticality": Service.CRITICALITY_NON_CRITICAL,
            },
            {
                "name": "postgres",
                "service_type": Service.SERVICE_TYPE_POSTGRES,
                "endpoint": postgres_endpoint,
                "criticality": Service.CRITICALITY_CRITICAL,
            },
        ]
        for payload in services:
            service, created = Service.objects.update_or_create(
                name=payload["name"],
                defaults={
                    "service_type": payload["service_type"],
                    "endpoint": payload["endpoint"],
                    "criticality": payload["criticality"],
                    "is_active": True,
                },
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action}: {service.name}")
