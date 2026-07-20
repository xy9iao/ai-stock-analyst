"""Pydantic schemas for the admin/ops endpoints."""

from datetime import datetime

from pydantic import BaseModel


class LlmSwitchRequest(BaseModel):
    enabled: bool
    ttl_minutes: int | None = None  # defaults to settings.llm_switch_ttl_minutes


class LlmSwitchRead(BaseModel):
    enabled: bool
    enabled_until: datetime | None


class KindStats(BaseModel):
    kind: str
    calls: int
    prompt_tokens: int
    completion_tokens: int
    cached_tokens: int
    avg_latency_ms: int


class StatsRead(BaseModel):
    total_calls: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_cached_tokens: int
    avg_latency_ms: int
    by_kind: list[KindStats]
