from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class STTResult:
    text: str
    backend: str


class BaseSTT:
    def transcribe(self, recognizer: Any, audio: Any, language: str) -> STTResult:
        raise NotImplementedError


class GoogleSTT(BaseSTT):
    def transcribe(self, recognizer: Any, audio: Any, language: str) -> STTResult:
        text = recognizer.recognize_google(audio, language=language)
        return STTResult(text=text, backend="google")


class VoskSTT(BaseSTT):
    """Offline transcription using a local Vosk model."""

    def __init__(self, model_path: str) -> None:
        try:
            from vosk import KaldiRecognizer, Model  # type: ignore
        except Exception as exc:  # pragma: no cover - tested by runtime integration
            raise RuntimeError(
                "Vosk backend selected but `vosk` is not installed. "
                "Install requirements and provide --vosk-model-path."
            ) from exc

        self._kaldi_recognizer = KaldiRecognizer
        self._model = Model(model_path)

    def transcribe(self, recognizer: Any, audio: Any, language: str) -> STTResult:
        _ = recognizer
        _ = language
        rec = self._kaldi_recognizer(self._model, 16000)
        raw = audio.get_raw_data(convert_rate=16000, convert_width=2)
        rec.AcceptWaveform(raw)
        payload = json.loads(rec.FinalResult())
        return STTResult(text=payload.get("text", ""), backend="vosk")


def build_stt_backend(name: str, vosk_model_path: str | None) -> BaseSTT:
    normalized = name.lower().strip()

    if normalized == "google":
        return GoogleSTT()

    if normalized == "vosk":
        if not vosk_model_path:
            raise ValueError("--vosk-model-path is required when --stt-backend vosk")
        return VoskSTT(vosk_model_path)

    raise ValueError(f"Unsupported STT backend: {name}")
