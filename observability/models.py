from django.db import models


class Service(models.Model):
    SERVICE_TYPE_HTTP = "http"
    SERVICE_TYPE_REDIS = "redis"
    SERVICE_TYPE_POSTGRES = "postgres"
    SERVICE_TYPE_CHOICES = (
        (SERVICE_TYPE_HTTP, "HTTP"),
        (SERVICE_TYPE_REDIS, "Redis"),
        (SERVICE_TYPE_POSTGRES, "Postgres"),
    )
    CRITICALITY_CRITICAL = "critical"
    CRITICALITY_NON_CRITICAL = "non_critical"
    CRITICALITY_CHOICES = (
        (CRITICALITY_CRITICAL, "Critical"),
        (CRITICALITY_NON_CRITICAL, "Non-Critical"),
    )

    name = models.CharField(max_length=255, unique=True)
    endpoint = models.URLField(blank=True, null=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)
    criticality = models.CharField(
        max_length=20,
        choices=CRITICALITY_CHOICES,
        default=CRITICALITY_CRITICAL,
    )
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.service_type})"


class ServiceStatus(models.Model):
    STATUS_OPERATIONAL = "operational"
    STATUS_DEGRADED = "degraded"
    STATUS_OUTAGE = "outage"
    STATUS_CHOICES = (
        (STATUS_OPERATIONAL, "Operational"),
        (STATUS_DEGRADED, "Degraded"),
        (STATUS_OUTAGE, "Outage"),
    )

    service = models.OneToOneField(
        Service,
        on_delete=models.CASCADE,
        related_name="service_status",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    last_checked = models.DateTimeField(auto_now=True)
    response_time_ms = models.IntegerField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    consecutive_failures = models.IntegerField(default=0)
    consecutive_success = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.service.name}: {self.status}"


class ServiceStatusHistory(models.Model):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="status_history",
    )
    status = models.CharField(max_length=20, choices=ServiceStatus.STATUS_CHOICES)
    response_time_ms = models.IntegerField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-checked_at",)

    def __str__(self) -> str:
        return f"{self.service.name} @ {self.checked_at.isoformat()} = {self.status}"


class Incident(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    affected_services = models.ManyToManyField(Service, related_name="incidents", blank=True)

    class Meta:
        ordering = ("-start_time",)

    def __str__(self) -> str:
        state = "open" if self.end_time is None else "closed"
        return f"Incident #{self.pk} ({state})"
