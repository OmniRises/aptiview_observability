import time

from django.db import connection

from .base import BaseCheck
from .message_normalizer import normalize_check_message


class DBCheck(BaseCheck):
    def run(self):
        start = time.perf_counter()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            latency_ms = int((time.perf_counter() - start) * 1000)
            return "operational", latency_ms, "DB query OK"
        except Exception as exc:  # noqa: BLE001
            return "outage", None, normalize_check_message(str(exc))
