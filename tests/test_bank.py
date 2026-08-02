import sqlite3
from pathlib import Path

import pytest

from MAIN.main import initialize_database, seed_sample_data
from Transcation.transaction import TransactionEngine
from auth import email_otp
from auth.AUTH import AuthenticationCheck
from customerservice.customer import Customer
from database.databade import Database


@pytest.fixture()
def bank_db(tmp_path):
    db_path = tmp_path / "bank_test.db"
    schema_path = Path(__file__).resolve().parents[1] / "database" / "branch.sql"
    initialize_database(str(db_path), str(schema_path))
    db = Database(str(db_path))
    seed_sample_data(db)
    yield db
    db.close_()


def test_initialize_database_creates_required_tables(tmp_path):
    db_path = tmp_path / "init_test.db"
    schema_path = Path(__file__).resolve().parents[1] / "database" / "branch.sql"

    initialize_database(str(db_path), str(schema_path))

    with sqlite3.connect(db_path) as conn:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }

    assert {"customer", "balance", "branch_details"}.issubset(tables)


def test_authentication_login_succeeds_for_valid_credentials(bank_db):
    auth = AuthenticationCheck(db=bank_db, ID_no=1, PASSWORD="password1")

    assert auth.login() is True


def test_authentication_login_fails_for_invalid_credentials(bank_db):
    auth = AuthenticationCheck(db=bank_db, ID_no=999, PASSWORD="wrong")

    assert auth.login() is False


def test_customer_update_pass_changes_password(bank_db, monkeypatch):
    customer = Customer(bank_db, None, None)
    responses = iter(["NID", "A123", "new_secure_password"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(responses))

    assert customer.update_pass() is True

    row = bank_db.fetchone_(
        "SELECT password FROM customer WHERE personal_id_type = ? AND personal_id = ?",
        "NID",
        "A123",
    )
    assert row[0] == "new_secure_password"


def test_customer_delete_acc_removes_account(bank_db, monkeypatch):
    customer = Customer(bank_db, None, None)
    monkeypatch.setattr("builtins.input", lambda _prompt="": "1")

    assert customer.delete_acc() is True
    row = bank_db.fetchone_("SELECT ID_NO FROM customer WHERE ID_NO = ?", 1)
    assert row is None


def test_transaction_engine_deposit_and_withdraw(bank_db):
    engine = TransactionEngine(bank_db)

    assert engine.login(1, "password1") is True
    assert engine.deposit(250) == 1250

    assert engine.login(1, "password1") is True
    assert engine.withdraw(100) == 1150


def test_transaction_engine_transfer_between_accounts(bank_db):
    engine = TransactionEngine(bank_db)

    assert engine.login(1, "password1") is True
    result = engine.transfer(2, 200)

    assert result["sender_balance"] == 800
    assert result["receiver_balance"] == 1200


def test_transaction_engine_requires_login_for_balance(bank_db):
    engine = TransactionEngine(bank_db)

    assert engine.get_balance(1) == 1000
    assert engine.current_account is None


def test_email_otp_raises_for_missing_password(monkeypatch):
    monkeypatch.delenv("EMAIL_OTP_PASSWORD", raising=False)

    with pytest.raises(ValueError):
        email_otp.otp("user@example.com")


def test_email_otp_returns_code_and_sends_message(monkeypatch):
    class FakeSMTP:
        def __init__(self, *args):
            self.sent_messages = []

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def login(self, sender_email, password):
            self.login_details = (sender_email, password)

        def send_message(self, message):
            self.sent_messages.append(message)

    fake_smtp = FakeSMTP()
    monkeypatch.setattr(email_otp.smtplib, "SMTP_SSL", lambda host, port: fake_smtp)
    monkeypatch.setattr(email_otp.random, "randint", lambda start, end: 654321)

    code = email_otp.otp("user@example.com", sender_password="secret")

    assert code == 654321
    assert fake_smtp.sent_messages
