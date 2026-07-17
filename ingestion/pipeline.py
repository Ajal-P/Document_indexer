from pathlib import Path

from ingestion.loader import DocumentLoader
from ingestion.metadata import MetadataExtractor
from ingestion.chunker import Chunker
from ingestion.keywords import KeywordExtractor
from ingestion.embedder import Embedder


# ======================================================
# Configuration
# ======================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FILE_PATH = (
    BASE_DIR
    / "docs"
    / "Malayalam_article_1.docx"
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
    # STEP 2 : Generate Metadata
    # ======================================================

    print("\n========== STEP 2 : DOCUMENT METADATA ==========\n")

    metadata = MetadataExtractor().extract(
        str(FILE_PATH),
        document["text"]
    )

    print(metadata)

    # ======================================================
    # STEP 3 : Chunking
    # ======================================================

    print("\n========== STEP 3 : CHUNKING ==========\n")

    chunker = Chunker(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    chunks = chunker.split(document["markdown"])

    print(f"Total Chunks : {len(chunks)}")

    # ======================================================
    # STEP 4 : Keyword Extraction
    # ======================================================

    print("\n========== STEP 4 : KEYWORD EXTRACTION ==========\n")

    keyword_extractor = KeywordExtractor()

    for chunk in chunks:

        chunk["keywords"] = keyword_extractor.extract(
            chunk["text"],
            metadata["language"]
        )

    print("✓ Keywords Generated")

    # ======================================================
    # STEP 5 : EMBEDDING GENERATION
    # ======================================================

    print("\n========== STEP 5 : EMBEDDING GENERATION ==========\n")

    embedder = Embedder()

    texts = [chunk["text"] for chunk in chunks]

    embeddings = embedder.embed_batch(texts)

    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding
        print("=" * 100)
        print(f"Chunk Index        : {chunk['chunk_index']}")
        print(f"Characters         : {chunk['character_count']}")
        print(f"Tokens             : {chunk['token_count']}")
        print(f"Keywords           : {chunk['keywords']}")
        print("-" * 100)
        print("Chunk Text:\n")
        print(chunk["text"])
        print("-" * 100)
        print(f"Embedding Dimension: {len(embedding)}")
        print("First 10 Values:")
        print(embedding[:10])
        print("=" * 100)
        print()
        
    print(f"Total Embeddings Generated : {len(embeddings)}")
        
    print("\n✓ Embeddings Generated Successfully")


if __name__ == "__main__":
    main()