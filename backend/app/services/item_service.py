import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate
from app.core.logging import get_logger

logger = get_logger(__name__)


class ItemService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: ItemCreate) -> Item:
        item = Item(**data.model_dump())
        self.db.add(item)
        await self.db.flush()
        logger.info("item_created", item_id=str(item.id), title=item.title)
        return item

    async def get_by_id(self, item_id: uuid.UUID) -> Item:
        result = await self.db.execute(select(Item).where(Item.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Item {item_id} not found")
        return item

    async def list_items(self, offset: int = 0, limit: int = 20) -> tuple[list[Item], int]:
        count_result = await self.db.execute(select(func.count()).select_from(Item))
        total = count_result.scalar_one()

        result = await self.db.execute(
            select(Item).order_by(Item.avg_rating.desc()).offset(offset).limit(limit)
        )
        return result.scalars().all(), total

    async def update(self, item_id: uuid.UUID, data: ItemUpdate) -> Item:
        item = await self.get_by_id(item_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        await self.db.flush()
        return item

    async def get_popular(self, limit: int = 50) -> list[Item]:
        result = await self.db.execute(
            select(Item)
            .where(Item.rating_count > 0)
            .order_by(Item.avg_rating.desc(), Item.rating_count.desc())
            .limit(limit)
        )
        return result.scalars().all()
