from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken


class Chunker:

    def __init__(
        self,
        chunk_size: int = 800,  #900, 1000,
        chunk_overlap: int = 100,  #150, 200,
    ):

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators = [
             "\n\n",
              "\n",
              ". ",
              "? ",
              "! ",
              "।",      # Devanagari danda (Hindi, Marathi, Nepali, etc.)
              "॥",      # Double danda
              " ",
              "",
            ]
        )

        self.encoding = tiktoken.get_encoding("cl100k_base")

    def split(self, text: str):

        split_chunks = self.splitter.split_text(text)

        chunks = []

        for index, chunk in enumerate(split_chunks):

            token_count = len(
                self.encoding.encode(chunk)
            )

            chunks.append(
                {
                    "chunk_index": index,
                    "character_count": len(chunk),
                    "token_count": token_count,
                    "text": chunk
                }
            )

        return chunks