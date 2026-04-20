from __future__ import annotations

import unittest

from speech_to_sign.stt import GoogleSTT, build_stt_backend


class DummyRecognizer:
    def recognize_google(self, audio, language):
        _ = audio
        _ = language
        return "hello"


class TestSTT(unittest.TestCase):
    def test_google_backend_builder(self) -> None:
        backend = build_stt_backend("google", None)
        self.assertIsInstance(backend, GoogleSTT)

    def test_vosk_requires_model_path(self) -> None:
        with self.assertRaises(ValueError):
            build_stt_backend("vosk", None)

    def test_google_transcribe(self) -> None:
        backend = GoogleSTT()
        result = backend.transcribe(DummyRecognizer(), audio=object(), language="en-US")
        self.assertEqual(result.text, "hello")
        self.assertEqual(result.backend, "google")


if __name__ == "__main__":
    unittest.main()
