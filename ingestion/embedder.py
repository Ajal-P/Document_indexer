from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL, DEVICE


class Embedder:
    """
    Loads the embedding model once and reuses it.
    """

    def __init__(self):

        self.model = SentenceTransformer(
            EMBEDDING_MODEL,
            device=DEVICE
        )

    def embed(self, text: str):

        return self.model.encode(
            text,
            normalize_embeddings=True
        )

    def embed_batch(self, texts: list[str]):

        return self.model.encode(
            texts,
            batch_size=32,
            normalize_embeddings=True,
            show_progress_bar=False
        )