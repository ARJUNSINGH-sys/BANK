import sqlite3


class Database:
    """Light wrapper around sqlite3.Connection/cursor providing a small,
    predictable API used by the auth layer.

    Public methods used by the codebase:
    - execute_(sql, *params) -> sqlite3.Cursor
    - fetchone_(sql, *params) -> tuple|None
    - fetchall_(sql, *params) -> list[tuple]
    - commit_() -> None
    - close_() -> None
    """

    def __init__(self, branch: str):
        try:
            self.connection = sqlite3.connect(branch)
            self.cursor = self.connection.cursor()
            print("Database connected!")
        except sqlite3.Error:
            print("the connection was refused please try again")
            raise

    def execute_(self, sql: str, *params):
        """Execute SQL with optional parameters and return the cursor."""
        if params:
            cur = self.cursor.execute(sql, params)
        else:
            cur = self.cursor.execute(sql)
        return cur

    def fetchone_(self, sql: str, *params):
        """Execute `sql` and return a single row (or None)."""
        cur = self.execute_(sql, *params)
        return cur.fetchone()

    def fetchall_(self, sql: str, *params):
        """Execute `sql` and return all rows."""
        cur = self.execute_(sql, *params)
        return cur.fetchall()

    def commit_(self):
        return self.connection.commit()

    def close_(self):
        return self.connection.close()


# Single shared Database instance (use this or create your own explicitly).
db = Database("branch.db")