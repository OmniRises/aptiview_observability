def normalize_check_message(raw_message: str) -> str:
    text = (raw_message or "").lower()

    if "name resolution" in text or "failed to resolve" in text or "nodename nor servname" in text:
        return "DNS resolution failed"
    if "timeout" in text or "timed out" in text:
        return "Request timed out"
    if (
        "connection error" in text
        or "connection refused" in text
        or "max retries exceeded" in text
        or "could not connect" in text
    ):
        return "Connection failed"
    if "http " in text:
        return raw_message
    if "missing endpoint" in text:
        return "Missing endpoint URL"
    return "Health check failed"
