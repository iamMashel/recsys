import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.item import ItemCreate, ItemRead
from app.services.item_service import ItemService
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemRead, status_code=201)
async def create_item(
    data: ItemCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = ItemService(db)
    return await service.create(data)


@router.get("/", response_model=dict)
async def list_items(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = ItemService(db)
    items, total = await service.list_items(offset=offset, limit=limit)
    return {"items": items, "total": total, "offset": offset, "limit": limit}


@router.get("/{item_id}", response_model=ItemRead)
async def get_item(item_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = ItemService(db)
    return await service.get_by_id(item_id)
