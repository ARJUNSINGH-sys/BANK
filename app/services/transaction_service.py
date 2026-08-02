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

    def deposit(self, account_no: int, password: str, amount: float) -> float | None:
        engine = TransactionEngine(self.db)
        if not engine.login(account_no, password):
            return None
        return engine.deposit(amount)

    def withdraw(self, account_no: int, password: str, amount: float) -> float | None:
        engine = TransactionEngine(self.db)
        if not engine.login(account_no, password):
            return None
        return engine.withdraw(amount)

    def transfer(
        self,
        sender_account_no: int,
        password: str,
        receiver_account_no: int,
        amount: float,
    ) -> dict | None:
        engine = TransactionEngine(self.db)
        if not engine.login(sender_account_no, password):
            return None
        return engine.transfer(receiver_account_no, amount)
