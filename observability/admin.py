from django.contrib import admin

from .models import Service, ServiceStatus


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "service_type", "endpoint", "is_active")
    list_filter = ("service_type", "is_active")
    search_fields = ("name", "endpoint")
    fields = ("name", "endpoint", "service_type", "is_active")


@admin.register(ServiceStatus)
class ServiceStatusAdmin(admin.ModelAdmin):
    list_display = ("service", "status", "response_time_ms", "last_checked")
    list_filter = ("status",)
    search_fields = ("service__name", "message")
    readonly_fields = ("service", "status", "last_checked", "response_time_ms")
    fields = ("service", "status", "last_checked", "response_time_ms", "message")
