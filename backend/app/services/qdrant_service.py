from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from app.config import get_settings
import uuid
from typing import List, Dict, Optional

settings = get_settings()

# Initialize Qdrant client (cached globally)
_client = None

def get_qdrant_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
    return _client

# Collection names
CV_COLLECTION = "cv_embeddings"
JD_COLLECTION = "jd_embeddings"
SKILLS_COLLECTION = "skills_embeddings"

def init_collections():
    """Initialize Qdrant collections if they don't exist"""
    client = get_qdrant_client()

    collections = [CV_COLLECTION, JD_COLLECTION, SKILLS_COLLECTION]

    for collection_name in collections:
        try:
            # Check if collection exists
            collection = client.get_collection(collection_name)
            print(f"✓ Collection '{collection_name}' already exists")
        except Exception as e:
            # Collection doesn't exist, create it
            try:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=settings.EMBEDDING_DIMENSION,
                        distance=Distance.COSINE
                    )
                )
                print(f"✓ Created collection '{collection_name}'")
            except Exception as create_error:
                # Collection might have been created between check and creation
                print(f"⚠ Collection '{collection_name}' might already exist: {create_error}")

def store_cv_embedding(
    cv_id: str,
    text: str,
    embedding: List[float],
    metadata: Dict
) -> str:
    """Store CV embedding in Qdrant"""
    client = get_qdrant_client()

    point_id = str(uuid.uuid4())

    client.upsert(
        collection_name=CV_COLLECTION,
        points=[
            PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "cv_id": cv_id,
                    "text": text,
                    "section": metadata.get("section", "full"),
                    **metadata
                }
            )
        ]
    )

    return point_id

def store_jd_embedding(
    jd_id: str,
    text: str,
    embedding: List[float],
    metadata: Dict
) -> str:
    """Store JD embedding in Qdrant"""
    client = get_qdrant_client()

    point_id = str(uuid.uuid4())

    client.upsert(
        collection_name=JD_COLLECTION,
        points=[
            PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "jd_id": jd_id,
                    "text": text,
                    "requirement_type": metadata.get("requirement_type", "general"),
                    **metadata
                }
            )
        ]
    )

    return point_id

def search_similar_cvs(
    query_embedding: List[float],
    limit: int = 5,
    filters: Optional[Dict] = None
) -> List[Dict]:
    """Search for similar CVs"""
    client = get_qdrant_client()

    search_result = client.search(
        collection_name=CV_COLLECTION,
        query_vector=query_embedding,
        limit=limit
    )

    return [
        {
            "id": hit.id,
            "score": hit.score,
            "payload": hit.payload
        }
        for hit in search_result
    ]

def search_similar_jds(
    query_embedding: List[float],
    limit: int = 5
) -> List[Dict]:
    """Search for similar job descriptions"""
    client = get_qdrant_client()

    search_result = client.search(
        collection_name=JD_COLLECTION,
        query_vector=query_embedding,
        limit=limit
    )

    return [
        {
            "id": hit.id,
            "score": hit.score,
            "payload": hit.payload
        }
        for hit in search_result
    ]

def get_rag_context_for_cv(cv_id: str, query_text: str, query_embedding: List[float]) -> str:
    """Get relevant context from similar CVs for RAG"""
    similar = search_similar_cvs(query_embedding, limit=3)

    context_parts = []
    for item in similar:
        if item["score"] > 0.7:  # Relevance threshold
            context_parts.append(f"Similar CV experience: {item['payload'].get('text', '')[:200]}")

    return "\n\n".join(context_parts) if context_parts else ""

def get_rag_context_for_jd(jd_id: str, query_embedding: List[float]) -> str:
    """Get relevant context from similar JDs for RAG"""
    similar = search_similar_jds(query_embedding, limit=3)

    context_parts = []
    for item in similar:
        if item["score"] > 0.7:
            context_parts.append(f"Similar JD requirement: {item['payload'].get('text', '')[:200]}")

    return "\n\n".join(context_parts) if context_parts else ""
