from pathlib import Path

from docling.document_converter import DocumentConverter

from ingestion.ocr import extract_if_needed

import unicodedata

import re


class DocumentLoader:

    def __init__(self):
        self.converter = DocumentConverter()

    def load(self, file_path: str) -> dict:

        print("=" * 80)
        print("Running Docling...")
        print("=" * 80)

        result = self.converter.convert(file_path)

        document = result.document

        markdown = document.export_to_markdown()
        text = document.export_to_text()

        if Path(file_path).suffix.lower() == ".pdf":

            print("Checking extracted text...")

            try:

                final_text = extract_if_needed(
                    docling_text=text,
                    pdf_path=file_path,
                )

                if final_text != text:

                    print("OCR extraction successful.")

                    text = final_text
                    markdown = final_text

                else:

                    print("Docling extraction looks good.")

            except Exception as e:

                print(f"OCR failed: {e}")

        # Normalize Unicode
        text = unicodedata.normalize("NFC", text)

        # Collapse repeated spaces/tabs (preserve paragraph breaks)
        text = re.sub(r"[ \t]+", " ", text)

        return {
            "filename": Path(file_path).name,
            "document": document,
            "markdown": markdown,
            "text": text,
        }