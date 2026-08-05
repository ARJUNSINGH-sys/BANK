from database.databade import db as default_db
from ..schemas.customer import CustomerCreateRequest, CustomerUpdateRequest, CustomerResponse


class CustomerService:
    def __init__(self, db_instance=None):
        self.db = db_instance or default_db

    def list_customers(self) -> list[CustomerResponse]:
        rows = self.db.fetchall_(
            """SELECT c.ID_no, c.name, c.personal_id_type, c.personal_id, c.address, 
                      c.Phone_No, c.Email, c.Branch_NO, b.branch_name, COALESCE(bal.balance, 0)
               FROM customer c
               LEFT JOIN branch_details b ON c.Branch_NO = b.Branch_id
               LEFT JOIN balance bal ON c.ID_no = bal.ID_no
               ORDER BY c.ID_no ASC"""
        )
        return [
            CustomerResponse(
                account_no=row[0],
                name=row[1],
                personal_id_type=row[2],
                personal_id=row[3],
                address=row[4],
                phone_no=str(row[5]) if row[5] is not None else "",
                email=row[6],
                branch_no=row[7],
                branch_name=row[8] or "Main Branch",
                balance=float(row[9]),
            )
            for row in rows
        ]

    def get_customer(self, customer_id: int) -> CustomerResponse | None:
        row = self.db.fetchone_(
            """SELECT c.ID_no, c.name, c.personal_id_type, c.personal_id, c.address, 
                      c.Phone_No, c.Email, c.Branch_NO, b.branch_name, COALESCE(bal.balance, 0)
               FROM customer c
               LEFT JOIN branch_details b ON c.Branch_NO = b.Branch_id
               LEFT JOIN balance bal ON c.ID_no = bal.ID_no
               WHERE c.ID_no = ?""",
            customer_id,
        )
        if not row:
            return None
        return CustomerResponse(
            account_no=row[0],
            name=row[1],
            personal_id_type=row[2],
            personal_id=row[3],
            address=row[4],
            phone_no=str(row[5]) if row[5] is not None else "",
            email=row[6],
            branch_no=row[7],
            branch_name=row[8] or "Main Branch",
            balance=float(row[9]),
        )

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
        customer_id = cursor.lastrowid
        if customer_id:
            self.db.execute_("INSERT OR IGNORE INTO balance (ID_no, balance) VALUES (?, ?)", customer_id, 1000)
            self.db.commit_()
        return customer_id

    def update_customer(self, customer_id: int, payload: CustomerUpdateRequest) -> bool:
        fields = []
        values = []
        data = payload.model_dump(exclude_none=True)
        
        # Map phone_no schema field to database column Phone_No
        if "phone_no" in data:
            val = data.pop("phone_no")
            fields.append("Phone_No = ?")
            values.append(val)
        if "email" in data:
            val = data.pop("email")
            fields.append("Email = ?")
            values.append(val)
        if "branch_no" in data:
            val = data.pop("branch_no")
            fields.append("Branch_NO = ?")
            values.append(val)

        for field_name, value in data.items():
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
        self.db.execute_("DELETE FROM balance WHERE ID_no = ?", customer_id)
        self.db.commit_()
        return self.db.fetchone_("SELECT ID_no FROM customer WHERE ID_no = ?", customer_id) is None
