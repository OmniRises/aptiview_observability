import time

import requests

from .base import BaseCheck
from .message_normalizer import normalize_check_message


class HTTPCheck(BaseCheck):
    def __init__(self, url: str):
        self.url = url

    def run(self):
        if not self.url:
            return "outage", None, "Missing endpoint URL"

        start = time.perf_counter()
        try:
            response = requests.get(self.url, timeout=3)
            latency_ms = int((time.perf_counter() - start) * 1000)
            if response.status_code == 200:
                try:
                    payload = response.json()
                    if isinstance(payload, dict) and "status" in payload:
                        if str(payload["status"]).lower() != "ok":
                            return "outage", latency_ms, "status!=ok"
                except ValueError:
                    pass
                return "operational", latency_ms, "OK"
            if 400 <= response.status_code < 500:
                return "degraded", latency_ms, f"HTTP {response.status_code}"
            if response.status_code >= 500:
                return "outage", latency_ms, f"HTTP {response.status_code}"
            return "degraded", latency_ms, f"HTTP {response.status_code}"
        except Exception as exc:  # noqa: BLE001
            return "outage", None, normalize_check_message(str(exc))
