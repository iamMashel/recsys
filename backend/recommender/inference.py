"""
Fallback inference using the Redis-cached CF model (built by train.py).
Used when Gorse returns no results (cold-start or Gorse is down).
"""
import json
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
CACHE_KEY = "recsys:item_cf_model"


async def get_cf_fallback(user_liked_items: list[str], n: int = 20) -> list[str]:
    """Return item IDs similar to what the user already liked."""
    import redis.asyncio as aioredis

    settings = get_settings()
    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        raw = await redis.get(CACHE_KEY)
    finally:
        await redis.aclose()

    if not raw:
        logger.warning("cf_model_not_in_cache")
        return []

    model: dict[str, list[str]] = json.loads(raw)
    scores: dict[str, int] = {}
    for item_id in user_liked_items:
        for neighbor in model.get(item_id, []):
            if neighbor not in user_liked_items:
                scores[neighbor] = scores.get(neighbor, 0) + 1

    return sorted(scores, key=lambda x: scores[x], reverse=True)[:n]
