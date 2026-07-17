from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
import yake


class KeywordExtractor:

    def __init__(self):

        embedding_model = SentenceTransformer(
            "BAAI/bge-m3"
        )

        self.keybert = KeyBERT(
            model=embedding_model
        )

    def extract(
        self,
        text: str,
        language: str,
        top_n: int = 10,
    ):

        language = language.lower()

        if language == "english":

            keywords = self.keybert.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 3),
                stop_words="english",
                top_n=top_n,
                use_mmr=True,
                diversity=0.4,
            )

            return [
                keyword
                for keyword, score in keywords
            ]

        else:

            extractor = yake.KeywordExtractor(

                lan="auto",

                n=3,

                top=top_n,

            )

            keywords = extractor.extract_keywords(text)

            return [

                keyword

                for keyword, score in keywords

            ]