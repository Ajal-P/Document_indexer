from ingestion.keywords import KeywordExtractor


class ChunkMetadataGenerator:

    def __init__(self):

        self.keyword_extractor = KeywordExtractor()

    def generate(
        self,
        chunk: dict,
        document_metadata: dict
    ):

        return {

            **document_metadata,

            "chunk_index": chunk["chunk_index"],

            "character_count": chunk["character_count"],

            "token_count": chunk["token_count"],

            "keywords": self.keyword_extractor.extract(
                chunk["text"]
            ),

            "text": chunk["text"]
        }