from pathlib import Path

BASE_DIR = Path(__file__).parent

EMBEDDING_MODEL = "BAAI/bge-m3"
DEVICE = "cpu"

VECTOR_SIZE = 1024
BATCH_SIZE = 32

COLLECTION_NAME = "documents_v5"

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

OCR_ENABLED = True

OCR_LANGUAGE = "en"

OCR_DEVICE = "cpu"

CORRUPTION_THRESHOLD = 20