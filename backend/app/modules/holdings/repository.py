"""Database access for holdings. Only this layer touches the Session."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Holding
from app.modules.holdings.schemas import HoldingCreate, HoldingUpdate


def list_holdings(db: Session) -> list[Holding]:
    return db.scalars(select(Holding)).all()


def get_holding(db: Session, holding_id: int) -> Holding | None:
    return db.get(Holding, holding_id)


def create_holding(db: Session, data: HoldingCreate) -> Holding:
    holding = Holding(**data.model_dump())
    db.add(holding)
    db.commit()
    db.refresh(holding)  # reload so id/created_at/updated_at are populated
    return holding


def update_holding(db: Session, holding: Holding, data: HoldingUpdate) -> Holding:
    # exclude_unset=True -> only the fields the client actually sent (partial update)
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(holding, field, value)
    db.commit()
    db.refresh(holding)
    return holding


def delete_holding(db: Session, holding: Holding) -> None:
    db.delete(holding)
    db.commit()
