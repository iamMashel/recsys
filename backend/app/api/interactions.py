from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.interaction import InteractionCreate, InteractionRead
from app.services.interaction_service import InteractionService
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("/", response_model=InteractionRead, status_code=201)
async def record_interaction(
    data: InteractionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = InteractionService(db)
    interaction = await service.record(current_user.id, data)

    # Dispatch to Celery worker — keeps this endpoint fast
    from workers.tasks import sync_single_feedback
    sync_single_feedback.delay(
        str(current_user.id),
        str(data.item_id),
        data.event_type.value,
        interaction.timestamp.isoformat(),
    )

    return interaction


@router.get("/me", response_model=list[InteractionRead])
async def my_interactions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = InteractionService(db)
    return await service.get_user_interactions(current_user.id)
