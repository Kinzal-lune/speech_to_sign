from __future__ import annotations

import logging
import queue
import threading
import time
from pathlib import Path

import speech_recognition as sr

from .config import PipelineConfig
from .sign_mapper import SignMapper
from .stt import build_stt_backend
from .vr_client import VRClient

logger = logging.getLogger(__name__)


class SpeechToSignPipeline:
    """Captures microphone speech and converts it into sign tokens."""

    def __init__(self, mapping_file: Path, config: PipelineConfig | None = None) -> None:
        self.config = config or PipelineConfig()
        self.mapper = SignMapper(mapping_file)
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = self.config.energy_threshold
        self.recognizer.pause_threshold = self.config.pause_threshold
        self.recognizer.dynamic_energy_threshold = self.config.dynamic_energy_threshold

        self.audio_queue: queue.Queue[sr.AudioData] = queue.Queue(maxsize=self.config.queue_maxsize)
        self._stop_event = threading.Event()
        self.stt_backend = build_stt_backend(self.config.stt_backend, self.config.vosk_model_path)

        self.vr_client = VRClient(
            endpoint=self.config.vr_endpoint,
            timeout=self.config.vr_timeout_seconds,
            socket_host=self.config.vr_socket_host,
            socket_port=self.config.vr_socket_port,
            socket_enabled=self.config.vr_socket_enabled,
            retries=self.config.vr_retries,
            retry_backoff_seconds=self.config.vr_retry_backoff_seconds,
        )

    def _capture_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                with sr.Microphone() as source:
                    logger.info("Microphone connected; adjusting for ambient noise")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                    while not self._stop_event.is_set():
                        try:
                            audio = self.recognizer.listen(
                                source,
                                timeout=self.config.listen_timeout,
                                phrase_time_limit=self.config.phrase_time_limit,
                            )
                            self.audio_queue.put(audio, timeout=0.5)
                        except sr.WaitTimeoutError:
                            continue
                        except queue.Full:
                            logger.warning("Audio queue full; dropping captured segment")
            except OSError as exc:
                logger.error("Microphone error: %s. Reconnecting...", exc)
                time.sleep(self.config.mic_reconnect_delay_seconds)

    def _process_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                audio = self.audio_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                text = self.stt_backend.transcribe(
                    self.recognizer,
                    audio,
                    self.config.language,
                ).text.strip()
            except sr.UnknownValueError:
                logger.info("No recognizable speech in segment")
                continue
            except sr.RequestError as exc:
                logger.error("Speech recognition request failed: %s", exc)
                continue
            except Exception as exc:  # defensive fallback to keep stream alive
                logger.exception("Unexpected STT failure: %s", exc)
                continue

            if not text:
                continue

            signs = self.mapper.to_sign_tokens(text)
            logger.info("Recognized text: %s", text)
            logger.info("Sign tokens: %s", signs)

            if self.config.send_to_vr:
                result = self.vr_client.send(signs=signs, transcript=text)
                if result.sent:
                    logger.info("VR delivery succeeded via %s in %s attempt(s)", result.channel, result.attempts)
                else:
                    logger.error("VR delivery failed via %s after %s attempt(s): %s", result.channel, result.attempts, result.detail)

    def run_forever(self) -> None:
        logger.info("Speech-to-sign streaming started. Press Ctrl+C to stop.")

        capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        process_thread = threading.Thread(target=self._process_loop, daemon=True)

        capture_thread.start()
        process_thread.start()

        try:
            while capture_thread.is_alive() and process_thread.is_alive():
                time.sleep(0.5)
        except KeyboardInterrupt:
            logger.info("Shutting down pipeline")
            self._stop_event.set()
            capture_thread.join(timeout=2)
            process_thread.join(timeout=2)
