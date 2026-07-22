"""
ocr.py

Wrapper around the isolated OCR environment.
"""

from pathlib import Path
import subprocess
import re

OCR_PYTHON = "ocr_env/bin/python"
OCR_RUNNER = "ingestion/ocr_runner.py"


def extract_text(pdf_path: str) -> str:
    """
    Run OCR inside the isolated OCR environment.
    """

    pdf_path = str(Path(pdf_path))

    result = subprocess.run(
        [
            OCR_PYTHON,
            OCR_RUNNER,
            pdf_path,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("\n========== OCR STDERR ==========")
        print(result.stderr)
        print("================================\n")
        raise RuntimeError("OCR process failed")

    return result.stdout.strip()


def has_symbol_noise(text: str) -> bool:
    """
    Detect excessive suspicious symbols that often appear in
    corrupted PDF text extraction.

    Legitimate English words are NOT considered noise.
    """

    symbols = re.findall(r"[&|@#$%^*_~=<>`]", text)

    if not symbols:
        return False

    ratio = len(symbols) / max(len(text), 1)

    if len(symbols) > 10 or ratio > 0.01:
        print(
            f"Detected {len(symbols)} suspicious symbols "
            f"({ratio:.2%})."
        )
        return True

    return False


def needs_ocr(text: str) -> bool:
    """
    Determine whether Docling output quality is poor enough
    to justify OCR.
    """

    if not text.strip():
        print("Empty extracted text.")
        return True

    # ---------------------------------------------------------
    # Unicode replacement character (�)
    # ---------------------------------------------------------

    replacement_count = text.count("\uFFFD")
    replacement_ratio = replacement_count / max(len(text), 1)

    if replacement_count > 5 or replacement_ratio > 0.01:
        print(
            f"Detected {replacement_count} replacement characters "
            f"({replacement_ratio:.2%})."
        )
        return True

    # ---------------------------------------------------------
    # Known corrupted Unicode characters
    # ---------------------------------------------------------

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

    corruption_score = sum(text.count(ch) for ch in bad_chars)

    if corruption_score > 20:
        print(
            f"Detected {corruption_score} corrupted Unicode characters."
        )
        return True

    # ---------------------------------------------------------
    # Broken Tamil graphemes
    #
    # Example:
    #   ப ொருள்
    #   உண் ணாமை
    # ---------------------------------------------------------

    broken_tamil = len(
        re.findall(r"[அ-ஹ]\s+[ா-்]", text)
    )

    if broken_tamil > 20:
        print(
            f"Detected {broken_tamil} broken Tamil graphemes."
        )
        return True

    # ---------------------------------------------------------
    # Multiple replacement sequences
    # ---------------------------------------------------------

    invalid_sequences = len(re.findall(r"�+", text))

    if invalid_sequences > 10:
        print(
            f"Detected {invalid_sequences} invalid replacement sequences."
        )
        return True

    # ---------------------------------------------------------
    # Suspicious symbol density
    # ---------------------------------------------------------

    if has_symbol_noise(text):
        return True

    print("Docling extraction looks good.")

    return False


def extract_if_needed(
    docling_text: str,
    pdf_path: str,
) -> str:
    """
    Return Docling output unless OCR is expected
    to produce better text.
    """

    print("Checking extracted text...")

    if not needs_ocr(docling_text):
        return docling_text

    print("Running OCR...\n")

    ocr_text = extract_text(pdf_path)

    if not ocr_text.strip():
        print("OCR returned empty output. Falling back to Docling.")
        return docling_text

    print("OCR completed successfully.")

    return ocr_text