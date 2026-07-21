"""
ocr.py

Wrapper around the isolated OCR environment.
"""

from pathlib import Path
import subprocess

OCR_PYTHON = "ocr_env/bin/python"
OCR_RUNNER = "ingestion/ocr_runner.py"


def extract_text(pdf_path: str) -> str:

    pdf_path = str(Path(pdf_path))

    result = subprocess.run(
        [
            OCR_PYTHON,
            OCR_RUNNER,
            pdf_path,
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    if result.stderr:
        print(result.stderr.strip())

    return result.stdout


def is_corrupted(text: str, threshold: int = 20) -> bool:

    if not text:
        return True

    bad_chars = {
        "ʭ",
        "ƹ",
        "ϗ",
        "Ł",
        "ǲ",
        "Ȯ",
        "̵",
        "˗",
        "ƞ",
    }

    score = sum(text.count(ch) for ch in bad_chars)

    return score > threshold


def extract_if_needed(
    docling_text: str,
    pdf_path: str,
) -> str:

    if not is_corrupted(docling_text):
        return docling_text

    print("Corrupted text detected.")
    print("Running OCR...")

    return extract_text(pdf_path)