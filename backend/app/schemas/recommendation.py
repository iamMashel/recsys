import uuid
from pydantic import BaseModel


class RecommendedItem(BaseModel):
    item_id: uuid.UUID
    title: str
    genres: str | None
    score: float
    reason: str  # "collaborative", "semantic", "hybrid"


class RecommendationResponse(BaseModel):
    user_id: uuid.UUID
    results: list[RecommendedItem]
    total: int
