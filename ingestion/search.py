from ingestion.embedder import Embedder
from ingestion.qdrant_store import QdrantStore


def main():

    print("=" * 80)
    print("Semantic Search")
    print("=" * 80)

    embedder = Embedder()

    store = QdrantStore()

    while True:

        query = input("\nEnter your question (type 'exit' to quit): ")

        if query.lower() == "exit":
            break

        query_vector = embedder.embed(query)

        results = store.search(
            query_vector,
            limit=8,
        )

        print("\nTop Results\n")

        if len(results.points) == 0:

            print("No results found.")

            continue

        for index, point in enumerate(results.points, start=1):

            payload = point.payload

            print("=" * 100)

            print(f"Rank         : {index}")

            print(f"Score        : {point.score:.4f}")

            print(f"Document     : {payload['document_name']}")

            print(f"Chunk Index  : {payload['chunk_index']}")

            print(f"Keywords     : {payload['keywords']}")

            print("\nText\n")

            print(payload["text"])

            print()
            

if __name__ == "__main__":
    main()