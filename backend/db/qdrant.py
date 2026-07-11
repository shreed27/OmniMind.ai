from qdrant_client import QdrantClient


def create_qdrant(url: str, api_key: str | None = None) -> QdrantClient:
    return QdrantClient(url=url, api_key=api_key or "")


def ensure_collection(client: QdrantClient, name: str, vector_size: int = 768) -> None:
    try:
        client.create_collection(
            collection_name=name,
            vectors_config={"size": vector_size, "distance": "Cosine"},
        )
    except Exception:  # pragma: no cover - ignore if exists
        pass
