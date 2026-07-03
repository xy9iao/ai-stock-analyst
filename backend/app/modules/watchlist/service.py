"""Business logic for watchlist items."""

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import WatchlistItem
from app.modules.watchlist import repository
from app.modules.watchlist.schemas import WatchlistItemCreate, WatchlistItemUpdate


def list_items(db: Session, session_id: str) -> list[WatchlistItem]:
    return repository.list_items(db, session_id)


def get_item(db: Session, item_id: int, session_id: str) -> WatchlistItem:
    item = repository.get_item(db, item_id, session_id)
    if item is None:
        raise AppError(
            code="watchlist_item_not_found",
            message=f"Watchlist item with id {item_id} not found",
            status_code=404,
        )
    return item


def create_item(db: Session, data: WatchlistItemCreate, session_id: str) -> WatchlistItem:
    return repository.create_item(db, data, session_id)


def update_item(
    db: Session, item_id: int, data: WatchlistItemUpdate, session_id: str
) -> WatchlistItem:
    item = get_item(db, item_id, session_id)  # raises 404 if missing
    return repository.update_item(db, item, data)


def delete_item(db: Session, item_id: int, session_id: str) -> None:
    item = get_item(db, item_id, session_id)  # raises 404 if missing
    repository.delete_item(db, item)
