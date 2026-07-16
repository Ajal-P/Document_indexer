from keybert import KeyBERT
from sentence_transformers import SentenceTransformer


class KeywordExtractor:

    def __init__(self):

        embedding_model = SentenceTransformer(
            "BAAI/bge-m3"
        )

        self.model = KeyBERT(
            model=embedding_model
        )

    def extract(
        self,
        text: str,
        top_n: int = 10,
    ):

        keywords = self.model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 3),
            stop_words="english",
            top_n=top_n,
        )

        return [keyword for keyword, score in keywords]