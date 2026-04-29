import time

import psycopg2

from .base import BaseCheck
from .message_normalizer import normalize_check_message


class DBCheck(BaseCheck):
    def __init__(self, dsn: str | None = None):
        self.dsn = dsn

    def run(self):
        if not self.dsn:
            return "outage", None, "Missing database URL"

        start = time.perf_counter()
        conn = None
        try:
            conn = psycopg2.connect(self.dsn, connect_timeout=3)
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            latency_ms = int((time.perf_counter() - start) * 1000)
            return "operational", latency_ms, "DB query OK"
        except Exception as exc:  # noqa: BLE001
            return "outage", None, normalize_check_message(str(exc))
        finally:
            if conn is not None:
                conn.close()
