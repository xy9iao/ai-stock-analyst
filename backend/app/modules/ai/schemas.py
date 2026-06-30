"""Request/response schemas for AI reports."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, model_validator


class ReportType(str, Enum):
    SINGLE_STOCK = "single_stock"
    PORTFOLIO = "portfolio"


class ReportRequest(BaseModel):
    """POST body. `ticker` is required for single_stock, ignored for portfolio."""

    report_type: ReportType
    ticker: str | None = None

    @model_validator(mode="after")
    def _require_ticker_for_single_stock(self) -> "ReportRequest":
        if self.report_type == ReportType.SINGLE_STOCK and not (self.ticker or "").strip():
            raise ValueError("ticker is required for a single_stock report")
        return self


class ReportRead(BaseModel):
    """A stored report returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    report_type: str
    title: str
    content_markdown: str
    created_at: datetime
