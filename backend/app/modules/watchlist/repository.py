"""Database access for watchlist items. Only this layer touches the Session."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import WatchlistItem
from app.modules.watchlist.schemas import WatchlistItemCreate, WatchlistItemUpdate


def list_items(db: Session) -> list[WatchlistItem]:
    return db.scalars(select(WatchlistItem)).all()


def get_item(db: Session, item_id: int) -> WatchlistItem | None:
    return db.get(WatchlistItem, item_id)


def create_item(db: Session, data: WatchlistItemCreate) -> WatchlistItem:
    item = WatchlistItem(**data.model_dump())
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
