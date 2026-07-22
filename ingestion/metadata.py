from pathlib import Path
import hashlib
from datetime import datetime

import langid


class MetadataExtractor:

    def __init__(self):
        # Restrict to languages you expect (optional)
        langid.set_languages([
            "en",
            "ml",
            "hi",
            "ta",
            "kn",
            "te",
        ])

    def detect_language(self, text: str) -> str:

        language, _ = langid.classify(text)

        return language

    def extract(
        self,
        file_path: str,
        text: str,
    ):

        language = self.detect_language(text)

        return {

            "document_name": Path(file_path).name,

            "document_hash": hashlib.sha256(
                text.encode("utf-8")
            ).hexdigest(),

            "language": language,

            "indexed_at": datetime.utcnow().isoformat(),

            "source": "local",

            "version": 1,

        }