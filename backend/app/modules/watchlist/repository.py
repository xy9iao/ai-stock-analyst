"""Database access for watchlist items. Only this layer touches the Session."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import WatchlistItem
from app.modules.watchlist.schemas import WatchlistItemCreate, WatchlistItemUpdate


def list_items(db: Session, session_id: str) -> list[WatchlistItem]:
    return db.scalars(select(WatchlistItem).where(WatchlistItem.session_id == session_id)).all()


def get_item(db: Session, item_id: int, session_id: str) -> WatchlistItem | None:
    item = db.get(WatchlistItem, item_id)
    # A row in another demo session's bucket is treated as nonexistent (404).
    if item is not None and item.session_id != session_id:
        return None
    return item


def create_item(db: Session, data: WatchlistItemCreate, session_id: str) -> WatchlistItem:
    item = WatchlistItem(**data.model_dump(), session_id=session_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_item(db: Session, item: WatchlistItem, data: WatchlistItemUpdate) -> WatchlistItem:
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item: WatchlistItem) -> None:
    db.delete(item)
    db.commit()
