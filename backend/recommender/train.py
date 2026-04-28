"""
Offline training pipeline (Phase 1: before Gorse is fully warmed up).
Builds a simple item-item collaborative filtering matrix from interactions
and stores it in Redis as a fallback when Gorse has no data.

Usage: python -m recommender.train
"""
import asyncio
import json
from collections import defaultdict
from app.core.logging import configure_logging, get_logger
from app.core.config import get_settings

configure_logging()
logger = get_logger(__name__)
settings = get_settings()

CACHE_KEY = "recsys:item_cf_model"
CACHE_TTL = 60 * 60 * 24  # 24 hours


async def build_and_cache():
    import redis.asyncio as aioredis
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    from app.models.interaction import Interaction

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Interaction.user_id, Interaction.item_id, Interaction.rating)
            .where(Interaction.rating.is_not(None))
        )
        rows = result.all()

    if not rows:
        logger.warning("no_ratings_found_skipping_train")
        return

    # Build user → items map
    user_items: dict[str, set[str]] = defaultdict(set)
    for user_id, item_id, _ in rows:
        user_items[str(user_id)].add(str(item_id))

    # Item-item co-occurrence
    co: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for items in user_items.values():
        items_list = list(items)
        for i in range(len(items_list)):
            for j in range(i + 1, len(items_list)):
                co[items_list[i]][items_list[j]] += 1
                co[items_list[j]][items_list[i]] += 1

    # Normalize to top-20 similar items per item
    model: dict[str, list[str]] = {}
    for item_id, neighbors in co.items():
        top = sorted(neighbors, key=lambda x: neighbors[x], reverse=True)[:20]
        model[item_id] = top

    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    await redis.set(CACHE_KEY, json.dumps(model), ex=CACHE_TTL)
    await redis.aclose()

    logger.info("cf_model_cached", items=len(model))


if __name__ == "__main__":
    asyncio.run(build_and_cache())
