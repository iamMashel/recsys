import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.interaction import EventType


class InteractionCreate(BaseModel):
    item_id: uuid.UUID
    event_type: EventType
    rating: float | None = None


class InteractionRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    item_id: uuid.UUID
    event_type: EventType
    rating: float | None
    timestamp: datetime

    model_config = {"from_attributes": True}
