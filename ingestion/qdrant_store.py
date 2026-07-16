from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

from config import (
    QDRANT_HOST,
    QDRANT_PORT,
    COLLECTION_NAME,
    VECTOR_SIZE,
)


class QdrantStore:
    """
    Handles all Qdrant database operations.

    Responsibilities:
    - Connect to Qdrant
    - Create collection
    - Insert points
    - Search vectors
    - Retrieve stored points
    - Delete documents
    - Check duplicate documents
    """

    def __init__(self):

        self.client = QdrantClient(
            host=QDRANT_HOST,
            port=QDRANT_PORT,
        )

        self.collection_name = COLLECTION_NAME

        self._create_collection()

    # =====================================================
    # Collection
    # =====================================================

    def _create_collection(self):

        if not self.client.collection_exists(self.collection_name):

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )

            print(
                f"Collection '{self.collection_name}' created."
            )

        else:

            print(
                f"Collection '{self.collection_name}' already exists."
            )

    # =====================================================
    # Build Point
    # =====================================================

    def build_point(
        self,
        embedding,
        payload,
    ):

        return PointStruct(
            id=str(uuid4()),
            vector=embedding.tolist(),
            payload=payload,
        )

    # =====================================================
    # Insert Points
    # =====================================================

    def insert_points(
        self,
        points,
    ):

        print(f"\nCollection      : {self.collection_name}")
        print(f"Number of points: {len(points)}")

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )

        print("Points inserted successfully.")

    # =====================================================
    # Semantic Search
    # =====================================================

    def search(
        self,
        embedding,
        limit=5,
    ):

        return self.client.query_points(
            collection_name=self.collection_name,
            query=embedding.tolist(),
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

    # =====================================================
    # Retrieve Stored Points (Debugging)
    # =====================================================

    def get_points(
        self,
        limit=5,
    ):

        points, _ = self.client.scroll(
            collection_name=self.collection_name,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

        return points

    # =====================================================
    # Duplicate Document Check
    # =====================================================

    def document_exists(
        self,
        document_hash,
    ):

        points, _ = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="document_hash",
                        match=MatchValue(
                            value=document_hash
                        ),
                    )
                ]
            ),
            limit=1,
        )

        return len(points) > 0

    # =====================================================
    # Delete Document
    # =====================================================

    def delete_document(
        self,
        document_hash,
    ):

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="document_hash",
                        match=MatchValue(
                            value=document_hash
                        ),
                    )
                ]
            ),
        )

        print("Document deleted.")

    # =====================================================
    # Collection Information
    # =====================================================

    def collection_info(self):

        return self.client.get_collection(
            self.collection_name
        )

    # =====================================================
    # Count Points
    # =====================================================

    def count_points(self):

        result = self.client.count(
            collection_name=self.collection_name,
            exact=True,
        )

        return result.count