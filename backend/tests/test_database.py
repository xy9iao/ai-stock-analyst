from sqlalchemy.orm import Session

from app.core.database import get_db


def test_get_db_yields_sqlalchemy_session() -> None:
    db_generator = get_db()
    db = next(db_generator)

    try:
        assert isinstance(db, Session)
    finally:
        try:
            next(db_generator)
        except StopIteration:
            pass
