"""HTTP routes for the watchlist (the API surface)."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.demo_session import get_session_id
from app.modules.watchlist import service
from app.modules.watchlist.schemas import (
    WatchlistItemCreate,
    WatchlistItemRead,
    WatchlistItemUpdate,
)

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])


@router.get("")
def list_items(
    db: Session = Depends(get_db), session_id: str = Depends(get_session_id)
) -> list[WatchlistItemRead]:
    return service.list_items(db, session_id)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_item(
    data: WatchlistItemCreate,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
) -> WatchlistItemRead:
    return service.create_item(db, data, session_id)


@router.get("/{item_id}")
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
) -> WatchlistItemRead:
    return service.get_item(db, item_id, session_id)


@router.patch("/{item_id}")
def update_item(
    item_id: int,
    data: WatchlistItemUpdate,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
) -> WatchlistItemRead:
    return service.update_item(db, item_id, data, session_id)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
) -> None:
    service.delete_item(db, item_id, session_id)
