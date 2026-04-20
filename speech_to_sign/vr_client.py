from __future__ import annotations

import json
import logging
import socket
import time
from dataclasses import dataclass

try:
    import requests
except ImportError:  # pragma: no cover - depends on environment install
    requests = None

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class VRSendResult:
    sent: bool
    channel: str
    detail: str
    attempts: int


class VRClient:
    """Sends sign sequences to VR systems through HTTP or TCP socket."""

    def __init__(
        self,
        endpoint: str,
        timeout: float,
        socket_host: str,
        socket_port: int,
        socket_enabled: bool,
        retries: int = 2,
        retry_backoff_seconds: float = 0.4,
    ) -> None:
        self.endpoint = endpoint
        self.timeout = timeout
        self.socket_host = socket_host
        self.socket_port = socket_port
        self.socket_enabled = socket_enabled
        self.retries = retries
        self.retry_backoff_seconds = retry_backoff_seconds

    def send(self, signs: list[str], transcript: str) -> VRSendResult:
        payload = {"transcript": transcript, "signs": signs}

        if self.socket_enabled:
            return self._send_with_retry("socket", payload)

        return self._send_with_retry("http", payload)

    def _send_with_retry(self, channel: str, payload: dict[str, object]) -> VRSendResult:
        attempts = self.retries + 1
        last_error = "unknown"

        for attempt in range(1, attempts + 1):
            result = self._send_socket(payload) if channel == "socket" else self._send_http(payload)
            if result.sent:
                result.attempts = attempt
                return result

            last_error = result.detail
            logger.warning("VR send attempt %s/%s failed (%s)", attempt, attempts, last_error)
            if attempt < attempts:
                time.sleep(self.retry_backoff_seconds * attempt)

        return VRSendResult(False, channel, last_error, attempts)

    def _send_http(self, payload: dict[str, object]) -> VRSendResult:
        if requests is None:
            return VRSendResult(False, "http", "requests package is not installed", 1)

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return VRSendResult(True, "http", f"status={response.status_code}", 1)
        except Exception as exc:
            return VRSendResult(False, "http", str(exc), 1)

    def _send_socket(self, payload: dict[str, object]) -> VRSendResult:
        message = json.dumps(payload).encode("utf-8")
        try:
            with socket.create_connection(
                (self.socket_host, self.socket_port),
                timeout=self.timeout,
            ) as conn:
                conn.sendall(message + b"\n")
            return VRSendResult(True, "socket", "delivered", 1)
        except OSError as exc:
            return VRSendResult(False, "socket", str(exc), 1)
