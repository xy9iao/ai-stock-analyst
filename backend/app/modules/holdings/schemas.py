"""Pydantic schemas for the Holdings API (request/response contracts)."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HoldingBase(BaseModel):
    """Optional descriptive fields shared by create and read."""

    company_name: str | None = None
    sector: str | None = None
    notes: str | None = None
    investment_thesis: str | None = None
    target_allocation: Decimal | None = Field(default=None, ge=0, le=1)


class HoldingCreate(HoldingBase):
    """Request body for creating a holding."""

    ticker: str = Field(max_length=16)
    shares: Decimal = Field(gt=0)
    average_cost: Decimal = Field(ge=0)

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        return value.strip().upper()


class HoldingUpdate(BaseModel):
    """Request body for updating a holding. All fields optional (partial update)."""

    ticker: str | None = Field(default=None, max_length=16)
    shares: Decimal | None = Field(default=None, gt=0)
    average_cost: Decimal | None = Field(default=None, ge=0)
    company_name: str | None = None
    sector: str | None = None
    notes: str | None = None
    investment_thesis: str | None = None
    target_allocation: Decimal | None = Field(default=None, ge=0, le=1)

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str | None) -> str | None:
        return value.strip().upper() if value is not None else value


class HoldingRead(HoldingBase):
    """Response body returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    shares: Decimal
    average_cost: Decimal
    created_at: datetime
    updated_at: datetime
