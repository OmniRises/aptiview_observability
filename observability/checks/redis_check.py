import os
import time

import redis

from .base import BaseCheck
from .message_normalizer import normalize_check_message


class RedisCheck(BaseCheck):
    def run(self):
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", "6379"))
        start = time.perf_counter()
        try:
            client = redis.Redis(host=host, port=port, socket_connect_timeout=3)
            client.ping()
            latency_ms = int((time.perf_counter() - start) * 1000)
            return "operational", latency_ms, "Redis ping OK"
        except Exception as exc:  # noqa: BLE001
            return "outage", None, normalize_check_message(str(exc))
