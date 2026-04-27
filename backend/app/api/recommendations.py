import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.recommendation import RecommendationResponse
from app.services.recommender import RecommenderService
from app.services.gorse_client import GorseClient
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/me", response_model=RecommendationResponse)
async def my_recommendations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    gorse = GorseClient()
    service = RecommenderService(db=db, gorse=gorse)
    return await service.get_recommendations(current_user.id)


@router.get("/{user_id}", response_model=RecommendationResponse)
async def get_user_recommendations(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    gorse = GorseClient()
    service = RecommenderService(db=db, gorse=gorse)
    return await service.get_recommendations(user_id)
