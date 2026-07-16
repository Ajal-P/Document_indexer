from pathlib import Path
import hashlib
from datetime import datetime
from lingua import LanguageDetectorBuilder


class MetadataExtractor:
    def __init__(self):

        self.detector = LanguageDetectorBuilder.from_all_languages().build()

    def extract(self, file_path: str, text: str):

        language = self.detector.detect_language_of(text)

        return {

            "document_name": Path(file_path).name,

            "document_hash": hashlib.sha256(
                text.encode("utf-8")
            ).hexdigest(),

            "language": language.iso_code_639_1.name.lower()
            if language
            else "unknown",

            "indexed_at": datetime.utcnow().isoformat(),

            "source": "local",

            "version": 1

        }