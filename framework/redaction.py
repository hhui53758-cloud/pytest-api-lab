"""只对日志副本脱敏，不改变实际请求。"""
SENSITIVE_KEYS = {
    "password", "password_hash", "authorization", "access_token", "token",
    "refresh_token", "cookie", "set-cookie", "salt",
}


def redact(value):
    if isinstance(value, dict):
        result = {
            key: "[REDACTED]" if str(key).lower() in SENSITIVE_KEYS else redact(item)
            for key, item in value.items()
        }
        if any(str(part).lower() in SENSITIVE_KEYS for part in value.get("loc", [])):
            if "input" in result:
                result["input"] = "[REDACTED]"
        return result
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    return value
