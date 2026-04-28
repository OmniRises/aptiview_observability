from django.contrib import admin

from .models import Incident, Service, ServiceStatus, ServiceStatusHistory


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "service_type", "criticality", "endpoint", "is_active")
    list_filter = ("service_type", "criticality", "is_active")
    search_fields = ("name", "endpoint")
    fields = ("name", "endpoint", "service_type", "criticality", "is_active")


@admin.register(ServiceStatus)
class ServiceStatusAdmin(admin.ModelAdmin):
    list_display = ("service", "status", "response_time_ms", "last_checked")
    list_filter = ("status",)
    search_fields = ("service__name", "message")
    readonly_fields = ("service", "status", "last_checked", "response_time_ms")
    fields = ("service", "status", "last_checked", "response_time_ms", "message")


@admin.register(ServiceStatusHistory)
class ServiceStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("service", "status", "response_time_ms", "checked_at")
    list_filter = ("status", "service__name")
    search_fields = ("service__name", "message")
    readonly_fields = ("service", "status", "response_time_ms", "message", "checked_at")


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ("id", "start_time", "end_time")
    filter_horizontal = ("affected_services",)
