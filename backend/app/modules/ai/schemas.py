"""Request/response schemas for AI reports."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReportType(str, Enum):
    SINGLE_STOCK = "single_stock"
    PORTFOLIO = "portfolio"
    RESEARCH = "research"


class ReportRequest(BaseModel):
    """POST body. `ticker` is required for single_stock; `query` for research."""

    report_type: ReportType
    ticker: str | None = None
    query: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def _require_type_specific_fields(self) -> "ReportRequest":
        if self.report_type == ReportType.SINGLE_STOCK and not (self.ticker or "").strip():
            raise ValueError("ticker is required for a single_stock report")
        if self.report_type == ReportType.RESEARCH and not (self.query or "").strip():
            raise ValueError("query is required for a research report")
        return self


class ReportRead(BaseModel):
    """A stored report returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    report_type: str
    title: str
    content_markdown: str
    created_at: datetime
