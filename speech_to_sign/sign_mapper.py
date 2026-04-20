from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

try:
    import nltk
except ImportError:  # pragma: no cover - depends on environment install
    nltk = None


class SignMapper:
    """Maps text to sign tokens via a configurable dictionary."""

    def __init__(self, mapping_path: Path) -> None:
        self.mapping_path = mapping_path
        self.mapping = self._load_mapping()

    def _load_mapping(self) -> dict[str, str]:
        if not self.mapping_path.exists():
            raise FileNotFoundError(
                f"Sign mapping file not found: {self.mapping_path}"
            )
        with self.mapping_path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)

        return {str(k).lower(): str(v) for k, v in data.items()}

    def tokenize(self, text: str) -> list[str]:
        """Tokenize text using NLTK, with regex fallback for low-resource devices."""
        normalized = text.lower().strip()
        if not normalized:
            return []

        if nltk is not None:
            try:
                return [tok for tok in nltk.word_tokenize(normalized) if tok.isalpha()]
            except LookupError:
                pass

        # On Raspberry Pi deployments, nltk/punkt may not be pre-installed.
        return re.findall(r"[a-zA-Z']+", normalized)

    def to_sign_tokens(self, text: str) -> list[str]:
        tokens = self.tokenize(text)
        return [self.mapping.get(token, "UNK") for token in tokens]

    def known_words(self) -> Iterable[str]:
        return self.mapping.keys()
