import os

from django.core.management.base import BaseCommand

from observability.models import Service


class Command(BaseCommand):
    help = "Seed initial services for observability monitoring."

    def handle(self, *args, **options):
        rename_map = {
            "backend": "Aptiview API",
            "redis": "Caching Service",
            "postgres": "Database Service",
        }
        for old_name, new_name in rename_map.items():
            if Service.objects.filter(name=old_name).exists() and not Service.objects.filter(name=new_name).exists():
                legacy_service = Service.objects.get(name=old_name)
                legacy_service.name = new_name
                legacy_service.save(update_fields=["name"])

        backend_endpoint = os.getenv(
            "SERVICE_BACKEND_ENDPOINT",
            "https://dev.aptiview.com/healthz",
        )
        interview_endpoint = os.getenv(
            "SERVICE_INTERVIEW_ENDPOINT",
            "http://host.docker.internal:3000/api/health",
        )
        redis_endpoint = os.getenv("SERVICE_REDIS_ENDPOINT") or None
        postgres_endpoint = os.getenv("SERVICE_POSTGRES_ENDPOINT") or None

        services = [
            {
                "name": "Aptiview API",
                "service_type": Service.SERVICE_TYPE_HTTP,
                "endpoint": backend_endpoint,
                "criticality": Service.CRITICALITY_CRITICAL,
            },
            {
                "name": "Caching Service",
                "service_type": Service.SERVICE_TYPE_REDIS,
                "endpoint": redis_endpoint,
                "criticality": Service.CRITICALITY_NON_CRITICAL,
            },
            {
                "name": "Interview Service",
                "service_type": Service.SERVICE_TYPE_HTTP,
                "endpoint": interview_endpoint,
                "criticality": Service.CRITICALITY_CRITICAL,
            },
            {
                "name": "Database Service",
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
