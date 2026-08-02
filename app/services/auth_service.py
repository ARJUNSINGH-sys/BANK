from auth.AUTH import AuthenticationCheck
from database.databade import db as default_db


class AuthService:
    def __init__(self, db_instance=None):
        self.db = db_instance or default_db

    def login(self, account_no: int, password: str) -> bool:
        auth = AuthenticationCheck(self.db, ID_no=account_no, PASSWORD=password)
        return auth.login()
