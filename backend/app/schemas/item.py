import uuid
from datetime import datetime
from pydantic import BaseModel


class ItemCreate(BaseModel):
    title: str
    genres: str | None = None
    description: str | None = None
    release_year: int | None = None
    movielens_id: int | None = None


class ItemUpdate(BaseModel):
    title: str | None = None
    genres: str | None = None
    description: str | None = None
    release_year: int | None = None


class ItemRead(BaseModel):
    id: uuid.UUID
    title: str
    genres: str | None
    description: str | None
    release_year: int | None
    avg_rating: float
    rating_count: int
    created_at: datetime

    model_config = {"from_attributes": True}
