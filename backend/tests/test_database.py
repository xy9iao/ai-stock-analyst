from sqlalchemy.orm import Session

from app.core.database import check_database_connection, get_db


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

def test_check_database_connection(monkeypatch) -> None:
    class FakeResult:
        def scalar_one(self) -> int:
            return 1

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback) -> None:
            return None

        def execute(self, statement):
            return FakeResult()

    class FakeEngine:
        def connect(self):
            return FakeConnection()

    monkeypatch.setattr("app.core.database.engine", FakeEngine())

    assert check_database_connection() is True
