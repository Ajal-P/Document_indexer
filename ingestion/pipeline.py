from pathlib import Path

from ingestion.loader import DocumentLoader
from ingestion.metadata import MetadataExtractor
from ingestion.chunker import Chunker
from ingestion.keywords import KeywordExtractor


# ======================================================
# Configuration
# ======================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FILE_PATH = (
    BASE_DIR
    / "docs"
    / "Malayalam_article_1.docx"
)

OUTPUT_FILE = (
    BASE_DIR
    / "docs"
    / "Malayalam_chunks.txt"
)

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def main():

    # ======================================================
    # STEP 1 : Load Document
    # ======================================================

    print("\n========== STEP 1 : LOAD DOCUMENT ==========\n")

    loader = DocumentLoader()

    document = loader.load(str(FILE_PATH))

    print("✓ Document Loaded")

    # ======================================================
    # STEP 2 : Markdown Preview
    # ======================================================

    print("\n========== DOCUMENT MARKDOWN ==========\n")

    print(document["markdown"])

    # ======================================================
    # STEP 3 : Generate Metadata
    # ======================================================

    print("\n========== STEP 3 : DOCUMENT METADATA ==========\n")

    metadata = MetadataExtractor().extract(
        str(FILE_PATH),
        document["text"]
    )

    print(metadata)

    # ======================================================
    # STEP 4 : Chunking
    # ======================================================

    print("\n========== STEP 4 : CHUNKING ==========\n")

    chunker = Chunker(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    chunks = chunker.split(document["markdown"])

    print(f"Total Chunks : {len(chunks)}")

    # ======================================================
    # STEP 5 : Keyword Extraction
    # ======================================================

    print("\n========== STEP 5 : KEYWORDS ==========\n")

    keyword_extractor = KeywordExtractor()
    

    # ======================================================
    # STEP 6 : Save Chunks to File
    # ======================================================

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

        file.write("DOCUMENT METADATA\n")
        file.write("=" * 80 + "\n")
        file.write(str(metadata))
        file.write("\n\n")

        for chunk in chunks:

            keywords = keyword_extractor.extract(
                chunk["text"],
                metadata["language"]
            )

            print("=" * 80)
            print(f"Chunk : {chunk['chunk_index']}")
            print(f"Characters : {chunk['character_count']}")
            print(f"Tokens     : {chunk['token_count']}")
            print(f"Keywords   : {keywords}")
            print("=" * 80)
            print(chunk["text"])
            print()

            file.write("=" * 80 + "\n")
            file.write(f"Chunk : {chunk['chunk_index']}\n")
            file.write(f"Characters : {chunk['character_count']}\n")
            file.write(f"Tokens     : {chunk['token_count']}\n")
            file.write(f"Keywords   : {keywords}\n")
            file.write("-" * 80 + "\n")
            file.write(chunk["text"])
            file.write("\n\n")

    print(f"\n✓ Chunks saved to:\n{OUTPUT_FILE}")

    print("\n✓ Chunking & Keyword Extraction Completed Successfully")


if __name__ == "__main__":
    main()