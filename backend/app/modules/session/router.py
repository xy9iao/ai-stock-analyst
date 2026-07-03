"""Demo-session endpoint: reset drops the cookie so the next request gets a
fresh, empty bucket (used by the "New demo session" button; harmless locally).
"""

from fastapi import APIRouter, Response, status

from app.core.demo_session import SESSION_COOKIE

router = APIRouter(prefix="/api/session", tags=["session"])


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_session(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE)
