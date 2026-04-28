"""
Batch embedding script — run once after seeding, then via Celery daily.
Usage: python -m recommender.embeddings
"""
import asyncio
from app.core.logging import configure_logging, get_logger
from app.services.embedding_service import get_embedding_service

configure_logging()
logger = get_logger(__name__)


async def index_all():
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    from app.models.item import Item

    svc = get_embedding_service()
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Item))
        items = result.scalars().all()

    logger.info("embedding_start", total=len(items))
    for i, item in enumerate(items):
        text = f"{item.title} {item.genres or ''}".strip()
        svc.index_item(item.id, text)
        if (i + 1) % 500 == 0:
            logger.info("embedding_progress", done=i + 1, total=len(items))

    logger.info("embedding_complete", total=len(items))


if __name__ == "__main__":
    asyncio.run(index_all())
