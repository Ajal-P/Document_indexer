from pathlib import Path

BASE_DIR = Path(__file__).parent

EMBEDDING_MODEL = "BAAI/bge-m3"
DEVICE = "cpu"

VECTOR_SIZE = 1024
BATCH_SIZE = 32

COLLECTION_NAME = "documents_v2"

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333