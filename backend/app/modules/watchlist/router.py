"""HTTP routes for the watchlist (the API surface)."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.watchlist import service
from app.modules.watchlist.schemas import (
    WatchlistItemCreate,
    WatchlistItemRead,
    WatchlistItemUpdate,
)

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])


@router.get("")
def list_items(db: Session = Depends(get_db)) -> list[WatchlistItemRead]:
    return service.list_items(db)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_item(data: WatchlistItemCreate, db: Session = Depends(get_db)) -> WatchlistItemRead:
    return service.create_item(db, data)


@router.get("/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)) -> WatchlistItemRead:
    return service.get_item(db, item_id)


@router.patch("/{item_id}")
def update_item(
    item_id: int, data: WatchlistItemUpdate, db: Session = Depends(get_db)
) -> WatchlistItemRead:
    return service.update_item(db, item_id, data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)) -> None:
    service.delete_item(db, item_id)
