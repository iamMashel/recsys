"""
Celery tasks for background processing.

Run worker:  celery -A workers.celery_app worker --loglevel=info
Run beat:    celery -A workers.celery_app beat  --loglevel=info
"""
import asyncio
from celery.utils.log import get_task_logger
from workers.celery_app import celery

logger = get_task_logger(__name__)


def _run(coro):
    """Run an async coroutine from a sync Celery task."""
    return asyncio.get_event_loop().run_until_complete(coro)


@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def sync_all_to_gorse(self):
    """Push all users, items, and interactions to Gorse."""
    try:
        _run(_sync_all_to_gorse())
    except Exception as exc:
        logger.error("sync_all_to_gorse failed: %s", exc)
        raise self.retry(exc=exc)


@celery.task(bind=True, max_retries=2)
def index_all_embeddings(self):
    """Embed all items and upsert into ChromaDB."""
    try:
        _run(_index_all_embeddings())
    except Exception as exc:
        logger.error("index_all_embeddings failed: %s", exc)
        raise self.retry(exc=exc)


@celery.task
def sync_single_feedback(user_id: str, item_id: str, feedback_type: str, timestamp: str):
    """Forward a single interaction to Gorse (fast, fire-and-forget)."""
    _run(_sync_single_feedback(user_id, item_id, feedback_type, timestamp))


# ── async implementations ──────────────────────────────────────────────────

async def _sync_all_to_gorse():
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    from app.models.user import User
    from app.models.item import Item
    from app.models.interaction import Interaction
    from app.services.gorse_client import GorseClient

    gorse = GorseClient()
    async with AsyncSessionLocal() as db:
        users = (await db.execute(select(User))).scalars().all()
        for u in users:
            await gorse.insert_user(u.id)
        logger.info("synced %d users to gorse", len(users))

        items = (await db.execute(select(Item))).scalars().all()
        for item in items:
            cats = [g.strip() for g in (item.genres or "").split(",") if g.strip()]
            await gorse.insert_item(item.id, cats)
        logger.info("synced %d items to gorse", len(items))

        interactions = (await db.execute(select(Interaction))).scalars().all()
        for ix in interactions:
            await gorse.insert_feedback(
                user_id=ix.user_id,
                item_id=ix.item_id,
                feedback_type=ix.event_type.value,
                timestamp=ix.timestamp.isoformat(),
            )
        logger.info("synced %d interactions to gorse", len(interactions))

    await gorse.close()


async def _index_all_embeddings():
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    from app.models.item import Item
    from app.services.embedding_service import get_embedding_service

    svc = get_embedding_service()
    async with AsyncSessionLocal() as db:
        items = (await db.execute(select(Item))).scalars().all()
        for item in items:
            text = f"{item.title} {item.genres or ''}".strip()
            svc.index_item(item.id, text)
    logger.info("indexed %d item embeddings", len(items))


async def _sync_single_feedback(user_id, item_id, feedback_type, timestamp):
    import uuid
    from app.services.gorse_client import GorseClient

    gorse = GorseClient()
    await gorse.insert_feedback(
        user_id=uuid.UUID(user_id),
        item_id=uuid.UUID(item_id),
        feedback_type=feedback_type,
        timestamp=timestamp,
    )
    await gorse.close()
