from pathlib import Path

from ingestion.loader import DocumentLoader
from ingestion.metadata import MetadataExtractor
from ingestion.chunker import Chunker
from ingestion.keywords import KeywordExtractor
from ingestion.embedder import Embedder
from ingestion.qdrant_store import QdrantStore


# ======================================================
# Configuration
# ======================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FILE_PATH = (
    BASE_DIR
    / "docs"
    / "Hindi Vyakaran & Rachna.pdf"
)

OCR_LANGUAGE = "hi"

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
        document["text"],
    )

    print(metadata)

    # ======================================================
    # STEP 2.5 : SAVE PROCESSED TEXT
    # ======================================================

    print("\n========== STEP 2.5 : SAVE PROCESSED TEXT ==========\n")

    output_dir = Path("processed")
    output_dir.mkdir(exist_ok=True)

    stem = Path(document["filename"]).stem

    (output_dir / f"{stem}.txt").write_text(
        document["text"],
        encoding="utf-8",
        )

    print("✓ Processed text saved")

    # ======================================================
    # STEP 3 : Chunking
    # ======================================================

    print("\n========== STEP 3 : CHUNKING ==========\n")

    chunker = Chunker(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
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
            metadata["language"],
        )

    print("✓ Keywords Generated")

    # ======================================================
    # STEP 4.5 : Build Context
    # ======================================================

    print("\n========== STEP 4.5 : BUILD CONTEXT ==========\n")

    for i, chunk in enumerate(chunks):

        context = []

        # Previous chunk keywords
        if i > 0:
            context.extend(chunks[i - 1]["keywords"][:3])

        # Current chunk keywords
        context.extend(chunk["keywords"])

        chunk["context"] = ", ".join(context)

    print("✓ Context Generated")

    # ======================================================
    # STEP 5 : Embedding Generation
    # ======================================================

    print("\n========== STEP 5 : EMBEDDING GENERATION ==========\n")

    embedder = Embedder()

    texts = [
        f"Context: {chunk['context']}\n\n{chunk['text']}"
        for chunk in chunks
    ]

    embeddings = embedder.embed_batch(texts)

    for chunk, embedding in zip(chunks, embeddings):

        chunk["embedding"] = embedding

        print("=" * 100)
        print(f"Chunk Index        : {chunk['chunk_index']}")
        print(f"Characters         : {chunk['character_count']}")
        print(f"Tokens             : {chunk['token_count']}")
        print(f"Keywords           : {chunk['keywords']}")
        print(f"Context            : {chunk['context']}")
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

    # ======================================================
    # STEP 6 : Store in Qdrant
    # ======================================================

    print("\n========== STEP 6 : STORE IN QDRANT ==========\n")

    store = QdrantStore()

    if store.document_exists(metadata["document_hash"]):
        print("✓ Document already indexed.")
        return

    points = []

    for chunk in chunks:

        payload = {
            **metadata,
            "chunk_index": chunk["chunk_index"],
            "text": chunk["text"],
            "context": chunk["context"],
            "keywords": chunk["keywords"],
            "character_count": chunk["character_count"],
            "token_count": chunk["token_count"],
        }

        point = store.build_point(
            embedding=chunk["embedding"],
            payload=payload,
        )

        points.append(point)

    store.insert_points(points)

    print(f"✓ Total Points in Collection : {store.count_points()}")
    print("\n✓ Pipeline Completed Successfully")

if __name__ == "__main__":
    main()