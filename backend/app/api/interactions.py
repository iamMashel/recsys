from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.interaction import InteractionCreate, InteractionRead
from app.services.interaction_service import InteractionService
from app.services.auth_service import get_current_user
from app.core.logging import get_logger

router = APIRouter(prefix="/interactions", tags=["interactions"])
logger = get_logger(__name__)


def _dispatch_to_gorse(user_id, item_id, event_type, timestamp):
    """Fire-and-forget Gorse sync via Celery. No-op if Celery is unavailable."""
    try:
        from workers.tasks import sync_single_feedback
        sync_single_feedback.delay(str(user_id), str(item_id), event_type, timestamp)
    except Exception as e:
        logger.warning("celery_dispatch_skipped", error=str(e))


@router.post("/", response_model=InteractionRead, status_code=201)
async def record_interaction(
    data: InteractionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = InteractionService(db)
    interaction = await service.record(current_user.id, data)
    _dispatch_to_gorse(current_user.id, data.item_id, data.event_type.value, interaction.timestamp.isoformat())
    return interaction


@router.get("/me", response_model=list[InteractionRead])
async def my_interactions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = InteractionService(db)
    return await service.get_user_interactions(current_user.id)
