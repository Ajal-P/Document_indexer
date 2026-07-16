from pathlib import Path
from time import perf_counter

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
    / "IT-policies-and-procedures-manual-template.docx"
)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


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
            chunk["text"]
        )

    print("✓ Keywords Generated")

    # ======================================================
    # STEP 5 : Load Embedding Model
    # ======================================================

    print("\n========== STEP 5 : LOAD EMBEDDING MODEL ==========\n")

    embedder = Embedder()

    print("✓ BGE-M3 Loaded")

    # ======================================================
    # STEP 6 : Connect Qdrant
    # ======================================================

    print("\n========== STEP 6 : CONNECT QDRANT ==========\n")

    store = QdrantStore()

    print("✓ Connected")

    # ======================================================
    # STEP 7 : Check Duplicate Document
    # ======================================================

    print("\n========== STEP 7 : CHECK DOCUMENT ==========\n")

    if store.document_exists(metadata["document_hash"]):

        print("Document already indexed.")

        return

    print("Document not found in Qdrant.")

    # ======================================================
    # STEP 8 : Generate Embeddings & Build Points
    # ======================================================

    print("\n========== STEP 8 : BUILD POINTS ==========\n")

    points = []

    for chunk in chunks:

        start = perf_counter()

        embedding = embedder.embed(
            chunk["text"]
        )

        elapsed = perf_counter() - start

        payload = {

            **metadata,

            "chunk_index": chunk["chunk_index"],

            "character_count": chunk["character_count"],

            "token_count": chunk["token_count"],

            "keywords": chunk["keywords"],

            "text": chunk["text"]

        }

        point = store.build_point(
            embedding=embedding,
            payload=payload
        )

        points.append(point)

        print(
            f"Chunk {chunk['chunk_index']:>3} | "
            f"Tokens : {chunk['token_count']:>4} | "
            f"Embedding : {elapsed:.3f}s"
        )

    print(f"\nTotal Points Built : {len(points)}")

    # ======================================================
    # STEP 9 : Store in Qdrant
    # ======================================================

    print("\n========== STEP 9 : UPSERT ==========\n")

    store.insert_points(points)

    print("✓ Successfully Stored")

    # ======================================================
    # STEP 10 : Collection Information
    # ======================================================

    print("\n========== STEP 10 : COLLECTION ==========\n")

    info = store.collection_info()

    print(info)

    # ======================================================
    # STEP 11 : Verify Stored Data
    # ======================================================

    print("\n========== STEP 11 : VERIFY ==========\n")


    print("\n✓ Pipeline Completed Successfully")


if __name__ == "__main__":
    main()