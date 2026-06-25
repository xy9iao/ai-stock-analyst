"""CRUD + validation tests for the holdings API."""

from decimal import Decimal

from fastapi.testclient import TestClient


def make_holding(client: TestClient, **overrides) -> dict:
    payload = {"ticker": "nvda", "shares": "3", "average_cost": "850.5"}
    payload.update(overrides)
    return client.post("/api/holdings", json=payload).json()


def test_create_normalizes_ticker_and_returns_201(client: TestClient) -> None:
    res = client.post(
        "/api/holdings",
        json={"ticker": " nvda ", "shares": "3", "average_cost": "850.5"},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["id"] >= 1
    assert body["ticker"] == "NVDA"  # validator stripped + uppercased
    assert Decimal(str(body["shares"])) == Decimal("3")
    assert "created_at" in body


def test_list_returns_created_holdings(client: TestClient) -> None:
    make_holding(client, ticker="AAPL")
    make_holding(client, ticker="MSFT")
    res = client.get("/api/holdings")
    assert res.status_code == 200
    assert {"AAPL", "MSFT"} <= {h["ticker"] for h in res.json()}


def test_get_existing_and_missing(client: TestClient) -> None:
    created = make_holding(client)
    ok = client.get(f"/api/holdings/{created['id']}")
    assert ok.status_code == 200
    assert ok.json()["id"] == created["id"]

    missing = client.get("/api/holdings/99999")
    assert missing.status_code == 404
    assert missing.json()["detail"]["code"] == "holding_not_found"


def test_update_changes_only_sent_fields(client: TestClient) -> None:
    created = make_holding(client)
    res = client.patch(f"/api/holdings/{created['id']}", json={"sector": "Tech"})
    assert res.status_code == 200
    assert res.json()["sector"] == "Tech"
    assert res.json()["ticker"] == "NVDA"  # untouched fields survive

    assert client.patch("/api/holdings/99999", json={"sector": "Tech"}).status_code == 404


def test_delete_then_gone(client: TestClient) -> None:
    created = make_holding(client)
    assert client.delete(f"/api/holdings/{created['id']}").status_code == 204
    assert client.get(f"/api/holdings/{created['id']}").status_code == 404
    assert client.delete("/api/holdings/99999").status_code == 404


def test_negative_shares_rejected_with_422(client: TestClient) -> None:
    res = client.post(
        "/api/holdings",
        json={"ticker": "NVDA", "shares": "-5", "average_cost": "10"},
    )
    assert res.status_code == 422


def test_missing_ticker_rejected_with_422(client: TestClient) -> None:
    res = client.post("/api/holdings", json={"shares": "1", "average_cost": "10"})
    assert res.status_code == 422
