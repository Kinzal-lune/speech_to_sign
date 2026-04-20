from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PipelineConfig:
    """Runtime configuration for the speech-to-sign pipeline."""

    language: str = "en-US"
    phrase_time_limit: int = 5
    listen_timeout: int = 1
    energy_threshold: int = 300
    pause_threshold: float = 0.8
    dynamic_energy_threshold: bool = True

    stt_backend: str = "google"
    vosk_model_path: str | None = None

    send_to_vr: bool = False
    vr_endpoint: str = "http://127.0.0.1:5000/sign-sequence"
    vr_timeout_seconds: float = 1.5
    vr_socket_host: str = "127.0.0.1"
    vr_socket_port: int = 8765
    vr_socket_enabled: bool = False
    vr_retries: int = 2
    vr_retry_backoff_seconds: float = 0.4

    queue_maxsize: int = 8
    mic_reconnect_delay_seconds: float = 1.0
