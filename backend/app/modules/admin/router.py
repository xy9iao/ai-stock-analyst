"""Admin/ops endpoints: the LLM master switch (token-gated) and public stats.

The switch endpoint is protected by a shared admin token (X-Admin-Token header,
compared against ADMIN_TOKEN from the environment). /api/stats is public — it
exposes only aggregate token/latency numbers, no user data.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core import llm_switch
from app.core.config import settings
from app.core.database import get_db
from app.core.errors import AppError
from app.models import LlmCall
from app.modules.admin.schemas import KindStats, LlmSwitchRead, LlmSwitchRequest, StatsRead

router = APIRouter(prefix="/api", tags=["admin"])


def _require_admin(x_admin_token: str | None) -> None:
    if not settings.admin_token or x_admin_token != settings.admin_token:
        raise AppError(code="admin_forbidden", message="Invalid admin token", status_code=403)


@router.post("/admin/llm")
def set_llm_switch(
    request: LlmSwitchRequest,
    db: Session = Depends(get_db),
    x_admin_token: str | None = Header(default=None),
) -> LlmSwitchRead:
    _require_admin(x_admin_token)
    ttl = request.ttl_minutes or settings.llm_switch_ttl_minutes
    until = llm_switch.set_enabled(db, enabled=request.enabled, ttl_minutes=ttl)
    return LlmSwitchRead(enabled=request.enabled, enabled_until=until)


@router.get("/admin/llm")
def get_llm_switch(
    db: Session = Depends(get_db),
    x_admin_token: str | None = Header(default=None),
) -> LlmSwitchRead:
    _require_admin(x_admin_token)
    until = llm_switch.enabled_until(db)
    enabled = until is not None and datetime.now(timezone.utc) < until
    return LlmSwitchRead(enabled=enabled, enabled_until=until)


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)) -> StatsRead:
    rows = db.execute(
        select(
            LlmCall.kind,
            func.count(LlmCall.id),
            func.coalesce(func.sum(LlmCall.prompt_tokens), 0),
            func.coalesce(func.sum(LlmCall.completion_tokens), 0),
            func.coalesce(func.sum(LlmCall.cached_tokens), 0),
            func.coalesce(func.avg(LlmCall.latency_ms), 0),
        ).group_by(LlmCall.kind)
    ).all()

    by_kind = [
        KindStats(
            kind=kind,
            calls=calls,
            prompt_tokens=int(prompt),
            completion_tokens=int(completion),
            cached_tokens=int(cached),
            avg_latency_ms=int(avg_latency),
        )
        for kind, calls, prompt, completion, cached, avg_latency in rows
    ]
    total_calls = sum(k.calls for k in by_kind)
    total_latency = sum(k.avg_latency_ms * k.calls for k in by_kind)
    return StatsRead(
        total_calls=total_calls,
        total_prompt_tokens=sum(k.prompt_tokens for k in by_kind),
        total_completion_tokens=sum(k.completion_tokens for k in by_kind),
        total_cached_tokens=sum(k.cached_tokens for k in by_kind),
        avg_latency_ms=int(total_latency / total_calls) if total_calls else 0,
        by_kind=by_kind,
    )
