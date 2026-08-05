from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app
from MAIN.main import initialize_database, seed_sample_data
from database.databade import Database, db as global_db


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    db_path = tmp_path / "api_test.db"
    schema_path = Path(__file__).resolve().parents[1] / "database" / "branch.sql"
    initialize_database(str(db_path), str(schema_path))
    test_db = Database(str(db_path))
    seed_sample_data(test_db)

    # Patch global_db connection used by services
    monkeypatch.setattr(global_db, "connection", test_db.connection)
    monkeypatch.setattr(global_db, "cursor", test_db.cursor)

    yield test_db
    test_db.close_()


client = TestClient(app)


def test_auth_login_api():
    res = client.post("/auth/login", json={"account_no": 1, "password": "password1"})
    assert res.status_code == 200
    assert res.json()["message"] == "Login successful"

    res_fail = client.post("/auth/login", json={"account_no": 1, "password": "wrong"})
    assert res_fail.status_code == 401


def test_list_customers_api():
    res = client.get("/customers/")
    assert res.status_code == 200
    customers = res.json()
    assert len(customers) >= 3
    assert customers[0]["name"] == "Alice"
    assert customers[0]["account_no"] == 1


def test_create_customer_api():
    payload = {
        "name": "David Miller",
        "password": "passDavid123",
        "personal_id_type": "PAN",
        "personal_id": "D987654",
        "address": "999 Palm St",
        "phone_no": "9876543210",
        "email": "david@example.com",
        "branch_no": 1,
    }
    res = client.post("/customers/", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "customer_id" in data

    # Verify retrieval
    res_get = client.get(f"/customers/{data['customer_id']}")
    assert res_get.status_code == 200
    assert res_get.json()["name"] == "David Miller"


def test_update_customer_api():
    payload = {"name": "Alice Updated", "address": "99 Cherry Blvd"}
    res = client.put("/customers/1", json=payload)
    assert res.status_code == 200

    res_get = client.get("/customers/1")
    assert res_get.json()["name"] == "Alice Updated"


def test_delete_customer_api():
    payload = {"account_no": 1, "password": "password1"}
    res = client.request("DELETE", "/customers/3", json=payload)
    assert res.status_code == 200

    res_get = client.get("/customers/3")
    assert res_get.status_code == 404


def test_deposit_api():
    res = client.post(
        "/transactions/deposit",
        json={"account_no": 1, "password": "password1", "amount": 500, "reference": "Bonus"},
    )
    assert res.status_code == 200
    assert res.json()["balance"] == 1500.0


def test_withdraw_api():
    res = client.post(
        "/transactions/withdraw",
        json={"account_no": 1, "password": "password1", "amount": 200, "reference": "ATM"},
    )
    assert res.status_code == 200
    assert res.json()["balance"] == 800.0


def test_withdraw_api_insufficient_funds():
    res = client.post(
        "/transactions/withdraw",
        json={"account_no": 1, "password": "password1", "amount": 99999},
    )
    assert res.status_code == 400


def test_transfer_api():
    res = client.post(
        "/transactions/transfer",
        json={
            "sender_account_no": 1,
            "password": "password1",
            "receiver_account_no": 2,
            "amount": 300,
            "reference": "Dinner Split",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["sender_balance"] == 700.0
    assert data["receiver_balance"] == 1300.0


def test_metrics_and_history_api():
    # Make a deposit first
    client.post(
        "/transactions/deposit",
        json={"account_no": 1, "password": "password1", "amount": 100},
    )

    res_metrics = client.get("/transactions/metrics")
    assert res_metrics.status_code == 200
    metrics = res_metrics.json()
    assert metrics["total_customers"] >= 3
    assert metrics["active_accounts"] >= 1

    res_history = client.get("/transactions/history")
    assert res_history.status_code == 200
    history = res_history.json()
    assert len(history) >= 1
