import uuid
from functools import lru_cache
from app.core.logging import get_logger

logger = get_logger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    import chromadb
    _ML_AVAILABLE = True
except ImportError:
    _ML_AVAILABLE = False
    logger.warning("ml_deps_not_installed", detail="sentence-transformers/chromadb missing — semantic recommendations disabled")


class EmbeddingService:
    """
    Semantic similarity via sentence-transformers + ChromaDB.
    Gracefully disabled when ML packages are not installed (e.g. free-tier deploy).
    """

    def __init__(self):
        self._model = None
        self._collection = None

    @property
    def available(self) -> bool:
        return _ML_AVAILABLE

    def _load(self):
        if not _ML_AVAILABLE:
            return
        if self._model is None:
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            client = chromadb.Client()
            self._collection = client.get_or_create_collection("items")
            logger.info("embedding_model_loaded")

    def index_item(self, item_id: uuid.UUID, text: str) -> None:
        if not _ML_AVAILABLE:
            return
        self._load()
        embedding = self._model.encode(text).tolist()
        self._collection.upsert(ids=[str(item_id)], embeddings=[embedding], documents=[text])

    def similar_items(self, query_text: str, n: int = 20) -> list[str]:
        if not _ML_AVAILABLE or not query_text:
            return []
        self._load()
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
