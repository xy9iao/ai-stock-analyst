"""Business logic for holdings: orchestrates the repository and enforces rules."""

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import Holding
from app.modules.holdings import repository
from app.modules.holdings.schemas import HoldingCreate, HoldingUpdate


def list_holdings(db: Session, session_id: str) -> list[Holding]:
    return repository.list_holdings(db, session_id)


def get_holding(db: Session, holding_id: int, session_id: str) -> Holding:
    holding = repository.get_holding(db, holding_id, session_id)
    if holding is None:
        raise AppError(
            code="holding_not_found",
            message=f"Holding with id {holding_id} not found",
            status_code=404,
        )
    return holding


def create_holding(db: Session, data: HoldingCreate, session_id: str) -> Holding:
    return repository.create_holding(db, data, session_id)


def update_holding(db: Session, holding_id: int, data: HoldingUpdate, session_id: str) -> Holding:
    holding = get_holding(db, holding_id, session_id)  # raises 404 if missing
    return repository.update_holding(db, holding, data)


def delete_holding(db: Session, holding_id: int, session_id: str) -> None:
    holding = get_holding(db, holding_id, session_id)  # raises 404 if missing
    repository.delete_holding(db, holding)
