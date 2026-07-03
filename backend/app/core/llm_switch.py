"""The LLM master switch — layer 2 of the demo cost defense.

State is a single row in the existing `settings` key-value table:
`llm_enabled_until` = ISO timestamp. In demo mode the switch is OFF by default
(row absent or in the past) and enabling it always carries a TTL, so a demo
left unattended can never burn credit indefinitely. Locally (demo_mode off)
the switch is not enforced.

Layer 1 is the DeepSeek prepaid balance (hard budget cap, no auto-recharge);
layer 3 is the per-session call caps in the ai/chat services.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import Setting

_KEY = "llm_enabled_until"


def _get(db: Session) -> Setting | None:
    return db.query(Setting).filter(Setting.key == _KEY).one_or_none()


def enabled_until(db: Session) -> datetime | None:
    row = _get(db)
    if row is None or not row.value:
        return None
    try:
        return datetime.fromisoformat(row.value)
    except ValueError:
        return None


def is_enabled(db: Session) -> bool:
    until = enabled_until(db)
    return until is not None and datetime.now(timezone.utc) < until


def set_enabled(db: Session, *, enabled: bool, ttl_minutes: int) -> datetime | None:
    """Turn the switch on (for ttl_minutes) or off. Returns the new expiry."""
    until = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes) if enabled else None
    row = _get(db)
    value = until.isoformat() if until else ""
    if row is None:
        db.add(Setting(key=_KEY, value=value))
    else:
        row.value = value
    db.commit()
    return until
