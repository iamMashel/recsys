import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.models.interaction import Interaction
from app.models.item import Item
from app.schemas.interaction import InteractionCreate
from app.core.logging import get_logger

logger = get_logger(__name__)


class InteractionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record(self, user_id: uuid.UUID, data: InteractionCreate) -> Interaction:
        interaction = Interaction(
            user_id=user_id,
            item_id=data.item_id,
            event_type=data.event_type,
            rating=data.rating,
        )
        self.db.add(interaction)
        await self.db.flush()

        if data.rating is not None:
            await self._update_item_stats(data.item_id)

        logger.info(
            "interaction_recorded",
            user_id=str(user_id),
            item_id=str(data.item_id),
            event_type=data.event_type,
        )
        return interaction

    async def get_user_interactions(
        self, user_id: uuid.UUID, limit: int = 100
    ) -> list[Interaction]:
        result = await self.db.execute(
            select(Interaction)
            .where(Interaction.user_id == user_id)
            .order_by(Interaction.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def _update_item_stats(self, item_id: uuid.UUID) -> None:
        result = await self.db.execute(
            select(
                func.avg(Interaction.rating),
                func.count(Interaction.rating),
            ).where(
                Interaction.item_id == item_id,
                Interaction.rating.is_not(None),
            )
        )
        avg_rating, count = result.one()
        if avg_rating is not None:
            await self.db.execute(
                update(Item)
                .where(Item.id == item_id)
                .values(avg_rating=round(float(avg_rating), 2), rating_count=count)
            )
