"""统一请求、认证、超时和脱敏日志，保留原始 Response。"""
import logging
from time import perf_counter

import requests

from framework.redaction import redact

LOGGER = logging.getLogger("api_tests")


class ApiClient:
    def __init__(self, base_url, timeout=3):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.trust_env = False

    def set_token(self, token):
        self.session.headers["Authorization"] = f"Bearer {token}"

    def request(self, method, path, **kwargs):
        if not path.startswith("/") or "?" in path:
            raise ValueError("Use a relative path and pass query parameters via params=")
        kwargs.setdefault("timeout", self.timeout)
        headers = {**dict(self.session.headers), **kwargs.get("headers", {})}
        LOGGER.info(
            "REQUEST method=%s path=%s headers=%s params=%s json=%s",
            method, path, redact(headers), redact(kwargs.get("params")), redact(kwargs.get("json")),
        )
        start = perf_counter()
        try:
            response = self.session.request(method, self.base_url + path, **kwargs)
        except requests.RequestException as error:
            LOGGER.error("REQUEST_ERROR method=%s path=%s type=%s elapsed_ms=%.2f",
                         method, path, type(error).__name__, (perf_counter() - start) * 1000)
            raise
        try:
            body = redact(response.json())
        except requests.exceptions.JSONDecodeError:
            body = "<empty or non-JSON body>"
        LOGGER.info("RESPONSE method=%s path=%s status=%s elapsed_ms=%.2f json=%s",
                    method, path, response.status_code, (perf_counter() - start) * 1000, body)
        return response

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)

    def close(self):
        self.session.close()
