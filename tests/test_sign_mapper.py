from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from speech_to_sign.sign_mapper import SignMapper


class TestSignMapper(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.mapping_file = Path(self.temp_dir.name) / "signs.json"
        self.mapping_file.write_text(
            json.dumps({"hello": "SIGN_HELLO", "world": "SIGN_WORLD"}),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_maps_known_and_unknown_tokens(self) -> None:
        mapper = SignMapper(self.mapping_file)
        self.assertEqual(mapper.to_sign_tokens("hello unknown world"), ["SIGN_HELLO", "UNK", "SIGN_WORLD"])

    def test_regex_fallback_when_nltk_data_missing(self) -> None:
        mapper = SignMapper(self.mapping_file)
        fake_nltk = Mock()
        fake_nltk.word_tokenize.side_effect = LookupError
        with patch("speech_to_sign.sign_mapper.nltk", fake_nltk):
            self.assertEqual(mapper.tokenize("Hello, world!"), ["hello", "world"])


if __name__ == "__main__":
    unittest.main()
