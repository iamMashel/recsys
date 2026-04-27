import uuid
from functools import lru_cache
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """
    Semantic similarity layer using sentence-transformers + ChromaDB.
    Loaded lazily so the model isn't imported at startup unless needed.
    """

    def __init__(self):
        self._model = None
        self._collection = None

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("embedding_model_loaded")

    def _load_collection(self):
        if self._collection is None:
            import chromadb

            client = chromadb.Client()
            self._collection = client.get_or_create_collection("items")

    def embed_text(self, text: str) -> list[float]:
        self._load_model()
        return self._model.encode(text).tolist()

    def index_item(self, item_id: uuid.UUID, text: str) -> None:
        self._load_model()
        self._load_collection()
        embedding = self._model.encode(text).tolist()
        self._collection.upsert(
            ids=[str(item_id)],
            embeddings=[embedding],
            documents=[text],
        )

    def similar_items(self, query_text: str, n: int = 20) -> list[str]:
        self._load_model()
        self._load_collection()
        try:
            embedding = self._model.encode(query_text).tolist()
            results = self._collection.query(query_embeddings=[embedding], n_results=n)
            return results["ids"][0] if results["ids"] else []
        except Exception as e:
            logger.warning("embedding_similarity_failed", error=str(e))
            return []


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
