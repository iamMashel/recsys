import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.interaction import Interaction
from app.models.item import Item
from app.services.gorse_client import GorseClient
from app.services.embedding_service import get_embedding_service
from app.schemas.recommendation import RecommendedItem, RecommendationResponse
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RecommenderService:
    def __init__(self, db: AsyncSession, gorse: GorseClient):
        self.db = db
        self.gorse = gorse
        self.embedding = get_embedding_service()
        self.settings = get_settings()

    async def get_recommendations(self, user_id: uuid.UUID) -> RecommendationResponse:
        cf_ids, semantic_ids, popular_ids = await self._fetch_all_signals(user_id)

        scores = self._merge_scores(cf_ids, semantic_ids, popular_ids)

        if not scores:
            logger.warning("no_recommendations_found", user_id=str(user_id))
            return RecommendationResponse(user_id=user_id, results=[], total=0)

        top_ids = sorted(scores, key=lambda i: scores[i]["score"], reverse=True)[
            : self.settings.TOP_K
        ]

        items = await self._fetch_items(top_ids)
        results = [
            RecommendedItem(
                item_id=item.id,
                title=item.title,
                genres=item.genres,
                score=round(scores[str(item.id)]["score"], 4),
                reason=scores[str(item.id)]["reason"],
            )
            for item in items
        ]

        logger.info(
            "recommendations_generated",
            user_id=str(user_id),
            count=len(results),
        )
        return RecommendationResponse(user_id=user_id, results=results, total=len(results))

    async def _fetch_all_signals(
        self, user_id: uuid.UUID
    ) -> tuple[list[str], list[str], list[str]]:
        cf_ids = await self.gorse.get_recommendations(user_id, n=20)

        # Gorse cold-start fallback: use local Redis CF model
        if not cf_ids:
            from recommender.inference import get_cf_fallback
            liked = await self._get_user_liked_item_ids(user_id)
            if liked:
                cf_ids = await get_cf_fallback(liked, n=20)

        user_text = await self._build_user_preference_text(user_id)
        semantic_ids = self.embedding.similar_items(user_text, n=20) if user_text else []

        popular_ids = await self._get_popular_ids(limit=20)

        return cf_ids, semantic_ids, popular_ids

    async def _get_user_liked_item_ids(self, user_id: uuid.UUID) -> list[str]:
        from sqlalchemy import select
        from app.models.interaction import Interaction
        result = await self.db.execute(
            select(Interaction.item_id)
            .where(Interaction.user_id == user_id, Interaction.rating >= 3.5)
            .order_by(Interaction.timestamp.desc())
            .limit(20)
        )
        return [str(r[0]) for r in result.all()]

    def _merge_scores(
        self,
        cf_ids: list[str],
        semantic_ids: list[str],
        popular_ids: list[str],
    ) -> dict[str, dict]:
        s = self.settings
        scores: dict[str, dict] = {}

        def add(item_id: str, weight: float, label: str):
            if item_id not in scores:
                scores[item_id] = {"score": 0.0, "reason": label}
            scores[item_id]["score"] += weight
            # track dominant source
            if weight >= max(
                s.CF_WEIGHT if label == "collaborative" else 0,
                s.SEMANTIC_WEIGHT if label == "semantic" else 0,
                s.POPULARITY_WEIGHT if label == "popular" else 0,
            ):
                scores[item_id]["reason"] = label

        for rank, iid in enumerate(cf_ids):
            # decay by rank position
            add(iid, s.CF_WEIGHT * (1 / (rank + 1)), "collaborative")

        for rank, iid in enumerate(semantic_ids):
            add(iid, s.SEMANTIC_WEIGHT * (1 / (rank + 1)), "semantic")

        for rank, iid in enumerate(popular_ids):
            add(iid, s.POPULARITY_WEIGHT * (1 / (rank + 1)), "popular")

        return scores

    async def _build_user_preference_text(self, user_id: uuid.UUID) -> str:
        result = await self.db.execute(
            select(Item.genres, Item.title)
            .join(Interaction, Interaction.item_id == Item.id)
            .where(
                Interaction.user_id == user_id,
                Interaction.rating >= 4.0,
            )
            .order_by(Interaction.timestamp.desc())
            .limit(10)
        )
        rows = result.all()
        return " ".join(
            f"{r.title} {r.genres or ''}" for r in rows
        ).strip()

    async def _get_popular_ids(self, limit: int = 20) -> list[str]:
        result = await self.db.execute(
            select(Item.id)
            .where(Item.rating_count > 0)
            .order_by(Item.avg_rating.desc(), Item.rating_count.desc())
            .limit(limit)
        )
        return [str(row[0]) for row in result.all()]

    async def _fetch_items(self, item_ids: list[str]) -> list[Item]:
        uuids = [uuid.UUID(i) for i in item_ids]
        result = await self.db.execute(select(Item).where(Item.id.in_(uuids)))
        items = result.scalars().all()
        id_order = {iid: idx for idx, iid in enumerate(item_ids)}
        return sorted(items, key=lambda i: id_order.get(str(i.id), 999))
