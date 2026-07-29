from auth.AUTH import authorise
from database.databade import db as default_db


class TransactionEngine:
    """Simple transaction engine for deposit, withdraw, and transfer operations."""

    def __init__(self, db=default_db):
        self.db = db
        self.current_account = None

    @authorise
    def login(self, account_no, password):
        """Authenticate the account and keep it active for subsequent actions."""
        valid_account = self._normalize_account(account_no)
        if valid_account is None:
            print("Invalid account number.")
            return False

        row = self.db.fetchone_(
            "SELECT ID_no FROM customer WHERE ID_no = ? AND password = ?",
            valid_account,
            password,
        )
        if not row:
            print("Login failed: incorrect account number or password.")
            return False

        self.current_account = valid_account
        return True

    def logout(self):
        self.current_account = None

    def get_balance(self, account_no=None):
        account_no = self._get_account_or_current(account_no)
        if account_no is None:
            return None

        row = self.db.fetchone_(
            "SELECT balance FROM balance WHERE ID_no = ?",
            account_no,
        )
        return 0 if row is None else row[0]

    @authorise
    def deposit(self, amount):
        account_no = self._require_login()
        if account_no is None:
            return False

        amount = self._normalize_amount(amount)
        if amount is None:
            print("Deposit amount must be a positive number.")
            self.logout()
            return False

        self._ensure_balance_row(account_no)
        self.db.execute_(
            "UPDATE balance SET balance = balance + ? WHERE ID_no = ?",
            amount,
            account_no,
        )
        self.db.commit_()
        balance = self.get_balance(account_no)
        self.logout()
        return balance

    @authorise
    def withdraw(self, amount):
        account_no = self._require_login()
        if account_no is None:
            return False

        amount = self._normalize_amount(amount)
        if amount is None:
            print("Withdraw amount must be a positive number.")
            self.logout()
            return False

        balance = self.get_balance(account_no)
        if balance < amount:
            print("Insufficient balance.")
            self.logout()
            return False

        self.db.execute_(
            "UPDATE balance SET balance = balance - ? WHERE ID_no = ?",
            amount,
            account_no,
        )
        self.db.commit_()
        new_balance = self.get_balance(account_no)
        self.logout()
        return new_balance

    @authorise
    def transfer(self, receiver_account_no, amount):
        sender_account = self._require_login()
        if sender_account is None:
            return False

        receiver_account = self._normalize_account(receiver_account_no)
        if receiver_account is None:
            print("Invalid receiver account number.")
            self.logout()
            return False

        if receiver_account == sender_account:
            print("Cannot transfer to the same account.")
            self.logout()
            return False

        amount = self._normalize_amount(amount)
        if amount is None:
            print("Transfer amount must be a positive number.")
            self.logout()
            return False

        if not self._account_exists(receiver_account):
            print("Receiver account does not exist.")
            self.logout()
            return False

        sender_balance = self.get_balance(sender_account)
        if sender_balance < amount:
            print("Insufficient balance for transfer.")
            self.logout()
            return False

        self._ensure_balance_row(receiver_account)
        self.db.execute_(
            "UPDATE balance SET balance = balance - ? WHERE ID_no = ?",
            amount,
            sender_account,
        )
        self.db.execute_(
            "UPDATE balance SET balance = balance + ? WHERE ID_no = ?",
            amount,
            receiver_account,
        )
        self.db.commit_()
        result = {
            "sender_balance": self.get_balance(sender_account),
            "receiver_balance": self.get_balance(receiver_account),
        }
        self.logout()
        return result

    def _require_login(self):
        if self.current_account is None:
            print("You must log in before performing transactions.")
            return None
        return self.current_account

    def _account_exists(self, account_no):
        row = self.db.fetchone_(
            "SELECT ID_no FROM customer WHERE ID_no = ?",
            account_no,
        )
        return bool(row)

    def _ensure_balance_row(self, account_no):
        if self.db.fetchone_("SELECT ID_no FROM balance WHERE ID_no = ?", account_no) is None:
            self.db.execute_(
                "INSERT INTO balance (ID_no, balance) VALUES (?, ?)",
                account_no,
                0,
            )
            self.db.commit_()

    def _normalize_amount(self, amount):
        try:
            value = float(amount)
        except (TypeError, ValueError):
            return None
        if value <= 0:
            return None
        return value

    def _normalize_account(self, account_no):
        try:
            return int(account_no)
        except (TypeError, ValueError):
            return None

    def _get_account_or_current(self, account_no):
        if account_no is None:
            return self._require_login()
        return self._normalize_account(account_no)
