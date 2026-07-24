"""
ocr_runner.py

Runs inside the isolated OCR environment.
Automatically detects the document language and performs OCR.
"""

import sys

import langid
import pytesseract
from pdf2image import convert_from_path


LANGUAGE_MAP = {
    "en": "eng",
    "hi": "hin+eng",
    "ml": "mal+eng",
    "ta": "tam+eng",
    "kn": "kan+eng",
    "te": "tel+eng",
}

langid.set_languages([
    "en",
    "hi",
    "ml",
    "ta",
    "kn",
    "te",
])


def detect_language(first_page):

    preview = pytesseract.image_to_string(
        first_page,
        lang="eng+hin+mal+tam+kan+tel",
        config="--oem 3 --psm 6",
    )

    language, confidence = langid.classify(preview)

    print(
        f"[OCR] Detected language: {language} ({confidence:.3f})",
        file=sys.stderr,
    )

    return LANGUAGE_MAP.get(language, "eng")


def main():

    if len(sys.argv) != 2:
        print("Usage: python ocr_runner.py file.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]

    pages = convert_from_path(
        pdf_path,
        dpi=300,
    )

    language = detect_language(pages[0])

    output = []

    for page in pages:

        text = pytesseract.image_to_string(
            page,
            lang=language,
            config="--oem 3 --psm 6",
        )

        output.append(text)

    print("\n".join(output))


if __name__ == "__main__":
    main()