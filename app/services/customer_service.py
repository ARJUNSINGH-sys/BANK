from database.databade import db as default_db
from ..schemas.customer import CustomerCreateRequest, CustomerUpdateRequest


class CustomerService:
    def __init__(self, db_instance=None):
        self.db = db_instance or default_db

    def create_customer(self, payload: CustomerCreateRequest) -> int | None:
        cursor = self.db.execute_(
            "INSERT INTO customer (password, name, personal_id_type, personal_id, address, Phone_No, Email, Branch_NO) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            payload.password,
            payload.name,
            payload.personal_id_type,
            payload.personal_id,
            payload.address,
            payload.phone_no,
            payload.email,
            payload.branch_no,
        )
        self.db.commit_()
        return cursor.lastrowid

    def update_customer(self, customer_id: int, payload: CustomerUpdateRequest) -> bool:
        fields = []
        values = []
        for field_name, value in payload.model_dump(exclude_none=True).items():
            fields.append(f"{field_name} = ?")
            values.append(value)

        if not fields:
            return False

        values.append(customer_id)
        sql = f"UPDATE customer SET {', '.join(fields)} WHERE ID_no = ?"
        self.db.execute_(sql, *values)
        self.db.commit_()
        return self.db.fetchone_("SELECT ID_no FROM customer WHERE ID_no = ?", customer_id) is not None

    def delete_customer(self, customer_id: int) -> bool:
        self.db.execute_("DELETE FROM customer WHERE ID_no = ?", customer_id)
        self.db.commit_()
        return self.db.fetchone_("SELECT ID_no FROM customer WHERE ID_no = ?", customer_id) is None
