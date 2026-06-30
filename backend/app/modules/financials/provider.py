"""The financial-data provider interface (structural Protocol)."""

from typing import Protocol

from app.modules.financials.schemas import FinancialSnapshot


class FinancialDataProvider(Protocol):
    def get_snapshot(self, ticker: str) -> FinancialSnapshot:
        """Return the latest financial snapshot, or raise AppError(404) if unknown."""
        ...
