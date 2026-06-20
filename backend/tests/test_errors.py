from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.errors import AppError, add_error_handlers


def test_app_error_handler_returns_consistent_response() -> None:
    test_app = FastAPI()
    add_error_handlers(test_app)

    @test_app.get("/raise-error")
    def raise_error() -> None:
        raise AppError(
            code="example_error",
            message="Example error message",
            status_code=418,
        )

    client = TestClient(test_app)

    response = client.get("/raise-error")

    assert response.status_code == 418
    assert response.json() == {
        "detail": {
            "code": "example_error",
            "message": "Example error message",
        }
    }
