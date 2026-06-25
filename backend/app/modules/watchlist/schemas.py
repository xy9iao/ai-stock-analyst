"""Pydantic schemas for the Watchlist API (request/response contracts)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WatchlistItemBase(BaseModel):
    """Optional descriptive fields shared by create and read."""

    company_name: str | None = None
    sector: str | None = None
    reason_to_watch: str | None = None
    notes: str | None = None


class WatchlistItemCreate(WatchlistItemBase):
    """Request body for adding a watchlist item."""

    ticker: str = Field(max_length=16)

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        return value.strip().upper()


class WatchlistItemUpdate(BaseModel):
    """Request body for updating a watchlist item. All fields optional."""

    ticker: str | None = Field(default=None, max_length=16)
    company_name: str | None = None
    sector: str | None = None
    reason_to_watch: str | None = None
    notes: str | None = None

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str | None) -> str | None:
        return value.strip().upper() if value is not None else value


class WatchlistItemRead(WatchlistItemBase):
    """Response body returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    created_at: datetime
    updated_at: datetime
