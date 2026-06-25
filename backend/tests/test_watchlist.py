"""CRUD + validation tests for the watchlist API."""

from fastapi.testclient import TestClient


def make_item(client: TestClient, **overrides) -> dict:
    payload = {"ticker": "nvda"}
    payload.update(overrides)
    return client.post("/api/watchlist", json=payload).json()


def test_create_normalizes_ticker_and_returns_201(client: TestClient) -> None:
    res = client.post(
        "/api/watchlist",
        json={"ticker": " nvda ", "reason_to_watch": "AI demand"},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["id"] >= 1
    assert body["ticker"] == "NVDA"
    assert body["reason_to_watch"] == "AI demand"


def test_list_returns_created_items(client: TestClient) -> None:
    make_item(client, ticker="AAPL")
    make_item(client, ticker="MSFT")
    res = client.get("/api/watchlist")
    assert res.status_code == 200
    assert {"AAPL", "MSFT"} <= {i["ticker"] for i in res.json()}


def test_get_existing_and_missing(client: TestClient) -> None:
    created = make_item(client)
    assert client.get(f"/api/watchlist/{created['id']}").status_code == 200

    missing = client.get("/api/watchlist/99999")
    assert missing.status_code == 404
    assert missing.json()["detail"]["code"] == "watchlist_item_not_found"


def test_update_changes_only_sent_fields(client: TestClient) -> None:
    created = make_item(client)
    res = client.patch(f"/api/watchlist/{created['id']}", json={"sector": "Tech"})
    assert res.status_code == 200
    assert res.json()["sector"] == "Tech"
    assert res.json()["ticker"] == "NVDA"

    assert client.patch("/api/watchlist/99999", json={"sector": "Tech"}).status_code == 404


def test_delete_then_gone(client: TestClient) -> None:
    created = make_item(client)
    assert client.delete(f"/api/watchlist/{created['id']}").status_code == 204
    assert client.get(f"/api/watchlist/{created['id']}").status_code == 404
    assert client.delete("/api/watchlist/99999").status_code == 404


def test_missing_ticker_rejected_with_422(client: TestClient) -> None:
    assert client.post("/api/watchlist", json={"sector": "Tech"}).status_code == 422
