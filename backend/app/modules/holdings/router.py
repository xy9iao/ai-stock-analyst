"""HTTP routes for holdings (the API surface)."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.demo_session import get_session_id
from app.modules.holdings import service
from app.modules.holdings.schemas import HoldingCreate, HoldingRead, HoldingUpdate

router = APIRouter(prefix="/api/holdings", tags=["holdings"])


@router.get("")
def list_holdings(
    db: Session = Depends(get_db), session_id: str = Depends(get_session_id)
) -> list[HoldingRead]:
    return service.list_holdings(db, session_id)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_holding(
    data: HoldingCreate,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
) -> HoldingRead:
    return service.create_holding(db, data, session_id)


@router.get("/{holding_id}")
def get_holding(
    holding_id: int,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
) -> HoldingRead:
    return service.get_holding(db, holding_id, session_id)


@router.patch("/{holding_id}")
def update_holding(
    holding_id: int,
    data: HoldingUpdate,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
) -> HoldingRead:
    return service.update_holding(db, holding_id, data, session_id)


@router.delete("/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holding(
    holding_id: int,
    db: Session = Depends(get_db),
    session_id: str = Depends(get_session_id),
) -> None:
    service.delete_holding(db, holding_id, session_id)
