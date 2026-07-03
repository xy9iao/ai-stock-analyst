"""Anonymous demo-session isolation (NOT a user/auth system).

In demo mode every visitor gets a random `session_id` cookie, and all user data
(holdings, watchlist, reports, chat) is bucketed by it, so demo visitors can't
see or pollute each other's data. Locally (demo_mode off) everything lives in a
single permanent bucket, LOCAL_SESSION_ID, which preserves pre-demo behavior
and data. Idle demo buckets are deleted after a TTL.
"""

import secrets
import time
from datetime import datetime, timedelta, timezone

from fastapi import Request, Response
from sqlalchemy import delete

from app.core.config import settings

LOCAL_SESSION_ID = "local"
SESSION_COOKIE = "session_id"

# Throttle TTL cleanup to at most once per hour per process.
_CLEANUP_INTERVAL_SECONDS = 3600
_last_cleanup: float = 0.0


def get_session_id(request: Request) -> str:
    """Dependency: the demo bucket for this request (set by the middleware)."""
    return getattr(request.state, "session_id", LOCAL_SESSION_ID)


async def session_middleware(request: Request, call_next) -> Response:
    if not settings.demo_mode:
        request.state.session_id = LOCAL_SESSION_ID
        return await call_next(request)

    session_id = request.cookies.get(SESSION_COOKIE)
    is_new = not session_id or len(session_id) > 64 or session_id == LOCAL_SESSION_ID
    if is_new:
        session_id = secrets.token_urlsafe(24)
        _maybe_cleanup_expired()

    request.state.session_id = session_id
    response = await call_next(request)
    if is_new:
        response.set_cookie(
            SESSION_COOKIE,
            session_id,
            max_age=settings.demo_session_ttl_days * 86400,
            httponly=True,
            samesite="lax",
        )
    return response


def _maybe_cleanup_expired() -> None:
    """Delete data from demo sessions idle past the TTL (throttled, best-effort)."""
    global _last_cleanup
    now = time.monotonic()
    if now - _last_cleanup < _CLEANUP_INTERVAL_SECONDS:
        return
    _last_cleanup = now

    # Imported here to avoid import cycles at app startup.
    from app.core.database import SessionLocal
    from app.models import ChatMessage, ChatSession, Holding, Report, WatchlistItem

    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.demo_session_ttl_days)
    db = SessionLocal()
    try:
        stale_chat_ids = [
            row.id
            for row in db.query(ChatSession)
            .filter(ChatSession.session_id != LOCAL_SESSION_ID, ChatSession.updated_at < cutoff)
            .all()
        ]
        if stale_chat_ids:
            db.execute(delete(ChatMessage).where(ChatMessage.chat_session_id.in_(stale_chat_ids)))
            db.execute(delete(ChatSession).where(ChatSession.id.in_(stale_chat_ids)))
        for model in (Holding, WatchlistItem, Report):
            db.execute(
                delete(model).where(model.session_id != LOCAL_SESSION_ID, model.updated_at < cutoff)
            )
        db.commit()
    except Exception:  # cleanup must never take down a request
        db.rollback()
    finally:
        db.close()
