from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class StockNote(TimestampMixin, Base):
    __tablename__ = "stock_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False)
