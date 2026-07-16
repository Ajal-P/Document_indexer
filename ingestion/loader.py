from pathlib import Path
from docling.document_converter import DocumentConverter


class DocumentLoader:
    def __init__(self):
        self.converter = DocumentConverter()

    def load(self, file_path: str) -> dict:
        result = self.converter.convert(file_path)

        document = result.document

        return {
            "filename": Path(file_path).name,
            "document": document,
            "markdown": document.export_to_markdown(),
            "text": document.export_to_text(),
        }