from Transcation.transaction import TransactionEngine
from database.databade import db as default_db


class TransactionService:
    def __init__(self, db_instance=None):
        self.db = db_instance or default_db

    def get_balance(self, account_no: int, password: str) -> float | None:
        engine = TransactionEngine(self.db)
        if not engine.login(account_no, password):
            return None
        return engine.get_balance(account_no)

    def deposit(self, account_no: int, password: str, amount: float, reference: str = "Cash Deposit") -> float | None:
        engine = TransactionEngine(self.db)
        if not engine.login(account_no, password):
            return None
        return engine.deposit(amount, reference=reference)

    def withdraw(self, account_no: int, password: str, amount: float, reference: str = "Cash Withdrawal") -> float | None:
        engine = TransactionEngine(self.db)
        if not engine.login(account_no, password):
            return None
        return engine.withdraw(amount, reference=reference)

    def transfer(
        self,
        sender_account_no: int,
        password: str,
        receiver_account_no: int,
        amount: float,
        reference: str = "Account Transfer",
    ) -> dict | None:
        engine = TransactionEngine(self.db)
        if not engine.login(sender_account_no, password):
            return None
        return engine.transfer(receiver_account_no, amount, reference=reference)

    def get_history(self, account_no: int | None = None, limit: int = 50) -> list[dict]:
        engine = TransactionEngine(self.db)
        return engine.get_history(account_no=account_no, limit=limit)

    def get_metrics(self) -> dict:
        row_cust = self.db.fetchone_("SELECT COUNT(*) FROM customer")
        total_customers = row_cust[0] if row_cust else 0

        row_acc = self.db.fetchone_("SELECT COUNT(*) FROM balance WHERE balance > 0")
        active_accounts = row_acc[0] if row_acc else 0

        row_bal = self.db.fetchone_("SELECT SUM(balance) FROM balance")
        total_balance = float(row_bal[0]) if (row_bal and row_bal[0]) else 0.0

        try:
            row_tx = self.db.fetchone_("SELECT COUNT(*) FROM transactions")
            todays_transfers = row_tx[0] if row_tx else 0
        except Exception:
            todays_transfers = 0

        return {
            "total_customers": total_customers,
            "active_accounts": active_accounts,
            "todays_transfers": todays_transfers,
            "total_balance": total_balance,
        }
