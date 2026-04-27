import uuid
import httpx
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class GorseClient:
    def __init__(self):
        settings = get_settings()
        self.base_url = settings.GORSE_API_URL
        self.api_key = settings.GORSE_API_KEY
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            headers = {"X-API-Key": self.api_key} if self.api_key else {}
            self._client = httpx.AsyncClient(
                base_url=self.base_url, headers=headers, timeout=5.0
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def get_recommendations(self, user_id: uuid.UUID, n: int = 20) -> list[str]:
        client = await self._get_client()
        try:
            res = await client.get(f"/api/recommend/{user_id}", params={"n": n})
            res.raise_for_status()
            return res.json() or []
        except httpx.HTTPError as e:
            logger.warning("gorse_recommendation_failed", user_id=str(user_id), error=str(e))
            return []

    async def insert_user(self, user_id: uuid.UUID) -> bool:
        client = await self._get_client()
        try:
            res = await client.post("/api/user", json={"UserId": str(user_id), "Labels": []})
            return res.status_code in (200, 201)
        except httpx.HTTPError as e:
            logger.warning("gorse_insert_user_failed", user_id=str(user_id), error=str(e))
            return False

    async def insert_item(self, item_id: uuid.UUID, categories: list[str]) -> bool:
        client = await self._get_client()
        try:
            res = await client.post(
                "/api/item",
                json={"ItemId": str(item_id), "Labels": categories, "IsHidden": False},
            )
            return res.status_code in (200, 201)
        except httpx.HTTPError as e:
            logger.warning("gorse_insert_item_failed", item_id=str(item_id), error=str(e))
            return False

    async def insert_feedback(
        self, user_id: uuid.UUID, item_id: uuid.UUID, feedback_type: str, timestamp: str
    ) -> bool:
        client = await self._get_client()
        try:
            res = await client.post(
                "/api/feedback",
                json=[
                    {
                        "FeedbackType": feedback_type,
                        "UserId": str(user_id),
                        "ItemId": str(item_id),
                        "Timestamp": timestamp,
                    }
                ],
            )
            return res.status_code in (200, 201)
        except httpx.HTTPError as e:
            logger.warning("gorse_feedback_failed", error=str(e))
            return False
